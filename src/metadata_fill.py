"""
Metadata fill module for playlists (Feature: metad_enr).

LAYER: Application Layer - Feature Implementation
ROLE: Main orchestrator for metadata enrichment
ARCHITECTURE: See src/README.md for full architecture

Core functionality:
- Fills missing metadata fields in playlists
- Queries multiple databases (MusicBrainz → AcousticBrainz → Discogs → Wikidata → Last.fm)
- Works with both internal module usage and CLI invocation
- Integrates with Apple Music library
- Supports both playlist and folder targets

This module can be:
1. Imported and used internally: from metadata_fill import MetadataFiller
2. Invoked from CLI: python -m metadata_fill --playlist "Favorites"

Database Query Order (Priority):
1. MusicBrainz - Primary source (track metadata, BPM, year)
2. AcousticBrainz - Audio analysis (needs MusicBrainz ID)
3. Discogs - Genre, release info (vinyl database)
4. Wikidata - Structured data (artist/track relationships)
5. Last.fm - User-generated tags (least reliable)
"""

import sys
import os
import logging
from typing import List, Optional, Dict
import argparse
from dataclasses import dataclass
from tqdm import tqdm

# Add project root to path for shared imports
_project_root = os.path.join(os.path.dirname(__file__), '..', '..')
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from apple_music import AppleMusicInterface

# Add src to path for local imports
sys.path.insert(0, os.path.dirname(__file__))
from audio_tags import TagManager
from metadata_enrichment import (
    MetadataEnricher, DownloadedTrackDetector, TrackIdentifier, MetadataField
)
from cover_art import CoverArtManager
from metadata_queries import MetadataQueryOrchestrator


@dataclass
class MetadataFillTarget:
    """Target for metadata filling operation."""
    target_type: str  # 'playlist' or 'folder'
    target_name: str
    force_overwrite: bool = False


class MetadataFiller:
    """Core metadata filling logic using persistent IDs."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize MetadataFiller.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        # Point to scripts directory in src/scripts
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        self.apple_music = AppleMusicInterface(scripts_dir)
        self.tag_manager = TagManager()
        self.enricher = MetadataEnricher(logger)
        self.detector = DownloadedTrackDetector()
        self.cover_art_manager = CoverArtManager(logger=logger)
        
        # Load API credentials from environment
        lastfm_key = os.getenv('LASTFM_API_KEY')
        discogs_token = os.getenv('DISCOGS_TOKEN')
        
        # Initialize query orchestrator with credentials
        self.query_orchestrator = MetadataQueryOrchestrator(
            lastfm_api_key=lastfm_key,
            discogs_token=discogs_token,
            logger=logger
        )
        
        self.stats = {
            'processed': 0,
            'enriched': 0,
            'skipped': 0,
            'errors': 0
        }
        # Load shared configs
        self.whitelist_enabled, self.whitelist = self._load_whitelist()
        self.playlist_folders_config = self._load_playlist_folders_config()
        # Cache for playlist IDs
        self._playlist_ids_cache = None
    
    @staticmethod
    def _load_whitelist():
        """Load centralized whitelist configuration"""
        try:
            from config import load_centralized_whitelist
            return load_centralized_whitelist(enabled_by_default=False)
        except ImportError:
            return False, set()
    
    def _load_playlist_folders_config(self) -> dict:
        """Load playlist folders config from data directory"""
        try:
            import json
            config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config', 'playlist_folders.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load playlist folders config: {e}")
            return {}
    
    def _get_playlist_ids(self) -> dict:
        """Get all user playlists with their persistent IDs"""
        if self._playlist_ids_cache is not None:
            return self._playlist_ids_cache
        
        try:
            # self.apple_music.scripts_dir is already pointing to the scripts directory
            script_path = os.path.join(self.apple_music.scripts_dir, 'get_ids_playlists.applescript')
            import subprocess
            result = subprocess.run(['osascript', script_path], capture_output=True, text=True, timeout=30)
            
            if not result.stdout:
                self.logger.error("Failed to get playlist IDs")
                return {}
            
            # Parse output: name:VALUE, id:HEXID
            # The output is all on one line, IDs are always 16 hex digits
            # So we can match name: followed by anything until , id:HEXID
            import re
            playlists = {}
            
            # Pattern: name:ANYTHING, id:16HEXDIGITS
            # Use non-greedy matching with [^}] to stop at the next id:
            pattern = r'name:([^}]+?),\s*id:([A-F0-9]{16})'
            matches = re.findall(pattern, result.stdout)
            
            for name, pid in matches:
                name = name.strip()
                # Remove quotes if present
                if name.startswith("'") and name.endswith("'"):
                    name = name[1:-1]
                elif name.startswith("\"") and name.endswith("\""):
                    name = name[1:-1]
                playlists[name] = pid
            
            self._playlist_ids_cache = playlists
            return playlists
            
        except Exception as e:
            self.logger.error(f"Error getting playlist IDs: {e}")
            return {}

    def fill_playlist(self, playlist_name: str, force: bool = False) -> Dict:
        """
        Fill metadata for all tracks in a playlist using persistent ID.
        
        Args:
            playlist_name: Name of the playlist
            force: Force overwrite existing metadata
            
        Returns:
            Dictionary with results
        """
        # Get playlist ID
        print(f"\nLoading playlist: {playlist_name}...")
        playlist_ids = self._get_playlist_ids()
        playlist_id = playlist_ids.get(playlist_name)
        
        if not playlist_id:
            self.logger.warning(f"Playlist '{playlist_name}' not found")
            return {'success': False, 'error': f'Playlist {playlist_name} not found'}
        
        # Get playlist tracks using ID
        try:
            tracks = self._get_playlist_tracks_by_id(playlist_id)
            if not tracks:
                self.logger.warning(f"Playlist '{playlist_name}' is empty")
                return {'success': False, 'error': 'Playlist is empty'}
        except Exception as e:
            self.logger.error(f"Failed to get playlist tracks: {e}")
            return {'success': False, 'error': str(e)}

        return self._process_tracks(tracks, force)
    
    def _get_playlist_tracks_by_id(self, playlist_id: str) -> Optional[List[Dict]]:
        """Get tracks from a playlist using persistent ID"""
        try:
            script_path = os.path.join(self.apple_music.scripts_dir, 'get_tracks_info_playlists.applescript')
            import subprocess
            result = subprocess.run(['osascript', script_path, playlist_id], capture_output=True, text=True, timeout=60)
            
            if not result.stdout or "ERROR" in result.stdout:
                return None
            
            # Parse AppleScript record format
            # Output is: name:X, id:Y, artist:Z, ... name:X2, id:Y2, artist:Z2, ...
            # All on one or few lines, fields separated by ", "
            import re
            tracks = []
            seen = set()
            
            # Split by "name:" to find track boundaries
            # Each track starts with "name:"
            parts = result.stdout.split('name:')
            
            for i, part in enumerate(parts):
                if not part.strip():
                    continue
                
                # For the first part (before first "name:"), skip it
                if i == 0:
                    continue
                
                # Now we have: "TrackName, id:ID, artist:Artist, ..."
                # Extract all key:value pairs until the next "name:" (which is in the next iteration)
                fields = {}
                
                # Split by ", " to get individual fields
                field_parts = part.split(', ')
                
                # First field is the name (no key: prefix)
                if field_parts:
                    fields['name'] = field_parts[0].strip()
                
                # Parse remaining fields
                for j in range(1, len(field_parts)):
                    field_str = field_parts[j].strip()
                    if ':' in field_str:
                        key, val = field_str.split(':', 1)
                        fields[key.strip()] = val.strip()
                
                # Check if this is a valid track
                track_name = fields.get('name', '')
                artist = fields.get('artist', '')
                
                if track_name and artist:
                    track_key = f"{track_name}_{artist}".lower()
                    if track_key not in seen:
                        seen.add(track_key)
                        tracks.append(fields)
            
            return tracks if tracks else None
            
        except Exception as e:
            self.logger.error(f"Error getting tracks by ID: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fill_folder(self, folder_name: str, force: bool = False) -> Dict:
        """
        Fill metadata for all tracks in a folder.
        
        Args:
            folder_name: Name/path of the folder
            force: Force overwrite existing metadata
            
        Returns:
            Dictionary with results
        """
        print(f"\nLoading folder: {folder_name}...")
        
        # Resolve folder path
        folder_path = self._resolve_folder_path(folder_name)
        if not folder_path or not os.path.isdir(folder_path):
            self.logger.error(f"Folder not found: {folder_name}")
            return {'success': False, 'error': 'Folder not found'}

        # Find all audio files in folder
        audio_files = self._find_audio_files(folder_path)
        if not audio_files:
            self.logger.warning(f"No audio files found in: {folder_path}")
            return {'success': False, 'error': 'No audio files found'}

        self.logger.info(f"Found {len(audio_files)} audio files")

        return self._process_files(audio_files, force)

    def _process_tracks(self, tracks: List[Dict], force: bool = False) -> Dict:
        """
        Process playlist tracks and fill metadata.
        
        Args:
            tracks: List of track metadata dictionaries
            force: Force overwrite existing metadata
            
        Returns:
            Processing results
        """
        results = {'success': True, 'processed': 0, 'enriched': 0, 'skipped': 0}
        
        self.logger.info(f"Starting metadata enrichment for {len(tracks)} tracks")

        for track in tqdm(tracks, desc="Processing tracks", unit="track"):
            track_name = track.get('name', 'Unknown')
            artist_name = track.get('artist', 'Unknown')
            track_num = results['processed'] + 1
            
            self.logger.debug(f"[{track_num}/{len(tracks)}] Processing: {artist_name} - {track_name}")
            
            # Check cloud status: only process uploaded or matched tracks
            cloud_status = track.get('cloudStatus', '')
            if cloud_status and cloud_status not in ['uploaded', 'matched']:
                self.logger.debug(f"  └─ Skipped: Cloud status is '{cloud_status}' (not uploaded/matched)")
                results['skipped'] += 1
                continue
            
            filepath = track.get('filepath')
            if not filepath or not self.detector.is_downloaded(filepath):
                self.logger.debug(f"  └─ Skipped: File not downloaded or not found")
                results['skipped'] += 1
                continue

            # Create track identifier
            track_id = TrackIdentifier(
                artist=track.get('artist', ''),
                title=track.get('name', ''),
                album=track.get('album')
            )

            if not track_id.is_complete():
                self.logger.debug(f"  └─ Skipped: Incomplete track info (missing artist or title)")
                results['skipped'] += 1
                continue

            # Read current tags
            current_tags = self.tag_manager.read_tags(filepath)
            self.logger.debug(f"  └─ Current tags: BPM={current_tags.get('bpm')}, Year={current_tags.get('year')}, Genre={current_tags.get('genre')}")
            
            # Enrich metadata
            enriched = self.enricher.enrich_track(filepath, current_tags, track_id, force)

            # Query databases
            self.logger.debug(f"  └─ Querying databases for: {artist_name} - {track_name}")
            entries = self.query_orchestrator.query_all_sources(
                track_id.artist,
                track_id.title
            )
            self.logger.debug(f"  └─ Found {len(entries)} metadata entries from databases")

            for entry in entries:
                enriched.add_entry(entry)

            # Write tags - only allow specific fields (year, bpm, genre, composer)
            if enriched.entries:
                ALLOWED_FIELDS = {'year', 'bpm', 'genre', 'composer'}
                tags_to_write = {
                    e.field.value: e.value 
                    for e in enriched.entries.values() 
                    if e.field.value in ALLOWED_FIELDS
                }
                if tags_to_write:
                    fields_str = ', '.join([f"{k}={v}" for k, v in tags_to_write.items()])
                    self.logger.debug(f"  └─ Writing {len(tags_to_write)} fields: {fields_str}")
                    success = self.tag_manager.write_tags(filepath, tags_to_write, force)
                    if success:
                        self.logger.info(f"  ✓ ENRICHED: {artist_name} - {track_name} ({fields_str})")
                        results['enriched'] += 1
                    else:
                        self.logger.warning(f"  ✗ FAILED to write tags: {artist_name} - {track_name}")
                        results['skipped'] += 1
                else:
                    self.logger.debug(f"  └─ Skipped: No writable fields available")
                    results['skipped'] += 1
            else:
                self.logger.debug(f"  └─ Skipped: No enrichment data found")
                results['skipped'] += 1

            results['processed'] += 1

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Metadata Enrichment Complete")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Total Processed: {results['processed']} tracks")
        self.logger.info(f"Successfully Enriched: {results['enriched']} tracks")
        self.logger.info(f"Skipped: {results['skipped']} tracks")
        self.logger.info(f"Log file: data/logs/metadata_enrichment.log")
        self.logger.info(f"{'='*80}\n")
        
        return results

    def _process_files(self, audio_files: List[str], force: bool = False) -> Dict:
        """
        Process audio files and fill metadata.
        
        Args:
            audio_files: List of file paths
            force: Force overwrite existing metadata
            
        Returns:
            Processing results
        """
        results = {'success': True, 'processed': 0, 'enriched': 0, 'skipped': 0}

        for filepath in tqdm(audio_files, desc="Processing files", unit="file"):
            # Read current tags
            current_tags = self.tag_manager.read_tags(filepath)
            
            artist = current_tags.get('artist', '')
            title = current_tags.get('title', '')

            if not artist or not title:
                results['skipped'] += 1
                continue

            # Create track identifier
            track_id = TrackIdentifier(
                artist=artist,
                title=title,
                album=current_tags.get('album')
            )

            # Enrich metadata
            enriched = self.enricher.enrich_track(filepath, current_tags, track_id, force)

            # Query databases
            entries = self.query_orchestrator.query_all_sources(artist, title)

            for entry in entries:
                enriched.add_entry(entry)

            # Write tags - only allow specific fields (year, bpm, genre, composer)
            if enriched.entries:
                ALLOWED_FIELDS = {'year', 'bpm', 'genre', 'composer'}
                tags_to_write = {
                    e.field.value: e.value 
                    for e in enriched.entries.values() 
                    if e.field.value in ALLOWED_FIELDS
                }
                if tags_to_write:
                    success = self.tag_manager.write_tags(filepath, tags_to_write, force)
                    if success:
                        self.logger.info(f"Enriched {len(tags_to_write)} fields: {title}")
                        results['enriched'] += 1
                    else:
                        self.logger.warning(f"Failed to write tags: {title}")
                        results['skipped'] += 1
                else:
                    results['skipped'] += 1
            else:
                results['skipped'] += 1
            
            # Embed cover art if MusicBrainz ID available
            if current_tags.get('musicbrainz_release_id'):
                mbid = current_tags.get('musicbrainz_release_id')
                try:
                    cover_success = self.cover_art_manager.enrich_with_cover_art(
                        filepath,
                        mbid=mbid,
                        artist=artist,
                        album=current_tags.get('album')
                    )
                    if cover_success:
                        self.logger.debug(f"Cover art embedded: {title}")
                except Exception as e:
                    self.logger.debug(f"Cover art embedding failed for {title}: {e}")

            results['processed'] += 1

        return results

    def _resolve_folder_path(self, folder_name: str) -> Optional[str]:
        """
        Resolve folder name to absolute path.
        
        Args:
            folder_name: Folder name or path
            
        Returns:
            Absolute path or None if not found
        """
        # Try as absolute path first
        if os.path.isdir(folder_name):
            return os.path.abspath(folder_name)

        # Try in common locations
        home = os.path.expanduser("~")
        common_paths = [
            os.path.join(home, "Music", folder_name),
            os.path.join(home, folder_name),
            os.path.join(home, "Music", "Music Media", folder_name),
        ]

        for path in common_paths:
            if os.path.isdir(path):
                return path

        return None

    def _find_audio_files(self, folder_path: str) -> List[str]:
        """
        Find all audio files in folder (non-recursive).
        
        Args:
            folder_path: Path to folder
            
        Returns:
            List of audio file paths
        """
        audio_files = []
        supported_formats = self.detector.get_supported_formats()

        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if os.path.isfile(filepath) and self.detector.is_audio_file(filepath):
                audio_files.append(filepath)

        return audio_files


class MetadataFillCLI:
    """CLI interface for metadata_fill module."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.filler = MetadataFiller(self.logger)
        # Point to scripts directory in src/scripts
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        self.apple_music = AppleMusicInterface(scripts_dir)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CLI with file and console output."""
        import logging.handlers
        from datetime import datetime
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger('metadata_fill')
        logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers to avoid duplicates
        logger.handlers = []
        
        # File handler - write to data/logs/metadata_enrichment.log
        log_file = os.path.join(logs_dir, 'metadata_enrichment.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler - INFO level for user-friendly output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def run(self, args: argparse.Namespace) -> int:
        """
        Run metadata filling operation.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        # Set logging level based on verbosity
        if hasattr(args, 'verbose') and args.verbose:
            self.logger.setLevel(logging.DEBUG)
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.DEBUG)
        
        # Log start of operation
        target = args.playlist if args.playlist else args.folder
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"METADATA ENRICHMENT STARTED")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Target: {target}")
        self.logger.info(f"Force overwrite: {getattr(args, 'force', False)}")
        self.logger.info(f"Verbose: {getattr(args, 'verbose', False)}")
        self.logger.info(f"{'='*80}\n")
        
        # Validate exactly one target is specified
        if args.playlist and args.folder:
            self.logger.error("Specify either --playlist or --folder, not both")
            return 1

        if not args.playlist and not args.folder:
            self.logger.error("Must specify either --playlist or --folder")
            return 1

        # Process target
        try:
            if args.playlist:
                result = self.filler.fill_playlist(
                    args.playlist,
                    force=args.force
                )
            else:  # args.folder
                result = self.filler.fill_folder(
                    args.folder,
                    force=args.force
                )

            if not result.get('success'):
                self.logger.error(f"Operation failed: {result.get('error')}")
                return 1

            # Print summary
            self._print_summary(result)
            return 0

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _print_summary(self, result: Dict) -> None:
        """Print operation summary."""
        print("\n" + "="*80)
        print("Metadata Fill Summary")
        print("="*80)
        print(f"Processed: {result.get('processed', 0)} items")
        print(f"Enriched:  {result.get('enriched', 0)} items")
        print(f"Skipped:   {result.get('skipped', 0)} items")
        print("="*80 + "\n")


def create_cli_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog='metadata-fill',
        description='Fill missing metadata for playlists or folders'
    )

    # Target selection (mutually exclusive)
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '--playlist',
        type=str,
        help='Playlist name to fill metadata for'
    )
    target_group.add_argument(
        '--folder',
        type=str,
        help='Folder path or name to fill metadata for'
    )

    # Options
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite existing metadata without asking'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()

    # Adjust logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get whitelist option
    cli = MetadataFillCLI()
    exit_code = cli.run(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
