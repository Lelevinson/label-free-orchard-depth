# Next-Session Review Brief — Levinson Milestone 4 (after the Snapshot 10 win)

Purpose: a focused brief for a FRESH session (a new model) to critically review the current lead
(Snapshot 10), find genuine weaknesses, and propose the next improvement. Metrics are already good;
the job is to push further honestly, not to rehash.

## Read first (source of truth)
1. `AGENTS.md` (root) — project status, current lead, constraints.
2. `CLAUDE.md` (root) — read order + working rules.
3. `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/DOCUMENTATION_INDEX.md`
4. `snapshots/10_ema_self_teacher/DESIGN_NOTE.md` + `snapshots/10_ema_self_teacher/results/final_result.md`
5. `LITERATURE_SHORTLIST.md` (Round 1 + Round 2 — verified candidate directions, several untried)
6. `M4_CHANGE_LOG.md` (full history incl. the negative results S08/S09)

## Current lead = Snapshot 10 (EMA in-domain self-teacher)
- Method: a frozen EMA copy of the student (in-domain, learns vegetation) distills to the student via
  a scale-and-shift-aware (SI-log) metric term + a normalized structure anchor, gated by two
  independent reliability filters (GC min-reprojection + DC flip-consistency). Off-by-default flags
  `--ema_self_distillation --ema_filter_adaptive`. Code in `snapshots/10_ema_self_teacher/code/`.
- Result (selected final checkpoint weights_29, TEST median-scaled): **abs_rel=0.3080, a1=0.6258.**
  - vs Original Lite-Mono (0.3836 / 0.4989): clean win on BOTH (~20% abs_rel, ~25% a1) — FIRST M4
    method to BEAT (not tie) the original on abs_rel.
  - vs Snapshot 07 (0.3840 / 0.6539): wins abs_rel ~20% for a small a1 give-back (-0.028).
- Inference unchanged: single-image RGB-only Lite-Mono. Training label-free (no GT/LiDAR/foundation teacher).
- Winning weights preserved at `snapshots/10_ema_self_teacher/checkpoint/` (encoder.pth + depth.pth).

## Known weaknesses / open issues (verify against files; don't take on faith)
1. **a1 give-back vs S07** (0.6258 vs 0.6539). Threshold accuracy is slightly below the prior best.
2. **Visual structure NOT improved.** S10 improves the numbers, not the appearance. Rendered depth
   maps look broadly similar to S07/original; **sky/far-field confusion and canopy over-smoothing
   remain unsolved.** (Boundary-sharpening attempts S08/S09 both FAILED — aggressive sharpening
   backfired on abs_rel. Any structural fix must be gentle.)
3. **Selection-rule quirk.** The B0-close-a1 selection rule mis-fell-back to an early scale-artifact
   checkpoint (weights_2, scale-ratio 6.2); weights_29 (final converged) was chosen manually. The
   rule may need revisiting for methods whose a1 sits in a different range than B0/S07.
4. **Keep-ratio never directly verified.** The canopy keep-ratio (the #1 design risk = GC filter
   starving canopy) is logged only to TensorBoard, and the env lacked a TB reader. It worked
   (abs_rel improved), but the filter behaviour was not directly inspected — worth confirming.
5. **EMA hyperparameters are first-shot defaults** (decay 0.99 constant, ~5-epoch warmup, weight 0.3,
   no decay ramp, adaptive tau=3.0). Likely room to tune.
6. **Single-domain evidence.** Only CitrusFarm Sequence 01. Generalization unverified.

## Candidate next directions (untried; ground any pick in LITERATURE_SHORTLIST + the failures)
- **Tune S10 to close the a1 gap** while keeping abs_rel: EMA decay ramp 0.99->0.999, warmup/weight
  schedule, DC/GC thresholds; or re-introduce more of S07's structure/ranking emphasis alongside.
- **Combine S10 with a remaining shortlist option:** Round 2 #2 (multi-frame cost-volume teacher,
  training-only, strongest abs_rel lever — but has real 8GB/AMP/feature-index build blockers) or
  Round 2 #3 (augmentation/TTA self-distillation — gentlest, smallest add).
- **Gently tackle the still-open sky/structure problem** (NOT via aggressive sharpening — that failed).
- **Validate generalization** on additional CitrusFarm sequences if data is available.

## Hard constraints (non-negotiable)
- Training LABEL-FREE in-domain (no depth GT / LiDAR / stereo / ZED depth as loss or mask; no
  external SUPERVISED foundation-model teacher — that is Marvel/hybrid territory).
- Inference SINGLE-IMAGE, RGB-only, lightweight (same Lite-Mono; no inference-time net/arch change).
- Hardware: single 8GB RTX 4060 laptop, batch 12 (paper setting), ~24-28h per 30-epoch run.
- Snapshot discipline: tested .py changes copied into the stage `code/`; off-by-default flags;
  update `AGENTS.md` same-turn; no long training without a written plan + explicit user OK; gate
  (3-epoch full-val) before any full run; evaluate on FULL val (not first-100 — that fooled us once).

## Task for the next session
1. Read the source-of-truth docs above; verify the current state against the actual files.
2. Critically review Snapshot 10 — confirm the result, probe the weaknesses, check claims.
3. Propose 2-3 concrete, evidence-grounded improvement directions (effort/risk each) and recommend one.
4. Do NOT start long training without a written plan + the user's explicit OK.
