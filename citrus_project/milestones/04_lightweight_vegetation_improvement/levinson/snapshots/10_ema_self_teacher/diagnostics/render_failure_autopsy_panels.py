"""Render depth-comparison panels for the 2026-06-11 failure autopsy.

For chosen test-frame indices, runs original Lite-Mono, S07 (weights_25) and
S10 (weights_29) on the RGB frame and renders:
  RGB | dense LiDAR label (valid pixels only) | original disp | S07 disp | S10 disp

Purpose: visually confirm the autopsy hypothesis that the remaining shared
abs_rel failures in open-clearing frames come from mis-sloped NEAR-ground
geometry (see failure_autopsy_2026-06-11.md). Output goes to the snapshot's
ignored local_evidence/ folder (bulky-evidence policy).

Usage:
  python render_failure_autopsy_panels.py --indices 1 44 47 102 247 344 392 16 358
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[7]
EVALUATOR_DIR = REPO_ROOT / "citrus_project" / "milestones" / "01_original_lite_mono_baseline"
sys.path.insert(0, str(EVALUATOR_DIR))

from evaluate_lite_mono_citrus import (  # noqa: E402
    image_to_input_tensor,
    load_lite_mono_model,
    load_npz_array,
)

LEVINSON = REPO_ROOT / "citrus_project" / "milestones" / "04_lightweight_vegetation_improvement" / "levinson"
DATASET_WS = REPO_ROOT / "citrus_project" / "dataset_workspace"
PER_SAMPLE_CSV = (LEVINSON / "snapshots" / "10_ema_self_teacher" / "results"
                  / "weights29_test_reverify" / "test_lite-mono_full_per_sample.csv")
MODELS = {
    "Original": REPO_ROOT / "weights" / "lite-mono",
    "S07 (w25)": LEVINSON / "snapshots" / "07_structure_aware_label_free_vegetation_depth" / "checkpoint",
    "S10 (w29)": LEVINSON / "snapshots" / "10_ema_self_teacher" / "checkpoint",
}
OUT_DIR = (LEVINSON / "snapshots" / "10_ema_self_teacher" / "local_evidence"
           / "failure_autopsy_panels")


def resolve(rel: str) -> Path:
    for base in (DATASET_WS, DATASET_WS / "prepared_training_dataset", REPO_ROOT):
        p = base / rel
        if p.exists():
            return p
    raise FileNotFoundError(rel)


def predict_disp(model, rgb_path: Path) -> np.ndarray:
    import torch  # noqa: F401

    with Image.open(rgb_path) as image:
        tensor = image_to_input_tensor(image.convert("RGB"), model)
    import torch
    with torch.no_grad():
        disp = model.depth_decoder(model.encoder(tensor))[("disp", 0)]
    return disp[0, 0].cpu().numpy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--indices", type=int, nargs="+", required=True)
    args = parser.parse_args()

    with PER_SAMPLE_CSV.open(newline="", encoding="utf-8") as fp:
        rows = {int(r["index"]): r for r in csv.DictReader(fp)}

    models = {
        name: load_lite_mono_model(folder, "lite-mono", no_cuda=False,
                                   min_depth=0.1, max_depth=100.0)
        for name, folder in MODELS.items()
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for idx in args.indices:
        row = rows[idx]
        rgb_path = resolve(row["rgb_rel"])
        dense = load_npz_array(resolve(row["dense_rel"])).astype(np.float64)
        valid = load_npz_array(resolve(row["valid_mask_rel"])).astype(bool)
        gt = np.where(valid, dense, np.nan)

        n_cols = 2 + len(models)
        fig, axes = plt.subplots(1, n_cols, figsize=(4.2 * n_cols, 3.2))
        with Image.open(rgb_path) as im:
            axes[0].imshow(im.convert("RGB"))
        axes[0].set_title(
            f"frame {idx}  abs_rel={float(row['median_scaled_abs_rel']):.3f} "
            f"a1={float(row['median_scaled_a1']):.3f}", fontsize=9)

        finite = gt[np.isfinite(gt)]
        vmax = np.percentile(finite, 95) if finite.size else 1.0
        im1 = axes[1].imshow(gt, cmap="magma_r", vmin=0, vmax=vmax)
        axes[1].set_title("LiDAR dense label (valid only, m)", fontsize=9)
        fig.colorbar(im1, ax=axes[1], fraction=0.04)

        for ax, (name, model) in zip(axes[2:], models.items()):
            disp = predict_disp(model, rgb_path)
            lo, hi = np.percentile(disp, 2), np.percentile(disp, 98)
            ax.imshow(disp, cmap="magma", vmin=lo, vmax=hi)
            ax.set_title(f"{name} disparity (near=bright)", fontsize=9)

        for ax in axes:
            ax.axis("off")
        fig.tight_layout()
        out = OUT_DIR / f"frame_{idx:04d}_panel.png"
        fig.savefig(out, dpi=110)
        plt.close(fig)
        print("saved", out)


if __name__ == "__main__":
    main()
