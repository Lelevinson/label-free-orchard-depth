# LiDAR-Aware Edge Loss Experiment Plan

Date: 2026-05-22

Owner/context: Marvel's next Milestone 4 improvement direction after the successful hybrid supervised 30-epoch run.

This experiment is separate from the previous boundary-loss-only and hybrid-supervised experiments. It should live in this folder so teammates and their Codex sessions can reason about it as a distinct method idea.

## Short Answer

Yes, this experiment should use the hybrid supervised method as the base direction.

But there are two meanings of "use the hybrid model":

1. Method base: yes. The new experiment should start from the hybrid supervised recipe: photometric self-supervision plus masked LiDAR depth supervision.
2. Weight initialization: not necessarily. For the cleanest comparison, the first gate should start from the same ImageNet-style Lite-Mono pretrain as the previous hybrid runs, not from the final 30-epoch hybrid checkpoint. That lets us compare "hybrid only" versus "hybrid plus LiDAR-aware edge loss" fairly.

Recommended first version:

```text
ImageNet/Lite-Mono pretrain
  -> hybrid supervised LiDAR depth loss
  -> plus LiDAR-aware edge loss
```

Optional later version:

```text
hybrid 30ep weights_29
  -> short fine-tune with LiDAR-aware edge loss
```

The optional fine-tune may be useful for squeezing visual boundary quality, but it is less clean as a method comparison because it starts from a stronger trained model.

## Motivation

The earlier RGB boundary loss was simple:

```text
RGB edge should match predicted disparity edge
```

That helped a little, but it had a weak assumption:

```text
RGB edge = depth edge
```

In orchards, this is often false. Leaves, shadows, bark texture, branch texture, sun glare, and canopy noise create many RGB edges that are not true geometric depth boundaries.

The hybrid supervised result showed that LiDAR supervision is much more reliable for this project because it teaches actual scene depth and absolute scale. The next logical step is to use LiDAR not only for pointwise depth supervision, but also for boundary supervision.

## General Goal

Teach Lite-Mono to make better depth transitions at real geometry boundaries in Citrus scenes while keeping inference RGB-only and lightweight.

Plain goal:

```text
RGB at inference time
  -> model predicts depth

LiDAR during training
  -> tells model which boundaries are real depth boundaries
```

This keeps RGB as the final input, but uses LiDAR as a teacher during training.

## Research Hypothesis

The current hybrid supervised model already learns good absolute scale and strong aggregate depth accuracy. However, qualitative panels still show moderate boundary artifacts around vegetation, tree rows, and sparse-label regions.

Hypothesis:

```text
Adding a LiDAR-aware edge loss will improve boundary-local depth accuracy and visual structure
without sacrificing the absolute-scale gains from hybrid supervised training.
```

The intended improvement is not necessarily a huge global metric jump. It may appear more clearly in:

- boundary-region abs_rel
- selected visual panels
- error-delta maps near tree/road/canopy transitions
- reduced over-smoothing at real depth discontinuities

## Role Of RGB And LiDAR

RGB:

- still the only input at inference/deployment time
- provides appearance cues: road, tree rows, trunks, canopy, shadows, sky, exposed ground
- is what the model must learn from

LiDAR:

- used only during training/evaluation
- provides metric depth labels and valid masks
- helps decide which RGB boundaries correspond to true depth changes

Core principle:

```text
Do not force depth edges at every RGB texture edge.
Use LiDAR to identify which edges are geometry edges.
```

Example:

```text
leaf texture edge:
  RGB edge = yes
  LiDAR depth jump = no
  do not force strong depth boundary

tree/road/canopy transition:
  RGB edge = yes
  LiDAR depth jump = yes
  encourage depth boundary
```

## Baseline To Compare Against

Primary baseline:

```text
hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/models/weights_29
```

Current best hybrid result:

| model | split | raw abs_rel | raw a1 | median abs_rel | median a1 | median scale ratio |
|---|---:|---:|---:|---:|---:|---:|
| Hybrid supervised 30ep | val | 0.1913 | 0.7968 | 0.1933 | 0.7805 | 0.9850 |
| Hybrid supervised 30ep | test | 0.1741 | 0.8186 | 0.1791 | 0.8001 | 1.0061 |

Secondary context baselines:

- plain Citrus 30ep
- boundary-loss-only 30ep
- hybrid supervised 5ep
- hybrid supervised weights_19

The new method must at least avoid breaking the strong raw-scale performance of the hybrid supervised result.

## Proposed Loss Design

The existing hybrid supervised loss is:

```text
L_total = L_photometric + L_smooth + lambda_lidar * L_lidar_depth
```

The proposed extension is:

```text
L_total = L_photometric
        + L_smooth
        + lambda_lidar * L_lidar_depth
        + lambda_edge * L_lidar_edge
```

Where:

```text
L_lidar_edge = boundary-aware loss based on trusted LiDAR depth gradients
```

### Edge Signal

Use the dense LiDAR label and valid mask:

```text
dense_lidar_npz/
dense_lidar_valid_mask_npz/
```

Compute valid label gradients:

```text
grad_label_x = |log(label[x+1]) - log(label[x])|
grad_label_y = |log(label[y+1]) - log(label[y])|
```

Only trust gradients where both neighboring label pixels are valid:

```text
edge_valid_x = valid[x+1] AND valid[x]
edge_valid_y = valid[y+1] AND valid[y]
```

Optional threshold:

```text
label_edge = grad_label > threshold
```

This avoids treating every tiny label change as a boundary.

### Prediction Signal

Use predicted depth or predicted log-depth at the same resolution:

```text
grad_pred_x = |log(pred[x+1]) - log(pred[x])|
grad_pred_y = |log(pred[y+1]) - log(pred[y])|
```

Use log-depth because relative depth differences are more stable than raw meter differences.

### Candidate Edge Loss

First simple version:

```text
L_lidar_edge = mean_valid( |grad_pred - grad_label| )
```

But only on trusted label-edge pixels:

```text
L_lidar_edge = mean( edge_valid * edge_weight * |grad_pred - grad_label| )
```

Possible edge weights:

```text
edge_weight = clamp(grad_label / threshold, 0, max_weight)
```

This makes stronger true depth jumps matter more.

## Why This Is Better Than The Old Boundary Loss

Old boundary loss:

```text
match predicted disparity edges to RGB image edges
```

Risk:

```text
RGB texture/shadow edges can create fake depth boundaries
```

New LiDAR-aware edge loss:

```text
match predicted depth edges to LiDAR depth-label edges
```

Benefit:

```text
supervises real geometry boundaries instead of all visual texture boundaries
```

RGB is still essential, because the model must learn RGB cues that predict those LiDAR-taught boundaries. LiDAR only teaches during training.

## Experiment Roadmap

### Stage 0: Code Isolation

Create a copied code folder for this experiment, similar to the hybrid supervised draft:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/lidar_aware_edge_loss_experiment/code/
```

Suggested copied files:

```text
layers.py
trainer.py
options.py
train_lidar_edge.py
```

Do not modify root runnable files for the first draft.

### Stage 1: Implementation

Add CLI flags:

```text
--lidar_edge_loss_weight
--lidar_edge_threshold
--lidar_edge_max_weight
--lidar_edge_use_log_depth
--lidar_edge_min_valid_pixels
```

Recommended defaults:

```text
--lidar_edge_loss_weight 0.0
--lidar_edge_threshold 0.05
--lidar_edge_max_weight 5.0
--lidar_edge_use_log_depth
--lidar_edge_min_valid_pixels 200
```

Add logging:

```text
lidar_edge_loss/0
lidar_edge_loss_weighted/0
lidar_edge_valid_fraction/0
lidar_edge_mean_label_gradient/0
```

### Stage 2: Smoke Test

Run one tiny smoke test:

```text
--max_train_steps 1
--batch_size 2
--lidar_edge_loss_weight 0.02
```

Check:

- no tensor shape errors
- no NaN/Inf
- edge valid fraction is nonzero
- total loss remains finite
- training still saves a checkpoint

### Stage 3: 2-Epoch Gate

Run a 2-epoch gate on the laptop or lab computer:

```text
--batch_size 12
--num_epochs 2
--lidar_loss_weight 0.1
--lidar_loss_type log_l1
--lidar_scale_align none
--lidar_loss_scales 0
--lidar_edge_loss_weight 0.02
```

Compare against:

- hybrid supervised 2ep absolute-scale run
- hybrid supervised 5ep run
- plain Citrus baseline

Decision:

Only continue if it does not damage scale and shows at least some improvement in metrics or visuals.

### Stage 4: 5-Epoch Gate

If the 2-epoch result is stable, run a 5-epoch gate.

Candidate weights:

```text
0.01
0.02
0.05
```

Recommended first choice:

```text
--lidar_edge_loss_weight 0.02
```

Why conservative:

The current hybrid model is already strong. A boundary term that is too heavy could overfit label artifacts or create edge noise.

### Stage 5: Full Run On Lab Computer

Only launch a 30-epoch lab run if the 5-epoch gate is clearly promising.

Before launching:

- confirm environment
- confirm dataset paths
- confirm checkpoints save every epoch
- confirm postprocess script works
- estimate runtime on lab GPU
- record exact command in this folder

Suggested checkpoint sweep after full run:

```text
weights_4
weights_9
weights_14
weights_19
weights_24
weights_29
```

Pick best validation checkpoint before making final test claims.

## Metrics To Track

Standard metrics:

- raw abs_rel
- raw a1
- median-scaled abs_rel
- median-scaled a1
- median scale ratio

Boundary-focused metrics to add if possible:

- abs_rel on LiDAR edge pixels
- a1 on LiDAR edge pixels
- abs_rel near LiDAR edge neighborhoods
- non-edge abs_rel, to check whether boundary gains hurt smooth regions

Qualitative outputs:

- baseline-vs-new-method panels
- current hybrid-vs-new-method panels
- edge-mask visualizations
- error-delta maps focused on boundary regions

## Success Criteria

Minimum success:

- training remains stable
- raw scale remains close to 1.0 median scale ratio
- no clear degradation versus hybrid supervised baseline
- selected boundary visual panels look at least as good as current hybrid

Strong success:

- improves val/test raw abs_rel and a1 over hybrid supervised 30ep
- improves boundary-region metrics
- visually reduces error around tree rows, road edges, trunks, and canopy transitions

Failure signal:

- raw scale gets worse
- global metrics regress
- error maps show red/orange artifacts around many vegetation textures
- predicted depth becomes overly sharp/noisy

## Lab Computer Workflow

If Codex cannot directly access the lab computer, use this workflow:

1. Codex prepares exact commands and scripts on the laptop.
2. User copies repo/scripts/data or pulls from git on the lab computer.
3. User runs smoke command first and sends logs back.
4. Codex reviews logs before long run.
5. User launches long run on lab computer.
6. User sends final JSON/CSV summaries and selected panels back.
7. Codex updates notes and interprets results.

This avoids locking the user's laptop for long jobs.

## Current Recommendation

Do not immediately run a 30-epoch LiDAR-aware edge experiment.

Recommended next concrete step:

```text
Implement isolated draft code
  -> one-step smoke
  -> 2-epoch gate
  -> 5-epoch gate
  -> only then lab 30-epoch run if promising
```

This is the most responsible path because the current hybrid supervised 30-epoch model is already strong, and the new edge term should prove it helps before spending another long run.
