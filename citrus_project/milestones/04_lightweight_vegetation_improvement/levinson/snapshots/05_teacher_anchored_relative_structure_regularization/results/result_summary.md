# Snapshot 05 Result Summary

Full 30-epoch run:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/
```

Final checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/runs/teacher_structure_regularization_b12_30ep_full/models/weights_29/
```

Full validation/test comparison:

| model | split | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| Original Lite-Mono | val | 0.7128 | 0.0195 | 0.4176 | 0.4629 |
| B0 plain Citrus | val | 0.7736 | 0.0074 | 0.5100 | 0.6107 |
| Snapshot 05 | val | 0.7372 | 0.0169 | 0.4611 | 0.5954 |
| Original Lite-Mono | test | 0.7273 | 0.0149 | 0.3836 | 0.4989 |
| B0 plain Citrus | test | 0.7787 | 0.0077 | 0.4889 | 0.6582 |
| Snapshot 05 | test | 0.7359 | 0.0147 | 0.4132 | 0.6463 |

First-100 validation reference:

| model | budget | raw abs_rel | raw a1 | median-scaled abs_rel | median-scaled a1 |
|---|---|---:|---:|---:|---:|
| Snapshot 04 no-mask control | 250 steps | 0.9099 | 0.0000 | 0.5634 | 0.3577 |
| Snapshot 04 best branch | 250 steps | 0.9028 | 0.0000 | 0.5651 | 0.3605 |
| Snapshot 05 | final 30-epoch checkpoint | 0.7314 | 0.0053 | 0.3444 | 0.6510 |

The first-100 Snapshot 05 row is useful for orientation but is not same-budget with the 250-step Snapshot 04 gates.
