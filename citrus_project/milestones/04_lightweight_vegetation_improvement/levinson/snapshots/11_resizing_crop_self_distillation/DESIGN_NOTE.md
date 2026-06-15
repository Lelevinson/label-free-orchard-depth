# DESIGN_NOTE — Snapshot 11 (S11): Resizing-Crop Self-Distillation on the S10 Stack

Status: KILLED BY GATE 2026-06-14 — NEGATIVE RESULT under this integration (see Section 6
post-mortems). Both launches collapsed identically once the crop loss activated at epoch 5:
the model converged to the DEGENERATE FLAT-DEPTH solution (predicted median depth ~0.20 m
constant across all 564 val frames vs true 1.0–4.6 m; val metrics frozen bit-identical
across epochs 5 and 6; scale-ratio ~12). Root-cause analysis: BOTH S11 crop terms are
scale-free (SI-log with per-sample offset removal + per-image-normalized structure), and a
COLLAPSED output satisfies them trivially (constant depth ⇒ zero consistency error); the
fast EMA teacher (half-life ~69 steps) follows the student into collapse, the DC filter
keeps everything (a flat teacher is perfectly flip-consistent), and the photometric loss's
resistance is neutralized by the classic zero-translation/automask degeneracy. Published
BDEdepth/RA-Depth do not collapse because their crop targets are METRIC-ANCHORED (teacher
disparity rescaled by the KNOWN zoom factor — a hard constraint a flat output cannot fake)
and applied from epoch 0. Identified candidate fix, recorded for post-deadline / Marvel /
lab-machine revisit, NOT attempted under the deadline: metric-anchored crop target
(`target = crop(teacher_disp) / scale_factor`, NO offset removal) + activation from early
training. Snapshot 10 remains the shipped paper result; this negative result is
paper-usable (predicted disease, literature cure assumes treatment-from-birth, retrofit
collapses to the known degenerate minimum). Code stays in root, off-by-default.
Hard context: ~1–1.5 weeks total remaining. This is a ONE-SHOT attempt with a predefined
kill rule; if it fails the gate, S10 ships as the paper result — no method-hopping.

## 0. Pre-build mechanism probe (run 2026-06-11, inference-only, no training)

`diagnostics/crop_consistency_probe.py` measured whether trained S10 contradicts itself
between a full view and a 0.7-scale cropped view of the same test image (407 frames,
SI-log space = exactly the invariance the S11 loss would use; per-frame CSV alongside).

- **Self-inconsistency is LARGE: mean 0.118** (≈12% scale-free disagreement; p10 0.075,
  p90 0.166). The position shortcut is real and the S11 loss has a substantial signal to
  train on — the necessary condition PASSED (had this been ~0.01, S11 would be dead now).
- **But per-frame correlation with abs_rel is WEAK** (pearson 0.19, spearman 0.18; overlap
  of top-40 inconsistent with top-40 worst-error = 11/40, ~3x chance but far from tight).
  Honest implication: enforcing consistency is NOT guaranteed to cut abs_rel frame-by-frame;
  the expected benefit is aggregate regularization (the same way S10's dense agreement loss
  helped globally). Worst-frame error is dominated by shared scene difficulty, which dilutes
  any single-model correlation.

Verdict: mechanism confirmed present and trainable; effect on the metric unproven — which is
precisely what the cheap 8-epoch gate (Section 4) exists to test before the 30-epoch commit.
Confidence tier: necessary condition passed; do NOT skip the gate on the strength of this.

## 1. Why this method (evidence chain, not literature hope)

The 2026-06-11 failure autopsy (`../10_ema_self_teacher/diagnostics/failure_autopsy_2026-06-11.md`)
established, on our own test data:

1. All models (original/S07/S10) predict a near-identical smooth bottom-to-top ground ramp —
   an "image-row = depth" SHORTCUT. Scores are governed by how well the scene matches the ramp
   (corridors fit; open clearings fail; all 40 worst frames are shared failures).
2. Labeled pixels are ~84% ground; S10's win was ramp calibration (ground error −22%,
   vegetation −9%).
3. S08/S09 failed because they tried to sharpen structure that is not predicted at all.

The training mechanism that directly attacks position shortcuts is **resizing-crop
self-distillation** (BDEdepth, arXiv 2309.05254; Round 2 shortlist #3; reported abs_rel
0.115→0.108 on KITTI from the augmentation+self-distillation mechanism alone, with results
on Lite-Mono itself): the same content placed at a different image position/scale must
receive consistent depth. This punishes "row = depth" and rewards reading image content.
Previously ranked "gentlest"; now also the best evidence-matched option.

## 2. Method (training-only; inference byte-for-byte unchanged)

On top of the frozen S10 stack (S07 losses + EMA self-teacher + DC/GC gates), add ONE loss:

- Sample a random crop box B per sample (LINEAR scale uniform in [0.5, 0.8], aspect
  preserved — v1 keeps no aspect jitter; box uniformly placed inside the image); crop the
  CLEAN target image and resize back to 640x192 -> `I_c`. Implemented as per-sample affine
  grids + one batched `grid_sample` (same grid reused for the teacher disparity and mask).
- Student forward (WITH grad) on `I_c` -> disparity `D_c`.
- Teacher target: the EMA teacher's existing clean-view disparity `D_t` (ALREADY computed by
  S10 every step — no new teacher forward), cropped with the same box B and resized -> detach.
- Loss = the SAME two S10 terms, reused verbatim: SI-log metric term + normalized-log
  structure anchor, computed between `D_c` and crop(`D_t`).
  KEY FIT: crop-zoom multiplies apparent depth by an unknown global factor; the SI-log term
  subtracts the global log-offset and the struct term is per-image normalized, so BOTH are
  invariant to exactly that ambiguity. We inherit S10's tested loss code instead of new math.
- Mask: crop of the S10 reliability mask M = (M_g · M_d), plus a 4-px crop-border margin.
  Starvation guard reused.
- Schedule: active only when the EMA teacher is active (step >= ema_start_step), with its own
  warmup ramp; weight modest (start 0.2).

New flags (all OFF by default; master `--crop_self_distillation`):
`--crop_distill_weight 0.2  --crop_distill_warmup_steps 1000  --crop_scale_min 0.5
 --crop_scale_max 0.8  --crop_struct_weight 0.5`
No-flag runs remain byte-for-byte S10 behavior.

## 3. Memory / time plan (8GB RTX 4060, batch 12 target) — MEASURED 2026-06-11

S10 peaks ~8.2 GiB at batch 12 (3 forwards: student grad, EMA clean, EMA flip). S11 adds a
2nd GRAD forward (cropped student) — grad activations are the expensive part.
All smokes: 3 full optimizer steps, batch 12, S10 opt.json + crop flags, EMA forced active;
all losses FINITE and stable in every configuration (crop_distill/l_si ~0.0015,
keep_ratio 0.84–0.90). Measured peak-VRAM ladder (allocated / reserved):

| crop subbatch | crop view res | peak alloc | peak reserved |
|---|---|---:|---:|
| 12 (full) | full 640x192 | 12.2 GiB | 12.8 GiB — heavy spill, NOT viable |
| 6 | full | 10.5 GiB | 10.9 GiB |
| 3 | full | 9.6 GiB | 10.0 GiB |
| 12 (full) | half 320x96 | 9.6 GiB | 10.0 GiB |
| **6** | **half 320x96** | **9.1 GiB** | **9.7 GiB ← CHOSEN** |
| 3 | half 320x96 | 8.9 GiB | 9.6 GiB (fallback; only 0.1 GiB below chosen — fixed overhead dominates) |

Chosen gate/full-run config: `--crop_distill_subbatch 6 --crop_view_downsample 2` — closest
to the proven-viable S09 regime (S09 ran a full 30-epoch run at ~8.8 GiB with mild slowdown).
Batch stays 12 and full resolution for ALL ORIGINAL losses (paper setting preserved); the
levers shrink only the ADDED crop lesson (6 of 12 samples, half-res view — S08 precedent).
Runtime bail rule for the gate: if a crop-active epoch exceeds ~90 min, abort and relaunch
with subbatch 3 + half-res. `--crop_view_downsample` validates to {1,2} (feed dims must stay
multiples of 32); half-res keeps the same loss signal (the SI/struct terms are computed on
the same grid as the sampled view, and resolution change is itself part of the BDEdepth
mechanism).

## 4. Gate protocol — single-launch watch-and-bail (user-improved 2026-06-11)

The original plan (separate 8-epoch gate, then restart the full run from 0) was replaced at
the user's suggestion with a strictly better single launch: gate and full run share an
IDENTICAL config + seed, so the first 8 epochs of the full run ARE the gate — no restart.
S10's own run is still the zero-cost control (same seed 0, same recipe), full-val metrics
per epoch in `../10_ema_self_teacher/results/validation_sweep.csv`:
epoch 5: abs_rel 0.4688 / a1 0.5524 · epoch 6: 0.4335 / 0.5545 · epoch 7: 0.4092 / 0.5593.

- Launch ONE run: S10 full config + `--crop_self_distillation --crop_distill_subbatch 6
  --crop_view_downsample 2`, seed 0, batch 12, `--num_epochs 30` (EMA+crop active from
  epoch ~5).
- As checkpoints weights_5/6/7 appear (~5–6 h in), evaluate FULL val (560; not first-100 —
  that fooled us once) on CPU in a separate process (S10-run precedent: epoch-10/18 CPU
  evals) so the GPU training is undisturbed.
- **CONTINUE** (run finishes; this is the full run): val abs_rel better than the S10 control
  at epochs 6 AND 7 by ≥0.005, AND val a1 ≥ control − 0.005 at epoch 7.
- **KILL the run** (ship S10 as the paper result): anything else — including
  "mixed/unclear". Mixed = kill is deliberate given the ~1.5-week budget. Salvage variants
  (e.g. stronger crop weight) exist but cost days; attempting one is a user decision against
  the deadline, not a default.
- **Runtime bail** (independent of metrics): if a crop-active epoch exceeds ~90 min, kill
  and relaunch with the fallback memory config (subbatch 3 + half-res); restart is
  unavoidable only in this branch.
- S11 code and this note are preserved regardless of verdict; a killed S11 can be revisited
  after the deadline or on a larger-memory machine (full-batch full-res needs ~13 GiB).

### Launch 1 post-mortem (2026-06-13/14): BatchNorm-pollution bug, found and fixed

First launch ran on pace (epochs 0-4 ~32 min, crop-active epoch 5 = 44 min, no memory
bail), but the epoch-5 full-val gate eval showed an artifact-class failure: abs_rel 0.5774,
a1 0.3419, median scale-ratio 12.2 (vs S10's 0.4688 / 0.5524 / ~3.4 at the same epoch).
Root cause (confirmed in code): Lite-Mono's encoder contains `nn.BatchNorm2d`
(`networks/depth_encoder.py` stem/CDC blocks); the crop branch runs the STUDENT in train
mode on zoomed half-res sub-batches, so every crop forward updated the BN running
statistics toward crop-view statistics. Train-mode losses stayed healthy (batch stats), but
eval-mode inference (running stats) drifted -> global-scale blow-up. S10 never hit this
because its extra forwards ran on frozen eval-mode EMA copies; the 3-step smoke could not
catch it because it never exercised an eval-mode pass. Fix: freeze all BatchNorm2d modules
(eval mode, running stats as fixed affine, gradients still flow) for the duration of the
crop forward only; the main full-res forward keeps updating BN stats normally. Run 1 was
killed at epoch 5 (~3.5 h spent; classed as a BUG failure, not a method verdict); the
poisoned run folder `s11_crop_distill_b12_30ep_seed0` is kept as evidence; relaunch r2 uses
the patched code under model_name `s11_crop_distill_b12_30ep_seed0_r2`. Gate rules and the
S10-sweep control comparison are unchanged (same seed, fresh from epoch 0, so epoch-matched
comparability is preserved).

## 5. One-shot timeline (fits 1.5 weeks with buffer; single-launch flow)

- Day 0 (done 2026-06-11): implementation, mechanism probe, memory ladder, config locked.
- Day 1 (on user GO): launch the single 30-epoch run in a standalone terminal (lesson from
  the killed first S10 run: Claude-session background jobs die with the session).
- Day 1 +6 h: CPU-evaluate weights_5/6/7 mid-run; apply CONTINUE/KILL rules (Section 4).
- Day 2–3: if CONTINUE, run finishes (~28–32 h total); validation-only checkpoint
  selection; full val/test eval; comparison panels (original/S07/S10/S11).
- Remaining days: paper materials (tables, autopsy figures, honest-limits wording);
  optionally the deferred S10 filter ablation and/or second-sequence generalization eval —
  paper-strengtheners, not blockers.
- If KILLED at the +6 h checkpoint: S10 is the paper result; all remaining days go to the
  ablation, second-sequence evidence, and writing. Either branch lands a complete story.

## 6. Workspace-rule compliance

- Previous snapshots S00–S10 are NOT modified (this plan lives in a NEW `11_*` folder).
- Implementation goes into root `trainer.py`/`options.py` as off-by-default flags;
  `ACTIVE_ROOT_CODE_STATE.md` updated when code lands; tested copies + diff into
  `11_*/code/` + `patches/` per snapshot discipline.
- No training starts without the user's explicit OK on this written plan.
- `AGENTS.md` updated same-turn at pointer altitude; details stay here.
