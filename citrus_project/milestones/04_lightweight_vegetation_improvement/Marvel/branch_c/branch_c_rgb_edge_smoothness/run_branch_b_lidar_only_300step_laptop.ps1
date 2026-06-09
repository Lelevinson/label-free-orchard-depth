$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Proj\lite-Mono"
$Python = "C:\Proj\miniforge3\envs\lite-mono\python.exe"
$RunName = "branch_b_lidar_only_from_w13_b12_300step"
$LogDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs"
$RunDir = Join-Path $RepoRoot (Join-Path $LogDir $RunName)
$TrainLog = Join-Path $RunDir "console.log"
$TrainScript = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/branch_c_rgb_edge_smoothness/train_hybrid_supervised.py"
$BaseWeights = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/models/weights_13"

Set-Location $RepoRoot
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

& $Python -u $TrainScript `
  --dataset citrus `
  --split citrus_prepared `
  --data_path citrus_project/dataset_workspace `
  --model lite-mono `
  --model_name $RunName `
  --log_dir $LogDir `
  --load_weights_folder $BaseWeights `
  --models_to_load encoder depth `
  --skip_optimizer_load `
  --batch_size 12 `
  --num_epochs 2 `
  --max_train_steps 300 `
  --lr 0.0001 0.000005 31 0.0001 0.00001 31 `
  --weight_decay 0.01 `
  --drop_path 0.2 `
  --height 192 `
  --width 640 `
  --num_workers 0 `
  --log_frequency 50 `
  --save_frequency 1 `
  --save_step_frequency 100 `
  --seed 0 `
  --disable_photometric_loss `
  --disparity_smoothness 0 `
  --boundary_loss_weight 0 `
  --lidar_loss_weight 0.1 `
  --lidar_loss_type log_l1 `
  --lidar_scale_align none `
  --lidar_loss_scales 0 `
  --lidar_loss_min_valid_pixels 500 2>&1 | Tee-Object -FilePath $TrainLog
