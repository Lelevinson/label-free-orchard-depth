# Teacher Anchor Checkpoint Selection: Snapshots 05 and 06

Date: 2026-05-18

Status: completed validation-first checkpoint sweep. No new training was run.

Packaging update: Snapshot 05 `weights_19` visual and plain-inference outputs were generated on 2026-05-19. A clearer professor-facing visual diagnosis package was then generated for the same checkpoint. No new training was run for either packaging step.

## Purpose

This note answers whether the teacher-anchored runs have an earlier checkpoint with a better publishable tradeoff than final `weights_29`.

The sweep covers:

- Snapshot 05: `teacher_structure_regularization_b12_30ep_full`
- Snapshot 06: `teacher_anchor_stabilization_b12_30ep_rank005_no_texture`

All saved `weights_0` through `weights_29` checkpoints were evaluated on full validation. Test was used only after validation selection.

## Selection Rule

Validation-only rule:

1. Use B0 validation median-scaled `a1=0.6107`.
2. Define "close to B0 a1" as within `0.02` absolute: `a1 >= 0.5907`.
3. For each run, select the checkpoint with the lowest full-validation median-scaled `abs_rel` among checkpoints passing that `a1` threshold.
4. If no checkpoint passes the threshold, fall back to the lowest validation median-scaled `abs_rel` and mark the a1 condition failed.
5. Evaluate only the selected checkpoint from each run on test.

This rule was chosen before looking at test results.

Machine-readable rule:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/selection_rule.json
```

## Commands

Run script:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/run_teacher_anchor_checkpoint_selection.py
```

Command file:

```text
commands/run_sweep.ps1
```

Selected Snapshot 05 `weights_19` visual command file:

```text
commands/render_snapshot05_weights19_visuals.ps1
```

Professor-facing visual diagnosis command file:

```text
commands/render_weights19_professor_visual_diagnostics.ps1
```

Professor-facing visual diagnosis script:

```text
scripts/render_weights19_professor_visual_diagnostics.py
```

## Output Paths

Main sweep output:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/
```

The `local_results/` directory contains generated evaluator output and is ignored by this machine's `.git/info/exclude`; the README and command scripts are the compact tracked handoff.

Important files:

```text
validation_sweep.csv
validation_sweep.json
selected_validation_checkpoints.csv
selected_validation_checkpoints.json
selected_test_results.csv
selected_test_results.json
comparison_summary.csv
comparison_summary.json
```

Per-checkpoint validation result folders:

```text
validation/snapshot05/weights_*/
validation/snapshot06/weights_*/
```

Test result folders for selected checkpoints only:

```text
test_selected/snapshot05/weights_19/
test_selected/snapshot06/weights_25/
```

Selected Snapshot 05 `weights_19` visual package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
```

Visual package contents:

```text
comparison_panels/original_vs_weights19_val_full/
comparison_panels/b0_vs_weights19_val_full/
comparison_panels/weights29_vs_weights19_val_full/
comparison_panels/original_vs_weights19_test_full/
comparison_panels/b0_vs_weights19_test_full/
comparison_panels/weights29_vs_weights19_test_full/
plain_inference_depth_outputs/
result_summary.md
```

The plain inference folder contains actual selected-checkpoint RGB, raw-depth, median-scaled-depth, disparity, panel, and NPZ array outputs for representative validation and test samples.

Professor-facing Snapshot 05 `weights_19` visual diagnosis package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/
```

Tracked compact summary:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/weights19_professor_visual_diagnosis_summary.md
```

Contents:

```text
full_image_qualitative/
valid_mask_evaluation/
cropped_masked_evaluation/
weights29_vs_weights19/
plain_inference/
sample_selection.csv
sample_selection.json
visual_diagnosis.md
```

## Validation Selection

| run | selected checkpoint | val raw abs_rel | val raw a1 | val median abs_rel | val median a1 | passed B0-close a1 |
|---|---|---:|---:|---:|---:|---|
| Snapshot 05 | `weights_19` | 0.7389 | 0.0177 | 0.4447 | 0.5915 | yes |
| Snapshot 06 | `weights_25` | 0.7347 | 0.0166 | 0.4493 | 0.5925 | yes |

Validation-only caveat:

| run | lowest validation abs_rel checkpoint | val median abs_rel | val median a1 | decision |
|---|---|---:|---:|---|
| Snapshot 05 | `weights_7` | 0.3716 | 0.5110 | not selected; a1 too far below B0-close threshold |
| Snapshot 06 | `weights_7` | 0.3882 | 0.5007 | not selected; a1 too far below B0-close threshold |

The early `weights_7` checkpoints are tempting on validation `abs_rel`, but they fail the pre-declared threshold-accuracy condition. They were not evaluated on test.

## Test Results For Selected Checkpoints

| model | split | raw abs_rel | raw a1 | median abs_rel | median a1 |
|---|---|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 `weights_29` | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 06 `weights_29` | val | 0.7375 | 0.0165 | 0.4578 | 0.5993 |
| Snapshot 05 selected `weights_19` | val | 0.7389 | 0.0177 | 0.4447 | 0.5915 |
| Snapshot 06 selected `weights_25` | val | 0.7347 | 0.0166 | 0.4493 | 0.5925 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 `weights_29` | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 06 `weights_29` | test | 0.7348 | 0.0150 | 0.4168 | 0.6418 |
| Snapshot 05 selected `weights_19` | test | 0.7391 | 0.0144 | 0.3947 | 0.6476 |
| Snapshot 06 selected `weights_25` | test | 0.7310 | 0.0148 | 0.4076 | 0.6359 |

## Interpretation

Snapshot 05 `weights_19` is the best validation-selected teacher-anchor checkpoint under the rule. On test it:

- improves B0 median-scaled `abs_rel` from `0.4889` to `0.3947`
- keeps most of B0 median-scaled `a1`: `0.6476` vs `0.6582`
- improves final Snapshot 05 `weights_29` test median-scaled `abs_rel`: `0.4132` to `0.3947`
- slightly improves final Snapshot 05 `weights_29` test median-scaled `a1`: `0.6463` to `0.6476`
- gets close to original Lite-Mono test median-scaled `abs_rel` (`0.3836`) but does not beat it
- beats original Lite-Mono test median-scaled `a1` by a large margin: `0.6476` vs `0.4989`

Visual inspection of the selected-checkpoint package is mixed but supportive: good and typical cases show broad relative-structure behavior consistent with the aggregate `abs_rel` improvement, while failure/largest-drop cases still show smooth maps and over-correction around vegetation and occlusion regions. The professor-facing diagnosis makes this caveat explicit by separating full-image qualitative depth from valid-mask-only evaluation behavior. This is evidence for `weights_19` as the main Snapshot 05 checkpoint, not a claim of a clean visual win.

Snapshot 06 `weights_25` also improves over B0 on median-scaled `abs_rel`, but it is weaker than Snapshot 05 `weights_19` on both selected-checkpoint test median-scaled metrics.

## Answer To The Research Question

Yes, teacher-anchored regularization can produce a validation-selected checkpoint that clearly improves over B0 while keeping most of B0's `a1`.

The best evidence is Snapshot 05 `weights_19`: test median-scaled `abs_rel=0.3947` and test median-scaled `a1=0.6476`. This is much better than B0 on `abs_rel` and only slightly below B0 on `a1`.

However, it still does not beat original Lite-Mono on test median-scaled `abs_rel`: `0.3947` vs original `0.3836`. It gets meaningfully closer than `weights_29`, while preserving the adapted model's much stronger `a1`.

Conclusion:

```text
checkpoint selection strengthens Snapshot 05; Snapshot 05 weights_19 is the best current Levinson label-free teacher-anchor checkpoint, but not a clean win over original Lite-Mono on median-scaled abs_rel
```

Use Snapshot 05 `weights_19` as the main Levinson label-free teacher-anchor result in paper tables unless a later, explicitly documented validation-selection protocol supersedes it. Keep `weights_29` as the final-epoch ablation/evidence point because the final epochs appear to trade off or over-drift relative to the selected checkpoint.
