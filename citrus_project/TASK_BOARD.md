# Task Board

Date: 2026-05-14

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
- Milestone 4 workstream ownership is split: Levinson focuses on self-supervised RGB-only training methods, while Marvel can explore supervised/hybrid methods using valid depth labels, valid masks, or LiDAR-guided training.
- Next main research step: choose the next self-supervised direction for Levinson and separately scope Marvel's supervised/hybrid starting point.

## Ownership

### Main Integrator

Current focus:

1. keep the Levinson self-supervised path and Marvel supervised/hybrid path separated
2. keep comparisons fair against original Lite-Mono, Milestone 3 weak adaptation, and the plain Citrus baseline
3. use small first-100 validation gates before any full training run
4. label self-supervised versus supervised/hybrid methods honestly
5. keep artifact cleanup conservative and documented

Near-term outputs:

- Levinson next self-supervised method-selection note
- Marvel supervised/hybrid starting-plan note
- professor-friendly explanation of the two workstreams and why supervision differs

### Levinson Workstream

Current focus:

1. self-supervised RGB-only training methods for Milestone 4
2. no `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED-depth training loss unless a separate hybrid branch is explicitly approved
3. preserve RGB-only inference
4. keep failed/mixed method evidence in Levinson snapshots

Working folder:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/`

Expected near-term output:

- next self-supervised direction proposal after the 01/02/03 mixed/negative gates

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
3. Do not launch another long run without a specific method, settings, checkpoint plan, workstream folder, and explicit user confirmation.
4. Do not mix Levinson self-supervised methods and Marvel supervised/hybrid methods in one run unless a new combined branch is explicitly approved.

## Next Review Point

In the next Milestone 4 chat:

1. review the baseline failure signals in plain language
2. choose Levinson's next self-supervised direction or Marvel's first supervised/hybrid direction
3. define the smallest safe implementation/evaluation slice inside the correct workstream
