# Snapshot 09: TSOB Boundary-Uncertainty Mixture

Status: implemented, CUDA smoke + 3-epoch gate + **full 30-epoch run** + checkpoint selection +
visual inspection. Conclusion: **STOP / negative**. Packaged retroactively on 2026-06-05.

## Method

Label-free, training-only. TSOB-style (BMVC 2025, arXiv 2509.15987) K=2 depth-mixture loss on top
of the Snapshot 07 teacher-anchor stack:

- a small training-only head (`networks/mixture_head.py`, `MixtureHead`) reads the decoder's
  scale-0 features (exposed via a one-line `("disp_feat", 0)` add in `networks/depth_decoder.py`)
  and outputs a second depth hypothesis offset, two per-component uncertainties, and a mixing
  weight;
- a moment-matching / Laplacian-NLL loss warps both hypotheses into the target frame and pushes
  the model to COMMIT to one hypothesis at boundaries instead of averaging them into a blob, with
  entropy + spatial-smoothness regularizers on the mixing weight.

Inference unchanged: single RGB image -> Lite-Mono encoder/depth decoder (uses the mean/`mu_0`
disparity). The mixture head is discarded at test time.

## Flags (all off by default)

`--tsob_mixture_loss --tsob_weight 0.1 --tsob_warmup_steps 200 --tsob_alpha_entropy_weight 0.01
--tsob_alpha_smooth_weight 0.01 --tsob_sigma_min 0.01`

## Results

3-epoch gate (first-100 val) initially looked like a win, but **full-560 val re-verification**
showed it was a small-sample artifact: a1 robustly up, abs_rel within control noise. The full
30-epoch run (batch 12, laptop) settled the question.

Validation-selected `weights_24` (B0-close-a1 rule), **test set**:

| model (test) | median abs_rel | median a1 |
|---|---:|---:|
| Original Lite-Mono | 0.3836 | 0.4989 |
| Snapshot 07 (lead) | 0.3840 | 0.6539 |
| **TSOB weights_24** | 0.4331 | 0.6492 |

TSOB is **worse than Snapshot 07 on both test metrics** (clearly worse abs_rel, marginally worse
a1). Visual panels (`runs/s09_tsob_full_logs/visuals/compare_original_s07_tsob.png`) show **no
visible de-blobbing** — all three produce smooth ground-plane gradients; none crisply resolves side
vegetation. The "sharper but overconfident -> bigger errors" pattern (the TSOB paper's own caveat)
held: a1/a2/a3 broadly up vs a 3-epoch control but abs_rel/sq_rel/rmse up.

Evidence: `results/gate_eval_summary.txt`; run logs + checkpoint selection + visuals under
`runs/s09_tsob_full_b12_30ep_seed0/` and `runs/s09_tsob_full_logs/` (ignored).

## Verdict

`STOP`. Negative result, numerically and visually. Snapshot 07 remains the lead. Second of two
negative de-blobbing attempts (with Snapshot 08). Lesson reinforced: aggressive boundary-sharpening
backfires; pivot to gentle teacher-quality improvement (EMA self-teacher direction).

## Provenance / Code State

Committed together with Snapshot 08 in commit **`2d3e4a2`**; original S07 baseline is **`ccd0f70`**.

- `code/networks/mixture_head.py`, `code/networks/depth_decoder.py` — stage-specific code (copied).
- `patches/combined_s08_s09_vs_S07baseline_commit2d3e4a2.diff` — full authoritative diff from S07
  baseline `ccd0f70` to `2d3e4a2`. TSOB-specific parts: `MixtureHead`, the `("disp_feat", 0)`
  exposure, the `--tsob_*` flags, and trainer `compute_tsob_mixture_loss`.
- Flags remain off by default; root behavior unchanged unless explicitly enabled.
