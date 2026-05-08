# Advisor Notes

This file tracks professor/advisor questions, recommendations, and follow-up research directions that should not get lost between chats or meetings.

Use it for:

1. questions that may affect later experiments
2. suggested reference directions
3. possible side studies or ablations
4. advice that is worth revisiting after the current milestone

Keep each entry short and practical:

- date
- what was asked or suggested
- why it might matter
- current interpretation
- follow-up action

## 2026-04-23 - Frame-motion sensitivity during self-supervised training

### Advisor question

What happens if the speed or motion between two neighboring frames is quite different? Will that affect prediction quality?

### Why it matters

This is relevant mainly to self-supervised training, because Lite-Mono-style monocular training relies on neighboring frames, predicted relative pose, and view-synthesis consistency.

Large or irregular frame-to-frame motion can reduce overlap, increase occlusion, and make the reprojection signal noisier.

### Current interpretation

1. This is a good research question, but not a main milestone by itself.
2. It is better treated as a later sub-study or ablation after the baseline and core adaptation path are working.
3. Best fit for now:
   - later Milestone 3 analysis, or
   - Milestone 4 supporting analysis
4. It should not replace the main improvement idea unless later evidence shows it is central to the method.

### Professor recommendation

Look for references that may connect to speed estimation or frame-to-frame motion handling, for example from highway speed camera / traffic speed detection work.

### Our current view on that recommendation

Partly related, but not directly the same problem.

Most highway speed-camera work is about estimating vehicle speed or displacement from video, radar, or tracked image motion. That is not the same as monocular depth estimation.

The most relevant overlap is likely in:

1. frame-to-frame motion estimation
2. optical flow / image displacement
3. ego-motion robustness
4. motion blur sensitivity
5. frame selection or frame sampling under variable motion

So:

1. traffic speed-detection references may be useful as secondary inspiration
2. they should not be the main literature base for this question
3. higher-priority references should still come from self-supervised depth, visual odometry, optical flow, and motion-robust video learning

### Follow-up action

1. Track this as a later analysis candidate, not a current milestone blocker.
2. Ask Friend A to note possible motion-robustness references in `literature_tracker.md`.
3. Revisit after Milestone 1 baseline results and before Milestone 4 improvement selection.

## 2026-05-08 - Milestone 3 loading, train-image, and sparse-LiDAR checks

### Advisor question

Could the bad Milestone 3 fine-tuning results be caused by incorrect weight loading, accidental training from scratch, validation-only generalization failure, or evaluation labels that are too different from KITTI LiDAR evaluation?

### Why it matters

If any of those simpler explanations were true, Milestone 3 would be an infrastructure/debugging problem rather than evidence that standard self-supervised Citrus adaptation is weak under the tested recipe family.

### Current interpretation

1. Original encoder/depth tensors load correctly from `weights/lite-mono`; the depth-frozen checkpoint matches original encoder/depth tensors exactly.
2. Evaluation on first-100 training images is not high-accuracy for adapted checkpoints, so the issue is not only validation-split generalization.
3. A sparse LiDAR-only first-100 validation sanity check, closer to KITTI-style projected LiDAR comparison and using no `local_idw` filling, still shows the adapted checkpoints worse than original on median-scaled relative-depth quality.

### Follow-up action

Use these checks as Milestone 3 closeout evidence. Milestone 4 should target the depth-structure drift directly instead of running longer versions of the same standard self-supervised recipe.

## 2026-05-08 - Batch-size feasibility on laptop GPU

### Advisor question

Could the smaller Milestone 3 batch size affect the fine-tuning result, and can the laptop run closer to the original Lite-Mono batch size?

### Why it matters

Batch size changes how many examples contribute to each optimizer update. A larger batch can make the training signal less noisy, so it is a reasonable experimental-control question.

### Current interpretation

The Lite-Mono README training example uses `--batch_size 12`, while previous Milestone 3 controlled runs used `--batch_size 4`. On the RTX 4060 Laptop GPU, true batch-size one-step CUDA smokes passed for batch sizes 8 and 12 with no gradient accumulation.

A normal one-epoch batch-size-12 Citrus control was then run with default LR, default drop path, default color augmentation, and no depth freezing. It finished cleanly, and photo loss decreased from about `0.164` to `0.133`, but first-100 validation median-scaled depth quality worsened from the original baseline `abs_rel=0.3680`, `a1=0.4807` to final one-epoch `abs_rel=3.0501`, `a1=0.2473`.

This means batch size 12 is technically feasible, but larger true batch size did not fix the Milestone 3 depth-structure drift in the normal control.

### Follow-up action

Use the batch-size-12 result as an advisor-facing control. Do not spend more time on larger-batch versions of the same standard recipe unless there is a new technical reason.
