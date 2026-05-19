$weights = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_29"
$out = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full"

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py `
  --baseline_results citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_per_sample.csv `
  --adapted_results "$out/val_lite-mono_full_per_sample.csv" `
  --baseline_weights_folder weights/lite-mono `
  --adapted_weights_folder $weights `
  --output_dir "$out/visual_compare_original_vs_snapshot05_val_full" `
  --metric median_scaled_a1 `
  --model lite-mono `
  --baseline_label "Original Lite-Mono" `
  --adapted_label "Snapshot 05"

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py `
  --baseline_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/results/val_lite-mono_full_per_sample.csv `
  --adapted_results "$out/val_lite-mono_full_per_sample.csv" `
  --baseline_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/checkpoint `
  --adapted_weights_folder $weights `
  --output_dir "$out/visual_compare_b0_vs_snapshot05_val_full" `
  --metric median_scaled_a1 `
  --model lite-mono `
  --baseline_label "B0 Plain Citrus" `
  --adapted_label "Snapshot 05"

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py `
  --run_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full `
  --weights_folder $weights `
  --output_dir "$out/teacher_structure_diagnostic_maps" `
  --sample_indices 94 521 20 196
