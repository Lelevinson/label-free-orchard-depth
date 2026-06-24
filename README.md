<div align="center">

# Toward Label-Free Lightweight Monocular Depth in Orchards

**In-domain self-distillation and an anatomy of domain shift — a label-free, RGB-only depth study, built on [Lite-Mono](https://github.com/noahzn/Lite-Mono) and validated on a citrus orchard.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
![Backbone: Lite-Mono ~3M](https://img.shields.io/badge/backbone-Lite--Mono%20~3M-success)
![Training: label-free](https://img.shields.io/badge/training-label--free%20%7C%20RGB--only-orange)
![Status: research draft](https://img.shields.io/badge/status-research%20draft-lightgrey)

</div>

> **What this is.** A study of how to improve a lightweight, single-camera, *self-supervised*
> depth network for **vegetation-dense agricultural scenes** (validated on the **CitrusFarm** orchard
> dataset), built on Lite-Mono — under two hard constraints: training stays **label-free / RGB-only**,
> and **inference is unchanged** (the same ~3M-parameter network runs on a single RGB image). Our
> method is the first in this study to *beat* the original Lite-Mono on overall error while keeping
> threshold accuracy well above it — at **zero extra inference cost.**

---

## Table of Contents
- [Highlights](#highlights)
- [Key result](#key-result)
- [Method at a glance](#method-at-a-glance)
- [Repository structure](#repository-structure)
- [Getting started](#getting-started)
- [Reproducing the results](#reproducing-the-results)
- [Honest scope and limitations](#honest-scope-and-limitations)
- [Experiment lineage](#experiment-lineage)
- [Team](#team)
- [Acknowledgements](#acknowledgements)
- [License](#license)
- [Citation](#citation)

---

## Highlights
- 🌳 **Domain.** Depth estimation in a citrus orchard (CitrusFarm), where repeated foliage, weak
  texture, wind, open clearings, and sky make standard (urban-trained) self-supervised depth struggle.
- 🧠 **Idea.** An **in-domain EMA self-teacher**: a slowly-updated exponential-moving-average copy of
  the student model — which learns the orchard as training proceeds — distills its predictions back
  into the student, using a **scale-and-shift-invariant (SI-log)** metric term plus a
  normalized-structure anchor.
- 🪶 **Free at inference.** The teacher and all training losses are discarded after training; the
  deployed model is the unmodified single-image, RGB-only, ~3M-parameter network.
- 🔬 **Honest by construction.** We report what did *not* work (a documented lineage of negative
  results), a diagnosed failure mode (the image-row→depth "ground-ramp" shortcut), and the fact that
  the reliability gates turned out near-inert — all tied to on-disk evaluation artifacts.

## Key result
CitrusFarm Sequence 01, test split, **median-scaled** metrics (training is label-free; LiDAR depth is
evaluation-only). Lower `abs_rel` is better; higher `δ` is better.

| Method | `abs_rel` ↓ | `δ₁` ↑ | `δ₂` ↑ | `δ₃` ↑ |
|---|:---:|:---:|:---:|:---:|
| Original Lite-Mono (baseline) | 0.3836 | 0.4989 | 0.7264 | 0.8700 |
| S07 (previous best, structure-aware) | 0.3840 | **0.6539** | 0.8407 | 0.9105 |
| **S10 — in-domain EMA self-teacher (ours)** | **0.3080** | 0.6258 | 0.8118 | 0.9005 |

**S10 is the first method in our label-free line to beat the original on `abs_rel`** (0.3080 vs
0.3836, ≈20% relative) while keeping `δ₁` far above it (0.6258 vs 0.4989, ≈25% relative). Versus our
previous best (S07) it wins `abs_rel` by a wide margin for a small, honestly-reported `δ₁` give-back.
The headline number was independently re-verified from the preserved checkpoint.

## Method at a glance
S10 = a structure-aware self-supervised stack (S07) **+ one training-only loss**: an EMA copy of the
student (no gradient) supplies a target depth, and the student is nudged to agree with it via

1. a **scale-and-shift-invariant SI-log** term — the part that actually moves median-scaled `abs_rel`
   (a purely normalized structure term is invisible to median scaling and can only *tie* it); and
2. a **normalized-structure anchor** — protects relative structure / threshold accuracy.

Two reliability gates (DC flip-consistency, GC min-reprojection) are designed to mask unreliable
pixels; in practice they were near-inert, so the gain comes from *near-dense* self-distillation
(reported transparently).

## Repository structure
```
.
├── README.md
├── train.py, trainer.py, options.py, evaluate_depth.py, test_simple.py
├── networks/, layers.py, kitti_utils.py, utils.py   # model + training code
├── weights/lite-mono/    # original Lite-Mono inference weights (baseline)
├── environment*.yml      # Conda environments
└── citrus_project/       # project-owned research
    ├── README.md, TASK_BOARD.md, TEAM_WORKFLOW.md
    ├── dataset_workspace/   # prepared CitrusFarm frames + eval labels (local, not tracked)
    ├── research/            # notes, literature, paper-support material
    └── milestones/
        └── 04_lightweight_vegetation_improvement/levinson/
            └── snapshots/   # S00–S11: design notes, code, checkpoints, results, diagnostics
```

## Getting started
**Environment.** Create the conda environment and install the LR-scheduler dependency:
```bash
conda env create -f environment.yml      # or environment.cpu.yml / environment.macos.yml
pip install 'git+https://github.com/saadnaeem-dev/pytorch-linear-warmup-cosine-annealing-warm-restarts-weight-decay'
```
Development was done on a single 8 GB RTX 4060, batch size 12, 640×192, 30 epochs (~24–28 h per full
run). For the original Lite-Mono usage (KITTI training/testing), see the upstream project:
<https://github.com/noahzn/Lite-Mono>.

## Reproducing the results
Trained inference weights (`encoder.pth` + `depth.pth`) are committed for the key models:

| Model | Path |
|---|---|
| Original Lite-Mono | `weights/lite-mono/` |
| B0 (plain Citrus fine-tune) | `citrus_project/.../levinson/snapshots/00_plain_citrus_baseline/checkpoint/` |
| S07 (previous best) | `.../snapshots/07_structure_aware_label_free_vegetation_depth/checkpoint/` |
| **S10 (hero)** | `.../snapshots/10_ema_self_teacher/checkpoint/` |

Each snapshot folder carries its own `DESIGN_NOTE.md`, `results/`, `diagnostics/`, and the exact
flags/commands used. The S10 training flags are off-by-default (`--ema_self_distillation
--ema_filter_adaptive`). For the evaluation protocol and current commands, see the snapshot result
summaries under each `snapshots/*/results/`.

## Honest scope and limitations
- **Metrics, not visuals.** S10 improves accuracy; sky/far-canopy confusion and canopy over-smoothing
  remain visually unsolved.
- **Near-inert gates.** The DC/GC reliability gates kept ~88% of pixels throughout; the gain is from
  broad SI-log self-distillation, not selective gating (an ablation isolating the gates was not run).
- **Single domain.** All results are CitrusFarm Sequence 01; generalization is unverified.
- **Evaluation labels** are project-derived from LiDAR (projection + densification), not an official
  ground-truth product, and cover ~37% of pixels — used for evaluation only, never in training.

## Experiment lineage
A fixed training recipe is held across all snapshots so comparisons isolate the objective change:

| Stage | Mechanism (training-only, label-free) | Verdict |
|---|---|---|
| B0 | plain Citrus fine-tune | high `δ₁`, poor `abs_rel` |
| S01–S04 | confidence / edge / temporal cues | negative / weak gates |
| S05–S06 | teacher-anchored structure regularization | promising / marginal |
| S07 | structure-aware + sky/far prior | previous best |
| S08–S09 | feature-metric / boundary-uncertainty (sharpening) | negative |
| **S10** | **in-domain EMA self-teacher** | **best (hero)** |
| S11 | resizing-crop self-distillation | negative (flat-depth collapse) |

## Team
- **Carlene Amelya** — Yuan Ze University
- **Levinson** — Yuan Ze University *(label-free / self-supervised workstream — this result)*
- **Marvel Aiken** — Yuan Ze University *(supervised / hybrid workstream)*

## Acknowledgements
- **[Lite-Mono](https://github.com/noahzn/Lite-Mono)** (Zhang et al., CVPR 2023) — the backbone,
  baseline, and training code this project builds on.
- **[Monodepth2](https://github.com/nianticlabs/monodepth2)** (Godard et al., ICCV 2019) — the
  self-supervised photometric recipe.
- The **CitrusFarm** dataset authors for the orchard RGB + LiDAR data used as our validation domain.

## License
Released under the **MIT License**, consistent with upstream Lite-Mono. See [`license`](license).
Original Lite-Mono code and weights remain under their authors' terms; the CitrusFarm dataset is
governed by its own license.

## Citation
If you use this work, please cite both this project and Lite-Mono. *(This work is a research draft;
citation details are provisional.)*
```bibtex
@misc{citrus_litemono_selfteacher,
  title  = {Toward Label-Free Lightweight Monocular Depth in Orchards:
            In-Domain Self-Distillation and an Anatomy of Domain Shift},
  author = {Amelya, Carlene and Levinson and Aiken, Marvel},
  year   = {2026},
  note   = {Yuan Ze University; research draft}
}
```
```bibtex
@InProceedings{Zhang_2023_CVPR,
  author    = {Zhang, Ning and Nex, Francesco and Vosselman, George and Kerle, Norman},
  title     = {Lite-Mono: A Lightweight CNN and Transformer Architecture for Self-Supervised Monocular Depth Estimation},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  month     = {June},
  year      = {2023},
  pages     = {18537-18546}
}
```
