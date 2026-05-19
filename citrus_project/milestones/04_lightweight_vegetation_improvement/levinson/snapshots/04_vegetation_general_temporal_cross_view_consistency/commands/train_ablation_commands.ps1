$PY = "D:/Conda_Envs/lite-mono/python.exe"
$LOG = "citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs"
$COMMON = @(
  "train.py",
  "--dataset", "citrus",
  "--split", "citrus_prepared",
  "--data_path", "citrus_project/dataset_workspace",
  "--model", "lite-mono",
  "--log_dir", $LOG,
  "--mypretrain", "weights/lite-mono/lite-mono-pretrain.pth",
  "--weights_init", "pretrained",
  "--batch_size", "12",
  "--num_epochs", "1",
  "--max_train_steps", "250",
  "--save_step_frequency", "250",
  "--height", "192",
  "--width", "640",
  "--num_workers", "0",
  "--log_frequency", "50",
  "--save_frequency", "1",
  "--seed", "0",
  "--temporal_geo_weight", "0.15",
  "--temporal_geo_warmup_steps", "100"
)

& $PY @COMMON --model_name "vg_tcv_geo_teacher_b12_250steps_seed0_w015" `
  --temporal_geo_consistency

& $PY @COMMON --model_name "vg_tcv_geo_visibility_teacher_b12_250steps_seed0_w015" `
  --temporal_geo_consistency `
  --visibility_aware_geo

& $PY @COMMON --model_name "vg_tcv_geo_visibility_teacher_b12_250steps_seed0_w015_vthr003" `
  --temporal_geo_consistency `
  --visibility_aware_geo `
  --visibility_cycle_threshold "0.003"

& $PY @COMMON --model_name "vg_tcv_geo_texture_teacher_b12_250steps_seed0_w015_tw035" `
  --temporal_geo_consistency `
  --texture_ambiguity_weighting `
  --texture_ambiguity_weight "0.35"

& $PY @COMMON --model_name "vg_tcv_geo_feature_teacher_b12_250steps_seed0_w015_fw005" `
  --temporal_geo_consistency `
  --feature_cross_view_consistency `
  --feature_consistency_weight "0.005" `
  --feature_consistency_warmup_steps "100"

& $PY @COMMON --model_name "vg_tcv_full_teacher_b12_250steps_seed0_w015_tw035_fw002" `
  --temporal_geo_consistency `
  --visibility_aware_geo `
  --texture_ambiguity_weighting `
  --texture_ambiguity_weight "0.35" `
  --feature_cross_view_consistency `
  --feature_consistency_weight "0.002" `
  --feature_consistency_warmup_steps "100"
