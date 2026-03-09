# System Architecture

High-level system design and technical infrastructure documentation.

## Architecture Overview

**affective_playlists** is a unified Python CLI application combining three feature domains:

```
affective_playlists (CLI entrypoint)
  ├── 4tempers (temperament analysis)
  ├── metad_enr (metadata enrichment)
  └── plsort (playlist organization)
```

Each domain operates independently but can share enriched metadata from the metadata enrichment pipeline.

## Core Components

### CLI Interface
- [src/cli_ui.py](../../src/cli_ui.py) - Interactive command-line interface
- [src/config.py](../../src/config.py) - Configuration management
- [main.py](../../main.py) - Application entrypoint

### Data Models
- [src/models.py](../../src/models.py) - Core domain models
- [src/track_metadata.py](../../src/track_metadata.py) - Track metadata representation

### Domain Orchestration
- [src/temperament_analyzer.py](../../src/temperament_analyzer.py) - Temperament analysis orchestrator
- [src/metadata_enrichment.py](../../src/metadata_enrichment.py) - Metadata enrichment orchestrator
- [src/playlist_classifier.py](../../src/playlist_classifier.py) - Playlist classification logic

### External API Integration
- [src/llm_client.py](../../src/llm_client.py) - OpenAI API client for temperament analysis
- [src/metadata_queries.py](../../src/metadata_queries.py) - MusicBrainz, Spotify, Last.fm integration
- [src/apple_music.py](../../src/apple_music.py) - Apple Music library access via AppleScript

### Utilities
- [src/logger.py](../../src/logger.py) - Structured logging
- [src/normalizer.py](../../src/normalizer.py) - Data normalization
- [src/playlist_utils.py](../../src/playlist_utils.py) - Playlist helpers
- [src/result_utils.py](../../src/result_utils.py) - Result formatting
- [src/cover_art.py](../../src/cover_art.py) - Cover art handling

## Platform Constraints

### macOS-Only Features
- **Music.app Integration**: Via AppleScript
  - Temperament analysis (requires playlist access)
  - Playlist organization (playlist move operations)

### Cross-Platform Features
- **Metadata Enrichment**: Supported on macOS, Linux, Windows
  - External API queries (MusicBrainz, Spotify, Last.fm)
  - File system operations

### Platform Guards

The system implements platform-specific validation:
1. **Temperament analysis**: Exits with guidance if not on macOS
2. **Playlist organization (move)**: Exits if not on macOS
3. **Metadata enrichment**: Works on all platforms
4. **Folder-based workflows**: Alternative to Music.app on non-macOS

## Configuration

- **Environment variables**: API keys (OPENAI_API_KEY, SPOTIFY_API_ID, etc.)
- **Configuration files**: 
  - `data/config/genre_map.json` - Genre classification rules
  - `data/config/weights.json` - Source priority for metadata enrichment
  - `data/config/playlist_folders.json` - Playlist organization targets

## Data Flow

### Metadata Enrichment Pipeline
```
User Input (playlist/folder selection)
  ↓
Track Collection (from source)
  ↓
Field Detection (identify missing fields)
  ↓
Multi-Source Query (MusicBrainz → Spotify → Last.fm → fallback)
  ↓
Provenance Tracking (record source for each field)
  ↓
Safe Write-back (per-track error isolation)
  ↓
Summary Report (with source details)
```

### Temperament Analysis Pipeline
```
User Input (playlist selection)
  ↓
Music.app Authentication
  ↓
Track Collection (from playlist)
  ↓
Metadata Enrichment (optional, for context)
  ↓
LLM Classification (OpenAI GPT)
  ↓
Result Reporting (Woe/Frolic/Dread/Malice)
```

### Playlist Organization Pipeline
```
User Input (playlist selection)
  ↓
Genre Classification (via metadata analysis)
  ↓
Folder Mapping (match genre to configured folder)
  ↓
Dry-run Preview (show intended moves)
  ↓
User Confirmation
  ↓
Execute Moves (on macOS only)
  ↓
Summary Report
```

## Testing Strategy

- **Unit tests**: [tests/](../../tests/) directory
- **Integration tests**: End-to-end workflow validation
- **Platform guards**: macOS/non-macOS behavior validation

Run tests with: `pytest tests/ -v`

## Quality Standards

All code must pass:
- Type checking: `mypy src/`
- Linting: `pylint src/`
- Code formatting: `black --check src/ tests/`
- Import sorting: `isort --check-only src/ tests/`

See [docs/rules/CODE_QUALITY_STANDARDS.md](../rules/CODE_QUALITY_STANDARDS.md) for details.

## Legacy Reference

For historical context:
- [docs/legacy-specs/TECH_REQ_SYSTEM_ARCHITECTURE.md](../legacy-specs/TECH_REQ_SYSTEM_ARCHITECTURE.md)
