"""
Shared modules for plMetaTemp subprojects.

This package provides common utilities used across:
- 4tempers: AI-based playlist temperament analysis
- metad_enr: Metadata filling and enrichment
- plsort: Playlist organization and classification
"""

from .apple_music import AppleMusicInterface
from .normalizer import TextNormalizer
from .logger import setup_logger
from .config import load_centralized_whitelist, filter_playlists_by_whitelist, get_filtered_playlists

__all__ = [
    'AppleMusicInterface',
    'TextNormalizer',
    'setup_logger',
    'load_centralized_whitelist',
    'filter_playlists_by_whitelist',
    'get_filtered_playlists',
]
