# Domain Guides

Domain-specific guides for each major feature area of affective_playlists.

Each domain guide provides:
- Overview and core features
- Link to authoritative OpenSpec specification
- Key scenarios and behaviors
- Implementation file references
- Configuration details
- Related domains and dependencies

## Domains

### [Metadata Enrichment](metadata/) `metad_enr`

Automatic filling of missing track metadata using multiple sources with deterministic fallback.

- **Key feature**: Field-aware querying with source provenance tracking
- **Sources**: MusicBrainz, Spotify, Last.fm, and others
- **Fields**: BPM, genre, release year
- **Cross-platform**: Works on macOS, Linux, Windows

### [Playlist Organization](playlists/) `plsort`

Genre-based classification and organization of playlists with explicit safeguards.

- **Key feature**: Safe organization workflow with dry-run and confirmation
- **Classification**: Uses track metadata to assign genre categories
- **Platforms**: Move operations require macOS; enrichment works cross-platform
- **Target structure**: Configurable folder organization

### [Temperament Analysis](temperament/) `4tempers`

LLM-based classification of playlists into four emotional temperaments.

- **Key feature**: Four-category classification using OpenAI GPT
- **Categories**: Woe (sad), Frolic (happy), Dread (dark), Malice (aggressive)
- **Metadata input**: Uses enriched track data for context
- **Platforms**: Requires macOS for Music.app access

## Architecture

### Integration Flow

```
Metadata Enrichment
  ↓ (enriched metadata)
  ├→ Playlist Organization (genre classification)
  └→ Temperament Analysis (mood classification)
```

### Authoritative Specifications

All behavior specifications are defined in [openspec/specs/](../../openspec/specs/):
- [metadata/spec.md](../../openspec/specs/metadata/spec.md)
- [playlists/spec.md](../../openspec/specs/playlists/spec.md)
- [temperament/spec.md](../../openspec/specs/temperament/spec.md)

## Source of Truth

Domain guides reference and explain the OpenSpec specifications. For the complete, authoritative requirements, always consult the corresponding spec.md file in openspec/specs/.

Legacy specifications from the brownfield migration are available in [docs/legacy-specs/](../legacy-specs/) for reference and traceability.
