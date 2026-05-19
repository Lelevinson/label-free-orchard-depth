$PY = "D:/Conda_Envs/lite-mono/python.exe"
$EVAL = "citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py"
$BASE = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs"
$RUNS = @(
  "vg_tcv_geo_teacher_b12_250steps_seed0_w015",
  "vg_tcv_geo_visibility_teacher_b12_250steps_seed0_w015",
  "vg_tcv_geo_visibility_teacher_b12_250steps_seed0_w015_vthr003",
  "vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035",
  "vg_tcv_geo_feature_teacher_b12_250steps_seed0_w015_fw005",
  "vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002"
)

foreach ($RUN in $RUNS) {
  & $PY $EVAL `
    --split val `
    --max_samples 100 `
    --run_model `
    --summary_only `
    --progress_interval 25 `
    --weights_folder "$BASE/$RUN/models/step_250" `
    --model lite-mono `
    --output_dir "$BASE/$RUN/eval_val100_step_250"
}
