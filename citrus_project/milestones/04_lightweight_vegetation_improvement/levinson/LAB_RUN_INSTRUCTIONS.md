# Lab Machine — Full TSOB Training Run Instructions

This file tells you exactly what to do on the lab machine to run the full 30-epoch
TSOB training. Read top to bottom, do each step in order.

Gate result (why we're running this): 3-epoch gate on laptop showed both metrics
improved — abs_rel improved by 0.018, a1 improved by 0.065. This is the best gate
signal of any method we've tried. Full run expected ~10-15 hours.

---

## Step 1 — Sync the code

In the repo folder on the lab machine, run:

```bash
git pull
```

This pulls all the new code (TSOB mixture loss, feature-metric loss, updated docs).
You should see files like `networks/mixture_head.py` appear.

---

## Step 2 — Get the weights (download if missing)

The training needs three weight files that are NOT in git (too large).
Check if they exist first:

```bash
ls weights/lite-mono/
```

You need ALL THREE of these:
- `weights/lite-mono/encoder.pth`              ← frozen teacher encoder
- `weights/lite-mono/depth.pth`                ← frozen teacher depth decoder
- `weights/lite-mono/lite-mono-pretrain.pth`   ← ImageNet pretrain for the student

**If missing, download them directly — no USB needed:**

```bash
# Make the folder
mkdir -p weights/lite-mono

# 1. Download the KITTI-trained model (gives encoder.pth + depth.pth inside a zip)
wget -O weights/lite-mono/lite_mono_kitti.zip \
  "https://surfdrive.surf.nl/files/index.php/s/CUjiK221EFLyXDY/download"

# Unzip — encoder.pth and depth.pth should appear inside
unzip weights/lite-mono/lite_mono_kitti.zip -d weights/lite-mono/
rm weights/lite-mono/lite_mono_kitti.zip   # clean up zip after

# 2. Download the ImageNet pretrain (single .pth file)
wget -O weights/lite-mono/lite-mono-pretrain.pth \
  "https://surfdrive.surf.nl/files/index.php/s/InMMGd5ZP2fXuia/download"
```

If `wget` is not available, use `curl` instead:
```bash
curl -L -o weights/lite-mono/lite_mono_kitti.zip \
  "https://surfdrive.surf.nl/files/index.php/s/CUjiK221EFLyXDY/download"
curl -L -o weights/lite-mono/lite-mono-pretrain.pth \
  "https://surfdrive.surf.nl/files/index.php/s/InMMGd5ZP2fXuia/download"
```

After downloading, verify all three files exist:
```bash
ls -lh weights/lite-mono/
# Should show: encoder.pth, depth.pth, lite-mono-pretrain.pth
```

Do not continue to Step 3 until all three files are confirmed present.

---

## Step 3 — Check the dataset path

The training expects the Citrus dataset here (relative to repo root):

```
citrus_project/dataset_workspace/prepared_training_dataset/
```

Check it exists and has content:

```bash
ls citrus_project/dataset_workspace/prepared_training_dataset/
```

You should see folders like `splits/`, `dense_lidar_npz/`, `dense_lidar_valid_mask_npz/`,
and files like `manifest.json`.

If the dataset is at a different path on the lab machine, add
`--data_path /your/path/here` to the training command in Step 4.

---

## Step 4 — Run the full training

**PowerShell (Windows):**

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py `
  --dataset citrus `
  --batch_size 12 `
  --num_epochs 30 `
  --num_workers 4 `
  --seed 0 `
  --weights_init pretrained `
  --mypretrain weights/lite-mono/lite-mono-pretrain.pth `
  --model_name s09_tsob_full_b12_30ep_seed0 `
  --log_dir citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs `
  --teacher_structure_regularization `
  --teacher_structure_weight 0.03 `
  --teacher_structure_warmup_steps 500 `
  --teacher_structure_decay 0.5 `
  --teacher_gradient_loss `
  --teacher_gradient_weight 0.01 `
  --teacher_ranking_loss `
  --teacher_ranking_weight 0.02 `
  --teacher_rank_samples 512 `
  --teacher_texture_ambiguity_emphasis `
  --texture_ambiguity_weight 0.25 `
  --structure_aware_teacher `
  --sky_far_structure_loss `
  --sky_far_weight 0.01 `
  --teacher_path weights/lite-mono `
  --tsob_mixture_loss `
  --tsob_weight 0.1 `
  --tsob_warmup_steps 200
```

**Linux/bash (if the lab machine runs Linux):**
Replace every backtick `` ` `` at the end of a line with a backslash `\`.
Also replace `D:/Conda_Envs/lite-mono/python.exe` with whatever Python is active
(try `which python` or `conda activate lite-mono` first).

---

## Step 5 — While it trains

Results save here automatically (one folder per epoch):

```
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/
  s09_tsob_full_b12_30ep_seed0/
    models/
      weights_0/    ← after epoch 1
      weights_1/    ← after epoch 2
      ...
      weights_29/   ← after epoch 30  (this is the final one)
```

Expected runtime: ~10-15 hours on a laptop GPU; faster on a better lab GPU (maybe 4-6h).
Batch size stays at 12 regardless of GPU power — keeps results comparable to all previous snapshots.

You can check progress anytime:
```bash
ls citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/s09_tsob_full_b12_30ep_seed0/models/
```
Count the `weights_*` folders — each one = one completed epoch.

---

## Step 6 — When it finishes

Commit and push the results back so the laptop can see them:

```bash
# The runs/ folder is git-ignored (too large), so just let me know it's done.
# Bring the results back via: copy the whole run folder to the laptop,
# OR just note which weights_N folders exist and their final training loss.
```

Actually the simplest thing: just message/tell me it's done and I'll guide you
through the checkpoint selection and evaluation from there.

---

## If something goes wrong

Common issues:

**"CUDA out of memory"** → reduce `--batch_size` from 12 to 10 and retry.
The 3-epoch gate ran fine at batch 10 on the laptop (7.3 GB VRAM).

**"No module named citrus_prepared_dataset"** → you're not running from the
repo root. Make sure you `cd` into the repo folder first before running.

**"FileNotFoundError: weights/lite-mono/..."** → weights are missing, go back
to Step 2.

**Training loss is NaN from the start** → check that the teacher weights loaded
correctly; the frozen teacher needs both `encoder.pth` and `depth.pth`.
