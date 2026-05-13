# Milestone 4 Snapshots

This folder stores tidy stage snapshots for Levinson's sequential Lite-Mono + Citrus improvements.

Read this file first, then open only the stage folder needed for the task.

## Current Stages

| folder | role |
|---|---|
| `00_plain_citrus_baseline/` | B0: plain Lite-Mono Citrus baseline from ImageNet encoder pretrain |

## Naming Rule

Use numeric, readable names:

```text
00_plain_citrus_baseline/
01_<first_method_name>/
02_<first_method_plus_second_method>/
03_<combined_method_name>/
```

Paper-style labels such as `A`, `A+B`, or `A+B+C` can be recorded inside a stage README later, but folder names should stay descriptive.

## Stage Folder Rule

Each completed stage should contain one compact `README.md` plus the artifacts needed to understand or rerun that stage:

- changed code files, when that stage changes code
- a simple marker file when a completed stage has no stage-specific code changes
- exact command scripts when they are known
- checkpoint files needed for inference/evaluation
- saved config such as `opt.json`
- result CSV/JSON files
- visual comparison panels

Avoid extra nested README files unless a subfolder becomes complicated enough to need its own map.

When a stage changes Python code, duplicate the tested `.py` files into that stage's `code/` folder. Preserve clear relative paths when useful, for example `code/trainer.py`, `code/options.py`, `code/layers.py`, or `code/networks/depth_decoder.py`.
