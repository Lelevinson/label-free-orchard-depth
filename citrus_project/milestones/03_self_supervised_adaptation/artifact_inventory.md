# Milestone 3 Artifact Inventory

Date: 2026-05-09
Last updated: 2026-05-11

Purpose: classify Milestone 3 notes, scripts, generated outputs, and run folders before any cleanup or deletion.

Rule:

```text
Do not delete checkpoints, run outputs, diagnostics, generated panels, scripts, or notes unless the user approves a specific cleanup list.
```

## Summary

Milestone 3 is closed as weak/negative evidence for standard self-supervised Citrus adaptation.
The artifact goal is now preservation and navigation, not more blind recipe scaling.

Professor-facing names should describe experiment purpose.
Internal `citrus_ss_*` folder names are kept only for reproducibility mapping.

2026-05-11 cleanup:

- deleted ignored smoke/pilot/VRAM run folders whose useful outcomes were already summarized in notes
- kept important evidence runs, advisor checks, and diagnostics
- kept source-of-truth notes, milestone handoff notes, and helper scripts

## Source-Of-Truth And Notes

| path | category | keep status | purpose |
|---|---|---|---|
| `AGENTS.md` | source-of-truth | keep current and compact | current project status, decisions, paths, and next actions |
| `citrus_project/milestones/03_self_supervised_adaptation/README.md` | milestone handoff | keep | concise Milestone 3 verdict, evidence table, commands, and next handoff |
| `citrus_project/milestones/03_self_supervised_adaptation/professor_loading_and_train_eval_check.md` | advisor-facing evidence | keep | parameter-loading, train-image, sparse-LiDAR, and batch-size controls |
| `citrus_project/research/baseline_notes.md` | detailed model evidence | keep | full run-by-run model behavior and comparison record |
| `citrus_project/research/advisor_notes.md` | advisor tracking | keep | professor questions and follow-up interpretations |
| `citrus_project/research/paper_shortlist.md` | paper-candidate index | keep | paper-useful results and caution notes |
| `citrus_project/research/student_qna.md` | beginner explanation | keep, compact when repetitive | stable plain-language explanations |

## Helper Scripts

| path | category | keep status | purpose |
|---|---|---|---|
| `diagnose_self_supervised_batch.py` | helper script | keep | fixed-batch diagnostics for photo loss, depth metrics, scale, masks, and pose behavior |
| `compare_original_vs_adapted_visuals.py` | helper script | keep | side-by-side visual comparison between original and adapted checkpoints |
| `run_controlled_decoderonly_lowdepthlr_1epoch.ps1` | reproducibility script | keep | launches the conservative 1000-step monitored probe |
| `evaluate_controlled_decoderonly_lowdepthlr.ps1` | reproducibility script | keep | evaluates conservative probe checkpoints |

## Evidence Runs To Preserve

These remaining runs are evidence-bearing. Keep them as Milestone 3's standard-adaptation evidence and diagnostics.

| professor-facing name | internal artifact | why preserve |
|---|---|---|
| Conservative control: safer recipe after 250/500/750/1000 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/` | main negative adapted-baseline evidence; includes step checkpoints, evaluations, and visual comparison panels |
| Control: no color augmentation after 250 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_250steps/` | shows removing color jitter reduces but does not solve relative-depth drift |
| Control: no color augmentation after 500 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_500steps/` | shows no-augmentation recipe worsens again when extended |
| Normal batch-size-12 training, one epoch | `runs/citrus_ss_batch12_normal_lr_1epoch/` | advisor-requested control showing larger true batch size does not fix the failure |
| Advisor check: training images and loading | `runs/professor_train_eval_check/` | saved first-100 train/validation evaluations used in professor note |
| Diagnostic: seeded warmup/depth-update trajectory | `runs/citrus_ss_seed0_warmup25_depth0_25steps/` and `depth5/30`, `depth15/40`, `depth25/50` | supports the finding that degradation starts soon after depth updates |
| Diagnostic: pose-only and depth-frozen controls | `runs/citrus_ss_pretrained_pose_depthfrozen_50steps/` and `runs/citrus_ss_pretrained_pose_depthencoderfrozen_depthfrozen_50steps/` | separates pose-only learning from depth-path changes; supports parameter-loading audit |
| Diagnostic: loss decomposition | `runs/diagnostics_loss_decomposition_2026-05-06/` | supports conclusion that smoothness is not the main failure driver and photo loss can improve while depth worsens |
| Diagnostic: fixed-batch internal comparison | `runs/diagnostics_fixed_m3_internal_compare/` | supports internal loss/scale/mask analysis across checkpoints |
| Diagnostic: seeded trajectory diagnostics | `runs/diagnostics_seed0_warmup25_trajectory_2026-05-06/` | diagnostic companion to seeded warmup/depth-update checkpoints |

## Summarized Evidence Deleted In 2026-05-11 Cleanup

These artifacts had useful results captured in notes and were deleted locally after user approval.

| professor-facing name | internal artifact | status |
|---|---|---|
| Early smoke: batch-4 one-step fit check | `runs/batch4_one_step_fit_check/` | deleted locally |
| Early smoke: batch-size-8 VRAM check | `runs/citrus_ss_batchsize8_vram_smoke_1step/` | deleted locally |
| Early smoke: batch-size-12 VRAM check | `runs/citrus_ss_batchsize12_vram_smoke_1step/` | deleted locally |
| Early smoke: 2-step training path | `runs/citrus_ss_finetune_smoke_2steps/` | deleted locally |
| Early smoke: 2-step retry with saved checkpoint | `runs/citrus_ss_finetune_smoke_2steps_retry/` | deleted locally |
| Early smoke: 1-step continuation | `runs/citrus_ss_finetune_smoke_resume_1step/` | deleted locally |
| Early smoke: 10-step checkpoint/evaluation plumbing | `runs/citrus_ss_finetune_smoke_10steps/` | deleted locally |
| Early pilot: 100-step fine-tuning | `runs/citrus_ss_finetune_pilot_100steps/` | deleted locally |
| Early pilot: 500-step low learning rate | `runs/citrus_ss_finetune_pilot_500steps_lr1e-5/` | deleted locally |
| Early pilot: batch size 4 and drop path 0 | `runs/citrus_ss_finetune_pilot_bs4_dp0_125steps/` | deleted locally |
| Early smoke: freeze-depth path | `runs/citrus_ss_freeze_depth_smoke_2steps/` | deleted locally |
| Early smoke: pretrained pose construction | `runs/citrus_ss_pretrained_pose_smoke_1step/` | deleted locally |
| Early pilot: pretrained-pose warmup only | `runs/citrus_ss_pretrained_pose_warmup_25steps/` | deleted locally |
| Early pilot: warmup then depth update | `runs/citrus_ss_pretrained_pose_warmup25_depth25_50steps/` | deleted locally |
| Early pilot: low-depth-LR warmup then update | `runs/citrus_ss_pretrained_pose_warmup25_depth25_50steps_depthlr1e-5/` | deleted locally |
| Early pilot: decoder-only after warmup | `runs/citrus_ss_pretrained_pose_warmup25_decoder25_50steps/` | deleted locally |
| Early pilot: previous-frame-only source | `runs/citrus_ss_prev_only_warmup25_depth25_50steps/` | deleted locally |

## Disposable-Looking Local Artifacts

These are not Milestone 3 research evidence, but still require approval before deletion if part of a cleanup command.

| path | category | note |
|---|---|---|
| `__pycache__/` | cache | disposable Python bytecode cache |
| `tmp_trainer_wiring_smoke/` | smoke output | small local smoke folder from trainer wiring |
| `citrus_project/dataset_workspace/__pycache__/` | cache | disposable Python bytecode cache |

## Generated Outputs Outside Milestone 3

| path | category | keep status |
|---|---|---|
| `citrus_project/dataset_workspace/projection_alignment_audit/` | dataset audit diagnostics | preserve unless a specific old audit output is approved for cleanup |
| `citrus_project/research/generated/` | ignored research/demo outputs | preserve unless regenerated or explicitly approved for cleanup |
| `citrus_project/milestones/01_original_lite_mono_baseline/results/` | Milestone 1 evidence | preserve |
| `citrus_project/milestones/01_original_lite_mono_baseline/visuals/` | Milestone 1 qualitative evidence | preserve |

## Reproducibility Mapping For Important Milestone 3 Runs

| professor-facing setting | saved source |
|---|---|
| Baseline: original Lite-Mono, no Citrus training | `weights/lite-mono/` |
| Diagnostic: pose warmup only, depth not updated | `runs/citrus_ss_seed0_warmup25_depth0_25steps/` |
| Diagnostic: depth allowed to update briefly | `runs/citrus_ss_seed0_warmup25_depth5_30steps/` |
| Diagnostic: depth allowed to update a little longer | `runs/citrus_ss_seed0_warmup25_depth15_40steps/` |
| Diagnostic: short run with depth updates | `runs/citrus_ss_seed0_warmup25_depth25_50steps/` |
| Conservative control: safer recipe after 250 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/models/step_250/` |
| Conservative control: same recipe after 1000 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/models/weights_0/` |
| Control: no color augmentation after 250 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_250steps/` |
| Control: no color augmentation after 500 updates | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_500steps/` |
| Normal batch-size-12 training, after 100/200/300 updates | `runs/citrus_ss_batch12_normal_lr_1epoch/models/step_100/`, `step_200/`, `step_300/` |
| Normal batch-size-12 training, after one epoch | `runs/citrus_ss_batch12_normal_lr_1epoch/models/weights_0/` |

## Current Cleanup Recommendation

Current state after 2026-05-11 cleanup:

1. Keep remaining Milestone 3 evidence runs and diagnostics.
2. Do not run more Milestone 3 training by default.
3. Use notes and preserved evidence runs as the standard-adaptation comparison source for Milestone 4.

Possible future cleanup pass, only after user approval:

1. Delete cache folders.
2. Delete empty diagnostic scratch folders if confirmed unused.
3. Keep remaining evidence runs until the paper comparison table and Milestone 4 baseline choice are stable.
