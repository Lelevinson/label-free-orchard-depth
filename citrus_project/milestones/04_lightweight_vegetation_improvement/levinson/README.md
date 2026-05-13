# Levinson Milestone 4 Workstream

This folder collects Levinson's Milestone 4 progress so the completed baseline and later improvement stages stay together.

Read this file first for this workstream, then open only the needed snapshot README.

## Contents

```text
results/
runs/
snapshots/
```

Current moved result folder:

```text
results/plain_litemono_imagenet_b12_30ep_final_weights29/
```

Current local ignored run folder:

```text
runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/
```

Current completed snapshot:

```text
snapshots/00_plain_citrus_baseline/
```

This is B0: the plain Lite-Mono Citrus baseline from ImageNet encoder pretrain. It includes copied inference weights, command scripts, result CSV/JSON files, visual panels, `config/opt.json`, and a no-code-changes marker.

The `runs/` folder is ignored by Git because it can contain optimizer states, pose-network weights, and TensorBoard logs. Keep lightweight committed evidence in `results/` and `snapshots/`.

## Code Snapshot Rule

When a tested Milestone 4 stage changes Python code, copy the tested files into that stage snapshot under `code/`.

Use clear relative paths when useful:

```text
snapshots/01_method_name/code/trainer.py
snapshots/01_method_name/code/options.py
snapshots/01_method_name/code/layers.py
snapshots/01_method_name/code/networks/depth_decoder.py
```

For stages with no stage-specific code changes, keep a simple marker such as:

```text
snapshots/00_plain_citrus_baseline/code/NO_CODE_CHANGES.txt
```
