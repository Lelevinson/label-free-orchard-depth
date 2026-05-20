# Snapshot 07 Design Note

Date: 2026-05-19

Status: historical design note for the completed Snapshot 07 method. Current results and presentation-facing conclusions live in `README.md` and `final_result_summary.md`.

Working name:

```text
Structure-Aware Label-Free Vegetation Depth
```

## Why Snapshot 05 weights_19 Is Not Enough

At design time, Snapshot 05 `weights_19` was the best then-current Levinson label-free checkpoint, but it was not a solved result. It strongly improved B0 test median-scaled `abs_rel` while keeping most of B0's `a1`, yet it still trailed Original Lite-Mono on test median-scaled `abs_rel`:

| model | test median abs_rel | test median a1 |
|---|---:|---:|
| Original Lite-Mono | 0.3836 | 0.4989 |
| B0 plain Citrus | 0.4889 | 0.6582 |
| Snapshot 05 `weights_19` | 0.3947 | 0.6476 |

The professor-facing visual diagnosis is more limiting than the table. `weights_19` can improve valid-mask errors while still producing full-image artifacts: sky and far canopy can merge, vegetation masses can become smooth dark blobs, and tree-ground boundaries are not crisp enough for a publishable qualitative improvement.

## Exact Failure Snapshot 07 Targets

Snapshot 07 targets the structure failures that remain after Snapshot 05:

1. vegetation blobs: large plant masses become smooth depth islands instead of preserving internal tree structure;
2. sky/far-canopy confusion: upper-image sky and far vegetation can be merged or assigned visually implausible depth;
3. tree-ground boundaries: boundary transitions are often too soft or misplaced;
4. over-smoothing: photometric adaptation still favors broad smooth maps in repeated foliage;
5. weak full-image qualitative depth: valid-mask improvements do not always translate into convincing full-frame depth.

## Why This Is More Than A Small Snapshot 05/06 Tweak

Snapshot 06 only changed teacher-anchor weights and texture emphasis. Snapshot 07 changes the training signal itself.

It keeps the frozen RGB teacher idea because Snapshot 05 proved it is useful, but it no longer trusts the teacher uniformly. Instead, it adds RGB-derived structure context:

1. a training-only boundary reliability map from RGB image gradients and teacher depth gradients;
2. boundary-aware teacher weighting so structure/gradient/ranking losses focus more on likely real tree-ground and tree-sky depth boundaries;
3. a strict RGB-only sky/far ordinal prior that pushes confident sky-like upper pixels to be farther than lower scene pixels in normalized inverse-depth space;
4. diagnostics for whether those maps are active, finite, and non-trivial.

The core hypothesis changes from "keep teacher relative structure while adapting" to "keep teacher structure where RGB/teacher cues agree, and add an explicit label-free far-region constraint for sky-like pixels." That is a method-level change, not another ranking-weight adjustment.

## Label-Free Training Signals

Allowed training signals:

1. target/source RGB frames from Citrus temporal triplets;
2. camera intrinsics and PoseNet geometry used by the existing self-supervised photometric objective;
3. frozen RGB-only Lite-Mono teacher predictions from `weights/lite-mono/`;
4. RGB-derived image gradients, color/position sky confidence, and lower-image reference priors computed from the input image only.

Disallowed signals remain disallowed:

```text
depth_gt, valid_mask, dense LiDAR, sparse LiDAR, ZED depth, LiDAR-derived labels, or LiDAR-derived training masks
```

Citrus labels and valid masks remain evaluation-only.

## Why Inference Remains RGB-Only And Lightweight

Snapshot 07 changes only the training objective. At inference, the deployed model is still the Lite-Mono student encoder plus depth decoder:

```text
one RGB image -> Lite-Mono student DepthNet -> depth/disparity
```

The frozen teacher, PoseNet, boundary reliability maps, sky/far priors, ranking loss, and diagnostics are training-only. No additional input modality, segmentation model, LiDAR, depth label, or runtime module is added.

## Main Risks

1. The RGB sky heuristic may be too strict and rarely activate, making the new sky prior meaningless.
2. If the sky heuristic is too broad, it may mistake far canopy for sky and hurt upper-image valid pixels.
3. RGB edges do not always mean depth edges; boundary weighting must stay conservative and rely on teacher-gradient agreement.
4. Extra teacher focus near boundaries may over-preserve the Original Lite-Mono teacher's bias.
5. The 250-500 step pilot may not predict 30-epoch behavior, so diagnostics must be checked before full training.

## Root-Code Starting State

Snapshot 07 deliberately builds from the active repo-root teacher-anchor workbench, not from the original Lite-Mono baseline and not by importing archival snapshot `code/` folders.

Rationale:

1. root `options.py` and `trainer.py` are already the tested Snapshot 05/06 teacher-anchor implementation used by `train.py`;
2. Snapshot 07 needs the existing frozen teacher loading, normalized teacher structure loss, gradient loss, ranking loss, texture ambiguity diagnostic support, and diagnostics logging;
3. the new method will add disabled-by-default flags and will copy the tested changed root files into this snapshot's `code/` folder after verification.

This choice preserves the active root policy in:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/ACTIVE_ROOT_CODE_STATE.md
```

If Snapshot 07 is later reverted or superseded, the snapshot `code/` folder should be treated as the frozen copy of the tested Snapshot 07 implementation.
