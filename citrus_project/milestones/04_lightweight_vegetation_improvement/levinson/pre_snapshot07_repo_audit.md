# Pre-Snapshot07 Repository Audit

Date: 2026-05-19

Scope: Levinson Milestone 4 hygiene checkpoint before any Snapshot 07 method work. No training or new experiments were run for this audit.

## Commands Inspected

- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- `git ls-files --others --exclude-standard`
- `git ls-files --ignored --exclude-standard`
- `git diff --check`

Note: plain `git ls-files --ignored --exclude-standard` is invalid in this Git version without `--others` or `--cached`; the audit used both corrected forms:

- `git ls-files --others --ignored --exclude-standard`
- `git ls-files --ignored --cached --exclude-standard`

## 1. Source Code Changes

Root active method code:

- `options.py`
- `trainer.py`

These remain on the active Snapshot 05/06 teacher-anchored method branch. The options surface includes the disabled-by-default Snapshot 04 temporal/feature flags and Snapshot 05 teacher-anchor flags. The trainer includes temporal cross-view utilities, teacher loading, scale-invariant teacher structure losses, gradient/ranking losses, optional texture ambiguity weighting, diagnostics logging, and debug map writing.

Helper/visualization code:

- `citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_temporal_cross_view_diagnostics.py`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/run_teacher_anchor_checkpoint_selection.py`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/render_selected_checkpoint_inference_visuals.py`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/render_weights19_professor_visual_diagnostics.py`

`train.py` and `evaluate_depth.py` have no tracked diff.

Tested code copies are preserved under the relevant snapshot `code/` folders, especially Snapshots 04, 05, and 06.

## 2. Tracked Compact Docs, Configs, Commands, Patches, Summaries

Safe compact tracked material is organized under:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/04_vegetation_general_temporal_cross_view_consistency/`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/`

These folders contain README/design/diagnostic notes, command scripts, config files, code copies, patches, and small CSV/JSON/Markdown summaries. No unignored `.png`, `.npz`, checkpoint, or model-weight files were present in `git ls-files --others --exclude-standard`.

Project context notes updated or staged for update:

- `AGENTS.md`
- `citrus_project/TASK_BOARD.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/README.md`
- `citrus_project/research/baseline_notes.md`
- `citrus_project/research/paper_shortlist.md`

## 3. Generated Evidence That Should Stay Local Only

Generated evidence remains present locally but should not be committed:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/04_vegetation_general_temporal_cross_view_consistency/local_evidence/`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/`

Approximate local generated evidence sizes at audit time:

| path | files | size |
|---|---:|---:|
| Snapshot 04 `local_evidence/` | 78 | 3.90 MB |
| Snapshot 05 `local_evidence/` | 362 | 289.77 MB |
| Snapshot 05 `selected_weights19_visuals/` | 125 | 202.81 MB |
| Snapshot 05 `selected_weights19_professor_visual_diagnostics/` | 99 | 59.44 MB |
| Snapshot 06 `local_evidence/` | 193 | 41.54 MB |
| checkpoint selection `local_results/` | 133 | 23.96 MB |

## 4. Large Artifacts That Must Not Be Committed

Large local artifacts remain ignored:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/` (about 23.9 GB at audit time)
- `weights/`
- `citrus_project/dataset_workspace/prepared_training_dataset/`
- extracted Citrus dataset folders under `citrus_project/dataset_workspace/`
- generated snapshot `local_evidence/`
- checkpoint-selection `local_results/`

The legacy B0 plain-Citrus result folder under `levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/` is already tracked even though the parent `levinson/results/` is now ignored for future generated output. It was left tracked to avoid silently rewriting historical evidence.

## 5. Accidental Junk / Cache Files

Ignored local junk/cache includes:

- `__pycache__/`
- `*.pyc`
- `.codex/`
- `.vscode/`
- dataset build outputs and projection diagnostics
- local run logs/checkpoints

No unignored accidental junk appeared in `git ls-files --others --exclude-standard` after the local evidence layout was checked.

## 6. Active Root-Code State

Root code remains active as Snapshot 05/06 branch.

Specifically:

- `options.py` and `trainer.py` are not restored to the shared baseline; they contain disabled-by-default method flags and trainer support for Snapshot 04 plus Snapshot 05/06 teacher-anchor work.
- `render_teacher_structure_diagnostics.py` and the updated comparison helper remain available for teacher-anchor diagnostics.
- Snapshot 06 did not need new implementation beyond Snapshot 05; it was a config-only stabilization.
- Snapshot 05 selected `weights_19` remains the current best Levinson label-free teacher-anchor checkpoint.

State label for handoff:

```text
root code remains active as Snapshot 05/06 branch; root code is ready for Snapshot 07 continuation after reading this audit and the Snapshot 05/06 READMEs
```

## Verification Plan

Before committing this hygiene checkpoint:

1. compile changed/untracked Python files without writing bytecode;
2. run `python train.py --help` to confirm the active option surface;
3. run `git diff --check`;
4. inspect the staged set to confirm no `local_evidence/`, `local_results/`, `runs/`, `weights/`, or large generated images are included.

Verification completed before commit:

- changed/untracked Python compile check: passed for 21 files;
- `D:/Conda_Envs/lite-mono/python.exe train.py --help`: passed and showed the Snapshot 04 temporal/feature flags plus Snapshot 05/06 teacher-anchor flags;
- `git diff --check`: passed, with only expected Windows LF-to-CRLF notices;
- unignored generated-binary check: no untracked `.png`, `.jpg`, `.jpeg`, `.pth`, `.pt`, `.ckpt`, or `.npz` files appeared in `git ls-files --others --exclude-standard`.

## Snapshot 07 Starting Guidance

Start a new Snapshot 07 chat by reading:

1. `AGENTS.md`
2. `citrus_project/TEAM_WORKFLOW.md`
3. `citrus_project/TASK_BOARD.md`
4. `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md`
5. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md`
6. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/pre_snapshot07_repo_audit.md`
7. Snapshot 05 README, checkpoint-selection README, and Snapshot 05 professor-facing `visual_diagnosis.md`

Do not start Snapshot 07 training until the team decides whether `weights_19` is sufficient as the current label-free result or whether the next method is clearly different from another small Snapshot 05/06 weight tweak.
