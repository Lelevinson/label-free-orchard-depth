# Milestone 4 Snapshots

This folder stores tidy stage snapshots for Levinson's sequential Lite-Mono + Citrus improvements.

Read this file first, then open only the stage folder needed for the task.

## Current Stages

| folder | role |
|---|---|
| `00_plain_citrus_baseline/` | B0: plain Lite-Mono Citrus baseline from ImageNet encoder pretrain |
| `01_photometric_confidence_masking/` | first self-supervised confidence-mask gate; stable but mixed, conclusion `uncertain / do not scale yet` |
| `02_rgb_edge_structure_preserving_loss/` | independent RGB-edge structure-loss gate; stable but negative, conclusion `stop` |
| `03_soft_confidence_multiplier/` | independent soft confidence backup gate; stable but negative, conclusion `stop` |

## Naming Rule

Use numeric, readable names:

```text
00_plain_citrus_baseline/
01_<first_method_name>/
02_<second_independent_method_name>/
03_<third_independent_method_name>/
```

Do not combine methods unless a future note explicitly approves a combined branch. Paper-style labels can be recorded inside a stage README later if useful, but folder names should stay descriptive and should not imply combined training unless the experiment actually combined methods.

## Stage Folder Rule

Each completed stage should contain one compact `README.md` plus the artifacts needed to understand or rerun that stage:

- changed code files, when that stage changes code
- a simple marker file when a completed stage has no stage-specific code changes
- exact command scripts when they are known
- checkpoint paths, and checkpoint files only when the snapshot is promoted as a compact inference package
- saved config such as `opt.json`
- result CSV/JSON files
- visual comparison panels or small visual-summary CSV/JSON files, with full panel paths recorded in the stage README when the PNGs stay in ignored run folders
- diagnostic CSV/JSON summaries when available

Avoid extra nested README files unless a subfolder becomes complicated enough to need its own map.

When a stage changes Python code, duplicate the tested `.py` files into that stage's `code/` folder. Preserve clear relative paths when useful, for example `code/trainer.py`, `code/options.py`, `code/layers.py`, or `code/networks/depth_decoder.py`.

The live root `trainer.py` and `options.py` were restored to the shared baseline state after the 01/02/03 gates were packaged. Experimental code lives in the snapshot `code/` folders for reproducibility; use the command scripts and README for each stage to see which single method was actually enabled.
