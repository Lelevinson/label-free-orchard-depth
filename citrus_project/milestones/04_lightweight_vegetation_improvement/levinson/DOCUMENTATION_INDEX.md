# Levinson Documentation Index

Status: navigation index for Levinson's Milestone 4 folder, refreshed after the
Snapshot 10 paper result, Snapshot 11 negative gate, and Milestone 6 paper-package
promotion.

Use this file to decide what to read. Do not treat every Markdown file under this folder as current guidance; many are preserved historical plans, diagnostic reports, or snapshot-local evidence notes.

## Start Here

1. `README.md`
   - Main Levinson workstream doorway.
   - Summarizes the workstream and points to the current S10/S11 evidence.
2. `ACTIVE_ROOT_CODE_STATE.md`
   - Current root-code policy.
   - Root `trainer.py` and `options.py` are active Snapshot 07 workbench code with off-by-default Snapshot 08/09/10/11 code layered on top, not original Lite-Mono baseline.
   - Snapshot `code/` folders are frozen archival copies and are not imported automatically by `train.py`.
3. `snapshots/README.md`
   - Compact map of all snapshot folders.
   - Use this before opening individual snapshot folders.
4. `archive/research_process_notes/REPO_TIDY_AUDIT.md`
   - Archived cleanup audit and safe documentation optimization report.
   - Use this before deleting, archiving, or consolidating old notes, generated files, or presentation assets.
5. `M4_CHANGE_LOG.md`
   - Dated Milestone 4 provenance log (snapshot packaging, checkpoint selection, presentation assets, the literature pass, and the S08 feature-metric / TSOB gates).
   - Moved out of the top-level `AGENTS.md` change log to keep that file at pointer altitude. Use it for "when/why did X happen", not as a current action plan.

## Current Lead Method

Snapshot 10 is the shipped Levinson label-free paper result:

```text
snapshots/10_ema_self_teacher/results/final_result.md
```

Use it for current method/result framing:

- label-free Citrus training;
- RGB-only Lite-Mono DepthNet inference;
- selected `weights_29`;
- test median-scaled `abs_rel=0.3080`, `a1=0.6258`;
- first Levinson method to beat original Lite-Mono on both headline median-scaled metrics;
- qualitative visuals remain mixed, and the reliability gates were near-inert.

Snapshot 11 is the post-S10 negative gate that stays in the paper story:

```text
snapshots/11_resizing_crop_self_distillation/DESIGN_NOTE.md
```

Paper package:

```text
citrus_project/milestones/06_paper_package/paper/
```

Snapshot 07 is the prior best / strongest-a1 reference:

```text
snapshots/07_structure_aware_label_free_vegetation_depth/README.md
snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md
```

Use Snapshot 07 for comparison wording, not as the current lead.

## Next-Direction Candidates

Verified literature shortlist and post-S11 next-method queue:

```text
LITERATURE_SHORTLIST.md
```

Use it for post-paper or paper-polish ideas only. For the current paper cycle,
S10 ships; S11 is killed by gate. Foundation-model distillation remains outside
Levinson's label-free scope and belongs in a clearly labeled hybrid branch.

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

- Current lead / paper result: Snapshot 10 `weights_29`.
- Prior best / strongest-a1 reference: Snapshot 07 `weights_25`.
- Previous best: Snapshot 05 `weights_19`.
- Snapshot 06: marginal/mixed ablation.
- Snapshot 01/02/03/04: useful negative or non-scaling gates.
- Training supervision: Levinson path is label-free for Citrus training; no depth/LiDAR/valid-mask losses or training masks.
- Evaluation: dense labels and valid masks are evaluation-only.
- Inference: RGB-only Lite-Mono DepthNet.
- Visuals: promising mixed; do not claim the full-image visual problem is solved.
