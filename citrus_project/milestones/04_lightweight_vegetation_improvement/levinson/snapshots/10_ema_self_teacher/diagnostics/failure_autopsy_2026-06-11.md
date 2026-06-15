# Test-set failure autopsy (2026-06-11) — where is the remaining S10 error?

Data: per-frame test CSVs already on disk (S10 `results/weights29_test_reverify/`, S07
`local_evidence/.../test_selected/weights_25/`, original Lite-Mono milestone-01 results).
No training. RGB frames of representative best/worst cases viewed directly.

## Findings

1. **S10 introduced ZERO new catastrophic failures.** All 40 worst S10 test frames
   (median-scaled abs_rel) are ALSO bad (>0.45) for BOTH Snapshot 07 and original Lite-Mono.
   No frame is fine for S07 (<0.35) but bad for S10. The remaining error is a shared,
   domain-wide failure mode, not an S10 regression.
2. **The worst frames cluster in contiguous time-blocks** (41–51, 100–106, 243–251, 339–349,
   390–395 plus index 1) — specific scene segments, consistent with time-block splits.
3. **Scene type of the worst frames (viewed RGB): wide-open clearings / row-end areas** —
   large bare-dirt foreground, tree lines far away, big sky. Best frames are classic in-row
   corridors with close canopy on both sides and a strong near-to-far ground gradient.
4. **The measured error concentrates in NEAR-ground scenes, not far scenes.** Bucketing all
   407 test frames by gt_median (median true depth of LiDAR-labeled pixels):
   - 1.3–1.8 m -> mean abs_rel 0.455 (worst)
   - 1.8–3.0 m -> 0.332
   - 3.0–3.3 m -> 0.211 (best)
   - 3.3–4.8 m -> 0.235
   In clearings the LiDAR-valid labels are dominated by close bare ground; the models get the
   near ground-plane gradient wrong there, and abs_rel (error divided by true depth) amplifies
   near-range mistakes. Within the worst block 41–51 the per-frame scale-ratio also swings
   wildly (1.4 -> 4.2) frame to frame and a1 collapses to 0.03–0.1.
5. Valid-label coverage is NOT the explanation: worst-40 mean valid fraction 0.358 vs
   all-frames 0.367 (no meaningful difference).

## Visual confirmation (panels rendered, same day)

Panels at `../local_evidence/failure_autopsy_panels/` (script
`render_failure_autopsy_panels.py`; frames 1, 16, 44, 47, 102, 247, 344, 358, 392;
RGB | masked dense LiDAR label | Original / S07-w25 / S10-w29 disparity).

**Confirmed core finding — stronger than the original hypothesis:** all three models
predict essentially the SAME thing on every inspected frame: a smooth bottom-to-top
near-to-far ramp (a learned ground-plane / image-row prior), with only faint lateral/object
structure where trees stand (Original shows slightly more visible tree darkening than
S07/S10, which look smoother — consistent with the long-standing "blobby" critique).
The per-frame score is therefore mostly determined by HOW WELL THE TRUE SCENE MATCHES A
VERTICAL RAMP:

- Best frames (16, 358): in-row corridor; ground fills the lower image, trees sit at a
  consistent distance band -> the ramp is a good fit -> abs_rel ~0.12.
- Worst frames (44, 102, ...): open clearings; side trees at 5-8 m and irregular near
  ground -> the ramp mis-prices both the near dirt and the lateral trees -> abs_rel 0.6-0.85,
  a1 collapses.

Implications:

1. S10's abs_rel win = a better-CALIBRATED ramp (the SI-log self-distillation tightened the
   global depth-vs-row mapping), NOT new object structure. This cleanly explains the
   metric-vs-visual divergence that has run through S05-S10.
2. The earlier planarity-prior idea is now LESS attractive than it looked from the buckets:
   the predictions are already ultra-smooth ramps; enforcing local planarity adds smoothness
   the model already over-has. Caution before adopting it.
3. The real remaining gap is LATERAL depth structure (trees vs gaps at the same image row).
   S08/S09 failed trying to sharpen boundaries of structure that largely is not predicted at
   all — consistent with this reading.
4. ANSWERED same day by the ground-vs-vegetation error split (script
   `ground_vs_vegetation_error_split.py`; vegetation = excess-green ExG > 0.05 on RGB):

   | model | frames | veg abs_rel | ground abs_rel |
   |---|---|---:|---:|
   | original | all | 0.3680 | 0.3824 |
   | original | worst40 | 0.6400 | 0.6382 |
   | original | rest | 0.3384 | 0.3545 |
   | S10 w29 | all | 0.3335 | 0.2993 |
   | S10 w29 | worst40 | 0.6882 | 0.7435 |
   | S10 w29 | rest | 0.2948 | 0.2508 |

   - **Labeled pixels are ~84% ground / ~16% vegetation** — the eval metric is mostly a
     ground-accuracy metric. (Caveat: worst40 was selected by S10's own error, so S10
     looking worse than original on those frames is partly selection bias.)
   - **S10's gain came mostly from ground pixels** (0.382→0.299, -22%) vs vegetation
     (0.368→0.334, -9%) — quantitative confirmation of the "better-calibrated ramp" reading.
   - For S10, vegetation is now the weaker region (0.334 vs 0.299), but at 16% label share,
     even perfect trees move overall abs_rel only modestly; the big remaining metric mass is
     clearing-frame ground geometry (worst40 ground 0.74).
   - Method implication: the failure is a "image-row = depth" SHORTCUT that breaks when scene
     layout deviates from the corridor template. The literature mechanism that directly
     attacks position shortcuts is resizing-crop / split-permute augmentation
     self-distillation (BDEdepth, Round 2 shortlist #3): the same content at a different
     image position must get consistent depth. Previously ranked "gentlest"; now also the
     best evidence-matched candidate. It composes with the existing S10 stack.
