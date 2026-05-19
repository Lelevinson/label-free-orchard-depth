from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[7]
EVALUATOR_DIR = (
    REPO_ROOT / "citrus_project" / "milestones" / "01_original_lite_mono_baseline"
)
if str(EVALUATOR_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATOR_DIR))

from evaluate_lite_mono_citrus import (  # noqa: E402
    image_to_input_tensor,
    load_lite_mono_model,
    load_npz_array,
)


MODEL_ORDER = ["original", "b0", "w19", "w29"]
MODEL_LABELS = {
    "original": "Original Lite-Mono",
    "b0": "B0 Plain Citrus",
    "w19": "Snapshot 05 weights_19",
    "w29": "Snapshot 05 weights_29",
}


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def safe_float(value: object, default: float = float("nan")) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_percentile(values: np.ndarray, percentile: float, fallback: float) -> float:
    finite = np.asarray(values, dtype=np.float32)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return fallback
    value = float(np.percentile(finite, percentile))
    return value if np.isfinite(value) else fallback


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("_") or "sample"


def load_rows_by_rgb(paths: Dict[str, Path]) -> Dict[str, Dict[str, Dict[str, str]]]:
    result: Dict[str, Dict[str, Dict[str, str]]] = {}
    for model_key, path in paths.items():
        result[model_key] = {row["rgb_rel"]: row for row in read_csv_rows(path)}
    return result


def model_metrics(row: Dict[str, str] | None) -> Dict[str, float]:
    if row is None:
        return {
            "median_scaled_abs_rel": float("nan"),
            "median_scaled_a1": float("nan"),
            "scale_ratio": float("nan"),
        }
    return {
        "median_scaled_abs_rel": safe_float(row.get("median_scaled_abs_rel")),
        "median_scaled_a1": safe_float(row.get("median_scaled_a1")),
        "scale_ratio": safe_float(row.get("scale_ratio")),
    }


def metric_text(metrics: Dict[str, float]) -> str:
    return (
        f"AbsRel={metrics['median_scaled_abs_rel']:.3f}, "
        f"a1={metrics['median_scaled_a1']:.3f}"
    )


def run_depth_and_disparity(rgb_path: Path, dense_shape: Tuple[int, int], model):
    import torch
    import torch.nn.functional as F

    with Image.open(rgb_path) as image:
        input_image = image.convert("RGB")
        input_tensor = image_to_input_tensor(input_image, model)

    with torch.no_grad():
        features = model.encoder(input_tensor)
        outputs = model.depth_decoder(features)
        raw_disp = outputs[("disp", 0)]
        scaled_disp, depth = model.disp_to_depth(raw_disp, model.min_depth, model.max_depth)
        raw_disp_resized = F.interpolate(
            raw_disp, size=dense_shape, mode="bilinear", align_corners=False
        )
        scaled_disp_resized = F.interpolate(
            scaled_disp, size=dense_shape, mode="bilinear", align_corners=False
        )
        depth_resized = F.interpolate(
            depth, size=dense_shape, mode="bilinear", align_corners=False
        )

    return {
        "raw_depth": depth_resized.detach().cpu().numpy()[0, 0].astype(np.float32),
        "raw_disp": raw_disp_resized.detach().cpu().numpy()[0, 0].astype(np.float32),
        "scaled_disp": scaled_disp_resized.detach().cpu().numpy()[0, 0].astype(np.float32),
    }


def scaled_depth(raw_depth: np.ndarray, row: Dict[str, str] | None) -> np.ndarray:
    scale = safe_float(row.get("scale_ratio")) if row is not None else float("nan")
    if not np.isfinite(scale):
        return np.full_like(raw_depth, np.nan, dtype=np.float32)
    return (raw_depth * scale).astype(np.float32)


def absrel_error(pred_scaled: np.ndarray, dense: np.ndarray, eval_mask: np.ndarray) -> np.ndarray:
    error = np.full(dense.shape, np.nan, dtype=np.float32)
    denom = np.maximum(dense[eval_mask], 1e-6)
    error[eval_mask] = np.abs(pred_scaled[eval_mask] - dense[eval_mask]) / denom
    return error


def crop_box(mask: np.ndarray, pad: int = 48) -> Tuple[slice, slice]:
    ys, xs = np.where(mask)
    if ys.size == 0 or xs.size == 0:
        return slice(0, mask.shape[0]), slice(0, mask.shape[1])
    y0 = max(int(ys.min()) - pad, 0)
    y1 = min(int(ys.max()) + pad + 1, mask.shape[0])
    x0 = max(int(xs.min()) - pad, 0)
    x1 = min(int(xs.max()) + pad + 1, mask.shape[1])
    return slice(y0, y1), slice(x0, x1)


def save_array_png(path: Path, array: np.ndarray, cmap: str, vmin=None, vmax=None) -> None:
    values = np.asarray(array, dtype=np.float32)
    if vmin is None:
        vmin = safe_percentile(values, 2, 0.0)
    if vmax is None:
        vmax = safe_percentile(values, 98, 1.0)
    if vmax <= vmin:
        vmax = vmin + 1.0
    plt.imsave(path, values, cmap=cmap, vmin=vmin, vmax=vmax)


def axis_image(ax, image, title: str, cmap=None, vmin=None, vmax=None):
    im = ax.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=9)
    ax.axis("off")
    return im


def maybe_colorbar(fig, im, ax):
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def render_full_image_panel(
    output_path: Path,
    rgb: Image.Image,
    dense: np.ndarray,
    eval_mask: np.ndarray,
    predictions: Dict[str, Dict[str, np.ndarray]],
    metrics: Dict[str, Dict[str, float]],
    title: str,
) -> None:
    label_display = np.where(eval_mask, dense, np.nan)
    depth_values = [label_display[np.isfinite(label_display)]]
    for key in MODEL_ORDER:
        depth_values.append(predictions[key]["scaled_depth"][np.isfinite(predictions[key]["scaled_depth"])])
    depth_values = np.concatenate([v for v in depth_values if v.size > 0])
    vmin = safe_percentile(depth_values, 2, 0.0)
    vmax = safe_percentile(depth_values, 98, 10.0)
    if vmax <= vmin:
        vmax = vmin + 1.0

    fig, axes = plt.subplots(2, 4, figsize=(18, 8.8), constrained_layout=True)
    fig.suptitle(title + "\nFull-image qualitative depth; sky/non-LiDAR regions remain visible.", fontsize=12)

    axis_image(axes[0, 0], rgb, "RGB input")
    for ax, key in zip(axes[0, 1:], ["original", "b0", "w19"]):
        im = axis_image(
            ax,
            predictions[key]["scaled_depth"],
            f"{MODEL_LABELS[key]}\n{metric_text(metrics[key])}",
            cmap="magma_r",
            vmin=vmin,
            vmax=vmax,
        )
        maybe_colorbar(fig, im, ax)

    im = axis_image(
        axes[1, 0],
        predictions["w29"]["scaled_depth"],
        f"{MODEL_LABELS['w29']}\n{metric_text(metrics['w29'])}",
        cmap="magma_r",
        vmin=vmin,
        vmax=vmax,
    )
    maybe_colorbar(fig, im, axes[1, 0])
    im = axis_image(axes[1, 1], label_display, "LiDAR depth label\n(valid pixels only)", cmap="magma_r", vmin=vmin, vmax=vmax)
    maybe_colorbar(fig, im, axes[1, 1])
    axis_image(axes[1, 2], eval_mask, f"Evaluation mask\ncoverage={eval_mask.mean():.1%}", cmap="gray")
    w19_b0 = predictions["b0"]["error_absrel"] - predictions["w19"]["error_absrel"]
    bound = safe_percentile(np.abs(w19_b0), 98, 0.5)
    im = axis_image(
        axes[1, 3],
        w19_b0,
        "Valid pixels: B0 error - W19 error\nblue worse, red better for W19",
        cmap="coolwarm",
        vmin=-bound,
        vmax=bound,
    )
    maybe_colorbar(fig, im, axes[1, 3])

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_valid_mask_panel(
    output_path: Path,
    rgb: Image.Image,
    dense: np.ndarray,
    eval_mask: np.ndarray,
    predictions: Dict[str, Dict[str, np.ndarray]],
    metrics: Dict[str, Dict[str, float]],
    title: str,
) -> None:
    label_display = np.where(eval_mask, dense, np.nan)
    label_values = label_display[np.isfinite(label_display)]
    vmin = safe_percentile(label_values, 2, 0.0)
    vmax = safe_percentile(label_values, 98, 10.0)
    if vmax <= vmin:
        vmax = vmin + 1.0
    error_values = np.concatenate(
        [
            predictions[key]["error_absrel"][np.isfinite(predictions[key]["error_absrel"])]
            for key in MODEL_ORDER
        ]
    )
    err_max = safe_percentile(error_values, 98, 1.0)
    if err_max <= 0:
        err_max = 1.0

    fig, axes = plt.subplots(2, 4, figsize=(18, 8.8), constrained_layout=True)
    fig.suptitle(title + "\nValid LiDAR evaluation region only.", fontsize=12)

    axis_image(axes[0, 0], rgb, "RGB input")
    axis_image(axes[0, 1], eval_mask, f"Evaluation mask\ncoverage={eval_mask.mean():.1%}", cmap="gray")
    im = axis_image(axes[0, 2], label_display, "LiDAR depth label\n(valid pixels only)", cmap="magma_r", vmin=vmin, vmax=vmax)
    maybe_colorbar(fig, im, axes[0, 2])
    w19_b0 = predictions["b0"]["error_absrel"] - predictions["w19"]["error_absrel"]
    bound = safe_percentile(np.abs(w19_b0), 98, 0.5)
    im = axis_image(
        axes[0, 3],
        w19_b0,
        "B0 error - W19 error\nred = W19 lower error",
        cmap="coolwarm",
        vmin=-bound,
        vmax=bound,
    )
    maybe_colorbar(fig, im, axes[0, 3])

    for ax, key in zip(axes[1], MODEL_ORDER):
        im = axis_image(
            ax,
            predictions[key]["error_absrel"],
            f"{MODEL_LABELS[key]}\nAbsRel error, {metric_text(metrics[key])}",
            cmap="inferno",
            vmin=0.0,
            vmax=err_max,
        )
        maybe_colorbar(fig, im, ax)

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_crop_panel(
    output_path: Path,
    rgb: Image.Image,
    dense: np.ndarray,
    eval_mask: np.ndarray,
    predictions: Dict[str, Dict[str, np.ndarray]],
    metrics: Dict[str, Dict[str, float]],
    title: str,
) -> None:
    ys, xs = crop_box(eval_mask)
    rgb_crop = np.asarray(rgb)[ys, xs]
    mask_crop = eval_mask[ys, xs]
    label_crop = np.where(mask_crop, dense[ys, xs], np.nan)
    b0_depth = np.where(mask_crop, predictions["b0"]["scaled_depth"][ys, xs], np.nan)
    w19_depth = np.where(mask_crop, predictions["w19"]["scaled_depth"][ys, xs], np.nan)
    depth_values = np.concatenate(
        [
            label_crop[np.isfinite(label_crop)],
            b0_depth[np.isfinite(b0_depth)],
            w19_depth[np.isfinite(w19_depth)],
        ]
    )
    vmin = safe_percentile(depth_values, 2, 0.0)
    vmax = safe_percentile(depth_values, 98, 10.0)
    if vmax <= vmin:
        vmax = vmin + 1.0

    errors = {
        key: predictions[key]["error_absrel"][ys, xs] for key in ["original", "b0", "w19"]
    }
    error_values = np.concatenate([arr[np.isfinite(arr)] for arr in errors.values()])
    err_max = safe_percentile(error_values, 98, 1.0)
    if err_max <= 0:
        err_max = 1.0
    improvement = errors["b0"] - errors["w19"]
    bound = safe_percentile(np.abs(improvement), 98, 0.5)

    fig, axes = plt.subplots(2, 4, figsize=(18, 8.8), constrained_layout=True)
    fig.suptitle(title + "\nCropped/masked view of evaluated pixels.", fontsize=12)

    axis_image(axes[0, 0], rgb_crop, "RGB crop")
    axis_image(axes[0, 1], mask_crop, "Evaluation mask crop", cmap="gray")
    im = axis_image(axes[0, 2], label_crop, "LiDAR depth label crop", cmap="magma_r", vmin=vmin, vmax=vmax)
    maybe_colorbar(fig, im, axes[0, 2])
    im = axis_image(axes[0, 3], w19_depth, f"W19 masked depth\n{metric_text(metrics['w19'])}", cmap="magma_r", vmin=vmin, vmax=vmax)
    maybe_colorbar(fig, im, axes[0, 3])

    im = axis_image(axes[1, 0], errors["original"], "Original AbsRel error", cmap="inferno", vmin=0.0, vmax=err_max)
    maybe_colorbar(fig, im, axes[1, 0])
    im = axis_image(axes[1, 1], errors["b0"], "B0 AbsRel error", cmap="inferno", vmin=0.0, vmax=err_max)
    maybe_colorbar(fig, im, axes[1, 1])
    im = axis_image(axes[1, 2], errors["w19"], "W19 AbsRel error", cmap="inferno", vmin=0.0, vmax=err_max)
    maybe_colorbar(fig, im, axes[1, 2])
    im = axis_image(
        axes[1, 3],
        improvement,
        "B0 error - W19 error\nred = W19 lower error",
        cmap="coolwarm",
        vmin=-bound,
        vmax=bound,
    )
    maybe_colorbar(fig, im, axes[1, 3])

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_w29_w19_panel(
    output_path: Path,
    rgb: Image.Image,
    dense: np.ndarray,
    eval_mask: np.ndarray,
    predictions: Dict[str, Dict[str, np.ndarray]],
    metrics: Dict[str, Dict[str, float]],
    title: str,
) -> None:
    label_display = np.where(eval_mask, dense, np.nan)
    depth_values = np.concatenate(
        [
            label_display[np.isfinite(label_display)],
            predictions["w29"]["scaled_depth"][np.isfinite(predictions["w29"]["scaled_depth"])],
            predictions["w19"]["scaled_depth"][np.isfinite(predictions["w19"]["scaled_depth"])],
        ]
    )
    vmin = safe_percentile(depth_values, 2, 0.0)
    vmax = safe_percentile(depth_values, 98, 10.0)
    if vmax <= vmin:
        vmax = vmin + 1.0
    error_values = np.concatenate(
        [
            predictions["w29"]["error_absrel"][np.isfinite(predictions["w29"]["error_absrel"])],
            predictions["w19"]["error_absrel"][np.isfinite(predictions["w19"]["error_absrel"])],
        ]
    )
    err_max = safe_percentile(error_values, 98, 1.0)
    if err_max <= 0:
        err_max = 1.0
    improvement = predictions["w29"]["error_absrel"] - predictions["w19"]["error_absrel"]
    bound = safe_percentile(np.abs(improvement), 98, 0.5)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5), constrained_layout=True)
    fig.suptitle(title + "\nSnapshot 05 checkpoint-selection comparison.", fontsize=12)
    axis_image(axes[0, 0], rgb, "RGB input")
    im = axis_image(axes[0, 1], predictions["w29"]["scaled_depth"], f"weights_29\n{metric_text(metrics['w29'])}", cmap="magma_r", vmin=vmin, vmax=vmax)
    maybe_colorbar(fig, im, axes[0, 1])
    im = axis_image(axes[0, 2], predictions["w19"]["scaled_depth"], f"weights_19 selected\n{metric_text(metrics['w19'])}", cmap="magma_r", vmin=vmin, vmax=vmax)
    maybe_colorbar(fig, im, axes[0, 2])
    im = axis_image(axes[1, 0], predictions["w29"]["error_absrel"], "weights_29 valid AbsRel error", cmap="inferno", vmin=0.0, vmax=err_max)
    maybe_colorbar(fig, im, axes[1, 0])
    im = axis_image(axes[1, 1], predictions["w19"]["error_absrel"], "weights_19 valid AbsRel error", cmap="inferno", vmin=0.0, vmax=err_max)
    maybe_colorbar(fig, im, axes[1, 1])
    im = axis_image(
        axes[1, 2],
        improvement,
        "weights_29 error - weights_19 error\nred = weights_19 lower error",
        cmap="coolwarm",
        vmin=-bound,
        vmax=bound,
    )
    maybe_colorbar(fig, im, axes[1, 2])
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_plain_outputs(
    output_dir: Path,
    rgb: Image.Image,
    w19_pred: Dict[str, np.ndarray],
    sample_title: str,
    prefix: str,
) -> Dict[str, str]:
    depth = w19_pred["raw_depth"]
    disp = w19_pred["scaled_disp"]
    depth_vmin = safe_percentile(depth, 2, 0.0)
    depth_vmax = safe_percentile(depth, 98, 10.0)
    disp_vmin = safe_percentile(disp, 2, 0.0)
    disp_vmax = safe_percentile(disp, 98, 1.0)
    output_dir.mkdir(parents=True, exist_ok=True)

    depth_png = output_dir / f"{prefix}_w19_raw_depth.png"
    disp_png = output_dir / f"{prefix}_w19_disparity.png"
    rgb_depth = output_dir / f"{prefix}_rgb_plus_w19_depth.png"
    rgb_disp = output_dir / f"{prefix}_rgb_plus_w19_disparity.png"

    save_array_png(depth_png, depth, "magma_r", depth_vmin, depth_vmax)
    save_array_png(disp_png, disp, "magma", disp_vmin, disp_vmax)

    for path, array, title, cmap, vmin, vmax in [
        (rgb_depth, depth, "Snapshot 05 weights_19 raw predicted depth", "magma_r", depth_vmin, depth_vmax),
        (rgb_disp, disp, "Snapshot 05 weights_19 predicted disparity", "magma", disp_vmin, disp_vmax),
    ]:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
        fig.suptitle(sample_title + "\nPlain RGB-only inference view; no LiDAR overlay.", fontsize=11)
        axis_image(axes[0], rgb, "RGB input")
        im = axis_image(axes[1], array, title, cmap=cmap, vmin=vmin, vmax=vmax)
        maybe_colorbar(fig, im, axes[1])
        fig.savefig(path, dpi=150)
        plt.close(fig)

    return {
        "raw_depth_png": str(depth_png),
        "disparity_png": str(disp_png),
        "rgb_depth_panel": str(rgb_depth),
        "rgb_disparity_panel": str(rgb_disp),
    }


def collect_samples(
    selected_root: Path,
    rows_by_split: Dict[str, Dict[str, Dict[str, Dict[str, str]]]],
) -> List[Dict[str, object]]:
    samples: Dict[Tuple[str, str], Dict[str, object]] = {}
    comparison_root = selected_root / "comparison_panels"
    for summary_path in sorted(comparison_root.glob("*/original_vs_adapted_selection_summary.csv")):
        folder = summary_path.parent.name
        split = "test" if "_test_" in folder else "val"
        for row in read_csv_rows(summary_path):
            rgb_rel = row["rgb_rel"]
            if rgb_rel not in rows_by_split[split]["w19"]:
                continue
            key = (split, rgb_rel)
            entry = samples.setdefault(
                key,
                {
                    "split": split,
                    "rgb_rel": rgb_rel,
                    "roles": [],
                },
            )
            entry["roles"].append(f"{folder}:{row.get('role', '')}")

    if samples:
        return list(samples.values())

    for split, rows_by_model in rows_by_split.items():
        rows = list(rows_by_model["w19"].values())
        finite_rows = [
            row for row in rows if np.isfinite(safe_float(row.get("median_scaled_a1")))
        ]
        values = np.array(
            [safe_float(row["median_scaled_a1"]) for row in finite_rows], dtype=np.float32
        )
        median_value = float(np.median(values))
        fallback = [
            ("adapted_good", max(finite_rows, key=lambda r: safe_float(r["median_scaled_a1"]))),
            (
                "adapted_typical",
                min(
                    finite_rows,
                    key=lambda r: abs(safe_float(r["median_scaled_a1"]) - median_value),
                ),
            ),
            ("adapted_bad", min(finite_rows, key=lambda r: safe_float(r["median_scaled_a1"]))),
        ]
        for role, row in fallback:
            samples[(split, row["rgb_rel"])] = {
                "split": split,
                "rgb_rel": row["rgb_rel"],
                "roles": [f"fallback:{role}"],
            }
    return list(samples.values())


def sample_prefix(split: str, row: Dict[str, str], roles: Iterable[str]) -> str:
    index = int(row["index"])
    role_text = "__".join(slug(role.split(":")[-1]) for role in roles)
    stem = slug(Path(row["rgb_rel"]).stem)
    return f"{split}_index_{index:04d}_{role_text}_{stem}"


def render_sample(
    sample: Dict[str, object],
    models: Dict[str, object],
    rows_by_split: Dict[str, Dict[str, Dict[str, Dict[str, str]]]],
    dataset_workspace: Path,
    output_dir: Path,
) -> Dict[str, object]:
    split = str(sample["split"])
    rgb_rel = str(sample["rgb_rel"])
    roles = list(sample["roles"])
    rows_by_model = rows_by_split[split]
    w19_row = rows_by_model["w19"][rgb_rel]
    dense = load_npz_array(dataset_workspace / w19_row["dense_rel"]).astype(np.float32)
    valid_mask = load_npz_array(dataset_workspace / w19_row["valid_mask_rel"]) > 0
    eval_mask = valid_mask & np.isfinite(dense) & (dense > 1e-3) & (dense < 80.0)
    rgb_path = dataset_workspace / rgb_rel
    rgb = Image.open(rgb_path).convert("RGB")

    predictions: Dict[str, Dict[str, np.ndarray]] = {}
    metrics: Dict[str, Dict[str, float]] = {}
    for key in MODEL_ORDER:
        row = rows_by_model[key].get(rgb_rel)
        pred = run_depth_and_disparity(rgb_path, dense.shape, models[key])
        pred["scaled_depth"] = scaled_depth(pred["raw_depth"], row)
        pred["error_absrel"] = absrel_error(pred["scaled_depth"], dense, eval_mask)
        predictions[key] = pred
        metrics[key] = model_metrics(row)

    prefix = sample_prefix(split, w19_row, roles)
    title = (
        f"{split.upper()} index {int(w19_row['index']):04d} | "
        + " | ".join(roles)
    )

    group_dirs = {
        "full": output_dir / "full_image_qualitative",
        "valid": output_dir / "valid_mask_evaluation",
        "crop": output_dir / "cropped_masked_evaluation",
        "w29": output_dir / "weights29_vs_weights19",
        "plain": output_dir / "plain_inference" / split,
    }
    for directory in group_dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    output_paths = {
        "full_image_panel": group_dirs["full"] / f"{prefix}_full_image_qualitative.png",
        "valid_mask_panel": group_dirs["valid"] / f"{prefix}_valid_mask_errors.png",
        "cropped_mask_panel": group_dirs["crop"] / f"{prefix}_cropped_valid_region.png",
        "weights29_vs_weights19_panel": group_dirs["w29"] / f"{prefix}_w29_vs_w19.png",
    }
    render_full_image_panel(output_paths["full_image_panel"], rgb, dense, eval_mask, predictions, metrics, title)
    render_valid_mask_panel(output_paths["valid_mask_panel"], rgb, dense, eval_mask, predictions, metrics, title)
    render_crop_panel(output_paths["cropped_mask_panel"], rgb, dense, eval_mask, predictions, metrics, title)
    render_w29_w19_panel(output_paths["weights29_vs_weights19_panel"], rgb, dense, eval_mask, predictions, metrics, title)
    plain_paths = render_plain_outputs(group_dirs["plain"], rgb, predictions["w19"], title, prefix)

    top_third = eval_mask[: eval_mask.shape[0] // 3]
    row_summary: Dict[str, object] = {
        "split": split,
        "index": int(w19_row["index"]),
        "rgb_rel": rgb_rel,
        "roles": "; ".join(roles),
        "valid_fraction": float(eval_mask.mean()),
        "top_third_valid_fraction": float(top_third.mean()) if top_third.size else float("nan"),
        "full_image_panel": str(output_paths["full_image_panel"]),
        "valid_mask_panel": str(output_paths["valid_mask_panel"]),
        "cropped_mask_panel": str(output_paths["cropped_mask_panel"]),
        "weights29_vs_weights19_panel": str(output_paths["weights29_vs_weights19_panel"]),
        **plain_paths,
    }
    for key in MODEL_ORDER:
        row_summary[f"{key}_median_scaled_abs_rel"] = metrics[key]["median_scaled_abs_rel"]
        row_summary[f"{key}_median_scaled_a1"] = metrics[key]["median_scaled_a1"]
    row_summary["w19_absrel_minus_b0"] = (
        metrics["w19"]["median_scaled_abs_rel"] - metrics["b0"]["median_scaled_abs_rel"]
    )
    row_summary["w19_a1_minus_b0"] = metrics["w19"]["median_scaled_a1"] - metrics["b0"]["median_scaled_a1"]
    row_summary["w19_absrel_minus_original"] = (
        metrics["w19"]["median_scaled_abs_rel"] - metrics["original"]["median_scaled_abs_rel"]
    )
    row_summary["w19_a1_minus_original"] = (
        metrics["w19"]["median_scaled_a1"] - metrics["original"]["median_scaled_a1"]
    )
    row_summary["w19_absrel_minus_w29"] = (
        metrics["w19"]["median_scaled_abs_rel"] - metrics["w29"]["median_scaled_abs_rel"]
    )
    row_summary["w19_a1_minus_w29"] = metrics["w19"]["median_scaled_a1"] - metrics["w29"]["median_scaled_a1"]
    return row_summary


def format_delta(value: float, lower_is_better: bool) -> str:
    if not np.isfinite(value):
        return "n/a"
    if lower_is_better:
        direction = "better" if value < 0 else "worse"
    else:
        direction = "better" if value > 0 else "worse"
    return f"{value:+.4f} ({direction})"


def pick_examples(rows: List[Dict[str, object]], split: str, role_name: str) -> List[Dict[str, object]]:
    return [
        row
        for row in rows
        if row["split"] == split and role_name in str(row["roles"])
    ]


def write_visual_report(output_dir: Path, rows: List[Dict[str, object]]) -> None:
    val_rows = [row for row in rows if row["split"] == "val"]
    test_rows = [row for row in rows if row["split"] == "test"]
    b0_better = [row for row in rows if safe_float(row["w19_absrel_minus_b0"]) < 0]
    original_better = [row for row in rows if safe_float(row["w19_absrel_minus_original"]) < 0]
    w29_better = [row for row in rows if safe_float(row["w19_absrel_minus_w29"]) < 0]
    top_third_values = [
        safe_float(row["top_third_valid_fraction"])
        for row in rows
        if np.isfinite(safe_float(row["top_third_valid_fraction"]))
    ]
    min_top_third = min(top_third_values) if top_third_values else float("nan")
    max_top_third = max(top_third_values) if top_third_values else float("nan")

    def example_lines(selected: List[Dict[str, object]]) -> List[str]:
        lines = []
        for row in selected:
            lines.append(
                "- "
                f"{row['split']} index {row['index']}: roles `{row['roles']}`, "
                f"W19-vs-B0 AbsRel {format_delta(safe_float(row['w19_absrel_minus_b0']), True)}, "
                f"W19-vs-Original AbsRel {format_delta(safe_float(row['w19_absrel_minus_original']), True)}"
            )
        return lines or ["- None in the selected diagnostic set."]

    good = pick_examples(rows, "val", "adapted_good")[:1] + pick_examples(rows, "test", "adapted_good")[:1]
    typical = pick_examples(rows, "val", "adapted_typical")[:1] + pick_examples(rows, "test", "adapted_typical")[:1]
    failures = [
        row
        for row in rows
        if "adapted_bad" in str(row["roles"]) or "largest_drop" in str(row["roles"])
    ]

    report = [
        "# Snapshot 05 weights_19 Professor Visual Diagnosis",
        "",
        "Status: generated after checkpoint selection; no new training was run.",
        "",
        "This package separates full-image qualitative behavior from the valid LiDAR evaluation region. "
        "That separation matters because sky and some far canopy regions are often outside the evaluation mask, "
        "but they are still visible in full-frame monocular depth maps.",
        "",
        "## Output Folders",
        "",
        "```text",
        "full_image_qualitative/",
        "valid_mask_evaluation/",
        "cropped_masked_evaluation/",
        "weights29_vs_weights19/",
        "plain_inference/",
        "sample_selection.csv",
        "sample_selection.json",
        "```",
        "",
        "## Direct Answers",
        "",
        "### Does Snapshot 05 weights_19 look better than B0?",
        "",
        "At the aggregate level, the validation-selected W19 checkpoint improves B0 on median-scaled AbsRel "
        "while keeping most of B0's a1. In this deliberately mixed diagnostic set, W19 has lower per-image "
        f"median-scaled AbsRel than B0 on {len(b0_better)}/{len(rows)} selected examples. The valid-mask panels "
        "are the fair place to judge this. The full-image panels remain visually mixed because W19 can produce "
        "dark, blob-like plant regions.",
        "",
        "### Does Snapshot 05 weights_19 look better than Original Lite-Mono?",
        "",
        f"Only partly. W19 has lower per-image median-scaled AbsRel than Original on "
        f"{len(original_better)}/{len(rows)} selected examples, but it often looks less natural in full-frame depth, "
        "especially around sky/far vegetation boundaries. This matches the aggregate story: W19 is much closer to "
        "Original on test AbsRel than B0 is, but it is not a clean visual or metric win over Original.",
        "",
        "### Where does it improve?",
        "",
        "It most clearly improves in the valid LiDAR evaluation region when B0 has smooth or poorly scaled "
        "vegetation/ground structure and W19 reduces relative error. The red areas in the `B0 error - W19 error` "
        "maps show where W19 is better inside the mask.",
        "",
        "### Where does it fail?",
        "",
        "The full-image panels show the main failure mode: W19 can make plant masses look too dark or blob-like, "
        "and tree/sky boundaries can look over-smoothed or merged. These are qualitative issues even when the "
        "valid-mask AbsRel improves.",
        "",
        "### Are the sky issues inside or outside the valid evaluation mask?",
        "",
        "The blue sky itself is mostly outside the LiDAR mask in the panels, but this should not be overstated: "
        f"the top third of the selected images still has {100 * min_top_third:.1f}% to "
        f"{100 * max_top_third:.1f}% valid-mask coverage because tree canopy and far vegetation also occupy "
        "that region. The valid-mask panels show exactly which upper-image pixels are evaluated; the full-image "
        "panels should be used to discuss sky artifacts that the metric may not penalize.",
        "",
        "### Do dark plant blobs correspond to valid-depth improvement?",
        "",
        "Sometimes, but not reliably. Use the paired full-image and valid-mask panels: if the full image looks "
        "blob-like but the valid-mask error map is red versus B0, then the artifact coexists with measured "
        "valid-region improvement. If the error map is neutral/blue, keep it as a failure case.",
        "",
        "### Are the professor-facing visuals good enough to show?",
        "",
        "Yes, as honest diagnostics. They are not good enough to claim the visual problem is solved. The cleanest "
        "presentation is to show one full-image panel beside the matching valid-mask panel so the professor sees "
        "both the qualitative issue and the evaluated-region behavior.",
        "",
        "### Is Snapshot 05 weights_19 visually paper-ready?",
        "",
        "Not yet as a polished qualitative win. It is numerically promising and professor-discussion-ready, but "
        "the full-image artifacts should be presented as limitations.",
        "",
        "## Suggested Professor Examples",
        "",
        "Good examples to show first:",
        *example_lines(good),
        "",
        "Typical examples:",
        *example_lines(typical),
        "",
        "Honest failure/largest-drop examples:",
        *example_lines(failures[:6]),
        "",
        "## Selected Sample Summary",
        "",
        "| split | index | roles | valid % | top-third valid % | W19-B0 AbsRel | W19-Original AbsRel | W19-W29 AbsRel |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        report.append(
            f"| {row['split']} | {row['index']} | {row['roles']} | "
            f"{100 * safe_float(row['valid_fraction']):.1f} | "
            f"{100 * safe_float(row['top_third_valid_fraction']):.1f} | "
            f"{safe_float(row['w19_absrel_minus_b0']):+.4f} | "
            f"{safe_float(row['w19_absrel_minus_original']):+.4f} | "
            f"{safe_float(row['w19_absrel_minus_w29']):+.4f} |"
        )
    report.append("")
    (output_dir / "visual_diagnosis.md").write_text("\n".join(report), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    levinson_root = (
        REPO_ROOT
        / "citrus_project"
        / "milestones"
        / "04_lightweight_vegetation_improvement"
        / "levinson"
    )
    snapshot05 = (
        levinson_root
        / "snapshots"
        / "05_teacher_anchored_relative_structure_regularization"
    )
    checkpoint_root = levinson_root / "checkpoint_selection" / "teacher_anchor_snapshot05_06"
    parser = argparse.ArgumentParser(
        description="Render professor-facing Snapshot 05 weights_19 visual diagnostics."
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=snapshot05
        / "local_evidence"
        / "selected_weights19_professor_visual_diagnostics",
    )
    parser.add_argument(
        "--dataset_workspace",
        type=Path,
        default=REPO_ROOT / "citrus_project" / "dataset_workspace",
    )
    parser.add_argument("--model", default="lite-mono")
    parser.add_argument("--no_cuda", action="store_true")
    parser.add_argument("--min_depth", type=float, default=0.1)
    parser.add_argument("--max_depth", type=float, default=100.0)
    parser.add_argument(
        "--original_weights",
        type=Path,
        default=REPO_ROOT / "weights" / "lite-mono",
    )
    parser.add_argument(
        "--b0_weights",
        type=Path,
        default=snapshot05.parent / "00_plain_citrus_baseline" / "checkpoint",
    )
    parser.add_argument(
        "--weights19",
        type=Path,
        default=levinson_root
        / "runs"
        / "teacher_structure_regularization_b12_30ep_full"
        / "models"
        / "weights_19",
    )
    parser.add_argument(
        "--weights29",
        type=Path,
        default=levinson_root
        / "runs"
        / "teacher_structure_regularization_b12_30ep_full"
        / "models"
        / "weights_29",
    )
    parser.add_argument(
        "--selected_visual_root",
        type=Path,
        default=snapshot05 / "local_evidence" / "selected_weights19_visuals",
    )
    parser.add_argument(
        "--checkpoint_results",
        type=Path,
        default=checkpoint_root / "local_results",
    )
    return parser.parse_args()


def rows_for_split(args: argparse.Namespace, split: str) -> Dict[str, Path]:
    original_base = REPO_ROOT / "citrus_project" / "milestones" / "01_original_lite_mono_baseline" / "results"
    b0_base = (
        REPO_ROOT
        / "citrus_project"
        / "milestones"
        / "04_lightweight_vegetation_improvement"
        / "levinson"
        / "snapshots"
        / "00_plain_citrus_baseline"
        / "results"
    )
    w29_base = (
        REPO_ROOT
        / "citrus_project"
        / "milestones"
        / "04_lightweight_vegetation_improvement"
        / "levinson"
        / "snapshots"
        / "05_teacher_anchored_relative_structure_regularization"
        / "local_evidence"
        / "final_weights29_evaluation_full"
    )
    if split == "val":
        w19_path = (
            args.checkpoint_results
            / "validation"
            / "snapshot05"
            / "weights_19"
            / "val_lite-mono_full_per_sample.csv"
        )
    else:
        w19_path = (
            args.checkpoint_results
            / "test_selected"
            / "snapshot05"
            / "weights_19"
            / "test_lite-mono_full_per_sample.csv"
        )
    return {
        "original": original_base / f"{split}_lite-mono_full_per_sample.csv",
        "b0": b0_base / f"{split}_lite-mono_full_per_sample.csv",
        "w19": w19_path,
        "w29": w29_base / f"{split}_lite-mono_full_per_sample.csv",
    }


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows_by_split = {
        split: load_rows_by_rgb(rows_for_split(args, split)) for split in ["val", "test"]
    }
    samples = collect_samples(args.selected_visual_root.resolve(), rows_by_split)
    samples = sorted(samples, key=lambda item: (str(item["split"]), str(item["rgb_rel"])))

    print("Loading models for professor diagnostics")
    models = {
        "original": load_lite_mono_model(args.original_weights.resolve(), args.model, args.no_cuda, args.min_depth, args.max_depth),
        "b0": load_lite_mono_model(args.b0_weights.resolve(), args.model, args.no_cuda, args.min_depth, args.max_depth),
        "w19": load_lite_mono_model(args.weights19.resolve(), args.model, args.no_cuda, args.min_depth, args.max_depth),
        "w29": load_lite_mono_model(args.weights29.resolve(), args.model, args.no_cuda, args.min_depth, args.max_depth),
    }

    summaries = []
    for sample in samples:
        print(f"Rendering {sample['split']} {sample['rgb_rel']} | {sample['roles']}")
        summaries.append(
            render_sample(
                sample=sample,
                models=models,
                rows_by_split=rows_by_split,
                dataset_workspace=args.dataset_workspace.resolve(),
                output_dir=output_dir,
            )
        )

    with (output_dir / "sample_selection.json").open("w", encoding="utf-8") as fp:
        json.dump(summaries, fp, indent=2)
        fp.write("\n")
    write_csv(output_dir / "sample_selection.csv", summaries)
    write_visual_report(output_dir, summaries)

    print(f"Saved professor diagnostics: {output_dir}")
    print(f"Rendered selected examples: {len(summaries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
