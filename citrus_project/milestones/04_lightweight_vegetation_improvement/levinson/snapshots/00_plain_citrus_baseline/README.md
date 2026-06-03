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
- this is "Citrus-only depth training from ImageNet visual features", not random-weight scratch training (agreed fair baseline init)
- batch size 12
- 30 epochs
- learning-rate schedule `0.0001 5e-6 31 0.0001 1e-5 31`, AdamW, weight decay `1e-2`, drop path `0.2`
- input size `640x192`
- temporal frames `[0, -1, 1]`
- `--weights_init pretrained` for the pose ResNet encoder (matches the Lite-Mono paper PoseNet setup)
- `--num_workers 0` for Windows data-loading stability (engineering setting, not a research hyperparameter)
- seed 0
- run completed 2026-05-10; roughly 10–15 h on the RTX 4060 Laptop (consistent with the earlier batch-size-12 one-epoch timing)
- the full `config/opt.json` in this snapshot is the source of truth for exact options

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

## Provenance Notes

- Historical mid-run `weights_15` CPU first-100 validation probe (not the promoted checkpoint): raw `abs_rel=0.7807`, raw `a1=0.0055`, median-scaled `abs_rel=0.4478`, median-scaled `a1=0.6720`. Versus the original first-100 reference (`abs_rel=0.3680`, `a1=0.4807`) this was a mixed signal — `a1` improved, `abs_rel` worsened. The promoted B0 checkpoint is the final-epoch `weights_29` above, not `weights_15`.
- A checkpoint sweep over the plain-baseline epochs was tried after final evaluation but discarded from committed evidence after visual review. Do not use sweep-derived checkpoints as representative Milestone 4 baselines unless a later, explicitly approved selection rule reintroduces them.
- On 2026-05-11 the old epoch checkpoints `weights_0`–`weights_28` were deleted locally; full `weights_29` was kept for unlikely exact-resume/debug needs. The old `baseline_checkpoint/` inference-only copy was removed after B0 was migrated into this snapshot structure.

## Conclusion

Mixed baseline evidence.

B0 improves median-scaled `a1` over original Lite-Mono on validation and test, but worsens raw-scale metrics and median-scaled `abs_rel`. Future Milestone 4 methods should try to keep the stronger threshold accuracy while reducing the larger relative-depth errors.
