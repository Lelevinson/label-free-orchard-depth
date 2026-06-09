$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Proj\lite-Mono"
$PythonRunner = "C:\Proj\miniforge3\condabin\mamba.bat"
$RunName = "phase2_boundary_loss_b12_30ep_w02"
$RunDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/$RunName"
$WeightsFolder = "$RunDir/models/weights_29"
$ResultsDir = "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/results/$RunName"
$VisualDir = "$ResultsDir/visuals"

Set-Location $RepoRoot

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/plot_training_losses.py `
  --run_dir $RunDir `
  --output_dir "$ResultsDir/loss_plots"

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split val `
  --max_samples 0 `
  --run_model `
  --summary_only `
  --progress_interval 50 `
  --weights_folder $WeightsFolder `
  --output_dir $ResultsDir

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split test `
  --max_samples 0 `
  --run_model `
  --summary_only `
  --progress_interval 50 `
  --weights_folder $WeightsFolder `
  --output_dir $ResultsDir

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/01_original_lite_mono_baseline/analyze_lite_mono_citrus_results.py `
  --split val `
  --results_dir $ResultsDir `
  --weights_folder $WeightsFolder `
  --output_dir "$VisualDir/single_model_val"

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/01_original_lite_mono_baseline/analyze_lite_mono_citrus_results.py `
  --split test `
  --results_dir $ResultsDir `
  --weights_folder $WeightsFolder `
  --output_dir "$VisualDir/single_model_test"

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/compare_phase2_visuals.py `
  --split val `
  --phase2_results_dir $ResultsDir `
  --phase2_weights $WeightsFolder `
  --output_dir "$VisualDir/baseline_vs_phase2_val" `
  --baseline_name "Plain Citrus" `
  --phase2_name "Phase 2 boundary"

& $PythonRunner run -n lite-mono python `
  citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/compare_phase2_visuals.py `
  --split test `
  --phase2_results_dir $ResultsDir `
  --phase2_weights $WeightsFolder `
  --output_dir "$VisualDir/baseline_vs_phase2_test" `
  --baseline_name "Plain Citrus" `
  --phase2_name "Phase 2 boundary"
