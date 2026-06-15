"""Re-render the qualitative comparison figures as legible DEPTH maps (not dark disparity).

For each chosen frame: RGB | LiDAR label | Original | S07 | S10 predicted depth (median-scaled
to the LiDAR per frame), all in the same magma colormap + shared colorbar — directly comparable.
Needs the GPU + dataset_workspace; reuses the milestone-01 evaluator's model loader.

Run from paper/:  D:/Conda_Envs/lite-mono/python.exe render_qual_compare.py
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[5]
EVAL_DIR = REPO / "citrus_project" / "milestones" / "01_original_lite_mono_baseline"
WORKSPACE = REPO / "citrus_project" / "dataset_workspace"
FIG = Path(__file__).resolve().parent / "figures"
LEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_DIR))
from evaluate_lite_mono_citrus import image_to_input_tensor, load_lite_mono_model, load_npz_array  # noqa: E402
from PIL import Image  # noqa: E402

MODELS = [
    ("Original Lite-Mono", REPO / "weights" / "lite-mono"),
    ("S07", LEV / "snapshots/07_structure_aware_label_free_vegetation_depth/checkpoint"),
    ("S10 (ours)", LEV / "snapshots/10_ema_self_teacher/checkpoint"),
]
# frame index -> (output filename, scene label)
FRAMES = {
    358: ("fig_qual_corridor_good.png", "In-row corridor (low error)"),
    44:  ("fig_qual_clearing_bad.png", "Open clearing (high error)"),
}
PS_CSV = LEV / "snapshots/10_ema_self_teacher/results/weights29_test_reverify/test_lite-mono_full_per_sample.csv"


def infer_depth(model, rgb_path, shape):
    import torch, torch.nn.functional as F
    with Image.open(rgb_path) as im:
        t = image_to_input_tensor(im.convert("RGB"), model)
    with torch.no_grad():
        feats = model.encoder(t)
        out = model.depth_decoder(feats)
        _, depth = model.disp_to_depth(out[("disp", 0)], model.min_depth, model.max_depth)
        depth = F.interpolate(depth, size=shape, mode="bilinear", align_corners=False)
    return depth.detach().cpu().numpy()[0, 0].astype(np.float32)


rows = {int(r["index"]): r for r in csv.DictReader(open(PS_CSV))}
loaded = [(name, load_lite_mono_model(weights_folder=wf.resolve(), model_name="lite-mono",
                                      no_cuda=False, min_depth=0.1, max_depth=100.0))
          for name, wf in MODELS]

for index, (out_name, scene) in FRAMES.items():
    r = rows[index]
    rgb_path = WORKSPACE / r["rgb_rel"]
    gt = load_npz_array(WORKSPACE / r["dense_rel"]).astype(np.float32)
    valid = load_npz_array(WORKSPACE / r["valid_mask_rel"])
    emask = (valid > 0) & np.isfinite(gt) & (gt > 0)
    gt_med = float(np.median(gt[emask]))

    preds = []
    for name, model in loaded:
        d = infer_depth(model, rgb_path, gt.shape)
        ratio = gt_med / float(np.median(d[emask]))  # per-frame median scaling, like eval
        preds.append((name, d * ratio))

    allv = np.concatenate([gt[emask]] + [p[emask] for _, p in preds])
    vmin, vmax = np.percentile(allv, 2), np.percentile(allv, 98)

    n = 2 + len(preds)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n, 3.0), constrained_layout=True)
    axes[0].imshow(Image.open(rgb_path).convert("RGB")); axes[0].set_title("RGB", fontsize=10)
    lab = np.where(emask, gt, np.nan)
    axes[1].imshow(lab, cmap="magma_r", vmin=vmin, vmax=vmax)
    axes[1].set_title("LiDAR depth (label)", fontsize=10)
    im = None
    for ax, (name, p) in zip(axes[2:], preds):
        im = ax.imshow(p, cmap="magma_r", vmin=vmin, vmax=vmax)
        ax.set_title(f"{name} depth", fontsize=10)
    for ax in axes:
        ax.axis("off")
    cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.01)
    cb.set_label("depth (m)", fontsize=9)
    fig.suptitle(f"{scene} — frame {index}, abs_rel={float(r['median_scaled_abs_rel']):.3f}, "
                 f"a1={float(r['median_scaled_a1']):.3f}", fontsize=11)
    fig.savefig(FIG / out_name, dpi=160)
    plt.close(fig)
    print(f"[ok] {out_name}  (vmin={vmin:.2f} vmax={vmax:.2f} m)")
print("done")
