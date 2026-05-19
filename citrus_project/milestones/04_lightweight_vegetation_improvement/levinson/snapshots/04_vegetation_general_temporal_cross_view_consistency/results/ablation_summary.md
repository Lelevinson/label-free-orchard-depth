# Ablation Summary

First-100 validation at step 250, batch size 12, ImageNet encoder pretrain.

| variant | median-scaled abs_rel | median-scaled a1 | raw abs_rel | raw a1 | conclusion |
|---|---:|---:|---:|---:|---|
| same-budget no-mask control | 0.5634 | 0.3577 | 0.9099 | 0.0000 | reference |
| temporal geometry | 0.5666 | 0.3597 | 0.9033 | 0.0000 | mixed, tiny `a1` gain |
| temporal geometry + default visibility | 0.5688 | 0.3581 | 0.9030 | 0.0000 | negative; visibility threshold was nearly a no-op |
| temporal geometry + strict visibility `0.003` | 0.5884 | 0.3107 | 0.9027 | 0.0000 | negative; mask became too sparse |
| temporal geometry + texture ambiguity | 0.5651 | 0.3605 | 0.9028 | 0.0000 | best tiny `a1` gain, not clean |
| temporal geometry + feature consistency | 0.5581 | 0.3373 | 0.9129 | 0.0000 | mixed; better `abs_rel`, worse `a1` |
| full, reduced feature weight | 0.5755 | 0.3503 | 0.9366 | 0.0000 | negative stacking |

Interpretation: this method family is technically working and self-supervised, but the 250-step evidence does not justify scaling a full training run yet. The most promising branch is temporal geometry plus texture ambiguity weighting, but its advantage over the same-budget control is tiny and only on median-scaled `a1`.
