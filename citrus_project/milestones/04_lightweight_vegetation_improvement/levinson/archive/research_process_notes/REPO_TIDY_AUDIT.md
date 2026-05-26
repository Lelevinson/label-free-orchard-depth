# Repo Tidy Audit

Date: 2026-05-25

Scope: careful documentation/workspace cleanup audit for the Lite-Mono + Citrus Farm research repo, with extra attention to `AGENTS.md`, top-level docs, `citrus_project/milestones/`, Milestone 4, Levinson snapshots 00-07, research handoff notes, presentation assets, documentation indexes, and task board files.

No training, experiments, model-code edits, dataset moves, checkpoint moves, generated-evidence moves, deletes, commits, or pushes were performed.

## Starting Git State

Before this tidy pass, `git status --short` showed existing work in progress:

```text
 M AGENTS.md
 M citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/README.md
?? citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/presentation_assets/
```

Those changes were treated as user/project work already in progress. This audit preserved and built around them.

## Files Inspected

Inventory commands inspected visible tracked/untracked docs with `rg --files -g "*.md" -g "*.txt" -g "*.rst"` and checked ignored/generated candidates with Git ignore/status commands.

Opened/read directly:

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `citrus_project/README.md`
- `citrus_project/TEAM_WORKFLOW.md`
- `citrus_project/TASK_BOARD.md`
- `citrus_project/research/README.md`
- `citrus_project/research/baseline_notes.md`
- `citrus_project/research/paper_shortlist.md`
- `citrus_project/research/literature_tracker.md`
- `citrus_project/research/scene_taxonomy.md`
- `citrus_project/milestones/README.md`
- `citrus_project/milestones/03_self_supervised_adaptation/README.md`
- `citrus_project/milestones/03_self_supervised_adaptation/artifact_inventory.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/README.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/pre_snapshot07_repo_audit.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/overnight_experiment_plan.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/README.md`
- Snapshot README/result/design docs for `00` through `07`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md`
- Markdown notes under `presentation_assets/progress_presentation/slide2_existing_model/`
- Markdown notes under `presentation_assets/progress_presentation/slide3_modified_model/`
- Markdown notes under `presentation_assets/progress_presentation/slide4_comparison/`

Searched by reference before classifying stale/removable candidates:

- Snapshot status terms: `Snapshot 07`, `Snapshot 05`, `Snapshot 06`, `current lead`, `strongest`, `weights_19`
- root-code terms: `active root`, `root code`, `snapshot code`, `train.py`, `archival`
- gate/full-run terms: `250-step`, `pilot`, `gate`, `full run`, `post-hoc`
- supervision terms: `training-only`, `inference`, `depth_gt`, `valid_mask`, `LiDAR`, `ZED`
- cleanup candidates: `tmp_pycache_snapshot07`, `tmp_trainer_wiring_smoke`, `val_lite-mono_max2`, `val_lite-mono_max3`, `presentation_assets`

## 1. Current Source-Of-Truth Docs

Keep these as main context/navigation files:

- `AGENTS.md` - top source of truth for current project status, decisions, paths, and next actions.
- `citrus_project/README.md` - Citrus workspace doorway and read map.
- `citrus_project/TEAM_WORKFLOW.md` - collaboration and ownership guide.
- `citrus_project/TASK_BOARD.md` - current work board.
- `citrus_project/research/README.md` - research-note doorway.
- `citrus_project/research/paper_shortlist.md` - current paper-candidate evidence index.
- `citrus_project/research/baseline_notes.md` - detailed model behavior/evidence archive.
- `citrus_project/research/dataset_notes.md` - dataset and label-route evidence.
- `citrus_project/research/advisor_notes.md` - advisor questions and follow-up record.
- `citrus_project/research/student_qna.md` - stable beginner explanations.
- `citrus_project/milestones/README.md` - milestone doorway.
- `citrus_project/milestones/*/README.md` - milestone handoffs.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md` - shared Milestone 4 handoff and workstream rules.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md` - Levinson workstream doorway.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md` - current Levinson AI/human navigation index.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md` - root-code policy for active `trainer.py`/`options.py` versus archival snapshot `code/`.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/README.md` - snapshot map.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/README.md` - current lead Levinson label-free method.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md` - compact current lead result summary.
- This file, `archive/research_process_notes/REPO_TIDY_AUDIT.md` - archived cleanup/audit guide.

## 2. Useful Historical/Provenance Docs

Keep these because they explain research history, even when they are not current action plans:

- `citrus_project/milestones/03_self_supervised_adaptation/README.md`
- `citrus_project/milestones/03_self_supervised_adaptation/professor_loading_and_train_eval_check.md`
- `citrus_project/milestones/03_self_supervised_adaptation/beginner_progress_summary.md`
- `citrus_project/milestones/03_self_supervised_adaptation/artifact_inventory.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/pre_snapshot07_repo_audit.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/overnight_experiment_plan.md`
- `snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/diagnostic_report.md`
- `snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/weights19_professor_visual_diagnosis_summary.md`
- `snapshots/06_teacher_anchor_stabilization/DESIGN_NOTE.md`
- `snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md`

These files are useful provenance, but future readers should prefer `AGENTS.md`, `DOCUMENTATION_INDEX.md`, Snapshot 07 README/final summary, and this audit for current framing.

## 3. Stale Or Misleading Docs Found

Facts found:

- `citrus_project/milestones/README.md` still described Milestone 4 as the "next active planning stage" and only highlighted the B0 snapshot.
- `citrus_project/research/baseline_notes.md` described Snapshot 05 `weights_19` as the "strongest current label-free teacher-anchor result" without immediately saying Snapshot 07 later superseded it as the current Levinson lead.
- `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md` repeated older "restored root trainer" wording for Snapshot 01/02/03 options. The factual conclusion was still correct, but the phrase could confuse readers because the current root workbench is Snapshot 07, not the restored post-03 baseline.
- The top-level `README.md` was still pure upstream Lite-Mono documentation, with no immediate pointer to `AGENTS.md` or `citrus_project/`.

Inferences:

- The stale Milestone 4 doorway wording was likely from before Snapshots 05-07 completed.
- The Snapshot 05 wording was historical but could mislead an AI/human reader scanning only `baseline_notes.md`.
- The upstream README is not wrong, but it is not enough as a doorway for this research fork.

## 4. Duplicate Or Overlapping Docs

Keep but clarify:

- `SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md`, `LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md`, and this `REPO_TIDY_AUDIT.md` overlap. They serve different moments:
  - snapshot-folder audit before presentation,
  - Levinson Markdown optimization before presentation,
  - current wider repo/workspace cleanup audit.
- `DOCUMENTATION_INDEX.md`, `levinson/README.md`, `snapshots/README.md`, and `AGENTS.md` all summarize Snapshot 07. This is intentional doorway duplication, but the index should remain the navigation entry.
- Snapshot README files and snapshot `results/*summary.md` files repeat metrics. Keep both: README is human handoff, result summary is compact evidence.
- Snapshot 06 has both `code/NO_CODE_CHANGES_FROM_SNAPSHOT05.txt` and copied code files. Keep: it documents config-only method change while preserving exact reference code.
- Snapshot 07 has a runnable checkpoint-selection script under `scripts/` and an archival copy under `code/`. Keep: runnable location versus frozen snapshot copy.

## 5. Presentation-Only Artifacts

Presentation assets are now clearly under:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/presentation_assets/progress_presentation/
```

Observed subfolders:

- `slide2_existing_model/`
- `slide3_modified_model/`
- `slide4_comparison/`

Classification:

- Presentation-only, not research source-of-truth.
- Useful for progress slides and speaker notes.
- Slide 4 contains post-hoc matched 250-step Snapshot 05/06 pilots. These must be labeled as post-hoc presentation fairness checks, not evidence that existed before the original Snapshot 05/06 full runs.
- The presentation assets are currently untracked. If the slide package should be preserved in Git, explicitly add it later. If not, keep it local or archive after presentation. Do not delete in this pass.

## 6. Temporary/Generated Files

Facts:

- `tmp_pycache_snapshot07/` exists and contains Python bytecode cache files from redirected compile/pycache work. It was not referenced by docs before this audit.
- `tmp_trainer_wiring_smoke/` exists, is ignored by `.gitignore`, and is referenced in `AGENTS.md` plus Milestone 3 `artifact_inventory.md` as a possible cleanup candidate.
- Root and subfolder `__pycache__/` directories exist and are ignored.
- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_max2_*` and `val_lite-mono_max3_*` are ignored local smoke/evaluator outputs. `val_lite-mono_max3_*` is referenced in `baseline_notes.md`; `max2` did not appear in the reference search.
- `runs/`, `local_evidence/`, `local_results/`, `weights/`, datasets, and caches are ignored/generated areas and were not modified.

Inference:

- `tmp_pycache_snapshot07/` is a strong cleanup candidate after approval.
- `tmp_trainer_wiring_smoke/` is probably disposable, but because it is explicitly listed in notes, deletion should wait for user approval.
- Ignored Milestone 1 max2/max3 smoke outputs are low priority; keep unless the user approves a targeted cleanup.

## 7. Markdown Consistency Problems Checked

Current lead method:

- Current factual state is Snapshot 07 `weights_25`.
- Fixed stale doorway wording so `milestones/README.md` and Levinson navigation point to Snapshot 07.

Snapshot 07 status:

- Snapshot 07 README/final summary/AGENTS agree: completed smoke, pilot, full run, validation-first checkpoint selection, full val/test evaluation, visual packaging; promising mixed/current lead.
- Existing user edit correctly warns that Snapshot 07 command scripts contain later stricter heuristic args that do not match archived `config/opt.json`.

Snapshot 05 previous-best status:

- Snapshot 05 is previous/pre-Snapshot07 best teacher-anchor checkpoint, not current overall Levinson lead.
- Fixed ambiguous `baseline_notes.md` wording.

Snapshot 06 marginal/mixed status:

- Snapshot 06 docs consistently say marginal/mixed ablation, not replacement.

Active root `trainer.py`/`options.py` state:

- Current source-of-truth is `ACTIVE_ROOT_CODE_STATE.md`: root code is active Snapshot 07 workbench code.
- Snapshot `code/` folders are archival copies, not imported automatically by `train.py`.
- No model-code change was made.

Full-run versus pilot/gate distinction:

- Existing Snapshot 01-04 docs correctly label 250-step gates.
- Slide 4 docs correctly label Snapshot 05/06 250-step rows as post-hoc matched gates.
- Report keeps presentation rows separated from research source-of-truth.

Training-only versus inference-time claims:

- Snapshot 04/05/06/07 docs consistently state training-only teacher/PoseNet/maps/losses and RGB-only DepthNet inference.
- No contradiction found in current Snapshot 07 label-free or inference claims.

## 8. Recommended Cleanup Actions

SAFE_EDIT_NOW:

- Add a top-level README research-fork pointer to `AGENTS.md` and `citrus_project/`.
- Refresh `citrus_project/milestones/README.md` so Milestone 4 is not described as merely future planning.
- Refresh `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md` wording around Levinson snapshots and current root workbench.
- Update Levinson `DOCUMENTATION_INDEX.md` and `README.md` to list this audit and separate `presentation_assets/` from source-of-truth docs.
- Clarify `baseline_notes.md` so Snapshot 05 `weights_19` is pre-Snapshot07 best, while Snapshot 07 is current lead.
- Update `TASK_BOARD.md` date/status for presentation assets and this tidy audit.
- Update `AGENTS.md` to include this audit in Document Roles, Milestone 4 status, Next Actions, and Recent Change Log.
- Create this report.

SAFE_RENAME_OR_MOVE:

- None performed.
- Possible future move, after approval: if presentation assets should be archived after the talk, move the whole `presentation_assets/progress_presentation/` tree into a dated archive folder under `presentation_assets/` instead of leaving ad hoc slide subfolders.

NEEDS_USER_CONFIRMATION_BEFORE_DELETE:

- `tmp_pycache_snapshot07/`
- `tmp_trainer_wiring_smoke/`
- root and project `__pycache__/` folders
- ignored Milestone 1 smoke outputs such as `val_lite-mono_max2_*`, after confirming no hidden need
- any presentation assets that are no longer needed after the progress presentation
- any old audit docs only if the user explicitly decides to consolidate history; current recommendation is to keep them as provenance

DO_NOT_TOUCH:

- `datasets/`
- `weights/`
- checkpoints
- `runs/`
- `local_evidence/`
- `local_results/`
- Citrus prepared dataset and extracted raw data
- caches/secrets under `.codex/` except by explicit user request
- root model/training code such as `trainer.py`, `options.py`, `layers.py`, and `networks/*.py`
- Marvel folder beyond read-only audit

## Safe Edits Performed

Documentation-only edits were made to:

```text
README.md
AGENTS.md
citrus_project/TASK_BOARD.md
citrus_project/milestones/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md
citrus_project/research/baseline_notes.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/REPO_TIDY_AUDIT.md
```

No files were deleted or moved.

No datasets, weights, checkpoints, runs, generated evidence, caches, root model code, or Marvel files were modified.

## Verification After Edits

Ran:

```text
git diff --check
git status --short
rg -n "[ \t]+$" citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/REPO_TIDY_AUDIT.md
```

Results:

- `git diff --check` passed with only expected LF-to-CRLF warnings from this Windows checkout.
- The trailing-whitespace check on this new report found no matches.
- Final status still includes pre-existing Snapshot 07 README and presentation-asset changes plus this audit's documentation edits; no model code, data, weights, runs, or generated evidence were modified.

## Delete/Archive Candidates Requiring Approval

Recommended first approval batch, if the user wants actual cleanup later:

1. Delete `tmp_pycache_snapshot07/`.
2. Delete disposable `__pycache__/` folders.
3. Delete `tmp_trainer_wiring_smoke/` if the user agrees the old smoke opt.json folders are no longer useful.
4. Decide whether untracked `presentation_assets/` should be committed, archived after the presentation, or left local.
5. Review ignored Milestone 1 max2/max3 smoke outputs separately; keep `max3` unless the `baseline_notes.md` reference is intentionally retired.

## Remaining Risks

- Presentation assets are untracked. If they are important to preserve, they need an intentional add/commit later.
- `AGENTS.md` and Snapshot 07 README already had pre-existing modifications before this audit. This pass preserved them, but they remain part of the working tree.
- Older historical notes still contain chronological wording such as "next" or "future" inside their original context. This is acceptable when the file has a status/supersession note or a current index points elsewhere.
- The repo still has many source-of-truth-like summaries by design. The safest pattern is to keep doorway docs current and mark old plans as historical, rather than deleting provenance.

## Final Recommended Documentation Structure

Start here:

```text
AGENTS.md
citrus_project/README.md
citrus_project/TEAM_WORKFLOW.md
citrus_project/TASK_BOARD.md
```

For Milestone 4:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/REPO_TIDY_AUDIT.md
```

For current Levinson method/result:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/final_result_summary.md
```

For provenance:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/pre_snapshot07_repo_audit.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/overnight_experiment_plan.md
```

For presentation only:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/presentation_assets/progress_presentation/
```

Use presentation files for slides, not for primary research claims unless the same claim is backed by the relevant source-of-truth docs above.
