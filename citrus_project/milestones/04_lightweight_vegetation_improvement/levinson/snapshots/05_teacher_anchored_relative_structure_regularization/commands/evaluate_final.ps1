$weights = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_29"
$out = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full"

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split val `
  --max_samples 0 `
  --run_model `
  --summary_only `
  --progress_interval 50 `
  --weights_folder $weights `
  --model lite-mono `
  --output_dir $out

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split test `
  --max_samples 0 `
  --run_model `
  --summary_only `
  --progress_interval 50 `
  --weights_folder $weights `
  --model lite-mono `
  --output_dir $out

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py `
  --split val `
  --max_samples 100 `
  --run_model `
  --summary_only `
  --progress_interval 25 `
  --weights_folder $weights `
  --model lite-mono `
  --output_dir $out
