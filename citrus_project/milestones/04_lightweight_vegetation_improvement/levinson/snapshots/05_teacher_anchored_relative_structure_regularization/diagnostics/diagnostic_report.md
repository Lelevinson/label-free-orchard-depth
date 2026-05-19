# Snapshot 05 Diagnostic Report

Date: 2026-05-17

Status: full 30-epoch run completed. Conclusion: promising mixed evidence; continue, but do not claim a clean win over original Lite-Mono.

## What Was Tested

Snapshot 05 used a frozen RGB-only Lite-Mono teacher from:

```text
weights/lite-mono/
```

The student was trained from the same B0 fair recipe: ImageNet encoder pretrain through `--mypretrain weights/lite-mono/lite-mono-pretrain.pth`, no `--load_weights_folder weights/lite-mono` for the student, batch size 12, 30 epochs, Citrus prepared temporal monocular frames, and `seed=0`.

Enabled training-only losses:

- scale-invariant normalized log inverse-depth structure agreement
- local normalized-disparity gradient agreement
- sparse pairwise ordinal/ranking consistency
- weak texture ambiguity emphasis as a teacher-loss prior

Teacher confidence was implemented but left off for this full run to avoid extra cost and because the main teacher anchor was the intended test.

## Smoke And Stability

Checks passed:

- `py_compile` passed with redirected Python bytecode cache.
- `train.py --help` showed the new teacher flags.
- CUDA batch-size-12 one-step smoke completed with finite losses.
- Full 30-epoch run completed without NaNs or crashes.

Final logged diagnostics from `diagnostics_last_logged.json`:

| signal | value |
|---|---:|
| final global step | 10624 |
| final train batch total loss | 0.0755 |
| teacher structure diff mean | 0.1581 |
| teacher structure weighted loss | 0.00238 |
| teacher gradient loss | 0.00731 |
| teacher ranking loss | 0.2939 |
| teacher ranking agreement | 0.9819 |
| teacher ranking valid ratio | 0.8354 |
| texture ambiguity high-ratio | 0.4097 |

The ranking signal did run and became highly aligned by the end. The teacher losses were nonzero but moderate, so they regularized the photometric training rather than replacing it.

## Metrics

Snapshot 05 improves strongly over B0 on `abs_rel` while mostly preserving B0's `a1` improvement:

- validation median-scaled `abs_rel`: B0 `0.5100` to Snapshot 05 `0.4611`
- test median-scaled `abs_rel`: B0 `0.4889` to Snapshot 05 `0.4132`
- validation raw `abs_rel`: B0 `0.7736` to Snapshot 05 `0.7372`
- test raw `abs_rel`: B0 `0.7787` to Snapshot 05 `0.7359`

Against original Lite-Mono, Snapshot 05 is mixed:

- improves median-scaled `a1` on validation and test
- still worsens median-scaled `abs_rel` on validation and test
- raw metrics are close but still slightly worse

This makes Snapshot 05 the strongest Levinson label-free direction so far, but not a clean paper claim yet.

## Qualitative Check

Generated qualitative folders:

```text
local_evidence/visual_summary/visual_compare_original_vs_snapshot05_val_full/
local_evidence/visual_summary/visual_compare_b0_vs_snapshot05_val_full/
local_evidence/visual_summary/teacher_structure_diagnostic_maps/
```

The checked B0-vs-Snapshot05 panel for sample `0094` is coherent: Snapshot 05 keeps the broad path/tree depth layout and reduces the sample median-scaled error slightly (`abs_rel=0.149` vs B0 `0.171`) while keeping `a1` essentially tied.

The teacher/student normalized-structure difference and gradient-error maps are visually meaningful rather than blank. They emphasize object boundaries, canopy edges, and ground/tree transitions. They are still smoother than true thin-branch geometry, so they should be treated as structure anchors, not as depth labels.

## Diagnosis

Why Snapshot 05 helped:

- The frozen RGB teacher supplies an external relative-structure anchor, unlike Snapshot 04's self-comparison across nearby frames.
- Per-image normalization avoids forcing the student's metric scale to copy the teacher.
- Ranking loss directly targets near/far ordering, which matches the recurring Milestone 3/B0 failure pattern.
- Gradient agreement preserves some teacher edge layout without using RGB edges as direct depth edges.

Why it is still not a clean win:

- The teacher comes from the original checkpoint, so it can preserve useful relative ordering but also anchors some non-Citrus bias.
- The student still depends on the photometric video objective for adaptation, and photometric ambiguity remains difficult in repeated vegetation.
- The method improves average relative error over B0, but B0's threshold `a1` advantage is slightly higher on the full splits.

Recommended next step:

Continue from Snapshot 05, but tune one clear revision rather than launching many variants. The most sensible follow-up is to preserve the current teacher anchor and test a lighter or scheduled ranking/gradient mix that tries to recover B0-level `a1` without losing the `abs_rel` gains.
