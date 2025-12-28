"""
Metadata Fill/Enrichment - Standalone metadata filling and enrichment tool.

Fills missing metadata fields (BPM, Genre, Year) in audio files by querying
external music databases and integrating with Apple Music playlists.

Main Components:
- metadata_fill: Core filling logic and CLI interface
- metadata_enrichment: Track enrichment orchestration
- metadata_queries: Database query implementations
- audio_tags: Tag reading/writing for multiple formats
- apple_music: Apple Music integration via AppleScript

Features:
- Playlist whitelist filtering for selective processing
- Multi-source database queries with confidence scoring
- Intelligent caching (7-day TTL)
- Support for multiple audio formats (MP3, FLAC, OGG, M4A, WAV, AIFF)
- AppleScript integration for Apple Music
- Zero external dependencies (stdlib-only)
"""

__version__ = "1.0.0"
__author__ = "Joel Debeljak"

from .metadata_fill import MetadataFiller, MetadataFillCLI, create_cli_parser
from .metadata_enrichment import (
    MetadataEnricher, DownloadedTrackDetector, TrackIdentifier,
    MetadataField, DatabaseSource
)
from .metadata_queries import MetadataQueryOrchestrator
from .audio_tags import TagManager

__all__ = [
    'MetadataFiller',
    'MetadataFillCLI',
    'MetadataEnricher',
    'DownloadedTrackDetector',
    'TrackIdentifier',
    'MetadataField',
    'DatabaseSource',
    'MetadataQueryOrchestrator',
    'TagManager',
    'create_cli_parser',
]
