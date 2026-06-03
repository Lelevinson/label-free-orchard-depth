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
