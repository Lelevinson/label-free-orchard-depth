# Dataset Workspace

This folder contains the Citrus-specific dataset pipeline and the local Citrus dataset workspace.

## What Lives Here

- download scripts
- extraction scripts
- audit/projection scripts
- densification/build scripts
- local dataset folders such as extracted RGB, extracted LiDAR, calibration, ground truth, and audit outputs

## Read Map

For dataset work, read this file first, then open only the script or research note matching the task.

- Build or rebuild the prepared dataset: `build_training_dataset.py`
- Audit RGB/LiDAR projection alignment: `audit_projection_alignment.py`
- Understand label-route decisions and quality evidence: `citrus_project/research/dataset_notes.md`
- Check current dataset status and canonical artifact paths: repo-root `AGENTS.md`

The local extracted data folders can be large. Do not inspect generated outputs unless the task needs a specific artifact.

## Path Behavior

The main pipeline scripts in this folder are meant to work relative to this workspace.

- `build_training_dataset.py` and `audit_projection_alignment.py` already resolve defaults from this folder
- the download/extract helper scripts were adjusted so relative paths resolve from this folder too

## Main Pipeline Order

1. `download_citrusfarm_seq_01_lidar.py`
2. `download_citrusfarm_seq_01_rgb_depth.py`
3. `extract_left_rgbd_from_raw.py`
4. `extract_lidar_from_raw.py`
5. `audit_projection_alignment.py`
6. `densify_lidar.py`
7. `build_training_dataset.py`
