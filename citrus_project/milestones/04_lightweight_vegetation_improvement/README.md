# Milestone 4: Lightweight Vegetation Improvement

Use this folder for milestone-specific helpers, notes, or experiment files related to:

- lightweight architecture changes
- vegetation-focused loss or feature ideas
- ablations and efficiency checks

## Plain Lite-Mono Citrus Baseline

Before testing a Milestone 4 improvement, run a plain Lite-Mono baseline trained on Citrus using the same data budget that the improved method will later use.

Purpose:

- train plain Lite-Mono on Citrus without using the KITTI depth-trained Lite-Mono checkpoint
- use the Lite-Mono ImageNet encoder pretrain as the starting visual-feature initialization
- keep the recipe close to the Lite-Mono paper/README training setup
- save outputs under the Milestone 4 workspace for tidy comparison

Confirmed recipe:

| setting | value |
|---|---|
| initialization | `weights/lite-mono/lite-mono-pretrain.pth` through `--mypretrain` |
| do not use | `--load_weights_folder weights/lite-mono` |
| dataset | Citrus prepared dataset |
| model | `lite-mono` |
| input size | `640x192` |
| batch size | `12` |
| epochs | `30` |
| LR schedule args | `0.0001 0.000005 31 0.0001 0.00001 31` |
| optimizer | AdamW from trainer |
| weight decay | `0.01` |
| drop path | `0.2` |
| pose encoder init | `--weights_init pretrained` |
| data loader workers | `0` for first overnight Windows run |
| checkpointing | every epoch |

Run from the repo root:

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4 `
  --log_dir citrus_project/milestones/04_lightweight_vegetation_improvement/runs `
  --mypretrain weights/lite-mono/lite-mono-pretrain.pth `
  --weights_init pretrained `
  --batch_size 12 `
  --num_epochs 30 `
  --lr 0.0001 0.000005 31 0.0001 0.00001 31 `
  --weight_decay 0.01 `
  --drop_path 0.2 `
  --height 192 `
  --width 640 `
  --num_workers 0 `
  --log_frequency 100 `
  --save_frequency 1 `
  --seed 0
```

Expected output folder:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/
```

Expected runtime:

```text
about 10-15 hours on the RTX 4060 Laptop GPU
```

Important note:

Do not add `--load_weights_folder weights/lite-mono` to this command. That would change the experiment from "Citrus training from ImageNet pretrain" into "fine-tuning the KITTI-trained Lite-Mono checkpoint."

## Mid-Run Checkpoint Probe

While the 30-epoch run was still active, checkpoint `weights_15` was evaluated on the first 100 validation samples using CPU inference so the evaluator would not compete with training for GPU memory.

Command shape:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split val `
  --max_samples 100 `
  --run_model `
  --summary_only `
  --progress_interval 25 `
  --weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/models/weights_15 `
  --model lite-mono `
  --no_cuda
```

Result:

| checkpoint | eval scope | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 | note |
|---|---|---:|---:|---:|---:|---|
| original Lite-Mono | first-100 val | 0.7289 | n/a | 0.3680 | 0.4807 | reference from Milestone 3 advisor table |
| ImageNet-pretrained Citrus baseline, `weights_15` | first-100 val | 0.7807 | 0.0055 | 0.4478 | 0.6720 | mixed mid-run signal: better median-scaled `a1`, worse median-scaled `abs_rel` |

Interpretation:

- This is not the final result.
- Training was still running, so this is only a mid-run checkpoint probe.
- The model is learning something different from the Milestone 3 fine-tuning runs: `a1` improved after median scaling, but mean relative error (`abs_rel`) is still worse than the original first-100 reference.
- Final checkpoint evaluation is documented below.

Note:

The evaluator printed the metrics successfully, but saving JSON/CSV from this assistant-side process was blocked by a local permission error while the run folder was active. The printed metrics above are preserved here.

## Final 30-Epoch Checkpoint Evaluation

The run finished successfully and originally produced checkpoints `weights_0` through `weights_29`.

Final checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/models/weights_29/
```

Saved evaluation outputs:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/results/plain_litemono_imagenet_b12_30ep_final_weights29/
```

Full validation/test comparison against the original Lite-Mono checkpoint:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| ImageNet-pretrained Citrus baseline, `weights_29` | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| ImageNet-pretrained Citrus baseline, `weights_29` | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |

Interpretation:

- The final checkpoint is not a clean win over the original checkpoint.
- Raw-scale metrics are worse, so the trained model still does not predict correct metric depth scale.
- Median-scaled `a1` is clearly better on both validation and test, meaning more valid pixels land within the common "close enough" depth threshold after one per-image scale correction.
- Median-scaled `abs_rel` is worse on both validation and test, meaning the average relative depth error is still larger even though more pixels pass the threshold.
- Plain meaning: the model learned useful Citrus relative-depth structure in many pixels, but it also makes larger errors in enough places that it cannot yet be called a strong improvement.

Comparison visuals:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/results/plain_litemono_imagenet_b12_30ep_final_weights29/visual_compare_original_vs_final_val_full/
```

Generated panels:

```text
adapted_good_index_0094_comparison.png
adapted_typical_index_0277_comparison.png
adapted_bad_index_0445_comparison.png
largest_drop_vs_original_index_0394_comparison.png
```

Temporary one-image panels under `citrus_project/research/generated/` were deleted before generating these final comparison panels.

## Checkpoint Storage

The full training run folder is local/ignored.

Current local checkpoint state after the 2026-05-11 cleanup:

- `weights_0` through `weights_28` were deleted locally.
- full `weights_29` remains in the ignored run folder for unlikely exact-resume/debug needs.
- committed metrics, visuals, and inference-only weights remain tracked separately.

Tracked inference-only copy:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/baseline_checkpoint/plain_litemono_imagenet_b12_30ep_weights29_inference/
```

This tracked copy contains only the final `encoder.pth` and `depth.pth` needed for RGB-only depth inference/evaluation. It does not include pose-network weights or optimizer states.

Note:

A checkpoint sweep was briefly tried after the final evaluation, but it was removed from the committed milestone evidence after visual review. The current recorded result is the final `weights_29` baseline above.
