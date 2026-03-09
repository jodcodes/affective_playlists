# Metadata Enrichment Domain Guide

Automatic filling of missing music metadata using multiple sources with deterministic fallback behavior.

## Overview

Metadata enrichment enables users to automatically populate missing track information (BPM, genre, release year) by querying multiple external databases in priority order. The system is designed for safe, reliable operation with robust error handling and source provenance tracking.

### Core Features

- **Field-aware querying**: Skip sources for fields that are already populated
- **Multi-source fallback**: Configured source priority with exhaustive search capabilities
- **Source provenance**: Track which source provided each enriched field
- **Safe write-back**: Per-track error isolation during batch operations
- **Apple Music compatibility**: Skip cover-art embedding for tracks from Apple Music

## Authoritative Specification

Complete specification: [openspec/specs/metadata/spec.md](../../../openspec/specs/metadata/spec.md)

### Key Scenarios

**Field-aware query strategy**  
When a track has existing genre but missing BPM and year, the system skips genre lookup and searches only for BPM and year.

**Exhaustive fallback for missing fields**  
If enrichment encounters partial source failures, the system continues through configured sources until all missing fields are found or all sources are exhausted.

**First-source wins per field**  
When multiple sources return values for the same field, only the first source in priority order is applied; later sources for that field are skipped.

**Per-track failure isolation**  
If one track fails during write-back, the system logs the failure and continues processing remaining tracks without interruption.

## Implementation

Source files related to metadata enrichment:

- [src/metadata_enrichment.py](../../../src/metadata_enrichment.py) - Core enrichment orchestration
- [src/metadata_fill.py](../../../src/metadata_fill.py) - Field population logic
- [src/metadata_queries.py](../../../src/metadata_queries.py) - Multi-source query handling
- [src/llm_client.py](../../../src/llm_client.py) - LLM-based enrichment fallback
- [tests/test_metadata_enrichment.py](../../../tests/test_metadata_enrichment.py) - Test suite

## Configuration

Metadata enrichment is configured via:

- `data/config/weights.json` - Source priority and field weights
- Environment variables for API credentials (Spotify, MusicBrainz, Last.fm, etc.)

## Related Domains

- [Playlist Organization](../playlists/) - Uses enriched metadata for genre classification
- [Temperament Analysis](../temperament/) - Uses enriched metadata for mood classification

## Legacy Reference

For historical context and requirements traceability:
- [docs/legacy-specs/SPEC_METADATA_ENRICHMENT.md](../../legacy-specs/SPEC_METADATA_ENRICHMENT.md)
