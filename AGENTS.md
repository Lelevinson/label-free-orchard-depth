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

Update policy:

1. Update `AGENTS.md` when project status, defaults, commands, paths, or research decisions change.
2. Update `student_qna.md` when a recurring beginner confusion is explained in a stable way.
3. Update `dataset_notes.md` for dataset quality or label-generation evidence.
4. Update `baseline_notes.md` for model behavior or comparison evidence.
5. Update `paper_shortlist.md` for results likely to support the paper.
6. Update `advisor_notes.md` for advisor questions or recommendations.
7. Update the relevant milestone README when milestone status, handoff guidance, or evidence ownership changes.
8. For Milestone 4 branch folders, put the main branch report at the branch-folder root with a `00_BRANCH_*_REPORT.md` filename so it is the first thing visible when the folder is opened.

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

Current local source-of-truth folder:

1. Treat `C:/Proj/lite-Mono` as the main local Windows project folder for future work.
2. Do not update the older `c:/Users/user/Documents/brgkuliah/sem6/ai apps/plantdepths/Lite-Mono-Main` copy; the user plans to delete it.
3. Do not write to `C:/Proj/lite-mono-citrus-lab-transfer` unless the user explicitly asks for transfer-repo changes.

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
   - `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/` for Levinson's current Milestone 4 results/progress.
   - `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/` for Marvel's active hybrid-supervised and RGB-edge Milestone 4 work.
7. The current B0 plain Citrus baseline snapshot is `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/`; it contains inference weights, a no-code-changes marker, command scripts, copied val/test result CSV/JSON files, copied visual comparison panels, and copied `config/opt.json`.
8. Future Levinson improvement code snapshots should live under `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/` once an improvement is implemented and tested.
9. Use descriptive numeric future snapshot names such as `01_photometric_confidence_masking/` and `02_confidence_masking_plus_structure_loss/`; record paper-style labels such as `A` or `A+B` inside the stage README only if useful.
10. Each completed improvement-stage snapshot should include one compact `README.md`, copies of changed code files when the stage is tested, optional small command/config/patch notes, and pointers to checkpoints, results, visuals, metric summary, and continue/stop/uncertain conclusion.
11. Whenever a Milestone 4 improvement changes `.py` files such as `trainer.py`, `options.py`, `layers.py`, `networks/*.py`, or helper scripts, duplicate the tested versions into the relevant stage snapshot under `code/`, preserving clear relative paths when useful. If a completed stage has no code changes, keep a simple marker such as `code/NO_CODE_CHANGES.txt`.
12. Milestone 4 collaborators should keep work inside their own workstream folder, update the shared Milestone 4 README when paths or collaboration rules change, and avoid editing another person's snapshots without explicit coordination.

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

## Reconstructed Late Milestone 4 Context

This section was rebuilt from chat/action history and the 2026-06-04 recovery backup after a duplicate-folder context-file mistake. It is not guaranteed to be byte-for-byte identical to the lost uncommitted notes, but it captures the project decisions needed going forward.

Phase/order decisions:

1. Milestone 4 originally had two planned method phases: Phase 1 occlusion masking and Phase 2 boundary-aware loss.
2. The user chose to start with Phase 2/boundary awareness first, before implementing Phase 1 occlusion masking.
3. The early direct boundary-loss/self-supervised direction was treated cautiously because photometric loss could improve while depth metrics did not reliably improve.
4. The project then pivoted toward hybrid supervised training with dense LiDAR labels as a training-only teacher while preserving RGB-only inference.

Hybrid supervised method status:

1. Hybrid training arrangement: RGB frames go into Lite-Mono; dense LiDAR depth and valid masks are separate supervision tensors used only during training.
2. The selected hybrid recipe uses pretrained Lite-Mono initialization, batch size 12, masked log-L1 LiDAR depth loss, LiDAR loss weight 0.1, no LiDAR scale alignment, and scale-0 LiDAR supervision.
3. The previous 30-epoch hybrid run `hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched` was checkpoint-scanned; `weights_13` beat final `weights_29` on validation and top-candidate test confirmation.
4. Selected `weights_13` metrics: validation raw abs_rel/a1=`0.1716`/`0.8131`, validation median-scaled abs_rel/a1=`0.1746`/`0.8160`; test raw abs_rel/a1=`0.1620`/`0.8149`, test median-scaled abs_rel/a1=`0.1677`/`0.8159`.
5. Lesson: never assume the final epoch is best; checkpoint sweep is required before claiming a 30-epoch result.
6. Direct visual comparisons support `weights_13` on typical/good selected samples, while some bad selected samples still favor `weights_29`.

Presentation/package status:

1. A progress-presentation package for the 2026-05-26 presentation exists under `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/presentation_2026_05_26_hybrid_progress/`.
2. It includes slide bullets/script, metric graphs, checkpoint-sweep graphs, selected Plain Citrus versus Hybrid `weights_13` panels, epoch-29-versus-epoch-13 panels, and a LiDAR-aware edge-loss roadmap.
3. The script explains why the project moved from pure self-supervised training to hybrid supervised training: vegetation texture, shadows, occlusions, and weak absolute-scale control made RGB photometric loss unreliable, while masked LiDAR supervision stabilizes scale during training only.
4. `graph_metric_summary_table.png` was simplified to median-scaled validation/test rows only for presentation clarity.
5. `PRESENTATION_6_MIN_SCRIPT.md` and `PRESENTATION_6_MIN_SCRIPT_GOOGLE_DOCS.docx` were created for a compact presentation delivery.

Lab-transfer and current lab-run status:

1. `LAB_COMPUTER_SETUP.md` documents the lab-computer transfer workflow, tmux usage, environment setup, dataset preparation order, and the reminder not to commit datasets/weights/runs.
2. The clean transfer repo was prepared to include project code/docs/READMEs/AGENTS while excluding local datasets, weights, caches, checkpoints, runs, results, snapshots, and log files.
3. The initial transfer missed full `Marvel/hybrid_supervised_draft` code; it was later patched to include `train_hybrid_supervised.py`, milestone-local `trainer.py`, `options.py`, `layers.py`, and hybrid run/postprocess scripts. The pretrain weight remains intentionally separate.
4. Lab prepared dataset build completed with 4918 total samples under `~/lite-mono-citrus-lab-transfer`: train=3947, val=564, test=407; trainer later reports 3911 train and 560 validation items after temporal-neighbor filtering.
5. Lab half-epoch gate (`--max_train_steps=164`) trained cleanly on CUDA and evaluated successfully. Test raw abs_rel/a1=`0.2588`/`0.5573`; test median-scaled abs_rel/a1=`0.2462`/`0.6609`.
6. The valid focused lab 30-epoch archive was later received under `C:/Proj/lite-Mono/citrus_project/dataset_workspace/labresults/hybrid_30ep_minimal/`; it contains all 30 encoder/depth checkpoints plus scalar logs and `opt.json`.
7. Full validation checkpoint sweep outputs were copied under `C:/Proj/lite-Mono/citrus_project/dataset_workspace/labresults/val/val/`. Validation selects `weights_9`, not final `weights_29`: `weights_9` val raw abs_rel/a1=`0.1765`/`0.8083`, median-scaled abs_rel/a1=`0.1832`/`0.8032`; `weights_29` val raw abs_rel/a1=`0.1945`/`0.7969`, median-scaled abs_rel/a1=`0.1963`/`0.7842`.
8. Lab test confirmation outputs were copied under `C:/Proj/lite-Mono/citrus_project/dataset_workspace/labresults/hybrid_lab_30epoch_b12_w01_logl1_fresh_test_/`. On test, `weights_9` wins raw/median abs_rel and median a1: raw abs_rel/a1=`0.1648`/`0.8108`, median abs_rel/a1=`0.1755`/`0.8051`. Final `weights_29` has slightly higher raw a1 and lower RMSE: raw abs_rel/a1=`0.1767`/`0.8134`, median abs_rel/a1=`0.1809`/`0.7979`. Current interpretation: lab `weights_9` is the validation-selected confirmed checkpoint, but earlier local Hybrid `weights_13` remains slightly stronger overall.
9. Future two-model visual comparisons should use same-image side-by-side panels, not separately selected good/typical/bad panels. Added `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/compare_two_checkpoints_raw_and_scaled.py` for this purpose; it renders RGB, LiDAR label, valid mask, both raw predictions, both median-scaled predictions, scaled error maps, and delta maps for the same selected samples. On 2026-06-08 it was patched to run locally without `torchvision`/`timm` by directly loading Lite-Mono files and using a small local `timm.models.layers` shim.
10. Local same-image raw-plus-scaled comparison panels for lab `weights_9` versus `weights_29` were generated under `C:/Proj/lite-Mono/citrus_project/dataset_workspace/labresults/raw_scaled_same_image_compare/`. Visual finding: `weights_29` often has a more plausible full-frame sky/far-background prior, but `weights_9` still wins more of the LiDAR-valid relative-depth metrics; this confirms that LiDAR-masked metrics and full-frame visual plausibility can disagree.

Next method direction:

1. Before starting LiDAR-aware edge-loss training, compare visual panels and practical availability for lab `weights_9`, lab `weights_29`, and the earlier selected hybrid `weights_13`; do not select by test alone.
2. The next planned method direction has shifted from pure LiDAR-aware edge loss toward `RGB-edge + LiDAR + prior-distillation` hybrid training, because LiDAR labels anchor metric depth but do not consistently trace clean vegetation boundaries, while RGB provides clearer boundary cues and teacher/prior preservation can protect unlabelled sky/background regions.
3. Keep the method goal narrow: improve boundary/structure behavior in vegetation while keeping inference RGB-only and lightweight.
4. Treat LiDAR depth-change/edge cues carefully: dense LiDAR labels do not draw clean plant outlines everywhere, so edge supervision should use valid masks/confidence and should not force unsupported edges.
5. For model-to-model qualitative comparison, use the same input indices for both models and include raw depth as well as median-scaled depth. Raw full-frame maps expose visual priors such as sky/far-background behavior that LiDAR-masked metrics may ignore.
6. New plan file: `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/rgb_edge_prior_distillation_experiment/PLAN.md`. It proposes staged ablations: LiDAR-only continued-training control, RGB edge-aware smoothness only, teacher prior outside LiDAR mask only, then the combined objective. The plan explicitly classifies this as supervised/hybrid training, not a pure self-supervised/unsupervised development path. After external critique on 2026-06-09, the teacher prior is treated as a risky candidate ablation, not as ground truth; the plan now requires per-loss active-pixel normalization, raw and scale-aligned teacher-prior variants, and fixed visual sanity/rejection checks.
7. Active first execution pass: raw teacher Branch D is deferred/removed for now. Prepare and test Branch B (`LiDAR-only continued training`) and Branch C (`LiDAR + RGB edge-aware smoothness`) first. Branch C code prep lives under `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/branch_c_rgb_edge_smoothness/`.
8. Branch C prep status on 2026-06-09: `--disable_photometric_loss` now also skips pose/reprojection work, `--skip_optimizer_load` lets `weights_13` initialize encoder/depth without inheriting old Adam state, and laptop 300-step Branch B/C pilot scripts are available in the Branch C folder.

Later milestones:

1. Milestone 5: optional supervised or hybrid training with dense LiDAR labels, unless Milestone 4 continues to own the hybrid-supervised branch for the paper contribution.
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

1. Treat `C:/Proj/lite-Mono` as the working source-of-truth folder; do not update the older sem6 copy or the lab-transfer repo unless explicitly asked.
2. Use the earlier local Hybrid `weights_13` as the preferred Branch B/C starting checkpoint when available; use lab `weights_9` only as the lab-machine fallback if the earlier checkpoint is unavailable.
3. Treat Branch C `weights_24` as the recommended checkpoint to carry forward for metric-depth reporting, while recording `weights_22` as the strict validation-raw winner and `weights_29` as the strong final-epoch comparison.
4. Keep professor-facing names descriptive and keep internal run-folder names in technical mappings.
5. Do not delete generated evidence or checkpoints unless the user explicitly approves a specific cleanup list.

Milestone 4 planning questions:

1. Did the lab 30-epoch hybrid run reproduce, beat, or underperform the earlier selected Hybrid `weights_13` result?
2. Should the LiDAR-aware edge-loss experiment start from the selected hybrid checkpoint or from pretrained Lite-Mono initialization?
3. What edge target is safest: LiDAR depth-gradient edges, RGB-image edges gated by LiDAR validity, or a confidence-weighted blend?
4. How should we report cases where metrics improve but visual panels look only subtly better than Plain Citrus?

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
15. 2026-05-22: Completed the Milestone 4 hybrid supervised checkpoint scan for `hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched`; `weights_13` beat final `weights_29` on validation and top-candidate test confirmation, so `weights_13` is the selected hybrid checkpoint for comparison and future LiDAR-aware edge-loss planning.
16. 2026-05-25: Prepared the 2026-05-26 progress-presentation package with slide bullets/script, metric graphs, checkpoint-sweep plots, Plain Citrus versus Hybrid `weights_13` panels, and the next LiDAR-aware edge-loss roadmap; the script explains the switch from pure self-supervised training to masked LiDAR-supervised hybrid training.
17. 2026-06-02: Prepared the lab-computer transfer workflow and clean GitHub-transfer repo, excluding datasets, weights, caches, checkpoints, runs, results, snapshots, and log files from source control.
18. 2026-06-03: Lab prepared dataset build completed under `~/lite-mono-citrus-lab-transfer` with `build_training_dataset.py --workers 8`: 4918 RGB-LiDAR samples, split counts train=3947, val=564, test=407, final/default transform `exact_lidar_parent_child_inverted`.
19. 2026-06-03: Lab half-epoch hybrid supervised gate completed and evaluated. Validation raw abs_rel/a1=`0.2753`/`0.5282`, validation median-scaled abs_rel/a1=`0.2610`/`0.6381`; test raw abs_rel/a1=`0.2588`/`0.5573`, test median-scaled abs_rel/a1=`0.2462`/`0.6609`. Interpretation: the short lab run strongly improves raw scale over Plain Citrus but remains behind selected Hybrid `weights_13`.
20. 2026-06-03: User launched a complete 30-epoch lab hybrid supervised run using the same recipe: batch size 12, LiDAR loss weight 0.1, log-L1 LiDAR loss, no LiDAR scale alignment, scale-0 LiDAR supervision, pretrained Lite-Mono initialization, save every epoch. Checkpoint sweep is required after completion because final epoch may not be best.
21. 2026-06-04: Inspected `C:/Proj/lite-Mono/citrus_project/dataset_workspace/labresults/marvel.zip`; the archive is damaged/incomplete and recoverable contents only show `hybrid_lab_halfepoch_b12_w01_164steps`, not the 30-epoch run. Request a new focused archive containing 30-epoch scalar logs plus `weights_*/encoder.pth` and `weights_*/depth.pth`.
22. 2026-06-04: Repaired context-file direction after duplicate-folder confusion. `C:/Proj/lite-Mono` is now the local source-of-truth folder; the older sem6 `Lite-Mono-Main` copy should not receive future updates.
23. 2026-06-06: Received and inspected the valid `hybrid_30ep_minimal` lab archive. It contains all 30 `weights_0` through `weights_29` encoder/depth checkpoints plus train/val scalar CSVs and `opt.json`. Generated scalar plots under `citrus_project/dataset_workspace/labresults/hybrid_30ep_minimal_analysis_plots/`. Scalar logs show train loss continues down to epoch 29, validation loss is lowest around epoch 16, validation scalar `abs_rel` is lowest at epoch 13, and scalar `a1` peaks around epoch 6; full val/test checkpoint sweep is still required before selecting the model.
24. 2026-06-06: Inspected the copied lab validation checkpoint sweep under citrus_project/dataset_workspace/labresults/val/val/. All 30 checkpoints were evaluated on validation. weights_9 is the current lab validation-selected checkpoint: raw abs_rel/a1=0.1765/0.8083, median-scaled abs_rel/a1=0.1832/0.8032. Final weights_29 is usable but weaker on validation: raw abs_rel/a1=0.1945/0.7969, median-scaled abs_rel/a1=0.1963/0.7842.
25. 2026-06-06: Inspected copied lab test confirmation for weights_9 and weights_29. weights_9 test raw abs_rel/a1=0.1648/0.8108 and median abs_rel/a1=0.1755/0.8051. weights_29 test raw abs_rel/a1=0.1767/0.8134 and median abs_rel/a1=0.1809/0.7979. weights_9 remains the selected lab checkpoint by validation and abs_rel; weights_29 is slightly better only on raw a1/RMSE.
26. 2026-06-06: Added `compare_two_checkpoints_raw_and_scaled.py` under Marvel to generate same-image raw plus median-scaled visual comparisons for two checkpoints. This was added after observing that LiDAR-masked metrics can prefer one checkpoint while another may look more plausible in unlabelled full-frame regions such as sky.
27. 2026-06-08: Extracted `some.zip` and `thing.zip` into `labresults/some_extracted/` and `labresults/thing_extracted/`. Generated local raw-plus-median-scaled same-image comparisons for lab `weights_9` versus `weights_29` under `labresults/raw_scaled_same_image_compare/`. The panels show `weights_29` can look more visually plausible in sky/background, while `weights_9` remains stronger on several LiDAR-valid metric regions.
28. 2026-06-08: Added `rgb_edge_prior_distillation_experiment/PLAN.md` under Marvel. The plan objectively proposes a staged next experiment combining masked LiDAR metric supervision, RGB edge-aware smoothness, and teacher/prior preservation outside the LiDAR-valid mask, with literature support and explicit risks. It now states that the experiment is supervised/hybrid, and that the expected heat-map outcome is improved full-frame sanity rather than guaranteed perfect depth.
29. 2026-06-09: Revised `rgb_edge_prior_distillation_experiment/PLAN.md` after critique. Important changes: `weights_29` is no longer framed as a strong teacher, only a candidate outside-mask prior; teacher loss must be normalized by active pixels, tested raw and scale-aligned, and compared against no-teacher controls; LiDAR-only continued training is now a required ablation; visual sanity must use a fixed image set and predefined rejection rules rather than subjective post-hoc selection.
30. 2026-06-09: Prepared local Branch C workspace by copying `hybrid_supervised_draft` to `branch_c_rgb_edge_smoothness/`, adding `--disable_photometric_loss`, and documenting Branch B/C commands in `BRANCH_C_PREP.md`. The active first-pass plan now prioritizes Branch B and Branch C, with raw teacher Branch D deferred.
31. 2026-06-09: Finished laptop Branch C prep: photometric-disabled training now skips pose/reprojection, `--skip_optimizer_load` was added for fresh optimizer state from `weights_13`, and two 300-step laptop pilot scripts were added for Branch B and Branch C under `branch_c_rgb_edge_smoothness/`.
32. 2026-06-09: Completed Branch C 2-epoch smoke and 30-epoch laptop run from earlier Hybrid `weights_13`. Final Branch C `weights_29` is the strongest result so far by final metrics: val raw abs_rel/a1=`0.1561`/`0.8668`, val median abs_rel/a1=`0.1581`/`0.8640`; test raw abs_rel/a1=`0.1399`/`0.8733`, test median abs_rel/a1=`0.1436`/`0.8675`. Visual panels and loss plots are saved under `branch_c_rgb_edge_smoothness/results/branch_c_rgb_edge_from_w13_b12_30ep_s001_laptop/`; validation checkpoint sweep remains the next selection step.
33. 2026-06-09: Completed Branch C checkpoint sweep. Validation raw `abs_rel` winner is `weights_22` with val raw abs_rel/a1=`0.1530`/`0.8664`; validation median `abs_rel` winner is `weights_24` with val median abs_rel/a1=`0.1562`/`0.8641`. Test confirmation favors `weights_24` for raw metric depth: test raw abs_rel/a1=`0.1384`/`0.8694`; final `weights_29` remains best among confirmed candidates for test median-scaled abs_rel/a1=`0.1436`/`0.8675`. Recommended checkpoint to carry forward is `weights_24`, with `weights_22` and `weights_29` retained as comparison points. Generated selected-checkpoint Plain Citrus comparison panels under `branch_c_rgb_edge_smoothness/results/branch_c_rgb_edge_from_w13_b12_30ep_s001_laptop/checkpoint_sweep/visuals/weights_24_baseline_vs_branch_c_val/` and `.../weights_24_baseline_vs_branch_c_test/`.
34. 2026-06-09: Generated same-image raw plus median-scaled comparison panels for Branch C `weights_24` versus final `weights_29` under `checkpoint_sweep/visuals/weights24_vs_weights29_val/` and `checkpoint_sweep/visuals/weights24_vs_weights29_test/`. Visual interpretation: the two checkpoints are very close; `weights_24` remains preferred for aggregate raw metric depth, while `weights_29` remains a strong final-epoch comparison.
35. 2026-06-09: Organized Branch C under `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/branch_c_rgb_edge_smoothness/`, updated references, added main-repo ignore rules for bulky local result dumps, and created a separate local backup repo at `C:/Proj/milestone-4-dump` with a committed Branch C snapshot plus copied context notes and the two-checkpoint comparison helper.
36. 2026-06-10: Added top-visible Branch C report aliases: `citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/00_BRANCH_C_REPORT.md` and `branch_c_rgb_edge_smoothness/00_BRANCH_C_TRAINING_REPORT.md`. Future branch folders should expose their main report as a `00_BRANCH_*_REPORT.md` file at the branch root.

## Update Template

Date:
Changed files:
What changed:
Why:
Validation run:
Open risks:
Next step:
Note-maintenance action:
