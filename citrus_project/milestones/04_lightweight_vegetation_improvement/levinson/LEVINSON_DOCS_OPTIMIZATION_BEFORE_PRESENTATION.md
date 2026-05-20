# Levinson Docs Optimization Before Presentation

Date: 2026-05-20

Scope: documentation-only optimization pass for `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/`. No training, experiments, model-code edits, root-code edits, push, folder reorganization, or Marvel-folder work was performed.

## Markdown Files Checked

Current navigation / source-of-truth docs:

- `README.md`
- `DOCUMENTATION_INDEX.md`
- `ACTIVE_ROOT_CODE_STATE.md`
- `snapshots/README.md`
- `SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md`
- `AGENTS.md` Levinson references

Snapshot-specific historical docs:

- `snapshots/00_plain_citrus_baseline/README.md`
- `snapshots/01_photometric_confidence_masking/README.md`
- `snapshots/02_rgb_edge_structure_preserving_loss/README.md`
- `snapshots/03_soft_confidence_multiplier/README.md`
- `snapshots/04_vegetation_general_temporal_cross_view_consistency/README.md`
- `snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md`
- `snapshots/04_vegetation_general_temporal_cross_view_consistency/results/ablation_summary.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/README.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/diagnostic_report.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/weights19_professor_visual_diagnosis_summary.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/results/result_summary.md`
- `snapshots/06_teacher_anchor_stabilization/README.md`
- `snapshots/06_teacher_anchor_stabilization/DESIGN_NOTE.md`
- `snapshots/06_teacher_anchor_stabilization/results/result_summary.md`
- `snapshots/07_structure_aware_label_free_vegetation_depth/README.md`
- `snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md`
- `snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md`

Audit/checkpoint-selection docs:

- `checkpoint_selection/teacher_anchor_snapshot05_06/README.md`
- `pre_snapshot07_repo_audit.md`
- `SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md`
- `LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md`

Old plans that are no longer active:

- `overnight_experiment_plan.md`
- `snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md`
- `snapshots/06_teacher_anchor_stabilization/DESIGN_NOTE.md`
- `snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md`

Ignored local evidence Markdown observed but intentionally not edited:

- `snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/visual_diagnosis.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/result_summary.md`
- `snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/result_summary.md`

Direct Levinson-level CSV/JSON summaries:

- none found directly under `levinson/`; compact CSV/JSON summaries live inside snapshot `results/`, `diagnostics/`, or checkpoint-selection folders.

## Current Source-Of-Truth Docs

Use this hierarchy for presentation preparation:

1. `README.md` - main workstream doorway.
2. `DOCUMENTATION_INDEX.md` - AI/human navigation map.
3. `ACTIVE_ROOT_CODE_STATE.md` - current root-code state.
4. `snapshots/07_structure_aware_label_free_vegetation_depth/README.md` - current lead method.
5. `snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md` - current lead result summary.
6. `SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md` - snapshot-folder consistency audit.

Current claims to preserve:

- Snapshot 07 is the current lead Levinson label-free candidate.
- Snapshot 05 `weights_19` is previous/pre-Snapshot07 best.
- Snapshot 06 is marginal/mixed.
- Snapshot 07 is numerically strongest but visually mixed.
- Root `trainer.py` and `options.py` are active Snapshot 07 workbench code, not original Lite-Mono baseline.
- Snapshot `code/` folders are frozen archival copies, not automatically imported by `train.py`.

## Historical Docs And Status Notes

Status notes were added or confirmed for:

- `overnight_experiment_plan.md`: marked as historical planning provenance, superseded by completed snapshots and Snapshot 07.
- `snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md`: marked as historical diagnostic/proposal note.
- `snapshots/06_teacher_anchor_stabilization/DESIGN_NOTE.md`: marked as historical completed design note and marginal/mixed ablation.
- `snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md`: marked as historical design note; current results live in README/final summary.
- `pre_snapshot07_repo_audit.md`: already had a supersession note from the previous audit and remains historical.

## Contradictions Fixed

This pass fixed or reinforced:

- The Levinson README now points to `DOCUMENTATION_INDEX.md`.
- `AGENTS.md` now lists `DOCUMENTATION_INDEX.md` as the Levinson AI/human navigation map.
- Old planning/design notes now clearly say they are historical and should not be treated as current action plans.
- Snapshot 07 design-note wording now avoids conflicting with the current Snapshot 07 lead state by framing Snapshot 05 `weights_19` as best at design time.

No contradiction was found requiring changes to Snapshot 07's label-free, RGB-only inference, or visually mixed claims.

## Redundant Or Confusing Files Found

Left unchanged and documented:

- `overnight_experiment_plan.md`: old queue plan, useful provenance after adding status note.
- `pre_snapshot07_repo_audit.md`: historical root-state audit, useful for explaining why Snapshot 07 started from Snapshot 05/06 root code.
- `SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md`: overlaps partly with this file, but focuses on snapshot folder tidiness rather than the broader documentation hierarchy.
- Snapshot 05/06/07 design notes: historical, but useful for method rationale and presentation backstory.
- Ignored `local_evidence/*.md` reports: evidence artifacts, not navigation docs; left untouched to avoid changing generated evidence.
- Snapshot 00 tracked checkpoint weights and PNG panels: unusual compared with later snapshots, but intentionally preserved as compact B0 inference/visual package.
- Snapshot 07 `scripts/run_snapshot07_checkpoint_selection.py` plus copied `code/run_snapshot07_checkpoint_selection.py`: intentional runnable-script plus archival-code-copy pattern.

No file was moved. No file was deleted.

## What Was Intentionally Left Alone

- `runs/`
- `weights/`
- `local_evidence/`
- `local_results/`
- large PNG folders
- datasets
- caches
- model checkpoints
- root `trainer.py` / `options.py`
- Marvel's folder

## Ready For Presentation Preparation

Yes. The folder is safe to use for presentation preparation.

Recommended presentation reading order:

1. `DOCUMENTATION_INDEX.md`
2. `README.md`
3. `ACTIVE_ROOT_CODE_STATE.md`
4. `snapshots/07_structure_aware_label_free_vegetation_depth/README.md`
5. `snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md`
6. `snapshots/05_teacher_anchored_relative_structure_regularization/README.md`
7. `checkpoint_selection/teacher_anchor_snapshot05_06/README.md`

Recommended presentation framing:

- lead result: Snapshot 07 `weights_25`;
- previous best: Snapshot 05 `weights_19`;
- ablation: Snapshot 06;
- negative evidence: Snapshots 01-04;
- label-free training and RGB-only inference;
- visually mixed qualitative story.
