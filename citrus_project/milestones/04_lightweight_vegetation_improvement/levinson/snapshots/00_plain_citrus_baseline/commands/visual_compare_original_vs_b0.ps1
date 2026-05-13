D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py `
  --baseline_results citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_per_sample.csv `
  --adapted_results citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/results/val_lite-mono_full_per_sample.csv `
  --baseline_weights_folder weights/lite-mono `
  --adapted_weights_folder citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/checkpoint `
  --output_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/00_plain_citrus_baseline/visual_compare_original_vs_final_val_full `
  --metric median_scaled_a1 `
  --model lite-mono
