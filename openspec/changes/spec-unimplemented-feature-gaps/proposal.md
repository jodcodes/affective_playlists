## Why
Several features are documented or implied by the code structure but are not fully implemented yet. Two high-impact gaps are currently explicit in source code: Apple Music folder structure parsing and non-MusicBrainz cover art providers.

## What Changes
- Define normative requirements for Apple Music playlist folder structure parsing.
- Define normative requirements for Spotify, Last.fm, and Discogs cover art download paths.
- Define observability and fallback requirements so unsupported or misconfigured providers fail explicitly and safely.
- Define test expectations for these currently incomplete paths.

## Capabilities

### New Capabilities
- `apple-music-folder-structure-parser`: Parse AppleScript output into a stable hierarchical folder-to-playlist mapping.
- `cover-art-provider-downloads`: Implement authenticated cover art retrieval for Spotify, Last.fm, and Discogs with fallback handling.
- `incomplete-feature-observability`: Standardize logs, status signaling, and test coverage for previously stubbed paths.

### Modified Capabilities
- None.

## Impact
- Affected modules: `src/apple_music.py`, `src/cover_art.py`, and related tests.
- External dependencies/config: Spotify credentials, Last.fm API key, Discogs token.
- Improves behavior consistency for metadata enrichment workflows that depend on cover art and folder organization metadata.
