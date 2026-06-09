import argparse
import csv
import importlib.util
import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


BASELINE_MODULE_DIR = Path(__file__).resolve().parents[2] / "01_original_lite_mono_baseline"
if str(BASELINE_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(BASELINE_MODULE_DIR))

from evaluate_lite_mono_citrus import (  # noqa: E402
    compute_depth_errors_np,
    load_npz_array,
    repo_root,
)


@dataclass
class SelectedRow:
    role: str
    row: dict
    metric_value: float


def read_rows(csv_path):
    with csv_path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def select_rows(rows, metric):
    scored = []
    for row in rows:
        try:
            value = float(row[metric])
        except (KeyError, TypeError, ValueError):
            continue
        if np.isfinite(value):
            scored.append((value, row))
    if not scored:
        raise ValueError("No finite values found for metric {}".format(metric))

    scored.sort(key=lambda item: item[0])
    return [
        SelectedRow("bad", scored[0][1], scored[0][0]),
        SelectedRow("typical", scored[len(scored) // 2][1], scored[len(scored) // 2][0]),
        SelectedRow("good", scored[-1][1], scored[-1][0]),
    ]


def percentile_or(values, percentile, fallback):
    values = values[np.isfinite(values)]
    if values.size == 0:
        return fallback
    value = float(np.percentile(values, percentile))
    if not np.isfinite(value):
        return fallback
    return value


def median_scale(pred, dense, eval_mask):
    pred_eval = pred[eval_mask].astype(np.float64)
    gt_eval = dense[eval_mask].astype(np.float64)
    pred_median = float(np.median(pred_eval))
    gt_median = float(np.median(gt_eval))
    if not np.isfinite(pred_median) or pred_median <= 0:
        return None
    return gt_median / pred_median


def compute_metrics(pred, dense, eval_mask, eval_min_depth, eval_max_depth):
    gt_eval = dense[eval_mask].astype(np.float64)
    pred_eval = np.clip(pred[eval_mask], eval_min_depth, eval_max_depth).astype(np.float64)
    return compute_depth_errors_np(gt_eval, pred_eval)


def ensure_repo_imports(root):
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def install_timm_layers_shim():
    import torch
    from torch import nn

    if "timm.models.layers" in sys.modules:
        return

    class DropPath(nn.Module):
        def __init__(self, drop_prob=0.0):
            super().__init__()
            self.drop_prob = float(drop_prob)

        def forward(self, x):
            if self.drop_prob == 0.0 or not self.training:
                return x
            keep_prob = 1.0 - self.drop_prob
            shape = (x.shape[0],) + (1,) * (x.ndim - 1)
            random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
            random_tensor.floor_()
            return x.div(keep_prob) * random_tensor

    def trunc_normal_(tensor, mean=0.0, std=1.0, a=-2.0, b=2.0):
        return torch.nn.init.trunc_normal_(tensor, mean=mean, std=std, a=a, b=b)

    timm_mod = types.ModuleType("timm")
    models_mod = types.ModuleType("timm.models")
    layers_mod = types.ModuleType("timm.models.layers")
    layers_mod.DropPath = DropPath
    layers_mod.trunc_normal_ = trunc_normal_
    models_mod.layers = layers_mod
    timm_mod.models = models_mod
    sys.modules["timm"] = timm_mod
    sys.modules["timm.models"] = models_mod
    sys.modules["timm.models.layers"] = layers_mod


def load_class_from_file(module_name, file_path, class_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def load_lite_mono_model_direct(weights_folder, model_name, no_cuda, min_depth, max_depth):
    import torch

    root = repo_root()
    ensure_repo_imports(root)
    install_timm_layers_shim()

    from layers import disp_to_depth

    networks_dir = root / "networks"
    DepthDecoder = load_class_from_file(
        "lite_mono_depth_decoder_direct",
        networks_dir / "depth_decoder.py",
        "DepthDecoder",
    )
    LiteMono = load_class_from_file(
        "lite_mono_depth_encoder_direct",
        networks_dir / "depth_encoder.py",
        "LiteMono",
    )

    device = torch.device("cuda" if torch.cuda.is_available() and not no_cuda else "cpu")
    encoder_path = weights_folder / "encoder.pth"
    decoder_path = weights_folder / "depth.pth"

    encoder_dict = torch.load(encoder_path, map_location=device)
    decoder_dict = torch.load(decoder_path, map_location=device)
    feed_height = int(encoder_dict["height"])
    feed_width = int(encoder_dict["width"])

    encoder = LiteMono(model=model_name, height=feed_height, width=feed_width)
    encoder.load_state_dict(
        {key: value for key, value in encoder_dict.items() if key in encoder.state_dict()}
    )
    encoder.to(device)
    encoder.eval()

    depth_decoder = DepthDecoder(encoder.num_ch_enc, scales=range(3))
    depth_decoder.load_state_dict(
        {
            key: value
            for key, value in decoder_dict.items()
            if key in depth_decoder.state_dict()
        }
    )
    depth_decoder.to(device)
    depth_decoder.eval()

    return {
        "encoder": encoder,
        "depth_decoder": depth_decoder,
        "disp_to_depth": disp_to_depth,
        "device": device,
        "feed_height": feed_height,
        "feed_width": feed_width,
        "min_depth": min_depth,
        "max_depth": max_depth,
    }


def image_to_input_tensor(image, model):
    import torch

    resized = image.resize((model["feed_width"], model["feed_height"]), Image.LANCZOS)
    arr = np.asarray(resized, dtype=np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    tensor = torch.from_numpy(arr).unsqueeze(0)
    return tensor.to(model["device"])


def run_lite_mono_inference_direct(rgb_path, label_shape, model):
    import torch
    import torch.nn.functional as F

    with Image.open(rgb_path) as image:
        input_image = image.convert("RGB")
        input_tensor = image_to_input_tensor(input_image, model)

    with torch.no_grad():
        features = model["encoder"](input_tensor)
        outputs = model["depth_decoder"](features)
        raw_disp = outputs[("disp", 0)]
        _, depth = model["disp_to_depth"](
            raw_disp,
            model["min_depth"],
            model["max_depth"],
        )
        depth_resized = F.interpolate(
            depth,
            size=label_shape,
            mode="bilinear",
            align_corners=False,
        )
    return depth_resized.detach().cpu().numpy()[0, 0]


def render_comparison(
    selected,
    workspace_dir,
    output_dir,
    model_a,
    model_b,
    name_a,
    name_b,
    eval_min_depth,
    eval_max_depth,
):
    row = selected.row
    rgb_path = workspace_dir / row["rgb_rel"]
    dense_path = workspace_dir / row["dense_rel"]
    mask_path = workspace_dir / row["valid_mask_rel"]

    dense = load_npz_array(dense_path).astype(np.float32)
    valid_mask = load_npz_array(mask_path) > 0
    raw_a = run_lite_mono_inference_direct(rgb_path, dense.shape, model_a)
    raw_b = run_lite_mono_inference_direct(rgb_path, dense.shape, model_b)

    eval_mask = (
        valid_mask
        & np.isfinite(dense)
        & (dense > eval_min_depth)
        & (dense < eval_max_depth)
        & np.isfinite(raw_a)
        & np.isfinite(raw_b)
        & (raw_a > 0)
        & (raw_b > 0)
    )
    if not np.any(eval_mask):
        raise ValueError("No valid comparison pixels for {}".format(row["rgb_rel"]))

    scale_a = median_scale(raw_a, dense, eval_mask)
    scale_b = median_scale(raw_b, dense, eval_mask)
    if scale_a is None or scale_b is None:
        raise ValueError("Invalid median scale for {}".format(row["rgb_rel"]))

    scaled_a = raw_a * scale_a
    scaled_b = raw_b * scale_b
    label_display = np.where(eval_mask, dense, np.nan)

    raw_metrics_a = compute_metrics(raw_a, dense, eval_mask, eval_min_depth, eval_max_depth)
    raw_metrics_b = compute_metrics(raw_b, dense, eval_mask, eval_min_depth, eval_max_depth)
    scaled_metrics_a = compute_metrics(scaled_a, dense, eval_mask, eval_min_depth, eval_max_depth)
    scaled_metrics_b = compute_metrics(scaled_b, dense, eval_mask, eval_min_depth, eval_max_depth)

    error_a = np.full(dense.shape, np.nan, dtype=np.float32)
    error_b = np.full(dense.shape, np.nan, dtype=np.float32)
    error_a[eval_mask] = np.abs(scaled_a[eval_mask] - dense[eval_mask])
    error_b[eval_mask] = np.abs(scaled_b[eval_mask] - dense[eval_mask])
    error_delta = error_b - error_a

    depth_values = np.concatenate(
        [
            label_display[np.isfinite(label_display)].reshape(-1),
            raw_a[np.isfinite(raw_a)].reshape(-1),
            raw_b[np.isfinite(raw_b)].reshape(-1),
            scaled_a[eval_mask].reshape(-1),
            scaled_b[eval_mask].reshape(-1),
        ]
    )
    vmin = percentile_or(depth_values, 2, 0.0)
    vmax = percentile_or(depth_values, 98, 10.0)
    if vmax <= vmin:
        vmax = vmin + 1.0

    err_max = percentile_or(
        np.concatenate([error_a[np.isfinite(error_a)], error_b[np.isfinite(error_b)]]),
        98,
        1.0,
    )
    if err_max <= 0:
        err_max = 1.0

    delta_abs = percentile_or(np.abs(error_delta[np.isfinite(error_delta)]), 98, 1.0)
    if delta_abs <= 0:
        delta_abs = 1.0

    rgb = Image.open(rgb_path).convert("RGB")
    index = int(row["index"])
    output_path = output_dir / "{}_index_{:04d}_raw_and_scaled_comparison.png".format(
        selected.role, index
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(3, 4, figsize=(24, 15), constrained_layout=True)
    fig.suptitle(
        (
            "{} sample index {} | raw: {} a1={:.3f}, abs_rel={:.3f}; "
            "{} a1={:.3f}, abs_rel={:.3f} | scaled: {} a1={:.3f}, abs_rel={:.3f}; "
            "{} a1={:.3f}, abs_rel={:.3f}"
        ).format(
            selected.role.title(),
            index,
            name_a,
            raw_metrics_a["a1"],
            raw_metrics_a["abs_rel"],
            name_b,
            raw_metrics_b["a1"],
            raw_metrics_b["abs_rel"],
            name_a,
            scaled_metrics_a["a1"],
            scaled_metrics_a["abs_rel"],
            name_b,
            scaled_metrics_b["a1"],
            scaled_metrics_b["abs_rel"],
        ),
        fontsize=12,
    )

    axes[0, 0].imshow(rgb)
    axes[0, 0].set_title("RGB")
    im = axes[0, 1].imshow(label_display, cmap="magma_r", vmin=vmin, vmax=vmax)
    axes[0, 1].set_title("Dense LiDAR label")
    fig.colorbar(im, ax=axes[0, 1], fraction=0.046, pad=0.04)
    axes[0, 2].imshow(eval_mask, cmap="gray")
    axes[0, 2].set_title("Valid eval mask ({:.1%})".format(eval_mask.mean()))
    axes[0, 3].axis("off")

    im = axes[1, 0].imshow(raw_a, cmap="magma_r", vmin=vmin, vmax=vmax)
    axes[1, 0].set_title("{} raw".format(name_a))
    fig.colorbar(im, ax=axes[1, 0], fraction=0.046, pad=0.04)
    im = axes[1, 1].imshow(raw_b, cmap="magma_r", vmin=vmin, vmax=vmax)
    axes[1, 1].set_title("{} raw".format(name_b))
    fig.colorbar(im, ax=axes[1, 1], fraction=0.046, pad=0.04)
    im = axes[1, 2].imshow(scaled_a, cmap="magma_r", vmin=vmin, vmax=vmax)
    axes[1, 2].set_title("{} median-scaled x{:.3f}".format(name_a, scale_a))
    fig.colorbar(im, ax=axes[1, 2], fraction=0.046, pad=0.04)
    im = axes[1, 3].imshow(scaled_b, cmap="magma_r", vmin=vmin, vmax=vmax)
    axes[1, 3].set_title("{} median-scaled x{:.3f}".format(name_b, scale_b))
    fig.colorbar(im, ax=axes[1, 3], fraction=0.046, pad=0.04)

    im = axes[2, 0].imshow(error_a, cmap="inferno", vmin=0.0, vmax=err_max)
    axes[2, 0].set_title("{} scaled abs error".format(name_a))
    fig.colorbar(im, ax=axes[2, 0], fraction=0.046, pad=0.04)
    im = axes[2, 1].imshow(error_b, cmap="inferno", vmin=0.0, vmax=err_max)
    axes[2, 1].set_title("{} scaled abs error".format(name_b))
    fig.colorbar(im, ax=axes[2, 1], fraction=0.046, pad=0.04)
    im = axes[2, 2].imshow(error_delta, cmap="coolwarm", vmin=-delta_abs, vmax=delta_abs)
    axes[2, 2].set_title("Error delta: {} - {}".format(name_b, name_a))
    fig.colorbar(im, ax=axes[2, 2], fraction=0.046, pad=0.04)
    raw_delta = raw_b - raw_a
    raw_delta_abs = percentile_or(np.abs(raw_delta[np.isfinite(raw_delta)]), 98, 1.0)
    im = axes[2, 3].imshow(raw_delta, cmap="coolwarm", vmin=-raw_delta_abs, vmax=raw_delta_abs)
    axes[2, 3].set_title("Raw depth delta: {} - {}".format(name_b, name_a))
    fig.colorbar(im, ax=axes[2, 3], fraction=0.046, pad=0.04)

    for ax in axes.ravel():
        ax.axis("off")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return {
        "role": selected.role,
        "index": index,
        "rgb_rel": row["rgb_rel"],
        "panel_path": str(output_path),
        "scale_a": scale_a,
        "scale_b": scale_b,
        "raw_abs_rel_a": raw_metrics_a["abs_rel"],
        "raw_a1_a": raw_metrics_a["a1"],
        "raw_abs_rel_b": raw_metrics_b["abs_rel"],
        "raw_a1_b": raw_metrics_b["a1"],
        "scaled_abs_rel_a": scaled_metrics_a["abs_rel"],
        "scaled_a1_a": scaled_metrics_a["a1"],
        "scaled_abs_rel_b": scaled_metrics_b["abs_rel"],
        "scaled_a1_b": scaled_metrics_b["a1"],
        "scaled_abs_rel_b_minus_a": scaled_metrics_b["abs_rel"] - scaled_metrics_a["abs_rel"],
        "scaled_a1_b_minus_a": scaled_metrics_b["a1"] - scaled_metrics_a["a1"],
    }


def write_outputs(output_dir, summaries, split):
    json_path = output_dir / "{}_raw_and_scaled_comparison_summary.json".format(split)
    csv_path = output_dir / "{}_raw_and_scaled_comparison_summary.csv".format(split)
    with json_path.open("w", encoding="utf-8") as fp:
        json.dump(summaries, fp, indent=2)
    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        writer.writerows(summaries)
    return json_path, csv_path


def parse_args():
    root = repo_root()
    parser = argparse.ArgumentParser(
        description="Render same-image raw and median-scaled depth comparisons for two checkpoints."
    )
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--selection_results_dir", type=Path, required=True)
    parser.add_argument(
        "--dataset_workspace",
        type=Path,
        default=root / "citrus_project" / "dataset_workspace",
    )
    parser.add_argument("--weights_a", type=Path, required=True)
    parser.add_argument("--weights_b", type=Path, required=True)
    parser.add_argument("--name_a", default="Model A")
    parser.add_argument("--name_b", default="Model B")
    parser.add_argument("--output_dir", type=Path, required=True)
    parser.add_argument("--metric", default="median_scaled_a1")
    parser.add_argument(
        "--sample_tag",
        default="full",
        help="Evaluator sample tag in the per-sample filename, e.g. full or max3.",
    )
    parser.add_argument("--model", default="lite-mono")
    parser.add_argument("--no_cuda", action="store_true")
    parser.add_argument("--min_depth", type=float, default=0.1)
    parser.add_argument("--max_depth", type=float, default=100.0)
    parser.add_argument("--eval_min_depth", type=float, default=1e-3)
    parser.add_argument("--eval_max_depth", type=float, default=80.0)
    return parser.parse_args()


def main():
    args = parse_args()
    per_sample_path = (
        args.selection_results_dir.resolve()
        / "{}_{}_{}_per_sample.csv".format(args.split, args.model, args.sample_tag)
    )
    rows = read_rows(per_sample_path)
    selected = select_rows(rows, args.metric)

    model_a = load_lite_mono_model_direct(
        args.weights_a.resolve(),
        args.model,
        args.no_cuda,
        args.min_depth,
        args.max_depth,
    )
    model_b = load_lite_mono_model_direct(
        args.weights_b.resolve(),
        args.model,
        args.no_cuda,
        args.min_depth,
        args.max_depth,
    )

    output_dir = args.output_dir.resolve()
    summaries = [
        render_comparison(
            selected=item,
            workspace_dir=args.dataset_workspace.resolve(),
            output_dir=output_dir,
            model_a=model_a,
            model_b=model_b,
            name_a=args.name_a,
            name_b=args.name_b,
            eval_min_depth=args.eval_min_depth,
            eval_max_depth=args.eval_max_depth,
        )
        for item in selected
    ]
    json_path, csv_path = write_outputs(output_dir, summaries, args.split)
    print("Wrote", json_path)
    print("Wrote", csv_path)
    for item in summaries:
        print("Panel:", item["panel_path"])


if __name__ == "__main__":
    main()
