# Milestone 4: Lightweight Vegetation Improvement

Use this folder for milestone-specific helpers, notes, or experiment files related to:

- lightweight architecture changes
- vegetation-focused loss or feature ideas
- ablations and efficiency checks

## Read Map

For Milestone 4 work, use this README as the main handoff. Do not inspect every result or snapshot folder by default.

- Baseline recipe, final metrics, checkpoint paths, and visual paths: this README.
- Levinson's Milestone 4 workstream, including the B0 plain Citrus baseline snapshot and tested 01/02/03 method-gate snapshots: `levinson/README.md`.
- Marvel's supervised/hybrid Milestone 4 workstream: `Marvel/README.md`.
- Original full baseline metric JSON/CSV result folder, preserved for existing references: `levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/`.

Levinson improvement code snapshots use descriptive numeric folders such as `levinson/snapshots/01_photometric_confidence_masking/` once an improvement is implemented and tested. Paper-style labels such as `A` or `A+B` can still be written inside stage READMEs later if useful.

## Workstream Folders

Milestone 4 uses small person/workstream folders so each contributor can keep their progress tidy without mixing snapshot evidence:

```text
levinson/
Marvel/
```

- `levinson/` contains the current completed B0 baseline snapshot and Levinson's self-supervised RGB-only Milestone 4 method gates.
- `Marvel/` is Marvel's supervised or hybrid Milestone 4 workstream. It may explore valid-depth, valid-mask, or LiDAR-guided training ideas.

Collaboration rule:

- Keep each person's Milestone 4 runs, results, snapshots, and helper notes inside their own workstream folder.
- Use the shared Milestone 4 README for rules that affect both workstreams.
- Do not edit another person's snapshots or results unless that person explicitly approves it.
- Before changing shared root training/model files, confirm the change and then copy the tested `.py` files into the relevant stage snapshot.
- Levinson's workstream should prioritize self-supervised RGB-only training methods and should not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED depth as a training loss unless a separate hybrid branch is explicitly approved.
- Marvel's workstream may use valid depth labels, valid masks, or LiDAR-guided training losses, but those runs must be labeled supervised or hybrid.
- Both workstreams may keep inference RGB-only, but training supervision differs. Do not present supervised/hybrid results as directly fair wins over self-supervised results without clear labeling and matched comparison context.

When a tested Milestone 4 stage changes Python files, duplicate the tested versions into that stage snapshot under `code/`. Use clear relative paths, for example:

```text
levinson/snapshots/01_method_name/code/trainer.py
levinson/snapshots/01_method_name/code/options.py
levinson/snapshots/01_method_name/code/layers.py
levinson/snapshots/01_method_name/code/networks/depth_decoder.py
```

If a completed stage has no code changes, use a simple marker such as `code/NO_CODE_CHANGES.txt`.

Current collaboration note:

After the 01/02/03 self-supervised gates were tested and packaged, the live root `options.py` and `trainer.py` were restored to the shared baseline state. The experimental method code is preserved in each tested snapshot under `code/`; it is not currently active in the global trainer.

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
  --log_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs `
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
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/
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
  --weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/models/weights_15 `
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
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/models/weights_29/
```

Saved evaluation outputs:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/
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
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/visual_compare_original_vs_final_val_full/
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

Final B0 baseline snapshot:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/
```

This snapshot contains the final inference weights, copied result CSV/JSON files, copied visual panels, and copied `config/opt.json`. It does not include pose-network weights or optimizer states.

The old `baseline_checkpoint/` inference-only copy was removed after this migration.

Note:

A checkpoint sweep was briefly tried after the final evaluation, but it was removed from the committed milestone evidence after visual review. The current recorded result is the final `weights_29` baseline above.

## Photometric-Confidence Masking Gate

Snapshot:

```text
levinson/snapshots/01_photometric_confidence_masking/
```

Purpose:

- keep Milestone 4 self-supervised for now
- keep inference unchanged
- add a training-only confidence weight on top of existing automasking
- downweight pixels where warped RGB reconstruction only barely beats identity/no-warp reconstruction
- avoid any `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED-depth training loss

Snapshot-tested options:

```text
--photometric_confidence_masking
--photometric_confidence_threshold 0.01
--photometric_confidence_ramp 0.05
--photometric_confidence_min_weight 0.25
```

These options are preserved in the snapshot code copy. They are not currently active in the restored root trainer unless that snapshot code is intentionally reapplied.

First 250-step gate from ImageNet encoder pretrain:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Original Lite-Mono first-100 reference | 0.7289 | 0.0131 | 0.3680 | 0.4807 |
| Same-budget no-mask ImageNet-pretrain control, step 250 | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Photometric-confidence masking, step 250 | 0.8985 | 0.0000 | 0.5582 | 0.3018 |

Conclusion:

```text
uncertain / do not scale yet
```

The method is technically stable and the confidence signal is not near zero everywhere, but the 250-step metric signal is mixed: slightly better median-scaled `abs_rel` than the same-budget no-mask control, worse median-scaled `a1`, and still much weaker than the original first-100 reference. Do not launch a longer photometric-confidence run without a follow-up reason such as tuning the confidence schedule or inspecting confidence masks directly.

## RGB-Edge Structure-Preserving Loss Gate

Snapshot:

```text
levinson/snapshots/02_rgb_edge_structure_preserving_loss/
```

Purpose:

- keep Milestone 4 self-supervised
- keep inference unchanged
- test whether a conservative RGB-edge disparity-gradient loss can reduce over-smoothing
- avoid any `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED-depth training loss
- do not combine with confidence masking or vegetation weighting

Snapshot-tested options:

```text
--rgb_edge_structure_loss
--rgb_edge_structure_weight 0.01
--rgb_edge_structure_threshold 0.08
--rgb_edge_structure_blur_kernel 5
--rgb_edge_structure_target_grad 0.02
```

These options are preserved in the snapshot code copy. They are not currently active in the restored root trainer unless that snapshot code is intentionally reapplied.

First 250-step gate from ImageNet encoder pretrain:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Same-budget no-mask ImageNet-pretrain control, step 250 | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| RGB-edge structure loss, step 250 | 0.8993 | 0.0000 | 0.5822 | 0.3280 |

Conclusion:

```text
stop
```

The run was stable and self-supervised, but it worsened both median-scaled `abs_rel` and median-scaled `a1` versus the same-budget no-mask control. Do not scale this exact configuration.

## Soft Confidence Multiplier Gate

Snapshot:

```text
levinson/snapshots/03_soft_confidence_multiplier/
```

Purpose:

- keep Milestone 4 self-supervised
- keep inference unchanged
- test whether a mild confidence multiplier avoids the normalized-weighting problem from 01
- avoid any `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED-depth training loss
- do not combine with RGB-edge structure loss

Snapshot-tested options:

```text
--soft_confidence_multiplier
--soft_confidence_threshold 0.01
--soft_confidence_ramp 0.05
--soft_confidence_strength 0.5
--soft_confidence_min_multiplier 0.75
```

These options are preserved in the snapshot code copy. They are not currently active in the restored root trainer unless that snapshot code is intentionally reapplied.

First 250-step gate from ImageNet encoder pretrain:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Same-budget no-mask ImageNet-pretrain control, step 250 | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Photometric-confidence masking 01, step 250 | 0.8985 | 0.0000 | 0.5582 | 0.3018 |
| Soft confidence multiplier, step 250 | 0.8978 | 0.0000 | 0.5676 | 0.3068 |

Conclusion:

```text
stop
```

The softer confidence multiplier did not rescue the confidence direction. It improved raw `abs_rel` slightly but worsened the relative-depth threshold metric, so do not scale this exact configuration.
