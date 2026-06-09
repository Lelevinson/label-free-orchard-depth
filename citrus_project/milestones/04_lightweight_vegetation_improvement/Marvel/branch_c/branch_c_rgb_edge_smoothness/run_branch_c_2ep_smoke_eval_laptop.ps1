$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Proj\lite-Mono"
$Python = "C:\Proj\miniforge3\envs\lite-mono\python.exe"
$RunName = "branch_c_rgb_edge_from_w13_b12_2ep_s001_laptop_v2"
$LogDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs"
$BranchDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/branch_c_rgb_edge_smoothness"
$RunDir = Join-Path $RepoRoot (Join-Path $LogDir $RunName)
$ResultsDir = "$BranchDir/results/$RunName"
$VisualDir = "$ResultsDir/visuals"
$TrainLog = Join-Path $RunDir "console.log"
$PostprocessLog = Join-Path $RunDir "postprocess.log"
$TrainScript = "$BranchDir/train_hybrid_supervised.py"
$BaseWeights = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/hybrid_supervised_b12_30ep_logl1_abs_w01_fresh_sched/models/weights_13"
$WeightsFolder = "$LogDir/$RunName/models/weights_1"

Set-Location $RepoRoot
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot $ResultsDir) | Out-Null

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
  --disparity_smoothness 0.001 `
  --boundary_loss_weight 0 `
  --lidar_loss_weight 0.1 `
  --lidar_loss_type log_l1 `
  --lidar_scale_align none `
  --lidar_loss_scales 0 `
  --lidar_loss_min_valid_pixels 500 2>&1 | Tee-Object -FilePath $TrainLog

if (-not (Test-Path (Join-Path $RepoRoot $WeightsFolder))) {
  throw "Expected 2-epoch checkpoint was not found: $WeightsFolder"
}

& $Python citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/plot_training_losses.py `
  --run_dir "$LogDir/$RunName" `
  --output_dir "$ResultsDir/loss_plots" 2>&1 | Tee-Object -FilePath $PostprocessLog

& $Python citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split val `
  --max_samples 0 `
  --run_model `
  --summary_only `
  --progress_interval 50 `
  --weights_folder $WeightsFolder `
  --output_dir $ResultsDir 2>&1 | Tee-Object -FilePath $PostprocessLog -Append

& $Python citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split test `
  --max_samples 0 `
  --run_model `
  --summary_only `
  --progress_interval 50 `
  --weights_folder $WeightsFolder `
  --output_dir $ResultsDir 2>&1 | Tee-Object -FilePath $PostprocessLog -Append

& $Python citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/compare_phase2_visuals.py `
  --split val `
  --phase2_results_dir $ResultsDir `
  --phase2_weights $WeightsFolder `
  --output_dir "$VisualDir/baseline_vs_branch_c_val" `
  --baseline_name "Plain Citrus" `
  --phase2_name "Branch C 2ep" 2>&1 | Tee-Object -FilePath $PostprocessLog -Append

& $Python citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/compare_phase2_visuals.py `
  --split test `
  --phase2_results_dir $ResultsDir `
  --phase2_weights $WeightsFolder `
  --output_dir "$VisualDir/baseline_vs_branch_c_test" `
  --baseline_name "Plain Citrus" `
  --phase2_name "Branch C 2ep" 2>&1 | Tee-Object -FilePath $PostprocessLog -Append
