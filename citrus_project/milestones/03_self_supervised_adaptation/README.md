# Milestone 3: Self-Supervised Adaptation

Use this folder for milestone-specific helpers, notes, and experiment files related to standard self-supervised Citrus fine-tuning/adaptation.

## Closeout Verdict

Milestone 3 is closed as weak/negative adapted-baseline evidence.

The standard self-supervised Citrus adaptation path works technically:

1. Citrus temporal batches load through the root trainer.
2. CUDA training runs start and stop under controlled limits.
3. Checkpoints, step checkpoints, and evaluations save correctly.
4. Diagnostic helpers can inspect photo loss, masks, pose behavior, scale drift, and LiDAR-valid metrics.

But the tested recipe family is not useful as an improvement:

1. Adapted checkpoints did not beat the untouched Milestone 1 original Lite-Mono baseline on first-100 validation relative-depth metrics.
2. Photo/reprojection loss can decrease while LiDAR-valid depth quality worsens.
3. Depth updates, not pose-only learning, are where the damaging behavior appears.
4. Adapted predictions become smoother and less structurally specific than the original baseline.
5. Longer or more conservative standard recipes did not recover.

Current project decision:

```text
Do not launch another longer/full Milestone 3 run without a new technical reason and explicit user confirmation.
Move next to Milestone 4 method planning.
```

## Where The Evidence Lives

| file | role |
|---|---|
| `README.md` | compact milestone handoff and result index |
| `artifact_inventory.md` | run-folder classification, cleanup candidates, and reproducibility mapping |
| `professor_loading_and_train_eval_check.md` | advisor-facing checks for loading, training-image evaluation, sparse LiDAR, and batch size |
| `beginner_progress_summary.md` | plain-language explanation for student/professor discussion |
| `citrus_project/research/baseline_notes.md` | detailed model evidence and run-by-run research record |
| `citrus_project/research/advisor_notes.md` | advisor questions and follow-up interpretation |
| `citrus_project/research/paper_shortlist.md` | paper-useful candidate result summary |

## Important Professor-Facing Result Names

Use descriptive experiment names in presentation tables.
Keep internal run folder names in technical mapping sections only.

| professor-facing name | purpose | internal artifact |
|---|---|---|
| Baseline: original Lite-Mono, no Citrus training | reference model to beat | `weights/lite-mono/` |
| Diagnostic: pose warmup only, depth not updated | test pose-only learning without changing deployment depth model | `runs/citrus_ss_seed0_warmup25_depth0_25steps/` |
| Diagnostic: depth allowed to update briefly | test early damage after 5 depth-update steps | `runs/citrus_ss_seed0_warmup25_depth5_30steps/` |
| Diagnostic: short run with depth updates | test 25 depth-update steps after warmup | `runs/citrus_ss_seed0_warmup25_depth25_50steps/` |
| Conservative control: safer recipe after 1000 updates | main monitored weak adapted baseline | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/` |
| Control: no color augmentation after 250 updates | test whether color jitter caused the drift | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_250steps/` |
| Control: no color augmentation after 500 updates | test whether no-augmentation remains stable longer | `runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_500steps/` |
| Normal batch-size-12 training, one epoch | advisor-requested larger-batch standard control | `runs/citrus_ss_batch12_normal_lr_1epoch/` |

Full artifact classification is in `artifact_inventory.md`.

## Main Quantitative Evidence

First-100 validation reference:

| setting | raw abs_rel | median-scaled abs_rel | median-scaled a1 | interpretation |
|---|---:|---:|---:|---|
| Baseline: original Lite-Mono, no Citrus training | 0.7289 | 0.3680 | 0.4807 | reference to beat |
| Diagnostic: pose warmup only, depth not updated | 0.7274 | 0.3758 | 0.4797 | close to baseline, but depth model did not adapt |
| Diagnostic: depth allowed to update briefly | 0.6781 | 0.3902 | 0.4484 | raw scale improves, relative structure starts dropping |
| Diagnostic: short run with depth updates | 0.7901 | 0.6354 | 0.2280 | depth structure badly damaged |
| Conservative control: safer recipe after 250 updates | 0.7331 | 0.4542 | 0.4290 | safer recipe still below original |
| Conservative control: safer recipe after 1000 updates | 0.7448 | 0.6615 | 0.1827 | did not recover with more steps |
| Control: no color augmentation after 250 updates | 0.7192 | 0.4108 | 0.4568 | less bad, still below original |
| Control: no color augmentation after 500 updates | 0.7235 | 0.5300 | 0.3513 | worsened again |
| Normal batch-size-12 training, after one epoch | 0.7190 | 3.0501 | 0.2473 | photo loss decreased, relative depth failed |

Result interpretation:

1. Raw-scale improvements alone are not enough.
2. Median-scaled metrics show whether the near/far structure survives after one global scale correction.
3. The tested self-supervised recipes often improve the photo-matching training game while damaging the relative-depth structure needed for Citrus scenes.

## Qualitative Evidence

Helper:

```text
compare_original_vs_adapted_visuals.py
```

Generated comparison panels:

```text
runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/visual_compare_original_vs_adapted_val100_weights_0/
```

Visual verdict:

1. The adapted checkpoint is smoother and less structurally specific.
2. It loses some tree/canopy/ground separation that the original baseline weakly preserved after median scaling.
3. The failure is relative-depth structure damage, not only global scale mismatch.

## Advisor Checks

Detailed note:

```text
professor_loading_and_train_eval_check.md
```

Checks completed:

1. Parameter loading:
   - original `weights/lite-mono` encoder/depth tensors load with no missing model tensors
   - extra checkpoint tensors are profiling metadata, not required model weights
   - fully depth-frozen checkpoint is tensor-identical to original encoder/depth tensors on common model tensors
2. First-100 training-image evaluation:
   - adapted checkpoints do not become high-accuracy on training images
   - train split mirrors the validation pattern
3. Sparse LiDAR-only/KITTI-like validation:
   - used raw projected sparse LiDAR pixels only, with no `local_idw`
   - original still beat adapted checkpoints on median-scaled relative-depth quality
4. Batch-size feasibility and control:
   - true batch sizes 8 and 12 pass one-step CUDA smokes on the laptop RTX 4060 GPU
   - normal batch-size-12 one-epoch training still degraded first-100 train and validation relative-depth metrics

Conclusion:

```text
The current evidence does not support wrong depth-weight loading, train/validation generalization alone, local_idw densification alone, or small batch size alone as the Milestone 3 failure cause.
```

## Safety And Trainer Changes From This Milestone

Root trainer/config additions made during Milestone 3:

1. `--max_train_steps`: default-off safety brake for short runs.
2. `--seed`: default-off reproducibility option for controlled comparisons.
3. Python 3-compatible `trainer.val()` iterator handling.
4. Modern torchvision ResNet pretrained-weight loading in `networks/resnet_encoder.py`.
5. `--freeze_depth_steps`: default-off pose warmup/depth optimizer freeze.
6. `--freeze_depth_encoder`: default-off depth encoder and BatchNorm freeze.
7. `--save_step_frequency`: default-off step checkpoint interval for monitored runs.

These options remain available for future controlled experiments, but they are not themselves the Milestone 4 improvement.

## Helper Scripts

| script | purpose |
|---|---|
| `diagnose_self_supervised_batch.py` | fixed-batch diagnostics for photo loss, loss decomposition, masks, pose, scale, and depth metrics |
| `compare_original_vs_adapted_visuals.py` | side-by-side original/adapted visual panels |
| `run_controlled_decoderonly_lowdepthlr_1epoch.ps1` | launches the conservative 1000-step monitored probe |
| `evaluate_controlled_decoderonly_lowdepthlr.ps1` | evaluates conservative probe checkpoints |

## Output Hygiene

1. Training runs/checkpoints should go under `citrus_project/milestones/03_self_supervised_adaptation/runs/`.
2. The original `weights/lite-mono/` folder is input-only and should not be overwritten.
3. Smoke-test folders may be disposable, but only after the user approves a specific cleanup list.
4. Evidence-bearing runs should be preserved until the Milestone 4 comparison baseline choice is stable.
5. Run-folder classification lives in `artifact_inventory.md`.

## Commands To Reuse Carefully

Conservative 1000-step monitored probe:

```powershell
citrus_project/milestones/03_self_supervised_adaptation/run_controlled_decoderonly_lowdepthlr_1epoch.ps1
```

Evaluate the conservative probe checkpoints:

```powershell
citrus_project/milestones/03_self_supervised_adaptation/evaluate_controlled_decoderonly_lowdepthlr.ps1
```

Run fixed-batch diagnostics:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/diagnose_self_supervised_batch.py --help
```

Do not run these as new experiments by default.
Use them only when there is a clear technical question and the user confirms the intended run.

## Handoff To Milestone 4

Milestone 4 should not simply rerun longer versions of Milestone 3.

Recommended target:

```text
Preserve or improve Citrus relative-depth structure while adapting to vegetation scenes.
```

Fair comparison ladder:

1. Original Lite-Mono, no Citrus training.
2. Documented weak/negative standard Citrus adaptation from Milestone 3.
3. Milestone 4 proposed lightweight vegetation-focused method.

First Milestone 4 gates:

1. Start with first-100 validation checks before full runs.
2. Track both raw and median-scaled metrics.
3. Inspect visual structure, not only loss curves.
4. Keep runtime/inference path RGB-only and lightweight.
5. Avoid calling a method an improvement unless it beats both the original baseline and the weak Milestone 3 adapted baseline under the same evaluation protocol.
