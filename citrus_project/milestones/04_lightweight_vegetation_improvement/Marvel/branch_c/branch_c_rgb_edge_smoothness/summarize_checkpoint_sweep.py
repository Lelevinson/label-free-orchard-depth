from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


METRIC_GROUPS = {
    "raw": "mean_raw_metrics",
    "median": "mean_median_scaled_metrics",
}


def checkpoint_index(name: str) -> int:
    return int(name.replace("weights_", ""))


def read_summary(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def row_from_summary(checkpoint: str, split: str, summary: dict) -> dict:
    row = {
        "checkpoint": checkpoint,
        "checkpoint_index": checkpoint_index(checkpoint),
        "split": split,
        "samples": summary.get("samples_with_metrics"),
        "mean_valid_fraction": summary.get("mean_valid_fraction"),
        "median_scale_ratio": summary.get("median_scale_ratio"),
        "mean_scale_ratio": summary.get("mean_scale_ratio"),
    }
    for prefix, key in METRIC_GROUPS.items():
        metrics = summary.get(key, {})
        row[f"{prefix}_abs_rel"] = metrics.get("abs_rel")
        row[f"{prefix}_sq_rel"] = metrics.get("sq_rel")
        row[f"{prefix}_rmse"] = metrics.get("rmse")
        row[f"{prefix}_rmse_log"] = metrics.get("rmse_log")
        row[f"{prefix}_a1"] = metrics.get("a1")
        row[f"{prefix}_a2"] = metrics.get("a2")
        row[f"{prefix}_a3"] = metrics.get("a3")
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_root", required=True, type=Path)
    parser.add_argument("--split", required=True)
    parser.add_argument("--output_csv", required=True, type=Path)
    parser.add_argument("--output_json", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    for checkpoint_dir in sorted(args.input_root.glob("weights_*"), key=lambda p: checkpoint_index(p.name)):
        summary_path = checkpoint_dir / f"{args.split}_lite-mono_full_summary.json"
        if not summary_path.exists():
            continue
        rows.append(row_from_summary(checkpoint_dir.name, args.split, read_summary(summary_path)))

    if not rows:
        raise RuntimeError(f"No {args.split} summaries found under {args.input_root}")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    ranked_raw = sorted(rows, key=lambda r: (float(r["raw_abs_rel"]), -float(r["raw_a1"])))
    ranked_median = sorted(rows, key=lambda r: (float(r["median_abs_rel"]), -float(r["median_a1"])))

    output = {
        "split": args.split,
        "num_checkpoints": len(rows),
        "best_by_raw_abs_rel": ranked_raw[0],
        "best_by_median_abs_rel": ranked_median[0],
        "top5_by_raw_abs_rel": ranked_raw[:5],
        "top5_by_median_abs_rel": ranked_median[:5],
        "rows": rows,
    }
    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {args.output_csv}")
    print(f"Wrote {args.output_json}")
    print(
        "Best raw abs_rel:",
        ranked_raw[0]["checkpoint"],
        ranked_raw[0]["raw_abs_rel"],
        "raw a1:",
        ranked_raw[0]["raw_a1"],
    )
    print(
        "Best median abs_rel:",
        ranked_median[0]["checkpoint"],
        ranked_median[0]["median_abs_rel"],
        "median a1:",
        ranked_median[0]["median_a1"],
    )


if __name__ == "__main__":
    main()
