"""
AppleScript interface for Apple Music integration.

Handles reading playlists, extracting track metadata, and moving playlists.
Supports both regular playlists and playlist folders.
Used by: plsort, metad_enr, 4tempers

NOTE: Whitelist filtering is handled by the calling code using shared.config module.
This interface just returns all playlists; the caller decides which to process.
"""

import subprocess
import json
import re
from typing import List, Dict, Optional, Tuple
import os


class AppleMusicInterface:
    """Interface to Apple Music via AppleScript."""

    def __init__(self, scripts_dir: str = "scripts"):
        """
        Initialize Apple Music interface.
        
        Args:
            scripts_dir: Directory containing AppleScript templates
        
        Note: Whitelist filtering is handled externally via shared.config module
        """
        self.scripts_dir = scripts_dir

    def _run_applescript(self, script: str) -> Tuple[bool, str]:
        """
        Run AppleScript and return result.
        
        Returns:
            (success: bool, output: str)
        """
        try:
            process = subprocess.Popen(
                ['osascript', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=script)
            
            if process.returncode != 0:
                return False, stderr
            
            return True, stdout.strip()
        except Exception as e:
            return False, str(e)

    def _load_script_template(self, template_name: str) -> str:
        """Load AppleScript template from file."""
        script_path = os.path.join(self.scripts_dir, f"{template_name}.applescript")
        try:
            with open(script_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"AppleScript template not found: {script_path}")


    def get_playlist_names(self) -> Optional[List[str]]:
        """
        Get list of all playlist names AND folder names in Apple Music.
        
        Includes both regular playlists and playlist folders.
        
        Returns:
            List of playlist/folder names or empty list if failed
        """
        script = '''
tell application "Music"
    set itemNames to {}
    
    -- Get regular playlists from library
    try
        repeat with pl in playlists
            set end of itemNames to name of pl
        end repeat
    end try
    
    -- Get playlist folders
    try
        repeat with fld in folders
            set end of itemNames to name of fld
        end repeat
    end try
    
    return itemNames
end tell
'''
        success, output = self._run_applescript(script)
        if not success:
            # Fallback: just get playlists
            script_fallback = '''
tell application "Music"
    set playlistNames to {}
    repeat with pl in playlists
        set end of playlistNames to name of pl
    end repeat
    return playlistNames
end tell
'''
            success, output = self._run_applescript(script_fallback)
            if not success:
                return []

        # Parse output (AppleScript returns items separated by commas)
        if not output:
            return []

        # Simple split on comma and clean up
        playlist_names = [name.strip() for name in output.split(",")]
        
        # Return all playlists without filtering
        # (whitelist filtering is handled by the caller via shared.config module)
        return playlist_names

    def is_folder(self, item_name: str) -> bool:
        """Check if an item is a folder (True) or playlist (False)."""
        script = f'''
tell application "Music"
    try
        set targetFolder to folder "{item_name}"
        return true
    on error
        return false
    end try
end tell
'''
        success, output = self._run_applescript(script)
        return success and "true" in output.lower()

    def get_playlist_tracks(self, playlist_name: str) -> Optional[List[Dict]]:
        """
        Get all tracks from a playlist or folder with metadata.
        
        Automatically detects if item is a folder or playlist and gets tracks accordingly.
        
        Returns:
            List of track metadata dicts or empty list if failed
        """
        # Try both approaches: regular playlist first, then as folder
        
        # Approach 1: Try as regular playlist
        tracks = self._get_regular_playlist_tracks(playlist_name)
        if tracks:
            return tracks
        
        # Approach 2: Try as folder
        tracks = self._get_folder_all_tracks(playlist_name)
        if tracks:
            return tracks
        
        # If both failed
        return []

    def _get_regular_playlist_tracks(self, playlist_name: str) -> Optional[List[Dict]]:
        """Get tracks from a regular (non-folder) playlist."""
        script = f'''
tell application "Music"
    set trackList to {{}}
    
    try
        set targetPlaylist to playlist "{playlist_name}"
        set trackCount to count of tracks of targetPlaylist
        if trackCount > 0 then
            repeat with trk in tracks of targetPlaylist
                set trackInfo to {{}}
                set trackInfo's title to name of trk
                set trackInfo's artist to artist of trk
                set trackInfo's album to album of trk
                set trackInfo's genre to genre of trk
                set trackInfo's bpm to bpm of trk
                set trackInfo's year to year of trk
                set trackInfo's composer to composer of trk
                set trackInfo's duration to duration of trk
                set end of trackList to trackInfo
            end repeat
        end if
        return trackList
    on error errMsg
        return {{}}
    end try
end tell
'''
        success, output = self._run_applescript(script)
        if not success or not output:
            return None

        tracks = self._parse_applescript_dict_list(output)
        return tracks if tracks else None

    def _get_folder_all_tracks(self, folder_name: str) -> Optional[List[Dict]]:
        """
        Get all tracks from all playlists within a folder.
        """
        # Step 1: Get list of playlists in the folder
        script = f'''
tell application "Music"
    set playlistNames to {{}}
    try
        set targetFolder to folder "{folder_name}"
        set playlistCount to count of playlists in targetFolder
        if playlistCount > 0 then
            repeat with pl in playlists in targetFolder
                set end of playlistNames to name of pl
            end repeat
        end if
    on error
        return {{}}
    end try
    return playlistNames
end tell
'''
        success, output = self._run_applescript(script)
        if not success or not output:
            return None

        # Parse playlist names
        playlist_names = [name.strip() for name in output.split(",") if name.strip()]
        
        if not playlist_names:
            return None

        # Step 2: Get tracks from each playlist in folder
        all_tracks = []
        for pl_name in playlist_names:
            tracks = self._get_regular_playlist_tracks(pl_name)
            if tracks:
                all_tracks.extend(tracks)

        return all_tracks if all_tracks else None

    def create_playlist_folder(self, folder_name: str, parent_folder: Optional[str] = None) -> bool:
        """
        Create a playlist folder in Apple Music.
        
        Returns:
            True if successful, False otherwise
        """
        if parent_folder:
            script = f'''
tell application "Music"
    try
        make new folder in folder "{parent_folder}" with properties {{name:"{folder_name}"}}
        return true
    on error errMsg
        return false
    end try
end tell
'''
        else:
            script = f'''
tell application "Music"
    try
        make new folder with properties {{name:"{folder_name}"}}
        return true
    on error errMsg
        return false
    end try
end tell
'''
        success, output = self._run_applescript(script)
        return success and "true" in output.lower()

    def move_playlist_to_folder(self, playlist_name: str, folder_name: str) -> bool:
        """
        Move a playlist to a specific folder.
        
        Returns:
            True if successful, False otherwise
        """
        script = f'''
tell application "Music"
    try
        set targetPlaylist to playlist "{playlist_name}"
        set targetFolder to folder "{folder_name}"
        move targetPlaylist to targetFolder
        return true
    on error errMsg
        return false
    end try
end tell
'''
        success, output = self._run_applescript(script)
        return success and "true" in output.lower()

    def create_playlist_if_missing(self, playlist_name: str) -> bool:
        """
        Create a new playlist if it doesn't exist.
        
        Returns:
            True if successful or already exists, False otherwise
        """
        script = f'''
tell application "Music"
    try
        set existing to playlist "{playlist_name}"
        return true
    on error
        try
            make new playlist with properties {{name:"{playlist_name}"}}
            return true
        on error
            return false
        end try
    end try
end tell
'''
        success, output = self._run_applescript(script)
        return success and "true" in output.lower()

    def _parse_applescript_dict_list(self, output: str) -> Optional[List[Dict]]:
        """
        Parse AppleScript dictionary list output.
        
        AppleScript returns data in a format like: {key1:value1, key2:value2}, {key1:value1, ...}
        
        This is a simplified parser - production code might need more robust parsing.
        """
        if not output:
            return None

        tracks = []
        
        # Pattern to match dict-like structures: {key:value, key:value, ...}
        dict_pattern = r'\{([^}]+)\}'
        matches = re.findall(dict_pattern, output)

        for match in matches:
            track_dict = {}
            # Parse key:value pairs
            pairs = match.split(',')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    # Try to convert to int
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    track_dict[key] = value
            
            if track_dict:
                tracks.append(track_dict)

        return tracks if tracks else None

    def get_playlist_folder_structure(self) -> Optional[Dict]:
        """
        Get the current folder structure of playlists.
        
        Returns:
            Hierarchical dict or None if failed
        """
        script = '''
tell application "Music"
    set folderStructure to {{}}
    repeat with folder in folders
        set folderStructure's (name of folder) to {}
        repeat with playlist in playlists of folder
            set end of folderStructure's (name of folder) to name of playlist
        end repeat
    end repeat
    return folderStructure
end tell
'''
        success, output = self._run_applescript(script)
        if not success:
            return None

        # Parse folder structure from output
        # This is complex due to AppleScript's output format
        return None  # TODO: Implement proper parsing

    def get_apple_music_version(self) -> Optional[str]:
        """Get the version of Apple Music/iTunes app."""
        script = '''
tell application "Music"
    return version
end tell
'''
        success, output = self._run_applescript(script)
        return output if success else None
