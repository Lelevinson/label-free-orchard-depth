# Snapshot 05 weights_19 Professor Visual Diagnosis Summary

Generated package:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/
```

Main report:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/levinson/snapshots/05_teacher_anchored_relative_structure_regularization/local_evidence/selected_weights19_professor_visual_diagnostics/visual_diagnosis.md
```

No new training was run. The package uses the validation-selected Snapshot 05 `weights_19` checkpoint and existing per-sample metric CSVs.

Contents:

```text
full_image_qualitative/
valid_mask_evaluation/
cropped_masked_evaluation/
weights29_vs_weights19/
plain_inference/
sample_selection.csv
sample_selection.json
visual_diagnosis.md
```

Summary:

- `weights_19` remains the best current Levinson label-free teacher-anchor checkpoint numerically.
- Full-image visuals are mixed: sky/far-canopy boundaries, dark plant blobs, and over-smoothed vegetation remain visible.
- Valid-mask panels show where the measured LiDAR evaluation region supports the numeric gains.
- The sky issue should not be hidden: blue-sky pixels are mostly outside the LiDAR mask, but upper-image canopy/far vegetation is partially evaluated.
- The package is professor-discussion-ready, not a polished paper qualitative win.

Suggested use:

- Show a good case with both the full-image panel and matching valid-mask panel.
- Show at least one failure/largest-drop case to be honest about full-image artifacts.
- Use this as diagnostic evidence for the current best checkpoint, not as a claim that Snapshot 05 visually solves vegetation depth.
