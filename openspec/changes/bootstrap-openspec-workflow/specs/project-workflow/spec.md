## ADDED Requirements

### Requirement: OpenSpec Artifacts For Project Changes
All non-trivial code changes MUST be tracked in OpenSpec using a dedicated change directory.

#### Scenario: New feature planned
- **WHEN** a contributor starts a new feature or refactor
- **THEN** they create a change directory under `openspec/changes/`
- **AND** they include `proposal.md`, `design.md`, and `tasks.md`
- **AND** they include at least one `specs/<area>/spec.md` requirement delta.

### Requirement: Copilot OpenSpec Workflow Availability
GitHub Copilot OpenSpec prompts and skills MUST be present in repository metadata.

#### Scenario: Repo setup complete
- **WHEN** OpenSpec is initialized for GitHub Copilot
- **THEN** `.github/prompts/` contains `opsx-propose`, `opsx-apply`, `opsx-archive`, and `opsx-explore` prompts
- **AND** `.github/skills/` contains the corresponding OpenSpec skills.
