"""plsort - Playlist Organization and Classification module."""

__version__ = "1.0.0"
__author__ = "affective_playlists"

from .plsort import categorize_playlists, classify_playlist, load_genre_data

__all__ = [
    'categorize_playlists',
    'classify_playlist',
    'load_genre_data',
]
