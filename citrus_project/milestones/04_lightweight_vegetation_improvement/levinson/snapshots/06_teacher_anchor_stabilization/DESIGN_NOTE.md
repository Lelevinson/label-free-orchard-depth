# Snapshot 06 Design Note: Teacher Anchor Stabilization

Date: 2026-05-18

Status: historical completed design note. The selected design ran for the full 30-epoch B0/Snapshot 05 recipe and is packaged in this snapshot; Snapshot 06 remains a marginal/mixed ablation, not the current lead after Snapshot 07.

## Starting Point

Snapshot 05 is promising mixed evidence:

- It improves B0 full validation median-scaled `abs_rel` from `0.5100` to `0.4611`.
- It improves B0 full test median-scaled `abs_rel` from `0.4889` to `0.4132`.
- It keeps most of B0's median-scaled `a1`, but trails B0 on full val/test `a1`.
- It still trails original Lite-Mono on full val/test median-scaled `abs_rel`.

Snapshot 05 full validation:

| model | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|
| Original Lite-Mono | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | 0.7372 | 0.0169 | 0.4611 | 0.5954 |

## Snapshot 05 Diagnosis

The per-sample validation comparison against B0 shows a tradeoff rather than a uniform improvement:

- `abs_rel` improves on 283/564 samples.
- `a1` improves on 194/564 samples.
- 144 samples improve on both metrics.
- 139 samples improve `abs_rel` while losing `a1`.
- 231 samples worsen on both metrics.
- Mean per-sample `abs_rel` delta vs B0 is `-0.0490`, but the median per-sample `abs_rel` delta is near zero.
- Mean per-sample `a1` delta vs B0 is `-0.0153`.

Interpretation: Snapshot 05 fixes some large `abs_rel` outliers, but it pushes many borderline pixels outside the `a1` threshold. This looks more like over-regularization or over-smoothing than a missing teacher signal.

The final training diagnostics also point at ranking as the largest teacher-loss term:

| signal | final value |
|---|---:|
| teacher structure weighted loss | 0.00238 |
| teacher gradient weighted loss | 0.00004 |
| teacher ranking weighted loss | 0.00295 |
| teacher ranking agreement | 0.9819 |
| texture ambiguity high-ratio | 0.4097 |

Ranking is already highly aligned by the end, but still contributes more weighted loss than direct structure. The texture boost is mild on average but focuses teacher pressure on ambiguous regions where the teacher may also be biased.

A selected checkpoint probe showed that Snapshot 05 `weights_19` improves full validation median-scaled `abs_rel` to `0.4447`, better than final `weights_29=0.4611`, but slightly lowers median-scaled `a1` to `0.5915`. This suggests the teacher anchor helps average structure when stronger, while B0-like threshold accuracy returns as teacher pressure weakens. Snapshot 06 should reduce the most brittle teacher pressure rather than increase all teacher terms.

## Selected Snapshot 06 Design

Use the same active Snapshot 05 implementation with a stabilized configuration:

- keep frozen RGB-only teacher from `weights/lite-mono/`
- keep scale-invariant normalized structure loss at `--teacher_structure_weight 0.03`
- keep local gradient loss at `--teacher_gradient_weight 0.01`
- keep ranking loss, but reduce it from `0.02` to `0.005`
- remove `--teacher_texture_ambiguity_emphasis`
- keep shared warmup/decay: `--teacher_structure_warmup_steps 500`, `--teacher_structure_decay 0.5`
- keep `--teacher_rank_samples 512`

Planned full run name:

```text
teacher_anchor_stabilization_b12_30ep_rank005_no_texture
```

## What Is Not Changed

- No depth labels, valid masks, LiDAR labels, ZED depth, or LiDAR-derived labels are used for training.
- Student still starts from ImageNet encoder pretrain via `--mypretrain weights/lite-mono/lite-mono-pretrain.pth`.
- Student is not initialized from the KITTI depth checkpoint.
- Teacher remains frozen and RGB-only.
- Inference remains one RGB image into the student Lite-Mono encoder/depth decoder.
- Dataset, split, batch size, epochs, seed, input size, optimizer settings, and LR schedule match B0/Snapshot 05.
- No Marvel supervised/hybrid code or results are used.

## Why This Is The Least-Risky Next Full Run

This run directly tests the most plausible Snapshot 05 failure mode: global ordinal/ranking pressure plus ambiguity emphasis may fix large average errors but hurt threshold accuracy on many pixels. Softening ranking and removing the texture boost should move the model toward B0's `a1` while preserving the teacher structure anchor that improved `abs_rel`.

Teacher confidence is not enabled in this first Snapshot 06 run because it would make the teacher weakest where the student initially disagrees with it, which may collapse the method toward B0 before testing the ranking hypothesis cleanly.

## Post-Run Outcome

Snapshot 06 was stable, but only marginally changed the Snapshot 05 tradeoff.

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 06 | val | 0.7375 | 0.0165 | 0.4578 | 0.5993 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 06 | test | 0.7348 | 0.0150 | 0.4168 | 0.6418 |

Interpretation: reducing ranking and removing texture emphasis slightly stabilized validation, but did not improve test. Keep Snapshot 06 as a deliberate stabilization ablation, not as a clean replacement for Snapshot 05.
