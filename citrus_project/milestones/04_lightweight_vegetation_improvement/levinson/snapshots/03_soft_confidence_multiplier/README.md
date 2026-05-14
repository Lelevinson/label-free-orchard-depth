# Snapshot 03: Soft Confidence Multiplier

Status: stop.

This was the approved independent backup gate after `02_rgb_edge_structure_preserving_loss` was bad at the 250-step screen.

## Method Summary

This experiment tested whether the first confidence method failed because normalized confidence reweighting was too disruptive. Instead of replacing the photo loss with a normalized weighted average, this variant weakly multiplies the existing automasked photo-loss map for warped-winning pixels.

It remains self-supervised. It uses only RGB reconstruction and identity/no-warp losses. It does not use `depth_gt`, `valid_mask`, LiDAR labels, dense labels, sparse labels, or ZED depth as a training loss.

Inference is unchanged: one RGB image goes through the same Lite-Mono encoder and depth decoder.

## Tested Settings

```text
--soft_confidence_multiplier
--soft_confidence_threshold 0.01
--soft_confidence_ramp 0.05
--soft_confidence_strength 0.5
--soft_confidence_min_multiplier 0.75
```

The command used defaults for the numeric values above.

## Code Snapshot Note

The copied `code/options.py` and `code/trainer.py` files are from the cumulative experimental trainer used while running the 02/03 gate queue. They include disabled options for other tested methods, but this snapshot's command enabled only `--soft_confidence_multiplier`.

This run did not combine soft confidence with RGB-edge structure loss or photometric-confidence masking. The live root `options.py` and `trainer.py` were restored to the shared baseline state after packaging.

## Run Paths

Smoke run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_smoke_2steps/
```

250-step gate run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/
```

Checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/models/step_250/
```

Evaluation:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/eval_val100_step_250/
```

Visual panels:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/visual_compare_control_vs_soft_confidence_val100_step_250/
```

Readable diagnostics:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/diagnostics_last_logged.json
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/diagnostics_last_logged.csv
```

Small copied artifacts are also saved under this snapshot in `results/`, `diagnostics/`, and `visual_summary/`.

## Metric Summary

First-100 validation at step 250:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Same-budget no-mask control | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Photometric-confidence masking 01 | 0.8985 | 0.0000 | 0.5582 | 0.3018 |
| Soft confidence multiplier | 0.8978 | 0.0000 | 0.5676 | 0.3068 |

Extra median-scaled metrics:

```text
sq_rel=1.6928, rmse=4.1185, rmse_log=0.7289, a2=0.5361, a3=0.6757
```

## Diagnostics Summary

Last logged training step: 200.

| diagnostic | scale 0 | scale 1 | scale 2 |
|---|---:|---:|---:|
| multiplier mean | 0.9742 | 0.9743 | 0.9746 |
| multiplier mean on warped winners | 0.9485 | 0.9486 | 0.9490 |
| warped-winner fraction | 0.5005 | 0.5005 | 0.4973 |
| weak-pixel fraction among warped winners | 0.5299 | 0.5292 | 0.5268 |
| margin mean | 0.0038 | 0.0039 | 0.0038 |
| photo loss before | 0.1350 | 0.1349 | 0.1350 |
| photo loss after | 0.1327 | 0.1326 | 0.1327 |
| effective loss delta | 0.0023 | 0.0023 | 0.0023 |

The multiplier was mild, but the metric pattern stayed weak and similar to the first confidence experiment.

## Visual Check

Generated panels:

```text
adapted_good_index_0035_comparison.png
adapted_typical_index_0090_comparison.png
adapted_bad_index_0024_comparison.png
largest_drop_vs_original_index_0048_comparison.png
```

The first-100 metrics were below the no-mask control, so this gate was treated as failed without scaling.

## Conclusion

Conclusion: stop this direction for now.

The softer multiplier did not rescue the confidence idea. It slightly improved raw metrics versus the no-mask control, but median-scaled `a1` remained clearly worse than the same-budget no-mask control and close to the failed `01_photometric_confidence_masking` result. This suggests the issue is not only normalized reweighting; RGB photometric confidence remains a poor reliability signal for Citrus vegetation under this setup.
