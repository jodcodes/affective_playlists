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
from tqdm import tqdm

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))

from logger import setup_logger

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


def categorize_playlists(dry_run: bool = True, verbose: bool = False, interactive: bool = True, playlist_names: List[str] = None) -> int:
    """
    Main function to categorize playlists.
    
    Args:
        dry_run: If True, only show what would be done
        verbose: Enable verbose logging
        interactive: If True, ask user which playlists to process
        playlist_names: Pre-selected playlist names (if provided, skips interactive selection)
    
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
    
    # If playlists already selected, use them
    if playlist_names:
        logger.info(f"Processing {len(playlist_names)} pre-selected playlists")
        print(f"\nProcessing {len(playlist_names)} playlists:")
        for name in playlist_names:
            print(f"  - {name}")
        
        # Categorize the playlists
        categorization_results = {}
        print("\nClassifying playlists by genre...")
        
        for playlist_name in tqdm(playlist_names, desc="Classifying playlists", unit="playlist"):
            # For now, just show the playlist name
            # In the future, this would access the actual playlist data
            genre = "unknown"
            categorization_results[playlist_name] = genre
            logger.debug(f"Classified {playlist_name} as {genre}")
        
        # Display results
        print("\n" + "="*70)
        print("CLASSIFICATION RESULTS")
        print("="*70 + "\n")
        
        for playlist_name, genre in categorization_results.items():
            if dry_run:
                status = "→ (DRY-RUN)"
            else:
                status = "→ (organizing)"
            print(f"  {playlist_name:40s} {status} {genre}")
        
        # If not dry-run, move playlists using AppleScript
        if not dry_run:
            print("\n" + "-"*70)
            print("Moving playlists to genre folders...\n")
            
            try:
                from temperament_analyzer import MusicAppClient
                music_client = MusicAppClient()
                
                if not music_client.authenticate():
                    print("ERROR: Could not connect to Music.app")
                    return 1
                
                # Get playlist IDs for moving
                playlist_ids = music_client._get_playlist_ids()
                
                # Create genre folders and move playlists
                genre_folders = {}  # Cache for created folders
                
                for playlist_name, genre in tqdm(categorization_results.items(), desc="Organizing", unit="playlist"):
                    try:
                        # Create folder if not already created
                        if genre not in genre_folders:
                            folder_id = music_client.create_folder(genre)
                            if folder_id:
                                genre_folders[genre] = folder_id
                            else:
                                logger.warning(f"Failed to create folder for genre: {genre}")
                                continue
                        
                        # Move playlist to folder
                        if playlist_name in playlist_ids:
                            playlist_id = playlist_ids[playlist_name]
                            folder_id = genre_folders[genre]
                            
                            success = music_client.move_playlist_to_folder(playlist_id, folder_id)
                            if success:
                                logger.info(f"Moved '{playlist_name}' to folder '{genre}'")
                            else:
                                logger.error(f"Failed to move '{playlist_name}' to folder '{genre}'")
                        else:
                            logger.warning(f"Playlist '{playlist_name}' not found in Music.app")
                    except Exception as e:
                        logger.error(f"Failed to move '{playlist_name}': {e}")
                
                print("\n✓ Playlist organization complete!")
            except Exception as e:
                logger.error(f"Failed to organize playlists: {e}")
                print(f"ERROR: {e}")
                return 1
        
        print()
        return 0
    
    selected_playlists = None
    
    if interactive:
        # Ask user which playlists to process
        print("\n" + "="*60)
        print("PLAYLIST SELECTION")
        print("="*60)
        print("\nOptions:")
        print("  1. All whitelisted playlists")
        print("  2. Select specific playlists from whitelist")
        print("  0. Cancel")
        print("-"*60)
        
        while True:
            choice = input("\nYour choice (0-2): ").strip()
            
            if choice == "0":
                print("Cancelled.\n")
                return 0
            elif choice == "1":
                logger.info("Processing: ALL whitelisted playlists")
                # Just process, don't load again
                print("\nProcessing all whitelisted playlists...")
                return 0
            elif choice == "2":
                # Select specific playlists
                try:
                    from temperament_analyzer import MusicAppClient
                    
                    print("\nConnecting to Music.app...")
                    music_client = MusicAppClient()
                    
                    if not music_client.authenticate():
                        print("ERROR: Could not connect to Music.app")
                        return 1
                    
                    # Get playlist IDs (fast - no tracks loaded)
                    print("Fetching playlist list from Music.app...")
                    playlist_ids = music_client._get_playlist_ids()
                    
                    # Filter by whitelist
                    if music_client.whitelist_enabled and music_client.whitelist:
                        playlist_ids = {name: pid for name, pid in playlist_ids.items() if name in music_client.whitelist}
                        logger.info(f"Whitelist enabled: {len(playlist_ids)} whitelisted playlists")
                    
                    if not playlist_ids:
                        print("No playlists found.")
                        return 1
                    
                    # Show playlist selection menu (without loading tracks)
                    print("\n" + "="*60)
                    print("AVAILABLE PLAYLISTS")
                    print("="*60 + "\n")
                    
                    playlist_list = list(playlist_ids.items())
                    for idx, (name, pid) in enumerate(playlist_list, 1):
                        print(f"{idx:2d}. {name}")
                    
                    print("\n" + "-"*60)
                    print("Select playlists to categorize:")
                    print("  Enter numbers separated by commas (e.g., 1,3,5)")
                    print("  Or 'all' to select all playlists")
                    print("  Or 'q' to cancel")
                    print("-"*60)
                    
                    while True:
                        user_input = input("\nYour selection: ").strip().lower()
                        
                        if user_input == 'q':
                            print("Cancelled.\n")
                            return 0
                        
                        if user_input == 'all':
                            selected_playlist_names = [name for name, _ in playlist_list]
                            print(f"\nSelected all {len(selected_playlist_names)} playlists")
                            break
                        
                        try:
                            indices = [int(x.strip()) - 1 for x in user_input.split(',')]
                            if any(idx < 0 or idx >= len(playlist_list) for idx in indices):
                                print(f"Invalid selection. Please enter numbers between 1 and {len(playlist_list)}.")
                                continue
                            
                            selected_playlist_names = [playlist_list[idx][0] for idx in indices]
                            print(f"\nSelected {len(selected_playlist_names)} playlist(s):")
                            for name in selected_playlist_names:
                                print(f"  - {name}")
                            break
                        except ValueError:
                            print(f"Invalid input. Please enter numbers (1-{len(playlist_list)}) separated by commas, 'all', or 'q'.")
                            continue
                    
                    # Now load only the selected playlists with their tracks
                    print("\nLoading selected playlists...")
                    selected_playlists_with_tracks = []
                    
                    for playlist_name in tqdm(selected_playlist_names, desc="Loading playlists", unit="playlist"):
                        try:
                            playlist_id = playlist_ids[playlist_name]
                            playlist = music_client._get_playlist_with_tracks_by_id(playlist_name, playlist_id)
                            if playlist and playlist.tracks:
                                selected_playlists_with_tracks.append(playlist)
                        except Exception as e:
                            logger.warning(f"Failed to load playlist '{playlist_name}': {e}")
                    
                    print(f"\nLoaded {len(selected_playlists_with_tracks)} playlists with tracks")
                    
                    # Return success - playlists are loaded
                    return 0
                except Exception as e:
                    logger.error(f"Failed to load playlists: {e}")
                    print(f"ERROR: {e}")
                    return 1
            else:
                print("Invalid choice. Please enter 0-2.")
    
    if verbose:
        logger.debug(f"Genres loaded: {list(genres.keys())}")
    
    return 0


def main(args=None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="plsort - Playlist Organization and Classification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry-run mode: show what would be done without modifying'
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
    
    parsed_args = parser.parse_args(args)
    
    # Set logging level
    if parsed_args.verbose:
        logger.setLevel('DEBUG')
    
    # Determine mode: default is EXECUTE (dry_run=False), unless --dry-run is specified
    dry_run = parsed_args.dry_run
    
    # Run with interactive mode enabled (pass args=[] to categorize_playlists)
    return categorize_playlists(dry_run=dry_run, verbose=parsed_args.verbose, interactive=True)


if __name__ == '__main__':
    sys.exit(main())
