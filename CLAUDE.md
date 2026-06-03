# CLAUDE.md

Lite-Mono + Citrus Farm research workspace: a publishable improvement to lightweight
monocular depth estimation for vegetation-dense agricultural scenes (Citrus Farm is the
current validation domain). Upstream-style Lite-Mono code is at the repo root; all
project-owned work lives under `citrus_project/`.

## Read first, in this order

**Before starting any task, read `AGENTS.md` — it is the source of truth and is required
context.** Then read the rest as the task needs:

1. `AGENTS.md` — **source of truth** (read it first, every session): project goal, milestone
   status, decisions, canonical paths, quick commands. It is long; read the whole file once,
   then re-read the relevant sections on demand.
2. `citrus_project/TEAM_WORKFLOW.md` — collaboration roles and edit boundaries.
3. `citrus_project/TASK_BOARD.md` — current work board and next review point.
4. Then the task-specific milestone / snapshot `README.md`. For Milestone 4 (Levinson),
   start from `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md`.

Folder-level `README.md` files are doorway maps — use them to find the right deep note
instead of reading every `.md`.

## Working rules

- Treat `AGENTS.md` as source of truth. When project status, defaults, commands, paths, or
  research decisions change, update it **in the same turn**, and end the reply with
  `Context file updated: Yes` (+ what changed) or `Context file updated: No` (+ why not).
- Notes are living documents, not append-only logs: update/supersede stale wording rather
  than stacking conflicting lines.
- Verify claims against the actual files and recent context before answering; label guesses
  as guesses; do not assume a file/script/folder is workflow-relevant without checking.
- Do not delete experiment evidence, checkpoints, panels, scripts, or notes without
  classifying them and getting explicit user approval (see AGENTS.md "Artifact Policy").
- Levinson's path is **label-free / self-supervised, RGB-only**; Marvel's path may use
  supervised/hybrid depth-label or LiDAR-guided losses. Label supervision honestly and keep
  the two workstreams' results separate. Inference stays RGB-only unless stated otherwise.
- When explaining model/PyTorch/image-processing concepts, slow down for mutual
  understanding: map formulas to tensors/code, use small concrete examples, and do
  concept-checks.

## Environment

- Project Python: `D:/Conda_Envs/lite-mono/python.exe`
- GPU: RTX 4060 Laptop. Platform: Windows / PowerShell.
