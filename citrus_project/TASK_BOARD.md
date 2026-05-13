# Task Board

Date: 2026-05-13

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
- Next main research step: choose one lightweight vegetation-focused improvement that targets the Milestone 3 and plain-Citrus-baseline failure pattern.

## Ownership

### Main Integrator

Current focus:

1. choose the first Milestone 4 improvement target
2. keep comparisons fair against original Lite-Mono, Milestone 3 weak adaptation, and the plain Citrus baseline
3. use small first-100 validation gates before any full training run
4. keep artifact cleanup conservative and documented

Near-term outputs:

- Milestone 4 method-selection note
- first small implementation/evaluation slice for the chosen improvement
- professor-friendly explanation of why the improvement targets vegetation-relative-depth structure

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
3. Do not launch another long run without a specific method, settings, checkpoint plan, and explicit user confirmation.

## Next Review Point

In the next Milestone 4 chat:

1. review the baseline failure signals in plain language
2. choose the first improvement direction
3. define the smallest safe implementation/evaluation slice
