# Paper Shortlist

This file tracks research artifacts that may later become paper tables, figures, or method details.

## Strong Candidates

### Original Lite-Mono Full Citrus Baseline

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/test_lite-mono_full_summary.json`

Why it matters:

- Provides the first full validation/test quantitative baseline for original pretrained Lite-Mono on Citrus.
- Supports the domain-gap argument: raw absolute scale is poor and median-scaled scores still leave substantial room for improvement.
- Gives lightweight-model metadata alongside accuracy: 3.075M depth-inference parameters and about 11.94 MiB of checkpoint weights.

Paper section fit:

- Experimental setup
- Baseline results
- Motivation for Citrus adaptation / vegetation-focused improvement
- Efficiency comparison

Current status:

- Full validation and test runs completed on 2026-04-28.
- First validation good/typical/bad visual panels were generated on 2026-04-28 using `median_scaled_a1`.
- Test good/typical/bad visual panels were generated on 2026-04-29 using `median_scaled_a1`.
- First written failure-case interpretation exists in `citrus_project/milestones/01_original_lite_mono_baseline/visual_interpretation.md`.
- Needs a tighter final figure/table design before it is a complete paper package.

### Dataset/Label Route Selection

Evidence notes:

- `citrus_project/research/dataset_notes.md`
- raw metrics: `citrus_project/dataset_workspace/projection_alignment_audit/time_spread_metrics_200/audit_metrics.csv`

Why it matters:

- Shows the LiDAR-to-camera transform route was selected using a time-spread quantitative check.
- Supports the claim that label generation was validated rather than assumed.
- Provides a table-ready comparison between `production_current` and `exact_lidar_parent_child_inverted`.

Paper section fit:

- Dataset construction
- Ground-truth / pseudo-label generation
- Calibration validation

Current status:

- Locked as the final/default dense-label route: `exact_lidar_parent_child_inverted`.
- Full prepared dataset build is now complete with 5282 samples and time-block splits of train=4311, val=564, test=407.

### Final Prepared Dataset Version

Evidence notes:

- `citrus_project/research/dataset_notes.md`
- `citrus_project/dataset_workspace/prepared_training_dataset/metrics/summary.json`

Why it matters:

- Gives the paper a concrete dataset version and split counts instead of only planned counts.
- Supports the reproducibility story around label generation, split policy, and evaluation setup.

Paper section fit:

- Dataset construction
- Experimental setup
- Reproducibility details

Current status:

- Built successfully on 2026-04-23.
- Ready to support Milestone 1 baseline evaluation.

### Conservative Dense Label Generation

Evidence notes:

- `citrus_project/dataset_workspace/densify_lidar.py`
- `citrus_project/research/dataset_notes.md`

Why it matters:

- `local_idw` fills only near LiDAR support and rejects fills when neighboring depths disagree too much.
- This supports a paper-facing argument that sparse vegetation labels should prefer validity masks over visually full but hallucinated labels.

Paper section fit:

- Dataset preprocessing
- Label reliability
- Training/evaluation mask construction

Current status:

- Implemented and tested.
- Needs final parameter lock before full dataset build.

## Early Candidates

### Milestone 3 Self-Supervised Adaptation Instability

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- `citrus_project/milestones/03_self_supervised_adaptation/README.md`
- ignored run outputs under `citrus_project/milestones/03_self_supervised_adaptation/runs/`

Why it matters:

- Shows that a plain self-supervised Citrus adaptation baseline is not automatically better than the untouched original model.
- The conservative 1000-step probe still worsened first-100 validation median-scaled depth quality: final `abs_rel=0.6615`, `a1=0.1827`, versus untouched baseline `abs_rel=0.3680`, `a1=0.4807`.
- Side-by-side visual panels show the adapted checkpoint becoming smoother and less structurally specific than the original baseline on selected validation examples.
- A no-color-augmentation 250-step control improved over the color-augmented 250-step control, but still did not beat the untouched baseline on median-scaled relative-depth metrics.
- Extending the no-color-augmentation control to 500 steps worsened relative-depth metrics again: `abs_rel=0.5300`, `a1=0.3513`.
- This is useful motivation for a Milestone 4 structure-preserving or vegetation-aware improvement, as long as it is presented carefully as negative/diagnostic evidence.

Paper section fit:

- Baseline adaptation results
- Failure analysis
- Motivation for proposed method

Current status:

- Documented as weak/negative adapted-baseline evidence.
- Use carefully: it supports the claim that standard self-supervised Citrus adaptation is not enough under the tested recipe family, rather than claiming all possible adaptation can never work.
- Next paper-facing need is to compare the future Milestone 4 improvement against original Lite-Mono and this documented Milestone 3 failure pattern.
- Visual comparison panels were generated on 2026-05-07 under the Milestone 3 ignored run folder.
- Advisor-requested checks on 2026-05-07 strengthen this interpretation: original encoder/depth loading has no missing model tensors, the fully depth-frozen checkpoint is tensor-identical to the original encoder/depth weights, and first-100 train-image evaluation is not high-accuracy for the adapted checkpoints.
- A sparse LiDAR-only first-100 validation sanity check on 2026-05-08 also keeps the same direction: original median-scaled `abs_rel=0.6072`, `a1=0.3724`; conservative adapted final1000 `abs_rel=0.8445`, `a1=0.1441`; no-augmentation 250-step `abs_rel=0.6712`, `a1=0.3234`. This reduces concern that the negative result comes only from semi-dense `local_idw` evaluation labels.
- A normal one-epoch true batch-size-12 control on 2026-05-08 also failed to recover: original first-100 validation median-scaled `abs_rel=0.3680`, `a1=0.4807`; batch12 step100 `abs_rel=0.6906`, `a1=0.1465`; final one-epoch `abs_rel=3.0501`, `a1=0.2473`, despite photo loss decreasing during training.

### Plain Lite-Mono Citrus Training From ImageNet Pretrain

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/README.md`
- results under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/`

Why it matters:

- Gives a fairer plain Lite-Mono Citrus-training baseline for later comparison with a Milestone 4 method.
- It starts from the Lite-Mono ImageNet encoder pretrain, not the KITTI depth-trained Lite-Mono checkpoint.
- Final epoch shows a mixed but useful signal: median-scaled `a1` improves, while raw-scale metrics and median-scaled `abs_rel` worsen.

Paper section fit:

- Experimental baselines
- Domain adaptation comparison
- Motivation for a structure-preserving or vegetation-aware improvement

Current status:

- Training completed on 2026-05-10.
- Final checkpoint `weights_29` validation: original median-scaled `abs_rel=0.4176`, `a1=0.4629`; trained baseline median-scaled `abs_rel=0.5100`, `a1=0.6107`.
- Final checkpoint `weights_29` test: original median-scaled `abs_rel=0.3836`, `a1=0.4989`; trained baseline median-scaled `abs_rel=0.4889`, `a1=0.6582`.
- Important caveat: the final checkpoint improves median-scaled `a1` but worsens raw-scale metrics and median-scaled `abs_rel`. Use this as baseline/motivation evidence, not a final proposed-method win.
- A later checkpoint sweep was discarded after visual review and is not part of committed paper evidence.

### Teacher-Anchored Label-Free Citrus Adaptation

Evidence notes:

- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/README.md`
- `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/README.md`
- checkpoint-selection note: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md`
- sweep outputs: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/`
- selected `weights_19` visual/inference package: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/`

Why it matters:

- This is the strongest Levinson label-free method family so far.
- It keeps Citrus training label-free: no `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels are used as training losses or masks.
- It uses a frozen RGB-only Lite-Mono teacher as a training-only relative-structure anchor while keeping inference as one RGB image into the Lite-Mono student.
- Checkpoint selection was validation-first: all Snapshot 05/06 checkpoints were swept on validation, then only selected checkpoints were tested.

Paper section fit:

- Proposed label-free/self-supervised adaptation method
- Ablation and checkpoint-selection protocol
- Main comparison against original Lite-Mono and B0 plain Citrus training

Current status:

- Snapshot 05 final `weights_29` test: median-scaled `abs_rel=0.4132`, `a1=0.6463`.
- Snapshot 06 final `weights_29` test: median-scaled `abs_rel=0.4168`, `a1=0.6418`.
- Validation-selected Snapshot 05 `weights_19` test: median-scaled `abs_rel=0.3947`, `a1=0.6476`.
- Validation-selected Snapshot 06 `weights_25` test: median-scaled `abs_rel=0.4076`, `a1=0.6359`.
- Best current label-free teacher-anchor checkpoint: Snapshot 05 `weights_19`.
- It clearly improves B0 test median-scaled `abs_rel` (`0.4889` to `0.3947`) while keeping most of B0 test median-scaled `a1` (`0.6582` to `0.6476`).
- It gets close to original Lite-Mono test median-scaled `abs_rel=0.3836`, but does not beat it, so claims must say "near-closes the gap" rather than "cleanly outperforms original."
- Visual packaging on 2026-05-19 supports the same cautious story: comparison panels and plain inference maps are mixed but useful, with broad structure gains in good/typical cases and remaining smooth/over-corrected vegetation or occlusion failures. Use `weights_19` as the main Snapshot 05 paper-table result; keep `weights_29` as the final-epoch ablation/evidence point.

### Original Lite-Mono Qualitative Citrus Prediction

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- generated local files under `citrus_project/research/generated/lite_mono_single_image_demo/`

Why it matters:

- Demonstrates original Lite-Mono can run on Citrus RGB frames.
- Useful as an early qualitative baseline/motivation example.

Paper section fit:

- Motivation
- Qualitative baseline comparison
- Failure-case analysis

Current status:

- Single-image sanity demo only.
- Quantitative claims should use the full baseline outputs above, not this demo.
- Still useful as a possible qualitative example source if regenerated consistently with labels and masks.

## Not Paper Evidence Yet

### Completed Presentation Slides

Source:

- removed after presentation cleanup

Why not:

- Useful for explaining progress at the time, but not a primary research artifact.
- Any table/figure from it should be regenerated from raw metrics or tracked research summaries before paper use.

