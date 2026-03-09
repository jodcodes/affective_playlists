# Proposal: Add Platform Guards and API Validation to CLI

## Intent
Improve robustness and user experience of the CLI by:
1. Preventing macOS-specific features (Temperament, Playlist Organization) from running on non-macOS platforms
2. Validating OpenAI API key before attempting client initialization
3. Providing clear, actionable error messages when preconditions are not met

## Problem Statement
Users on non-macOS platforms (Linux, Windows) receive cryptic errors when attempting to use macOS-only features. Similarly, missing API credentials cause failures deep in the initialization chain rather than during early validation.

## Scope

### Included
- Platform guards for temperament analysis and playlist organization
- API key validation with setup guidance
- Unit & integration tests for guards and validation
- Improved logging with structured error context

### Excluded
- CLI redesign or argument parsing changes
- New features or functionality changes
- Refactoring of non-CLI code

## Impact
- User experience: Better error messages, fewer confusing failures
- Reliability: Early exit prevents wasted work on misconfigured environments
- Testing: Comprehensive coverage of platform and environment edge cases
- Observability: Structured logging aids debugging

## Dependencies
- No external package changes
- Builds on existing error/info/warning formatting (cli_ui.py)
- Follows CODE_QUALITY_STANDARDS.md (logging rules)
