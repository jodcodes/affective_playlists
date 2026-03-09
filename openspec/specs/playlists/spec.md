# Playlists Specifications

## Overview
Playlist organization SHALL classify playlists by genre and optionally move them into configured folders with explicit confirmation safeguards.

### Requirement: Genre Classification
The system MUST classify each selected playlist using available track metadata and configured genre logic.

#### Scenario: Playlist classified with confidence
- GIVEN a playlist with sufficient track metadata
- WHEN classification runs
- THEN the system SHALL produce a genre assignment with details

#### Scenario: Unclassified playlist handling
- GIVEN a playlist cannot be classified reliably
- WHEN organization summary is produced
- THEN the system MUST mark it as unclassified and avoid moving it automatically

### Requirement: Safe Organization Actions
The system MUST require explicit user confirmation before executing real playlist move operations.

#### Scenario: User declines confirmation
- GIVEN organization is about to run in execute mode
- WHEN the user declines confirmation
- THEN the system SHALL cancel without changing playlist locations

#### Scenario: Dry-run behavior
- GIVEN dry-run mode is active
- WHEN organization is executed
- THEN the system MUST report intended moves without performing them

### Requirement: Platform Constraints
Apple Music move operations MUST only run on macOS.

#### Scenario: Non-macOS organization attempt
- GIVEN the command runs on non-macOS
- WHEN the user starts playlist organization
- THEN the CLI MUST stop with platform-error message and guide to alternatives
- AND exit code SHALL be 1

#### Scenario: Folder-based enrichment on non-macOS (allowed)
- GIVEN the user selects metadata enrichment in Folder mode on non-macOS
- WHEN enrichment runs
- THEN the system SHALL NOT apply platform guard (macOS not required for folders)
- AND processing SHALL continue normally
