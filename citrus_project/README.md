# Citrus Project Workspace

This folder contains the project-owned work for the Citrus Farm + Lite-Mono research effort.

The original Lite-Mono repository code remains at the repo root. Custom project work is grouped here so it is easier to see what belongs to the research fork versus the upstream model code.

## Structure

- `dataset_workspace/` - Citrus dataset download, extraction, audit, densification, and build scripts plus the local dataset workspace
- `research/` - research notes, paper shortlist, beginner Q&A, and ignored generated artifacts
- `milestones/` - milestone-specific folders for future implementation, experiments, notes, and outputs
- `TEAM_WORKFLOW.md` - team onboarding and collaboration rules
- `TASK_BOARD.md` - current owner/status/next-action board

## Read Map

Do not read every Markdown file by default. Start from the smallest doorway document that matches the task:

1. For project status and current decisions, read repo-root `AGENTS.md`.
2. For team handoff or ownership, read `TEAM_WORKFLOW.md` and `TASK_BOARD.md`.
3. For dataset pipeline work, read `dataset_workspace/README.md`, then only the scripts or notes named there.
4. For research evidence, read `research/README.md`, then the one note matching the question.
5. For milestone work, read `milestones/README.md`, then the matching milestone folder README.

Folder READMEs are meant to act as maps. Deeper notes should be opened only when their role matches the current task.

## Working Rule

When possible:

1. keep Citrus-specific pipeline code and data workflow under `dataset_workspace/`
2. keep paper/support notes under `research/`
3. place milestone-specific code, experiment helpers, and notes under the matching folder in `milestones/`

This keeps the custom research work separate from the original Lite-Mono codebase.
