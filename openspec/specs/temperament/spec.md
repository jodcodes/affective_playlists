# Temperament Specifications

## Overview
Temperament analysis SHALL classify playlists into one of four temperaments using LLM-based interpretation of track/playlist metadata.

### Requirement: Four-Category Classification
The system MUST classify each analyzed playlist into exactly one category: Woe, Frolic, Dread, or Malice.

#### Scenario: Successful classification
- GIVEN a valid playlist with accessible tracks
- WHEN analysis completes without API error
- THEN the system SHALL return exactly one temperament label

#### Scenario: Missing API credentials
- GIVEN no valid LLM API key is configured
- WHEN temperament analysis starts
- THEN the system MUST fail fast with a user-facing configuration error

### Requirement: Music.app Access
The system MUST authenticate against Music.app before attempting playlist analysis.

#### Scenario: Authentication failure
- GIVEN Music.app is unavailable or inaccessible
- WHEN analysis starts
- THEN the system SHALL stop and return an authentication error

#### Scenario: Non-macOS execution
- GIVEN the command runs on a non-macOS platform (Linux, Windows)
- WHEN the user selects temperament analysis or playlist organization
- THEN the CLI MUST reject execution with platform-specific message
- AND the system SHALL suggest workarounds (e.g., folder enrichment for non-macOS)
- AND exit code SHALL be 1

#### Scenario: Missing API credentials (early validation)
- GIVEN OPENAI_API_KEY is not set in environment
- WHEN temperament analysis starts
- THEN the system MUST detect missing key BEFORE client initialization
- AND SHALL print setup link to https://platform.openai.com/api-keys
- AND SHALL log configuration error to structured logger
- AND exit code SHALL be 1

### Requirement: Resilient Processing
The system MUST handle per-playlist or per-request failures with clear logging.

#### Scenario: API timeout during analysis
- GIVEN the LLM request times out
- WHEN retry policy is exhausted
- THEN the system SHALL log the failure context and return a non-zero exit code
