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

## Professor-Facing Result Table

This table avoids internal checkpoint names. Read the rows as a story:

1. start from the original model
2. protect the depth model for a short warmup
3. allow more depth updates
4. see whether longer/more conservative training recovers

| plain setting | what changed during training | train median abs_rel | train median a1 | val median abs_rel | val median a1 | plain takeaway |
|---|---:|---:|---:|---:|---:|---:|
| Original Lite-Mono | no Citrus fine-tuning | 0.3814 | 0.4649 | 0.3680 | 0.4807 | baseline to beat |
| Pose warmup only | pose learns for 25 steps; depth is protected | 0.3853 | 0.4726 | 0.3758 | 0.4797 | stays close to original |
| Very early depth update | only 5 depth-update steps after warmup | 0.4105 | 0.4199 | 0.3902 | 0.4484 | depth quality starts dropping |
| More depth updates | 15 depth-update steps after warmup | 0.4217 | 0.4229 | 0.4409 | 0.3908 | relative depth gets worse |
| Short run with depth updates | 25 depth-update steps after warmup | 0.6026 | 0.2460 | 0.6354 | 0.2280 | depth structure is badly damaged |
| Conservative longer run, early checkpoint | cautious decoder-only recipe at 250 steps | 0.4631 | 0.4067 | 0.4542 | 0.4290 | longer cautious training still below baseline |
| Conservative longer run, final | same cautious recipe at 1000 steps | 0.6590 | 0.1901 | 0.6615 | 0.1827 | did not recover; got worse |
| No color augmentation, 250 steps | same cautious recipe, but no color jitter | 0.4283 | 0.4336 | 0.4108 | 0.4568 | less bad, still below baseline |
| No color augmentation, 500 steps | no color jitter, trained longer | 0.5313 | 0.3297 | 0.5300 | 0.3513 | worsened again |

Raw-scale numbers are kept for completeness below. Raw-scale metrics check whether predicted meter values are close before scale correction. Median-scaled metrics are easier for this advisor check because they ask whether the model kept the useful near/far structure after correcting one global scale factor.

| plain setting | train raw abs_rel | val raw abs_rel |
|---|---:|---:|
| Original Lite-Mono | 0.7289 | 0.7289 |
| Pose warmup only | 0.7340 | 0.7274 |
| Very early depth update | 0.6909 | 0.6781 |
| More depth updates | 0.6713 | 0.6697 |
| Short run with depth updates | 0.7830 | 0.7901 |
| Conservative longer run, early checkpoint | 0.7331 | 0.7331 |
| Conservative longer run, final | 0.7496 | 0.7448 |
| No color augmentation, 250 steps | 0.7213 | 0.7192 |
| No color augmentation, 500 steps | 0.7251 | 0.7235 |

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

## Technical Mapping

This section maps the professor-facing labels back to saved run folders. It is not meant to be the main presentation table.

| plain setting | saved checkpoint/result source |
|---|---|
| Original Lite-Mono | `weights/lite-mono` |
| Pose warmup only | `citrus_ss_seed0_warmup25_depth0_25steps` |
| Very early depth update | `citrus_ss_seed0_warmup25_depth5_30steps` |
| More depth updates | `citrus_ss_seed0_warmup25_depth15_40steps` |
| Short run with depth updates | `citrus_ss_seed0_warmup25_depth25_50steps` |
| Conservative longer run, early checkpoint | `citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/models/step_250` |
| Conservative longer run, final | `citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/models/weights_0` |
| No color augmentation, 250 steps | `citrus_ss_seed0_decoderonly_lowdepthlr_noaug_250steps` |
| No color augmentation, 500 steps | `citrus_ss_seed0_decoderonly_lowdepthlr_noaug_500steps` |
