# Phase 2 Boundary-Loss Code Modification Note

Date: 2026-05-14

This folder began as a draft code snapshot for Marvel's Milestone 4 Phase 2 work. On 2026-05-14, the same boundary-loss changes were applied to the repo-root `layers.py`, `trainer.py`, and `options.py` so the runnable training path can execute the Phase 2 experiment.

The copied files under `code/` remain the review/reference snapshot for the intended root changes.

## Purpose

The Phase 2 idea is to make Lite-Mono more boundary-aware for vegetation scenes. The current Lite-Mono training loss already has edge-aware smoothness, but that term mainly says "do not over-smooth too strongly at RGB edges." The new boundary term is more direct: it asks predicted disparity edges to line up with RGB image edges.

Plain goal:

```text
leaves, branches, trunks, fruit/canopy boundaries in RGB
        ->
sharper and better-aligned depth/disparity transitions
```

## Files Copied

The draft copies are:

```text
code/layers.py
code/trainer.py
code/options.py
```

These correspond to the root files:

```text
layers.py
trainer.py
options.py
```

## What Changed

### `code/layers.py`

Added `BoundaryLoss`, a small PyTorch module that:

1. converts RGB to grayscale;
2. computes horizontal and vertical gradients for predicted disparity;
3. computes horizontal and vertical gradients for the grayscale RGB image;
4. optionally normalizes gradients per image;
5. returns an L1 gradient-matching loss.

This uses predicted disparity instead of raw metric depth because Lite-Mono's existing smoothness regularization already works on normalized disparity.

### `code/options.py`

Added two Phase 2 CLI options:

```text
--boundary_loss_weight
--disable_boundary_normalize
```

`--boundary_loss_weight` defaults to `0.0`, so the old training behavior is unchanged unless Phase 2 is explicitly enabled. A first real run can try `--boundary_loss_weight 0.2`, matching the Phase 2 planning documents.

### `code/trainer.py`

Added boundary-loss setup in `Trainer.__init__`:

```python
self.boundary_loss = BoundaryLoss(normalize=not self.opt.disable_boundary_normalize)
```

Added safe defaults and validation in `configure_dataset_options`.

Added the boundary term in `compute_losses` after the normal smoothness loss:

```python
if self.opt.boundary_loss_weight > 0:
    boundary_loss = self.boundary_loss(norm_disp, color)
    loss += self.opt.boundary_loss_weight * boundary_loss / (2 ** scale)
```

The loss is logged as:

```text
boundary_loss/<scale>
boundary_loss_weighted/<scale>
```

## Intended Training Use

Once copied into the root code and after `prepared_training_dataset/` exists, a smoke run should enable the term with a small step cap:

```powershell
python train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --boundary_loss_weight 0.2 `
  --max_train_steps 5
```

The smoke test should confirm:

1. no shape errors;
2. `boundary_loss/0` appears in logs;
3. total loss is finite;
4. no NaN or Inf values appear.

## Current Status

The Phase 2 changes have now been applied to the root training code and smoke-tested.

Completed checks on 2026-05-14:

1. `layers.py`, `options.py`, `trainer.py`, and `train.py` passed `py_compile`.
2. A 5-step Phase 2 smoke run completed with `--boundary_loss_weight 0.2`.
3. A batch-size-12 10-step gate completed without CUDA OOM.
4. A controlled 1-epoch Phase 2 run completed:

```text
model_name: phase2_boundary_loss_b12_1ep_w02
run folder: citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/phase2_boundary_loss_b12_1ep_w02
batch_size: 12
num_epochs: 1
boundary_loss_weight: 0.2
checkpoint: models/weights_0
```

Observed console loss during the 1-epoch run:

```text
batch 0:   0.17042
batch 100: 0.15147
batch 200: 0.14243
batch 300: 0.14434
```
