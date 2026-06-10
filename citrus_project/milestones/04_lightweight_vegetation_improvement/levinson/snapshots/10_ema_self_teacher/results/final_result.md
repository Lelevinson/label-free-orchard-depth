# Snapshot 10 — Final Result (EMA in-domain self-teacher)

Full 30-epoch run, batch 12, seed 0, ImageNet pretrain, S07 stack + `--ema_self_distillation
--ema_filter_adaptive`. Selection note: the automatic B0-close-a1 rule fell back to an early
artifact checkpoint (weights_2, scale-ratio 6.2, not converged) because no S10 checkpoint reaches
B0's val a1>=0.59 (S10 sits ~0.57 on val). The defensible pick is the FINAL converged checkpoint
weights_29 (lowest val abs_rel among converged epochs 13-29, stable a1).

## Selected: weights_29 (final), TEST median-scaled

| model | abs_rel | a1 | a2 | a3 |
|---|---:|---:|---:|---:|
| Original Lite-Mono | 0.3836 | 0.4989 | - | - |
| Snapshot 07 (prev best) | 0.3840 | 0.6539 | - | - |
| **S10 weights_29** | **0.3080** | 0.6258 | 0.8118 | 0.9005 |
| S10 weights_25 (alt) | 0.3088 | 0.6296 | 0.8123 | 0.9017 |

S10 val (weights_29): abs_rel=0.3453, a1=0.5712.

## Verdict

- vs ORIGINAL Lite-Mono: CLEAN WIN on BOTH — abs_rel 0.3080 vs 0.3836 (~20% better), a1 0.6258 vs
  0.4989 (~25% better). FIRST Milestone 4 method to BEAT (not tie) the original on abs_rel.
- vs Snapshot 07: large abs_rel win (0.3080 vs 0.3840, ~20%) for a small a1 give-back (0.6258 vs
  0.6539, -0.028). A genuinely good trade (unlike S08/S09 which lost abs_rel for nothing).
- This is the strongest Levinson label-free result: it is the first to clearly beat the original on
  overall accuracy while keeping threshold accuracy well above the original.
- Inference unchanged: single-image RGB-only Lite-Mono. Training label-free (EMA self-teacher is
  a copy of the student; no GT/LiDAR/foundation teacher).

Remaining honest limitations: a1 slightly below S07; sky/far-field confusion and canopy
over-smoothing are not visually solved (S10 targets accuracy, not appearance).
