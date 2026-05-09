# Professor Checks: Loading, Training Images, Sparse LiDAR, And Batch Size

Date: 2026-05-07 to 2026-05-08

Purpose: answer advisor questions before moving fully into Milestone 4:

1. Could the bad Milestone 3 results be caused by incorrect parameter loading?
2. If we evaluate on training images instead of validation images, does the adapted model become high-accuracy?
3. Does the conclusion change if evaluation uses sparse projected LiDAR only, closer to KITTI-style evaluation?
4. Can the laptop run a true batch size closer to the original Lite-Mono training example, and does that fix the result?

Naming rule:

```text
Use experiment descriptions in professor-facing tables.
Keep exact run-folder names in Technical Mapping only.
```

## Parameter-Loading Audit

Compared:

- original checkpoint: `weights/lite-mono/`
- fully depth-frozen Milestone 3 checkpoint:
  `runs/citrus_ss_pretrained_pose_depthencoderfrozen_depthfrozen_50steps/models/weights_0/`

Result:

| component     | loaded model tensors | missing model tensors | changed tensors versus original | max absolute difference |
| ------------- | -------------------: | --------------------: | ------------------------------: | ----------------------: |
| encoder       |            263 / 263 |                     0 |                               0 |                     0.0 |
| depth decoder |              18 / 18 |                     0 |                               0 |                     0.0 |

Notes:

- The original checkpoint contains extra profiling metadata tensors such as `total_ops` and `total_params`; these are not model parameters used by Lite-Mono inference.
- All actual encoder/depth model tensors were available and loaded.
- The fully depth-frozen checkpoint is tensor-identical to the original encoder/depth model.

Interpretation:

```text
The current evidence does not support "wrong parameter loading" as the cause of the Milestone 3 failure.
```

## Evaluation On Training Images And Normal Validation

Saved outputs:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/professor_train_eval_check/
```

Scope:

- training-image evaluation: run inference on the first 100 images from the training split
- normal validation evaluation: run inference on the first 100 images from the validation split
- metrics: per-image mean, same evaluator as Milestone 1/3
- reminder: lower `abs_rel` is better; higher `a1` is better
- no training happens during this step; this is only inference/evaluation using saved checkpoints

## Professor-Facing Result Table

This table avoids internal checkpoint and folder names. Read the columns like this:

- `training images`: evaluation on images from the training split
- `normal validation`: evaluation on images from the validation split
- `Original Lite-Mono weights`: the original pretrained model, with no Citrus fine-tuning

Naming rule for the main tables:

```text
Use experiment descriptions, not run-folder names.
Exact folder names are only kept in Technical Mapping at the end.
```

Read the rows as a story:

1. start from the original pretrained weights
2. protect the depth model for a short warmup
3. allow more depth updates
4. check whether longer or safer training recovers

| setting shown to professor                           | what it means                                         | training images median abs_rel | training images median a1 | normal validation median abs_rel | normal validation median a1 | takeaway                         |
| ---------------------------------------------------- | ----------------------------------------------------- | -----------------------------: | ------------------------: | -------------------------------: | --------------------------: | -------------------------------- |
| Baseline: original Lite-Mono, no Citrus training     | original pretrained model, no Citrus fine-tuning      |                         0.3814 |                    0.4649 |                           0.3680 |                      0.4807 | baseline to beat                 |
| Diagnostic: pose warmup only, depth not updated      | pose learns for 25 updates; depth model is protected  |                         0.3853 |                    0.4726 |                           0.3758 |                      0.4797 | still close to original          |
| Diagnostic: depth allowed to update briefly          | depth model updates for only 5 updates after warmup   |                         0.4105 |                    0.4199 |                           0.3902 |                      0.4484 | quality starts dropping          |
| Diagnostic: depth allowed to update a little longer  | depth model updates for 15 updates after warmup       |                         0.4217 |                    0.4229 |                           0.4409 |                      0.3908 | relative depth gets worse        |
| Diagnostic: short run with depth updates             | depth model updates for 25 updates after warmup       |                         0.6026 |                    0.2460 |                           0.6354 |                      0.2280 | depth structure is badly damaged |
| Conservative control: safer recipe after 250 updates | lower-risk decoder-only recipe checked at 250 updates |                         0.4631 |                    0.4067 |                           0.4542 |                      0.4290 | still below original             |
| Conservative control: same recipe after 1000 updates | same lower-risk recipe checked at 1000 updates        |                         0.6590 |                    0.1901 |                           0.6615 |                      0.1827 | did not recover                  |
| Control: no color augmentation after 250 updates     | same safer recipe, but without color jitter           |                         0.4283 |                    0.4336 |                           0.4108 |                      0.4568 | less bad, still below original   |
| Control: no color augmentation after 500 updates     | same no-color-jitter recipe, trained longer           |                         0.5313 |                    0.3297 |                           0.5300 |                      0.3513 | worsened again                   |

Raw-scale numbers are kept for completeness below. Raw-scale metrics check whether predicted meter values are close before scale correction. Median-scaled metrics are easier for this advisor check because they ask whether the model kept the useful near/far structure after correcting one global scale factor.

| setting shown to professor                           | training images raw abs_rel | normal validation raw abs_rel |
| ---------------------------------------------------- | --------------------------: | ----------------------------: |
| Baseline: original Lite-Mono, no Citrus training     |                      0.7289 |                        0.7289 |
| Diagnostic: pose warmup only, depth not updated      |                      0.7340 |                        0.7274 |
| Diagnostic: depth allowed to update briefly          |                      0.6909 |                        0.6781 |
| Diagnostic: depth allowed to update a little longer  |                      0.6713 |                        0.6697 |
| Diagnostic: short run with depth updates             |                      0.7830 |                        0.7901 |
| Conservative control: safer recipe after 250 updates |                      0.7331 |                        0.7331 |
| Conservative control: same recipe after 1000 updates |                      0.7496 |                        0.7448 |
| Control: no color augmentation after 250 updates     |                      0.7213 |                        0.7192 |
| Control: no color augmentation after 500 updates     |                      0.7251 |                        0.7235 |

Interpretation:

- Evaluation on training images is not high-accuracy for the adapted checkpoints.
- The training-image results show the same broad pattern as normal validation: early depth updates can improve raw-scale `abs_rel`, but median-scaled relative-depth quality worsens.
- This suggests the failure is not just a train/validation generalization problem.
- The stronger explanation remains that the current self-supervised photo objective is not guiding the depth network toward LiDAR-valid Citrus depth quality.

Plain-language summary:

```text
The model is not simply overfitting validation badly.
Even on training images, the adapted checkpoints do not become clearly better than the original model.
```

## Sparse LiDAR-Only / KITTI-Like Sanity Check

Date: 2026-05-08

Purpose: answer the follow-up question, "What if we evaluate closer to the original KITTI LiDAR style?"

What changed for this check:

- main Citrus evaluation uses the prepared semi-dense `local_idw` LiDAR labels plus valid masks
- this sanity check used only raw projected sparse LiDAR pixels
- no `local_idw` filling was used
- no result files were written, so there was nothing to clean up from this check

Scope:

- split: first 100 validation images
- LiDAR-to-camera route: `exact_lidar_parent_child_inverted`
- mean sparse valid coverage: 0.9555% of image pixels
- mean valid sparse pixels per image: 8806

Main result:

| setting shown to professor                           | median-scaled abs_rel | median-scaled a1 | raw abs_rel | takeaway                              |
| ---------------------------------------------------- | --------------------: | ---------------: | ----------: | ------------------------------------- |
| Baseline: original Lite-Mono, no Citrus training     |                0.6072 |           0.3724 |      0.7631 | best of this sparse-label check       |
| Conservative control: same recipe after 1000 updates |                0.8445 |           0.1441 |      0.7809 | clearly worse than original           |
| Control: no color augmentation after 250 updates     |                0.6712 |           0.3234 |      0.7538 | closer, but still worse than original |

Interpretation:

- The sparse-only check is harsher and noisier because it uses less than 1% of image pixels.
- Even with this closer-to-KITTI sparse LiDAR comparison, the adapted checkpoints still do not beat the original model on relative-depth quality.
- This reduces the chance that the Milestone 3 negative result is caused only by the `local_idw` densification step.
- It does not prove the Citrus label pipeline is perfect; it is a sanity check that points in the same direction as the normal evaluation.

## Batch-Size Feasibility Check

Date: 2026-05-08

Purpose: answer the advisor question, "Can we use a batch size closer to the original Lite-Mono training example?"

Reference:

- Lite-Mono README training example uses `--batch_size 12`
- `options.py` default is `--batch_size 16`
- earlier Milestone 3 controlled runs used `--batch_size 4`

Device:

- NVIDIA GeForce RTX 4060 Laptop GPU
- about 8 GB VRAM

One-step CUDA smoke results:

| true batch size | gradient accumulation used? | result | first-step loss | examples/s |
| --------------: | --------------------------- | ------ | --------------: | ---------: |
|               8 | no                          | passed |         0.16359 |        7.0 |
|              12 | no                          | passed |         0.16436 |        6.5 |

Commands used the same general Citrus trainer path:

```text
train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --num_epochs 1 --seed 0 --max_train_steps 1 --drop_path 0
```

Interpretation:

- The laptop can fit a true batch-size-12 one-step CUDA training pass.
- This is closer to the original README training example than the previous batch-size-4 Milestone 3 runs.
- This does not prove a full long run is stable or better.
- It also does not explain away the Milestone 3 degradation by itself; batch size may affect training noise, but previous failures showed depth-structure drift after depth updates.

## Batch-Size-12 Normal One-Epoch Control

Date: 2026-05-08

Purpose: directly test the advisor concern that the earlier batch-size-4 runs might be too noisy by running a normal batch-size-12 Citrus fine-tuning control.

Run:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_batch12_normal_lr_1epoch/
```

Recipe:

- true `--batch_size 12`
- no gradient accumulation
- original Lite-Mono encoder/depth loaded from `weights/lite-mono`
- pose encoder uses pretrained ResNet initialization; pose decoder trains normally
- depth encoder and depth decoder both train from step 0
- no depth freeze and no depth-encoder freeze
- default Lite-Mono LR: depth `0.0001`, pose `0.0001`
- default `drop_path=0.2`
- default Citrus color augmentation probability `0.5`
- one epoch, about 356 optimizer steps
- step checkpoints saved at 100, 200, and 300

Training observation:

- CUDA run finished cleanly.
- The trainer's logged `loss` is the self-supervised optimization loss: mainly photo/reprojection loss, plus a small smoothness term.
- Logged training loss decreased from `0.16435` at the first logged batch to `0.13308` near the end.
- This means the self-supervised photo-matching objective was being optimized.

First 100 training images and first 100 validation images:

Column meaning:

- `training loss`: self-supervised photo-matching objective used during training; lower is better
- `raw abs_rel`: depth error before scale correction; lower is better
- `median-scaled abs_rel`: relative depth/shape error after one scale correction; lower is better
- `a1`: percentage-style accuracy within a tolerance band; higher is better

| setting                                          | training loss, lower better | train images raw abs_rel, lower better | train images median-scaled abs_rel, lower better | train images a1, higher better | validation images raw abs_rel, lower better | validation images median-scaled abs_rel, lower better | validation images a1, higher better |
| ------------------------------------------------ | --------------------------: | -------------------------------------: | -----------------------------------------------: | -----------------------------: | ------------------------------------------: | ----------------------------------------------------: | ----------------------------------: |
| Baseline: original Lite-Mono, no Citrus training |                         n/a |                                 0.7289 |                                           0.3814 |                         0.4649 |                                      0.7289 |                                                0.3680 |                              0.4807 |
| Normal batch-size-12 training, after 100 updates |                     0.14370 |                                 0.7556 |                                           0.7035 |                         0.1290 |                                      0.7521 |                                                0.6906 |                              0.1465 |
| Normal batch-size-12 training, after 200 updates |                     0.13473 |                                 0.6737 |                                           0.7796 |                         0.1277 |                                      0.6643 |                                                0.7540 |                              0.1375 |
| Normal batch-size-12 training, after 300 updates |                     0.13694 |                                 0.6690 |                                           1.1209 |                         0.0851 |                                      0.6468 |                                                1.0451 |                              0.0932 |
| Normal batch-size-12 training, after one epoch   |                     0.13308 |                                 0.7408 |                                           3.0331 |                         0.2616 |                                      0.7190 |                                                3.0501 |                              0.2473 |

Loss-reference row:

| logged point        | training loss, lower better |
| ------------------- | --------------------------: |
| first logged update |                     0.16435 |
| after 100 updates   |                     0.14370 |
| after 200 updates   |                     0.13473 |
| after 300 updates   |                     0.13694 |
| near end of epoch   |                     0.13308 |

Interpretation:

- Batch size 12 did not fix the standard self-supervised adaptation problem.
- The logged training loss went down, so the model was improving at the photo-matching training objective.
- Raw-scale `abs_rel` improved around steps 200-300, but median-scaled relative-depth quality became much worse than the original model.
- The same damage appears on training images and validation images.
- This supports the current Milestone 3 conclusion: the issue is not only small batch size; the ordinary photo-loss adaptation objective is still moving depth structure in a direction that does not match LiDAR-valid Citrus depth.

## Technical Mapping

This section maps the professor-facing labels back to saved run folders. It is only for reproducibility, not for the main presentation table.

| professor-facing setting                                 | saved checkpoint/result source                                               |
| -------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Baseline: original Lite-Mono, no Citrus training         | `weights/lite-mono`                                                          |
| Diagnostic: pose warmup only, depth not updated          | `citrus_ss_seed0_warmup25_depth0_25steps`                                    |
| Diagnostic: depth allowed to update briefly              | `citrus_ss_seed0_warmup25_depth5_30steps`                                    |
| Diagnostic: depth allowed to update a little longer      | `citrus_ss_seed0_warmup25_depth15_40steps`                                   |
| Diagnostic: short run with depth updates                 | `citrus_ss_seed0_warmup25_depth25_50steps`                                   |
| Conservative control: safer recipe after 250 updates     | `citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/models/step_250`    |
| Conservative control: same recipe after 1000 updates     | `citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/models/weights_0`   |
| Control: no color augmentation after 250 updates         | `citrus_ss_seed0_decoderonly_lowdepthlr_noaug_250steps`                      |
| Control: no color augmentation after 500 updates         | `citrus_ss_seed0_decoderonly_lowdepthlr_noaug_500steps`                      |
| Normal batch-size-12 training, after 100/200/300 updates | `citrus_ss_batch12_normal_lr_1epoch/models/step_100`, `step_200`, `step_300` |
| Normal batch-size-12 training, after one epoch           | `citrus_ss_batch12_normal_lr_1epoch/models/weights_0`                        |
