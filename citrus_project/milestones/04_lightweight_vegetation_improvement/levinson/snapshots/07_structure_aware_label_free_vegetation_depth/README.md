# Snapshot 07: Structure-Aware Label-Free Vegetation Depth

Status: completed design note, CUDA smoke, 250-step pilot, full 30-epoch fair run, validation-first checkpoint selection, full validation/test evaluation, and visual packaging.

Conclusion: `promising mixed / strongest Levinson label-free candidate so far`. Snapshot 07 is a real method-level change and the best Levinson result numerically, but the qualitative full-frame depth is still not clean enough to call the visual problem solved.

## Method

Training-supervision label: `structure-aware RGB-teacher-guided label-free self-supervised adaptation`.

Snapshot 07 builds from the active Snapshot 05/06 teacher-anchor root code and adds two training-only structure signals:

- reliable-boundary teacher anchoring: RGB image gradients and frozen teacher disparity gradients are combined into a soft boundary-reliability map, then teacher structure, gradient, and ranking losses are boosted at those reliable tree/ground/plant boundaries
- RGB-only sky/far pseudo-structure: a conservative sky-like confidence map from color, brightness, saturation, and top-image position adds a scale-free ordinal loss that encourages confident sky/far pixels to be farther than lower-scene reference pixels

This targets Snapshot 05 `weights_19` visual failures directly: vegetation blobs, over-smoothing, weak tree-ground boundaries, sky/far-canopy confusion, and weak full-image qualitative depth.

This is more than a small config tweak. It changes the loss computation, adds new RGB-derived masks/maps, changes teacher weighting spatially, adds a new ordinal sky/far term, adds diagnostics for the new signals, and adds Snapshot 07 checkpoint-selection tooling.

## Label-Free Scope

Training uses only Citrus RGB video frames, camera intrinsics, predicted poses, and frozen RGB-only Lite-Mono teacher predictions. It does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as a training loss or training mask.

Citrus labels and valid masks are used only for evaluation.

Inference remains unchanged and lightweight: one RGB image goes through the Lite-Mono student encoder/depth decoder. The teacher, PoseNet, boundary reliability maps, sky/far maps, ordinal loss, and diagnostics are training-only.

## Commands

Command scripts:

```text
commands/train_smoke.ps1
commands/train_250step_pilot.ps1
commands/train_full.ps1
commands/run_checkpoint_selection.ps1
commands/render_visuals.ps1
commands/render_diagnostics.ps1
```

Full run command used the same fair setup as B0/Snapshot 05: batch size 12, 30 epochs, seed 0, Citrus prepared split, ImageNet encoder pretrain, and no depth-label training leakage.

For exact full-run Snapshot 07 weights and heuristic thresholds, use `config/opt.json` and `diagnostics/full_run_last_logged.json` as the source of truth. The copied command scripts preserve runnable command templates but contain later stricter sky/far and boundary arguments that do not match the archived completed-run `opt.json`.

## Paths

Snapshot package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/
```

Full run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/structure_aware_label_free_vegetation_depth_b12_30ep_full/
```

Validation-selected checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/structure_aware_label_free_vegetation_depth_b12_30ep_full/models/weights_25/
```

Generated evidence:

```text
local_evidence/checkpoint_selection/
local_evidence/visuals/comparison_panels/
local_evidence/visuals/plain_inference_depth_outputs/
local_evidence/visuals/structure_diagnostic_maps/
```

`local_evidence/` is generated evidence and is ignored. Compact summaries are copied into `results/` and `diagnostics/`.

## Gate Evidence

CUDA one-step smoke passed with finite losses and non-trivial new signals:

- `structure_boundary/mean/0` about `0.00370`, ratio about `0.00434`
- `structure_sky/mean/0` about `0.1757`, ratio about `0.2441`
- `sky_far/loss/0` about `0.9340`

250-step pilot passed and improved both first-100 validation median-scaled metrics over the same-budget no-mask ImageNet-pretrain control:

| run | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| no-mask control, 250 steps | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Snapshot 07 pilot, 250 steps | 0.9044 | 0.0000 | 0.5497 | 0.3712 |

Pilot diagnostics at step 200 were non-trivial and finite:

- `structure_boundary/mean/0` about `0.0050`, ratio about `0.00705`
- `structure_sky/mean/0` about `0.1747`, ratio about `0.2463`
- `sky_far/valid_image_ratio/0` was `1.0`
- `sky_far/separation_mean/0` about `2.23`

This justified one full fair 30-epoch run.

## Metrics

Snapshot 07 checkpoint selection evaluated all `weights_0` through `weights_29` on full validation and selected `weights_25` without test access. Rule: choose the lowest validation median-scaled `abs_rel` among checkpoints with validation median-scaled `a1 >= B0_val_a1 - 0.02`; test was run only after selection.

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 `weights_19` | val | 0.7389 | 0.0177 | 0.4447 | 0.5915 |
| Snapshot 05 `weights_29` | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 06 selected `weights_25` | val | 0.7347 | 0.0166 | 0.4493 | 0.5925 |
| Snapshot 07 selected `weights_25` | val | 0.7265 | 0.0167 | 0.4344 | 0.5927 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 `weights_19` | test | 0.7391 | 0.0144 | 0.3947 | 0.6476 |
| Snapshot 05 `weights_29` | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 06 selected `weights_25` | test | 0.7310 | 0.0148 | 0.4076 | 0.6359 |
| Snapshot 07 selected `weights_25` | test | 0.7297 | 0.0130 | 0.3840 | 0.6539 |

Interpretation:

- Snapshot 07 beats B0 and Snapshot 05 `weights_19` on test median-scaled `abs_rel`.
- Snapshot 07 improves test median-scaled `a1` over Snapshot 05 `weights_19`.
- Snapshot 07 nearly matches original Lite-Mono on test median-scaled `abs_rel`, trailing by about `0.0004`, while strongly improving test median-scaled `a1`.
- Snapshot 07 slightly trails B0 on test median-scaled `a1`.

## Visuals

Generated visual evidence includes:

```text
local_evidence/visuals/comparison_panels/original_vs_snapshot07_val_full/
local_evidence/visuals/comparison_panels/original_vs_snapshot07_test_full/
local_evidence/visuals/comparison_panels/b0_vs_snapshot07_val_full/
local_evidence/visuals/comparison_panels/b0_vs_snapshot07_test_full/
local_evidence/visuals/comparison_panels/snapshot05w19_vs_snapshot07_val_full/
local_evidence/visuals/comparison_panels/snapshot05w19_vs_snapshot07_test_full/
local_evidence/visuals/plain_inference_depth_outputs/
local_evidence/visuals/structure_diagnostic_maps/
```

Qualitative judgment: promising mixed. Valid-mask comparison panels often support the metric gain, and some plant/ground regions look more stable than Snapshot 05. Full-image plain inference still shows smooth vegetation masses and occasional poor sky/far-canopy behavior, especially in failure cases. Snapshot 07 is a serious paper candidate numerically, but needs either better qualitative selection/diagnosis or one more principled visual-structure improvement before being presented as a clean visual solution.

## Code State

Changed tested files are copied into `code/`:

```text
code/options.py
code/trainer.py
code/render_teacher_structure_diagnostics.py
code/render_selected_checkpoint_inference_visuals.py
code/run_snapshot07_checkpoint_selection.py
patches/final_method.diff
```

Root code now remains active on Snapshot 07 structure-aware teacher-anchor workbench code. Snapshot `code/` folders are archival copies and are not imported automatically by `train.py`.
