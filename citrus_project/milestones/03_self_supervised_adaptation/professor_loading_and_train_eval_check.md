# Professor Check: Loading And Train-Image Evaluation

Date: 2026-05-07

Purpose: answer two advisor questions before moving fully into Milestone 4:

1. Could the bad Milestone 3 results be caused by incorrect parameter loading?
2. If we evaluate on training images instead of validation images, does the adapted model become high-accuracy?

## Parameter-Loading Audit

Compared:

- original checkpoint: `weights/lite-mono/`
- fully depth-frozen Milestone 3 checkpoint:
  `runs/citrus_ss_pretrained_pose_depthencoderfrozen_depthfrozen_50steps/models/weights_0/`

Result:

| component | loaded model tensors | missing model tensors | changed tensors versus original | max absolute difference |
|---|---:|---:|---:|---:|
| encoder | 263 / 263 | 0 | 0 | 0.0 |
| depth decoder | 18 / 18 | 0 | 0 | 0.0 |

Notes:

- The original checkpoint contains extra profiling metadata tensors such as `total_ops` and `total_params`; these are not model parameters used by Lite-Mono inference.
- All actual encoder/depth model tensors were available and loaded.
- The fully depth-frozen checkpoint is tensor-identical to the original encoder/depth model.

Interpretation:

```text
The current evidence does not support "wrong parameter loading" as the cause of the Milestone 3 failure.
```

## Train-Image Evaluation Check

Saved outputs:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/professor_train_eval_check/
```

Scope:

- split: first 100 training samples
- comparison: matching first 100 validation summaries where available
- metrics: per-image mean, same evaluator as Milestone 1/3
- reminder: lower `abs_rel` is better; higher `a1` is better

| checkpoint | train raw abs_rel | train median abs_rel | train median a1 | val raw abs_rel | val median abs_rel | val median a1 |
|---|---:|---:|---:|---:|---:|---:|
| original | 0.7289 | 0.3814 | 0.4649 | 0.7289 | 0.3680 | 0.4807 |
| seed0 depth0/25 | 0.7340 | 0.3853 | 0.4726 | 0.7274 | 0.3758 | 0.4797 |
| seed0 depth5/30 | 0.6909 | 0.4105 | 0.4199 | 0.6781 | 0.3902 | 0.4484 |
| seed0 depth15/40 | 0.6713 | 0.4217 | 0.4229 | 0.6697 | 0.4409 | 0.3908 |
| seed0 depth25/50 | 0.7830 | 0.6026 | 0.2460 | 0.7901 | 0.6354 | 0.2280 |
| conservative step250 | 0.7331 | 0.4631 | 0.4067 | 0.7331 | 0.4542 | 0.4290 |
| conservative final1000 | 0.7496 | 0.6590 | 0.1901 | 0.7448 | 0.6615 | 0.1827 |
| no aug 250 | 0.7213 | 0.4283 | 0.4336 | 0.7192 | 0.4108 | 0.4568 |
| no aug 500 | 0.7251 | 0.5313 | 0.3297 | 0.7235 | 0.5300 | 0.3513 |

Interpretation:

- Training-image evaluation is not high-accuracy for the adapted checkpoints.
- The train split shows the same broad pattern as validation: early depth updates can improve raw-scale `abs_rel`, but median-scaled relative-depth quality worsens.
- This suggests the failure is not just a train/validation generalization problem.
- The stronger explanation remains that the current self-supervised photo objective is not guiding the depth network toward LiDAR-valid Citrus depth quality.

Plain-language summary:

```text
The model is not simply overfitting validation badly.
Even on training images, the adapted checkpoints do not become clearly better than the original model.
```
