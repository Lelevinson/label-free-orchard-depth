# Snapshot 04: Vegetation-General Temporal Cross-View Consistency

Status: implemented and tested as a 250-step self-supervised gate. Conclusion: technically stable but weak negative evidence; do not scale.

## Method Summary

This snapshot implements a training-only method family for vegetation-heavy monocular depth:

```text
Vegetation-General Temporal Cross-View Consistency for Lightweight Monocular Depth
```

The goal is to reduce dependence on raw RGB photometric matching in repeated leaf/branch texture. Inference is unchanged: one RGB image goes through the same Lite-Mono encoder and depth decoder. PoseNet, source-frame depth prediction, geometry consistency, feature consistency, texture ambiguity maps, and visibility maps are training-only.

The method remains self-supervised. It uses monocular RGB temporal frames, camera intrinsics, predicted PoseNet transforms, predicted depths, and encoder features. It does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses. Citrus labels/masks are used only for evaluation.

Generic vegetation rationale:

- repeated local plant texture can produce misleading low photometric error
- thin leaves/branches cause occlusion and disocclusion
- RGB edges do not always align with depth edges
- correct depth should be more temporally/geometrically consistent across nearby frames than false texture matches

No citrus-specific detector, green-pixel mask, hand-labeled vegetation mask, or depth-label training signal is used.

## Source Code Changes

Root files changed and copied here:

- `code/options.py`
- `code/trainer.py`
- `code/citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_temporal_cross_view_diagnostics.py`

Changes:

- `options.py`: added disabled-by-default flags for temporal geometry, visibility filtering, texture ambiguity weighting, and feature cross-view consistency.
- `trainer.py`: added source-frame stop-gradient teacher depth/features, log-depth temporal geometry loss, projection/visibility masks, texture ambiguity maps, feature consistency, scalar JSON/CSV diagnostics, and TensorBoard/debug map logging.
- `render_temporal_cross_view_diagnostics.py`: renders PNG maps for input RGB, predicted depth, photometric error, geometry error, visibility/projection masks, texture ambiguity, and feature consistency maps.

The source-frame branch was revised after an early batch-size-12 attempt proved too slow when source depths participated in the backward graph. The tested implementation uses stop-gradient source predictions as a training-only teacher; each source frame still receives normal depth supervision when it appears as a target in other batches.

Root files remain as the active method branch after packaging. They were not restored to baseline.

## Flags

Core flags:

```text
--temporal_geo_consistency
--temporal_geo_weight
--temporal_geo_warmup_steps
--temporal_consistency_scales
--visibility_aware_geo
--visibility_cycle_threshold
--texture_ambiguity_weighting
--texture_ambiguity_weight
--feature_cross_view_consistency
--feature_consistency_weight
--feature_consistency_warmup_steps
--feature_consistency_scale
```

All flags are off by default, preserving original Lite-Mono behavior unless explicitly enabled.

## Runs

All training outputs are under:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/
```

Tested runs:

| variant | run folder |
|---|---|
| no-mask same-budget control | `plain_litemono_citrus_imagenet_pretrain_b12_250steps_seed0_control/` |
| temporal geometry | `vg_tcv_geo_teacher_b12_250steps_seed0_w015/` |
| geometry + default visibility | `vg_tcv_geo_visibility_teacher_b12_250steps_seed0_w015/` |
| geometry + strict visibility | `vg_tcv_geo_visibility_teacher_b12_250steps_seed0_w015_vthr003/` |
| geometry + texture ambiguity | `vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035/` |
| geometry + feature consistency | `vg_tcv_geo_feature_teacher_b12_250steps_seed0_w015_fw005/` |
| full reduced-feature method | `vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002/` |

Command files:

```text
commands/train_ablation_commands.ps1
commands/evaluate_val100_commands.ps1
commands/render_visual_diagnostics.ps1
```

## Evidence

Copied result summaries:

```text
results/ablation_summary.md
results/ablation_summary.csv
results/ablation_summary.json
results/*_val_lite-mono_max100_summary.json
results/*_val_lite-mono_max100_per_sample.csv
diagnostics/*_diagnostics_last_logged.json
diagnostics/*_diagnostics_last_logged.csv
local_evidence/visual_summary/
patches/final_method.diff
diagnostic_report_and_snapshot05_proposal.md
```

Qualitative maps:

```text
local_evidence/visual_summary/geo_texture_diagnostic_maps/
local_evidence/visual_summary/full_diagnostic_maps/
```

Standard control-vs-method panel summaries:

```text
local_evidence/visual_summary/geo_texture_original_vs_adapted_selection_summary.json
local_evidence/visual_summary/geo_texture_original_vs_adapted_selection_summary.csv
local_evidence/visual_summary/full_original_vs_adapted_selection_summary.json
local_evidence/visual_summary/full_original_vs_adapted_selection_summary.csv
```

Full panel PNGs remain in the ignored run folders:

```text
runs/vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035/visual_compare_control_vs_geo_texture_val100_step_250/
runs/vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002/visual_compare_control_vs_full_val100_step_250/
```

## Metric Summary

First-100 validation at step 250:

| variant | median-scaled abs_rel | median-scaled a1 | raw abs_rel | raw a1 |
|---|---:|---:|---:|---:|
| same-budget no-mask control | 0.5634 | 0.3577 | 0.9099 | 0.0000 |
| temporal geometry | 0.5666 | 0.3597 | 0.9033 | 0.0000 |
| geometry + default visibility | 0.5688 | 0.3581 | 0.9030 | 0.0000 |
| geometry + strict visibility `0.003` | 0.5884 | 0.3107 | 0.9027 | 0.0000 |
| geometry + texture ambiguity | 0.5651 | 0.3605 | 0.9028 | 0.0000 |
| geometry + feature consistency | 0.5581 | 0.3373 | 0.9129 | 0.0000 |
| full, reduced feature weight | 0.5755 | 0.3503 | 0.9366 | 0.0000 |

## Interpretation

What worked:

- The implementation is stable at batch size 12 after the source-frame teacher revision.
- Projection masks are nonempty, usually about 98% projection-valid at the logged steps.
- Texture ambiguity maps are active, with about 35% high-ambiguity pixels and mean photometric multiplier around 0.91 for the tested texture branch.
- Feature consistency is active and well covered, with about 97% mask coverage.

What failed or stayed weak:

- Temporal geometry alone only gives a tiny `a1` gain and slightly worsens median-scaled `abs_rel`.
- Default visibility threshold `0.35` is nearly a no-op because geometry disagreement is much smaller than that.
- Strict visibility threshold `0.003` makes the mask real but too sparse and hurts metrics badly.
- Feature consistency improves median-scaled `abs_rel` but clearly hurts median-scaled `a1`.
- Full stacking is negative even with reduced feature weight.

Conclusion:

```text
stable but weak negative evidence; do not scale
```

The best branch is temporal geometry plus texture ambiguity weighting, but the gain is tiny (`a1=0.3605` vs control `0.3577`) and median-scaled `abs_rel` is still worse than the control (`0.5651` vs `0.5634`). Feature consistency improved `abs_rel` but hurt `a1`, strict visibility became harmful, and full stacking was negative. Keep this snapshot as coherent, technically working, weak negative Milestone 4 evidence.

The follow-up diagnostic report and Snapshot 05 proposal are saved in:

```text
diagnostic_report_and_snapshot05_proposal.md
```
