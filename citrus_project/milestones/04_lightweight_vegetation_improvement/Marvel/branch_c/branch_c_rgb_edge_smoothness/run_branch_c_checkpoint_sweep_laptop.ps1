$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Proj\lite-Mono"
$Python = "C:\Proj\miniforge3\envs\lite-mono\python.exe"
$RunName = "branch_c_rgb_edge_from_w13_b12_30ep_s001_laptop"
$LogDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs"
$BranchDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/branch_c/branch_c_rgb_edge_smoothness"
$ModelsDir = "$LogDir/$RunName/models"
$ResultsDir = "$BranchDir/results/$RunName"
$SweepRoot = "$ResultsDir/checkpoint_sweep"
$ValRoot = "$SweepRoot/val"
$TestRoot = "$SweepRoot/test_confirm"
$SweepLog = Join-Path $RepoRoot "$SweepRoot/checkpoint_sweep.log"
$Summarizer = "$BranchDir/summarize_checkpoint_sweep.py"

Set-Location $RepoRoot
New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot $ValRoot) | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot $TestRoot) | Out-Null

"Branch C validation sweep started $(Get-Date -Format s)" | Tee-Object -FilePath $SweepLog

foreach ($i in 0..29) {
  $Checkpoint = "weights_$i"
  $WeightsFolder = "$ModelsDir/$Checkpoint"
  $OutputDir = "$ValRoot/$Checkpoint"
  $SummaryPath = Join-Path $RepoRoot "$OutputDir/val_lite-mono_full_summary.json"

  if (Test-Path $SummaryPath) {
    "Skipping existing val summary for $Checkpoint" | Tee-Object -FilePath $SweepLog -Append
    continue
  }

  "Evaluating val $Checkpoint $(Get-Date -Format s)" | Tee-Object -FilePath $SweepLog -Append
  & $Python citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
    --split val `
    --max_samples 0 `
    --run_model `
    --summary_only `
    --progress_interval 100 `
    --weights_folder $WeightsFolder `
    --output_dir $OutputDir 2>&1 | Tee-Object -FilePath $SweepLog -Append
}

& $Python $Summarizer `
  --input_root $ValRoot `
  --split val `
  --output_csv "$SweepRoot/val_sweep_summary.csv" `
  --output_json "$SweepRoot/val_sweep_summary.json" 2>&1 | Tee-Object -FilePath $SweepLog -Append

$ValRows = Import-Csv (Join-Path $RepoRoot "$SweepRoot/val_sweep_summary.csv")
$TopRaw = $ValRows | Sort-Object { [double]$_.raw_abs_rel }, { -[double]$_.raw_a1 } | Select-Object -First 3
$TopMedian = $ValRows | Sort-Object { [double]$_.median_abs_rel }, { -[double]$_.median_a1 } | Select-Object -First 3
$TestCheckpoints = @()
$TestCheckpoints += $TopRaw.checkpoint
$TestCheckpoints += $TopMedian.checkpoint
$TestCheckpoints += "weights_29"
$TestCheckpoints = $TestCheckpoints | Sort-Object -Unique

"Test-confirm checkpoints: $($TestCheckpoints -join ', ')" | Tee-Object -FilePath $SweepLog -Append

foreach ($Checkpoint in $TestCheckpoints) {
  $WeightsFolder = "$ModelsDir/$Checkpoint"
  $OutputDir = "$TestRoot/$Checkpoint"
  $SummaryPath = Join-Path $RepoRoot "$OutputDir/test_lite-mono_full_summary.json"

  if (Test-Path $SummaryPath) {
    "Skipping existing test summary for $Checkpoint" | Tee-Object -FilePath $SweepLog -Append
    continue
  }

  "Evaluating test $Checkpoint $(Get-Date -Format s)" | Tee-Object -FilePath $SweepLog -Append
  & $Python citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
    --split test `
    --max_samples 0 `
    --run_model `
    --summary_only `
    --progress_interval 100 `
    --weights_folder $WeightsFolder `
    --output_dir $OutputDir 2>&1 | Tee-Object -FilePath $SweepLog -Append
}

& $Python $Summarizer `
  --input_root $TestRoot `
  --split test `
  --output_csv "$SweepRoot/test_confirm_summary.csv" `
  --output_json "$SweepRoot/test_confirm_summary.json" 2>&1 | Tee-Object -FilePath $SweepLog -Append

"Branch C checkpoint sweep finished $(Get-Date -Format s)" | Tee-Object -FilePath $SweepLog -Append
