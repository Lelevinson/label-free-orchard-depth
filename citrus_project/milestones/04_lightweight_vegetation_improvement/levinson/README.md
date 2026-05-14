# Levinson Milestone 4 Workstream

This folder collects Levinson's Milestone 4 progress so the completed baseline and later improvement stages stay together.

Read this file first for this workstream, then open only the needed snapshot README.

Levinson's workstream is the self-supervised Milestone 4 path. Prioritize RGB-only training objectives or constraints that do not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED depth as a training loss. If a future idea needs label supervision, create or move it to a clearly separate hybrid branch instead of mixing it into this workstream.

Inference should remain RGB-only unless a future note explicitly says otherwise. Training-supervision claims must be labeled honestly when comparing against Marvel's supervised/hybrid workstream.

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

Tested improvement snapshots:

```text
snapshots/01_photometric_confidence_masking/
snapshots/02_rgb_edge_structure_preserving_loss/
snapshots/03_soft_confidence_multiplier/
```

This is the first self-supervised Milestone 4 method gate. It adds disabled-by-default photometric-confidence masking on top of existing automasking, copies tested `trainer.py` and `options.py`, records smoke and 250-step gate commands, and concludes `uncertain / do not scale yet`.

`02_rgb_edge_structure_preserving_loss/` is the conservative RGB-edge structure-loss gate. It remained self-supervised and inference-neutral, but the 250-step first-100 validation result worsened both median-scaled `abs_rel` and `a1` versus the same-budget no-mask control, so it concludes `stop`.

`03_soft_confidence_multiplier/` is the independent backup confidence gate. It tested a mild multiplier instead of normalized confidence reweighting, but still worsened median-scaled `a1` versus the same-budget no-mask control, so it concludes `stop`.

After these gates were packaged, the live root `options.py` and `trainer.py` were restored to the shared baseline state for collaboration. The tested experimental code remains in each snapshot's `code/` folder for reproducibility or later reapplication.

The `runs/` folder is ignored by Git because it can contain optimizer states, pose-network weights, and TensorBoard logs. Keep lightweight committed evidence in `results/` and `snapshots/`.

Do not edit Marvel's folder from this workstream without explicit approval.

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
