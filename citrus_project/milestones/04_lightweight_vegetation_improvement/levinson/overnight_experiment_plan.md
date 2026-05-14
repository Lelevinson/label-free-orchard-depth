# Levinson Milestone 4 Overnight Experiment Plan

Executed planning note for the controlled self-supervised Milestone 4 overnight gates.

Status: executed for experiments 02 and 03 after user approval.

This note is retained as planning provenance. The source-of-truth conclusions and copied evidence artifacts live in the matching snapshot READMEs and the shared Milestone 4 README.

## Guardrails

1. Keep Milestone 4 self-supervised for now.
2. Do not use `depth_gt`, `valid_mask`, LiDAR labels, dense labels, sparse labels, or ZED depth as a training loss.
3. Keep inference unchanged: one RGB image goes through the Lite-Mono encoder and depth decoder.
4. Keep every method isolated in its own run, result, and snapshot folder.
5. Do not combine methods unless explicitly approved.
6. Work only inside Levinson's Milestone 4 workstream.
7. Do not touch Marvel's folder.
8. If an experiment fails, record the failure and move only to the next pre-approved experiment if it is safe to do so.
9. User approved running `03_soft_confidence_multiplier` without another overnight approval if `02_rgb_edge_structure_preserving_loss` was bad or unclear.

## Current Status: 01 Photometric Confidence Masking

Snapshot:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/01_photometric_confidence_masking/
```

Run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/photometric_confidence_masking_b12_250steps_seed0/
```

Conclusion:

1. The method ran correctly and was stable.
2. It remained self-supervised and did not use depth labels as a training loss.
3. It slightly improved median-scaled `abs_rel` versus the same-budget no-mask 250-step control.
4. It worsened median-scaled `a1` versus the same-budget no-mask 250-step control.
5. Confidence diagnostic panels suggested that the effective-weight maps often trusted high-texture vegetation and ground, not reliably useful depth geometry.
6. Do not scale this exact configuration.

Key first-100 validation comparison at step 250:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Same-budget no-mask control | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Photometric-confidence masking | 0.8985 | 0.0000 | 0.5582 | 0.3018 |

## Recommended Queue

1. `02_rgb_edge_structure_preserving_loss`
   - Main next candidate.
   - Test alone first.
   - Goal: preserve tree, ground, canopy, and row structure without labels.
2. `03_soft_confidence_multiplier`
   - Backup diagnostic candidate.
   - Test if the structure-loss gate fails or is unclear.
   - Do not combine with structure loss.
3. `04_vegetation_aware_photometric_weighting_design`
   - Design-only for now.
   - Do not run overnight unless explicitly approved after reviewing a stronger rationale.

## Experiment 02: RGB-Edge Structure-Preserving Loss

Method name:

```text
Conservative RGB-edge / structure-preserving depth loss
```

Problem it targets:

Standard self-supervised adaptation can make Citrus depth predictions broad and smooth. It can reduce photo loss while weakening useful tree, ground, canopy, and row structure. This candidate targets the relative-depth structure problem more directly than photometric-confidence masking.

Why it fits current evidence:

1. Milestone 3 showed photo loss can improve while median-scaled depth structure worsens.
2. The 01 confidence maps trusted high-texture areas, so pixel selection alone did not solve the geometry problem.
3. A conservative structure loss asks the model not to erase strong scene boundaries, instead of asking which photometric pixels are trustworthy.

Exact files likely to change after approval:

```text
options.py
trainer.py
layers.py   optional, only if helper gradient code is cleaner there
```

Snapshot folder name:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/02_rgb_edge_structure_preserving_loss/
```

Run folder name:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/rgb_edge_structure_b12_250steps_seed0/
```

Command shape after implementation:

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name rgb_edge_structure_b12_250steps_seed0 `
  --log_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs `
  --mypretrain weights/lite-mono/lite-mono-pretrain.pth `
  --weights_init pretrained `
  --batch_size 12 `
  --num_epochs 1 `
  --max_train_steps 250 `
  --save_step_frequency 250 `
  --height 192 `
  --width 640 `
  --num_workers 0 `
  --log_frequency 50 `
  --seed 0 `
  --rgb_edge_structure_loss
```

Likely disabled-by-default options:

```text
--rgb_edge_structure_loss
--rgb_edge_structure_weight
--rgb_edge_structure_threshold
--rgb_edge_structure_blur_kernel
--rgb_edge_structure_target_grad
```

Expected diagnostics:

```text
rgb_edge_structure/loss/{scale}
rgb_edge_structure/edge_fraction/{scale}
rgb_edge_structure/disp_grad_on_edges/{scale}
rgb_edge_structure/hinge_active_fraction/{scale}
rgb_edge_structure/rgb_grad_mean/{scale}
rgb_edge_structure/weighted_loss_contribution/{scale}
```

250-step gate evaluation:

1. Evaluate `models/step_250/` on first-100 validation samples.
2. Compare against the existing same-budget no-mask control:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_250steps_seed0_control/
```

3. Use the same metric emphasis:
   - median-scaled `abs_rel`
   - median-scaled `a1`
   - raw metrics as secondary context
4. Generate visual panels using the existing comparison helper if possible.
5. Prefer also generating RGB-edge, disparity-gradient, and active-loss masks for the same selected samples.

Stop criteria:

1. Loss becomes NaN or unstable.
2. Structure loss dominates the total loss.
3. Median-scaled `a1` drops clearly below the no-mask control.
4. Visuals show texture chasing, noisy depth edges, or worse row/canopy structure.

Continue criteria:

1. Training is stable.
2. Structure diagnostics are nonzero but not dominant.
3. Median-scaled `a1` improves or holds while `abs_rel` does not clearly worsen.
4. Visuals show better tree/ground/canopy/row structure without obvious leaf-texture overfitting.

Uncertain criteria:

1. `a1` improves but `abs_rel` worsens.
2. Metrics are nearly tied but visuals look cleaner.
3. Diagnostics suggest the loss is too weak or too sparse.

Executed result:

```text
Status: stop.
First-100 validation at step 250:
raw abs_rel=0.8993, raw a1=0.0000,
median-scaled abs_rel=0.5822, median-scaled a1=0.3280.
```

This missed the same-budget no-mask control on both median-scaled `abs_rel` and `a1`, so the independent backup `03_soft_confidence_multiplier` was run.

## Experiment 03: Soft Confidence Multiplier

Method name:

```text
Soft photometric-confidence multiplier
```

Problem it targets:

The first confidence experiment may have failed partly because the normalized weighted average changed optimization dynamics too strongly. This backup variant tests whether confidence can be used as a weak damping factor without replacing the normal automasked photo-loss averaging behavior.

Why it fits current evidence:

1. 01 was stable, so the confidence signal is technically usable.
2. 01 was mixed/negative, and diagnostics showed the weighted loss was not simply smaller.
3. A weak multiplier isolates whether the normalized reweighting was the disruptive part.

Exact files likely to change after approval:

```text
options.py
trainer.py
```

Snapshot folder name:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/03_soft_confidence_multiplier/
```

Run folder name:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/soft_confidence_multiplier_b12_250steps_seed0/
```

Command shape after implementation:

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name soft_confidence_multiplier_b12_250steps_seed0 `
  --log_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs `
  --mypretrain weights/lite-mono/lite-mono-pretrain.pth `
  --weights_init pretrained `
  --batch_size 12 `
  --num_epochs 1 `
  --max_train_steps 250 `
  --save_step_frequency 250 `
  --height 192 `
  --width 640 `
  --num_workers 0 `
  --log_frequency 50 `
  --seed 0 `
  --soft_confidence_multiplier
```

Likely disabled-by-default options:

```text
--soft_confidence_multiplier
--soft_confidence_threshold
--soft_confidence_ramp
--soft_confidence_strength
--soft_confidence_min_multiplier
```

Expected diagnostics:

```text
soft_confidence/multiplier_mean/{scale}
soft_confidence/weak_pixel_fraction/{scale}
soft_confidence/margin_mean/{scale}
soft_confidence/photo_loss_before/{scale}
soft_confidence/photo_loss_after/{scale}
soft_confidence/effective_loss_delta/{scale}
```

250-step gate evaluation:

1. Evaluate `models/step_250/` on first-100 validation samples.
2. Compare against both:
   - same-budget no-mask control
   - 01 photometric-confidence masking
3. Generate confidence multiplier maps for selected visual samples.

Stop criteria:

1. It repeats the 01 pattern: slight `abs_rel` improvement but clear `a1` drop.
2. Multiplier maps still mostly trust high-texture vegetation/ground.
3. Loss scale changes substantially despite the intended weak multiplier design.

Continue criteria:

1. It preserves or improves `a1` versus the no-mask control.
2. It does not worsen `abs_rel` clearly.
3. Visuals are not flatter or more texture-biased than the no-mask control.

Uncertain criteria:

1. Metrics are close to the no-mask control.
2. Diagnostics show the multiplier is too weak to matter.

Executed result:

```text
Status: stop.
First-100 validation at step 250:
raw abs_rel=0.8978, raw a1=0.0000,
median-scaled abs_rel=0.5676, median-scaled a1=0.3068.
```

This remained worse than the same-budget no-mask control on median-scaled `a1` and did not rescue the confidence direction.

## Experiment 04: Vegetation-Aware Photometric Weighting

Method name:

```text
Vegetation-aware photometric weighting
```

Problem it targets:

Vegetation-heavy image regions may be photometrically misleading because repeated leaves, shadows, and similar green textures can make wrong depth look reconstructable.

Why it is not recommended for the overnight queue yet:

1. It is more heuristic.
2. It risks becoming color/dataset-specific.
3. It may suppress exactly the regions where Citrus depth structure matters most.
4. It needs design review before implementation.

Exact files likely to change if later approved:

```text
options.py
trainer.py
possibly a helper visualization script
```

Snapshot folder name if later approved:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/04_vegetation_aware_photometric_weighting/
```

Run folder name if later approved:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/vegetation_aware_photometric_b12_250steps_seed0/
```

Command shape:

```text
Design-only for now. Do not run overnight without explicit approval.
```

Expected diagnostics if later implemented:

```text
vegetation_weight/mean/{scale}
vegetation_weight/suppressed_fraction/{scale}
vegetation_weight/photo_loss_before/{scale}
vegetation_weight/photo_loss_after/{scale}
```

Stop criteria:

1. It suppresses too much canopy/tree signal.
2. It worsens `a1`.
3. Visuals become flatter around trees or row boundaries.

Continue criteria:

1. It improves structure without removing too much vegetation signal.
2. It has a clear Citrus-specific explanation and avoids label use.

## Morning Summary Checklist

For each approved run completed overnight, record:

1. Run name and command.
2. Snapshot folder name.
3. Checkpoint path used for evaluation.
4. First-100 validation result path.
5. Visual panel path.
6. Whether CSV/JSON result files were saved.
7. Key metrics:
   - raw `abs_rel`
   - raw `a1`
   - median-scaled `abs_rel`
   - median-scaled `a1`
8. Diagnostic scalar summary.
9. Visual read:
   - tree/canopy structure
   - ground/row structure
   - texture chasing
   - over-smoothing
10. Conclusion:
    - continue
    - stop
    - uncertain
11. If code changed, copy tested changed files into the matching snapshot `code/` folder.
12. Update the snapshot README.
13. Update `AGENTS.md` and the shared Milestone 4 README only if project status, decisions, commands, or paths changed.

## Recommended Execution Order

1. Implement and test `02_rgb_edge_structure_preserving_loss`. Done.
2. Run its smoke test. Done.
3. Run its 250-step gate. Done.
4. Evaluate first-100 validation. Done.
5. Generate visual panels and readable diagnostics. Done.
6. Decide continue / stop / uncertain. Stop.
7. Because `02` failed, implement and test `03_soft_confidence_multiplier`. Done.
8. Run its smoke test, 250-step gate, evaluation, visual panels, and diagnostics. Done.
9. Keep `04_vegetation_aware_photometric_weighting` design-only.

## Approval Required

Approval is required before:

1. Editing `trainer.py`, `options.py`, `layers.py`, or any model code.
2. Running additional training beyond the executed approved 02/03 250-step gates.
3. Running a new evaluation that writes result artifacts.
4. Promoting any temporary plan into the source-of-truth milestone README or `AGENTS.md`.
