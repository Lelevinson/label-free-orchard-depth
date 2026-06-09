# RGB-Edge + LiDAR + Prior-Distillation Hybrid Plan

Date: 2026-06-08

## One-Sentence Idea

Train a Lite-Mono student with masked LiDAR depth supervision for metric depth, RGB edge-aware regularization for boundary structure, and teacher/prior preservation outside the LiDAR-valid mask so the model does not damage full-frame visual priors such as sky and far background.

```text
RGB image -> student Lite-Mono -> predicted depth

valid LiDAR depth + mask -> metric depth supervision on trusted pixels
RGB image gradients       -> edge-aware smoothness / boundary regularization
frozen teacher checkpoint -> soft depth prior outside LiDAR-valid regions
```

At inference time, only the student Lite-Mono model is used:

```text
RGB image -> student Lite-Mono -> depth
```

No LiDAR and no teacher are used at inference time.

## Training Type

This experiment is a supervised/hybrid training direction, not a pure self-supervised direction.

More precise classification:

1. Masked LiDAR depth loss is supervised, because the student is trained against projected/densified LiDAR depth labels.
2. Teacher/prior preservation is distillation or pseudo-supervision, because a frozen checkpoint provides target depth behavior outside the LiDAR-valid mask.
3. RGB edge-aware smoothness is regularization, not label supervision, but it is part of the hybrid objective.
4. There is no planned pure unsupervised/self-supervised branch in this experiment.

Training inputs:

```text
RGB image + LiDAR depth label + LiDAR valid mask + frozen teacher prediction
```

Inference input:

```text
RGB image only
```

The final model must remain RGB-only and lightweight at inference time.

## Why This Idea Exists

The lab hybrid supervised run gave a useful but incomplete result:

1. `weights_9` is better by validation selection and several LiDAR-valid test metrics.
2. `weights_29` can look more visually plausible in raw full-frame maps, especially sky and far-background regions.
3. The mismatch happens because Citrus metrics only evaluate valid LiDAR-label pixels. Sky and many unlabelled regions can look wrong without affecting the score much.
4. Dense/interpolated LiDAR labels are useful for scale and depth anchoring, but they do not consistently draw clean plant/tree boundaries.
5. RGB frames often show clearer visual boundaries than the LiDAR-derived depth labels: sky vs canopy, ground vs tree row, shadowed vegetation vs bright road.

Therefore, a pure "LiDAR edge loss" is probably too narrow. A better next direction is to combine complementary signals:

1. LiDAR: real metric depth anchor where labels are valid.
2. RGB: boundary/structure cue.
3. Teacher/prior: full-frame sanity guard outside LiDAR supervision.

## Objective Function

Proposed total loss:

```text
L_total =
  L_lidar_valid
+ lambda_smooth * L_rgb_edge_aware_smoothness
+ lambda_prior  * L_teacher_prior_outside_lidar_mask
```

Important normalization rule:

Each loss must be normalized by its own active pixel count or valid support, not by the full image size. This matters because the outside-LiDAR region can be much larger than the valid LiDAR region. Without per-loss normalization, a small `lambda_prior` can still dominate simply because it covers many more pixels.

```text
L_lidar_valid = sum(valid_mask * lidar_error) / max(sum(valid_mask), eps)
L_prior       = sum(outside_mask * teacher_error) / max(sum(outside_mask), eps)
L_smooth      = mean(edge_aware_smoothness_terms)
```

This experiment should report each loss component separately during training.

### 1. Masked LiDAR Depth Loss

Purpose:

Use dense LiDAR labels as the metric depth teacher only where the valid mask says labels are trustworthy.

Possible implementation:

```text
L_lidar_valid = mean( valid_mask * |log(student_depth) - log(lidar_depth)| )
```

Recommended starting point:

Reuse the current successful hybrid supervised recipe:

1. `lidar_loss_type = log_l1`
2. `lidar_loss_weight = 0.1`
3. `lidar_scale_align = none`
4. `lidar_loss_scales = 0`

Reason:

The current hybrid run already improved raw scale strongly versus Plain Citrus. Do not destabilize the known useful part first.

### 2. RGB Edge-Aware Smoothness

Purpose:

Encourage depth to be smooth in visually smooth regions, while allowing depth discontinuities near strong RGB edges.

Common form:

```text
L_smooth =
  |dD/dx| * exp(-|dI/dx|)
+ |dD/dy| * exp(-|dI/dy|)
```

Recommended depth representation:

Apply the smoothness term to inverse depth/disparity or normalized inverse depth, not raw metric depth, unless a later code review finds a strong reason to do otherwise. This follows common monocular-depth practice and avoids over-penalizing raw-depth gradients in far regions.

Plain-language meaning:

1. If RGB changes little, depth should not change wildly.
2. If RGB changes sharply, depth is allowed to change.
3. This does not force every RGB edge to become a depth edge; it only relaxes smoothness at RGB edges.

Recommended starting point:

Use edge-aware smoothness, not hard RGB-depth edge matching.

Reason:

Hard edge matching is risky in Citrus scenes because leaves, shadows, highlights, and texture can create RGB edges that are not true depth edges.

### 3. Teacher Prior Outside LiDAR Mask

Purpose:

Prevent the student from destroying full-frame depth priors in regions that LiDAR does not supervise, especially sky and far background.

Possible implementation:

```text
outside_mask = 1 - dilate(valid_mask)
L_prior = mean( outside_mask * robust_log_depth_difference(student_depth, teacher_depth) )
```

Important detail:

The teacher loss should be applied mostly outside the LiDAR-valid region. Inside the LiDAR-valid region, LiDAR should dominate because it is the actual metric supervision.

Candidate teachers:

| Teacher | Strength | Risk |
|---|---|---|
| Lab `weights_29` | Better raw full-frame sky/background prior than `weights_9`; same lab run/domain | Slightly worse LiDAR-valid relative metrics |
| Earlier Hybrid `weights_13` | Best known hybrid checkpoint by previous val/test metrics | May not preserve sky/background as well; may not be locally/lab available in the same setup |
| Original Lite-Mono | Strong general pretrained visual prior | Bad Citrus metric scale/domain behavior |

Recommended first teacher:

Treat lab `weights_29` as a candidate teacher outside the LiDAR mask, not as ground truth.

Reason:

The motivation came from `weights_29` looking more visually plausible in unlabelled sky/background regions while `weights_9` had better LiDAR-valid metrics. This makes `weights_29` worth testing as an outside-mask prior, but it does not prove `weights_29` is physically correct. It may only look nicer. Therefore, `weights_29` teacher loss must be weak, outside-mask-only, and tested against no-teacher and alternative-teacher ablations.

Teacher-prior variants to test:

| Variant | Description | Why |
|---|---|---|
| No teacher | LiDAR + RGB smoothness only | Required control |
| Raw teacher | Match teacher depth outside mask directly | Tests whether `weights_29` prior helps as-is |
| Scale-aligned teacher | Align teacher/student outside-mask median or mean before loss | Reduces scale tension between LiDAR-controlled valid regions and teacher-controlled invalid regions |
| Alternative teacher if available | Earlier Hybrid `weights_13` or original Lite-Mono | Tests whether `weights_29` was the wrong prior source |

Current execution decision, 2026-06-09:

Raw teacher prior is removed from the first execution pass because `weights_29` is weaker by depth metrics and its better sky/background behavior is not ground truth. The first active runs should focus on the LiDAR-only continued-training control and Branch C, LiDAR + RGB edge-aware smoothness. Teacher-prior variants are deferred until after those cleaner branches are evaluated.

Preferred first teacher-prior loss:

Use a robust log-depth or inverse-depth shape loss outside the dilated LiDAR mask, with an option for outside-mask scale alignment. Do not let the teacher determine global metric scale; LiDAR should control metric scale.

Recommended student initialization:

Start from lab `weights_9` if the goal is to preserve the best lab-selected metric checkpoint and repair its visual-prior weakness.

Alternative:

Start from earlier Hybrid `weights_13` if the old checkpoint is available in the same environment and still confirmed as the strongest overall baseline.

## Literature Support

This plan is not novel because each component already exists somewhere in depth-estimation literature. The possible contribution is the combination and motivation for vegetation-dense agricultural monocular depth adaptation.

### Lite-Mono / Lightweight Monocular Depth

Lite-Mono is the base model family here. The original paper argues for a lightweight CNN/Transformer architecture for self-supervised monocular depth estimation and reports strong accuracy with far fewer trainable parameters than heavier alternatives.

Source:

1. Ning Zhang, Francesco Nex, George Vosselman, Norman Kerle. "Lite-Mono: A Lightweight CNN and Transformer Architecture for Self-Supervised Monocular Depth Estimation." arXiv, 2022. https://arxiv.org/abs/2211.13202

Relevance:

Our inference constraint is RGB-only and lightweight. This plan keeps the Lite-Mono inference architecture unchanged.

### RGB Edge-Aware Smoothness

Monodepth2-style self-supervised monocular depth uses image-aware smoothness to regularize predicted disparity/depth. The idea is common: depth should be smoother in visually smooth regions and allowed to change near image edges.

Source:

1. Clement Godard, Oisin Mac Aodha, Michael Firman, Gabriel Brostow. "Digging Into Self-Supervised Monocular Depth Estimation." ICCV, 2019. https://arxiv.org/abs/1806.01260

Relevance:

RGB edge-aware regularization is a standard and defensible component, not a random invention. However, it must be used softly because RGB edges are not always depth edges.

### Sparse LiDAR + RGB Guidance

Sparse-to-Dense and related depth-completion work supports the idea that sparse LiDAR and RGB provide complementary information: LiDAR supplies geometry/depth samples, while RGB supplies dense visual context.

Sources:

1. Fangchang Ma, Guilherme Venturelli Cavalheiro, Sertac Karaman. "Self-supervised Sparse-to-Dense: Self-supervised Depth Completion from LiDAR and Monocular Camera." ICRA, 2019 / arXiv, 2018. https://arxiv.org/abs/1807.00275
2. Jiaxiong Qiu et al. "DeepLiDAR: Deep Surface Normal Guided Depth Prediction for Outdoor Scene From Sparse LiDAR Data and Single Color Image." CVPR, 2019. https://openaccess.thecvf.com/content_CVPR_2019/html/Qiu_DeepLiDAR_Deep_Surface_Normal_Guided_Depth_Prediction_for_Outdoor_Scene_CVPR_2019_paper.html

Relevance:

Our setting is not standard depth completion because inference must be RGB-only. Still, the training signal logic is related: LiDAR provides depth/scale evidence, while RGB guides dense structure.

### Teacher / Student Distillation For Monocular Depth

Teacher-student and self-distillation approaches have been used in monocular depth estimation to transfer structure, preserve priors, or improve generalization.

Sources:

1. "Pseudo Supervised Monocular Depth Estimation with Teacher-Student Network." arXiv, 2021. https://arxiv.org/abs/2110.11545
2. "TIE-KD: Teacher-Independent and Explainable Knowledge Distillation for Monocular Depth Estimation." arXiv, 2024. https://arxiv.org/abs/2402.14340
3. Haifeng Hu et al. "Monocular Depth Estimation via Self-Supervised Self-Distillation." Sensors, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC11243901/

Relevance:

Using a frozen teacher as a prior-preservation signal is defensible. Our version is deliberately narrower: the teacher is not meant to beat LiDAR supervision; it only guards unlabelled regions from drifting into visually implausible depth.

## Is This Sound?

Yes, conditionally.

It is sound because the losses are assigned to the regions where each signal is strongest:

1. LiDAR-valid pixels: trust LiDAR for metric depth.
2. RGB edges/smooth regions: use RGB to shape regularization, not absolute depth.
3. LiDAR-invalid pixels: use a teacher as a soft prior, not as ground truth.

It would become unsound if:

1. RGB edges are treated as guaranteed depth discontinuities.
2. Teacher predictions are treated as ground truth everywhere.
3. LiDAR interpolation artifacts are treated as perfect labels.
4. We select checkpoints by test-set performance instead of validation.
5. We report full-frame visual plausibility without acknowledging that metrics only cover valid LiDAR pixels.

## Is This Practical?

Yes.

Engineering complexity is moderate:

1. The student is the existing Lite-Mono model.
2. The LiDAR loss already exists in the hybrid supervised draft.
3. RGB edge-aware smoothness can be implemented with finite-difference gradients.
4. Teacher prior requires loading a frozen second Lite-Mono checkpoint during training.
5. Inference cost remains unchanged because the teacher is training-only.

Main practical cost:

Training will be slower because the teacher forward pass adds compute. If necessary, teacher depth can be precomputed for train images, but that creates storage and synchronization overhead.

Recommended first implementation:

Use online teacher inference during a small 1-2 epoch gate. If it is too slow, then consider precomputing teacher depths.

## Is This Research-Worthy?

Potentially yes, but it must be framed honestly.

Weak framing:

"We invented RGB edge-aware loss and distillation."

This is false. Those ideas already exist.

Stronger framing:

"In vegetation-dense agricultural monocular depth adaptation, masked LiDAR supervision improves metric depth but can damage unlabelled full-frame priors. We propose a lightweight RGB-only inference method trained with complementary supervision: LiDAR for metric depth, RGB for boundary-aware regularization, and teacher prior preservation outside LiDAR support."

This is more defensible because it is based on an observed failure mode in our experiments.

Research value depends on whether ablations show:

1. LiDAR-only hybrid improves metric depth but has visual-prior artifacts.
2. Adding RGB edge-aware smoothness improves boundary/structure or reduces oversmoothing without hurting scale.
3. Adding teacher prior improves sky/background/full-frame sanity without sacrificing LiDAR-valid metrics too much.
4. The combined method gives a better balance than any single component.

## Risks And Failure Modes

### Risk 1: RGB Edges Are Not Depth Edges

Leaves, shadows, lighting changes, and texture can create false RGB edges.

Mitigation:

Use edge-aware smoothness, not hard edge alignment. Start with a small weight.

### Risk 2: Teacher Preserves Bad Biases

If `weights_29` is wrong in some regions, the student may inherit those errors.

Mitigation:

Apply teacher loss mostly outside LiDAR-valid pixels and with a small weight. Do not let it override LiDAR supervision. Test both raw and scale-aligned teacher losses, and compare against a no-teacher branch.

Critical limitation:

`weights_29` looking better in sky/background is not proof that it is physically more correct. It may only preserve a visually pleasing prior. This experiment can claim improved full-frame sanity only if the improvement is shown on fixed visual panels and does not meaningfully degrade LiDAR-valid metrics.

### Risk 3: Loss Weights Become A Tuning Trap

Three losses can create many hyperparameters.

Mitigation:

Run ablations in stages. Add one component at a time. Keep the first run small.

### Risk 4: Visual Improvement May Not Show In Standard Metrics

Sky/background sanity may not affect LiDAR-valid metrics.

Mitigation:

Use same-image raw-plus-scaled visual panels as a formal qualitative check. Add a small "sky/background sanity" visual section, but do not pretend it is a quantitative benchmark unless we define a real mask/metric.

Stricter evaluation note:

Visual sanity should be a predefined rejection criterion, not an open-ended way to choose whichever checkpoint looks nicest after training.

### Risk 5: It May Be Too Incremental

The method combines known tools.

Mitigation:

The paper contribution must focus on the agricultural-domain failure mode and ablation evidence, not on claiming the individual losses are new.

## Experiment Stages

### Stage 0: Lock Baselines And Selection Protocol

Goal:

Avoid confusing metric wins with visual wins.

Required references:

1. Plain Citrus baseline.
2. Earlier Hybrid `weights_13`.
3. Lab Hybrid `weights_9`.
4. Lab Hybrid `weights_29`.

Required comparison rule:

Use validation for checkpoint selection. Use test for confirmation only. For visuals, use same-image raw-plus-scaled panels.

Fixed visual protocol:

1. Fix a small validation visual set before training new variants.
2. Include sky/background-heavy images, ordinary orchard-row images, and difficult vegetation-boundary images.
3. Use fixed colormap limits when comparing the same image across models.
4. Always show RGB, valid mask, raw depth, median-scaled depth, and LiDAR-valid error map.
5. Do not let a post-hoc "this looks nicer" impression choose the final checkpoint.

Primary checkpoint selection:

Use validation `abs_rel` and `a1` on LiDAR-valid pixels.

Secondary rejection rule:

Reject a checkpoint if it has obvious predefined visual failures on the fixed visual set, such as:

1. sky/far background collapsing into a near-depth cave in multiple fixed examples
2. large unnatural discontinuity around the LiDAR valid-mask boundary
3. severe loss of tree/ground separation compared with the baseline student

These rejection rules are safeguards, not a replacement for validation metrics.

### Stage 0.5: LiDAR-Only Continued Training Control

Goal:

Control for the effect of extra training time. Without this, any improvement might be incorrectly credited to RGB smoothness or teacher prior.

Loss:

```text
L_total = L_lidar_valid
```

Requirement:

Use the same training budget as the first short ablation runs. This control should be included in the minimum ablation table.

### Stage 1: Reproduce Student Initialization

Goal:

Start from the chosen student checkpoint and run a short sanity gate.

Recommended student:

Lab `weights_9` if working from lab artifacts.

Gate:

1. 0.5 to 1 epoch.
2. Confirm loss does not explode.
3. Generate same-image panels.
4. Confirm no immediate sky/background collapse beyond the starting checkpoint.

### Stage 2: Add RGB Edge-Aware Smoothness Only

Goal:

Test whether RGB regularization improves boundaries/structure without changing the LiDAR-depth anchor too much.

Loss:

```text
L_total = L_lidar_valid + lambda_smooth * L_rgb_edge_aware_smoothness
```

Initial weight:

Small. Example search:

```text
lambda_smooth in {0.001, 0.005, 0.01}
```

Stop condition:

If LiDAR-valid `abs_rel` worsens clearly and visuals do not improve, do not continue this branch.

### Stage 3: Add Teacher Prior Only

Goal:

Test whether teacher preservation fixes full-frame/sky priors without losing LiDAR-valid accuracy.

Loss:

```text
L_total = L_lidar_valid + lambda_prior * L_teacher_prior_outside_lidar_mask
```

Teacher:

Start with lab `weights_29` only as a candidate prior source, not a trusted depth teacher.

Initial weight:

Small. Example search:

```text
lambda_prior in {0.01, 0.03, 0.05}
```

Teacher-loss variants:

```text
raw outside-mask teacher prior
scale-aligned outside-mask teacher prior
```

Decision rule:

If raw teacher prior improves visuals but hurts LiDAR-valid metrics, try the scale-aligned prior before discarding the teacher branch. If both hurt metrics or create new artifacts, drop teacher prior and keep the no-teacher RGB-smoothness branch.

Mask:

Use outside-mask loss:

```text
outside_mask = 1 - dilated(valid_lidar_mask)
```

Use dilation so the teacher does not fight LiDAR near uncertain label boundaries.

### Stage 4: Combine RGB Smoothness + Teacher Prior

Goal:

Test whether the two fixes complement each other.

Loss:

```text
L_total =
  L_lidar_valid
+ lambda_smooth * L_rgb_edge_aware_smoothness
+ lambda_prior  * L_teacher_prior_outside_lidar_mask
```

Start with the best weights from Stage 2 and Stage 3, not a huge blind grid.

### Stage 5: Evaluation And Reporting

Metrics:

1. Validation and test raw depth metrics.
2. Validation and test median-scaled metrics.
3. Same-image raw-plus-scaled visual panels.
4. Boundary-focused qualitative panels.
5. Sky/background sanity panels.
6. Runtime/parameter count remains unchanged at inference.

Recommended checkpoint selection:

1. Select by validation metrics and visual sanity.
2. Confirm on test.
3. Do not select by test.

Minimum ablation table:

| Model | LiDAR loss | RGB smoothness | Teacher prior | Purpose |
|---|---|---|---|---|
| Student baseline | existing | no | no | Current best metric baseline |
| Teacher/reference baseline | existing | no | no | Visual-prior reference, not ground truth |
| LiDAR-only continued training | yes | no | no | Controls for extra training |
| LiDAR + RGB smoothness | yes | yes | no | Tests RGB regularization |
| Optional LiDAR + scale-aligned teacher prior | yes | no | scale-aligned outside-mask | Tests safer prior preservation only after Branch C |
| Optional LiDAR + RGB + best teacher variant | yes | yes | best validated variant | Tests final combination only if teacher branch earns it |

Evaluation warnings:

1. Do not claim "more accurate full-frame depth" unless a real full-frame evaluation target exists.
2. It is acceptable to claim "better metric-visual balance" only if LiDAR-valid metrics remain competitive and fixed visual panels improve according to the predefined rejection/sanity rules.
3. Visual panels are evidence, not ground truth.

## Success Criteria

Minimum acceptable success:

1. Does not significantly degrade lab `weights_9` LiDAR-valid test abs_rel.
2. Improves full-frame visual sanity compared with `weights_9`.
3. Does not produce obvious sky/cave artifacts on same-image raw panels.

Strong success:

1. Matches or beats earlier Hybrid `weights_13` on test abs_rel/a1.
2. Looks closer to `weights_29` or better for sky/background priors.
3. Shows better boundary behavior than both `weights_9` and `weights_29`.
4. Keeps inference RGB-only and lightweight.

Failure:

1. Metrics improve only by exploiting LiDAR mask while full-frame predictions get worse.
2. Visuals improve only in sky but LiDAR-valid orchard depth collapses.
3. The method requires too much tuning to beat the current hybrid baseline.

## Expected Heat-Map Outcome

This experiment should improve the chance that the heat/depth map looks more globally sane, but it does not guarantee a fully correct heat map.

What we expect to improve:

1. LiDAR-valid orchard/ground/tree regions should remain metrically stronger than Plain Citrus.
2. RGB edge-aware smoothness should reduce some boundary bleeding and unreasonable depth changes in visually smooth regions.
3. Teacher-prior preservation should reduce `weights_9`-style full-frame artifacts, especially cave-like sky/background behavior.

What may still be wrong:

1. Sky has no real LiDAR depth label, so even teacher preservation is only a prior, not ground truth.
2. RGB edges can be false depth edges because shadows, leaf texture, and lighting changes can produce strong color boundaries.
3. Dense LiDAR labels do not perfectly trace vegetation, so boundary metrics may still be imperfect.
4. Monocular depth is inherently ambiguous; a single RGB frame cannot always infer exact metric depth everywhere.

Realistic target:

The goal is not a perfect heat map. The goal is a better balance than the current choices:

```text
weights_9: better LiDAR-valid metrics, weaker full-frame visual prior
weights_29: better sky/background visual prior, weaker LiDAR-valid relative metrics
```

A successful model should keep most of the metric advantage of `weights_9` while looking closer to `weights_29` or better in sky/background and full-frame raw-depth sanity.

## Honest Recommendation

Proceed with this experiment, but do not oversell it.

This is a good idea because it directly responds to a real observed failure mode:

```text
LiDAR-valid metrics can prefer a checkpoint whose full-frame raw depth looks visually worse.
```

The proposed method is not groundbreaking at the component level. LiDAR supervision, RGB edge-aware smoothness, and distillation all have precedent. The possible research contribution is the agricultural-domain combination, the careful mask-aware objective, and the evidence that the method balances metric depth with full-frame visual sanity better than LiDAR-only adaptation.

The next implementation should be staged and ablation-driven. If Stage 2 or Stage 3 fails, stop that branch early rather than forcing a combined method.
