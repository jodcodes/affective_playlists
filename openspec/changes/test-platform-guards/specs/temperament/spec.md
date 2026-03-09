# Temperament Specifications — Delta Spec: test-platform-guards

## ADDED Scenario: Non-macOS execution
- GIVEN the command runs on a non-macOS platform (Linux, Windows)
- WHEN the user selects temperament analysis or playlist organization
- THEN the CLI MUST reject execution with platform-specific message
- AND the system SHALL suggest workarounds (e.g., folder enrichment for non-macOS)
- AND exit code SHALL be 1

## ADDED Scenario: Missing API credentials (early validation)
- GIVEN OPENAI_API_KEY is not set in environment
- WHEN temperament analysis starts
- THEN the system MUST detect missing key BEFORE client initialization
- AND SHALL print setup link to https://platform.openai.com/api-keys
- AND SHALL log configuration error to structured logger
- AND exit code SHALL be 1

## MODIFIED Scenario: Successful classification (unchanged behavior)
No changes to happy path; all successful paths remain identical.
Platform guard returns True on macOS, validation returns True with valid key.
