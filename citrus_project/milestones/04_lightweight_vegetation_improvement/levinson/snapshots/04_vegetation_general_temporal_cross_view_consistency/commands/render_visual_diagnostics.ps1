$PY = "D:/Conda_Envs/lite-mono/python.exe"
$SCRIPT = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/render_temporal_cross_view_diagnostics.py"
$BASE = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs"

& $PY $SCRIPT `
  --run_dir "$BASE/vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035" `
  --weights_folder "$BASE/vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035/models/step_250" `
  --output_dir "$BASE/vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035/visual_diagnostics_val_samples" `
  --sample_indices 0 35 82 96

& $PY $SCRIPT `
  --run_dir "$BASE/vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002" `
  --weights_folder "$BASE/vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002/models/step_250" `
  --output_dir "$BASE/vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002/visual_diagnostics_val_samples" `
  --sample_indices 0 35 82 96
