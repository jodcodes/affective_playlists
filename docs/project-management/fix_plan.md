# Fix Plan

## Priority 1 (Critical)
- [ ] [spec-seed-metadata] Seed metadata domain into `openspec/specs/metadata/spec.md`
- [ ] [spec-seed-temperament] Seed temperament domain into `openspec/specs/temperament/spec.md`
- [ ] [spec-seed-playlists] Seed playlist organization domain into `openspec/specs/playlists/spec.md`
- [ ] [ci-quality-gates] Enforce tests, type-check, lint, and formatting in CI

## Priority 2 (High)
- [ ] [packaging-hardening] Reduce runtime import-path hacks and improve package execution model
- [ ] [platform-guarding] Keep macOS-only flows explicitly guarded with clear user guidance
- [ ] [docs-drift] Keep docs and repository links aligned with current owner and workflows

## Priority 3 (Medium)
- [ ] [spec-seed-apple-music] Seed Apple Music integration behavior spec
- [ ] [spec-seed-llm-client] Seed LLM client behavior spec
- [ ] [coverage-growth] Raise coverage around enrichment edge-cases and fallback paths

## Completed
- [x] [brownfield-bootstrap] Create OpenSpec baseline files and migration scaffold
- [x] [test-platform-guards] Add platform guards and API validation tests
  → Implementation: main.py, tests/test_main_platform_guards.py, tests/test_main_cli_platform.py
  → Specs: Merged into openspec/specs/temperament/spec.md and openspec/specs/playlists/spec.md
  → Results: 12 new tests, all 169 tests passing
  → Status: ARCHIVED in openspec/changes/test-platform-guards/
