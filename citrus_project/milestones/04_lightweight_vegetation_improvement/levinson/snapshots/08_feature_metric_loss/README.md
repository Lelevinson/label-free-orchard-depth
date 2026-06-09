# Snapshot 08: Feature-Metric Loss (FeatDepth-style)

Status: implemented, CUDA smoke + 3-epoch gate tested. Conclusion: **STOP / negative-mixed**.
Packaged retroactively on 2026-06-05 (the code was developed directly in root and committed
before this folder existed — see Provenance).

## Method

Label-free, training-only. Adds a FeatDepth-style feature-metric loss on top of the Snapshot 07
teacher-anchor stack:

- a small training-only image autoencoder (`networks/feature_net.py`, `FeatureNet`) produces a
  feature map shaped by reconstruction + first-order discriminative + second-order convergent
  regularizers (so the matching landscape has single convergence basins instead of the flat
  plateaus that raw photometric matching suffers in low-texture canopy);
- source features are reprojected into the target frame with the predicted depth/pose grid and
  compared in feature space (features detached in the matching term so the autoencoder is shaped
  only by its own objective). Runs at half resolution (`--feature_metric_downsample 2`) for memory.

Inference unchanged: single RGB image -> Lite-Mono encoder/depth decoder. The feature net is
discarded at test time.

## Flags (all off by default)

`--feature_metric_loss --feature_metric_weight 0.01 --feature_metric_warmup_steps 500
--feature_metric_channels 16 --feature_recon_weight 1.0 --feature_dis_weight 1e-3
--feature_cvt_weight 1e-3 --feature_metric_downsample 2`

## Result (3-epoch gate, batch 10, first-100 val, weights_2)

| arm | median abs_rel | median a1 |
|---|---:|---:|
| control (S07 stack only) | 0.3150 | 0.5152 |
| experiment (+ feature-metric) | 0.3318 | 0.5169 |

`a1` essentially unchanged (no S04-style tank), but `abs_rel` worsened by 0.0168. Weak/mixed gate
signal, weaker than S05/S07 pilots which improved both metrics. **Not promoted to a full run.**

Compact evidence: `results/gate_eval_results.md`. Run logs:
`runs/s08_gate_logs/` (ignored).

## Verdict

`STOP`. One of two negative "de-blobbing" attempts (with Snapshot 09 / TSOB). Lesson: aggressive
sharpening/feature tricks trade off `abs_rel`; pivot to gentle teacher-quality improvement.

## Provenance / Code State

The S08 code was implemented directly in the active root code and committed together with the
Snapshot 09 (TSOB) code in commit **`2d3e4a2`** ("feat(m4): add TSOB mixture loss + feature-metric
loss"). The original pre-S08/S09 Snapshot 07 root baseline is commit **`ccd0f70`**.

- `code/networks/feature_net.py` — the stage-specific new module (copied).
- `patches/combined_s08_s09_vs_S07baseline_commit2d3e4a2.diff` — the full authoritative diff of all
  root-code additions (`options.py`, `trainer.py`, `networks/`) from the S07 baseline `ccd0f70` to
  `2d3e4a2`. It also contains the Snapshot 09 TSOB code and a tiny untested
  `--teacher_texture_reliability_gate` probe, because all three were committed together; the
  feature-metric-specific parts are `FeatureNet`, the `--feature_*` flags, and trainer
  `compute_feature_metric_losses` / `feature_first_order_l1` / `feature_second_order_l1`.
- The flags remain off by default, so root behavior is unchanged unless explicitly enabled.
