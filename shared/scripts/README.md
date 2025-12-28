# Shared AppleScript Utilities

Zentrale AppleScript-Sammlung für alle Music.app-Operationen in diesem Projekt.

## Files

### music_app.applescript
- `checkMusicApp()` - Überprüft ob Music.app verfügbar ist

### playlist_reader.applescript
- `getPlaylists()` - Ruft alle Playlists ab
- `getPlaylistTracks(playlistName)` - Ruft alle Tracks einer Playlist ab (mit Metadaten)

### playlist_manager.applescript
- `createPlaylistFolder(folderName)` - Erstellt einen Playlist-Ordner
- `movePlaylistToFolder(playlistName, folderName)` - Verschiebt Playlist in Ordner
- `createPlaylist(playlistName)` - Erstellt neue Playlist
- `deletePlaylist(playlistName)` - Löscht Playlist

## Python Usage

### Via AppleMusicInterface (shared.apple_music)
```python
from shared.apple_music import AppleMusicInterface
import os

shared_scripts = os.path.join(os.path.dirname(__file__), '..', 'shared', 'scripts')
ami = AppleMusicInterface(shared_scripts)

# Get playlists
playlists = ami.get_playlist_names()

# Get tracks from playlist
tracks = ami.get_playlist_tracks('My Playlist')
```

### Via Shared Script Utils
```python
from shared.scripts import (
    check_music_app,
    get_playlists,
    get_playlist_tracks,
    create_playlist_folder,
    move_playlist_to_folder,
    create_playlist,
    delete_playlist
)

# Check if app is available
if check_music_app():
    # Get all playlists
    playlists = get_playlists()
    
    # Get tracks from a specific playlist
    tracks_text = get_playlist_tracks('My Playlist')
    
    # Manage playlists
    create_playlist_folder('My Folder')
    move_playlist_to_folder('My Playlist', 'My Folder')
```

## Direct AppleScript Execution

```bash
osascript shared/scripts/playlist_reader.applescript
osascript shared/scripts/playlist_reader.applescript "Playlist Name"
osascript shared/scripts/playlist_manager.applescript create_folder "Folder Name"
osascript shared/scripts/playlist_manager.applescript move "Playlist" "Folder"
```

## Output Formats

### get_playlist_tracks
Pipe-separated format:
```
persistentID | trackID | name | artist | album | genre | bpm | year | composer | duration
```

### getPlaylists
One playlist name per line.

## Migration Notes

Diese zentrale Scripts-Sammlung ersetzt die duplicierten Scripts in:
- ~~4tempers/scripts/~~ (gelöscht)
- ~~plsort/scripts/~~ (gelöscht)

Alle Module wurden aktualisiert um auf `shared/scripts` zu zeigen.
