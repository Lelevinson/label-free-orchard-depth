# Paper outline — Levinson Milestone 4 (working plan, review against this)

Status: outline drafted 2026-06-14. Single `main.tex` (IEEEtran, two-column, no page limit,
figure-rich) + `figures/` + `tables/` + `references.bib`. No local LaTeX toolchain → author
writes carefully and compiles on Overleaf. NO number may appear that is not in a source doc.

## Working title (draft)
"Label-Free Self-Distillation for Lightweight Monocular Depth in Vegetation-Dense Orchards:
A Self-Teacher that Improves Accuracy, and an Honest Anatomy of What Does Not Work"

## Honest contribution claims
1. An in-domain **EMA self-teacher** (Snapshot 10): scale-and-shift-invariant (SI-log) metric
   distillation + normalized-structure anchor, training-only, inference byte-for-byte
   unchanged (single-image RGB-only Lite-Mono, ~3.07M params). First Milestone-4 label-free
   method to BEAT original Lite-Mono on CitrusFarm Seq01 on BOTH median-scaled abs_rel
   (0.3080 vs 0.3836) and a1 (0.6258 vs 0.4989); beats prior-best S07 on abs_rel (0.3080 vs
   0.3840) for a small a1 give-back (0.6258 vs 0.6539).
2. A **diagnosis** of the dominant failure mode on vegetation — the image-row→depth position
   shortcut / ground-ramp collapse — with our own quantitative evidence (crop self-
   inconsistency ~12%; near-ground error concentration; ~84/16 ground/vegetation label split;
   S10's gain is ground-ramp calibration not object structure), corroborated by prior urban
   findings (van Dijk ICCV'19; EPCDepth ICCV'21; DaCCN ICCV'23).
3. A documented set of **negative results with mechanisms** (S08 feature-metric, S09 mixture-
   uncertainty, S11 crop self-distillation collapse) — community guidance, not filler.

## Section plan
- Abstract
- I. Introduction — agricultural robot motivation; lightweight RGB-only constraint; domain
  gap urban→vegetation; the three contributions; honest scope (single domain, metrics-not-
  visuals).
- II. Related Work — self-sup mono depth (Monodepth2, Lite-Mono); self-distillation / mean-
  teacher (EC-Depth, ER-Depth, BDEdepth, AugUndo, RA-Depth); position-shortcut literature
  (van Dijk, EPCDepth, DaCCN, Camera-Pose-Matters); foundation-model distillation = NOT
  label-free (Depth Anything etc., explicitly out of scope / hybrid future work).
- III. Dataset & Evaluation Protocol — CitrusFarm Seq01; LiDAR→ZED projection + local-IDW
  densification = EVAL-ONLY labels; valid masks; raw vs median-scaled metrics; label-free
  training vs eval-only GT separation (integrity statement). Numbers from AGENTS.md.
- IV. Method — EMA in-domain self-teacher. Math: SI-log term (per-image offset removal),
  normalized-log structure anchor, DC∧GC gates, warmup/weight schedule, EMA update.
  HONEST BOX: the DC∧GC gates were near-inert (~88% kept) → the gain came from near-DENSE
  SI-log distillation; gating credit requires an ablation we did not run.
- V. Experimental Journey & Ablations — B0 plain Citrus; S01–S04 negative gates; S05/S06
  teacher-anchor; S07 structure-aware (prior best); S08/S09 sharpening failures; → motivates
  S10. Table 2 (one line each).
- VI. Failure Analysis (diagnosis) — position shortcut; ground-vs-vegetation error split;
  why boundary-sharpening fails (ground-contact-edge object-detection mechanism); S11 crop
  collapse to constant-depth degenerate minimum (mechanism + the metric-anchored fix we did
  not have time to run).
- VII. Results — main table; per-frame win/loss vs S07; qualitative panels; per-epoch val
  curve; explicit "metrics improve, visuals do not" honesty.
- VIII. Limitations & Future Work — single-domain (Seq01 only); visuals unsolved; gating
  ablation; metric-anchored crop fix; data-grafting / PDA-equivariance queue; second-sequence
  generalization; hybrid foundation-distillation (Marvel) as separate future path.
- IX. Conclusion.
- References (references.bib from LITERATURE_SHORTLIST + cited baselines).

## Tables (in tables/, \input into main.tex)
- T1 main results: Original Lite-Mono, B0 plain-Citrus, S05 w19, S07 w25, **S10 w29** —
  median-scaled abs_rel/a1/a2/a3 (+ raw where in docs); params 3.07M, FPS ~28–30.
- T2 journey/ablation: B0,S01–S11 mechanism + verdict (one line each).
- T3 ground-vs-vegetation error split (Original vs S10; from autopsy note).
- T4 per-frame win/loss S10 vs S07 (from autopsy note).

## Figures (in figures/)
- F1 method schematic — **NEEDS A HUMAN TO DRAW** (no such figure exists). Placeholder.
- F2 qualitative depth panels RGB|LiDAR|Original|S07|S10 — GENERATE (renderer exists).
- F3 failure autopsy: clearing (bad) vs corridor (good) — exists / regenerate.
- F4 error vs scene-distance bars — GENERATE from weights29 per-sample CSV.
- F5 keep-ratio trace (gates near-inert) — GENERATE from extracted ema_distill scalars.
- F6 S11 collapse (constant ~0.20 m predicted depth) — GENERATE from gate eval CSV.
- F7 per-epoch val abs_rel curve — GENERATE from validation_sweep.csv.

## Needs-a-human flags (collect in main.tex comments + final report)
- Author block / affiliation.
- F1 architecture schematic must be drawn by hand.
- Any reference whose bibliographic details can't be verified → marked `% UNVERIFIED`.
