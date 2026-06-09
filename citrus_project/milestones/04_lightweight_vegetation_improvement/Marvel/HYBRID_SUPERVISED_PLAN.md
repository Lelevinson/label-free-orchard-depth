# Hybrid Supervised Citrus Training Plan

Date noted: 2026-05-17
Owner/workstream: Marvel, Milestone 4
Status: planned future experiment, not implemented yet

## Short Summary

This experiment should test whether Lite-Mono improves on Citrus scenes when the original self-supervised photometric objective is anchored by the prepared LiDAR-derived depth labels.

The first target method is:

```text
total_loss = photometric_self_supervised_loss
           + boundary_loss_optional
           + lambda_lidar * masked_scale_aware_lidar_depth_loss
```

The important difference from the current Phase 2 boundary-loss idea is that this method uses actual Citrus label information. It should not ask raw RGB texture edges to act as depth supervision everywhere.

## Main Hypothesis

Lite-Mono's self-supervised photometric loss can decrease while Citrus LiDAR depth metrics do not improve. A masked LiDAR supervision term should reduce this mismatch by directly anchoring predictions to the project-owned depth labels in valid regions.

Expected benefit:

- better median-scaled validation/test metrics than plain Citrus adaptation
- less scale drift during training
- more reliable depth on vegetation structure where labels are valid
- clearer paper argument because the method uses the dataset pipeline contribution

Failure mode to watch:

- the LiDAR labels are semi-dense and interpolated, so a naive supervised loss may over-trust uncertain vegetation fills
- direct absolute-scale loss may fight monocular scale ambiguity too early
- label supervision may improve valid-mask metrics but hurt photometric consistency or visual smoothness

## Existing Repo Hooks

The repo already has the key data pieces.

Dataset loader:

```text
citrus_project/milestones/02_citrus_integration/citrus_prepared_dataset.py
```

Current returned fields:

```text
inputs["depth_gt"]     # dense LiDAR-derived depth label, shape [B, 1, H, W]
inputs["valid_mask"]   # prepared valid-label mask, shape [B, 1, H, W]
inputs["label_mask"]   # valid, finite, positive label mask, shape [B, 1, H, W]
```

Prepared label folders:

```text
citrus_project/dataset_workspace/prepared_training_dataset/dense_lidar_npz/
citrus_project/dataset_workspace/prepared_training_dataset/dense_lidar_valid_mask_npz/
```

Current trainer hooks:

```text
trainer.py
  compute_losses()
  compute_depth_losses()
  get_depth_metric_mask()
```

`compute_depth_losses()` already interpolates predicted depth to label resolution and uses the valid mask for metric logging. The supervised loss should reuse the same masking logic, but must remain differentiable instead of detaching the prediction.

## Proposed First Implementation

### New Options

Add these flags to `options.py`:

```text
--lidar_loss_weight
--lidar_loss_type
--lidar_scale_align
--lidar_loss_min_depth
--lidar_loss_max_depth
--lidar_loss_warmup_epochs
--lidar_loss_scales
--lidar_loss_min_valid_pixels
```

Recommended defaults:

```text
--lidar_loss_weight 0.0
--lidar_loss_type log_l1
--lidar_scale_align median
--lidar_loss_min_depth 0.001
--lidar_loss_max_depth 80.0
--lidar_loss_warmup_epochs 0
--lidar_loss_scales 0
--lidar_loss_min_valid_pixels 500
```

The default weight must be `0.0` so existing training behavior stays unchanged unless the experiment explicitly enables it.

### First Loss Version

Use masked, median-aligned log-depth L1 at scale 0:

```text
pred_depth = outputs[("depth", 0, 0)]
pred_depth = interpolate pred_depth to depth_gt size
mask = label_mask & finite(depth_gt) & finite(pred_depth)

scale = median(depth_gt[mask]) / median(pred_depth[mask])
pred_aligned = pred_depth * detach(scale)

lidar_loss = mean(abs(log(pred_aligned) - log(depth_gt))) over mask
```

Why log-depth:

- depth errors at 2 m and 20 m should not be treated equally in raw meters
- log depth is less dominated by large far-depth values
- it matches the project's concern that relative structure matters in vegetation

Why median alignment:

- monocular depth has scale ambiguity
- current Citrus runs show large scale-ratio shifts
- median alignment lets the loss first teach relative depth shape without forcing absolute metric scale too early

Why detach the scale:

- scale alignment should be a normalization step, not a shortcut where the model learns by manipulating the scale factor

### Loss Integration Location

In `trainer.py`, add a helper:

```text
compute_lidar_supervision_loss(inputs, outputs, scale)
```

Then inside `compute_losses()`:

```text
if self.opt.lidar_loss_weight > 0 and "depth_gt" in inputs:
    lidar_loss = self.compute_lidar_supervision_loss(inputs, outputs, scale)
    loss += current_lidar_weight * lidar_loss / (2 ** scale)
```

Log at least:

```text
lidar_loss/0
lidar_loss_weighted/0
lidar_valid_fraction/0
lidar_scale_ratio/0
```

The valid fraction and scale ratio are important because they tell us whether the supervised signal is actually active and whether scale drift is being reduced.

## Experiment Ladder

Do not jump straight to 30 epochs. Use staged gates.

### Stage S0: Code Safety Smoke

Purpose: prove the implementation runs and does not change behavior when disabled.

Commands:

```powershell
C:\Proj\miniforge3\condabin\mamba.bat run -n lite-mono python -m py_compile trainer.py options.py layers.py
```

Disabled-loss smoke:

```powershell
C:\Proj\miniforge3\condabin\mamba.bat run -n lite-mono python train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name hybrid_supervised_disabled_smoke `
  --log_dir citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs `
  --mypretrain weights/lite-mono/lite-mono-pretrain.pth `
  --weights_init pretrained `
  --batch_size 2 `
  --num_epochs 1 `
  --max_train_steps 1 `
  --height 192 `
  --width 640 `
  --num_workers 0 `
  --seed 0 `
  --lidar_loss_weight 0.0
```

Success criteria:

- py_compile passes
- one-step disabled smoke matches normal training behavior
- no missing-key errors for `depth_gt`, `valid_mask`, or `label_mask`

### Stage S1: One-Step Enabled Smoke

Purpose: prove the supervised LiDAR term computes and logs.

Suggested run:

```text
model_name = hybrid_supervised_smoke_1step_w01
--batch_size 2
--max_train_steps 1
--lidar_loss_weight 0.1
--lidar_loss_type log_l1
--lidar_scale_align median
```

Success criteria:

- loss is finite
- `lidar_loss/0` is finite
- `lidar_valid_fraction/0` is nonzero
- `lidar_scale_ratio/0` is finite and not absurd
- backward pass succeeds without CUDA OOM

### Stage S2: Short Gate

Purpose: test whether the supervised signal improves early depth metrics faster than the existing approaches.

Suggested run:

```text
model_name = hybrid_supervised_b12_2ep_w01
batch_size = 12
num_epochs = 2
lidar_loss_weight = 0.1
lidar_loss_type = log_l1
lidar_scale_align = median
seed = 0
```

Compare against:

```text
plain_citrus_b12_2ep_control
phase2_boundary_loss_b12_2ep_w005
phase2_boundary_loss_b12_2ep_w02
```

Primary gate metric:

```text
full val/test median-scaled abs_rel and a1
```

Secondary diagnostics:

```text
raw-scale abs_rel and a1
median scale ratio
training-time lidar_loss/0
training-time lidar_scale_ratio/0
visual comparison panels
```

Go criteria:

- beats plain 2ep control on val median-scaled abs_rel
- does not reduce test a1 below plain 2ep control
- shows lower or more stable scale ratio than plain 2ep control
- visual panels do not show obvious label overfitting artifacts

Stop criteria:

- worse than plain 2ep control on both val abs_rel and a1
- raw-scale metrics collapse
- `lidar_loss/0` dominates photometric loss
- predictions become visibly noisy or hole-shaped around label masks

### Stage S3: Weight Sweep

Purpose: find a useful supervised weight before spending long GPU time.

Candidates:

```text
lambda_lidar = 0.02
lambda_lidar = 0.05
lambda_lidar = 0.10
lambda_lidar = 0.20
```

Recommended order:

1. `0.10`
2. `0.05`
3. `0.20` only if `0.10` improves without artifacts
4. `0.02` if `0.05` is too strong

Keep everything else fixed:

```text
same seed
same batch size
same pretrain
same train/val/test splits
same evaluator
```

### Stage S4: 5-Epoch or 10-Epoch Trend Gate

Purpose: avoid another blind multi-day run.

Run only the best S2/S3 candidate for 5 or 10 epochs.

Compare against:

- same checkpoint duration plain Citrus control if needed
- final plain Citrus 30ep baseline as the long-run target
- current Phase 2 30ep result if available

Go criteria for 30 epochs:

- improvement over same-duration plain control is clear
- full val and test move in the same direction
- loss curves show no supervised-loss domination
- visuals look at least as coherent as plain Citrus

### Stage S5: Full 30-Epoch Run

Purpose: only after gates show real signal.

Suggested naming:

```text
hybrid_supervised_b12_30ep_logl1_median_wXX
```

Expected outputs:

```text
loss_plots/
val_lite-mono_full_summary.json
test_lite-mono_full_summary.json
visuals/single_model_val/
visuals/single_model_test/
visuals/baseline_vs_hybrid_val/
visuals/baseline_vs_hybrid_test/
```

## Evaluation Plan

Always report both raw-scale and median-scaled metrics.

Primary full-split metrics:

```text
abs_rel
sq_rel
rmse
rmse_log
a1
a2
a3
median_scale_ratio
mean_valid_fraction
```

Primary comparisons:

```text
Original pretrained Lite-Mono on Citrus
Plain Citrus final 30ep baseline
Plain Citrus same-duration control
Phase 2 boundary-loss same-duration run
Hybrid supervised candidate
```

Visual panels should include:

```text
RGB
LiDAR label
valid mask or label coverage
plain baseline prediction
hybrid prediction
plain error map
hybrid error map
error delta
```

## Paper-Framing Angle

Possible method framing:

```text
Label-anchored lightweight monocular adaptation for vegetation-dense agricultural scenes.
```

Possible claim if it works:

```text
Self-supervised adaptation alone can reduce photometric error without reliably improving LiDAR-valid depth metrics. Adding masked, scale-aware LiDAR supervision anchors the lightweight monocular model to agricultural depth structure while preserving RGB-only inference.
```

Important constraint:

Runtime inference remains monocular RGB-only. LiDAR labels are used only during training/evaluation.

## Risks And Controls

Risk: supervised loss overfits interpolated labels.
Control: use `label_mask`, inspect valid coverage, compare sparse/raw LiDAR evaluation if available.

Risk: scale-aligned supervised loss improves median-scaled metrics but not raw-scale metrics.
Control: report raw-scale metrics and median scale ratio separately.

Risk: direct LiDAR supervision erases useful self-supervised structure.
Control: keep photometric loss active in the first hybrid version.

Risk: stronger labels make comparison unfair against plain self-supervised baseline.
Control: frame this as a new label-anchored training method enabled by the Citrus pipeline, not as a tiny same-setting tweak.

Risk: training time is too expensive.
Control: require 1-step, 2-epoch, and 5/10-epoch gates before a full 30-epoch run.

## Initial Recommendation

The first real run should be:

```text
hybrid_supervised_b12_2ep_logl1_median_w01
```

with:

```text
--lidar_loss_weight 0.1
--lidar_loss_type log_l1
--lidar_scale_align median
--lidar_loss_scales 0
--batch_size 12
--num_epochs 2
--seed 0
```

If `w0.1` is unstable or visually noisy, try `w0.05`. If `w0.1` is stable and clearly improves over the fair 2-epoch plain control, run a 5-epoch or 10-epoch gate before considering 30 epochs.
