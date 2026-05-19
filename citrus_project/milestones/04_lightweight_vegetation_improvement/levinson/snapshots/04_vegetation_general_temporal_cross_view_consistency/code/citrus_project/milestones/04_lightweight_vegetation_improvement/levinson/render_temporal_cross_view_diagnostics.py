from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from PIL import Image
from torch.utils.data._utils.collate import default_collate


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from trainer import Trainer  # noqa: E402


def tensor_to_rgb_image(tensor: torch.Tensor) -> Image.Image:
    array = tensor.detach().cpu().clamp(0.0, 1.0).numpy()
    array = np.transpose(array, (1, 2, 0))
    return Image.fromarray((array * 255.0).astype(np.uint8), mode="RGB")


def tensor_to_gray_image(tensor: torch.Tensor) -> Image.Image:
    array = tensor.detach().cpu().float().numpy()
    if array.ndim == 3:
        array = array[0]
    finite = np.isfinite(array)
    if not finite.any():
        scaled = np.zeros_like(array, dtype=np.uint8)
    else:
        values = array[finite]
        lo = float(np.percentile(values, 1))
        hi = float(np.percentile(values, 99))
        if hi <= lo:
            hi = lo + 1e-6
        scaled = np.clip((array - lo) / (hi - lo), 0.0, 1.0)
        scaled[~finite] = 0.0
        scaled = (scaled * 255.0).astype(np.uint8)
    return Image.fromarray(scaled, mode="L")


def scalar_losses(losses: dict) -> dict:
    summary = {}
    for name, value in losses.items():
        if isinstance(value, torch.Tensor):
            if value.numel() == 1:
                summary[name] = float(value.detach().cpu())
        elif isinstance(value, np.ndarray):
            if value.size == 1:
                summary[name] = float(value.reshape(-1)[0])
        elif np.isscalar(value):
            summary[name] = float(value)
    return summary


def load_options(run_dir: Path, weights_folder: Path, output_dir: Path, batch_size: int,
                 no_cuda: bool) -> SimpleNamespace:
    opt_path = run_dir / "models" / "opt.json"
    with opt_path.open(encoding="utf-8") as fp:
        options = json.load(fp)

    options["batch_size"] = batch_size
    options["num_workers"] = 0
    options["no_cuda"] = bool(no_cuda or not torch.cuda.is_available())
    options["load_weights_folder"] = str(weights_folder)
    options["models_to_load"] = ["encoder", "depth", "pose_encoder", "pose"]
    options["mypretrain"] = None
    options["log_dir"] = str(output_dir / "_diagnostic_trainer_logs")
    options["model_name"] = "diagnostic_loader"
    options["max_train_steps"] = 0
    options["save_step_frequency"] = 0
    options["log_frequency"] = 1000000
    options["profile"] = False
    return SimpleNamespace(**options)


def save_sample_maps(output_dir: Path, sample_number: int, dataset_index: int,
                     inputs: dict, outputs: dict) -> dict:
    sample_dir = output_dir / f"sample_{dataset_index:04d}"
    sample_dir.mkdir(parents=True, exist_ok=True)

    saved = {}
    rgb = inputs[("color", 0, 0)][sample_number]
    tensor_to_rgb_image(rgb).save(sample_dir / "input_rgb.png")
    saved["input_rgb"] = str(sample_dir / "input_rgb.png")

    depth = outputs[("depth", 0, 0)][sample_number]
    tensor_to_gray_image(depth).save(sample_dir / "pred_depth_gray.png")
    saved["pred_depth_gray"] = str(sample_dir / "pred_depth_gray.png")
    tensor_to_gray_image(1.0 / depth.clamp_min(1e-3)).save(
        sample_dir / "pred_inverse_depth_gray.png")
    saved["pred_inverse_depth_gray"] = str(sample_dir / "pred_inverse_depth_gray.png")

    map_specs = [
        (("photo_error", 0), "photo_error_gray.png"),
        (("temporal_geo_error", 0), "geometry_error_gray.png"),
        (("temporal_geo_visibility", 0), "visibility_mask_gray.png"),
        (("temporal_geo_projection_valid", 0), "projection_valid_gray.png"),
        (("texture_ambiguity", 0), "texture_ambiguity_gray.png"),
        (("feature_consistency_error", 2), "feature_error_gray.png"),
        (("feature_consistency_mask", 2), "feature_mask_gray.png"),
    ]
    for key, filename in map_specs:
        if key in outputs:
            tensor_to_gray_image(outputs[key][sample_number]).save(sample_dir / filename)
            saved[filename[:-4]] = str(sample_dir / filename)
    return saved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render temporal cross-view diagnostic maps for a Milestone 4 run.")
    parser.add_argument("--run_dir", type=Path, required=True)
    parser.add_argument("--weights_folder", type=Path, required=True)
    parser.add_argument("--output_dir", type=Path, required=True)
    parser.add_argument("--sample_indices", nargs="+", type=int, default=[0, 35, 82, 96])
    parser.add_argument("--no_cuda", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    opt = load_options(
        args.run_dir.resolve(),
        args.weights_folder.resolve(),
        args.output_dir.resolve(),
        batch_size=len(args.sample_indices),
        no_cuda=args.no_cuda,
    )

    trainer = Trainer(opt)
    trainer.set_eval()
    trainer.epoch = 0
    trainer.step = 0
    dataset = trainer.val_loader.dataset
    samples = [dataset[index] for index in args.sample_indices]
    inputs = default_collate(samples)

    with torch.no_grad():
        outputs, losses = trainer.process_batch(inputs)

    manifest = {
        "run_dir": str(args.run_dir.resolve()),
        "weights_folder": str(args.weights_folder.resolve()),
        "sample_indices": args.sample_indices,
        "losses": scalar_losses(losses),
        "samples": {},
    }
    for sample_number, dataset_index in enumerate(args.sample_indices):
        manifest["samples"][str(dataset_index)] = save_sample_maps(
            args.output_dir, sample_number, dataset_index, inputs, outputs)

    with (args.output_dir / "diagnostic_visual_manifest.json").open(
            "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2, sort_keys=True)

    print("Saved temporal cross-view diagnostics")
    print(f"  Output: {args.output_dir.resolve()}")
    print(f"  Samples: {', '.join(str(i) for i in args.sample_indices)}")


if __name__ == "__main__":
    main()
