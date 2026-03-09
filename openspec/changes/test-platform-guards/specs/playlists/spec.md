# Playlists Specifications — Delta Spec: test-platform-guards

## MODIFIED Scenario: Safe Organization Actions
- GIVEN organization is about to run on non-macOS
- WHEN the user starts playlist organization
- THEN the CLI MUST stop with a platform-error message and guide to alternatives
- AND exit code SHALL be 1

## ADDED Scenario: Folder-based enrichment on non-macOS (allowed)
- GIVEN the user selects metadata enrichment in Folder mode on non-macOS
- WHEN enrichment runs
- THEN the system SHALL NOT apply platform guard (macOS not required for folders)
- AND processing SHALL continue normally
