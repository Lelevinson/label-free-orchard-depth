"""Generate paper figures + dump verified numbers, all from on-disk evidence.

Run: D:/Conda_Envs/lite-mono/python.exe make_figures.py   (from the paper/ folder)
No GPU, no model inference — reads result summary JSONs and per-sample CSVs only, so every
plotted value traces to an existing evaluation artifact.
"""
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LEV = Path(__file__).resolve().parents[1]          # levinson/
FIG = Path(__file__).resolve().parent / "figures"
FIG.mkdir(exist_ok=True)
M1 = LEV.parents[1] / "01_original_lite_mono_baseline" / "results"

def load_json(p):
    try:
        return json.load(open(p))
    except Exception as e:
        print("  [miss]", p, e); return None

def med(d, k):
    # summary JSONs store nested dict; find median-scaled metrics block
    for key in ("median_scaled", "median_scaled_metrics", "metrics_median_scaled"):
        if isinstance(d, dict) and key in d:
            return d[key].get(k)
    return d.get(k) if isinstance(d, dict) else None

# ---------- 1. collect main-table summary numbers ----------
SUMMARIES = {
 "Original Lite-Mono": M1 / "test_lite-mono_full_summary.json",
 "B0 plain-Citrus":    LEV / "snapshots/00_plain_citrus_baseline/results/test_lite-mono_full_summary.json",
 "S05 w19":            LEV / "checkpoint_selection/teacher_anchor_snapshot05_06/local_results/test_selected/snapshot05/weights_19/test_lite-mono_full_summary.json",
 "S07 w25":            LEV / "snapshots/07_structure_aware_label_free_vegetation_depth/local_evidence/checkpoint_selection/test_selected/weights_25/test_lite-mono_full_summary.json",
 "S09 TSOB w24":       LEV / "runs/s09_tsob_full_logs/checkpoint_selection/test_selected/weights_24/test_lite-mono_full_summary.json",
 "S10 w29":            LEV / "snapshots/10_ema_self_teacher/results/weights29_test_reverify/test_lite-mono_full_summary.json",
}
print("\n=== MAIN-TABLE NUMBERS (TEST) ===")
print(f"{'model':<20}{'mAbsRel':>9}{'mA1':>8}{'mA2':>8}{'mA3':>8}{'rawAbsRel':>11}{'rawA1':>8}")
for name, p in SUMMARIES.items():
    d = load_json(p)
    if not d:
        continue
    b = d.get("mean_median_scaled_metrics", {})
    rw = d.get("mean_raw_metrics", {})
    g = lambda blk, k: (f"{blk[k]:.4f}" if k in blk and blk[k] is not None else "?")
    print(f"{name:<20}{g(b,'abs_rel'):>9}{g(b,'a1'):>8}{g(b,'a2'):>8}{g(b,'a3'):>8}"
          f"{g(rw,'abs_rel'):>11}{g(rw,'a1'):>8}")

# ---------- helper: load per-sample CSV ----------
def load_ps(p):
    rows = {}
    try:
        for r in csv.DictReader(open(p)):
            rows[int(r["index"])] = r
    except Exception as e:
        print("  [miss ps]", p, e)
    return rows

S10_PS = load_ps(LEV / "snapshots/10_ema_self_teacher/results/weights29_test_reverify/test_lite-mono_full_per_sample.csv")
ORIG_PS = load_ps(M1 / "test_lite-mono_full_per_sample.csv")
S07_PS = load_ps(LEV / "snapshots/07_structure_aware_label_free_vegetation_depth/local_evidence/checkpoint_selection/test_selected/weights_25/test_lite-mono_full_per_sample.csv")

# ---------- F3 error vs scene distance (Original vs S10) ----------
try:
    edges = [1.0, 1.8, 2.4, 3.0, 3.3, 5.0]
    def buck(ps):
        out = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            vals = [float(r["median_scaled_abs_rel"]) for r in ps.values()
                    if lo <= float(r["gt_median"]) < hi]
            out.append(np.mean(vals) if vals else np.nan)
        return out
    labels = [f"{lo:.1f}-{hi:.1f}" for lo, hi in zip(edges[:-1], edges[1:])]
    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.bar(x - w/2, buck(ORIG_PS), w, label="Original Lite-Mono", color="#999999")
    ax.bar(x + w/2, buck(S10_PS), w, label="S10 (ours)", color="#2a7fb8")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel("scene distance: median LiDAR depth of labeled pixels (m)")
    ax.set_ylabel("median-scaled abs_rel")
    ax.set_title("Error concentrates in near-range / open-clearing scenes")
    ax.legend(); fig.tight_layout(); fig.savefig(FIG/"fig_error_vs_distance.png", dpi=160)
    plt.close(fig); print("[ok] fig_error_vs_distance.png")
except Exception as e:
    print("[F3 fail]", e)

# ---------- F4 ground-vs-vegetation error split (from autopsy note numbers) ----------
try:
    # values from diagnostics/failure_autopsy_2026-06-11.md (ExG split, full 407-frame test)
    groups = ["Vegetation pixels", "Ground pixels"]
    orig = [0.3680, 0.3824]; s10 = [0.3335, 0.2993]
    x = np.arange(len(groups)); w = 0.38
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.bar(x - w/2, orig, w, label="Original", color="#999999")
    ax.bar(x + w/2, s10, w, label="S10 (ours)", color="#2a7fb8")
    for i, (o, s) in enumerate(zip(orig, s10)):
        ax.text(i - w/2, o+0.005, f"{o:.3f}", ha="center", fontsize=8)
        ax.text(i + w/2, s+0.005, f"{s:.3f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel("median-scaled abs_rel"); ax.set_ylim(0, 0.45)
    ax.set_title("S10 gains come mostly from ground (labels are ~84% ground)")
    ax.legend(); fig.tight_layout(); fig.savefig(FIG/"fig_ground_vs_veg.png", dpi=160)
    plt.close(fig); print("[ok] fig_ground_vs_veg.png")
except Exception as e:
    print("[F4 fail]", e)

# ---------- F5 EMA gate keep-ratio trace (gates near-inert) ----------
try:
    sc = LEV / "snapshots/10_ema_self_teacher/diagnostics/ema_distill_scalars_train.csv"
    from collections import defaultdict
    series = defaultdict(list)
    for r in csv.DictReader(open(sc)):
        series[r["tag"]].append((int(r["step"]), float(r["value"])))
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for tag, lab, col in [("ema_distill/keep_ratio", "overall keep-ratio", "#2a7fb8"),
                          ("ema_distill/keep_ratio_canopy", "lower-image (canopy-proxy) keep-ratio", "#d1701f")]:
        pts = sorted(series.get(tag, []))
        if pts:
            ax.plot([s for s, _ in pts], [v for _, v in pts], label=lab, color=col)
    ax.axhspan(0.2, 0.8, color="green", alpha=0.08, label="design target band 0.2-0.8")
    ax.set_xlabel("training step"); ax.set_ylabel("fraction of pixels kept by DC$\\wedge$GC gates")
    ax.set_ylim(0, 1.0); ax.set_title("Reliability gates were near-inert (~88% kept)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(FIG/"fig_keep_ratio.png", dpi=160)
    plt.close(fig); print("[ok] fig_keep_ratio.png")
except Exception as e:
    print("[F5 fail]", e)

# ---------- F6 per-epoch validation curve ----------
try:
    sweep = LEV / "snapshots/10_ema_self_teacher/results/validation_sweep.csv"
    ep, ar, a1 = [], [], []
    for r in csv.DictReader(open(sweep)):
        ep.append(int(r["epoch"])); ar.append(float(r["median_scaled_abs_rel"]))
        a1.append(float(r["median_scaled_a1"]))
    fig, ax1 = plt.subplots(figsize=(6.4, 3.2))
    ax1.plot(ep, ar, color="#2a7fb8", marker="o", ms=3, label="val abs_rel")
    ax1.set_xlabel("epoch"); ax1.set_ylabel("median-scaled abs_rel", color="#2a7fb8")
    ax2 = ax1.twinx(); ax2.plot(ep, a1, color="#d1701f", marker="s", ms=3, label="val a1")
    ax2.set_ylabel("median-scaled a1", color="#d1701f")
    ax1.set_title("S10 validation over training (epoch 2 = early scale artifact)")
    fig.tight_layout(); fig.savefig(FIG/"fig_val_curve.png", dpi=160)
    plt.close(fig); print("[ok] fig_val_curve.png")
except Exception as e:
    print("[F6 fail]", e)

# ---------- F7 S11 collapse scatter ----------
try:
    s11 = load_ps(LEV / "runs/s11_crop_logs/gate_eval_r2/weights_6/val_lite-mono_full_per_sample.csv")
    gt = [float(r["gt_median"]) for r in s11.values()]
    pm = [float(r["pred_median"]) for r in s11.values()]
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    ax.scatter(gt, pm, s=8, alpha=0.5, color="#b03030")
    ax.set_xlabel("ground-truth median depth (m)")
    ax.set_ylabel("predicted median depth (m)")
    ax.set_title("S11 collapse: prediction constant (~0.20 m) regardless of scene")
    ax.set_ylim(0, max(0.3, max(pm)*1.1))
    fig.tight_layout(); fig.savefig(FIG/"fig_s11_collapse.png", dpi=160)
    plt.close(fig); print("[ok] fig_s11_collapse.png")
    print(f"  S11 pred_median range: {min(pm):.4f}-{max(pm):.4f}; gt range {min(gt):.2f}-{max(gt):.2f}")
except Exception as e:
    print("[F7 fail]", e)

# ---------- per-frame win/loss S10 vs S07 (numbers for table) ----------
try:
    common = set(S10_PS) & set(S07_PS)
    d_ar = [float(S10_PS[i]["median_scaled_abs_rel"]) - float(S07_PS[i]["median_scaled_abs_rel"]) for i in common]
    d_a1 = [float(S10_PS[i]["median_scaled_a1"]) - float(S07_PS[i]["median_scaled_a1"]) for i in common]
    n = len(common)
    print("\n=== PER-FRAME S10 vs S07 (test) ===")
    print(f"frames {n}; S10 better abs_rel {sum(1 for d in d_ar if d<0)}/{n} "
          f"({100*sum(1 for d in d_ar if d<0)/n:.1f}%); mean d_abs_rel {np.mean(d_ar):+.4f}; "
          f"S10 better a1 {sum(1 for d in d_a1 if d>0)}/{n} ({100*sum(1 for d in d_a1 if d>0)/n:.1f}%)")
except Exception as e:
    print("[winloss fail]", e)

print("\nfigures in", FIG)
