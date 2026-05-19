from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List

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


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def safe_float(value: str, default: float = float("nan")) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_percentile(values: np.ndarray, percentile: float, fallback: float) -> float:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return fallback
    value = float(np.percentile(finite, percentile))
    return value if np.isfinite(value) else fallback


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("_") or "sample"


def collect_samples(
    per_sample_csv: Path,
    comparison_summaries: Iterable[Path],
) -> List[Dict[str, object]]:
    per_sample_rows = read_csv_rows(per_sample_csv)
    by_rgb = {row["rgb_rel"]: row for row in per_sample_rows}
    selected: Dict[str, Dict[str, object]] = {}

    for summary_path in comparison_summaries:
        if not summary_path.exists():
            continue
        source = summary_path.parent.name
        for summary_row in read_csv_rows(summary_path):
            rgb_rel = summary_row["rgb_rel"]
            if rgb_rel not in by_rgb:
                continue
            row = selected.setdefault(
                rgb_rel,
                {
                    "metrics": by_rgb[rgb_rel],
                    "roles": [],
                },
            )
            row["roles"].append(
                {
                    "comparison": source,
                    "role": summary_row.get("role", ""),
                    "panel_path": summary_row.get("panel_path", ""),
                }
            )

    if selected:
        return list(selected.values())

    finite_rows = [
        row
        for row in per_sample_rows
        if np.isfinite(safe_float(row.get("median_scaled_a1", "")))
    ]
    if not finite_rows:
        raise ValueError(f"No usable rows found in {per_sample_csv}")

    values = np.array(
        [safe_float(row["median_scaled_a1"]) for row in finite_rows], dtype=np.float64
    )
    median_value = float(np.median(values))
    fallback_rows = [
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
    return [
        {
            "metrics": row,
            "roles": [{"comparison": "per_sample_fallback", "role": role, "panel_path": ""}],
        }
        for role, row in fallback_rows
    ]


def run_depth_and_disparity(rgb_path: Path, dense_shape, model):
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
        "raw_disp": raw_disp_resized.detach().cpu().numpy()[0, 0],
        "scaled_disp": scaled_disp_resized.detach().cpu().numpy()[0, 0],
        "raw_depth": depth_resized.detach().cpu().numpy()[0, 0],
    }


def save_array_image(path: Path, array: np.ndarray, cmap: str, invert: bool = False) -> None:
    values = np.asarray(array, dtype=np.float32)
    if invert:
        values = -values
    vmin = safe_percentile(values, 2, 0.0)
    vmax = safe_percentile(values, 98, 1.0)
    if vmax <= vmin:
        vmax = vmin + 1.0
    plt.imsave(path, values, cmap=cmap, vmin=vmin, vmax=vmax)


def render_panel(
    output_path: Path,
    rgb_path: Path,
    dense: np.ndarray,
    valid_mask: np.ndarray,
    raw_depth: np.ndarray,
    scaled_depth: np.ndarray,
    scaled_disp: np.ndarray,
    title: str,
) -> None:
    eval_mask = (valid_mask > 0) & np.isfinite(dense) & (dense > 0)
    label_display = np.where(eval_mask, dense, np.nan)
    depth_values = np.concatenate(
        [
            raw_depth[np.isfinite(raw_depth)],
            scaled_depth[np.isfinite(scaled_depth)],
            label_display[np.isfinite(label_display)],
        ]
    )
    depth_vmin = safe_percentile(depth_values, 2, 0.0)
    depth_vmax = safe_percentile(depth_values, 98, 10.0)
    if depth_vmax <= depth_vmin:
        depth_vmax = depth_vmin + 1.0

    disp_vmin = safe_percentile(scaled_disp, 2, 0.0)
    disp_vmax = safe_percentile(scaled_disp, 98, 1.0)
    if disp_vmax <= disp_vmin:
        disp_vmax = disp_vmin + 1.0

    rgb = Image.open(rgb_path).convert("RGB")
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    fig.suptitle(title, fontsize=13)

    axes[0, 0].imshow(rgb)
    axes[0, 0].set_title("RGB input")
    im = axes[0, 1].imshow(raw_depth, cmap="magma_r", vmin=depth_vmin, vmax=depth_vmax)
    axes[0, 1].set_title("weights_19 raw predicted depth")
    fig.colorbar(im, ax=axes[0, 1], fraction=0.046, pad=0.04)
    im = axes[0, 2].imshow(
        scaled_depth, cmap="magma_r", vmin=depth_vmin, vmax=depth_vmax
    )
    axes[0, 2].set_title("weights_19 median-scaled depth")
    fig.colorbar(im, ax=axes[0, 2], fraction=0.046, pad=0.04)

    im = axes[1, 0].imshow(scaled_disp, cmap="magma", vmin=disp_vmin, vmax=disp_vmax)
    axes[1, 0].set_title("weights_19 predicted disparity")
    fig.colorbar(im, ax=axes[1, 0], fraction=0.046, pad=0.04)
    im = axes[1, 1].imshow(label_display, cmap="magma_r", vmin=depth_vmin, vmax=depth_vmax)
    axes[1, 1].set_title("LiDAR depth label (visual reference)")
    fig.colorbar(im, ax=axes[1, 1], fraction=0.046, pad=0.04)
    axes[1, 2].imshow(eval_mask, cmap="gray")
    axes[1, 2].set_title(f"Evaluation mask ({eval_mask.mean():.1%})")

    for ax in axes.ravel():
        ax.axis("off")

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_split(args: argparse.Namespace, split: str) -> List[Dict[str, object]]:
    per_sample_csv = args.per_sample_csv_template.format(split=split)
    comparison_paths = [
        Path(str(path).format(split=split)).resolve()
        for path in args.comparison_summary
    ]
    samples = collect_samples(Path(per_sample_csv).resolve(), comparison_paths)

    workspace = args.dataset_workspace.resolve()
    output_root = args.output_dir.resolve() / split
    output_root.mkdir(parents=True, exist_ok=True)
    model = load_lite_mono_model(
        weights_folder=args.weights_folder.resolve(),
        model_name=args.model,
        no_cuda=args.no_cuda,
        min_depth=args.min_depth,
        max_depth=args.max_depth,
    )

    manifest_rows = []
    for sample in samples:
        row = sample["metrics"]
        index = int(row["index"])
        rgb_rel = row["rgb_rel"]
        dense_rel = row["dense_rel"]
        valid_mask_rel = row["valid_mask_rel"]
        sample_prefix = output_root / f"index_{index:04d}_{slug(Path(rgb_rel).stem)}"

        rgb_path = workspace / rgb_rel
        dense = load_npz_array(workspace / dense_rel).astype(np.float32)
        valid_mask = load_npz_array(workspace / valid_mask_rel)
        prediction = run_depth_and_disparity(rgb_path, dense.shape, model)
        raw_depth = prediction["raw_depth"].astype(np.float32)
        scaled_disp = prediction["scaled_disp"].astype(np.float32)
        scale_ratio = safe_float(row.get("scale_ratio", ""))
        scaled_depth = raw_depth * scale_ratio if np.isfinite(scale_ratio) else raw_depth

        Image.open(rgb_path).convert("RGB").save(
            sample_prefix.with_name(sample_prefix.name + "_input_rgb.png")
        )
        save_array_image(
            sample_prefix.with_name(sample_prefix.name + "_pred_depth_raw_magma.png"),
            raw_depth,
            "magma_r",
        )
        save_array_image(
            sample_prefix.with_name(
                sample_prefix.name + "_pred_depth_median_scaled_magma.png"
            ),
            scaled_depth,
            "magma_r",
        )
        save_array_image(
            sample_prefix.with_name(sample_prefix.name + "_pred_disparity_magma.png"),
            scaled_disp,
            "magma",
        )
        np.savez_compressed(
            sample_prefix.with_name(sample_prefix.name + "_prediction_arrays.npz"),
            raw_depth=raw_depth,
            median_scaled_depth=scaled_depth.astype(np.float32),
            raw_disparity=prediction["raw_disp"].astype(np.float32),
            scaled_disparity=scaled_disp,
            scale_ratio=np.array(scale_ratio, dtype=np.float32),
        )

        title = (
            f"{split} index {index} | "
            f"a1={safe_float(row.get('median_scaled_a1', '')):.3f}, "
            f"abs_rel={safe_float(row.get('median_scaled_abs_rel', '')):.3f}, "
            f"scale={scale_ratio:.3f}"
        )
        render_panel(
            output_path=sample_prefix.with_name(
                sample_prefix.name + "_weights19_plain_inference_panel.png"
            ),
            rgb_path=rgb_path,
            dense=dense,
            valid_mask=valid_mask,
            raw_depth=raw_depth,
            scaled_depth=scaled_depth,
            scaled_disp=scaled_disp,
            title=title,
        )

        summary = {
            "split": split,
            "index": index,
            "rgb_rel": rgb_rel,
            "dense_rel": dense_rel,
            "valid_mask_rel": valid_mask_rel,
            "scale_ratio": scale_ratio,
            "median_scaled_abs_rel": safe_float(row.get("median_scaled_abs_rel", "")),
            "median_scaled_a1": safe_float(row.get("median_scaled_a1", "")),
            "roles": sample["roles"],
            "output_dir": str(output_root),
            "panel": str(
                sample_prefix.with_name(
                    sample_prefix.name + "_weights19_plain_inference_panel.png"
                )
            ),
        }
        with sample_prefix.with_name(
            sample_prefix.name + "_sample_summary.json"
        ).open("w", encoding="utf-8") as fp:
            json.dump(summary, fp, indent=2)
            fp.write("\n")
        manifest_rows.append(summary)

    return manifest_rows


def parse_args() -> argparse.Namespace:
    levinson_root = (
        REPO_ROOT
        / "citrus_project"
        / "milestones"
        / "04_lightweight_vegetation_improvement"
        / "levinson"
    )
    selected_root = (
        levinson_root
        / "snapshots"
        / "05_teacher_anchored_relative_structure_regularization"
        / "local_evidence"
        / "selected_weights19_visuals"
    )
    checkpoint_selection_root = (
        levinson_root
        / "checkpoint_selection"
        / "teacher_anchor_snapshot05_06"
        / "local_results"
    )
    parser = argparse.ArgumentParser(
        description="Render plain inference depth/disparity outputs for selected Snapshot 05 weights_19."
    )
    parser.add_argument(
        "--weights_folder",
        type=Path,
        default=(
            REPO_ROOT
            / "citrus_project"
            / "milestones"
            / "04_lightweight_vegetation_improvement"
            / "levinson"
            / "runs"
            / "teacher_structure_regularization_b12_30ep_full"
            / "models"
            / "weights_19"
        ),
    )
    parser.add_argument(
        "--dataset_workspace",
        type=Path,
        default=REPO_ROOT / "citrus_project" / "dataset_workspace",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=selected_root / "plain_inference_depth_outputs",
    )
    parser.add_argument(
        "--per_sample_csv_template",
        default=str(
            checkpoint_selection_root
            / "{split}_selected"
            / "snapshot05"
            / "weights_19"
            / "{split}_lite-mono_full_per_sample.csv"
        ),
        help=(
            "Format string for selected per-sample CSV. The built-in default is "
            "overridden internally for validation because its folder is named validation/."
        ),
    )
    parser.add_argument(
        "--comparison_summary",
        type=Path,
        action="append",
        default=[
            selected_root
            / "comparison_panels"
            / "original_vs_weights19_{split}_full"
            / "original_vs_adapted_selection_summary.csv",
            selected_root
            / "comparison_panels"
            / "b0_vs_weights19_{split}_full"
            / "original_vs_adapted_selection_summary.csv",
            selected_root
            / "comparison_panels"
            / "weights29_vs_weights19_{split}_full"
            / "original_vs_adapted_selection_summary.csv",
        ],
    )
    parser.add_argument("--splits", nargs="+", default=["val", "test"], choices=["val", "test"])
    parser.add_argument("--model", default="lite-mono")
    parser.add_argument("--no_cuda", action="store_true")
    parser.add_argument("--min_depth", type=float, default=0.1)
    parser.add_argument("--max_depth", type=float, default=100.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_rows = []
    checkpoint_selection_root = (
        REPO_ROOT
        / "citrus_project"
        / "milestones"
        / "04_lightweight_vegetation_improvement"
        / "levinson"
        / "checkpoint_selection"
        / "teacher_anchor_snapshot05_06"
        / "local_results"
    )
    for split in args.splits:
        if split == "val":
            args.per_sample_csv_template = str(
                checkpoint_selection_root
                / "validation"
                / "snapshot05"
                / "weights_19"
                / "val_lite-mono_full_per_sample.csv"
            )
        elif split == "test":
            args.per_sample_csv_template = str(
                checkpoint_selection_root
                / "test_selected"
                / "snapshot05"
                / "weights_19"
                / "test_lite-mono_full_per_sample.csv"
            )
        all_rows.extend(render_split(args, split))

    args.output_dir.resolve().mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir.resolve() / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fp:
        json.dump(
            {
                "weights_folder": str(args.weights_folder.resolve()),
                "note": (
                    "Plain inference visualizations from Snapshot 05 selected weights_19. "
                    "LiDAR labels and masks are included only as visual/evaluation references."
                ),
                "samples": all_rows,
            },
            fp,
            indent=2,
        )
        fp.write("\n")
    print(f"Saved manifest: {manifest_path}")
    print(f"Rendered samples: {len(all_rows)}")


if __name__ == "__main__":
    main()
