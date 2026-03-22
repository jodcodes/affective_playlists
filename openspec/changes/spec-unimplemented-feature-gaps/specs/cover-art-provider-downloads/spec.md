## ADDED Requirements

### Requirement: Spotify Cover Art Retrieval
The system MUST support Spotify cover art retrieval when valid Spotify credentials are configured.

#### Scenario: Spotify credentials are present and album art exists
- **WHEN** `download_from_spotify` is called with a valid album identifier and configured credentials
- **THEN** it returns image bytes for cover art
- **AND** caches the downloaded image for subsequent requests.

#### Scenario: Spotify credentials are missing
- **WHEN** Spotify credentials are absent or invalid
- **THEN** `download_from_spotify` returns `None`
- **AND** emits a clear log entry indicating configuration is missing or invalid.

### Requirement: Last.fm Cover Art Retrieval
The system MUST support Last.fm cover art retrieval when a valid Last.fm API key is configured.

#### Scenario: Last.fm query resolves album image
- **WHEN** `download_from_lastfm` is called with artist and album values and a valid API key
- **THEN** it returns image bytes for the best available album image
- **AND** caches the downloaded image.

#### Scenario: Last.fm API key is missing
- **WHEN** no Last.fm API key is configured
- **THEN** `download_from_lastfm` returns `None`
- **AND** logs that Last.fm retrieval was skipped due to missing credentials.

### Requirement: Discogs Cover Art Retrieval
The system MUST support Discogs cover art retrieval when a valid Discogs token is configured.

#### Scenario: Discogs release image is available
- **WHEN** `download_from_discogs` is called with a valid Discogs release identifier and token
- **THEN** it returns image bytes for the release cover
- **AND** caches the downloaded image.

#### Scenario: Discogs token is missing
- **WHEN** Discogs token is not configured
- **THEN** `download_from_discogs` returns `None`
- **AND** logs a skip reason referencing missing Discogs token.

### Requirement: Multi-Provider Cover Art Fallback
The downloader MUST attempt providers in configured priority order and continue when a provider fails.

#### Scenario: First provider fails, second succeeds
- **WHEN** the first attempted provider returns `None` or errors
- **THEN** the downloader continues to the next provider
- **AND** returns image bytes from the first successful provider.

#### Scenario: All providers fail
- **WHEN** every configured provider fails or is unavailable
- **THEN** the downloader returns `None`
- **AND** logs that no provider could return cover art.
