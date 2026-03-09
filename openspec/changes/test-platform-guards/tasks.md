# Tasks: Platform Guards and API Validation

## Implementation
- [x] Add `require_macos()` guard function to main.py
- [x] Add `validate_openai_api_key()` validation function to main.py
- [x] Integrate guards into `run_temperament_analysis()`
- [x] Integrate guards into `run_metadata_enrichment()` (playlist only)
- [x] Integrate guards into `run_playlist_organization()`
- [x] Replace import-time `print()` with `logger` calls
- [x] Add exception context (`exc_info=True`) to error logging
- [x] Add debug logging for flow tracking

## Testing
- [x] Write unit tests for `require_macos()` on darwin/linux/win32
- [x] Write unit tests for API key validation (present/absent)
- [x] Write integration tests for CLI platform behavior
- [x] Verify folder enrichment is **not** platform-guarded
- [x] Run full test suite (no regressions)

## Verification
- [x] All 169 tests pass (136 existing + 33 new)
- [x] Platform guards return correct exit codes (1 for failure)
- [x] API validation blocks missing keys
- [x] Error messages guide users to solutions

## Documentation
- [x] Update AGENTS.md coding rules (logging standards)
- [x] Specs verify behavior in openspec/specs/temperament#scenario
- [x] Tests document expected platform constraints

## Completion Criteria
✅ All tasks done
✅ 12 new tests: test_main_platform_guards.py, test_main_cli_platform.py
✅ 0 test failures
