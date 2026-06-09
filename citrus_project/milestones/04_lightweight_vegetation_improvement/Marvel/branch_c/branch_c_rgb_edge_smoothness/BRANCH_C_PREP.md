# Branch C Prep: LiDAR + RGB Edge-Aware Smoothness

Date: 2026-06-09

## Purpose

Prepare the clean Branch C training code for the `RGB-edge + LiDAR` experiment.

Branch C tests the user's core idea:

```text
LiDAR labels/masks -> metric depth supervision
RGB image gradients -> boundary-aware smoothness regularization
```

This branch does not use teacher/prior distillation.

## Important Code Change

This folder is a copy of:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/hybrid_supervised_draft/
```

New Branch C option:

```text
--disable_photometric_loss
--skip_optimizer_load
```

Why it matters:

The old hybrid trainer still included Lite-Mono's self-supervised photometric reconstruction loss. For the new ablation plan, we need cleaner branches:

1. LiDAR-only continued training control.
2. LiDAR + RGB edge-aware smoothness.

`--disable_photometric_loss` lets us keep the supervised LiDAR loss and smoothness regularization while turning off the old photometric loss.

When `--disable_photometric_loss` is enabled, this branch now also skips the pose network and image-warping path. That keeps the Branch B/C tests aligned with the supervised-only experiment and reduces wasted laptop VRAM/time.

`--skip_optimizer_load` should be used when starting from an existing checkpoint such as `weights_13`. It loads encoder/depth as the model initialization but does not inherit the old Adam optimizer state from the previous training recipe.

## Branch Definitions

### Branch B: LiDAR-Only Continued Training Control

Purpose:

Control for extra training time.

Core settings:

```text
--disable_photometric_loss
--disparity_smoothness 0
--boundary_loss_weight 0
--lidar_loss_weight 0.1
--lidar_loss_type log_l1
--lidar_scale_align none
--lidar_loss_scales 0
```

### Branch C: LiDAR + RGB Edge-Aware Smoothness

Purpose:

Test whether RGB-guided smoothness improves boundary/structure behavior while LiDAR keeps metric depth anchored.

Core settings:

```text
--disable_photometric_loss
--disparity_smoothness 0.001
--boundary_loss_weight 0
--lidar_loss_weight 0.1
--lidar_loss_type log_l1
--lidar_scale_align none
--lidar_loss_scales 0
```

Optional smoothness sweep:

```text
--disparity_smoothness 0.001
--disparity_smoothness 0.005
--disparity_smoothness 0.01
```

Start with `0.001` because it is the Lite-Mono-style default. Increase only if the effect is too weak.

## Student/Base Checkpoint

Preferred student:

```text
earlier Hybrid weights_13
```

Fallback if `weights_13` is not available on the lab machine:

```text
lab Hybrid weights_9
```

## Laptop Prep Status

Prepared locally:

```text
C:/Proj/lite-Mono/citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/branch_c_rgb_edge_smoothness/
```

The code is prepared locally and can be transferred to the lab computer. Long training should still be done on the lab machine when possible, but laptop 300-step pilot runs are prepared.

Local base checkpoint confirmed:

```text
C:/Proj/lite-Mono/citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/models/weights_13/
```

Both `encoder.pth` and `depth.pth` exist.

Laptop pilot scripts:

```text
run_branch_b_lidar_only_300step_laptop.ps1
run_branch_c_rgb_edge_300step_laptop.ps1
```

These scripts:

1. Start from the earlier best local Hybrid `weights_13`.
2. Load only `encoder` and `depth`.
3. Use `--skip_optimizer_load`.
4. Disable photometric loss.
5. Save step checkpoints every 100 training steps.
6. Write console logs under `Marvel/runs/<run_name>/console.log`.

## First Run Recommendation

Do not start with long training.

Recommended first gate:

```text
Branch B: 200-300 steps
Branch C: 200-300 steps
```

Then compare:

1. Training losses are finite.
2. LiDAR-valid validation metrics do not collapse.
3. Same-image raw/scaled visual panels do not show obvious new artifacts.

Only after this should we run 2-5 epoch ablations.
