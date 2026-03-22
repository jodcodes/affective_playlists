## 1. Apple Music folder parser

- [x] 1.1 Add parsing fixtures for representative AppleScript folder outputs
- [x] 1.2 Implement folder structure parsing in `get_playlist_folder_structure`
- [x] 1.3 Add tests for valid, empty, and malformed folder output handling

## 2. Cover art provider implementations

- [x] 2.1 Implement Spotify cover art retrieval with credential validation and logging
- [x] 2.2 Implement Last.fm cover art retrieval with API key validation and logging
- [x] 2.3 Implement Discogs cover art retrieval with token validation and logging
- [x] 2.4 Extend `download()` fallback orchestration to use configured providers safely

## 3. Observability and hardening

- [x] 3.1 Add structured skip/failure log messages for unsupported or misconfigured providers
- [x] 3.2 Add tests that assert graceful fallback behavior when one provider fails
- [x] 3.3 Update user-facing docs for required credentials and current provider status
