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
   `citrus_project/milestones/04_lightweight_vegetation_improvement/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/`.
10. Run completed successfully on 2026-05-10; originally saved checkpoints `weights_0` through `weights_29`.
11. Historical mid-run `weights_15` CPU first-100 validation probe: raw `abs_rel=0.7807`, raw `a1=0.0055`, median-scaled `abs_rel=0.4478`, median-scaled `a1=0.6720`. This was a mixed signal versus the original first-100 reference (`abs_rel=0.3680`, `a1=0.4807`): `a1` improved, `abs_rel` worsened.
12. Final epoch `weights_29` full validation: raw `abs_rel=0.7736`, `a1=0.0074`; median-scaled `abs_rel=0.5100`, `a1=0.6107`.
13. Final epoch `weights_29` full test: raw `abs_rel=0.7787`, `a1=0.0077`; median-scaled `abs_rel=0.4889`, `a1=0.6582`.
14. Interpretation: final epoch improves median-scaled `a1` over original Lite-Mono on val/test, but worsens raw-scale metrics and median-scaled `abs_rel`. This is useful positive signal but not a clean improvement.
15. Saved final evaluation:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/results/plain_litemono_imagenet_b12_30ep_final_weights29/`.
16. Saved comparison panels:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/results/plain_litemono_imagenet_b12_30ep_final_weights29/visual_compare_original_vs_final_val_full/`.
17. The full training run folder is local/ignored. On 2026-05-11, old epoch checkpoints `weights_0` through `weights_28` were deleted locally; full `weights_29` remains for unlikely exact-resume/debug needs.
18. Tracked inference-only final baseline weights:
    `citrus_project/milestones/04_lightweight_vegetation_improvement/baseline_checkpoint/plain_litemono_imagenet_b12_30ep_weights29_inference/`.
19. A checkpoint sweep was tried after final evaluation but discarded from committed evidence after visual review; do not use sweep-derived checkpoints as representative Milestone 4 baselines unless a later explicitly approved selection rule reintroduces them.

Later milestones:

1. Milestone 5: optional supervised or hybrid training with dense LiDAR labels.
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
4. Continue Milestone 4 planning around a structure-preserving or vegetation-aware lightweight improvement using the new plain-Citrus-baseline failure pattern.

Milestone 4 planning questions:

1. Which failure signal should the first method target: relative-depth drift, over-smoothing, vegetation boundary loss, or scale instability?
2. Should the first method be an objective change, a lightweight architecture addition, or a constrained adaptation rule?
3. Which Milestone 3 weak baseline checkpoint should represent standard adaptation in comparison tables?
4. Should Milestone 4 use first-100 validation gates first, then full val/test runs only after a clear improvement?

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

## Update Template

Date:
Changed files:
What changed:
Why:
Validation run:
Open risks:
Next step:
Note-maintenance action:
