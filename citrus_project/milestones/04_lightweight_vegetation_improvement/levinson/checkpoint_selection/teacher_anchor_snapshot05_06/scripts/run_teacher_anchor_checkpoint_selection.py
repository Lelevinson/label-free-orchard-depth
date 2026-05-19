from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[5]
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
DEFAULT_OUTPUT = (
    LEVINSON_ROOT
    / "results"
    / "teacher_anchor_checkpoint_selection_snapshot05_06"
)
B0_VAL_SUMMARY = (
    LEVINSON_ROOT
    / "snapshots"
    / "00_plain_citrus_baseline"
    / "results"
    / "val_lite-mono_full_summary.json"
)


@dataclass(frozen=True)
class RunSpec:
    name: str
    label: str
    models_dir: Path


RUNS = [
    RunSpec(
        name="snapshot05",
        label="Snapshot 05",
        models_dir=LEVINSON_ROOT
        / "runs"
        / "teacher_structure_regularization_b12_30ep_full"
        / "models",
    ),
    RunSpec(
        name="snapshot06",
        label="Snapshot 06",
        models_dir=LEVINSON_ROOT
        / "runs"
        / "teacher_anchor_stabilization_b12_30ep_rank005_no_texture"
        / "models",
    ),
]


def checkpoint_epoch(path: Path) -> int:
    try:
        return int(path.name.split("_", maxsplit=1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Unexpected checkpoint folder name: {path}") from exc


def checkpoint_dirs(models_dir: Path) -> List[Path]:
    dirs = [
        path
        for path in models_dir.iterdir()
        if path.is_dir() and path.name.startswith("weights_")
    ]
    return sorted(dirs, key=checkpoint_epoch)


def summary_path(output_dir: Path, split: str, checkpoint: Path) -> Path:
    max_tag = "full"
    return output_dir / f"{split}_lite-mono_{max_tag}_summary.json"


def run_eval(
    python_exe: str,
    split: str,
    checkpoint: Path,
    output_dir: Path,
    force: bool,
    progress_interval: int,
) -> None:
    summary = summary_path(output_dir, split, checkpoint)
    if summary.exists() and not force:
        print(f"[skip] {split} {checkpoint.name}: {summary}")
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


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fp:
        return json.load(fp)


def extract_metrics(run: RunSpec, checkpoint: Path, split: str, output_dir: Path) -> Dict[str, object]:
    data = read_json(summary_path(output_dir, split, checkpoint))
    raw = data["mean_raw_metrics"]
    med = data["mean_median_scaled_metrics"]
    return {
        "run": run.name,
        "label": run.label,
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
        "scale_ratio_median": data["median_scale_ratio"],
        "model_forward_fps": data["timing"]["model_forward_fps"],
        "weights_folder": str(checkpoint),
        "summary_json": str(summary_path(output_dir, split, checkpoint)),
    }


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
        fp.write("\n")


def select_checkpoint(
    rows: Iterable[Dict[str, object]],
    b0_val_a1: float,
    a1_margin: float,
) -> Dict[str, object]:
    rows = list(rows)
    threshold = b0_val_a1 - a1_margin
    candidates = [
        row for row in rows if float(row["median_scaled_a1"]) >= threshold
    ]
    pool = candidates if candidates else rows
    selected = min(
        pool,
        key=lambda row: (
            float(row["median_scaled_abs_rel"]),
            -float(row["median_scaled_a1"]),
            int(row["epoch"]),
        ),
    )
    selected = dict(selected)
    selected["a1_close_threshold"] = threshold
    selected["a1_close_passed"] = bool(candidates)
    selected["selection_rule"] = (
        "lowest validation median_scaled_abs_rel among checkpoints with "
        f"median_scaled_a1 >= B0_val_a1 - {a1_margin:.3f}; "
        "fallback to lowest abs_rel if none qualify"
    )
    return selected


def collect_baseline_rows() -> List[Dict[str, object]]:
    return [
        {
            "model": "Original Lite-Mono",
            "split": "val",
            "raw_abs_rel": 0.7128,
            "raw_a1": 0.0195,
            "median_scaled_abs_rel": 0.4176,
            "median_scaled_a1": 0.4629,
            "notes": "original RGB-only Lite-Mono checkpoint",
        },
        {
            "model": "B0 plain Citrus",
            "split": "val",
            "raw_abs_rel": 0.7736,
            "raw_a1": 0.0074,
            "median_scaled_abs_rel": 0.5100,
            "median_scaled_a1": 0.6107,
            "notes": "plain Citrus baseline, final weights_29",
        },
        {
            "model": "Snapshot 05 weights_29",
            "split": "val",
            "raw_abs_rel": 0.7372,
            "raw_a1": 0.0169,
            "median_scaled_abs_rel": 0.4611,
            "median_scaled_a1": 0.5954,
            "notes": "reported final checkpoint",
        },
        {
            "model": "Snapshot 06 weights_29",
            "split": "val",
            "raw_abs_rel": 0.7375,
            "raw_a1": 0.0165,
            "median_scaled_abs_rel": 0.4578,
            "median_scaled_a1": 0.5993,
            "notes": "reported final checkpoint",
        },
        {
            "model": "Original Lite-Mono",
            "split": "test",
            "raw_abs_rel": 0.7273,
            "raw_a1": 0.0149,
            "median_scaled_abs_rel": 0.3836,
            "median_scaled_a1": 0.4989,
            "notes": "original RGB-only Lite-Mono checkpoint",
        },
        {
            "model": "B0 plain Citrus",
            "split": "test",
            "raw_abs_rel": 0.7787,
            "raw_a1": 0.0077,
            "median_scaled_abs_rel": 0.4889,
            "median_scaled_a1": 0.6582,
            "notes": "plain Citrus baseline, final weights_29",
        },
        {
            "model": "Snapshot 05 weights_29",
            "split": "test",
            "raw_abs_rel": 0.7359,
            "raw_a1": 0.0147,
            "median_scaled_abs_rel": 0.4132,
            "median_scaled_a1": 0.6463,
            "notes": "reported final checkpoint",
        },
        {
            "model": "Snapshot 06 weights_29",
            "split": "test",
            "raw_abs_rel": 0.7348,
            "raw_a1": 0.0150,
            "median_scaled_abs_rel": 0.4168,
            "median_scaled_a1": 0.6418,
            "notes": "reported final checkpoint",
        },
    ]


def comparison_rows(
    selected_val: List[Dict[str, object]],
    selected_test: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    rows = collect_baseline_rows()
    for val_row in selected_val:
        rows.append(
            {
                "model": f"{val_row['label']} validation-selected {val_row['checkpoint']}",
                "split": "val",
                "raw_abs_rel": val_row["raw_abs_rel"],
                "raw_a1": val_row["raw_a1"],
                "median_scaled_abs_rel": val_row["median_scaled_abs_rel"],
                "median_scaled_a1": val_row["median_scaled_a1"],
                "notes": "selected without test-set access",
            }
        )
    for test_row in selected_test:
        rows.append(
            {
                "model": f"{test_row['label']} validation-selected {test_row['checkpoint']}",
                "split": "test",
                "raw_abs_rel": test_row["raw_abs_rel"],
                "raw_a1": test_row["raw_a1"],
                "median_scaled_abs_rel": test_row["median_scaled_abs_rel"],
                "median_scaled_a1": test_row["median_scaled_a1"],
                "notes": "test evaluated after validation selection",
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validation-first checkpoint selection for Snapshot 05 and Snapshot 06."
    )
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip_eval", action="store_true")
    parser.add_argument("--a1_margin", type=float, default=0.02)
    parser.add_argument("--progress_interval", type=int, default=100)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    val_rows: List[Dict[str, object]] = []
    selected_val: List[Dict[str, object]] = []
    selected_test: List[Dict[str, object]] = []

    b0_val = read_json(B0_VAL_SUMMARY)
    b0_val_a1 = float(b0_val["mean_median_scaled_metrics"]["a1"])

    for run in RUNS:
        checkpoints = checkpoint_dirs(run.models_dir)
        if not checkpoints:
            raise FileNotFoundError(f"No checkpoints found in {run.models_dir}")
        for checkpoint in checkpoints:
            ckpt_output = output_dir / "validation" / run.name / checkpoint.name
            if not args.skip_eval:
                run_eval(
                    args.python,
                    "val",
                    checkpoint,
                    ckpt_output,
                    args.force,
                    args.progress_interval,
                )
            val_rows.append(extract_metrics(run, checkpoint, "val", ckpt_output))

        run_val_rows = [row for row in val_rows if row["run"] == run.name]
        selected = select_checkpoint(run_val_rows, b0_val_a1, args.a1_margin)
        selected_val.append(selected)

    write_csv(output_dir / "validation_sweep.csv", val_rows)
    write_json(output_dir / "validation_sweep.json", val_rows)
    write_json(
        output_dir / "selection_rule.json",
        {
            "rule": (
                "For each run, select the checkpoint with lowest validation "
                "median_scaled_abs_rel among checkpoints with validation "
                "median_scaled_a1 within the specified absolute margin of B0. "
                "If no checkpoint qualifies, select the lowest validation "
                "median_scaled_abs_rel checkpoint and flag the a1 miss."
            ),
            "b0_validation_median_scaled_a1": b0_val_a1,
            "a1_margin": args.a1_margin,
            "a1_close_threshold": b0_val_a1 - args.a1_margin,
            "test_set_used_for_selection": False,
        },
    )
    write_json(output_dir / "selected_validation_checkpoints.json", selected_val)
    write_csv(output_dir / "selected_validation_checkpoints.csv", selected_val)

    for selected in selected_val:
        run = next(item for item in RUNS if item.name == selected["run"])
        checkpoint = run.models_dir / str(selected["checkpoint"])
        test_output = output_dir / "test_selected" / run.name / str(selected["checkpoint"])
        if not args.skip_eval:
            run_eval(
                args.python,
                "test",
                checkpoint,
                test_output,
                args.force,
                args.progress_interval,
            )
        selected_test.append(extract_metrics(run, checkpoint, "test", test_output))

    write_json(output_dir / "selected_test_results.json", selected_test)
    write_csv(output_dir / "selected_test_results.csv", selected_test)

    comparison = comparison_rows(selected_val, selected_test)
    write_csv(output_dir / "comparison_summary.csv", comparison)
    write_json(output_dir / "comparison_summary.json", comparison)

    print("\nSelected validation checkpoints:")
    for row in selected_val:
        print(
            f"  {row['label']}: {row['checkpoint']} "
            f"val med_abs={float(row['median_scaled_abs_rel']):.4f}, "
            f"val med_a1={float(row['median_scaled_a1']):.4f}, "
            f"a1_close_passed={row['a1_close_passed']}"
        )
    print(f"\nWrote sweep outputs to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
