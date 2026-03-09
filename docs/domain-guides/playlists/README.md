# Playlist Organization Domain Guide

Genre-based classification and organization of playlists with explicit confirmation safeguards.

## Overview

Playlist organization enables users to classify playlists by genre and optionally move them into configured folder structures. The system provides a safe workflow with dry-run preview, explicit confirmation steps, and platform-specific constraints.

### Core Features

- **Genre classification**: Classify playlists using available track metadata and configured genre logic
- **Safe organization**: Explicit user confirmation before executing playlist moves
- **Dry-run mode**: Preview intended moves without modifying playlists
- **Unclassified handling**: Playlists that cannot be reliably classified are flagged and not moved
- **Platform constraints**: Move operations require macOS; metadata enrichment works on all platforms

## Authoritative Specification

Complete specification: [openspec/specs/playlists/spec.md](../../../openspec/specs/playlists/spec.md)

### Key Scenarios

**Playlist classified with confidence**  
A playlist with sufficient track metadata receives a genre assignment with classification details.

**Unclassified playlist handling**  
When a playlist cannot be reliably classified, the system marks it as unclassified and avoids automatic movement.

**User declines confirmation**  
If the user declines confirmation before execution, the system cancels without changing playlist locations.

**Dry-run behavior**  
In dry-run mode, the system reports intended moves without performing them, enabling safe preview.

**Non-macOS organization attempt**  
On non-macOS platforms, the system exits with a platform-error message and provides guidance to alternatives.

**Folder-based enrichment on non-macOS**  
Metadata enrichment in folder mode is allowed on non-macOS without platform guards.

## Implementation

Source files related to playlist organization:

- [src/playlist_classifier.py](../../../src/playlist_classifier.py) - Genre classification logic
- [src/playlist_manager.py](../../../src/playlist_manager.py) - Playlist move orchestration
- [src/playlist_utils.py](../../../src/playlist_utils.py) - Playlist utilities
- [tests/test_playlist_classifier.py](../../../tests/test_playlist_classifier.py) - Test suite

## Configuration

Playlist organization is configured via:

- `data/config/playlist_folders.json` - Target folder mappings by genre
- `data/config/genre_map.json` - Genre classification rules

## Deployment Constraints

- **macOS required**: Playlist move operations require macOS and Music.app access via AppleScript
- **Non-macOS**: Metadata enrichment can still run in folder mode without modification
- **Apple Music**: The system integrates with Apple Music library on macOS

## Related Domains

- [Metadata Enrichment](../metadata/) - Provides enriched metadata for classification
- [Temperament Analysis](../temperament/) - Alternative classification approach based on mood

## Legacy Reference

For historical context and requirements traceability:
- [docs/legacy-specs/SPEC_PLAYLIST_ORGANIZATION.md](../../legacy-specs/SPEC_PLAYLIST_ORGANIZATION.md)
