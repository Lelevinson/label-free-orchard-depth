# Snapshot 07 Final Result Summary

Snapshot 07 method: structure-aware RGB-teacher-guided label-free self-supervised adaptation.

The method keeps the Snapshot 05 teacher-anchor base but adds reliable-boundary teacher weighting from RGB edges plus teacher disparity edges, and an RGB-only sky/far ordinal pseudo-structure term. These are training-only signals. No Citrus labels, valid masks, LiDAR, ZED depth, or depth-derived masks are used for training.

Inference remains unchanged: one RGB image into Lite-Mono DepthNet.

## Pilot

The CUDA smoke and 250-step pilot were stable. The new maps were non-empty and finite. First-100 validation:

| run | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|
| no-mask control, 250 steps | 0.5634 | 0.3577 |
| Snapshot 07 pilot, 250 steps | 0.5497 | 0.3712 |

This justified one full 30-epoch run.

## Selected Checkpoint

Validation-only selection chose:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/structure_aware_label_free_vegetation_depth_b12_30ep_full/models/weights_25/
```

Rule: lowest full-validation median-scaled `abs_rel` among checkpoints with validation median-scaled `a1 >= B0_val_a1 - 0.02`; test was evaluated only after selection.

## Final Metrics

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 `weights_19` | test | 0.7391 | 0.0144 | 0.3947 | 0.6476 |
| Snapshot 07 `weights_25` | test | 0.7297 | 0.0130 | 0.3840 | 0.6539 |

Snapshot 07 is the best Levinson label-free result so far on the main test tradeoff: it nearly matches original Lite-Mono test median-scaled `abs_rel` while keeping B0-like threshold accuracy. It beats Snapshot 05 `weights_19` on both test median-scaled `abs_rel` and `a1`.

## Qualitative Judgment

Promising mixed. The valid-mask panels align with the metric improvement, but full-image depth still has visible smooth vegetation blobs and some sky/far-canopy weakness. Use as the current lead paper candidate, but be honest that the qualitative story is not fully solved.

## Decision

Classification: `promising mixed / strongest Levinson label-free candidate so far`.

Recommended next action: prepare a concise paper-style method figure and qualitative failure grid, then decide whether one final visual-quality refinement is worth running before freezing Levinson's label-free method.
