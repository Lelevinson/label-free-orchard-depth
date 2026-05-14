# Marvel Milestone 4 Workstream

This folder is Marvel's Milestone 4 workstream for supervised or hybrid Citrus depth-improvement experiments.

## Scope

Marvel may explore methods that use valid depth labels, valid masks, dense LiDAR labels, sparse LiDAR labels, or LiDAR-guided losses during training.

Inference can still remain RGB-only: one RGB image goes through the Lite-Mono-style depth model at test time. The key difference from Levinson's workstream is training supervision.

## Separation Rules

- Keep Marvel runs, results, snapshots, helper scripts, and notes inside this folder.
- Label methods honestly as supervised or hybrid whenever they use depth labels, valid masks, or LiDAR-derived signals during training.
- Do not mix Marvel's supervised/hybrid training losses into Levinson's self-supervised snapshots.
- Do not claim supervised/hybrid results are directly fair wins over self-supervised methods unless the comparison clearly explains the different supervision.
- Do not edit Levinson's folder without explicit approval.

## Snapshot Rule

When a tested Marvel stage changes Python files such as `trainer.py`, `options.py`, `layers.py`, `networks/*.py`, or helper scripts, copy the tested versions into that stage snapshot under `code/`.

Use clear snapshot names, for example:

```text
snapshots/01_valid_mask_guided_depth_loss/
snapshots/02_sparse_lidar_relative_depth/
```

Each completed snapshot should include a compact `README.md`, command notes, checkpoint path, result path, visual path if available, metric summary, diagnostic summary, and conclusion.
