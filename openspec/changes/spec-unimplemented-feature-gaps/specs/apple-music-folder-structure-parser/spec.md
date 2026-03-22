## ADDED Requirements

### Requirement: Parse Playlist Folder Structure From AppleScript Output
The system MUST parse AppleScript folder output into a deterministic hierarchical mapping of folder names to playlist names.

#### Scenario: Valid folder output is parsed
- **WHEN** `get_playlist_folder_structure` receives successful AppleScript output containing one or more folders and playlists
- **THEN** it returns a dictionary where each key is a folder name
- **AND** each value is an ordered list of playlist names within that folder.

#### Scenario: Empty folder output is handled
- **WHEN** AppleScript succeeds but returns no folders
- **THEN** the method returns an empty dictionary
- **AND** does not raise an exception.

### Requirement: Reject Malformed Folder Output Safely
The system MUST fail safely on malformed AppleScript output without corrupting caller state.

#### Scenario: Malformed output cannot be parsed
- **WHEN** folder output does not match expected parsable structures
- **THEN** the method returns `None`
- **AND** logs a debug or warning message with parse failure context.
