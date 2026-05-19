# Levinson Milestone 4 Workstream

This folder collects Levinson's Milestone 4 progress so the completed baseline and later improvement stages stay together.

Read this file first for this workstream, then open only the needed snapshot README.

Levinson's workstream is the self-supervised Milestone 4 path. Prioritize RGB-only training objectives or constraints that do not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED depth as a training loss. If a future idea needs label supervision, create or move it to a clearly separate hybrid branch instead of mixing it into this workstream.

Inference should remain RGB-only unless a future note explicitly says otherwise. Training-supervision claims must be labeled honestly when comparing against Marvel's supervised/hybrid workstream.

## Contents

```text
results/
runs/
snapshots/
```

Current moved result folder:

```text
results/plain_litemono_imagenet_b12_30ep_final_weights29/
```

Large generated results for Snapshots 05/06 are now kept with their relevant evidence owner instead of the shared `results/` folder:

```text
snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full/
snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/
snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/
checkpoint_selection/teacher_anchor_snapshot05_06/local_results/
```

These bulky local-evidence folders are ignored by the shared `.gitignore`; this checkout also has matching `.git/info/exclude` rules as a personal safety net. Compact snapshot READMEs/results remain available for handoff.

Current local ignored run folder:

```text
runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/
runs/teacher_structure_regularization_b12_30ep_full/
runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/
```

Baseline snapshot:

```text
snapshots/00_plain_citrus_baseline/
```

This is B0: the plain Lite-Mono Citrus baseline from ImageNet encoder pretrain. It includes copied inference weights, command scripts, result CSV/JSON files, visual panels, `config/opt.json`, and a no-code-changes marker.

Tested improvement snapshots:

```text
snapshots/01_photometric_confidence_masking/
snapshots/02_rgb_edge_structure_preserving_loss/
snapshots/03_soft_confidence_multiplier/
snapshots/04_vegetation_general_temporal_cross_view_consistency/
snapshots/05_teacher_anchored_relative_structure_regularization/
snapshots/06_teacher_anchor_stabilization/
```

`01_photometric_confidence_masking/` is the first self-supervised Milestone 4 method gate. It adds disabled-by-default photometric-confidence masking on top of existing automasking, copies tested `trainer.py` and `options.py`, records smoke and 250-step gate commands, and concludes `uncertain / do not scale yet`.

`02_rgb_edge_structure_preserving_loss/` is the conservative RGB-edge structure-loss gate. It remained self-supervised and inference-neutral, but the 250-step first-100 validation result worsened both median-scaled `abs_rel` and `a1` versus the same-budget no-mask control, so it concludes `stop`.

`03_soft_confidence_multiplier/` is the independent backup confidence gate. It tested a mild multiplier instead of normalized confidence reweighting, but still worsened median-scaled `a1` versus the same-budget no-mask control, so it concludes `stop`.

`04_vegetation_general_temporal_cross_view_consistency/` is the coherent temporal cross-view method-family gate. It implements training-only temporal geometry, visibility, texture ambiguity weighting, and feature consistency while keeping inference RGB-only and self-supervised. It was technically stable after revising source-frame predictions into a stop-gradient teacher, but its 250-step ablations are weak negative evidence. The best branch, geometry + texture ambiguity, only slightly improved first-100 median-scaled `a1` over the same-budget control (`0.3605` vs `0.3577`) while still worsening median-scaled `abs_rel` (`0.5651` vs `0.5634`), so it concludes `stable but weak negative; do not scale`.

The Snapshot 04 diagnostic report and next-method proposal are saved at:

```text
snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md
```

`05_teacher_anchored_relative_structure_regularization/` is the full teacher-anchored label-free run. It uses the normal self-supervised Citrus video objective plus a frozen RGB-only Lite-Mono teacher from `weights/lite-mono/` for scale-invariant structure, gradient, and ranking regularization. It does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses or training masks. It completed the full 30-epoch fair B0 recipe and concludes `continue / promising mixed`: it improves B0's raw and median-scaled `abs_rel`, keeps most of B0's median-scaled `a1`, and beats original Lite-Mono on median-scaled `a1`, but still trails original Lite-Mono on median-scaled `abs_rel`.

Snapshot 05 final metrics:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |

Snapshot 05 package:

```text
snapshots/05_teacher_anchored_relative_structure_regularization/
```

`06_teacher_anchor_stabilization/` is a deliberate Snapshot 05 ablation. It reuses the same frozen RGB-only teacher implementation but reduces `--teacher_ranking_weight` from `0.02` to `0.005` and removes `--teacher_texture_ambiguity_emphasis`. It completed the full 30-epoch fair B0 recipe. Validation is slightly better than Snapshot 05 (`median abs_rel=0.4578`, `a1=0.5993`), but test is slightly worse (`median abs_rel=0.4168`, `a1=0.6418`), so it concludes `promising mixed / marginal stabilization`, not a clean replacement.

Snapshot 06 package:

```text
snapshots/06_teacher_anchor_stabilization/
```

Teacher-anchor checkpoint-selection note:

```text
checkpoint_selection/teacher_anchor_snapshot05_06/README.md
```

This validation-first sweep evaluated Snapshot 05 and Snapshot 06 `weights_0` through `weights_29` on full validation, then evaluated only the selected checkpoints on test. The rule selected the lowest validation median-scaled `abs_rel` checkpoint whose validation median-scaled `a1` stayed within `0.02` absolute of B0. Snapshot 05 `weights_19` is the strongest current label-free teacher-anchor checkpoint: test median-scaled `abs_rel=0.3947`, `a1=0.6476`. It improves B0 strongly on `abs_rel`, keeps most of B0's `a1`, and gets close to original Lite-Mono on median-scaled `abs_rel`, but does not beat original.

Selected Snapshot 05 `weights_19` visual and plain inference outputs:

```text
snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
```

This package contains original-vs-`weights_19`, B0-vs-`weights_19`, and `weights_29`-vs-`weights_19` panels for validation and test, plus plain RGB/depth/disparity outputs from the selected checkpoint. It was generated without new training. Visuals are mixed but support using `weights_19` as the main Snapshot 05 table result: broad structure is often better, but smoothness and vegetation/occlusion failures remain.

Professor-facing Snapshot 05 `weights_19` diagnosis:

```text
snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/visual_diagnosis.md
```

Use this for discussion. It separates full-image qualitative depth from valid-LiDAR-only evaluation behavior and is explicit that `weights_19` is numerically promising but not visually solved or paper-polished.

After the 01/02/03 gates were packaged, the live root `options.py` and `trainer.py` were restored to the shared baseline state for collaboration. Snapshot 04 later left the live root as the active temporal-cross-view method branch. Snapshot 05 superseded it, and Snapshot 06 reuses that same teacher-anchored implementation. Live root `options.py`, `trainer.py`, `render_teacher_structure_diagnostics.py`, and the visual comparison helper currently remain as the active teacher-anchored method branch. The tested experimental code remains in each snapshot's `code/` folder for reproducibility or later reapplication.

The `runs/` folder is ignored by Git because it can contain optimizer states, pose-network weights, and TensorBoard logs. The legacy B0 folder under `results/` remains tracked for existing references, but new compact evidence should live in the relevant snapshot or checkpoint-selection folder while bulky generated outputs stay under ignored `local_evidence/` or `local_results/`.

Pre-Snapshot07 hygiene audit:

```text
pre_snapshot07_repo_audit.md
```

This note records the current active root-code state, local-evidence layout, ignored artifact policy, and verification steps before the next Levinson method attempt.

Do not edit Marvel's folder from this workstream without explicit approval.

## Code Snapshot Rule

When a tested Milestone 4 stage changes Python code, copy the tested files into that stage snapshot under `code/`.

Use clear relative paths when useful:

```text
snapshots/01_method_name/code/trainer.py
snapshots/01_method_name/code/options.py
snapshots/01_method_name/code/layers.py
snapshots/01_method_name/code/networks/depth_decoder.py
```

For stages with no stage-specific code changes, keep a simple marker such as:

```text
snapshots/00_plain_citrus_baseline/code/NO_CODE_CHANGES.txt
```
