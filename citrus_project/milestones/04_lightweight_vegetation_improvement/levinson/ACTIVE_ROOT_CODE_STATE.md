# Active Root Code State

Date: 2026-06-05 (updated; was 2026-05-20)

This note exists to prevent future Milestone 4 chats from confusing the live repo-root training code with frozen snapshot copies.

## Current Policy

Root code is the active implementation workbench.

Snapshot `code/` folders are frozen reproducibility copies.

Every completed Levinson snapshot that changes tested Python code must copy the tested changed files into that snapshot's `code/` folder.

## Current Root State

Root `trainer.py` and `options.py` are the active Snapshot 07 structure-aware teacher-anchor workbench, with additional OFF-BY-DEFAULT experimental code layered on top from later stages:

- Snapshot 08 (feature-metric loss) — `--feature_metric_loss` + `networks/feature_net.py`; NEGATIVE result, packaged in `snapshots/08_feature_metric_loss/`.
- Snapshot 09 (TSOB mixture) — `--tsob_mixture_loss` + `networks/mixture_head.py` + one-line `networks/depth_decoder.py` exposure; NEGATIVE result, packaged in `snapshots/09_tsob_boundary_uncertainty_mixture/`.
- Snapshot 10 (EMA in-domain self-teacher) — `--ema_self_distillation` (+ `--ema_*` flags), `update_ema`/`compute_ema_distill_loss` in `trainer.py`; CURRENT IN-PROGRESS BUILD. Design at `snapshots/10_ema_self_teacher/DESIGN_NOTE.md`; tested `trainer.py`/`options.py` are to be copied into `snapshots/10_ema_self_teacher/code/` once smoke-tested and run (do NOT repeat the 08/09 miss where this copy step was skipped).

With NO new flags, `train.py` reproduces Snapshot 07 behavior byte-for-byte — every 08/09/10 path is gated behind its off-by-default master flag. They are not restored to the original Lite-Mono baseline and not restored to the shared Milestone 2/3 baseline trainer state.

The active root code is what `train.py` imports and runs by default.

This means:

- root `options.py` exposes Snapshot 04 temporal/feature flags, Snapshot 05/06 teacher-anchor flags, and Snapshot 07 structure-aware teacher/sky-far flags;
- root `trainer.py` contains Snapshot 04 temporal cross-view utilities, Snapshot 05/06 teacher-anchor regularization code, and Snapshot 07 reliable-boundary plus RGB-only sky/far pseudo-structure code;
- all new method flags remain disabled by default, so plain runs still require explicit flags;
- Snapshot 05/06 teacher-anchor behavior and Snapshot 07 structure-aware behavior are available from root when the relevant flags are enabled.

## Snapshot Copies Are Archival

Snapshot `code/` folders are not automatically imported by `train.py`.

To run a snapshot exactly, future Codex or a human researcher should either:

1. use the committed snapshot `code/` files as a reference while checking the active root code; or
2. intentionally restore/copy the snapshot `code/` files into the repo root before running, then document that restoration.

Do not assume a snapshot `code/` folder changes runtime behavior by existing in the tree.

## Verified Snapshot Code Copies

Snapshot 05 code folder:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/code/
```

Contains:

```text
options.py
trainer.py
citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/render_selected_checkpoint_inference_visuals.py
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/render_weights19_professor_visual_diagnostics.py
```

Snapshot 06 code folder:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/code/
```

Contains:

```text
NO_CODE_CHANGES_FROM_SNAPSHOT05.txt
options.py
trainer.py
citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py
```

Snapshot 06 is a configuration-only stabilization of Snapshot 05, so it does not have additional implementation files beyond the active Snapshot 05 teacher-anchor code.

Snapshot 07 code folder:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/code/
```

Contains:

```text
options.py
trainer.py
render_teacher_structure_diagnostics.py
render_selected_checkpoint_inference_visuals.py
run_snapshot07_checkpoint_selection.py
```

Snapshot 07 builds from the active Snapshot 05/06 teacher-anchor implementation and adds reliable-boundary teacher weighting plus an RGB-only sky/far ordinal pseudo-structure loss.

## Why This Matters After Snapshot 07

The active root workbench is a valid starting point as long as future methods deliberately inspect it first.

Before implementing Snapshot 08 or any other future Levinson method, future Codex should decide whether to:

1. build from the active Snapshot 07 structure-aware teacher-anchor code;
2. restore the shared baseline trainer/options first; or
3. copy a specific snapshot archival version into root intentionally.

Any choice is acceptable only if it is documented in the next snapshot README or design note before training.

## Why This Is Dangerous If Undocumented

It is dangerous to leave this implicit because future agents may assume root `trainer.py` and `options.py` are baseline Lite-Mono code. They are not.

If that mistake happens, a future run might:

- unknowingly inherit teacher-anchor or temporal-consistency implementation code;
- unknowingly inherit Snapshot 07 structure-aware teacher/sky-far code;
- compare against the wrong control;
- fail to copy changed code into the new snapshot;
- mislabel a run as baseline or pure self-supervised-from-scratch.

## Required Future Workflow

Before any new Levinson method edits or training:

1. read this file;
2. read `AGENTS.md`;
3. read `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/README.md`;
4. read the relevant snapshot README(s);
5. inspect root `trainer.py` and `options.py`;
6. document whether the new method starts from active Snapshot 07 root code, a restored baseline, or a copied archival snapshot.

Going forward:

```text
root code = active implementation workbench
snapshot/code = frozen reproducibility copy
completed snapshot = must copy tested changed code into snapshot/code
```
