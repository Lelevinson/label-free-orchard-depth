"""Split per-pixel test error into VEGETATION vs GROUND label pixels (no training).

Follow-up to failure_autopsy_2026-06-11.md: the panels showed all models predict a
smooth ground ramp with little lateral tree structure. This script quantifies how much
of the remaining median-scaled abs_rel sits on vegetation label pixels vs ground label
pixels, for Original Lite-Mono and S10 weights_29.

Pixel classification is a standard excess-green index on the RGB resized to label shape:
ExG = 2g - r - b (on [0,1] channels); vegetation = ExG > 0.05. Label-free, checkable.
Median scaling per image uses ALL valid pixels (same convention as the evaluator).

Usage:
  python ground_vs_vegetation_error_split.py
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
    load_lite_mono_model,
    load_npz_array,
    run_lite_mono_inference,
)

LEVINSON = REPO_ROOT / "citrus_project" / "milestones" / "04_lightweight_vegetation_improvement" / "levinson"
DATASET_WS = REPO_ROOT / "citrus_project" / "dataset_workspace"
PER_SAMPLE_CSV = (LEVINSON / "snapshots" / "10_ema_self_teacher" / "results"
                  / "weights29_test_reverify" / "test_lite-mono_full_per_sample.csv")
MODELS = {
    "original": REPO_ROOT / "weights" / "lite-mono",
    "s10_w29": LEVINSON / "snapshots" / "10_ema_self_teacher" / "checkpoint",
}
EVAL_MIN, EVAL_MAX = 0.001, 80.0
EXG_THRESHOLD = 0.05
WORST40 = {1, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 100, 101, 102, 104, 105, 106,
           243, 244, 247, 248, 249, 250, 251, 339, 342, 343, 344, 345, 348, 349, 370,
           371, 390, 391, 392, 393, 394, 395}


def resolve(rel: str) -> Path:
    for base in (DATASET_WS, DATASET_WS / "prepared_training_dataset", REPO_ROOT):
        p = base / rel
        if p.exists():
            return p
    raise FileNotFoundError(rel)


def vegetation_mask(rgb_path: Path, shape) -> np.ndarray:
    with Image.open(rgb_path) as im:
        rgb = np.asarray(
            im.convert("RGB").resize((shape[1], shape[0]), Image.BILINEAR),
            dtype=np.float64) / 255.0
    exg = 2.0 * rgb[..., 1] - rgb[..., 0] - rgb[..., 2]
    return exg > EXG_THRESHOLD


def abs_rel(pred: np.ndarray, gt: np.ndarray, mask: np.ndarray) -> float:
    if mask.sum() < 50:
        return float("nan")
    p, g = pred[mask], gt[mask]
    return float(np.mean(np.abs(p - g) / g))


def main():
    with PER_SAMPLE_CSV.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))

    models = {
        name: load_lite_mono_model(folder, "lite-mono", no_cuda=False,
                                   min_depth=0.1, max_depth=100.0)
        for name, folder in MODELS.items()
    }

    acc = {(m, grp, reg): [] for m in models for grp in ("all", "worst40", "rest")
           for reg in ("veg", "ground")}
    veg_fracs = []

    for n, row in enumerate(rows):
        idx = int(row["index"])
        rgb_path = resolve(row["rgb_rel"])
        dense = load_npz_array(resolve(row["dense_rel"])).astype(np.float64)
        valid = load_npz_array(resolve(row["valid_mask_rel"])).astype(bool)
        valid &= np.isfinite(dense) & (dense > EVAL_MIN) & (dense < EVAL_MAX)
        veg = vegetation_mask(rgb_path, dense.shape)
        veg_fracs.append(float((veg & valid).sum()) / max(1, valid.sum()))

        for name, model in models.items():
            pred, _ = run_lite_mono_inference(rgb_path, dense.shape, model, False)
            pred = np.clip(pred, EVAL_MIN, EVAL_MAX)
            scale = np.median(dense[valid]) / np.median(pred[valid])
            pred_scaled = np.clip(pred * scale, EVAL_MIN, EVAL_MAX)
            for reg, mask in (("veg", valid & veg), ("ground", valid & ~veg)):
                value = abs_rel(pred_scaled, dense, mask)
                if np.isfinite(value):
                    acc[(name, "all", reg)].append(value)
                    grp = "worst40" if idx in WORST40 else "rest"
                    acc[(name, grp, reg)].append(value)
        if (n + 1) % 100 == 0:
            print(f"  {n + 1}/{len(rows)} frames")

    print(f"\nvegetation share of labeled pixels: mean {np.mean(veg_fracs):.3f}")
    print(f"{'model':<10} {'frames':<8} {'veg abs_rel':>12} {'ground abs_rel':>15}")
    for name in models:
        for grp in ("all", "worst40", "rest"):
            v = acc[(name, grp, "veg")]
            g = acc[(name, grp, "ground")]
            print(f"{name:<10} {grp:<8} {np.mean(v):>12.4f} {np.mean(g):>15.4f}"
                  f"   (n={len(v)}/{len(g)})")


if __name__ == "__main__":
    main()
