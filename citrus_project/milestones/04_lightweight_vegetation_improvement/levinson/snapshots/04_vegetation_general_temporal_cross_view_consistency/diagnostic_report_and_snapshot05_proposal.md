# Snapshot 04 Diagnostic Report and Snapshot 05 Proposal

Date: 2026-05-17

Status: historical diagnostic/proposal note. The Snapshot 05 proposal was implemented, then superseded by Snapshot 07 as the current lead Levinson label-free candidate. Keep this file for provenance and failure analysis; do not treat it as a current action plan.

Update on 2026-05-17: the proposed Snapshot 05 direction below was implemented and full-run tested under `../05_teacher_anchored_relative_structure_regularization/`. The older design wording here is retained as the diagnostic handoff from Snapshot 04, but the active Snapshot 05 name is Teacher-Anchored Relative-Structure Regularization.

Verdict: Snapshot 04 is stable but weak negative evidence. Do not scale it.

## 1. Why Temporal Geometry Gave Only Tiny Gains

Temporal geometry compared the student mostly against its own nearby-frame predictions. After the source-frame branch was made a stop-gradient teacher, the loss became practical, but it still had no independent structure anchor. A wrong but temporally smooth depth field can satisfy this signal.

The measured geometry disagreement was also very small: logged mean log-depth error was about `0.006` to `0.009`, and the weighted geometry contribution was tiny beside the photometric loss. Projection coverage was high, usually about `98%`, so the default visibility setting did not isolate the hard leaf/branch occlusion zones where the method was supposed to matter.

The strict visibility probe confirmed the other side of the problem: when the mask was forced to become selective, it became too sparse or too harsh and hurt `a1` badly. So Snapshot 04 did not find the useful middle ground between "supervise almost everything" and "throw away too much."

## 2. Why Feature Consistency Improved Abs Rel But Hurt A1

Feature consistency likely acted as a broad stabilizer. It improved median-scaled `abs_rel` (`0.5581` vs control `0.5634`) because low-resolution encoder features are smoother and less pixel-noisy than raw RGB matching.

But the same smoothness is a bad fit for the `a1` threshold. In dense vegetation, many errors are boundary and ordering errors around thin leaves, branches, and overlapping plant layers. Low-resolution feature alignment can reduce average relative error while blurring or weakening those local separations, pushing more pixels outside the `1.25x` threshold. That matches the observed drop in median-scaled `a1` (`0.3373` vs control `0.3577`).

## 3. Are The Maps Meaningful Or Mostly Noisy?

They are technically meaningful and nonblank, but not yet strong enough to trust as the main supervision.

- Geometry error maps have real variation, but the raw logged disagreement is tiny. They show projection/model mismatch, not a strong correction signal for vegetation depth.
- Visibility maps are mostly projection-valid masks. The saved samples are around `95%` valid, and the logs are around `98%`; default visibility is therefore mostly a no-op rather than a true occlusion model.
- Texture ambiguity maps are the most meaningful reusable maps. They are active, full-range in the saved PNGs, and mark roughly `29%` to `35%` high-ambiguity pixels depending on the diagnostic batch.
- Feature error maps are active and covered, with about `97%` feature mask coverage in the training log, but the signal is too coarse to protect thin vegetation structure by itself.

## 4. What Is Worth Reusing

Reuse the diagnostic infrastructure, projection-valid accounting, map rendering, and the texture-ambiguity estimate as an analysis or weak reliability prior.

Do not reuse Snapshot 04's temporal geometry, default visibility, or feature-consistency losses as the next main method without a redesign. The ablations show they are stable and self-supervised, but they do not create a useful enough training signal.

## 5. What Should Replace Snapshot 04

Snapshot 05 should move away from cross-view self-consistency and target the failure mode that has appeared repeatedly: Citrus adaptation damages relative depth structure even when training losses look stable.

Proposed Snapshot 05:

```text
05_teacher_anchored_relative_structure_regularization
```

Working method name:

```text
Teacher-Anchored Relative-Structure Regularization for Label-Free Self-Supervised Vegetation Adaptation
```

Core idea: keep the normal self-supervised photometric training, but add a training-only frozen RGB teacher that anchors relative depth structure. The teacher is not a Citrus depth label route; it produces pseudo-structure from RGB only. The student still uses one RGB image at inference.

The teacher signal should not be raw metric depth regression. It should be scale-invariant structure:

- robust normalized inverse-depth or log-depth agreement
- local gradient/edge agreement on predicted disparity structure
- sparse pairwise ordinal/ranking consistency between sampled pixels
- teacher confidence from augmentation stability or teacher-student agreement
- optional mild texture-ambiguity emphasis only as a support prior, not as the main method

Why this is clearly different from Snapshot 04:

- no source-frame predicted-depth consistency as the main signal
- no feature warping as the main signal
- no attempt to fix repeated vegetation texture by only changing cross-view masks
- directly addresses relative-depth drift and over-smoothing, the repeated failure pattern from Milestone 3 and Snapshot 04

The implemented Snapshot 05 followed the same core idea but, by later user instruction, proceeded to a full 30-epoch run after minimal compile/help/CUDA-smoke checks rather than stopping at a 250-step gate.
