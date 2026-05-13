# Snapshot 00: Plain Citrus Baseline

This is B0, the plain Lite-Mono Citrus baseline from ImageNet encoder pretrain.

It is the main comparison baseline for future Milestone 4 improvements.

## Contents

```text
checkpoint/
code/
commands/
config/
results/
visual_compare_original_vs_final_val_full/
```

Included:

- `checkpoint/encoder.pth`
- `checkpoint/depth.pth`
- `code/NO_CODE_CHANGES.txt`
- `commands/train.ps1`
- `commands/evaluate_val.ps1`
- `commands/evaluate_test.ps1`
- `commands/visual_compare_original_vs_b0.ps1`
- `config/opt.json`
- full validation/test result CSV and JSON files under `results/`
- original-vs-B0 visual comparison panels under `visual_compare_original_vs_final_val_full/`

Not included:

- pose-network weights
- optimizer states
- earlier epoch checkpoints

## What This Stage Is

Plain Lite-Mono trained on the prepared Citrus dataset:

- initialized with `weights/lite-mono/lite-mono-pretrain.pth` through `--mypretrain`
- did not use `--load_weights_folder weights/lite-mono`
- batch size 12
- 30 epochs
- input size `640x192`
- temporal frames `[0, -1, 1]`
- seed 0

## Source Paths

Original final checkpoint source:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/models/weights_29/
```

Original result folder:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/
```

## Metric Summary

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus baseline | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus baseline | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |

## Conclusion

Mixed baseline evidence.

B0 improves median-scaled `a1` over original Lite-Mono on validation and test, but worsens raw-scale metrics and median-scaled `abs_rel`. Future Milestone 4 methods should try to keep the stronger threshold accuracy while reducing the larger relative-depth errors.
