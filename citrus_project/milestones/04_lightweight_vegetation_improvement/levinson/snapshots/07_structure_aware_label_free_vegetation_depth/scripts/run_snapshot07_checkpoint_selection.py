from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[7]
EVAL_SCRIPT = (
    REPO_ROOT
    / "citrus_project"
    / "milestones"
    / "01_original_lite_mono_baseline"
    / "evaluate_lite_mono_citrus.py"
)
LEVINSON_ROOT = (
    REPO_ROOT
    / "citrus_project"
    / "milestones"
    / "04_lightweight_vegetation_improvement"
    / "levinson"
)
SNAPSHOT_ROOT = (
    LEVINSON_ROOT
    / "snapshots"
    / "07_structure_aware_label_free_vegetation_depth"
)
DEFAULT_MODELS_DIR = (
    LEVINSON_ROOT
    / "runs"
    / "structure_aware_label_free_vegetation_depth_b12_30ep_full"
    / "models"
)
B0_VAL_SUMMARY = (
    LEVINSON_ROOT
    / "snapshots"
    / "00_plain_citrus_baseline"
    / "results"
    / "val_lite-mono_full_summary.json"
)


def checkpoint_epoch(path: Path) -> int:
    try:
        return int(path.name.split("_", maxsplit=1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Unexpected checkpoint folder name: {path}") from exc


def checkpoint_dirs(models_dir: Path) -> List[Path]:
    return sorted(
        [
            path
            for path in models_dir.iterdir()
            if path.is_dir() and path.name.startswith("weights_")
        ],
        key=checkpoint_epoch,
    )


def summary_path(output_dir: Path, split: str) -> Path:
    return output_dir / f"{split}_lite-mono_full_summary.json"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fp:
        return json.load(fp)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
        fp.write("\n")


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_eval(
    python_exe: str,
    split: str,
    checkpoint: Path,
    output_dir: Path,
    progress_interval: int,
    force: bool,
) -> None:
    if summary_path(output_dir, split).exists() and not force:
        print(f"[skip] {split} {checkpoint.name}: {summary_path(output_dir, split)}")
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        python_exe,
        str(EVAL_SCRIPT),
        "--split",
        split,
        "--max_samples",
        "0",
        "--run_model",
        "--summary_only",
        "--progress_interval",
        str(progress_interval),
        "--weights_folder",
        str(checkpoint),
        "--model",
        "lite-mono",
        "--output_dir",
        str(output_dir),
    ]
    print(f"[eval] {split} {checkpoint}")
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def metrics_from_summary(checkpoint: Path, split: str, output_dir: Path) -> Dict[str, object]:
    data = read_json(summary_path(output_dir, split))
    raw = data["mean_raw_metrics"]
    med = data["mean_median_scaled_metrics"]
    return {
        "checkpoint": checkpoint.name,
        "epoch": checkpoint_epoch(checkpoint),
        "split": split,
        "samples": data["samples_with_metrics"],
        "raw_abs_rel": raw["abs_rel"],
        "raw_a1": raw["a1"],
        "median_scaled_abs_rel": med["abs_rel"],
        "median_scaled_a1": med["a1"],
        "median_scaled_a2": med["a2"],
        "median_scaled_a3": med["a3"],
        "median_scale_ratio": data["median_scale_ratio"],
        "model_forward_fps": data["timing"]["model_forward_fps"],
        "weights_folder": str(checkpoint),
        "summary_json": str(summary_path(output_dir, split)),
    }


def select_checkpoint(
    val_rows: List[Dict[str, object]],
    b0_val_a1: float,
    a1_margin: float,
) -> Dict[str, object]:
    threshold = b0_val_a1 - a1_margin
    candidates = [
        row for row in val_rows
        if float(row["median_scaled_a1"]) >= threshold
    ]
    pool = candidates if candidates else val_rows
    selected = min(
        pool,
        key=lambda row: (
            float(row["median_scaled_abs_rel"]),
            -float(row["median_scaled_a1"]),
            int(row["epoch"]),
        ),
    )
    selected = dict(selected)
    selected["b0_val_a1"] = b0_val_a1
    selected["a1_margin"] = a1_margin
    selected["a1_close_threshold"] = threshold
    selected["a1_close_passed"] = bool(candidates)
    selected["selection_rule"] = (
        "lowest full-validation median_scaled_abs_rel among checkpoints with "
        "median_scaled_a1 >= B0_val_a1 - a1_margin; fallback to lowest abs_rel "
        "if no checkpoint qualifies"
    )
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validation-first checkpoint selection for Snapshot 07.")
    parser.add_argument("--models_dir", type=Path, default=DEFAULT_MODELS_DIR)
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=SNAPSHOT_ROOT / "local_evidence" / "checkpoint_selection",
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--a1_margin", type=float, default=0.02)
    parser.add_argument("--progress_interval", type=int, default=100)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip_eval", action="store_true")
    args = parser.parse_args()

    models_dir = args.models_dir.resolve()
    output_dir = args.output_dir.resolve()
    b0_val_a1 = float(
        read_json(B0_VAL_SUMMARY)["mean_median_scaled_metrics"]["a1"])

    val_rows: List[Dict[str, object]] = []
    checkpoints = checkpoint_dirs(models_dir)
    if not checkpoints:
        raise FileNotFoundError(f"No weights_* checkpoints found in {models_dir}")

    for checkpoint in checkpoints:
        val_output = output_dir / "validation" / checkpoint.name
        if not args.skip_eval:
            run_eval(
                args.python,
                "val",
                checkpoint,
                val_output,
                args.progress_interval,
                args.force,
            )
        val_rows.append(metrics_from_summary(checkpoint, "val", val_output))

    selected_val = select_checkpoint(val_rows, b0_val_a1, args.a1_margin)
    selected_checkpoint = models_dir / selected_val["checkpoint"]
    selected_test_output = (
        output_dir / "test_selected" / selected_val["checkpoint"])
    if not args.skip_eval:
        run_eval(
            args.python,
            "test",
            selected_checkpoint,
            selected_test_output,
            args.progress_interval,
            args.force,
        )
    selected_test = metrics_from_summary(
        selected_checkpoint, "test", selected_test_output)

    write_csv(output_dir / "validation_sweep.csv", val_rows)
    write_json(output_dir / "validation_sweep.json", val_rows)
    write_json(output_dir / "selected_validation_checkpoint.json", selected_val)
    write_csv(output_dir / "selected_validation_checkpoint.csv", [selected_val])
    write_json(output_dir / "selected_test_result.json", selected_test)
    write_csv(output_dir / "selected_test_result.csv", [selected_test])
    write_json(
        output_dir / "selection_rule.json",
        {
            "b0_validation_median_scaled_a1": b0_val_a1,
            "a1_margin": args.a1_margin,
            "a1_close_threshold": b0_val_a1 - args.a1_margin,
            "test_set_used_for_selection": False,
            "rule": selected_val["selection_rule"],
        },
    )

    print("\nSelected Snapshot 07 checkpoint:")
    print(
        "  {checkpoint}: val med_abs={abs_rel:.4f}, val med_a1={a1:.4f}, "
        "a1_close_passed={passed}".format(
            checkpoint=selected_val["checkpoint"],
            abs_rel=float(selected_val["median_scaled_abs_rel"]),
            a1=float(selected_val["median_scaled_a1"]),
            passed=selected_val["a1_close_passed"],
        )
    )
    print(
        "  test med_abs={abs_rel:.4f}, test med_a1={a1:.4f}".format(
            abs_rel=float(selected_test["median_scaled_abs_rel"]),
            a1=float(selected_test["median_scaled_a1"]),
        )
    )
    print(f"\nWrote Snapshot 07 selection outputs to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
