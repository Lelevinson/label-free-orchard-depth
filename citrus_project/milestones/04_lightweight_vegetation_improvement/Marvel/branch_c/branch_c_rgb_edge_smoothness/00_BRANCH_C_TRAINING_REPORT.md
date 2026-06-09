# Branch C Training Report

Date: 2026-06-09

## Description

Branch C tests a clean supervised/hybrid training variant:

```text
RGB image -> Lite-Mono prediction
Dense LiDAR + valid mask -> metric depth supervision during training
RGB image gradients -> edge-aware disparity smoothness
```

Inference remains RGB-only. LiDAR is used only during training/evaluation.

## Method

Starting checkpoint:

```text
Marvel/runs/hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/models/weights_13
```

This is the earlier best local hybrid checkpoint by validation/test evidence.

Branch C settings:

```text
--disable_photometric_loss
--disparity_smoothness 0.001
--boundary_loss_weight 0
--lidar_loss_weight 0.1
--lidar_loss_type log_l1
--lidar_scale_align none
--lidar_loss_scales 0
--models_to_load encoder depth
--skip_optimizer_load
```

Important isolation choices:

1. The old self-supervised photometric/reprojection loss is disabled.
2. The pose/reprojection path is skipped when photometric loss is disabled.
3. Only encoder/depth weights are loaded from `weights_13`.
4. Optimizer state is fresh so the old recipe's Adam momentum does not leak into this branch.

## Estimated Runtime

Before training on the RTX 4050 Laptop GPU:

1. 2-epoch smoke plus val/test evaluation: about 1.5 to 3 hours.
2. 30-epoch continuation: about 20 to 35 hours.

Actual observed runtime:

1. 2-epoch smoke plus val/test evaluation and visual generation: about 44 minutes.
2. 30-epoch training plus val/test evaluation and visual generation: about 9 hours 44 minutes.

The original estimate was too pessimistic because disabling photometric loss also removed pose/reprojection work after the Branch C patch.

## Setup Notes And Hiccups

Preparation issues found and fixed:

1. The folder already existed from the first prep pass, copied from `hybrid_supervised_draft`.
2. Sandbox access to `C:/Proj/lite-Mono` required explicit approval because the active shell workspace is the older sem6 folder.
3. `--disable_photometric_loss` originally removed the photometric loss term but still allowed pose/reprojection machinery to run. This was fixed inside the Branch C folder.
4. Loading from `weights_13` originally risked restoring old Adam optimizer state. `--skip_optimizer_load` was added inside the Branch C folder.
5. Root `trainer.py` and `options.py` are already modified in the repo, but Branch C training imports and uses the copied files inside `branch_c_rgb_edge_smoothness/`.
6. The first smoke attempt failed immediately because skipping `generate_images_pred()` also skipped disparity-to-depth conversion, so LiDAR loss could not find `outputs[("depth", 0, 0)]`. The Branch C trainer now always creates depth tensors and skips only photometric warping when photometric loss is disabled.
7. Dependency check showed the active Python environment is already under `C:/Proj/miniforge3/envs/lite-mono`, with CUDA available on the RTX 4050 Laptop GPU. No dependency reinstall was needed.

## 2-Epoch Smoke Result

Status: complete.

Run script:

```text
run_branch_c_2ep_smoke_eval_laptop.ps1
```

Run folder:

```text
Marvel/runs/branch_c_rgb_edge_from_w13_b12_2ep_s001_laptop_v2/
```

Results folder:

```text
branch_c_rgb_edge_smoothness/results/branch_c_rgb_edge_from_w13_b12_2ep_s001_laptop_v2/
```

Metric summary:

| split | raw abs_rel | raw a1 | median abs_rel | median a1 |
|---|---:|---:|---:|---:|
| val | 0.1682 | 0.8465 | 0.1717 | 0.8380 |
| test | 0.1525 | 0.8498 | 0.1571 | 0.8420 |

Visual comparison:

Selected good/typical examples improved clearly against Plain Citrus in LiDAR-valid regions. The selected bad example remained weak by `a1`, but still reduced `abs_rel` substantially against Plain Citrus.

Verdict after 2 epochs:

Worth continuing. The smoke result was already stronger than the earlier selected Hybrid `weights_13` on test raw `abs_rel` (`0.1525` versus `0.1620`) and did not show visual collapse.

## 30-Epoch Result

Status: complete.

Run script:

```text
run_branch_c_30ep_eval_laptop.ps1
```

Run folder:

```text
Marvel/runs/branch_c_rgb_edge_from_w13_b12_30ep_s001_laptop/
```

Results folder:

```text
branch_c_rgb_edge_smoothness/results/branch_c_rgb_edge_from_w13_b12_30ep_s001_laptop/
```

Final checkpoint evaluated:

```text
weights_29
```

Metric summary:

| model/checkpoint | split | raw abs_rel | raw a1 | median abs_rel | median a1 |
|---|---|---:|---:|---:|---:|
| earlier Hybrid `weights_13` | val | 0.1716 | 0.8131 | 0.1746 | 0.8160 |
| Branch C 30ep `weights_29` | val | 0.1561 | 0.8668 | 0.1581 | 0.8640 |
| earlier Hybrid `weights_13` | test | 0.1620 | 0.8149 | 0.1677 | 0.8159 |
| Branch C 30ep `weights_29` | test | 0.1399 | 0.8733 | 0.1436 | 0.8675 |

Visual interpretation:

The final Branch C panels show clear improvement over Plain Citrus on selected good and typical examples. Error maps are substantially darker in LiDAR-valid tree/ground regions. The selected bad example remains a hard case and still has poor `a1`, but its `abs_rel` improves from Plain Citrus `1.595` to Branch C `0.628`.

Training-curve interpretation:

Training and validation curves are noisy but healthy. `de/abs_rel` trends downward, `da/a1` trends upward, and there is no obvious loss explosion or collapse in the final run. The final epoch is strong, but this does not prove it is the best checkpoint.

Verdict:

Branch C is the strongest result so far by final val/test metrics. This was not a wasted run. The RGB edge-aware smoothness plus LiDAR-supervised training objective appears to be a genuinely useful improvement over the earlier hybrid checkpoint.

Open risk:

Resolved by checkpoint sweep below. Final `weights_29` is strong, but it is not the only competitive checkpoint.

## Checkpoint Sweep Result

Status: complete.

Sweep script:

```text
run_branch_c_checkpoint_sweep_laptop.ps1
```

Sweep output folder:

```text
branch_c_rgb_edge_smoothness/results/branch_c_rgb_edge_from_w13_b12_30ep_s001_laptop/checkpoint_sweep/
```

Files:

```text
val_sweep_summary.csv
val_sweep_summary.json
test_confirm_summary.csv
test_confirm_summary.json
checkpoint_sweep.log
visuals/weights_24_baseline_vs_branch_c_val/
visuals/weights_24_baseline_vs_branch_c_test/
```

Validation sweep:

All 30 checkpoints, `weights_0` through `weights_29`, were evaluated on the full validation split.

Top validation checkpoints by raw `abs_rel`:

| checkpoint | val raw abs_rel | val raw a1 | val median abs_rel | val median a1 |
|---|---:|---:|---:|---:|
| `weights_22` | 0.1530 | 0.8664 | 0.1574 | 0.8634 |
| `weights_24` | 0.1531 | 0.8673 | 0.1562 | 0.8641 |
| `weights_14` | 0.1539 | 0.8636 | 0.1595 | 0.8601 |
| `weights_28` | 0.1551 | 0.8671 | 0.1580 | 0.8642 |
| `weights_18` | 0.1552 | 0.8647 | 0.1577 | 0.8627 |
| `weights_29` | 0.1561 | 0.8668 | 0.1581 | 0.8640 |

Validation interpretation:

The final epoch is not the absolute best validation checkpoint, but it is close. The strongest validation region is late training, around `weights_22` to `weights_29`, not the early or middle epochs. This is different from the earlier hybrid run where a much earlier checkpoint was clearly better than the final checkpoint.

Test confirmation:

The sweep test-confirmed validation top candidates plus final `weights_29`: `weights_14`, `weights_18`, `weights_22`, `weights_24`, and `weights_29`.

| checkpoint | test raw abs_rel | test raw a1 | test median abs_rel | test median a1 |
|---|---:|---:|---:|---:|
| `weights_24` | 0.1384 | 0.8694 | 0.1437 | 0.8657 |
| `weights_22` | 0.1393 | 0.8672 | 0.1455 | 0.8658 |
| `weights_29` | 0.1399 | 0.8733 | 0.1436 | 0.8675 |
| `weights_14` | 0.1412 | 0.8654 | 0.1466 | 0.8627 |
| `weights_18` | 0.1416 | 0.8664 | 0.1457 | 0.8644 |

Selection interpretation:

Strict validation-only raw `abs_rel` selection points to `weights_22`.

The best balanced checkpoint is `weights_24`: it is essentially tied with `weights_22` on validation raw `abs_rel`, is best on validation median `abs_rel`, and gives the best test raw `abs_rel`.

Final `weights_29` remains highly competitive and wins test median-scaled `abs_rel` and `a1`, but it is slightly weaker than `weights_24` on raw-scale `abs_rel`. Since this project cares about metric depth from LiDAR-supervised training, `weights_24` is the most practical selected checkpoint for Branch C unless we decide to use a strictly validation-raw-only rule.

Final verdict after sweep:

Branch C is a real improvement. The selected-late checkpoint region improves substantially over the earlier Hybrid `weights_13` and over Plain Citrus. The sweep did not reveal overfitting collapse; instead, it showed a late plateau where `weights_22`, `weights_24`, `weights_28`, and `weights_29` are all strong. The recommended checkpoint to carry forward is `weights_24`, with `weights_22` recorded as the strict validation-raw winner and `weights_29` retained as the strong final-epoch comparison.

Selected-checkpoint visual note:

Additional Plain Citrus versus Branch C panels were generated for the recommended `weights_24` checkpoint. The selected typical/good panels visibly reduce LiDAR-valid error against Plain Citrus. The selected bad panel remains a hard failure by `a1`, but its `abs_rel` improves from Plain Citrus `1.595` to Branch C `0.626`.

Direct `weights_24` versus `weights_29` panels:

Same-image raw plus median-scaled comparison panels were generated for the recommended checkpoint and the final checkpoint:

```text
checkpoint_sweep/visuals/weights24_vs_weights29_val/
checkpoint_sweep/visuals/weights24_vs_weights29_test/
```

Interpretation:

The two checkpoints are visually very close. `weights_24` is preferred for aggregate raw metric depth, while `weights_29` remains a strong final-epoch comparison and can be slightly better on some median-scaled selected examples. This supports carrying `weights_24` forward as the selected checkpoint without treating `weights_29` as a failed model.
