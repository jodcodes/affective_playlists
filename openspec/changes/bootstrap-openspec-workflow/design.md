## Context
`affective_playlists` is a Python-based project with CLI and metadata enrichment workflows. OpenSpec is used to make changes explicit before implementation.

## Design
- Keep OpenSpec artifacts inside `openspec/` at repository root.
- Use one change folder per feature or refactor.
- Require a minimal artifact set for each change:
  - `proposal.md` for motivation and scope
  - `design.md` for technical approach
  - `tasks.md` for implementation checklist
  - `specs/<area>/spec.md` for normative requirements and scenarios

## Notes
- OpenSpec command prompts for GitHub Copilot are installed under `.github/prompts/`.
- OpenSpec skills are installed under `.github/skills/`.
- On macOS case-insensitive filesystems, avoid naming local clones as `OpenSpec` if `openspec/` is needed.
