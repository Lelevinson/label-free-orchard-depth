# Levinson Snapshot Folder Audit Before Presentation

Date: 2026-05-20

Scope: Levinson Milestone 4 snapshot-folder tidiness and consistency after Snapshot 07 packaging. No training, evaluation, new method work, dataset movement, run movement, checkpoint movement, or push was performed for this audit.

## Overall Status

Levinson's Milestone 4 folder is ready for progress-presentation preparation with one important caveat: the presentation should describe Snapshot 07 as the current lead label-free candidate, but should not claim that full-image qualitative vegetation depth is solved.

Current lead result:

```text
Snapshot 07 selected weights_25
test median-scaled abs_rel=0.3840
test median-scaled a1=0.6539
```

Current positioning:

- Snapshot 05 `weights_19` is the previous best teacher-anchor checkpoint and the main Snapshot 05 comparison point.
- Snapshot 06 is a marginal/mixed ablation, not the lead.
- Snapshot 07 is the current lead Levinson label-free candidate.
- Levinson training remains label-free: no `depth_gt`, `valid_mask`, LiDAR, ZED depth, dense labels, sparse labels, or label-derived masks were used as training losses or training masks.
- Valid masks and dense depth labels are evaluation-only.
- Inference remains RGB-only Lite-Mono DepthNet.
- Visual evidence remains mixed; do not present Snapshot 07 as a clean full-image visual solution.

## Snapshot Status Table

| snapshot | README | method/result description | code/config/commands/patches | evidence layout | audit status |
|---|---|---|---|---|---|
| `00_plain_citrus_baseline/` | present | Correctly describes B0 plain Citrus baseline from ImageNet encoder pretrain and mixed final result | `code/NO_CODE_CHANGES.txt`, commands, `config/opt.json`, compact checkpoint | Contains tracked compact inference weights and four PNG panels by prior design | Tidy; leave tracked weights/PNGs alone because they are the promoted compact B0 package |
| `01_photometric_confidence_masking/` | present | Correctly says uncertain / do not scale yet | tested `options.py` and `trainer.py`, smoke/gate/eval/visual commands | compact results, diagnostics, and visual-summary CSV/JSON tracked | Tidy |
| `02_rgb_edge_structure_preserving_loss/` | present | Correctly says stop; label-free RGB-edge gate was negative | tested `options.py` and `trainer.py`, commands | compact results, diagnostics, and visual-summary CSV/JSON tracked | Tidy |
| `03_soft_confidence_multiplier/` | present | Correctly says stop; label-free soft-confidence gate was negative | tested `options.py` and `trainer.py`, commands | compact results, diagnostics, and visual-summary CSV/JSON tracked | Tidy |
| `04_vegetation_general_temporal_cross_view_consistency/` | present | Correctly says stable weak negative / do not scale | tested code, commands, diagnostics, patch, diagnostic report | bulky maps under `local_evidence/`, compact summaries tracked | Tidy after wording fix: root-code statement is now explicitly historical |
| `05_teacher_anchored_relative_structure_regularization/` | present | Correctly documents Snapshot 05 final run and selected `weights_19`; wording now marks it as pre-Snapshot07 best, not current lead | tested code copies, commands, config, diagnostics, patch, selected-checkpoint notes | bulky selected visuals under `local_evidence/`; compact results/diagnostics tracked | Tidy after wording fixes |
| `06_teacher_anchor_stabilization/` | present | Correctly says promising mixed / marginal stabilization, not replacement | design note, copied Snapshot 05 teacher code, commands, config, diagnostics, patches | bulky visuals under `local_evidence/`, compact results tracked | Tidy after historical root-code wording fix |
| `07_structure_aware_label_free_vegetation_depth/` | present | Correctly documents current lead Snapshot 07, label-free scope, pilot, validation-only checkpoint selection, full val/test metrics, and mixed visuals | design note, commands, config, copied tested code, patch, checkpoint-selection script | bulky visuals under `local_evidence/`; compact result summaries, visual manifests, and diagnostics tracked | Tidy; current lead candidate |

## Contradictions Found And Fixed

The audit found several stale present-tense statements left from earlier milestones:

- `archive/research_process_notes/pre_snapshot07_repo_audit.md` described Snapshot 05/06 root code and Snapshot 05 `weights_19` as current. A supersession note and local wording fixes now mark those statements as historical and point current root state to `ACTIVE_ROOT_CODE_STATE.md`.
- Snapshot 07 `DESIGN_NOTE.md` used pre-implementation present tense for Snapshot 05 `weights_19`; it now says "at design time" to avoid conflicting with Snapshot 07's lead status.
- Snapshot 04 README said root files remained as the active method branch. It now says that was the packaging-time state and has been superseded.
- Snapshot 05 README said `weights_19` was the current best Levinson label-free teacher-anchor candidate. It now says strongest pre-Snapshot07 teacher-anchor candidate and main Snapshot 05 comparison point.
- Snapshot 06 README said root code remained active on the teacher-anchored branch. It now says that was the packaging-time state and has been superseded by Snapshot 07.
- The Snapshot 05/06 checkpoint-selection README conclusion now says Snapshot 05 `weights_19` is the best pre-Snapshot07 teacher-anchor checkpoint and that Snapshot 07 later superseded it as the current lead.
- The Snapshot 05 professor visual diagnosis summary now avoids saying `weights_19` is the current best checkpoint.
- `AGENTS.md`, the Levinson README, and `snapshots/README.md` now point readers to this audit and keep Snapshot 07 as the current lead.

No contradiction was found in the core Snapshot 07 label-free/inference claims.

## Files Edited

Markdown-only edits:

```text
AGENTS.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/pre_snapshot07_repo_audit.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/04_vegetation_general_temporal_cross_view_consistency/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/weights19_professor_visual_diagnosis_summary.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/README.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md
```

Files moved: none.

Code changed: none.

## Duplicate Or Potentially Confusing Files

These were found and intentionally left alone:

- Snapshot 00 includes tracked `checkpoint/encoder.pth`, `checkpoint/depth.pth`, and four PNG comparison panels. This is unusual compared with later snapshots, but it is the intentional compact promoted B0 inference package and should not be moved before a presentation.
- Snapshot 05 and Snapshot 06 `code/` folders preserve some helper scripts under nested repo-relative paths. This is verbose, but it records provenance and is consistent with the snapshot rule.
- Snapshot 06 has both `code/NO_CODE_CHANGES_FROM_SNAPSHOT05.txt` and copied code files. This is slightly redundant but useful: it says the method was config-only while still preserving runnable reference code.
- Snapshot 07 keeps `scripts/run_snapshot07_checkpoint_selection.py` and also copies the same script into `code/` as an archival tested-code copy. This is intentional: `scripts/` is the runnable location, while `code/` is the frozen reproducibility copy.
- Snapshot 07 `code/trainer.py` is semantically the tested root trainer copy; it differs from root `trainer.py` only by one trailing blank line at EOF normalized during packaging so `git diff --check` stays clean.

No duplicate was severe enough to justify deletion or movement in this audit.

## Active Root-Code State

Verified current root-code state:

- root `options.py` and `trainer.py` are active Snapshot 07 structure-aware teacher-anchor workbench code, not original Lite-Mono baseline code;
- root code exposes disabled-by-default Snapshot 04 temporal/feature flags, Snapshot 05/06 teacher-anchor flags, and Snapshot 07 structure-aware teacher/sky-far flags;
- `train.py` imports the root workbench code, not snapshot `code/` folders;
- Snapshot `code/` folders are frozen archival copies only;
- Snapshot 07 tested root code copies are saved under `snapshots/07_structure_aware_label_free_vegetation_depth/code/`.

Hash check during audit:

- root `options.py` matches Snapshot 07 `code/options.py`;
- root `render_teacher_structure_diagnostics.py` matches Snapshot 07 `code/render_teacher_structure_diagnostics.py`;
- root selected-checkpoint visual helper matches Snapshot 07 `code/render_selected_checkpoint_inference_visuals.py`;
- root `trainer.py` differs from Snapshot 07 `code/trainer.py` only by the trailing blank line noted above.

Future agents should read:

```text
ACTIVE_ROOT_CODE_STATE.md
```

before any root training-code edit or attempt to reproduce an older snapshot.

## Intentionally Left Alone

The audit did not touch:

- `runs/`;
- `local_evidence/`;
- `local_results/`;
- B0 compact checkpoint weights;
- tracked B0 visual PNG panels;
- datasets;
- caches;
- Marvel's folder;
- root model/trainer code.

## Presentation Readiness

Ready for presentation preparation: yes.

Recommended presentation framing:

- show Snapshot 07 as the current lead label-free method;
- show Snapshot 05 `weights_19` as the previous best teacher-anchor comparison;
- show Snapshot 06 as a marginal stabilization ablation;
- state clearly that all Levinson methods keep RGB-only inference and do not use depth/LiDAR/valid-mask training losses;
- use the mixed qualitative visuals honestly, especially sky/far-canopy and vegetation-blob failures.
