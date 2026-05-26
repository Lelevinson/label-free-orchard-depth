# Task Board

Date: 2026-05-25

## Current Project Position

- Milestone 0 is complete through the full prepared Citrus dataset build.
- Milestone 1 original Lite-Mono Citrus baseline is complete with full validation/test metrics, visuals, FPS, parameter count, and checkpoint metadata.
- Milestone 2 Citrus Dataset/DataLoader and root trainer integration is complete, including CUDA one-step smoke on the RTX 4060 Laptop GPU.
- Milestone 3 standard self-supervised Citrus adaptation is closed as weak/negative adapted-baseline evidence.
- Milestone 3 cleanup is complete enough for handoff: important evidence/diagnostic runs remain, while summarized smoke/pilot/VRAM run folders were deleted locally.
- Milestone 4 plain Lite-Mono Citrus baseline from ImageNet encoder pretrain is complete and committed.
- The Milestone 4 plain baseline final checkpoint `weights_29` is mixed evidence: median-scaled `a1` improves, but raw-scale metrics and median-scaled `abs_rel` worsen.
- Milestone 4 old epoch checkpoints `weights_0` through `weights_28` were deleted locally; full ignored `weights_29`, committed inference weights, metrics, and visuals remain.
- Folder-level README maps are initialized so future chats can find the right notes without reading every Markdown file.
- The Milestone 4 B0 plain Citrus baseline is packaged under `levinson/snapshots/00_plain_citrus_baseline/` with copied inference weights, command scripts, no-code-changes marker, result files, visual panels, and `opt.json`.
- Levinson's first self-supervised Milestone 4 gates `01_photometric_confidence_masking`, `02_rgb_edge_structure_preserving_loss`, and `03_soft_confidence_multiplier` are packaged as mixed/negative non-scaling evidence.
- Levinson's `04_vegetation_general_temporal_cross_view_consistency` gate is implemented, tested, and packaged as stable weak negative evidence. The best branch, temporal geometry + texture ambiguity, gave only a tiny first-100 validation `a1` gain over the same-budget no-mask control and still worsened median-scaled `abs_rel`; full stacking was negative. Do not scale Snapshot 04.
- Levinson's `05_teacher_anchored_relative_structure_regularization` full run is implemented, trained for 30 epochs, evaluated on full val/test, and packaged as promising mixed label-free evidence. It improves B0 on raw and median-scaled `abs_rel`, keeps most of B0's median-scaled `a1`, and beats original Lite-Mono on median-scaled `a1`, but still trails original Lite-Mono on median-scaled `abs_rel`.
- Levinson's `06_teacher_anchor_stabilization` full run is implemented, trained for 30 epochs, evaluated on full val/test, and packaged as a deliberate Snapshot 05 ablation. It reduced ranking weight to `0.005` and removed texture emphasis; validation is slightly better than Snapshot 05, but test is slightly worse, so it is promising mixed / marginal stabilization rather than a clean replacement.
- Levinson's Snapshot 05/06 checkpoint-selection sweep is complete. The validation-only rule selected Snapshot 05 `weights_19` and Snapshot 06 `weights_25`; selected test results made Snapshot 05 `weights_19` the strongest pre-Snapshot07 label-free teacher-anchor checkpoint (`median abs_rel=0.3947`, `a1=0.6476` on test).
- Snapshot 05 selected `weights_19` remains visually packaged as the strongest pre-Snapshot07 teacher-anchor candidate. Comparison panels against original Lite-Mono, B0, and Snapshot 05 `weights_29` plus plain selected-checkpoint RGB/depth/disparity outputs are saved under `levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/`. No new training was run for that packaging step.
- Levinson's `07_structure_aware_label_free_vegetation_depth` method is implemented, piloted, trained for 30 epochs, validation-selected, evaluated on full val/test, and packaged. It adds reliable-boundary teacher weighting plus RGB-only sky/far ordinal pseudo-structure. Selected `weights_25` is the current strongest Levinson label-free candidate (`test median abs_rel=0.3840`, `a1=0.6539`), nearly matching original Lite-Mono on median `abs_rel` while preserving B0-like `a1`; qualitative full-image depth remains promising mixed.
- Large generated Levinson evidence was tidied into snapshot-local `local_evidence/` folders and checkpoint-selection `local_results/`; this checkout now uses `.git/info/exclude` as a personal ignore so bulky generated outputs do not flood `git status`.
- A pre-Snapshot07 repository audit now records the active root-code state, local-evidence layout, ignored artifact policy, and verification checklist at `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/pre_snapshot07_repo_audit.md`. Shared `.gitignore` rules now also ignore Levinson generated `local_evidence/`, `local_results/`, future `results/`, and run artifacts.
- Root `options.py`, `trainer.py`, the teacher diagnostic renderer, and the visual comparison helper currently remain on the Snapshot 07 structure-aware active method branch; tested copies and patch artifacts are preserved in the snapshots.
- Progress-presentation assets now live under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/presentation_assets/progress_presentation/`; treat them as slide-support material, not research source-of-truth.
- Cleanup/tidy guidance is archived in `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/archive/research_process_notes/REPO_TIDY_AUDIT.md`; do not delete/archive candidates from that report without explicit approval.
- Milestone 4 workstream ownership is split: Levinson focuses on self-supervised RGB-only training methods, while Marvel can explore supervised/hybrid methods using valid depth labels, valid masks, or LiDAR-guided training.
- Next main research step: review Snapshot 07 as the lead label-free paper candidate, especially whether its mixed full-image visuals need one final principled refinement before freezing Levinson's method.

## Ownership

### Main Integrator

Current focus:

1. keep the Levinson self-supervised path and Marvel supervised/hybrid path separated
2. keep comparisons fair against original Lite-Mono, Milestone 3 weak adaptation, and the plain Citrus baseline
3. use small gates for risky ideas, but treat Snapshots 05 and 06 as already full-run tested
4. label self-supervised versus supervised/hybrid methods honestly
5. keep artifact cleanup conservative and documented
6. treat Snapshot 04 as stable weak negative evidence and do not scale it
7. treat Snapshot 07 `weights_25` as the strongest current Levinson label-free candidate, with the caveat that it is numerically strong but not a clean full-image visual solution

Near-term outputs:

- Levinson Snapshot 07 paper-facing package review; the selected-checkpoint visual and diagnostic packages are now available for that decision
- Marvel supervised/hybrid starting-plan note
- professor-friendly explanation of the two workstreams and why supervision differs
- user decision on delete/archive candidates from the repo tidy audit

### Levinson Workstream

Current focus:

1. self-supervised RGB-only training methods for Milestone 4
2. no `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED-depth training loss unless a separate hybrid branch is explicitly approved
3. preserve RGB-only inference
4. keep failed/mixed method evidence in Levinson snapshots
5. treat Snapshot 07 as the current lead; continue only with a clearly motivated visual-structure refinement, not another small weight tweak

Working folder:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/`

Expected near-term output:

- Snapshot 07 `weights_25` review as the current best label-free result, using the new visual/inference and diagnostic package

### Marvel Workstream

Current focus:

1. supervised or hybrid training methods using valid depth labels, valid masks, or LiDAR-guided losses
2. keep inference RGB-only unless explicitly changed
3. keep results, snapshots, and claims separate from Levinson's self-supervised path

Working folder:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/`

Expected near-term output:

- first supervised/hybrid experiment design note with honest supervision labeling

### Friend A

Current focus:

1. literature scouting for lightweight monocular depth improvements
2. rank ideas for vegetation-dense scenes
3. identify ideas that are realistic for Milestone 4

Working file:

- `citrus_project/research/literature_tracker.md`

Expected near-term output:

- 5 to 10 candidate ideas with lightweight/risk judgment

### Friend B

Current focus:

1. define scene categories from a small shared sample pack
2. pick representative and difficult example frames
3. prepare qualitative-support notes for later results/paper writing

Working files:

- `citrus_project/research/scene_taxonomy.md`
- `citrus_project/milestones/00_dataset_audit/sample_pack/`

Expected near-term output:

- first-pass scene taxonomy
- example-frame shortlist
- notes on why certain scenes are hard for depth estimation

## Blocked / Waiting

1. Friend B’s deeper work still depends on a small curated sample pack being prepared.
2. Milestone 4 method work is not blocked by more Milestone 3 training.
3. Do not launch another long run without a specific method, settings, checkpoint plan, workstream folder, and explicit user confirmation; Snapshots 05, 06, and 07 are already full-run tested.
4. Do not mix Levinson self-supervised methods and Marvel supervised/hybrid methods in one run unless a new combined branch is explicitly approved.

## Next Review Point

In the next Milestone 4 chat:

1. review Snapshot 07 `weights_25` checkpoint-selection result and visual package in plain language
2. decide whether Levinson should freeze Snapshot 07 as the current label-free paper-table method or attempt one final clearly motivated visual-structure refinement
3. read `ACTIVE_ROOT_CODE_STATE.md`
4. define the smallest safe implementation/evaluation slice inside the correct workstream if any further training is approved
