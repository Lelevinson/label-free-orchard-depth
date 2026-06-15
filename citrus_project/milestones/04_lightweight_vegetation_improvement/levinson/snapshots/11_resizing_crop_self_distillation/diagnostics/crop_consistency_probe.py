"""S11 pre-build mechanism probe (inference-only, NO training).

Question: does the trained S10 model actually contradict itself between a full view and a
cropped/zoomed view of the same image? If yes (large scale-free inconsistency, correlated
with per-frame error), the planned S11 crop self-distillation loss has a real signal to
train on. If no, S11 should be killed before any training is spent.

Method per test frame:
  1. Predict depth on the full image.
  2. Crop a fixed-seed random box (linear scale 0.7), resize to feed size, predict again.
  3. Compare in SI-log space (subtract the mean log-ratio, which removes the crop-zoom
     scale ambiguity EXACTLY — same invariance the S11 training loss would use).
  4. Report mean |residual| (~= mean relative disagreement, directly comparable to abs_rel
     units) and its correlation with the frame's median-scaled abs_rel from the S10
     weights_29 re-verified test eval.

Usage: python crop_consistency_probe.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[7]
EVALUATOR_DIR = REPO_ROOT / "citrus_project" / "milestones" / "01_original_lite_mono_baseline"
sys.path.insert(0, str(EVALUATOR_DIR))

from evaluate_lite_mono_citrus import (  # noqa: E402
    image_to_input_tensor,
    load_lite_mono_model,
)

LEVINSON = REPO_ROOT / "citrus_project" / "milestones" / "04_lightweight_vegetation_improvement" / "levinson"
DATASET_WS = REPO_ROOT / "citrus_project" / "dataset_workspace"
PER_SAMPLE_CSV = (LEVINSON / "snapshots" / "10_ema_self_teacher" / "results"
                  / "weights29_test_reverify" / "test_lite-mono_full_per_sample.csv")
S10_CKPT = LEVINSON / "snapshots" / "10_ema_self_teacher" / "checkpoint"
OUT_CSV = Path(__file__).with_name("crop_consistency_per_frame.csv")
CROP_SCALE = 0.7
BORDER = 8  # px margin trimmed from the comparison to ignore resampling edge effects


def predict_depth(model, image: Image.Image) -> np.ndarray:
    import torch
    tensor = image_to_input_tensor(image, model)
    with torch.no_grad():
        disp = model.depth_decoder(model.encoder(tensor))[("disp", 0)]
        _, depth = model.disp_to_depth(disp, model.min_depth, model.max_depth)
    return depth[0, 0].cpu().numpy()


def main():
    with PER_SAMPLE_CSV.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))

    model = load_lite_mono_model(S10_CKPT, "lite-mono", no_cuda=False,
                                 min_depth=0.1, max_depth=100.0)
    rng = np.random.default_rng(0)
    results = []

    for row in rows:
        rgb_path = DATASET_WS / row["rgb_rel"]
        with Image.open(rgb_path) as im:
            image = im.convert("RGB")
        w, h = image.size
        cw, ch = int(w * CROP_SCALE), int(h * CROP_SCALE)
        x0 = int(rng.integers(0, w - cw + 1))
        y0 = int(rng.integers(0, h - ch + 1))

        d_full = predict_depth(model, image)
        d_crop = predict_depth(model, image.crop((x0, y0, x0 + cw, y0 + ch)))

        # Cut the same box out of the full-view prediction (proportional coords),
        # resize to the crop prediction's grid.
        fh, fw = d_full.shape
        fx0, fy0 = int(x0 / w * fw), int(y0 / h * fh)
        fx1, fy1 = int((x0 + cw) / w * fw), int((y0 + ch) / h * fh)
        ref = np.asarray(Image.fromarray(d_full[fy0:fy1, fx0:fx1]).resize(
            (d_crop.shape[1], d_crop.shape[0]), Image.BILINEAR))

        r = np.log(np.clip(d_crop, 1e-6, None)) - np.log(np.clip(ref, 1e-6, None))
        r = r[BORDER:-BORDER, BORDER:-BORDER]
        si_residual = float(np.mean(np.abs(r - r.mean())))
        results.append({
            "index": int(row["index"]),
            "si_inconsistency": si_residual,
            "median_scaled_abs_rel": float(row["median_scaled_abs_rel"]),
        })

    inc = np.array([r["si_inconsistency"] for r in results])
    err = np.array([r["median_scaled_abs_rel"] for r in results])
    pearson = float(np.corrcoef(inc, err)[0, 1])
    rank = lambda a: np.argsort(np.argsort(a))
    spearman = float(np.corrcoef(rank(inc), rank(err))[0, 1])

    with OUT_CSV.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    print(f"frames: {len(results)}  (crop scale {CROP_SCALE}, seed 0)")
    print(f"self-inconsistency (scale-free, ~relative units): "
          f"mean {inc.mean():.4f}  median {np.median(inc):.4f}  "
          f"p10 {np.percentile(inc, 10):.4f}  p90 {np.percentile(inc, 90):.4f}")
    print(f"correlation with per-frame abs_rel: pearson {pearson:.3f}  spearman {spearman:.3f}")
    top = np.argsort(-inc)[:40]
    worst_err = set(np.argsort(-err)[:40])
    overlap = sum(1 for i in top if i in worst_err)
    print(f"overlap between 40 most self-inconsistent and 40 worst-error frames: {overlap}/40")
    print("per-frame CSV:", OUT_CSV)


if __name__ == "__main__":
    main()
