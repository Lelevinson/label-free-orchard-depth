# Hybrid Supervised 30-Epoch Result Report

Date: 2026-05-21

This note summarizes Marvel's 30-epoch hybrid supervised Lite-Mono experiment as handoff context for a teammate's Codex session. The main comparison here is against the plain Citrus Lite-Mono baseline, not against the shorter 5-epoch gate.

## Short Verdict

The run was successful and was not wasted. The 30-epoch hybrid supervised model is much stronger than the plain Citrus baseline, especially because it fixes the raw-scale failure that plain/self-supervised Citrus training still had.

The honest caveat is that the final 30-epoch checkpoint was only slightly better than the earlier 5-epoch hybrid checkpoint, so future recipes should still use shorter gates before spending a long full run. But as evidence for the hybrid supervised approach, this is currently our strongest result.

## Experiment

Run name:

```text
hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched
```

Training recipe:

- model: `lite-mono`
- dataset: prepared Citrus RGB + dense LiDAR labels
- initialization: `weights/lite-mono/lite-mono-pretrain.pth`
- batch size: `12`
- epochs: `30`
- LiDAR supervision weight: `0.1`
- LiDAR loss type: `log_l1`
- LiDAR scale alignment: `none`
- supervised scale: `0`
- minimum valid supervised pixels: `500`

Final checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/models/weights_29/
```

Main output folder:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/results/hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/
```

Important files:

```text
loss_plots/train_loss_curves.png
loss_plots/val_loss_curves.png
val_lite-mono_full_summary.json
val_lite-mono_full_per_sample.csv
test_lite-mono_full_summary.json
test_lite-mono_full_per_sample.csv
visuals/baseline_vs_hybrid_val/
visuals/baseline_vs_hybrid_test/
```

## Metric Comparison Against Plain Citrus

Plain Citrus baseline refers to the final 30-epoch ImageNet-pretrained plain Citrus run from Levinson's baseline work. The hybrid model is Marvel's final 30-epoch `weights_29`.

| model | split | raw abs_rel | raw a1 | median abs_rel | median a1 |
|---|---:|---:|---:|---:|---:|
| Plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Hybrid supervised 30ep | val | 0.1913 | 0.7968 | 0.1933 | 0.7805 |
| Plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Hybrid supervised 30ep | test | 0.1741 | 0.8186 | 0.1791 | 0.8001 |

Interpretation:

- Raw-scale metrics improved dramatically. This is important because plain Citrus still had very poor raw-scale depth behavior.
- Median-scaled metrics also improved strongly, which means the hybrid model is not only fixing scale but also improving relative depth structure.
- The final hybrid model kept scale stable: median scale ratio was about `0.9850` on validation and `1.0061` on test.
- In plain language, the hybrid model predicts Citrus depth at a much more correct absolute scale while also improving the near/far layout.

## Loss Behavior

The loss fluctuated batch-to-batch, but the overall trend was healthy. The fluctuations are expected because each logged batch can contain different scene geometry, tree density, shadows, road texture, and valid LiDAR coverage.

| split | epoch window | mean loss | min | max | std |
|---|---:|---:|---:|---:|---:|
| train | 0-2 | 0.1482 | 0.1310 | 0.2397 | 0.0283 |
| train | 3-10 | 0.1151 | 0.0912 | 0.1489 | 0.0132 |
| train | 11+ | 0.0926 | 0.0712 | 0.1153 | 0.0110 |
| val | 0-2 | 0.1543 | 0.1372 | 0.2336 | 0.0248 |
| val | 3-10 | 0.1243 | 0.0998 | 0.1516 | 0.0135 |
| val | 11+ | 0.1059 | 0.0863 | 0.1215 | 0.0079 |

Final epoch 29 logged means:

- train loss: `0.0719`
- val loss: `0.0967`
- train LiDAR weighted loss: `0.0143`
- val LiDAR weighted loss: `0.0152`
- train LiDAR valid fraction: about `37.0%`
- val LiDAR valid fraction: about `36.7%`

Interpretation:

The model did not diverge. Both train and val loss moved downward, and the fluctuation range became smaller after the early epochs. This supports the result as a stable training run, not a lucky final checkpoint from unstable training.

## Weights and Inference

The final checkpoint folder contains:

```text
encoder.pth
depth.pth
pose_encoder.pth
pose.pth
adam.pth
adam_pose.pth
```

For RGB-only depth inference, the important files are:

```text
encoder.pth
depth.pth
```

The pose files are training-time components for self-supervised photometric learning. The Adam files are optimizer states for resuming training. They are not needed for final RGB-only depth inference.

Model size and speed metadata from evaluation:

- inference parameters: `3,074,747`
- encoder parameters: `2,848,120`
- depth decoder parameters: `226,627`
- checkpoint size for encoder + depth decoder: about `11.83 MiB`
- GPU evaluation model-forward FPS: about `15.3` to `15.6` in this evaluator path

This keeps the result within the lightweight Lite-Mono framing.

## Image Comparison Summary

Comparison panels are saved here:

```text
visuals/baseline_vs_hybrid_val/
visuals/baseline_vs_hybrid_test/
```

Selected validation panels:

```text
bad_index_0200_comparison.png
typical_index_0309_comparison.png
good_index_0044_comparison.png
```

Selected test panels:

```text
bad_index_0343_comparison.png
typical_index_0113_comparison.png
good_index_0057_comparison.png
```

Selected-panel metrics:

| split | role | plain abs_rel | plain a1 | hybrid abs_rel | hybrid a1 |
|---|---|---:|---:|---:|---:|
| val | bad | 1.5900 | 0.0131 | 0.4061 | 0.1757 |
| val | typical | 0.2681 | 0.7407 | 0.1595 | 0.8010 |
| val | good | 0.1180 | 0.8828 | 0.0924 | 0.9193 |
| test | bad | 1.6435 | 0.0261 | 0.5331 | 0.0743 |
| test | typical | 0.2010 | 0.7837 | 0.1399 | 0.8392 |
| test | good | 0.1103 | 0.8961 | 0.0939 | 0.9174 |

Visual interpretation:

- The hybrid model improves the selected bad cases a lot in absolute relative error, although the bad cases are still visibly hard.
- Typical and good examples improve more cleanly.
- The hybrid model produces a depth layout that better follows the road/tree geometry than plain Citrus.
- Edge artifacts remain around vegetation boundaries and sparse LiDAR regions.
- The result should be described as a strong depth and scale improvement, not as a perfect boundary-quality solution.

## Why The Images May Look Less Dramatic Than The Metrics

Important nuance for visual review:

The baseline-vs-hybrid comparison panels use median-scaled depth visualizations. This means both Plain Citrus and Hybrid are individually rescaled to match the LiDAR median depth for that image before plotting.

That is useful for comparing relative depth shape, but it hides one of the hybrid model's biggest wins: absolute scale.

Plain Citrus was very weak in raw-scale metrics:

| model | split | raw abs_rel | raw a1 |
|---|---:|---:|---:|
| Plain Citrus | val | 0.7736 | 0.0074 |
| Hybrid supervised 30ep | val | 0.1913 | 0.7968 |
| Plain Citrus | test | 0.7787 | 0.0077 |
| Hybrid supervised 30ep | test | 0.1741 | 0.8186 |

Visually, after median scaling, Plain Citrus receives an artificial per-image scale correction. That can make the colorized depth maps look closer to Hybrid than the raw metrics suggest.

Other reasons the visual gain can look modest:

- The panels show only a small number of selected examples, while the metrics average hundreds of images and millions of valid pixels.
- The improvement may be distributed as many modest per-pixel corrections, not one obvious visual transformation.
- In the colorized depth maps, similar broad shapes can look visually close even when the numeric depth values are meaningfully better.
- The error maps and error-delta maps are more important than the raw depth-color panels for judging improvement.
- Citrus vegetation labels are semi-dense and imperfect, especially around foliage, holes, boundaries, and sparse LiDAR regions.

Recommended wording:

The hybrid model substantially improves Citrus depth accuracy and absolute scale over plain Citrus adaptation. Qualitative gains are moderate rather than visually dramatic, and they are clearest in the error maps/delta maps rather than always obvious in the depth-color panels.

## Was the Long Run Worth It?

Yes, scientifically.

The 30-epoch run proves that the hybrid supervised recipe can train to completion, stay scale-stable, improve strongly over the plain Citrus baseline, and preserve the lightweight Lite-Mono inference setup.

However, the extra compute beyond the earlier 5-epoch run gave only a small additional gain. The 5-epoch run was already very strong, and the 30-epoch final checkpoint only slightly improved over it. This means the method is promising, but future recipe testing should use short gates first before committing to full 30-epoch runs.

Recommended framing for teammates:

- Strong result: hybrid supervised Lite-Mono is currently much more promising than boundary-loss-only training.
- Strong result: absolute-scale LiDAR supervision fixes the scale problem.
- Careful claim: 30 epochs produced the best checkpoint so far, but most gains appeared early.
- Open risk: dense LiDAR labels are project-derived and imperfect, so visual review and label-quality caveats still matter.

## Next Recommendations

1. Use `weights_29` as the current best full-run checkpoint.
2. Keep the 5-epoch and `weights_19` checkpoints for ablation/context.
3. Do not delete the generated visuals, per-sample CSVs, or loss plots.
4. For future recipe variants, use 2-epoch or 5-epoch gates before another 30-epoch run.
5. If time allows, do a checkpoint sweep across `weights_4`, `weights_9`, `weights_14`, `weights_19`, `weights_24`, and `weights_29` to confirm the best validation checkpoint.
