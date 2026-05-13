# Research Artifacts

This folder stores research notes, experiment summaries, paper-candidate indexes, and beginner-friendly support notes.

Use this folder for material that may later support the paper:

- dataset-construction evidence
- calibration/label-quality decisions
- baseline model runs
- quantitative summaries
- paper table/figure candidates
- beginner-friendly reference notes that help the team explain the work consistently

Do not store large generated outputs here directly. Put generated images, NumPy files, and other bulky local artifacts under `citrus_project/research/generated/`, which is ignored by git.

## Read Map

Do not read every research note by default. Use this map to pick the smallest relevant file:

- current project status and decisions: repo-root `AGENTS.md`
- dataset-building, label route, calibration, or split evidence: `dataset_notes.md`
- model behavior, baseline metrics, adaptation evidence, or Milestone 4 baseline details: `baseline_notes.md`
- paper-candidate results and likely table/figure material: `paper_shortlist.md`
- advisor questions, recommendations, and follow-up interpretations: `advisor_notes.md`
- beginner explanations and stable definitions: `student_qna.md`
- literature scouting and improvement ideas: `literature_tracker.md`
- scene categories, hard examples, and qualitative support: `scene_taxonomy.md`

Open a deeper note only when its role matches the task. `paper_shortlist.md` is an index of paper-useful evidence, not the full archive.

## Tracked Notes

Current tracked notes include:

- `student_qna.md` for recurring plain-language questions and answers
- `dataset_notes.md` for dataset-building and label-quality evidence
- `baseline_notes.md` for baseline-run notes
- `paper_shortlist.md` for likely paper material
- `literature_tracker.md` for related-work intake and improvement ideas
- `scene_taxonomy.md` for scene categories and example selection
- `advisor_notes.md` for professor/advisor questions and recommendations

Quick structure:

- `paper_shortlist.md` = shortlist of results that may later appear in the paper
- `dataset_notes.md` = dataset-building and label-quality evidence
- `baseline_notes.md` = baseline/model experiment notes
- `literature_tracker.md` = model-improvement and related-work tracker
- `scene_taxonomy.md` = scene categories and qualitative-support tracker
- `advisor_notes.md` = professor/advisor questions, recommendations, and follow-up ideas
- `student_qna.md` = simple recurring explanations for students
- `generated/` = ignored local outputs only

