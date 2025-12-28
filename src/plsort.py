#!/usr/bin/env python3
"""
plsort - Playlist Organization and Classification

Categorizes playlists by genre (world, electronic, jazz, disco/funk/soul, rock, hip-hop)
using artist lists and metadata enrichment.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))

from shared.logger import setup_logger

logger = setup_logger(__name__)


def load_genre_data() -> Dict[str, List[str]]:
    """Load genre-based artist lists from centralized data folder."""
    genres = {}
    # All data is now centralized in data/ folder
    data_root = PROJECT_ROOT.parent if PROJECT_ROOT.name == 'src' else PROJECT_ROOT
    artist_lists_dir = data_root / "data" / "artist_lists"
    
    genre_files = {
        "world": "world.json",
        "electronic": "electronic.json",
        "jazz": "jazz.json",
        "disco_funk_soul": "disco_funk_soul.json",
        "rock": "rock.json",
        "hiphop": "hiphop.json",
    }
    
    for genre_name, filename in genre_files.items():
        filepath = artist_lists_dir / filename
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    genres[genre_name] = {
                        "artists": data.get("artists", []),
                        "keywords": data.get("keywords", []),
                        "description": data.get("description", "")
                    }
        except Exception as e:
            logger.warning(f"Failed to load genre data for {genre_name}: {e}")
    
    return genres


def classify_playlist(playlist_name: str, track_artists: List[str], genres: Dict) -> Optional[str]:
    """
    Classify a playlist into one of the defined genres.
    
    Args:
        playlist_name: Name of the playlist
        track_artists: List of artist names in the playlist
        genres: Genre classification data
    
    Returns:
        Assigned genre name or None
    """
    if not track_artists:
        return None
    
    genre_scores = {genre: 0 for genre in genres.keys()}
    
    # Score each track against each genre
    for artist in track_artists:
        artist_lower = artist.lower()
        
        for genre_name, genre_data in genres.items():
            # Check if artist is in genre's artist list
            if any(a.lower() == artist_lower for a in genre_data.get("artists", [])):
                genre_scores[genre_name] += 2
            
            # Check if artist matches any keyword
            if any(kw in artist_lower for kw in genre_data.get("keywords", [])):
                genre_scores[genre_name] += 1
    
    # Return the genre with highest score
    if max(genre_scores.values()) > 0:
        return max(genre_scores, key=genre_scores.get)
    
    return None


def categorize_playlists(dry_run: bool = True, verbose: bool = False) -> int:
    """
    Main function to categorize playlists.
    
    Args:
        dry_run: If True, only show what would be done
        verbose: Enable verbose logging
    
    Returns:
        Exit code
    """
    logger.info("Loading genre classification data...")
    genres = load_genre_data()
    
    if not genres:
        logger.error("No genre data loaded")
        return 1
    
    logger.info(f"Loaded {len(genres)} genre categories:")
    for genre in genres.keys():
        logger.info(f"  - {genre}")
    
    logger.info("\nPlaylist categorization ready.")
    logger.info(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    
    if verbose:
        logger.debug(f"Genres loaded: {list(genres.keys())}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="plsort - Playlist Organization and Classification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry-run mode: show what would be done without modifying (default)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually move playlists in Apple Music (requires confirmation)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--playlist',
        type=str,
        help='Process single playlist by name'
    )
    
    parser.add_argument(
        '--enrich',
        type=str,
        nargs='+',
        choices=['musicbrainz', 'lastfm', 'discogs', 'rym'],
        help='Enrich data from web sources'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '--config-dir',
        type=str,
        default=str(PROJECT_ROOT / 'config'),
        help='Configuration directory (default: config)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel('DEBUG')
    
    # Determine mode
    dry_run = not args.execute
    
    return categorize_playlists(dry_run=dry_run, verbose=args.verbose)


if __name__ == '__main__':
    sys.exit(main())
