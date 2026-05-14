# Snapshot 01: Photometric Confidence Masking

This is Levinson's first Milestone 4 self-supervised improvement gate.

Conclusion: uncertain / do not scale yet.

## Method Summary

Photometric-confidence masking is a training-loss-only change. It keeps the existing Lite-Mono automasking idea, then softly downweights pixels where warped RGB reconstruction only barely beats the identity/no-warp comparison.

For each pixel:

```text
identity_min = best identity/no-warp loss across source frames
reproj_min   = best warped/reprojected loss across source frames
margin       = identity_min - reproj_min
```

Positive margin means warping helped. Larger positive margin means warping helped more clearly.

This snapshot used the moderate settings:

```text
--photometric_confidence_threshold 0.01
--photometric_confidence_ramp 0.05
--photometric_confidence_min_weight 0.25
```

Warped-winning pixels receive a soft weight between `0.25` and `1.0`. Identity-winning pixels still follow normal automasking behavior and do not provide useful depth-training gradients.

The method is self-supervised: it uses only RGB reconstruction and identity/no-warp losses already computed by Lite-Mono. It does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED depth as a training loss. Citrus depth labels and masks are used only for evaluation/monitoring.

Inference is unchanged: one RGB image goes through the same Lite-Mono encoder and depth decoder.

## Contents

```text
code/
commands/
diagnostics/
results/
visual_summary/
```

Included tested code copies:

- `code/trainer.py`
- `code/options.py`

Small copied evidence artifacts:

- `results/val_lite-mono_max100_summary.json`
- `results/val_lite-mono_max100_per_sample.csv`
- `diagnostics/confidence_diagnostics_summary.json`
- `diagnostics/confidence_diagnostics_summary.csv`
- `visual_summary/original_vs_adapted_selection_summary.json`
- `visual_summary/original_vs_adapted_selection_summary.csv`

## Source Code Changes

- `options.py`: added disabled-by-default command-line options for photometric-confidence masking.
- `trainer.py`: added the confidence-weighted photo-loss branch and scalar diagnostics. The default path still uses the original `to_optimise.mean()` behavior when `--photometric_confidence_masking` is not set.

## Run Paths

Smoke run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_smoke_2steps/
```

Main 250-step method gate:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_b12_250steps_seed0/
```

Main method checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_b12_250steps_seed0/models/step_250/
```

Main method first-100 validation result:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_b12_250steps_seed0/eval_val100_step_250/
```

Same-budget no-mask control:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_250steps_seed0_control/
```

Visual comparison:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_b12_250steps_seed0/visual_compare_control_vs_confidence_val100_step_250/
```

Confidence diagnostic panels:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_b12_250steps_seed0/visual_confidence_diagnostics_val100_step_250/
```

## Commands

Command scripts are saved under `commands/`.

Key run choices:

- Citrus prepared dataset
- Lite-Mono ImageNet encoder pretrain through `--mypretrain weights/lite-mono/lite-mono-pretrain.pth`
- no `--load_weights_folder weights/lite-mono`
- batch size 12 for the 250-step gate
- seed 0
- `--num_workers 0`
- `--max_train_steps 250`
- no structure loss, no vegetation weighting, no LiDAR/depth-guided loss

## Metric Summary

First-100 validation:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Original Lite-Mono first-100 reference | 0.7289 | 0.0131 | 0.3680 | 0.4807 |
| Same-budget no-mask ImageNet-pretrain control, step 250 | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Photometric-confidence masking, step 250 | 0.8985 | 0.0000 | 0.5582 | 0.3018 |

Interpretation:

- The confidence method was stable, but it was not a clear improvement.
- It slightly improved median-scaled `abs_rel` over the same-budget no-mask control.
- It worsened median-scaled `a1` versus the same-budget no-mask control.
- Both 250-step ImageNet-pretrain runs were much weaker than the original Lite-Mono first-100 reference, so 250 steps is too early to be a full method verdict.

## Diagnostics Summary

Smoke result:

- `train.py --help` exposes the new options.
- `py_compile` passed for `options.py` and `trainer.py`.
- CUDA 2-step smoke completed with finite losses.
- TensorBoard event data contains the requested `photometric_confidence/*` scalar tags.

Main 250-step train diagnostics at the last logged train step, step 200:

| diagnostic | scale 0 | scale 1 | scale 2 |
|---|---:|---:|---:|
| confidence mean among warped winners | 0.6987 | 0.6994 | 0.7006 |
| confident pixel fraction | 0.3656 | 0.3654 | 0.3653 |
| margin mean | 0.0034 | 0.0033 | 0.0033 |
| effective weight mean | 0.3435 | 0.3431 | 0.3425 |
| unweighted photo loss | 0.1351 | 0.1351 | 0.1352 |
| weighted photo loss | 0.1655 | 0.1657 | 0.1660 |

The confidence signal was not near zero everywhere. The mixed validation result is therefore not explained by the mask simply deleting nearly all training signal.

## Visual Check

Generated panels:

```text
adapted_good_index_0035_comparison.png
adapted_typical_index_0045_comparison.png
adapted_bad_index_0023_comparison.png
largest_drop_vs_original_index_0096_comparison.png
```

Visual read:

- The confidence run looked broadly similar to the no-mask 250-step control.
- It did not show an obvious vegetation/row-structure rescue.
- The typical and largest-drop selected panels lost `a1` versus the no-mask control.

## Conclusion

Status: uncertain / do not scale yet.

This first moderate/soft photometric-confidence gate is technically valid and self-supervised, but the 250-step evidence is mixed. It should not be promoted to a long Milestone 4 run without a follow-up reason, such as tuning the confidence schedule, inspecting confidence masks directly, or finding evidence that the method needs more warmup before its metric signal appears.
