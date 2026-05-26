# Levinson Documentation Index

Status: current navigation index for Levinson's Milestone 4 folder after Snapshot 07 packaging.

Use this file to decide what to read. Do not treat every Markdown file under this folder as current guidance; many are preserved historical plans, diagnostic reports, or snapshot-local evidence notes.

## Start Here

1. `README.md`
   - Main Levinson workstream doorway.
   - Summarizes B0, Snapshots 01-07, current lead result, evidence ownership, and rules for bulky outputs.
2. `ACTIVE_ROOT_CODE_STATE.md`
   - Current root-code policy.
   - Root `trainer.py` and `options.py` are active Snapshot 07 workbench code, not original Lite-Mono baseline.
   - Snapshot `code/` folders are frozen archival copies and are not imported automatically by `train.py`.
3. `snapshots/README.md`
   - Compact map of all snapshot folders.
   - Use this before opening individual snapshot folders.
4. `archive/research_process_notes/REPO_TIDY_AUDIT.md`
   - Archived cleanup audit and safe documentation optimization report.
   - Use this before deleting, archiving, or consolidating old notes, generated files, or presentation assets.

## Current Lead Method

Snapshot 07 is the current lead Levinson label-free candidate:

```text
snapshots/07_structure_aware_label_free_vegetation_depth/README.md
snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md
```

Use these for current method/result framing:

- label-free Citrus training;
- RGB-only Lite-Mono DepthNet inference;
- selected `weights_25`;
- test median-scaled `abs_rel=0.3840`, `a1=0.6539`;
- numerically strongest Levinson result so far;
- qualitative visuals remain mixed.

Snapshot 07 design provenance:

```text
snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md
```

This is historical design context. Prefer the Snapshot 07 README and final summary for presentation wording.

## Previous Best And Ablations

Previous/pre-Snapshot07 best:

```text
snapshots/05_teacher_anchored_relative_structure_regularization/README.md
checkpoint_selection/teacher_anchor_snapshot05_06/README.md
snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/weights19_professor_visual_diagnosis_summary.md
```

Use these to explain Snapshot 05 `weights_19` as the previous best teacher-anchor checkpoint and the main Snapshot 05 comparison point.

Marginal/mixed ablation:

```text
snapshots/06_teacher_anchor_stabilization/README.md
snapshots/06_teacher_anchor_stabilization/DESIGN_NOTE.md
```

Use these to explain why reduced ranking/no texture emphasis did not replace Snapshot 05 or Snapshot 07.

Negative or non-scaling gates:

```text
snapshots/01_photometric_confidence_masking/README.md
snapshots/02_rgb_edge_structure_preserving_loss/README.md
snapshots/03_soft_confidence_multiplier/README.md
snapshots/04_vegetation_general_temporal_cross_view_consistency/README.md
```

Use these as honest negative/mixed evidence, not as current action plans.

## Archived Audits And Hygiene Notes

Pre-presentation snapshot folder audit:

```text
archive/research_process_notes/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md
```

This records snapshot-folder tidiness, contradictions fixed, active root-code state, confusing duplicates, and presentation readiness after Snapshot 07.

Documentation optimization audit:

```text
archive/research_process_notes/LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md
```

This records the Markdown inventory, current-versus-historical hierarchy, stale-plan status notes, redundant/confusing docs, and presentation-readiness decision.

Historical pre-Snapshot07 repo audit:

```text
archive/research_process_notes/pre_snapshot07_repo_audit.md
```

This is preserved as historical state before Snapshot 07 began. It contains old Snapshot 05/06 root-code statements that are now explicitly superseded. For current root-code state, use `ACTIVE_ROOT_CODE_STATE.md`.

This index:

```text
DOCUMENTATION_INDEX.md
```

Use it as the navigation map for humans and AI agents.

Archived repo/workspace cleanup audit:

```text
archive/research_process_notes/REPO_TIDY_AUDIT.md
```

This records source-of-truth docs, historical/provenance docs, stale or overlapping notes, presentation-only artifacts, temporary/generated cleanup candidates, and actions that need user approval before deletion.

## Historical Plans

Do not use these as current action plans:

```text
archive/research_process_notes/overnight_experiment_plan.md
snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md
snapshots/06_teacher_anchor_stabilization/DESIGN_NOTE.md
snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md
```

They are useful for provenance, rationale, and explaining why earlier paths were stopped or superseded.

## Bulky Evidence Policy

Bulky generated outputs should stay local and ignored:

```text
runs/
snapshots/*/local_evidence/
checkpoint_selection/*/local_results/
```

Do not commit generated run folders, exhaustive checkpoint sweeps, large visual folders, PNG packs, NPZ arrays, datasets, or caches.

Compact tracked evidence should live inside the relevant snapshot:

```text
snapshots/<stage>/results/
snapshots/<stage>/diagnostics/
snapshots/<stage>/config/
snapshots/<stage>/commands/
snapshots/<stage>/patches/
```

Exception: `snapshots/00_plain_citrus_baseline/` intentionally includes compact inference weights and a small set of PNG panels as the promoted B0 package.

## Presentation Framing

Presentation assets are separated under:

```text
presentation_assets/progress_presentation/
```

Treat those files as slide-support material, not research source-of-truth. They may contain cropped visuals, simplified tables, speaker notes, and post-hoc presentation fairness checks. Source research claims should be checked against `AGENTS.md`, the milestone/snapshot READMEs, and `archive/research_process_notes/REPO_TIDY_AUDIT.md`.

Use this wording hierarchy:

- Current lead: Snapshot 07 `weights_25`.
- Previous best: Snapshot 05 `weights_19`.
- Snapshot 06: marginal/mixed ablation.
- Snapshot 01/02/03/04: useful negative or non-scaling gates.
- Training supervision: Levinson path is label-free for Citrus training; no depth/LiDAR/valid-mask losses or training masks.
- Evaluation: dense labels and valid masks are evaluation-only.
- Inference: RGB-only Lite-Mono DepthNet.
- Visuals: promising mixed; do not claim the full-image visual problem is solved.
