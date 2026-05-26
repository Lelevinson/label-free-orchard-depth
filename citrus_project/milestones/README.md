# Milestones Workspace

These folders are reserved for milestone-specific work as the project progresses.

Use them to keep new code, experiment helpers, notes, plots, and milestone-scoped artifacts grouped by stage instead of scattering them across the whole repo.

## Folder Map

- `00_dataset_audit/` - dataset construction, calibration checks, label-route validation (complete through full dataset build)
- `01_original_lite_mono_baseline/` - original Lite-Mono baseline runs and evaluation helpers (core baseline evidence complete; optional polish deferred)
- `02_citrus_integration/` - Citrus Dataset/DataLoader and evaluation integration
- `03_self_supervised_adaptation/` - self-supervised Citrus fine-tuning/adaptation work (documented as weak/negative baseline evidence)
- `04_lightweight_vegetation_improvement/` - lightweight vegetation-focused model/loss improvements (active; Levinson has completed snapshots 00-07, with Snapshot 07 as the current label-free lead candidate)
- `05_optional_supervised_or_hybrid/` - optional supervised or hybrid training additions
- `06_paper_package/` - paper tables, figures, writing support, and final packaging

## Read Map

Do not open every milestone note by default. Use this order:

1. Read repo-root `AGENTS.md` for current milestone status.
2. Read this file to choose the milestone folder.
3. Read only the matching milestone `README.md`.
4. Open deeper milestone notes only when that README says they are relevant.

Active Milestone 4 work should start at:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/README.md
```

For Levinson's current Milestone 4 navigation map, use:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md
```

Milestone 4 B0 snapshot is at:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/README.md
```

That folder contains the B0 inference weights plus copied final result files, visuals, and `opt.json`.

Current Levinson label-free lead snapshot is at:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/README.md
```

Future Milestone 4 code snapshots are described in the Milestone 4 README and should only be created once an improvement stage actually changes code.

Current milestone state:

- Milestone 0 is complete through the full dataset build.
- Milestone 1 has full original Lite-Mono validation/test metrics, validation/test good-typical-bad visuals, and first written interpretation.
- Optional Milestone 1 polish is deferred for now.
- Milestone 2 core integration is complete: Citrus prepared Dataset/DataLoader, temporal-neighbor diagnostics, temporal triplet batch smoke checks, trainer-compatibility dry run, root depth-metric guard, root `--dataset citrus` trainer wiring, one-step optimizer smoke, CUDA one-step smoke, and train-only Citrus color augmentation are in place.
- Milestone 3 standard self-supervised Citrus adaptation is documented as a weak/negative adapted-baseline result. The tested recipe family runs technically but fails to beat the untouched baseline and can damage relative depth structure.
- Milestone 4 is active. Levinson's label-free self-supervised workstream has completed B0/Snapshot 00 through Snapshot 07; Snapshot 07 `weights_25` is the current strongest Levinson label-free candidate, with promising mixed visuals. Marvel's supervised/hybrid workstream remains separate.

These folders are the intended home for milestone-specific code, notes, helpers, and outputs as each stage becomes active.
