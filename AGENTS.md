# AGENTS.md

## Purpose

This file is the shared source-of-truth context for the Lite-Mono + Citrus Farm research project.
The project goal is a publishable research paper on improving lightweight monocular depth estimation for vegetation-dense agricultural environments, with Citrus Farm as the current main benchmark/domain and a lightweight RGB-only pest-killing robot perception stack as motivation.

All new chats should read this file first.

## Mandatory Context Workflow

1. Read this file before starting any task.
2. Treat this file as source of truth for current project status, decisions, important paths, and next steps.
3. If code, config, data-pipeline behavior, experiment defaults, milestone status, important paths, or research decisions change, update this file in the same turn.
4. Do not mark a task complete until this file is updated when required.
5. In every final response, include:
   - `Context file updated: Yes`
   - short summary of what was updated in this file
6. If no update is required, include:
   - `Context file updated: No`
   - reason no update was required

## Living Notes Rule

1. Treat project notes as living documents, not append-only logs.
2. Keep this file compact and current: source-of-truth status, active decisions, important paths/commands, and next actions.
3. Keep run-by-run evidence in the matching milestone README or research note, and point to it from here.
4. When a newer result supersedes an older temporary result, update or mark the older wording instead of leaving conflicting notes.
5. Prefer clarity for future chats over preserving every intermediate line in this file.

## Document Roles

1. `AGENTS.md` is the current source of truth for project goal, milestone state, current decisions, canonical paths, and next actions.
2. `citrus_project/research/student_qna.md` is the beginner-friendly companion note for recurring explanations and stable definitions.
3. `citrus_project/research/dataset_notes.md` stores dataset-building, label-route, and quality evidence.
4. `citrus_project/research/baseline_notes.md` stores model-behavior, baseline, adaptation, and comparison evidence.
5. `citrus_project/research/paper_shortlist.md` tracks results that may later appear in the paper.
6. `citrus_project/research/advisor_notes.md` tracks professor/advisor questions, recommendations, and follow-up directions.
7. `citrus_project/milestones/*/README.md` files are teammate-facing handoffs for each milestone.
8. `citrus_project/milestones/03_self_supervised_adaptation/artifact_inventory.md` classifies Milestone 3 run artifacts, helper scripts, generated outputs, and cleanup candidates.
9. Folder-level `README.md` files are doorway maps. Use them to decide which deeper notes are relevant instead of reading every `.md` file in a folder.
10. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/README.md` is the compact B0 plain Citrus baseline snapshot for Levinson's Milestone 4 workstream. It contains inference weights plus copied final result files, visual panels, and `config/opt.json`.
11. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md` is the explicit policy note for the live repo-root training code versus frozen snapshot `code/` copies. Read it before any new Milestone 4 Levinson root-code edit.
12. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md` is the human/AI navigation map for Levinson's Milestone 4 docs after Snapshot 07.
13. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md` is the pre-presentation audit of Levinson snapshot folder tidiness, contradictions, active root-code state, and presentation readiness.
14. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md` is the documentation optimization audit that inventories current versus historical Levinson docs before presentation preparation.

Update policy:

1. Update `AGENTS.md` when project status, defaults, commands, paths, or research decisions change.
2. Update `student_qna.md` when a recurring beginner confusion is explained in a stable way.
3. Update `dataset_notes.md` for dataset quality or label-generation evidence.
4. Update `baseline_notes.md` for model behavior or comparison evidence.
5. Update `paper_shortlist.md` for results likely to support the paper.
6. Update `advisor_notes.md` for advisor questions or recommendations.
7. Update the relevant milestone README when milestone status, handoff guidance, or evidence ownership changes.

## User Collaboration Preference

When discussing codebase details, verify against actual files and recent project context before answering.

1. Do not assume file importance, workflow relevance, or implementation behavior without checking.
2. Look for edge cases and mismatches before speaking confidently about scripts, tests, folders, or pipeline behavior.
3. If something is a guess, label it clearly.
4. For ideas or brainstorming, propose possibilities as possibilities.
5. Do not treat legacy or sidecar files as important to the active workflow unless relevance is confirmed.
6. When explaining AI/PyTorch/image-processing concepts, use concrete mental hooks, small examples, and project-specific artifacts.
7. For deep model-algorithm work, slow down for mutual understanding: map formulas to tensors/code, ask concept checks, and correct misunderstandings gently but explicitly.

## Workspace Layout

Original/upstream-style Lite-Mono code remains at the repo root.
Project-owned Citrus work lives under `citrus_project/`.

Important folders:

1. `citrus_project/dataset_workspace/` - active Citrus dataset pipeline workspace.
2. `citrus_project/research/` - research notes, paper shortlist material, advisor notes, and beginner explanations.
3. `citrus_project/milestones/` - milestone-specific code, notes, helpers, and outputs.
4. `citrus_project/TEAM_WORKFLOW.md` - collaboration/onboarding guide for teammates and AI assistants.
5. `citrus_project/TASK_BOARD.md` - current work board.
6. `citrus_project/milestones/00_dataset_audit/sample_pack/` - low-storage sample pack area for collaborators.

Team-collaboration rule:

1. Teammates and their AI assistants should read `AGENTS.md`, then `citrus_project/TEAM_WORKFLOW.md`, then `citrus_project/TASK_BOARD.md`.
2. Keep fragile pipeline/model-code work coordinated through the main integrator.
3. Friend A is a good fit for literature scouting and related-work intake.
4. Friend B is a good fit for scene taxonomy, example selection, and qualitative-support notes.

## Project Goal

Publish an improved Lite-Mono-style monocular depth estimation method for vegetation-dense agricultural environments.

Research objective:

1. Use original Lite-Mono as the lightweight monocular depth baseline.
2. Measure the domain gap between urban/KITTI-style behavior and vegetation-dense agricultural scenes.
3. Build a reliable Citrus Farm RGB + depth-label evaluation/training pipeline.
4. Improve Lite-Mono or its training objective for dense vegetation while keeping runtime inference monocular RGB-only and lightweight.
5. Compare original Lite-Mono, standard Citrus-adapted Lite-Mono, and the proposed improved variant under the same Citrus data budget and splits.
6. Frame Citrus Farm as the current validation domain, not the only intended deployment domain.

Dataset-preparation objective:

1. Download aligned Citrus Farm ROS bag files.
2. Extract ZED RGB/depth and Velodyne LiDAR point cloud data.
3. Match RGB frames with LiDAR by timestamp.
4. Project and densify LiDAR depth for evaluation labels and optional supervised/hybrid training.
5. Export reproducible train/val/test manifests, metrics, masks, and diagnostics.

## Citrus Farm Dataset Understanding

1. CitrusFarm is a multimodal agricultural robotics dataset for localization, mapping, and crop monitoring in citrus tree farms.
2. It includes seven sequences from three citrus fields, multiple tree species/growth stages, planting patterns, and daylight conditions.
3. It provides stereo RGB, ZED depth, monochrome, near-infrared, thermal, wheel odometry, LiDAR, IMU, and GPS-RTK.
4. Raw data is released as modality-split ROS bag blocks. Bags from the same folder can be played together by timestamp.
5. Official tooling includes `download_citrusfarm.py` and `bag2files.py`; these are not a monocular-depth training pipeline.
6. Our LiDAR-to-ZED projection and densification pipeline is a project-derived label pipeline, not an official Citrus Farm ground-truth product.

## Canonical Dataset Pipeline

Script order:

1. `citrus_project/dataset_workspace/download_citrusfarm_seq_01_lidar.py`
2. `citrus_project/dataset_workspace/download_citrusfarm_seq_01_rgb_depth.py`
3. `citrus_project/dataset_workspace/extract_left_rgbd_from_raw.py`
4. `citrus_project/dataset_workspace/extract_lidar_from_raw.py`
5. `citrus_project/dataset_workspace/audit_projection_alignment.py`
6. `citrus_project/dataset_workspace/densify_lidar.py`
7. `citrus_project/dataset_workspace/build_training_dataset.py`

Key decisions:

1. RGB-LiDAR pairing uses timestamp matching with same-session preference and optional cross-session fallback under the same max delta.
2. Split strategy defaults to time blocks to reduce adjacent-frame leakage.
3. Final/default LiDAR-to-ZED transform is `exact_lidar_parent_child_inverted`.
4. `production_current` remains runnable as an alternate comparison route.
5. Final/default dense-label interpolation is `local_idw`, a conservative local inverse-distance weighted fill.
6. Valid masks are saved and must be used for Citrus training/evaluation metrics.

## Current Data Snapshot

Local dataset workspace:

1. `citrus_project/dataset_workspace/Calibration/`
2. `citrus_project/dataset_workspace/extracted_rgbd/`
3. `citrus_project/dataset_workspace/extracted_lidar/`
4. `citrus_project/dataset_workspace/prepared_training_dataset/`
5. `citrus_project/dataset_workspace/projection_alignment_audit/` ignored diagnostics

Final prepared dataset:

1. Built on 2026-04-23 with `exact_lidar_parent_child_inverted` and `local_idw`.
2. Output root: `citrus_project/dataset_workspace/prepared_training_dataset/`.
3. Total matched samples: 5282.
4. Dense LiDAR depth labels: 5282 NPZ files.
5. Valid masks: 5282 NPZ files.
6. Time-block split counts:
   - train: 4311
   - val: 564
   - test: 407
7. Safe same-split temporal triplets under the 200 ms neighbor rule:
   - train: 4275
   - val: 560
   - test: 399

Important prepared artifacts:

1. `prepared_training_dataset/splits/train_pairs.txt`
2. `prepared_training_dataset/splits/val_pairs.txt`
3. `prepared_training_dataset/splits/test_pairs.txt`
4. `prepared_training_dataset/metrics/all_samples.csv`
5. `prepared_training_dataset/dense_lidar_npz/`
6. `prepared_training_dataset/dense_lidar_valid_mask_npz/`
7. `prepared_training_dataset/manifest.json`

## Dataset Evidence Summary

Final route decision:

1. Four transform candidates were audited.
2. `current_chain_no_invert` and `exact_lidar_parent_child_direct` were visually rejected.
3. `production_current` and `exact_lidar_parent_child_inverted` were both visually plausible.
4. A 200-sample time-spread local-IDW route probe showed:
   - `production_current` had higher dense fill on 198/200 samples.
   - `exact_lidar_parent_child_inverted` had lower ZED absolute error on 200/200 samples.
   - `exact_lidar_parent_child_inverted` had lower ZED relative error on 200/200 samples.
5. Final choice: `exact_lidar_parent_child_inverted`, favoring cleaner overlap agreement over higher fill ratio.

Detailed evidence:

1. `citrus_project/research/dataset_notes.md`
2. `citrus_project/research/paper_shortlist.md`
3. ignored visual/metrics diagnostics under `citrus_project/dataset_workspace/projection_alignment_audit/`

## Milestone Status

Milestone 0 - Dataset audit and build:

1. Complete through full prepared dataset build.
2. Final label route and split policy are materialized under `prepared_training_dataset/`.
3. Detailed handoff: `citrus_project/milestones/00_dataset_audit/README.md`.

Milestone 1 - Original Lite-Mono baseline:

1. Core evidence complete.
2. Full original Lite-Mono validation/test runs are saved under `citrus_project/milestones/01_original_lite_mono_baseline/results/`.
3. Visual good/typical/bad panels are saved under `citrus_project/milestones/01_original_lite_mono_baseline/visuals/`.
4. Validation result:
   - samples: 564/564
   - mean valid-label coverage: 37.2272%
   - raw `abs_rel=0.7128`, `a1=0.0195`
   - median-scaled `abs_rel=0.4176`, `a1=0.4629`
   - model-forward FPS: 28.478
5. Test result:
   - samples: 407/407
   - mean valid-label coverage: 36.7190%
   - raw `abs_rel=0.7273`, `a1=0.0149`
   - median-scaled `abs_rel=0.3836`, `a1=0.4989`
   - model-forward FPS: 29.529
6. Depth-inference model metadata:
   - total parameters: 3,074,747
   - encoder parameters: 2,848,120
   - depth-decoder parameters: 226,627
   - checkpoint size: about 11.94 MiB
   - pose network is training-only and not counted for RGB-only inference.
7. Detailed evidence: `citrus_project/research/baseline_notes.md`.

Milestone 2 - Citrus trainer integration:

1. Core integration complete.
2. Added `CitrusPreparedDataset`, temporal triplet loading, same-split neighbor diagnostics, trainer-compatible metadata-free batches, Citrus-safe depth metric behavior, root `--dataset citrus` wiring, one-step optimizer smoke, CUDA one-step smoke, and train-only Citrus color augmentation.
3. Root trainer safety/config additions include:
   - `--dataset citrus`
   - `--split citrus_prepared`
   - `--citrus_prepared_name`
   - `--citrus_max_neighbor_delta_ms`
   - `--depth_metric_crop auto|kitti_eigen|none`
   - `--citrus_color_aug_probability`
4. Citrus defaults resolve to `split=citrus_prepared`, `data_path=citrus_project/dataset_workspace`, and `depth_metric_crop=none`.
5. Detailed handoff: `citrus_project/milestones/02_citrus_integration/README.md`.

Milestone 3 - Standard self-supervised Citrus adaptation:

1. Closed as documented weak/negative adapted-baseline evidence.
2. Training, checkpoint saving, continuation-style loading, diagnostics, and evaluation all work.
3. Tested standard recipe family did not beat untouched original Lite-Mono on first-100 validation relative-depth metrics.
4. Key failure pattern:
   - photo/reprojection loss can decrease
   - raw-scale depth can sometimes move closer
   - median-scaled relative-depth structure gets worse
   - adapted outputs become smoother and less structurally specific
5. Do not launch another longer/full Milestone 3 run without a new technical reason and explicit confirmation.
6. On 2026-05-11, local ignored smoke/pilot/VRAM run folders were deleted after their results had been summarized; important evidence and diagnostic runs remain under `runs/`.
7. Detailed evidence and artifact classification:
   - `citrus_project/milestones/03_self_supervised_adaptation/README.md`
   - `citrus_project/milestones/03_self_supervised_adaptation/professor_loading_and_train_eval_check.md`
   - `citrus_project/milestones/03_self_supervised_adaptation/artifact_inventory.md`
   - `citrus_project/research/baseline_notes.md`
   - `citrus_project/research/advisor_notes.md`
   - `citrus_project/research/paper_shortlist.md`

Milestone 4 - Lightweight vegetation improvement:

1. Active stage after the cleanup pass.
2. Goal: choose one lightweight vegetation-focused improvement that targets the Milestone 3 and plain-Citrus-baseline failure patterns.
3. Compare against:
   - original Lite-Mono baseline
   - documented weak/negative Milestone 3 adapted baseline
   - plain Lite-Mono trained on Citrus from ImageNet encoder pretrain
   - the Milestone 4 proposed variant
4. Initial target: preserve or improve Citrus relative depth structure while adapting to vegetation scenes.
5. Milestone folder: `citrus_project/milestones/04_lightweight_vegetation_improvement/`.
6. Milestone 4 workstream folders:
   - `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/` for Levinson's self-supervised Milestone 4 improvement path.
   - `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/` for Marvel's supervised or hybrid Milestone 4 path using valid depth labels, valid masks, or LiDAR-guided training.
7. The current B0 plain Citrus baseline snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/`; it contains inference weights, a no-code-changes marker, command scripts, copied val/test result CSV/JSON files, copied visual comparison panels, and copied `config/opt.json`.
8. The photometric-confidence masking gate snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/01_photometric_confidence_masking/`; it contains copied tested `trainer.py` and `options.py`, command scripts, metric/diagnostic summaries, and an `uncertain / do not scale yet` conclusion.
9. The RGB-edge structure-preserving loss gate snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/02_rgb_edge_structure_preserving_loss/`; it contains copied tested `trainer.py` and `options.py`, command scripts, metric/diagnostic summaries, and a `stop` conclusion.
10. The soft confidence multiplier backup gate snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/03_soft_confidence_multiplier/`; it contains copied tested `trainer.py` and `options.py`, command scripts, metric/diagnostic summaries, and a `stop` conclusion.
11. The Vegetation-General Temporal Cross-View Consistency gate snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/04_vegetation_general_temporal_cross_view_consistency/`; it contains copied tested `trainer.py`, `options.py`, the diagnostic renderer script, command scripts, result/diagnostic summaries, qualitative diagnostic maps, a final diff, `diagnostic_report_and_snapshot05_proposal.md`, and a `stable weak negative; do not scale` conclusion.
12. The Teacher-Anchored Relative-Structure Regularization snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/`; it contains copied tested `trainer.py`, `options.py`, helper scripts, command files, `config/opt.json`, result CSV/JSON/Markdown summaries, diagnostic reports/maps, visual comparison folders, a final diff, and a `continue / promising mixed` conclusion.
13. The Teacher Anchor Stabilization snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/`; it reuses the Snapshot 05 teacher implementation with reduced ranking weight and no texture-ambiguity emphasis, contains copied tested code, command files, `config/opt.json`, result CSV/JSON/Markdown summaries, visual/diagnostic maps, patch artifacts, and a `promising mixed / marginal stabilization` conclusion.
14. The Structure-Aware Label-Free Vegetation Depth snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/`; it adds reliable-boundary teacher weighting plus RGB-only sky/far ordinal pseudo-structure, contains `DESIGN_NOTE.md`, copied tested code, command files, `config/opt.json`, result/diagnostic summaries, visual manifests, a final diff, and a `promising mixed / strongest Levinson label-free candidate so far` conclusion.
15. The teacher-anchor checkpoint-selection note is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/`; it evaluated Snapshot 05 and Snapshot 06 `weights_0` through `weights_29` on full validation, selected checkpoints without test access, then tested only the selected checkpoints. Its large local sweep outputs are under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/`, which is ignored by this checkout's `.git/info/exclude`.
16. The selected Snapshot 05 `weights_19` visual/inference package is snapshot-local generated evidence at `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/`, also ignored by the local personal exclude file. The clearer professor-facing `weights_19` diagnosis package is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/`.
17. Snapshot 07 generated evidence is snapshot-local and ignored under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/local_evidence/`; compact summaries are tracked in its `results/` and `diagnostics/` folders.
18. Future Levinson improvement code snapshots should live under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/` once an improvement is implemented and tested.
19. Use descriptive numeric future snapshot names such as `08_method_name/`; record paper-style labels such as `A` or `A+B` inside the stage README only if useful.
20. Each completed improvement-stage snapshot should include one compact `README.md`, copies of changed code files when the stage is tested, optional small command/config/patch notes, and pointers to checkpoints, results, visuals, metric summary, and continue/stop/uncertain conclusion.
21. Large local generated evidence should stay under the relevant snapshot's ignored `local_evidence/` folder or the relevant checkpoint-selection note's ignored `local_results/` folder. The shared `.gitignore` ignores Levinson `runs/`, future `results/`, snapshot `local_evidence/`, and checkpoint-selection `local_results/`; this checkout also keeps matching `.git/info/exclude` rules as a personal safety net.
22. Whenever a Milestone 4 improvement changes `.py` files such as `trainer.py`, `options.py`, `layers.py`, `networks/*.py`, or helper scripts, duplicate the tested versions into the relevant stage snapshot under `code/`, preserving clear relative paths when useful. If a completed stage has no code changes, keep a simple marker such as `code/NO_CODE_CHANGES.txt`.
23. Milestone 4 collaborators should keep work inside their own workstream folder, update the shared Milestone 4 README when paths or collaboration rules change, and avoid editing another person's snapshots without explicit coordination.
24. After the 01/02/03 Milestone 4 gates were packaged, the live root `options.py` and `trainer.py` were restored to the shared baseline state for collaboration. Snapshot 04 then left the live root on the temporal-cross-view method branch. Snapshot 05 superseded that active branch; Snapshot 06 was a config-only stabilization of the same teacher-anchored branch; Snapshot 07 now supersedes the active workbench with structure-aware teacher/sky-far code. Live root `options.py`, `trainer.py`, `render_teacher_structure_diagnostics.py`, and the visual comparison helper remain active for Snapshot 07, with tested copies preserved in Snapshot 07 `code/`. The explicit policy note is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md`: root code is the active implementation workbench; snapshot `code/` folders are frozen archival copies and are not automatically imported by `train.py`.
25. Workstream separation decision:
   - Levinson's path should prioritize self-supervised RGB-only training methods.
   - Levinson should not use `depth_gt`, `valid_mask`, LiDAR labels, dense labels, sparse labels, or ZED depth as a training loss unless the team explicitly creates a separate hybrid branch.
   - Marvel's path can explore supervised or hybrid methods that use valid depth labels, valid masks, or LiDAR-guided training.
   - Both paths should keep inference RGB-only unless explicitly stated otherwise, but their training supervision differs and must be labeled honestly.
   - Do not directly claim supervised/hybrid results are fair wins over self-supervised results without clear labeling and matched comparison context.

Milestone 4 photometric-confidence masking gate:

1. Tested in its snapshot as a disabled-by-default training-loss option:
   - `--photometric_confidence_masking`
   - `--photometric_confidence_threshold`
   - `--photometric_confidence_ramp`
   - `--photometric_confidence_min_weight`
2. It adds on top of existing automasking and remains self-supervised: it uses only RGB reconstruction-vs-identity losses, not `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED depth as a training loss.
3. Inference is unchanged: one RGB image goes through the same Lite-Mono encoder/depth decoder.
4. Moderate gate defaults: threshold `0.01`, ramp `0.05`, min weight `0.25`.
5. CUDA smoke passed, and the 250-step gate completed from ImageNet encoder pretrain with batch size 12, seed 0, and no `--load_weights_folder weights/lite-mono`.
6. First-100 validation at step 250:
   - same-budget no-mask ImageNet-pretrain control: raw `abs_rel=0.9099`, raw `a1=0.0000`, median-scaled `abs_rel=0.5634`, median-scaled `a1=0.3577`
   - photometric-confidence masking: raw `abs_rel=0.8985`, raw `a1=0.0000`, median-scaled `abs_rel=0.5582`, median-scaled `a1=0.3018`
7. Interpretation: stable but mixed. It slightly improves median-scaled `abs_rel` over the same-budget control but worsens median-scaled `a1`, and both 250-step ImageNet-pretrain runs are much weaker than the original first-100 reference. Do not scale this method yet without a follow-up technical reason.

Milestone 4 overnight self-supervised gates after photometric confidence:

1. RGB-edge structure-preserving loss was tested in its snapshot as a disabled-by-default training-loss option:
   - `--rgb_edge_structure_loss`
   - `--rgb_edge_structure_weight`
   - `--rgb_edge_structure_threshold`
   - `--rgb_edge_structure_blur_kernel`
   - `--rgb_edge_structure_target_grad`
2. It remains self-supervised: it uses only the target RGB image and predicted normalized disparity, not `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, or ZED depth as a training loss. Inference is unchanged.
3. First-100 validation at step 250:
   - same-budget no-mask ImageNet-pretrain control: raw `abs_rel=0.9099`, raw `a1=0.0000`, median-scaled `abs_rel=0.5634`, median-scaled `a1=0.3577`
   - RGB-edge structure loss: raw `abs_rel=0.8993`, raw `a1=0.0000`, median-scaled `abs_rel=0.5822`, median-scaled `a1=0.3280`
4. Interpretation: stable but negative. It worsened both median-scaled `abs_rel` and `a1` versus the same-budget control, so stop this exact configuration.
5. Soft confidence multiplier was tested in its snapshot as a disabled-by-default independent backup option:
   - `--soft_confidence_multiplier`
   - `--soft_confidence_threshold`
   - `--soft_confidence_ramp`
   - `--soft_confidence_strength`
   - `--soft_confidence_min_multiplier`
6. It remains self-supervised: it uses only RGB reconstruction and identity/no-warp losses, not depth labels. Inference is unchanged.
7. First-100 validation at step 250:
   - same-budget no-mask ImageNet-pretrain control: raw `abs_rel=0.9099`, raw `a1=0.0000`, median-scaled `abs_rel=0.5634`, median-scaled `a1=0.3577`
   - soft confidence multiplier: raw `abs_rel=0.8978`, raw `a1=0.0000`, median-scaled `abs_rel=0.5676`, median-scaled `a1=0.3068`
8. Interpretation: stable but negative. It did not rescue the confidence direction and clearly worsened median-scaled `a1`, so stop this exact configuration.
9. Do not scale the exact 01, 02, or 03 configurations by default. Keep future Milestone 4 self-supervised changes isolated and first test with 250-step gates.

Milestone 4 vegetation-general temporal cross-view consistency gate:

1. Snapshot 04 implemented a coherent self-supervised method family with disabled-by-default flags for:
   - `--temporal_geo_consistency`
   - `--temporal_geo_weight`
   - `--temporal_geo_warmup_steps`
   - `--temporal_consistency_scales`
   - `--visibility_aware_geo`
   - `--visibility_cycle_threshold`
   - `--texture_ambiguity_weighting`
   - `--texture_ambiguity_weight`
   - `--feature_cross_view_consistency`
   - `--feature_consistency_weight`
   - `--feature_consistency_warmup_steps`
   - `--feature_consistency_scale`
2. It remains self-supervised and RGB-only at inference: source-frame depth/features, PoseNet geometry, visibility masks, texture ambiguity maps, and feature consistency are training-only and use only RGB frames plus intrinsics.
3. The source-frame branch was revised to a stop-gradient teacher after a batch-size-12 gate attempt was too slow when source depths participated in the backward graph.
4. First-100 validation at step 250:
   - same-budget no-mask control: median-scaled `abs_rel=0.5634`, `a1=0.3577`
   - temporal geometry: median-scaled `abs_rel=0.5666`, `a1=0.3597`
   - geometry + default visibility: median-scaled `abs_rel=0.5688`, `a1=0.3581`
   - geometry + strict visibility threshold `0.003`: median-scaled `abs_rel=0.5884`, `a1=0.3107`
   - geometry + texture ambiguity: median-scaled `abs_rel=0.5651`, `a1=0.3605`
   - geometry + feature consistency: median-scaled `abs_rel=0.5581`, `a1=0.3373`
   - full reduced-feature method: median-scaled `abs_rel=0.5755`, `a1=0.3503`
5. Interpretation: technically stable but weak negative evidence. The best branch, geometry + texture ambiguity, gives only a tiny `a1` gain over the no-mask control and still worsens median-scaled `abs_rel`; feature consistency improves `abs_rel` but hurts `a1`; strict visibility becomes too sparse; full stacking is negative.
6. Do not launch a longer Snapshot 04 run. The diagnostic report concludes that temporal geometry compared the model mostly against itself, default visibility was mostly projection validity, feature consistency was too coarse for thin vegetation, and texture ambiguity is the only component worth reusing as a weak prior/diagnostic.
7. The Snapshot 04 design-only follow-up proposal was superseded by the completed Snapshot 05 run described below.

Milestone 4 teacher-anchored relative-structure regularization:

1. Snapshot 05 folder: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/`.
2. Method framing: Teacher-Anchored Relative-Structure Regularization for Label-Free Self-Supervised Vegetation Adaptation.
3. Training uses the standard Citrus self-supervised monocular video objective plus a frozen RGB-only Lite-Mono teacher from `weights/lite-mono/`.
4. The teacher is training-only and supplies pseudo-structure from RGB predictions, not ground truth. The student is not forced to copy teacher metric scale.
5. Enabled full-run flags:
   - `--teacher_structure_regularization`
   - `--teacher_structure_weight 0.03`
   - `--teacher_structure_warmup_steps 500`
   - `--teacher_structure_decay 0.5`
   - `--teacher_gradient_loss`
   - `--teacher_gradient_weight 0.01`
   - `--teacher_ranking_loss`
   - `--teacher_ranking_weight 0.02`
   - `--teacher_rank_samples 512`
   - `--teacher_texture_ambiguity_emphasis`
   - `--texture_ambiguity_weight 0.25`
   - `--teacher_path weights/lite-mono`
6. Teacher confidence flags were implemented but left off for the full run.
7. The method remains label-free for Citrus training: it does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses or training masks. Citrus labels/masks are evaluation-only.
8. Inference remains unchanged and lightweight: one RGB image goes through the Lite-Mono student encoder/depth decoder.
9. Full run:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/`.
10. Final checkpoint:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_29/`.
11. Evaluation:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full/`.
12. Full validation result: raw `abs_rel=0.7372`, raw `a1=0.0169`, median-scaled `abs_rel=0.4611`, median-scaled `a1=0.5954`.
13. Full test result: raw `abs_rel=0.7359`, raw `a1=0.0147`, median-scaled `abs_rel=0.4132`, median-scaled `a1=0.6463`.
14. Comparison: Snapshot 05 improves B0's raw and median-scaled `abs_rel` on val/test while keeping most of B0's median-scaled `a1` gain; against original Lite-Mono it improves median-scaled `a1` but still worsens median-scaled `abs_rel`.
15. Conclusion: promising mixed evidence and the strongest Levinson label-free direction so far, but not a clean win over original Lite-Mono. Continue with one deliberate revision, not random variant stacking.

Milestone 4 teacher anchor stabilization:

1. Snapshot 06 folder: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/`.
2. Method framing: Teacher Anchor Stabilization, still label-free teacher-anchored self-supervised adaptation.
3. Snapshot 06 reused the active Snapshot 05 teacher implementation and changed only the full-run configuration:
   - reduced `--teacher_ranking_weight` from `0.02` to `0.005`
   - removed `--teacher_texture_ambiguity_emphasis`
   - kept `--teacher_structure_weight 0.03`
   - kept `--teacher_gradient_weight 0.01`
   - kept `--teacher_structure_warmup_steps 500`
   - kept `--teacher_structure_decay 0.5`
   - kept `--teacher_rank_samples 512`
   - kept `--teacher_path weights/lite-mono`
4. The motivation was Snapshot 05's per-sample tradeoff: it improved many average errors but trailed B0 on median-scaled `a1`, with ranking as the largest final teacher-loss term and texture emphasis potentially focusing teacher pressure in ambiguous vegetation regions.
5. The method remains label-free for Citrus training: it does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses or training masks. Citrus labels/masks are evaluation-only.
6. Inference remains unchanged and lightweight: one RGB image goes through the Lite-Mono student encoder/depth decoder.
7. Full run:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/`.
8. Final checkpoint:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29/`.
9. Evaluation:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/`.
10. Full validation result: raw `abs_rel=0.7375`, raw `a1=0.0165`, median-scaled `abs_rel=0.4578`, median-scaled `a1=0.5993`.
11. Full test result: raw `abs_rel=0.7348`, raw `a1=0.0150`, median-scaled `abs_rel=0.4168`, median-scaled `a1=0.6418`.
12. Comparison: Snapshot 06 slightly improves Snapshot 05 on validation median-scaled `abs_rel` and `a1`, but slightly worsens Snapshot 05 on test median-scaled `abs_rel` and `a1`. It still improves B0 on median-scaled `abs_rel`, still trails B0 on median-scaled `a1`, and still trails original Lite-Mono on median-scaled `abs_rel`.
13. Conclusion: promising mixed / marginal stabilization. Keep as a deliberate ablation; do not declare it a clean replacement for Snapshot 05.

Milestone 4 teacher-anchor checkpoint selection:

1. Checkpoint-selection note: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/README.md`.
2. Sweep output folder: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/checkpoint_selection/teacher_anchor_snapshot05_06/local_results/`.
3. Selection rule: evaluate all Snapshot 05 and Snapshot 06 `weights_0` through `weights_29` on full validation; select the checkpoint with lowest validation median-scaled `abs_rel` among checkpoints whose validation median-scaled `a1` is within `0.02` absolute of B0 validation `a1=0.6107`; if none qualify, fall back to lowest validation `abs_rel`. Test is not used for selection.
4. Validation-selected Snapshot 05 checkpoint: `weights_19`, with validation raw `abs_rel=0.7389`, raw `a1=0.0177`, median-scaled `abs_rel=0.4447`, median-scaled `a1=0.5915`.
5. Validation-selected Snapshot 06 checkpoint: `weights_25`, with validation raw `abs_rel=0.7347`, raw `a1=0.0166`, median-scaled `abs_rel=0.4493`, median-scaled `a1=0.5925`.
6. Selected Snapshot 05 `weights_19` test result: raw `abs_rel=0.7391`, raw `a1=0.0144`, median-scaled `abs_rel=0.3947`, median-scaled `a1=0.6476`.
7. Selected Snapshot 06 `weights_25` test result: raw `abs_rel=0.7310`, raw `a1=0.0148`, median-scaled `abs_rel=0.4076`, median-scaled `a1=0.6359`.
8. Interpretation before Snapshot 07: Snapshot 05 `weights_19` was the best Levinson label-free teacher-anchor checkpoint. It clearly improved B0 median-scaled `abs_rel` (`0.4889` to `0.3947`) while keeping most of B0 median-scaled `a1` (`0.6582` to `0.6476`). It got close to original Lite-Mono test median-scaled `abs_rel=0.3836` but did not beat it.
9. Validation-only caveat: very early `weights_7` checkpoints had lower validation median-scaled `abs_rel` (`0.3716` for Snapshot 05 and `0.3882` for Snapshot 06) but failed the B0-close `a1` threshold (`0.5110` and `0.5007`), so they were not selected or tested.
10. Visual/inference packaging completed on 2026-05-19 without new training. Output folder: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/`.
11. The package includes original-vs-`weights_19`, B0-vs-`weights_19`, and `weights_29`-vs-`weights_19` panels for full validation and test representatives, plus plain `weights_19` RGB/raw-depth/median-scaled-depth/disparity PNGs, NPZ arrays, and a manifest for representative validation/test samples.
12. Professor-facing visual diagnosis package generated without new training: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/`. It contains full-image qualitative panels, valid-mask-only error panels, cropped/masked evaluated-region panels, `weights_29` versus `weights_19` panels, plain inference panels, `sample_selection.csv/json`, and `visual_diagnosis.md`. A tracked compact summary is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/diagnostics/weights19_professor_visual_diagnosis_summary.md`.
13. Visual read: mixed but useful. Good/typical cases show broad relative-structure behavior consistent with aggregate gains; failure/largest-drop cases still show smooth maps and over-correction around vegetation/occlusion regions. The professor-facing diagnosis explicitly notes that full-image sky/far-canopy and dark-blob artifacts remain and that `weights_19` is numerically promising but not visually paper-polished. Keep `weights_19` as the main Snapshot 05 comparison point, while noting it has been superseded by Snapshot 07 as the current lead Levinson label-free candidate.

Milestone 4 structure-aware label-free vegetation depth:

1. Snapshot 07 folder: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/`.
2. Method framing: Structure-Aware RGB-Teacher-Guided Label-Free Self-Supervised Vegetation Depth.
3. Snapshot 07 builds from the active Snapshot 05/06 teacher-anchor root code and adds two training-only label-free signals:
   - reliable-boundary teacher anchoring from RGB edge confidence multiplied by frozen-teacher disparity-edge confidence;
   - RGB-only sky/far ordinal pseudo-structure from conservative color, brightness, saturation, and top-image priors.
4. It targets Snapshot 05 `weights_19` visual failures: vegetation blobs, over-smoothing, sky/far-canopy confusion, tree-ground boundary weakness, and weak full-image qualitative depth.
5. The method remains label-free for Citrus training: it does not use `depth_gt`, `valid_mask`, dense LiDAR, sparse LiDAR, ZED depth, or LiDAR-derived labels as training losses or training masks. Citrus labels/masks are evaluation-only.
6. Inference remains unchanged and lightweight: one RGB image goes through the Lite-Mono student encoder/depth decoder.
7. Design note: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/07_structure_aware_label_free_vegetation_depth/DESIGN_NOTE.md`.
8. Full run:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/structure_aware_label_free_vegetation_depth_b12_30ep_full/`.
9. Validation-selected checkpoint:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/structure_aware_label_free_vegetation_depth_b12_30ep_full/models/weights_25/`.
10. CUDA smoke passed with finite losses and non-trivial new maps. Snapshot 07 pilot first-100 validation at step 250 improved the same-budget no-mask control on both median metrics: control median-scaled `abs_rel=0.5634`, `a1=0.3577`; Snapshot 07 pilot median-scaled `abs_rel=0.5497`, `a1=0.3712`.
11. Validation-only checkpoint selection evaluated `weights_0` through `weights_29` on full validation and selected `weights_25` by the B0-close `a1` rule before test evaluation.
12. Selected Snapshot 07 `weights_25` full validation result: raw `abs_rel=0.7265`, raw `a1=0.0167`, median-scaled `abs_rel=0.4344`, median-scaled `a1=0.5927`.
13. Selected Snapshot 07 `weights_25` full test result: raw `abs_rel=0.7297`, raw `a1=0.0130`, median-scaled `abs_rel=0.3840`, median-scaled `a1=0.6539`.
14. Comparison: Snapshot 07 beats B0 and Snapshot 05 `weights_19` on test median-scaled `abs_rel`, improves test median-scaled `a1` over Snapshot 05 `weights_19`, nearly matches original Lite-Mono on test median-scaled `abs_rel` (`0.3840` versus `0.3836`), and strongly beats original Lite-Mono on test median-scaled `a1` (`0.6539` versus `0.4989`). It slightly trails B0 test median-scaled `a1=0.6582`.
15. Visual judgment: promising mixed. Valid-mask panels often support the metric gains, but full-image plain inference still shows smooth vegetation masses and some sky/far-canopy weakness.
16. Conclusion: promising mixed / strongest Levinson label-free candidate so far. Treat Snapshot 07 `weights_25` as the current lead paper candidate, but do not claim the full-image visual problem is solved.

Milestone 4 plain Lite-Mono Citrus baseline planning:

1. User agreed that the fair plain Lite-Mono Citrus baseline should start from the Lite-Mono ImageNet encoder pretrain, not from KITTI depth-trained `encoder.pth`/`depth.pth`.
2. This means "Citrus-only depth training from ImageNet visual features," not true random-weight scratch training.
3. The run should use `--mypretrain weights/lite-mono/lite-mono-pretrain.pth` and should not use `--load_weights_folder weights/lite-mono` when the purpose is the plain Citrus training baseline.
4. Confirmed paper/README-matching baseline recipe: `batch_size=12`, `num_epochs=30`, `lr=0.0001 5e-6 31 0.0001 1e-5 31`, AdamW, `weight_decay=1e-2`, `drop_path=0.2`, input size `640x192`, monocular temporal frames `[0,-1,1]`, and 50% flip/color augmentation.
5. Use `--weights_init pretrained` for the pose ResNet encoder, consistent with the Lite-Mono paper's PoseNet setup.
6. Use `--num_workers 0` for the first overnight run for Windows stability and because previous controlled Citrus runs used it; this is an engineering/data-loading setting, not a research hyperparameter.
7. The RTX 4060 Laptop GPU already passed true batch-size-12 one-step smoke and completed a batch-size-12 one-epoch control in Milestone 3, so this recipe is technically feasible.
8. Expected runtime for the 30-epoch run is roughly 10-15 hours, based on the previous batch-size-12 one-epoch timing.
9. Confirmed output folder:
   `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/`.
10. Run completed successfully on 2026-05-10; originally saved checkpoints `weights_0` through `weights_29`.
11. Historical mid-run `weights_15` CPU first-100 validation probe: raw `abs_rel=0.7807`, raw `a1=0.0055`, median-scaled `abs_rel=0.4478`, median-scaled `a1=0.6720`. This was a mixed signal versus the original first-100 reference (`abs_rel=0.3680`, `a1=0.4807`): `a1` improved, `abs_rel` worsened.
12. Final epoch `weights_29` full validation: raw `abs_rel=0.7736`, `a1=0.0074`; median-scaled `abs_rel=0.5100`, `a1=0.6107`.
13. Final epoch `weights_29` full test: raw `abs_rel=0.7787`, `a1=0.0077`; median-scaled `abs_rel=0.4889`, `a1=0.6582`.
14. Interpretation: final epoch improves median-scaled `a1` over original Lite-Mono on val/test, but worsens raw-scale metrics and median-scaled `abs_rel`. This is useful positive signal but not a clean improvement.
15. Saved final evaluation:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/`.
16. Saved comparison panels:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/results/plain_litemono_imagenet_b12_30ep_final_weights29/visual_compare_original_vs_final_val_full/`.
17. The full training run folder is local/ignored. On 2026-05-11, old epoch checkpoints `weights_0` through `weights_28` were deleted locally; full `weights_29` remains for unlikely exact-resume/debug needs.
18. Final B0 baseline package:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/`.
19. The old `baseline_checkpoint/` inference-only copy was removed after B0 was migrated into the agreed snapshot structure.
20. A checkpoint sweep was tried after final evaluation but discarded from committed evidence after visual review; do not use sweep-derived checkpoints as representative Milestone 4 baselines unless a later explicitly approved selection rule reintroduces them.

Later milestones:

1. Milestone 5: optional broader supervised/hybrid expansion or paper-facing follow-up beyond the current Marvel Milestone 4 supervised/hybrid workstream.
2. Milestone 6: paper package, tables, figures, and writing support.

## Milestone 3 Evidence Snapshot

Professor-facing names should describe experiment purpose, not internal run-folder names.
Internal folder names belong in technical mapping sections.

Important first-100 validation reference:

1. Untouched original Lite-Mono: median-scaled `abs_rel=0.3680`, `a1=0.4807`.
2. Conservative control after 1000 updates: median-scaled `abs_rel=0.6615`, `a1=0.1827`.
3. No-color-augmentation control after 250 updates: median-scaled `abs_rel=0.4108`, `a1=0.4568`.
4. No-color-augmentation control after 500 updates: median-scaled `abs_rel=0.5300`, `a1=0.3513`.
5. Normal batch-size-12 one-epoch control final: median-scaled `abs_rel=3.0501`, `a1=0.2473`.

Advisor-requested checks:

1. Parameter loading:
   - original encoder/depth tensors load with no missing model tensors
   - fully depth-frozen checkpoint matches original encoder/depth tensors exactly on common model tensors
2. Training-image evaluation:
   - adapted checkpoints do not become high-accuracy on first-100 training images
   - train-image behavior mirrors validation behavior
3. Sparse LiDAR-only evaluation:
   - first-100 validation, raw projected sparse LiDAR only, no `local_idw`
   - original median-scaled `abs_rel=0.6072`, `a1=0.3724`
   - conservative final1000 median-scaled `abs_rel=0.8445`, `a1=0.1441`
   - no-augmentation 250-step median-scaled `abs_rel=0.6712`, `a1=0.3234`
4. Batch-size feasibility:
   - true batch sizes 8 and 12 pass one-step CUDA smokes on the RTX 4060 Laptop GPU
   - batch size 12 did not fix the one-epoch control

Interpretation:

1. Current evidence does not support wrong depth-weight loading, validation-only generalization failure, `local_idw` densification alone, or small batch size alone as the Milestone 3 failure cause.
2. The standard self-supervised photo objective is not aligned enough with LiDAR-valid Citrus relative-depth quality under the tested recipe family.
3. Milestone 4 should target depth-structure preservation or vegetation-aware cues, not blind scaling of the same recipe.

## Artifact Policy

Do not delete experiment evidence, checkpoints, generated panels, scripts, or notes without first classifying them and getting explicit user approval.

Current categories:

1. Source-of-truth notes:
   - `AGENTS.md`
   - milestone README files
   - `citrus_project/research/*.md`
2. Evidence-bearing outputs:
   - full prepared dataset
   - projection audit diagnostics
   - Milestone 1 results/visuals
   - Milestone 3 important run folders/checkpoints/evaluations/diagnostics
3. Helper scripts:
   - dataset scripts in `citrus_project/dataset_workspace/`
   - milestone helpers under `citrus_project/milestones/*/`
4. Generated/ignored outputs:
   - `citrus_project/dataset_workspace/projection_alignment_audit/`
   - `citrus_project/research/generated/`
   - `citrus_project/milestones/03_self_supervised_adaptation/runs/`
   - `tmp_trainer_wiring_smoke/`
   - `__pycache__/`
5. Possible cleanup candidates after approval:
   - disposable smoke-test checkpoints whose results are already summarized
   - small local smoke folders such as `tmp_trainer_wiring_smoke/`
   - Python cache folders

Milestone 3 run-specific classification lives in:

```text
citrus_project/milestones/03_self_supervised_adaptation/artifact_inventory.md
```

## Known Risks

1. LiDAR-derived dense labels are project-generated, not official Citrus Farm ground truth.
2. Dense interpolation can create plausible but unsupported depth in vegetation gaps; valid masks and conservative fill settings are mandatory.
3. Citrus Farm Sequence 01 is only the current validation domain. Broader agricultural claims need more data or careful wording.
4. Standard self-supervised adaptation can reduce photo loss while damaging depth structure.
5. Long training runs should use planned checkpoints, monitoring, and clear stop criteria.
6. TensorBoard logs and checkpoints can consume several GB; classify before cleanup.

## Terminology

1. Pairing: matching RGB frames and LiDAR scans by timestamp.
2. Projection: mapping LiDAR 3D points into the ZED image plane using calibration.
3. Densification: turning sparse projected LiDAR into a semi-dense depth map.
4. Valid mask: pixels where the depth label should be trusted for metrics/training.
5. Raw metrics: depth metrics before scale correction.
6. Median-scaled metrics: metrics after one per-image scale correction; useful for judging relative near/far structure.
7. Photo loss: self-supervised image reconstruction loss used during Lite-Mono-style training.
8. Pose network: training-time helper for camera motion; not used for RGB-only depth inference.

## Quick Commands

Use `D:/Conda_Envs/lite-mono/python.exe` as the current project Python.

Dataset build from `citrus_project/dataset_workspace/`:

```powershell
D:/Conda_Envs/lite-mono/python.exe build_training_dataset.py
```

Projection audit from `citrus_project/dataset_workspace/`:

```powershell
D:/Conda_Envs/lite-mono/python.exe audit_projection_alignment.py --max_samples 12 --output_dir projection_alignment_audit/time_spread_visual_12
```

Milestone 1 full baseline from repo root:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 0 --run_model --summary_only --progress_interval 50 --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split test --max_samples 0 --run_model --summary_only --progress_interval 50 --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

Milestone 2 core smokes from repo root:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/02_citrus_integration/inspect_citrus_prepared_dataset.py --temporal --samples_per_split 2 --batch_size 2 --splits train val
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/02_citrus_integration/inspect_temporal_neighbors.py
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/02_citrus_integration/smoke_root_citrus_one_step_train.py --use_cuda
```

Milestone 3 status:

1. Do not run another long Milestone 3 adaptation by default.
2. Use `artifact_inventory.md`, the Milestone 3 README, and `baseline_notes.md` before deciding whether any run folder is needed.

## Next Actions

Immediate:

1. Treat the final-epoch plain Lite-Mono Citrus run as mixed evidence, not a clean improvement.
2. Do not delete generated evidence or checkpoints unless the user explicitly approves a specific cleanup list.
3. Keep professor-facing names descriptive and keep internal run-folder names in technical mappings.
4. Treat Milestone 4 gates `01_photometric_confidence_masking`, `02_rgb_edge_structure_preserving_loss`, and `03_soft_confidence_multiplier` as completed non-scaling gates.
5. Treat Snapshot 04 temporal cross-view consistency as stable weak negative evidence; do not scale it.
6. Treat Snapshot 05 teacher-anchored relative-structure regularization as promising mixed label-free evidence; after validation-only checkpoint selection and visual packaging, Snapshot 05 `weights_19` is the strongest pre-Snapshot07 teacher-anchor checkpoint and a key comparison point.
7. Treat Snapshot 06 teacher anchor stabilization as a completed deliberate ablation: reducing ranking weight and removing texture emphasis slightly improved validation versus Snapshot 05 final weights but did not beat Snapshot 05 `weights_19`.
8. Treat Snapshot 07 structure-aware label-free vegetation depth as the current strongest Levinson label-free candidate: selected `weights_25` has test median-scaled `abs_rel=0.3840`, `a1=0.6539`, nearly matching original Lite-Mono on `abs_rel` while preserving B0-like `a1`, but qualitative full-image depth remains mixed.
9. The active root code remains the Snapshot 07 structure-aware branch; use `ACTIVE_ROOT_CODE_STATE.md`, the Snapshot 07 `code/` folder, and Snapshot 07 patch artifacts if the shared baseline or an earlier snapshot state needs to be restored later.
10. Future Levinson follow-up should not start new training until the team reviews the Snapshot 07 visual packages, reads `ACTIVE_ROOT_CODE_STATE.md`, and decides whether Snapshot 07 is sufficient for the paper or whether one final clearly motivated visual-structure refinement is worth running.
11. Keep Levinson's next work label-free/self-supervised unless a separate hybrid branch is explicitly approved.
12. Let Marvel explore supervised/hybrid depth-label or valid-mask-guided ideas in the separate Marvel workstream.
13. Do not launch longer 01/02/03/04 runs by default and do not randomly stack more Snapshot 05/06/07 variants.

Milestone 4 planning questions:

1. Is Snapshot 07 `weights_25` sufficient as the current label-free paper-table result, given that it nearly matches original Lite-Mono's median-scaled `abs_rel` while preserving B0-like `a1`?
2. Is one final visual-structure refinement justified, or should Snapshot 07 be frozen and explained honestly as promising mixed?
3. Which Milestone 3 weak baseline checkpoint should represent standard adaptation in comparison tables?
4. Which Snapshot 07 qualitative cases best explain the improved `abs_rel` and remaining full-image visual weaknesses?

## Recent Change Log

1. 2026-04-17: Final/default dense-label transform locked to `exact_lidar_parent_child_inverted`.
2. 2026-04-23: Full `prepared_training_dataset/` build completed with 5282 samples and time-block splits.
3. 2026-04-28: Full original Lite-Mono Citrus validation/test baseline completed and saved.
4. 2026-05-05: Milestone 2 core Citrus trainer integration completed, including CUDA one-step smoke.
5. 2026-05-07: Milestone 3 standard self-supervised adaptation closed as weak/negative evidence.
6. 2026-05-08: Advisor checks completed for parameter loading, train-image evaluation, sparse LiDAR-only evaluation, and batch-size-12 control.
7. 2026-05-09: Workspace cleanup pass compacted this file and moved Milestone 3 artifact classification into the milestone workspace.
8. 2026-05-09: Milestone 4 baseline planning recorded ImageNet-encoder initialization for the plain Lite-Mono Citrus baseline.
9. 2026-05-10: Plain Lite-Mono Citrus ImageNet-pretrained 30-epoch run completed; final `weights_29` val/test evaluation and original-vs-final comparison panels saved under the Milestone 4 results folder.
10. 2026-05-10: Checkpoint-sweep interpretation was reverted after visual review; final-epoch `weights_29` remains the current inspected plain Lite-Mono Citrus baseline evidence, with the full run ignored and an inference-only checkpoint copy tracked.
11. 2026-05-11: Local cleanup deleted Milestone 4 old epoch checkpoints `weights_0` through `weights_28` and Milestone 3 smoke/pilot/VRAM run folders; committed metrics, visuals, inference weights, final `weights_29`, and Milestone 3 evidence runs were preserved.
12. 2026-05-12: Task board refreshed for Milestone 4 handoff readiness.
13. 2026-05-13: Added folder-level README maps and migrated B0 inference weights, command scripts, no-code-changes marker, result files, visual panels, and `opt.json` into Levinson's agreed Milestone 4 snapshot structure under `levinson/snapshots/00_plain_citrus_baseline/`; removed the old `baseline_checkpoint/` copy.
14. 2026-05-13: Added Milestone 4 workstream folders for `levinson/` and `Marvel/`, moved the Milestone 4 `results/` and local ignored `runs/` folders under `levinson/`, and recorded the rule that tested `.py` improvements must be duplicated into the matching stage snapshot.
15. 2026-05-14: Implemented disabled-by-default photometric-confidence masking in `options.py` and `trainer.py`, ran CUDA smoke plus a 250-step self-supervised gate and same-budget no-mask control, saved visual comparison panels, and packaged Levinson snapshot `01_photometric_confidence_masking/` with an `uncertain / do not scale yet` conclusion.
16. 2026-05-14: Ran the approved overnight Milestone 4 self-supervised queue: `02_rgb_edge_structure_preserving_loss` first, then independent backup `03_soft_confidence_multiplier` because 02 was negative. Both were stable 250-step gates but worsened median-scaled validation metrics versus the same-budget no-mask control, so both snapshots were packaged with `stop` conclusions and no 04 vegetation-aware training was run.
17. 2026-05-14: Restored the live root `options.py` and `trainer.py` to the shared baseline state after packaging the 01/02/03 snapshot code copies, reducing collaboration friction while preserving reproducibility evidence in Levinson's snapshots.
18. 2026-05-14: Recorded Milestone 4 workstream separation: Levinson owns the self-supervised RGB-only training path, while Marvel can explore supervised/hybrid valid-depth, valid-mask, or LiDAR-guided training in a separate workstream with honest labeling.
19. 2026-05-17: Implemented and tested Levinson snapshot `04_vegetation_general_temporal_cross_view_consistency/` with temporal geometry, visibility, texture ambiguity, feature consistency, and full ablations. The source-frame branch was revised to a stop-gradient teacher for practical batch-size-12 gates. Results are stable weak negative evidence; do not scale Snapshot 04. Root `options.py`, `trainer.py`, and the new diagnostic renderer remain as the active method branch, with tested copies and `patches/final_method.diff` saved in the snapshot.
20. 2026-05-17: Added the Snapshot 04 diagnostic report, then superseded its design-only Snapshot 05 proposal with the completed `05_teacher_anchored_relative_structure_regularization/` full 30-epoch run. Snapshot 05 uses a frozen RGB-only Lite-Mono teacher for scale-invariant structure, gradient, and ranking regularization with no Citrus labels or valid masks as training losses. Final val/test metrics are promising mixed evidence: better than B0 on raw and median-scaled `abs_rel`, close to B0 on median-scaled `a1`, better than original on median-scaled `a1`, but still worse than original on median-scaled `abs_rel`. Root code remains active as the Snapshot 05 branch, with tested copies and `patches/final_method.diff` saved in the snapshot.
21. 2026-05-18: Completed Levinson snapshot `06_teacher_anchor_stabilization/`, a config-only stabilization of Snapshot 05 with reduced ranking weight (`0.005`) and no texture-ambiguity emphasis. The full 30-epoch run is stable and packaged; validation is slightly better than Snapshot 05 but test is slightly worse, so Snapshot 06 is a promising mixed/marginal ablation rather than a clean replacement. Root code remains the active teacher-anchored branch.
22. 2026-05-18: Ran validation-first checkpoint selection for Snapshot 05 and Snapshot 06 without new training. The selected checkpoints are Snapshot 05 `weights_19` and Snapshot 06 `weights_25`; test evaluation after selection shows Snapshot 05 `weights_19` is strongest so far, with test median-scaled `abs_rel=0.3947` and `a1=0.6476`.
23. 2026-05-19: Packaged Snapshot 05 selected `weights_19` as the then-best Levinson label-free teacher-anchor candidate without new training. Generated validation/test comparison panels versus original Lite-Mono, B0, and Snapshot 05 `weights_29`, plus plain selected-checkpoint RGB/depth/disparity outputs under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_visuals/`. Visuals are mixed but support using `weights_19` as the main Snapshot 05 comparison point with the caveat that it still does not beat original Lite-Mono on median-scaled `abs_rel`.
24. 2026-05-19: Tidied large Levinson generated evidence into snapshot-local `local_evidence/` folders and the checkpoint-selection note's `local_results/` folder. Added local-only `.git/info/exclude` rules for those bulky generated folders and for future `levinson/results/` outputs, and set this repository's local `core.excludesfile` to `.git/info/exclude`, so the user's checkout can keep evidence without flooding `git status`.
25. 2026-05-19: Generated a professor-facing Snapshot 05 `weights_19` visual diagnosis package without new training at `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/`. The package separates full-image qualitative issues from valid-LiDAR evaluation behavior and concludes that `weights_19` is numerically promising and professor-discussion-ready, but not visually solved or paper-polished.
26. 2026-05-19: Added the pre-Snapshot07 repository audit at `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/pre_snapshot07_repo_audit.md`, documented that root `options.py` and `trainer.py` remained active as the Snapshot 05/06 teacher-anchor branch before Snapshot 07, and promoted the local-evidence ignore policy into shared `.gitignore` while keeping `.git/info/exclude` as a personal safety net.
27. 2026-05-19: Added `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md` to make the active-root policy explicit before Snapshot 07: root code is the active workbench used by `train.py`, snapshot `code/` folders are frozen archival copies, and future methods must inspect and document root-code state before editing or training.
28. 2026-05-20: Completed and packaged Levinson snapshot `07_structure_aware_label_free_vegetation_depth/`. Snapshot 07 adds reliable-boundary teacher weighting and RGB-only sky/far ordinal pseudo-structure without Citrus training labels, passed smoke and 250-step pilot gates, completed one fair 30-epoch run, selected `weights_25` by validation-only checkpoint selection, and reached test median-scaled `abs_rel=0.3840`, `a1=0.6539`. It is the current strongest Levinson label-free candidate, with promising mixed visual evidence rather than a clean solved visual story. Root code now remains active as the Snapshot 07 structure-aware branch.
29. 2026-05-20: Added the Levinson pre-presentation snapshot-folder audit at `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/SNAPSHOT_FOLDER_AUDIT_BEFORE_PRESENTATION.md` and clarified stale historical wording in Snapshot 04/05/06, the Snapshot 05/06 checkpoint-selection note, and the pre-Snapshot07 audit so future readers do not confuse pre-Snapshot07 evidence with the current Snapshot 07 lead state.
30. 2026-05-20: Added `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md` as the AI-friendly Levinson documentation map before presentation preparation, and marked old planning/design notes as historical where needed.
31. 2026-05-20: Added `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/LEVINSON_DOCS_OPTIMIZATION_BEFORE_PRESENTATION.md` to record the Levinson Markdown inventory, current documentation hierarchy, historical/stale docs, redundant/confusing files, and presentation-readiness decision.

## Update Template

Date:
Changed files:
What changed:
Why:
Validation run:
Open risks:
Next step:
Note-maintenance action:
