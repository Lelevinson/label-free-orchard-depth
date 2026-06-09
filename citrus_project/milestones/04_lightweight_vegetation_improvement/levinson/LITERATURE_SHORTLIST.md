# Levinson Milestone 4 — Label-Free Improvement Literature Shortlist

Status: candidate-direction shortlist from a verified deep-research literature pass (2026-06-03).
Scope: self-supervised / label-free, RGB-only, lightweight monocular depth for vegetation-dense
scenes, to fix Snapshot 07's remaining failures (canopy over-smoothing / "blobs", sky/far-canopy
confusion, median-scaled `abs_rel` not clearly beating original Lite-Mono).

Method: deep-research harness, 6 search angles, 26 primary sources, 122 claims extracted, top 25
adversarially verified (3-vote), 25/25 confirmed, 0 refuted. Provenance is literature only; none of
these results are validated on vegetation — see "Honest caveats".

## A. Self-supervised PURE candidates (keep Levinson's label-free identity)

1. Feature-metric loss — FeatDepth (Shu et al., ECCV 2020, arXiv 2007.10603; code
   github.com/sconlyshootery/FeatDepth).
   - What: add a self-supervised feature-metric loss on a learned feature autoencoder whose loss
     landscape is regularized (1st/2nd-order) to form "proper convergence basins".
   - Why it fits: explicitly targets the photometric loss's "plateau landscapes for textureless
     pixels / multiple local minima" — the exact mechanism behind canopy-interior blobs.
   - Purity: PURE (no GT/LiDAR/foundation teacher). Code change: moderate (small feature
     autoencoder + loss term). Repo built on mmcv/mmdetection, not a literal Monodepth2 fork.

2. Boundary-uncertainty via per-pixel mixture distributions — TSOB (Naver Labs / LIRIS-INSA,
   BMVC 2025 oral, arXiv 2509.15987; code github.com/Visual-Behavior/TSOB).
   - What: model depth as a per-pixel mixture, shifting uncertainty onto mixture weights; yields
     crisp discontinuities (up to ~35% sharper boundaries on KITTI/VKITTIv2).
   - Why it fits: directly attacks boundary blur / "spurious intermediate 3D points" =
     over-smoothing. Plugs into Monodepth2-style loops via variance-aware losses. Newest + most
     novel of the pure options.
   - Purity: PURE. Risk: validated urban; softmax mixtures can be overconfident out-of-domain.

3. Surface-normal / planarity priors — Yang et al., AAAI 2018 (arXiv 1711.03665).
   - What: differentiable depth-to-normal + normal-to-depth layers tied by edge-aware
     depth-normal consistency (local planar smoothness).
   - Purity: PURE. Code change: moderate (two differentiable layers + consistency loss). Older,
     urban-validated mechanism. Related: P3Depth piecewise-planarity (CVPR 2022).

4. Multi-frame cost-volume as a TRAINING-ONLY teacher — ManyDepth (CVPR 2021, arXiv 2104.14540),
   DepthFormer (CVPR 2022), MGDepth/ManyDepth2 (arXiv 2312.15268), FusionDepth (arXiv 2305.06036).
   - What: strongest label-free `abs_rel` gains (ManyDepth KITTI 0.115->0.098). ManyDepth's
     pattern: single-frame mono teacher at training only + L1 consistency where cost-volume vs
     single-frame disagree by >100% (teacher disposable at inference).
   - HARD CAVEAT: standard variants need multiple frames + cost volume AT INFERENCE -> violates our
     single-image RGB-only lightweight inference. In-constraint use = distill a multi-frame teacher
     into our single-image Lite-Mono student; do NOT ship a multi-frame inference net.
   - These papers name low-texture surfaces + moving objects + boundary blur as their failure
     regimes — matching our canopy/wind-foliage/sky problems.

5. Label-free reliable-region masks (borrowable components):
   - ORDMP directional mask (Springer PAA 2025, DOI 10.1007/s10044-025-01584-w): mask photometric
     supervision where optical flow vs reconstructed flow disagree. Label-free, separable from
     ORDMP's supervised teacher.
   - Temporal self-distillation: use the student's own prior-epoch weights as teacher (the one
     purity-preserving distillation idea; Sensors 2024 24/13/4090 uses it but also injects
     supervised LeReS, so only the temporal part is pure).

## B. NOT label-free — supervised foundation-model teacher (Marvel / hybrid workstream only)

- Distilling Depth Anything V2 / MiDaS / Marigold / LeReS as a teacher gives the LARGEST accuracy
  and boundary gains and best targets blob/boundary errors. Methods: Distill Any Depth
  (arXiv 2502.19204), ORDMP, Sensors 2025 VIO distillation (PMC12431346), LeReS-based.
- Every verified method here explicitly TRADES AWAY self-supervised purity ("transforming the
  self-supervised task into a supervised one"). Belongs in Marvel's supervised/hybrid path and must
  be labeled honestly, NOT as Levinson label-free.
- FSRE-Depth semantic feature-metric loss (ICCV 2021, arXiv 2108.08829) also targets weak-texture/
  boundary geometry but needs a SUPERVISED segmentation model -> not label-free in-domain unless
  vegetation semantics are obtained label-free.

## Honest caveats

- DOMAIN GAP: every quantitative result above is urban/driving (KITTI, VKITTIv2, DDAD). NONE is
  validated on vegetation/canopy. The "boundary-blur/low-texture -> canopy-blob" mapping is our own
  mechanistically-plausible extrapolation. This is both the main risk AND the novelty opportunity:
  no one has shown these fixes on dense agricultural vegetation.
- Distill Any Depth gains are self-reported on zero-shot RELATIVE depth and its student is ViT-scale
  (not ~3M Lite-Mono). Multi-frame KITTI numbers are authors' own tables.
- Sky/far-canopy confusion is NOT directly addressed by any verified method; a dedicated label-free
  ordinal/sky prior (we already have one) likely stays necessary alongside any structural fix.

## Open questions to resolve before committing compute

1. Do urban boundary/low-texture fixes transfer to fractal foliage "boundaries"?
2. Can a multi-frame teacher be distilled into our single-image Lite-Mono student without breaking
   RGB-only inference?
3. Can FSRE-style semantic gains be had with label-free vegetation segmentation?
4. How do the pure methods (feature-metric + mixture-uncertainty + normal-consistency) compose on a
   ~3M backbone in 8GB at 640x192 without regressing the already-good `a1`?

---

# Round 2 (2026-06-05) — Gentle, abs_rel-focused, teacher-improving directions

Lesson-informed follow-up after S08 (feature-metric) and S09 (TSOB) both TRADED OFF
(nudged a1 / threshold but worsened abs_rel). Question: gentlest label-free TRAINING-side
ways to improve overall accuracy (abs_rel) WITHOUT regressing a1, ideally by improving the
teacher/pseudo-label. Verified deep-research pass: 23 sources, 25 claims, 23 confirmed / 2 killed.

## RANKED #1 (recommended): EMA mean-teacher in-domain self-distillation + consistency-filtered pseudo-labels
- What: replace/complement the FIXED urban (KITTI) teacher with an ADAPTIVE in-domain teacher =
  an EMA (running-average) copy of the student itself, which learns vegetation as training
  proceeds. Distill its predictions to the student, but only where reliable — gated by
  consistency filters (DC-Filter = depth consistency across views, GC-Filter = geometric
  consistency). EC-Depth (arXiv 2310.08044), ER-Depth (ACM 10.1145/3750050).
- Why it should help abs_rel (not trade off): under DOMAIN SHIFT / corruption (the exact analog
  of an urban teacher on vegetation) abs_rel AND a1 improve TOGETHER, no trade-off
  (ER-Depth KITTI-C 0.115->0.111 abs_rel, a1 0.869->0.874). On clean in-domain data it is
  accuracy-SAFE (abs_rel flat, sq_rel/RMSE slightly better). The consistency filter is the
  gentle mechanism that prevents propagating teacher errors (directly answers our "aggressive
  backfires" lesson).
- Purity: PRESERVED (no labels, no external supervised teacher). Inference: single-image
  RGB-only (only student DepthNet at test). Feasibility 8GB @ batch 12: GOOD (one frozen
  forward pass + a weight copy). Code: MEDIUM (EMA update hook, 2 consistency filters,
  distillation loss). Directly fixes S07's known weakness: its teacher is a fixed out-of-domain
  urban model that is itself blobby on vegetation.
- Variant #1b: previous-EPOCH checkpoint teacher (SRD-Depth 2302.09789; SS-MDE mechanism) — a
  hard copy of last epoch instead of a running average; simpler bookkeeping (we already save
  per-epoch checkpoints), slightly less smooth.
- Failure modes: gains are regime-specific to OOD/hard data (good for us — CitrusFarm IS OOD vs
  the urban teacher); without the DC/GC filters a noisy teacher propagates errors; two-stage
  recipe (needs a decent stage-1 model — we have S07).

## RANKED #2: distill a self-supervised MULTI-FRAME cost-volume teacher into the single-image student (training-only)
- ManyDepth (2104.14540), FusionDepth (2305.06036), Mono-ViFI (2407.14126; shares weights so
  single-image inference, even reports on Lite-Mono). Literature's strongest label-free abs_rel
  improver. Purity preserved; inference single-image. BUT: LARGE code change, MODERATE 8GB
  feasibility (cost-volume training is memory-heavy, may force lower batch/frames), and cost
  volumes are unreliable on moving/low-texture vegetation. Higher ceiling, higher risk/effort.

## RANKED #3: augmentation / TTA self-distillation (gentlest, smallest change)
- BDEdepth (2309.05254, resizing-crop / split-permute self-distill, abs_rel 0.115->0.108 from the
  augmentation+self-distill mechanism alone), EPCDepth selective post-processing (2109.12484),
  Mono-ViFI spatial branch. Modest but real abs_rel gains, label-free, SMALL-MEDIUM code.

## CAUTION / guardrails
- Heavy weather/corruption augmentation ALONE (Robust-Depth 2307.08357) is accuracy-SAFE but does
  NOT lift clean-condition abs_rel — pair augmentation with self-distillation for an actual gain.
- DO NOT adopt external supervised teachers / GT (SS-MDE's LeReS term; MaskingDepth's semi-sup GT)
  — those break label-free purity (Marvel/hybrid territory). Take only the self-distillation /
  EMA / consistency-filter / augmentation MECHANICS.

## Honest caveat
- ALL quantitative evidence is KITTI / KITTI-C (urban + synthetic corruption), NOT CitrusFarm
  vegetation. The OOD/corruption regime is the closest analog, but the magnitude of any abs_rel
  gain on dense vegetation is unverified — must be gated in-domain.
