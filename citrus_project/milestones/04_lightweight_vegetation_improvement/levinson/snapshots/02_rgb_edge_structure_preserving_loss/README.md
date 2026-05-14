# Snapshot 02: RGB-Edge Structure-Preserving Loss

Status: stop.

This was the main next Milestone 4 self-supervised gate after `01_photometric_confidence_masking`.

## Method Summary

This experiment added a conservative RGB-edge structure loss during training. It uses only the target RGB image and the predicted normalized disparity. It does not use `depth_gt`, `valid_mask`, LiDAR labels, dense labels, sparse labels, or ZED depth as a training loss.

The loss weakly discourages completely flat normalized disparity at strong blurred RGB edges:

```text
edge = blurred RGB gradient > threshold
disp_grad = normalized disparity gradient
loss = mean(edge * relu(target_grad - disp_grad))
```

Inference is unchanged: one RGB image goes through the same Lite-Mono encoder and depth decoder.

## Tested Settings

```text
--rgb_edge_structure_loss
--rgb_edge_structure_weight 0.01
--rgb_edge_structure_threshold 0.08
--rgb_edge_structure_blur_kernel 5
--rgb_edge_structure_target_grad 0.02
```

The command used defaults for the numeric values above.

## Code Snapshot Note

The copied `code/options.py` and `code/trainer.py` files are from the cumulative experimental trainer used while running the 02/03 gate queue. They include disabled options for other tested methods, but this snapshot's command enabled only `--rgb_edge_structure_loss`.

This run did not combine structure loss with photometric-confidence masking or soft confidence. The live root `options.py` and `trainer.py` were restored to the shared baseline state after packaging.

## Run Paths

Smoke run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_smoke_2steps/
```

250-step gate run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/
```

Checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/models/step_250/
```

Evaluation:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/eval_val100_step_250/
```

Visual panels:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/visual_compare_control_vs_rgb_edge_val100_step_250/
```

Readable diagnostics:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/diagnostics_last_logged.json
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/diagnostics_last_logged.csv
```

Small copied artifacts are also saved under this snapshot in `results/`, `diagnostics/`, and `visual_summary/`.

## Metric Summary

First-100 validation at step 250:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Same-budget no-mask control | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| RGB-edge structure loss | 0.8993 | 0.0000 | 0.5822 | 0.3280 |

Extra median-scaled metrics:

```text
sq_rel=1.7804, rmse=4.1727, rmse_log=0.7517, a2=0.5482, a3=0.6722
```

## Diagnostics Summary

Last logged training step: 200.

| diagnostic | scale 0 | scale 1 | scale 2 |
|---|---:|---:|---:|
| edge fraction | 0.0121 | 0.0222 | 0.0449 |
| disp grad on edges | 0.0024 | 0.0070 | 0.0192 |
| hinge active fraction | 1.0000 | 0.9759 | 0.5975 |
| raw structure loss | 0.000429 | 0.000583 | 0.000567 |
| weighted contribution | 0.00000429 | 0.00000292 | 0.00000142 |
| total train loss | 0.1348 | n/a | n/a |

The structure loss was active but very small. The conservative edge threshold selected few pixels, especially at scale 0.

## Visual Check

Generated panels:

```text
adapted_good_index_0039_comparison.png
adapted_typical_index_0082_comparison.png
adapted_bad_index_0023_comparison.png
largest_drop_vs_original_index_0027_comparison.png
```

The first-100 metrics were already below the no-mask control, so this gate was treated as failed without scaling.

## Conclusion

Conclusion: stop this exact configuration.

The run was stable and self-supervised, but it worsened both median-scaled `abs_rel` and median-scaled `a1` versus the same-budget no-mask control. The loss appears too weak/sparse to rescue structure at this 250-step gate, while still failing the metric screen.

Because this was clearly not promising, the pre-approved independent backup `03_soft_confidence_multiplier` was run next.
