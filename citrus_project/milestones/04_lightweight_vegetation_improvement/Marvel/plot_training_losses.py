import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


DEFAULT_TAGS = [
    "loss",
    "loss/0",
    "boundary_loss/0",
    "boundary_loss_weighted/0",
    "smooth_loss/0",
    "de/abs_rel",
    "da/a1",
]


def read_scalars(csv_path):
    values = defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            try:
                step = int(row["step"])
                value = float(row["value"])
            except (KeyError, TypeError, ValueError):
                continue
            values[row["tag"]].append((step, value))
    return values


def plot_tags(scalars, tags, output_path, title):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plotted = 0

    plt.figure(figsize=(11, 6))
    for tag in tags:
        points = scalars.get(tag, [])
        if not points:
            continue
        xs, ys = zip(*points)
        plt.plot(xs, ys, marker="o", markersize=2, linewidth=1.5, label=tag)
        plotted += 1

    if plotted == 0:
        raise ValueError(
            "None of the requested tags were found. Available tags: {}".format(
                ", ".join(sorted(scalars.keys()))))

    plt.title(title)
    plt.xlabel("Training step")
    plt.ylabel("Scalar value")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot Lite-Mono CSV scalar logs written by trainer.py.")
    parser.add_argument(
        "--run_dir",
        type=Path,
        required=True,
        help="Training run directory containing train_scalars.csv / val_scalars.csv.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=None,
        help="Output folder for PNG plots. Defaults to <run_dir>/plots.",
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        default=DEFAULT_TAGS,
        help="Scalar tags to include in the combined plots.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run_dir = args.run_dir.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else run_dir / "plots"

    for mode in ["train", "val"]:
        csv_path = run_dir / "{}_scalars.csv".format(mode)
        if not csv_path.exists():
            print("Skipping missing scalar file:", csv_path)
            continue
        scalars = read_scalars(csv_path)
        plot_tags(
            scalars,
            args.tags,
            output_dir / "{}_loss_curves.png".format(mode),
            "{} loss curves: {}".format(mode.title(), run_dir.name),
        )
        print("Wrote", output_dir / "{}_loss_curves.png".format(mode))


if __name__ == "__main__":
    main()
