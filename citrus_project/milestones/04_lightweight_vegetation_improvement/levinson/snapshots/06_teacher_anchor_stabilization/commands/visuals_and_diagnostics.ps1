D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py `
  --baseline_results citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_per_sample.csv `
  --adapted_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/val_lite-mono_full_per_sample.csv `
  --baseline_weights_folder weights/lite-mono `
  --adapted_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29 `
  --output_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/visual_compare_original_vs_snapshot06_val_full `
  --metric median_scaled_a1 `
  --baseline_label Original `
  --adapted_label Snapshot06 `
  --model lite-mono

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py `
  --baseline_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/results/val_lite-mono_full_per_sample.csv `
  --adapted_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/val_lite-mono_full_per_sample.csv `
  --baseline_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/checkpoint `
  --adapted_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29 `
  --output_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/visual_compare_b0_vs_snapshot06_val_full `
  --metric median_scaled_a1 `
  --baseline_label B0 `
  --adapted_label Snapshot06 `
  --model lite-mono

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py `
  --baseline_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/final_weights29_evaluation_full/val_lite-mono_full_per_sample.csv `
  --adapted_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/val_lite-mono_full_per_sample.csv `
  --baseline_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_29 `
  --adapted_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29 `
  --output_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/visual_compare_snapshot05_vs_snapshot06_val_full `
  --metric median_scaled_a1 `
  --baseline_label Snapshot05 `
  --adapted_label Snapshot06 `
  --model lite-mono

D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_teacher_structure_diagnostics.py `
  --run_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture `
  --weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29 `
  --output_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/teacher_structure_diagnostic_maps `
  --sample_indices 95 2 21 175 171 394 196
