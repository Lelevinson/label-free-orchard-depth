# Snapshot 10 — partial result at epoch 12 (weights_11)

The 30-epoch run was interrupted at epoch 12 (the Claude session / background process
was closed, which killed the run). All 12 epoch checkpoints survived on disk.
weights_11 evaluated on GPU (full val 560, full test 407), median-scaled:

| model | split | abs_rel | a1 |
|---|---|---:|---:|
| Original Lite-Mono | test | 0.3836 | 0.4989 |
| Snapshot 07 (prev best) | test | 0.3840 | 0.6539 |
| **S10 weights_11 (12 ep)** | test | **0.3339** | 0.6045 |
| **S10 weights_11 (12 ep)** | val  | 0.3764 | 0.5503 |

Read: at only 12/30 epochs, S10 ALREADY beats original Lite-Mono AND Snapshot 07 on
median-scaled abs_rel (0.3339 vs 0.3836/0.3840) — the first method in M4 to beat (not
tie) the original on abs_rel. a1 (0.6045) trails S07 (0.6539) but was still climbing
(val a1 0.5463 @ ep11 -> 0.5503 @ ep12). The method WORKS; needs the full run finished
(a1 to keep climbing) for the final fair comparison. Re-run must survive session close
(run in a standalone terminal, not a Claude background process).

## Trend update — epoch 18 (weights_17), clean restart run

| checkpoint | split | abs_rel | a1 |
|---|---|---:|---:|
| S10 @ ep12 | test | 0.3339 | 0.6045 |
| S10 @ ep18 | test | 0.3197 | 0.6265 |
| S10 @ ep12 | val | 0.3764 | 0.5503 |
| S10 @ ep18 | val | 0.3638 | 0.5666 |
| ref: Snapshot 07 | test | 0.3840 | 0.6539 |
| ref: Original | test | 0.3836 | 0.4989 |

Trajectory: abs_rel still improving (test 0.3339->0.3197, ~17% better than S07/original);
a1 climbing (test 0.6045->0.6265, gap to S07 shrinking 0.049->0.027). On track for a clean
or near-clean win on BOTH metrics by epoch 30. Final verdict pending the finished run +
validation-only checkpoint selection.
