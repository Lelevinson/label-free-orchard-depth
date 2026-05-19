# Snapshot 06: Teacher Anchor Stabilization

Status: completed full 30-epoch run, evaluated on full validation and test.

Conclusion: `promising mixed / marginal stabilization`. Snapshot 06 is a useful ablation of Snapshot 05, but it is not a clean replacement.

## Method

Training-supervision label: `label-free teacher-anchored self-supervised adaptation`.

Snapshot 06 keeps the Snapshot 05 frozen RGB-only Lite-Mono teacher from `weights/lite-mono/`, but changes the enabled configuration:

- reduced `--teacher_ranking_weight` from `0.02` to `0.005`
- removed `--teacher_texture_ambiguity_emphasis`
- kept scale-invariant structure agreement at `--teacher_structure_weight 0.03`
- kept local gradient agreement at `--teacher_gradient_weight 0.01`
- kept `--teacher_structure_warmup_steps 500`, `--teacher_structure_decay 0.5`, and `--teacher_rank_samples 512`

Why: Snapshot 05 improved average relative structure but trailed B0 on median-scaled `a1`. Its final diagnostics showed ranking as the largest teacher loss, and visual/per-sample checks suggested some over-regularized threshold errors. Snapshot 06 tested whether weaker ranking plus no texture boost would recover `a1` while preserving the `abs_rel` gain.

What did not change:

- no depth labels, valid masks, LiDAR, ZED depth, or LiDAR-derived labels are used as training losses or training masks
- teacher is frozen, RGB-only, and training-only
- student starts from ImageNet encoder pretrain via `--mypretrain weights/lite-mono/lite-mono-pretrain.pth`
- student is not initialized from the KITTI depth-trained checkpoint
- inference remains one RGB image into the Lite-Mono student DepthNet
- dataset, split, batch size, epochs, seed, input size, optimizer, and LR schedule match B0/Snapshot 05
- no Marvel supervised/hybrid code or evidence is used

## Command

Full training command is saved at:

```text
commands/train_full.ps1
```

The effective command was:

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name teacher_anchor_stabilization_b12_30ep_rank005_no_texture `
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
  --seed 0 `
  --teacher_structure_regularization `
  --teacher_structure_weight 0.03 `
  --teacher_structure_warmup_steps 500 `
  --teacher_structure_decay 0.5 `
  --teacher_gradient_loss `
  --teacher_gradient_weight 0.01 `
  --teacher_ranking_loss `
  --teacher_ranking_weight 0.005 `
  --teacher_rank_samples 512 `
  --teacher_path weights/lite-mono
```

## Paths

Full run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/
```

Final checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29/
```

Evaluation results:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/
```

This generated evidence folder is snapshot-local and ignored by this machine's `.git/info/exclude`; compact summaries remain in `results/`.

Snapshot package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/
```

## Metrics

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 06 | val | 0.7375 | 0.0165 | 0.4578 | 0.5993 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 06 | test | 0.7348 | 0.0150 | 0.4168 | 0.6418 |

First-100 validation orientation for Snapshot 06 final checkpoint:

| scope | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| val first 100 | 0.7314 | 0.0053 | 0.3458 | 0.6558 |

## Visuals

Visual comparison panels and teacher-structure diagnostic maps are saved in the generated evidence folder:

```text
local_evidence/visual_summary/visual_compare_original_vs_snapshot06_val_full/
local_evidence/visual_summary/visual_compare_b0_vs_snapshot06_val_full/
local_evidence/visual_summary/visual_compare_snapshot05_vs_snapshot06_val_full/
local_evidence/visual_summary/teacher_structure_diagnostic_maps/
```

The diagnostic maps include selected validation indices `95`, `2`, `21`, `175`, `171`, `394`, and `196`.

## Interpretation

Snapshot 06 partially supports the diagnosis that Snapshot 05's ranking and texture emphasis were too strong: validation improves slightly in both median-scaled `abs_rel` and `a1`. But the test split moves the other way, with slightly worse median-scaled `abs_rel` and `a1` than Snapshot 05. This means reduced ranking/no texture was not the whole cause of the remaining tradeoff.

Snapshot 06 remains better than B0 on median-scaled `abs_rel`, but it still trails B0 on median-scaled `a1`. It also still trails original Lite-Mono on median-scaled `abs_rel`, while beating original Lite-Mono on median-scaled `a1`.

Research decision: keep Snapshot 06 as a deliberate stabilization ablation. Do not declare it the new best method over Snapshot 05. A next label-free direction should probably change the teacher schedule or checkpoint selection policy more fundamentally, rather than only lowering ranking/texture pressure.

## Checkpoint Selection Follow-Up

A later validation-first checkpoint sweep selected Snapshot 06 `weights_25` under the same B0-close `a1` rule used for Snapshot 05:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md
```

Snapshot 06 `weights_25` test metrics are median-scaled `abs_rel=0.4076` and `a1=0.6359`. This improves over B0 on median-scaled `abs_rel`, but it remains weaker than validation-selected Snapshot 05 `weights_19` (`abs_rel=0.3947`, `a1=0.6476`). Snapshot 06 should remain a marginal ablation rather than the lead teacher-anchor checkpoint.

## Code State

No new Python implementation was needed beyond the active Snapshot 05 teacher branch. Tested active files are still copied into `code/` for reproducibility:

```text
code/options.py
code/trainer.py
code/citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py
code/citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py
```

Root code remains active on the teacher-anchored branch. It was not restored to the shared baseline state after this run.
