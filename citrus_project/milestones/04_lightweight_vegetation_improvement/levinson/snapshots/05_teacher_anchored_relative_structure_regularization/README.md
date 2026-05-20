# Snapshot 05: Teacher-Anchored Relative-Structure Regularization

Status: full 30-epoch run completed. Checkpoint-selection update: `weights_19` became the strongest pre-Snapshot07 Levinson label-free teacher-anchor candidate. Conclusion: promising mixed evidence; use the validation-selected checkpoint as the main Snapshot 05 comparison point, but do not claim a clean win over original Lite-Mono.

Method framing:

```text
Teacher-Anchored Relative-Structure Regularization for Label-Free Self-Supervised Vegetation Adaptation
```

This snapshot replaces Snapshot 04's weak cross-view self-consistency with a training-only frozen RGB teacher. The student still learns from the standard self-supervised monocular video photometric objective, but extra losses ask it to preserve relative depth structure from the teacher while adapting to Citrus.

## Why This Is Label-Free

Training uses only monocular RGB frames, camera intrinsics, predicted poses, and frozen RGB teacher predictions. It does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses or training masks.

Citrus dense labels and valid masks are used only for evaluation.

This is not pure self-supervised from scratch: the student is regularized by a frozen RGB-only teacher checkpoint. The honest label is `label-free teacher-anchored self-supervised adaptation` or `RGB-teacher-guided relative-structure regularization`.

Inference remains unchanged and lightweight: one RGB image goes into the student Lite-Mono encoder/depth decoder. The teacher, PoseNet, ranking loss, gradient loss, structure loss, and diagnostics are training-only.

## Teacher

Teacher checkpoint:

```text
weights/lite-mono/
```

This is the same frozen RGB-only Lite-Mono checkpoint used as the original baseline. It predicts depth/disparity from RGB only. It is not trained, and no Citrus labels are used to create teacher targets.

The teacher is used only for scale-invariant relative structure:

- normalized log inverse-depth agreement
- normalized local disparity-gradient agreement
- sparse pairwise ordinal/ranking consistency

The student is not forced to copy teacher metric scale.

## Source Code Changes

Changed tested files copied here:

```text
code/options.py
code/trainer.py
code/citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py
code/citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py
code/citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/render_selected_checkpoint_inference_visuals.py
code/citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/scripts/render_weights19_professor_visual_diagnostics.py
patches/final_method.diff
```

At Snapshot 05 packaging time, root code remained active as the Snapshot 05 branch and was not restored to the shared baseline state. That historical state was later superseded by Snapshot 07; read `../../ACTIVE_ROOT_CODE_STATE.md` for the current root-code state.

## Flags

All Snapshot 05 flags are disabled by default, preserving original behavior when they are off:

```text
--teacher_structure_regularization
--teacher_structure_weight
--teacher_structure_warmup_steps
--teacher_structure_decay
--teacher_gradient_loss
--teacher_gradient_weight
--teacher_ranking_loss
--teacher_ranking_weight
--teacher_rank_samples
--teacher_confidence
--teacher_confidence_threshold
--teacher_texture_ambiguity_emphasis
--teacher_path
```

Teacher confidence is implemented but was not enabled for the full run.

## Commands

Command scripts:

```text
commands/train_smoke.ps1
commands/train_full.ps1
commands/evaluate_final.ps1
commands/visuals_and_diagnostics.ps1
```

Selected-checkpoint and professor-facing visual command scripts are kept with the checkpoint-selection note:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/commands/render_snapshot05_weights19_visuals.ps1
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/commands/render_weights19_professor_visual_diagnostics.ps1
```

Full run command:

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name teacher_structure_regularization_b12_30ep_full `
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
  --teacher_ranking_weight 0.02 `
  --teacher_rank_samples 512 `
  --teacher_texture_ambiguity_emphasis `
  --texture_ambiguity_weight 0.25 `
  --teacher_path weights/lite-mono
```

## Outputs

Full training output:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/
```

Final checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_29/
```

Validation-selected checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_19/
```

`weights_19` was selected after training by the validation-only checkpoint-selection rule documented in:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md
```

No new training was run for the checkpoint-selection or visual-packaging update. Test was used only after selection.

Evaluation output:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full/
```

This generated evidence folder is snapshot-local and ignored by this machine's `.git/info/exclude`; compact summaries remain in `results/`.

Snapshot-copied evidence:

```text
config/opt.json
diagnostics/diagnostics_last_logged.json
diagnostics/diagnostics_last_logged.csv
diagnostics/smoke_diagnostics_last_logged.json
diagnostics/weights19_professor_visual_diagnosis_summary.md
results/val_lite-mono_full_summary.json
results/test_lite-mono_full_summary.json
results/val_lite-mono_max100_summary.json
results/comparison_summary.csv
results/comparison_summary.json
results/result_summary.md
local_evidence/visual_summary/
```

## Metrics

Full validation/test comparison:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |

Validation-selected checkpoint update:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 `weights_29` | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 05 selected `weights_19` | val | 0.7389 | 0.0177 | 0.4447 | 0.5915 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 `weights_29` | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 05 selected `weights_19` | test | 0.7391 | 0.0144 | 0.3947 | 0.6476 |

Interpretation: `weights_19` is preferred over `weights_29` because later epochs appear to trade off or over-drift: `weights_19` has better validation median-scaled `abs_rel` under the pre-declared `a1` constraint and also improves test median-scaled `abs_rel` and `a1` versus `weights_29`.

First-100 validation orientation:

| model | budget | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Snapshot 04 no-mask control | 250 steps | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Snapshot 04 best branch | 250 steps | 0.9028 | 0.0000 | 0.5651 | 0.3605 |
| Snapshot 05 | final 30-epoch checkpoint | 0.7314 | 0.0053 | 0.3444 | 0.6510 |

The first-100 Snapshot 05 row is not same-budget with Snapshot 04; it is included only to show that the full teacher-anchored run moved far beyond the weak Snapshot 04 gate behavior.

## Visuals

Copied visual outputs:

```text
local_evidence/visual_summary/visual_compare_original_vs_snapshot05_val_full/
local_evidence/visual_summary/visual_compare_b0_vs_snapshot05_val_full/
local_evidence/visual_summary/teacher_structure_diagnostic_maps/
```

Selected `weights_19` visual package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
```

Contents:

```text
comparison_panels/original_vs_weights19_val_full/
comparison_panels/b0_vs_weights19_val_full/
comparison_panels/weights29_vs_weights19_val_full/
comparison_panels/original_vs_weights19_test_full/
comparison_panels/b0_vs_weights19_test_full/
comparison_panels/weights29_vs_weights19_test_full/
plain_inference_depth_outputs/
result_summary.md
```

The plain inference folder contains actual `weights_19` RGB, raw-depth, median-scaled-depth, disparity, panel, and NPZ array outputs for representative validation and test samples.

Professor-facing `weights_19` visual diagnosis package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/
```

Contents:

```text
full_image_qualitative/
valid_mask_evaluation/
cropped_masked_evaluation/
weights29_vs_weights19/
plain_inference/
sample_selection.csv
sample_selection.json
visual_diagnosis.md
```

This package is the clearest professor-facing visual evidence for the selected checkpoint. It explicitly separates full-frame qualitative artifacts from valid-LiDAR evaluation behavior. Its conclusion is honest: `weights_19` is numerically promising and worth discussing, but not visually solved or paper-polished because dark plant blobs, smoothed vegetation, and sky/far-canopy boundary artifacts remain.

Teacher diagnostic maps include:

```text
input_rgb.png
student_depth_gray.png
teacher_depth_gray.png
student_disp_gray.png
teacher_disp_gray.png
student_normalized_structure_gray.png
teacher_normalized_structure_gray.png
student_teacher_structure_diff_gray.png
teacher_gradient_error_gray.png
texture_ambiguity_gray.png
photo_error_gray.png
```

`teacher_confidence_gray.png` is absent because `--teacher_confidence` was off.

## Vegetation Scope

This method is meant for vegetation-heavy farm scenes in general, not citrus-specific appearance. It does not use a citrus detector, fruit/tree heuristic, green-pixel threshold, hand-labeled vegetation mask, or Citrus depth label during training.

The assumptions are generic:

- repeated local leaf/branch texture can mislead photometric matching
- thin occlusions and overlapping plants can damage temporal reconstruction
- RGB edges do not always correspond to depth edges
- a frozen RGB teacher can preserve useful relative ordering while the student adapts photometrically to the new farm domain

## Interpretation

What worked:

- The method is stable at batch size 12 for the full 30-epoch run.
- It improves raw and median-scaled `abs_rel` substantially over the B0 plain Citrus baseline.
- It keeps most of B0's median-scaled `a1` improvement and remains far better than original Lite-Mono on median-scaled `a1`.
- Teacher/student diagnostic maps are meaningful enough to inspect boundaries and structure disagreement.

What failed or stayed mixed:

- Snapshot 05 does not beat original Lite-Mono on median-scaled `abs_rel`.
- It slightly trails B0 on median-scaled `a1`.
- The frozen teacher may preserve useful ordering while also importing original-checkpoint bias.

Decision:

```text
continue / promising mixed
```

This is the strongest Levinson label-free direction so far, and it is clearly different from Snapshot 04. After validation-only checkpoint selection, `weights_19` should be used as the main Snapshot 05 result in paper tables. The result remains mixed: it nearly closes the original Lite-Mono median-scaled `abs_rel` gap on test while preserving B0-like `a1`, but it still does not beat original Lite-Mono on median-scaled `abs_rel`.

## Follow-Up

Snapshot 06 tested the immediate stabilization hypothesis by reducing ranking weight from `0.02` to `0.005` and removing texture-ambiguity emphasis:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/
```

It slightly improved validation over Snapshot 05 but slightly worsened test, so it should be treated as a marginal ablation rather than a clean replacement. Future teacher-anchor work should change schedule or checkpoint-selection logic more clearly instead of only nudging ranking/texture weights.

## Checkpoint Selection Follow-Up

A validation-first checkpoint sweep later evaluated Snapshot 05 and Snapshot 06 `weights_0` through `weights_29` on full validation and tested only the selected checkpoints:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md
```

Under the rule "lowest validation median-scaled `abs_rel` while keeping validation median-scaled `a1` within `0.02` of B0", Snapshot 05 `weights_19` is selected and becomes the strongest pre-Snapshot07 Levinson label-free teacher-anchor checkpoint. Its test metrics are median-scaled `abs_rel=0.3947` and `a1=0.6476`, better than this snapshot's final `weights_29` test metrics.

The selected-checkpoint visual package was generated on 2026-05-19:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/
```

Visual read: mixed but useful. Good/typical cases show the broad relative-structure improvement behind the metric gains, while failure/largest-drop cases still show smooth predictions and over-correction around vegetation and occlusion regions. This supports using `weights_19` as the main Snapshot 05 comparison point, not claiming a clean visual or metric win over original Lite-Mono.

A clearer professor-facing visual diagnosis was generated afterward:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/visual_diagnosis.md
```

It should be used for discussion because it shows full-image qualitative issues, valid-mask-only error behavior, cropped evaluated regions, `weights_29` versus `weights_19`, and simple plain-inference panels without hiding failure cases.
