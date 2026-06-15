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

## Post-hoc verification (2026-06-11, fresh-session review)

1. **Headline result independently reproduced.** Re-ran the full test eval on the preserved
   snapshot checkpoint (`checkpoint/`): abs_rel=0.3080, a1=0.6258, a2=0.8118, a3=0.9005 —
   exact match. Durable machine-generated evidence now at `results/weights29_test_reverify/`
   (previously the weights_29 test numbers existed only as transcribed markdown; the run-log
   `test_selected/` folder held only the auto-rule weights_2 eval).
2. **Keep-ratio finally inspected directly** (TB event file parsed with
   `diagnostics/read_tb_scalars.py`; scalars in `diagnostics/ema_distill_scalars_train.csv`).
   Finding: the DC∧GC filters were NEAR-INERT for the whole run — overall keep-ratio
   0.874–0.917 (mean 0.89) and canopy-band keep-ratio 0.841–0.918 (mean 0.88), never inside
   the design target band 0.2–0.8. The feared canopy starvation never happened, but the flip
   side is that ~88% of all pixels passed both gates (adaptive τ=3.0 on a τ·mean threshold is
   very loose for right-skewed error distributions). Honest implication: the abs_rel win came
   from near-DENSE EMA SI-log self-distillation, not from selective reliability gating; the
   gating story needs an ablation (and/or tighter percentile thresholds) before it can be
   credited in the paper.
3. **a1 deficit is a method property, not a selection artifact.** Val a1 plateaus ≈0.57
   across ALL converged checkpoints (max 0.5743 at weights_19); no S10 checkpoint reaches
   B0's a1>=0.59 selection bar. weights_25 (test 0.3088/0.6296) is metrically interchangeable
   with weights_29.
4. **Paired per-frame test comparison vs S07 weights_25** (407 common frames): S10 better on
   abs_rel on 62.4% of frames (median per-frame delta -0.032; mean -0.076 boosted by a tail
   of large wins, best -0.787). The 56 frames improving >0.2 cluster in contiguous
   time-blocks where S07 was worst (abs_rel 0.45–0.6 → ~0.25–0.30) — S10 fixes S07's worst
   segments. The a1 give-back is broad (S07 better on 68.1% of frames, mean -0.028), not an
   outlier effect.
5. Protocol notes: the DESIGN_NOTE's 10-epoch control-vs-experiment gate and pre-gate
   mechanism check were not run as written; the first (killed) run's epoch-12 eval served as
   the watch-and-bail gate. The full run trained from ImageNet pretrain with the S07 stack
   (NOT warm-started from the S07 checkpoint as the DESIGN_NOTE protocol sketched) — this
   matches the B0/S05/S07 recipe and is the fairer comparison. The "canopy" keep-ratio band
   is rows below 40% image height, which includes much ground; treat it as a lower-image
   proxy, not a true canopy mask.
