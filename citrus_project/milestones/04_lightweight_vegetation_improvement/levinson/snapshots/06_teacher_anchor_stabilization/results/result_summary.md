# Snapshot 06 Result Summary

Snapshot 06 tested the same frozen RGB-only teacher branch as Snapshot 05, but reduced the ranking loss from `0.02` to `0.005` and removed texture-ambiguity emphasis.

Conclusion: `promising mixed / marginal stabilization`. Validation improves slightly over Snapshot 05 on both median-scaled `abs_rel` and `a1`, but test is slightly worse on both median-scaled metrics. Snapshot 06 still beats B0 on median-scaled `abs_rel`, still trails B0 on median-scaled `a1`, and still does not beat original Lite-Mono on median-scaled `abs_rel`.

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Snapshot 06 | val | 0.7375 | 0.0165 | 0.4578 | 0.5993 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |
| Snapshot 06 | test | 0.7348 | 0.0150 | 0.4168 | 0.6418 |

First-100 validation orientation for Snapshot 06 final checkpoint: raw `abs_rel=0.7314`, raw `a1=0.0053`, median-scaled `abs_rel=0.3458`, median-scaled `a1=0.6558`.

Artifacts:

- Full run: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/`
- Final checkpoint: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_anchor_stabilization_b12_30ep_rank005_no_texture/models/weights_29/`
- Main generated results: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/local_evidence/final_weights29_evaluation_full/`
- Snapshot package: `citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/06_teacher_anchor_stabilization/`
