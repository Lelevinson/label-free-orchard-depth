# Snapshot 08 Gate Evaluation — 2026-06-03

Both arms: batch 10, seed 0, 3 epochs, ImageNet-pretrain init, Snapshot 07 teacher-anchor stack.
Evaluated: first-100 validation, final checkpoint weights_2.

| arm | median abs_rel ↓ | median a1 ↑ | raw abs_rel | raw a1 |
|---|---:|---:|---:|---:|
| control (S07 stack only) | 0.3150 | 0.5152 | 0.8105 | 0.0112 |
| experiment (S07 + feature-metric) | 0.3318 | 0.5169 | 0.7478 | 0.0062 |

a1 guard: NOT triggered (a1 delta = +0.0017, feature-metric did not tank a1).
abs_rel: experiment WORSE by 0.0168 at 3 epochs.

Context: feature_metric_warmup_steps=500; at 3 epochs (3×357=1071 steps) the weight
only just cleared warmup. The basin-shaping benefit may not have matured.
Verdict: mixed / not a clear gate pass. Recommendation: pending decision.
