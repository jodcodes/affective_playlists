## Context
The repository has two explicit implementation gaps in runtime code:
1. `AppleMusicClient.get_playlist_folder_structure` currently returns `None` with a TODO marker.
2. `CoverArtDownloader` only implements MusicBrainz downloading, while Spotify/Last.fm/Discogs methods are placeholders that always return `None`.

These gaps are important because project documentation and architecture documents describe multi-source metadata capabilities.

## Goals / Non-Goals

**Goals:**
- Define implementation-ready requirements for the two stubbed feature areas.
- Make fallback behavior deterministic and observable when provider credentials are missing.
- Ensure each new requirement can be verified with automated tests.

**Non-Goals:**
- Changing the existing source priority order in metadata enrichment.
- Redesigning the entire AppleScript integration layer.
- Introducing UI-level behavior changes unrelated to folder parsing or cover-art retrieval.

## Decisions

1. Use a normalized structure for folder parsing output
- Decision: `get_playlist_folder_structure` returns a dictionary keyed by folder name with playlist-name arrays, and never returns partial malformed data.
- Rationale: Callers need deterministic shape for downstream operations and tests.
- Alternative considered: return raw AppleScript string and parse downstream. Rejected due to duplicated parsing and fragile consumers.

2. Keep provider-specific authentication optional but explicit
- Decision: Spotify/Last.fm/Discogs implementations must check required credentials and log structured skip reasons.
- Rationale: optional credentials are a project requirement; silent behavior obscures why data is missing.
- Alternative considered: hard fail when credentials are absent. Rejected because enrichment is designed for best-effort operation.

3. Enforce fallback semantics in downloader orchestration
- Decision: if one provider fails, downloader proceeds to remaining configured providers without raising unhandled exceptions.
- Rationale: current architecture prefers graceful degradation.
- Alternative considered: fail-fast. Rejected because it reduces enrichment coverage.

4. Add explicit test coverage for each previously stubbed path
- Decision: each new capability requires success + failure scenarios in tests.
- Rationale: without tests, regressions can reintroduce placeholder behavior.

## Risks / Trade-offs
- [Provider API variability] -> Mitigation: parse defensively, validate expected fields, and handle schema drift as provider errors.
- [Rate limiting and auth errors] -> Mitigation: distinguish retryable errors from permanent configuration issues in logs and return values.
- [AppleScript output formatting differences] -> Mitigation: build parser against realistic fixtures and include malformed-output tests.
- [Increased test complexity] -> Mitigation: use mocked network and AppleScript outputs.

## Migration Plan
- Add tests first for current gaps (expected failures or xfail markers if needed).
- Implement parser and provider methods incrementally behind existing method signatures.
- Confirm no regressions in current enrichment and cover-art code paths.

## Open Questions
- Should provider failures be surfaced as structured error objects in addition to logging?
- Should partial folder parsing return an empty dict or `None` when output is syntactically valid but empty?
