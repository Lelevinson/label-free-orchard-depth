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
- Original full baseline metric JSON/CSV result folder, preserved for existing references: `levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/`. New large generated Levinson outputs should go under the relevant snapshot's local `local_evidence/` folder or checkpoint-selection `local_results/` folder instead of this shared results area.

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

After the 01/02/03 self-supervised gates were tested and packaged, the live root `options.py` and `trainer.py` were restored to the shared baseline state. Snapshot 04 then left the live root on the temporal-cross-view method branch. Snapshot 05 superseded that active branch, and Snapshot 06 reuses the same teacher-anchored implementation with a config-only stabilization. Live root `options.py`, `trainer.py`, the teacher diagnostic renderer, and the visual comparison helper remain on the teacher-anchored regularization branch, with tested copies and patch artifacts preserved under `levinson/snapshots/05_teacher_anchored_relative_structure_regularization/` and `levinson/snapshots/06_teacher_anchor_stabilization/`.

Large local generated evidence policy:

- Keep compact, curated snapshot evidence in the snapshot root folders.
- Keep bulky generated panels, NPZ arrays, and exhaustive sweep folders under snapshot-local `local_evidence/` or checkpoint-selection `local_results/`.
- The shared `.gitignore` now ignores Levinson `runs/`, `results/`, snapshot `local_evidence/`, and checkpoint-selection `local_results/` folders so future generated evidence does not flood Git. This checkout also keeps matching `.git/info/exclude` rules as a personal safety net.

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

## Vegetation-General Temporal Cross-View Consistency Gate

Snapshot:

```text
levinson/snapshots/04_vegetation_general_temporal_cross_view_consistency/
```

Purpose:

- keep Levinson's path self-supervised and RGB-only at inference
- add training-only temporal geometry, visibility masking, texture ambiguity weighting, and feature cross-view consistency
- target generic vegetation failure modes: repeated local texture, thin occlusions, overlapping plants, and RGB-depth mismatch
- avoid any `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, green-pixel mask, or citrus-specific detector as a training signal

Tested options include:

```text
--temporal_geo_consistency
--visibility_aware_geo
--texture_ambiguity_weighting
--feature_cross_view_consistency
```

The source-frame branch was revised to a stop-gradient teacher after an initial batch-size-12 attempt was too slow when source predictions participated in the backward graph.

First-100 validation at step 250:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Same-budget no-mask ImageNet-pretrain control, step 250 | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Temporal geometry | 0.9033 | 0.0000 | 0.5666 | 0.3597 |
| Geometry + default visibility | 0.9030 | 0.0000 | 0.5688 | 0.3581 |
| Geometry + strict visibility `0.003` | 0.9027 | 0.0000 | 0.5884 | 0.3107 |
| Geometry + texture ambiguity | 0.9028 | 0.0000 | 0.5651 | 0.3605 |
| Geometry + feature consistency | 0.9129 | 0.0000 | 0.5581 | 0.3373 |
| Full reduced-feature method | 0.9366 | 0.0000 | 0.5755 | 0.3503 |

Conclusion:

```text
stable but weak negative evidence; do not scale
```

The best branch, geometry + texture ambiguity, gave only a tiny median-scaled `a1` gain over the same-budget control and still worsened median-scaled `abs_rel`. Feature consistency improved `abs_rel` but hurt `a1`; strict visibility became too sparse; full stacking was negative. Do not launch a longer Snapshot 04 run.

Follow-up diagnostic and next-method proposal:

```text
levinson/snapshots/04_vegetation_general_temporal_cross_view_consistency/diagnostic_report_and_snapshot05_proposal.md
```

Completed Snapshot 05:

```text
levinson/snapshots/05_teacher_anchored_relative_structure_regularization/
```

Method framing:

```text
Teacher-Anchored Relative-Structure Regularization for Label-Free Self-Supervised Vegetation Adaptation
```

This replacement moved away from cross-view self-consistency and tested a frozen RGB-only teacher as a training-only relative-structure anchor. The student still trained with the normal Citrus self-supervised photometric video objective from ImageNet encoder pretrain. The teacher was the original RGB-only Lite-Mono checkpoint at `weights/lite-mono/`; it was not trained and did not use Citrus labels. The run did not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses or masks. Inference remains one RGB image into the student Lite-Mono depth network.

Full run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/
```

Saved evaluation:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full/
```

Full validation/test comparison:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |

Conclusion:

```text
continue / promising mixed
```

Snapshot 05 improves B0's raw and median-scaled `abs_rel` on validation/test while keeping most of B0's median-scaled `a1` gain. It also beats original Lite-Mono on median-scaled `a1`, but still trails original Lite-Mono on median-scaled `abs_rel`, so it is not a clean win yet.

Completed Snapshot 06:

```text
levinson/snapshots/06_teacher_anchor_stabilization/
```

Method framing:

```text
Teacher Anchor Stabilization for Label-Free Teacher-Anchored Self-Supervised Adaptation
```

Snapshot 06 is a deliberate Snapshot 05 ablation. It kept the frozen RGB-only teacher and scale-invariant structure/gradient losses, but reduced `--teacher_ranking_weight` from `0.02` to `0.005` and removed `--teacher_texture_ambiguity_emphasis`. It did not add any depth labels, valid masks, LiDAR, ZED depth, or LiDAR-derived training masks/losses. Inference remains one RGB image into the student Lite-Mono depth network.

Full run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/
```

Saved evaluation:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/
```

Full validation/test comparison:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 06 | val | 0.7375 | 0.0165 | 0.4578 | 0.5993 |
| original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 06 | test | 0.7348 | 0.0150 | 0.4168 | 0.6418 |

Conclusion:

```text
promising mixed / marginal stabilization
```

Snapshot 06 slightly improves Snapshot 05 on validation median-scaled `abs_rel` and `a1`, but slightly worsens test median-scaled `abs_rel` and `a1`. Keep it as a useful ablation, not a clean replacement for Snapshot 05. Future Levinson teacher-anchor work should change the schedule/checkpoint-selection logic more clearly rather than keep nudging ranking or texture weights.

## Teacher-Anchor Checkpoint Selection

Checkpoint-selection note:

```text
levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md
```

Sweep output:

```text
levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/
```

Selected Snapshot 05 `weights_19` visual/inference package:

```text
levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
```

Selection rule:

```text
Full validation only. Select the lowest median-scaled abs_rel checkpoint whose validation median-scaled a1 is within 0.02 absolute of B0 validation a1. Evaluate test only after selection.
```

Selected checkpoints:

| run | selected checkpoint | val median abs_rel | val median a1 | test median abs_rel | test median a1 |
|---|---|---:|---:|---:|---:|
| Snapshot 05 | `weights_19` | 0.4447 | 0.5915 | 0.3947 | 0.6476 |
| Snapshot 06 | `weights_25` | 0.4493 | 0.5925 | 0.4076 | 0.6359 |

Interpretation:

Snapshot 05 `weights_19` is the strongest current Levinson label-free teacher-anchor checkpoint. It clearly improves B0 test median-scaled `abs_rel` (`0.4889` to `0.3947`) while keeping most of B0 test median-scaled `a1` (`0.6582` to `0.6476`). It gets close to original Lite-Mono test median-scaled `abs_rel=0.3836`, but does not beat it. Do not use test to choose a different checkpoint unless a new explicit selection protocol is defined.

The 2026-05-19 visual packaging pass generated comparison panels against original Lite-Mono, B0, and Snapshot 05 `weights_29` on validation and test, plus plain selected-checkpoint RGB/depth/disparity outputs. Visual read: mixed but useful. `weights_19` should be the main Snapshot 05 paper-table checkpoint, while `weights_29` remains the final-epoch ablation/evidence point. No new training was run for this packaging step. The bulky generated visual package is intentionally snapshot-local and locally ignored.
