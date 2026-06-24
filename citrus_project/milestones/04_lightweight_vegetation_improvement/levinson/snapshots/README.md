# Milestone 4 Snapshots

This folder stores tidy stage snapshots for Levinson's sequential Lite-Mono + Citrus improvements.

Read this file first, then open only the stage folder needed for the task.

## Current Stages

| folder | role |
|---|---|
| `00_plain_citrus_baseline/` | B0: plain Lite-Mono Citrus baseline from ImageNet encoder pretrain |
| `01_photometric_confidence_masking/` | first self-supervised confidence-mask gate; stable but mixed, conclusion `uncertain / do not scale yet` |
| `02_rgb_edge_structure_preserving_loss/` | independent RGB-edge structure-loss gate; stable but negative, conclusion `stop` |
| `03_soft_confidence_multiplier/` | independent soft confidence backup gate; stable but negative, conclusion `stop` |
| `04_vegetation_general_temporal_cross_view_consistency/` | temporal geometry, visibility, texture ambiguity, and feature cross-view method-family gate; stable weak negative evidence, conclusion `do not scale` |
| `05_teacher_anchored_relative_structure_regularization/` | full teacher-anchored label-free self-supervised adaptation run; selected checkpoint `weights_19` was the pre-Snapshot07 best teacher-anchor candidate |
| `06_teacher_anchor_stabilization/` | reduced-ranking/no-texture stabilization of Snapshot 05; promising mixed marginal ablation, not a clean replacement |
| `07_structure_aware_label_free_vegetation_depth/` | structure-aware RGB-teacher-guided label-free method; selected checkpoint `weights_25` is the prior best / strongest-a1 reference |
| `08_feature_metric_loss/` | FeatDepth-style feature-metric loss on the S07 stack; 3-epoch gate weak/mixed (abs_rel worsened), conclusion `stop` |
| `09_tsob_boundary_uncertainty_mixture/` | TSOB-style K=2 depth-mixture loss on the S07 stack; full 30-epoch run worse than S07 on both test metrics, no visible de-blobbing, conclusion `stop` |
| `10_ema_self_teacher/` | EMA in-domain self-teacher on the S07 stack; selected checkpoint `weights_29` is the shipped label-free paper result (`abs_rel=0.3080`, `a1=0.6258` on test) |
| `11_resizing_crop_self_distillation/` | resizing-crop self-distillation on the S10 stack; killed by gate after flat-depth collapse, conclusion `negative result / stop` |

## Latest Stage

Snapshot 10 is the current shipped Levinson label-free paper result:

```text
10_ema_self_teacher/results/final_result.md
```

It builds on the S07 stack and adds an EMA in-domain self-teacher via
scale-and-shift-aware SI-log self-distillation plus a normalized structure anchor.
It remains label-free for Citrus training: no `depth_gt`, `valid_mask`, dense LiDAR,
sparse LiDAR, ZED depth, or LiDAR-derived label is used as a training loss or mask.
Inference remains the unchanged single-image RGB Lite-Mono depth network.

The selected `weights_29` checkpoint gets test median-scaled `abs_rel=0.3080`
and `a1=0.6258`, beating original Lite-Mono (`0.3836`, `0.4989`) on both
headline metrics. Visuals remain mixed and the reliability gates were near-inert,
so the conclusion is a real metric win with honest limitations.

Snapshot 11 is the latest attempted method, but it was killed by gate:

```text
11_resizing_crop_self_distillation/DESIGN_NOTE.md
```

It is paper-usable negative evidence, not the shipped method.

Current paper package:

```text
citrus_project/milestones/06_paper_package/paper/
```

Previous checkpoint-selection decision:

```text
05_teacher_anchored_relative_structure_regularization/ weights_19
```

Snapshot 05 `weights_19` was selected by the validation-only teacher-anchor checkpoint sweep and visually packaged on 2026-05-19 without new training. It is the main Snapshot 05 comparison point, not the current Levinson lead after Snapshot 07. Visual and plain inference outputs are saved under:

```text
05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
```

Snapshot 07 generated visual evidence is saved under:

```text
07_structure_aware_label_free_vegetation_depth/local_evidence/visuals/
```

`local_evidence/` folders are local generated evidence folders and are ignored by the shared `.gitignore`; this checkout also keeps matching `.git/info/exclude` rules as a personal safety net.

## Naming Rule

Use numeric, readable names:

```text
00_plain_citrus_baseline/
01_<first_method_name>/
02_<second_independent_method_name>/
03_<third_independent_method_name>/
04_<fourth_method_name>/
05_<fifth_method_name>/
06_<sixth_method_name>/
07_<seventh_method_name>/
```

Do not combine methods unless a future note explicitly approves a combined branch. Paper-style labels can be recorded inside a stage README later if useful, but folder names should stay descriptive and should not imply combined training unless the experiment actually combined methods.

## Stage Folder Rule

Each completed stage should contain one compact `README.md` plus the artifacts needed to understand or rerun that stage:

- changed code files, when that stage changes code
- a simple marker file when a completed stage has no stage-specific code changes
- exact command scripts when they are known
- checkpoint paths, and checkpoint files only when the snapshot is promoted as a compact inference package
- saved config such as `opt.json`
- result CSV/JSON files
- visual comparison panels or small visual-summary CSV/JSON files, with full panel paths recorded in the stage README when the PNGs stay in ignored run folders
- diagnostic CSV/JSON summaries when available

Avoid extra nested README files unless a subfolder becomes complicated enough to need its own map.

When a stage changes Python code, duplicate the tested `.py` files into that stage's `code/` folder. Preserve clear relative paths when useful, for example `code/trainer.py`, `code/options.py`, `code/layers.py`, or `code/networks/depth_decoder.py`.

The live root `trainer.py` and `options.py` were restored to the shared baseline state after the 01/02/03 gates were packaged. Snapshot 04 later left the live root trainer/options as the active temporal-cross-view method branch. Snapshot 05 superseded that branch, Snapshot 06 reused the teacher-anchored implementation with different flags, and Snapshot 07 now supersedes that active root workbench with structure-aware teacher/sky-far code. Root `trainer.py`, `options.py`, `render_teacher_structure_diagnostics.py`, and the visual comparison helper remain active for Snapshot 07. Tested copies and patch artifacts live in `05_teacher_anchored_relative_structure_regularization/`, `06_teacher_anchor_stabilization/`, and `07_structure_aware_label_free_vegetation_depth/`. Use each stage README and command scripts to see which method was actually enabled.

Snapshots 08 (feature-metric), 09 (TSOB), 10 (EMA self-teacher), and 11
(crop self-distillation) added further off-by-default experimental code directly
to root `options.py`/`trainer.py` and supporting network/helper files. S08, S09,
and S11 are negative results. Snapshot 10 `weights_29` is promoted as the Levinson
label-free paper result; Snapshot 07 `weights_25` remains the strongest-a1 reference.
