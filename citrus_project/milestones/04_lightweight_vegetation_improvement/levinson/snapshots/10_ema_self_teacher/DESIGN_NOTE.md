# DESIGN_NOTE — Snapshot 10 (S10): EMA In-Domain Self-Teacher with Independent DC/GC Consistency Gating

Status: BUILT, RUN, and a WIN. Produced 2026-06-05 by a multi-agent research + design +
adversarial-review workflow (20 agents); implemented + smoke-tested 2026-06-05; full 30-epoch run
completed 2026-06-10. RESULT (selected weights_29, test median-scaled): abs_rel=0.3080, a1=0.6258 —
a clean win over original Lite-Mono on BOTH metrics and the first Milestone 4 method to BEAT (not
tie) the original on abs_rel; beats Snapshot 07 on abs_rel by ~20% for a small a1 give-back. See
`results/final_result.md`. This is the research-ranked-#1 direction (EC-Depth/ER-Depth family) with
four review-fatal bugs of the naive versions fixed. The spec below is the as-built design.

## 1. Summary

Add ONE new training-only loss `L_dist` on top of the frozen Snapshot 07 stack: an **EMA
(exponential-moving-average) copy of the live student** — which is *in-domain* (learns vegetation
as training proceeds) — supervises the live student in two coupled spaces:
- a small **scale-and-shift-aware metric-log-depth term** (`L_si`) that can actually move
  median-scaled abs_rel, and
- the repo's per-image-normalized log-inverse term (`L_struct`) that protects relative structure,

**only on pixels where two genuinely-independent reliability filters agree**: GC (geometric
min-reprojection error, reused free from `outputs[("photo_error",0)]`) and DC (depth consistency
under a real horizontal-flip of the EMA teacher — NOT the degenerate stochastic-color-aug
comparison). All OFF by default; inference byte-for-byte unchanged (EMA copy discarded at test;
only `encoder.pth`+`depth.pth` load). Adds one (or two, with DC-flip) no-grad forward per step.

Chosen over the multi-frame cost-volume teacher (not safely buildable at batch 12 on 8GB) and over
an equal-weight two-space version (its normalized term dominates ~10x, reproducing S07's tie).

## 2. Why this and not the failed S08/S09

S08 (feature-metric) and S09 (TSOB) both added **boundary-localized energy rewarding commitment at
edges**, applied **densely including on untrustworthy foliage pixels** → nudged a1 but distorted the
global ordinal/scale field → abs_rel rose. No reliability gate, no in-domain target.

S10 is gentle by four independent mechanisms:
1. **Not a sharpening objective** — `L_dist` is a masked L1/Charbonnier pull toward a low-pass
   time-averaged consensus; zero boundary-localized energy.
2. **In-domain self-generated teacher** — the EMA teacher learns citrus, unlike S07's frozen
   urban/blobby teacher (the suspected S07 root weakness).
3. **DC∧GC discard exactly the foliage pixels that broke S08/S09** — geometrically inconsistent
   (high photo_error) and flip-unstable pixels are zeroed, so the loss cannot pull toward a wrong
   value there.
4. **EMA lag (m=0.99, half-life ≈69 steps) + warmup** prevent the teacher echoing the student's
   newest mistake (no fast positive-feedback loop).

**The central honest caveat (and the key fix):** the repo's `normalized_log_inverse_from_disp`
subtracts per-image mean and divides by per-image std; a loss purely in that space only reshapes
z-scored structure, and median-scaled abs_rel divides out global scale/offset at eval — which is
why S07's normalized-space loss only TIED abs_rel. To move abs_rel, S10 MUST include the
scale-and-shift-aware (Eigen SI-log) term on metric log-depth, low weight, gated identically. This
is the single most important fix versus the naive candidates.

## 3. Full math (scale 0 only; injected AFTER `total_loss /= self.num_scales`)

Quantities: student disparity `D_s = outputs[("disp",0)]` (grad, from color_aug forward); EMA
teacher `D_t = outputs[("ema_disp",0)].detach()` (no-grad, on CLEAN color); metric depth
`Z = disp_to_depth(D)`; normalized log-inverse `S = normalized_log_inverse_from_disp(D)`.

**Term A — scale-and-shift-aware metric distillation `L_si` (the abs_rel mover).** Log-depth
`ℓ = log(Z)`, residual `r(p) = ℓ_s(p) − ℓ_t(p)`; remove only the single global offset (the
median-scaling DOF), not the std:
```
r̄   = Σ M(p)·r(p) / (Σ M(p) + 1e-6)
L_si = Σ M(p)·charbonnier(r(p) − r̄) / (Σ M(p) + 1e-6)
```

**Term B — normalized-log structure anchor `L_struct` (protects a1):**
```
L_struct = weighted_mean(charbonnier(S_s − S_t), M)
```

**Combined:** `L_dist = L_si + λ_struct · L_struct`   (λ_struct = 0.5; SI leads, struct anchors).

**Schedule:** `γ(step) = ema_distill_weight · min(1, (step+1 − ema_start_step)/ema_distill_warmup_steps)`
for `step ≥ ema_start_step` else 0. `total_loss += γ(step) · L_dist`.
Defaults: weight 0.3, warmup 2000, start ≈ 5 epochs of steps.

**EMA update (once per optimizer step, after `model_optimizer.step()`):**
```
for ps,pt in zip(student.parameters(), ema.parameters()): pt.mul_(m).add_(ps.detach(), alpha=1−m)
for bs,bt in zip(student.buffers(), ema.buffers()):
    if bt.is_floating_point(): bt.mul_(m).add_(bs.detach(), alpha=1−m)
    else: bt.copy_(bs)
```
`m = 0.99` (optional ramp to 0.999).

**GC-filter (free):** `pe = outputs[("photo_error",0)].detach(); δ_g = ema_gc_tau·mean(pe); M_g = (pe < δ_g)`.
`ema_gc_tau = 3.0` adaptive.

**DC-filter (real geometric aug):** run EMA teacher a 2nd no-grad time on horizontally-flipped clean
target, flip back → `D_t_flip`; in RAW disparity space `dc = |D_t − D_t_flip|; δ_d = ema_dc_tau·mean(dc); M_d = (dc < δ_d)`.
`ema_dc_tau = 3.0`. (Raw disparity, not normalized-log, because flip is normalized-space-equivariant.)

**Mask + starvation guard:** `M = (M_g·M_d).detach(); keep = M.mean(); if keep < ema_min_keep_ratio: γ_eff = 0 this step`.
Log `M.mean()` AND a canopy-restricted keep-ratio (lower 60% rows) every log step — keep-ratio
collapse in canopy is the #1 early-warning instrument. Target band 0.2–0.8.

## 4. Exact integration into trainer.py / options.py

- `import copy` at top.
- Build EMA copies in `__init__` AFTER `self.load_model()` (so deepcopy captures the S07-warm
  student): `self.ema_models = {n: copy.deepcopy(self.models[n]) for n in ("encoder","depth")}`;
  freeze + eval each; keep in **`self.ema_models`, NOT `self.models`** (so set_train/optimizer/
  save_model loops never touch them); do NOT add to `parameters_to_train`.
- Defaults + validation in the `hasattr` block: all `ema_*` defaults; validate `0<decay≤1`,
  weights ≥0, `τ>0`; require monocular + PoseNet + scale 0; require `ema_start_step ≥ freeze_depth_steps`;
  assert `load_weights_folder` set when `ema_self_distillation` on (warm-start enforcement).
- `predict_ema_teacher(inputs, outputs)` called in `process_batch` after `predict_teacher_structure`,
  gated on `step ≥ ema_start_step`: no_grad enc+dec on clean `color`; if DC, also flipped forward
  (reuse the same local var so the first's activations free before the second — no stacked peaks).
- `compute_ema_distill_loss(inputs, outputs)` called in `compute_losses` AFTER the `/num_scales`
  line (beside the tsob/feature_metric blocks): build M_g, M_d, M; L_si; L_struct; starvation guard;
  return γ(step)·L_dist; add to total_loss. Log diagnostics.
- `update_ema()` in run_epoch immediately after `model_optimizer.step()`, gated on
  `not depth_updates_frozen()` (EMA tracks the trained student; avoids BN drift while conv frozen).
- Persistence: save `self.step`/`self.epoch` to a `train_state.pth` and `ema_models` →
  `ema_encoder.pth`/`ema_depth.pth` on per-epoch checkpoints; restore on `load_model` if present.
  (Fixes the verified resume desync — `self.step` is hard-reset to 0 in `train()` and never persisted.)

Reused unchanged: `normalized_log_inverse_from_disp`, `charbonnier`, `weighted_mean`,
`disp_to_depth`, `freeze_module`, `outputs[("photo_error",0)]`. Inference/eval/export untouched.

## 5. New flags (all OFF / inert by default)

```
--ema_self_distillation     (store_true, master switch, default OFF)
--ema_decay 0.99            --ema_decay_final 0.99   (==decay ⇒ no ramp)
--ema_start_step 0          (0 ⇒ auto = 5 epochs of steps)
--ema_distill_weight 0.3    --ema_distill_warmup_steps 2000
--ema_struct_weight 0.5     (λ_struct)
--ema_filter_adaptive       (store_true, τ·mean thresholds, RECOMMENDED ON)
--ema_gc_tau 3.0  --ema_gc_delta 0.04   (fixed-mode, raw photo-error units)
--ema_dc_tau 3.0  --ema_dc_delta 0.03   (fixed-mode, RAW disparity units)
--ema_min_keep_ratio 0.05   (starvation guard floor)
```
Master switch OFF ⇒ byte-for-byte S07 behavior. No DC-residual mode, no fp16 mode in defaults
(both review-flagged degenerate/untested; if memory binds, drop batch size first).

## 6. 8GB / batch-12 memory plan

Baseline S07 ≈ 7.7 GiB (already includes one no-grad frozen-teacher forward). S10 adds a 2nd
(EMA on clean) + a 3rd (DC-flip) no-grad enc+dec forward. EMA weight copies ~12–15 MB, no optimizer
state, no grad. Realistic peak ~8.3–8.9 GiB at batch 12 → likely small WDDM shared-memory spill,
not hard OOM, but UNVERIFIED. **Mandatory one-step CUDA smoke (~20 steps) logging
max_memory_allocated/reserved BEFORE the gate.** Decision rule: if reserved peak > ~7.6 GiB with no
headroom, drop to batch 10 for the full run (proven lever). Never add a cost volume.
Step-time +30–50% → ~48–55 min/epoch → 30-epoch run ≈ 24–28h.

## 7. Gate → full-run protocol

- **Step 0 — memory smoke** (mandatory). Pin the batch that passes; use it for BOTH gate and full run.
- **Pre-gate mechanism check (cheap, ~3 epochs):** S07 + a scale-aware augmentation self-distillation
  arm WITHOUT EMA/filters (just `L_si` on a flip-augmented student view) — does ANY scale-aware
  self-distillation move citrus abs_rel? If the gentlest arm moves it, the heavy EMA may be
  unnecessary; if nothing moves it, early evidence to pivot before 24h.
- **Gate (control vs experiment, same seed + batch):** control = S07 `--num_epochs 10`; experiment =
  S07 + `--ema_self_distillation --ema_filter_adaptive`, real ~5-epoch warmup, weight 0.3. Run the
  REAL median-scaled eval at epoch 10.
  - **Pass:** experiment abs_rel strictly < control AND a1 ≥ control − 0.005 AND canopy keep-ratio in
    0.2–0.8 AND no abs_rel plateau-then-rise.
  - **Kill:** abs_rel ≥ control, OR a1 drops >0.01, OR canopy keep-ratio <0.05 or >0.95.
- **Full run (if gate passes):** warm-start from S07 checkpoint, all S07 flags + gated EMA flags,
  20–30 epochs, checkpoint every epoch (EMA + step state saved). Compare to S07 30-epoch on the same
  test split (median-scaled abs_rel, a1, a2, a3, rmse). Eval loads only encoder+depth (single-image RGB).

## 8. Expected metric movement

Direction: **abs_rel down, a1 flat-to-up** — regime-matched OOD result (EC-Depth under domain shift
abs_rel 0.185→0.111, a1 0.716→0.874, together). Citrus magnitude unknown (no vegetation evidence).
abs_rel can move (unlike S07's tie) because `L_si` is scale-and-shift-aware on metric log-depth — it
supervises relative magnitude that survives median scaling. No S08/S09 trade-off because the
objective is a gentle masked agreement toward a low-pass in-domain consensus, EMA-lagged, and silent
on foliage where it would harm. Most-likely realistic outcome: modest abs_rel improvement if canopy
keep-ratio holds in-band, or near-tie if GC starves the canopy.

## 9. Risks + fallback

1. **Canopy keep-ratio collapse (most-likely failure):** GC keeps low-photo-error pixels; foliage
   reprojects poorly → GC keeps sky/trunk/ground, rejects canopy → trains where already fine → ties
   S07. Mitigate: adaptive τ·mean; canopy-restricted keep-ratio logging; min-keep floor; per-band GC
   threshold if canopy keep <0.1.
2. **Confirmation-bias entrenchment:** EMA preserves the slow blobby-canopy bias. Mitigate:
   independent filters (flip-invariance vs reprojection), keep S07 ranking+sky priors ON as external
   anchor, modest m and γ, abort-on-plateau-then-rise monitor.
3. **DC filter inert (keep ≈1.0):** gating collapses to GC-only. Mitigate: log DC-alone keep-ratio;
   tighten τ_d or report honestly.
4. **Memory spill:** likely small, not OOM. Mitigate: smoke probe + batch 12→10.
5. **Warm-start/freeze ordering:** EMA deepcopy must capture S07-warm student; `ema_start_step ≥
   freeze_depth_steps` (enforced).

**Fallback if gate fails:** (a) cheapest — ship the pre-gate scale-aware augmentation
self-distillation arm alone (research-ranked #3, BDEdepth-style, accuracy-safe) if it moved abs_rel;
(b) if NO self-distillation family member moves clean abs_rel (evidence the self-teacher shares the
student's blobby representation), the only remaining label-free abs_rel lever is the research-ranked
#2 multi-frame cost-volume teacher — a separate larger build requiring the 8GB/AMP/feature-indexing
blockers solved first (gradient-checkpointed plane sweep, batch-8 baseline). Not a quick pivot.

## Provenance

Design produced by workflow `snapshot10-design` (research → brief → 3 parallel designs → 9 adversarial
reviews → synthesis). Primary sources: EC-Depth arXiv 2310.08044 + repo RuijieZhu94/EC-Depth;
ER-Depth ACM 10.1145/3750050; BDEdepth arXiv 2309.05254 (Lite-Mono result); SRD-Depth arXiv 2302.09789;
Mean-Teacher arXiv 1703.01780; Monodepth2 arXiv 1806.01260; ManyDepth 2104.14540 / Mono-ViFI 2407.14126
(cost-volume path + foliage-failure critique). Full technical brief archived alongside this note.
