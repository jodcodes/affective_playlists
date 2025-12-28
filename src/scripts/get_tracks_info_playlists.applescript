-- getPlaylistTracksJSON_byPID.scpt
on getPlaylistTracksByPID(playlistPID)
	try
		if (count of playlistPID) is 0 then
			return "ERROR: Playlist persistent ID required"
		end if
		
		tell application "Music"
			-- Playlist per PID finden
			set p to first playlist whose persistent ID is playlistPID
			
			set pid to persistent ID of p
			set trackList to {}
			
			repeat with t in tracks of p
				set tname to name of t
				if tname is missing value then set tname to ""
				
				set tartist to artist of t
				if tartist is missing value then set tartist to ""
				
				set talbum to album of t
				if talbum is missing value then set talbum to ""
				
				set tgenre to genre of t
				if tgenre is missing value then set tgenre to ""
				
				set tbpm to bpm of t
				if tbpm is missing value then set tbpm to ""
				
				set tyear to year of t
				if tyear is missing value then set tyear to ""
				
				set tcomposer to composer of t
				if tcomposer is missing value then set tcomposer to ""
				
				set tduration to duration of t
				if tduration is missing value then set tduration to ""
				
				-- Track als Record (JSON-ähnlich)
				set end of trackList to {playlistID:pid, trackID:(persistent ID of t), name:tname, artist:tartist, album:talbum, genre:tgenre, bpm:tbpm, year:tyear, composer:tcomposer, duration:tduration}
			end repeat
		end tell
		
		return trackList
	on error errMsg
		return "ERROR: " & errMsg
	end try
end getPlaylistTracksByPID

-- Run
on run argv
	if (count of argv) is 0 then
		return "ERROR: Playlist persistent ID required"
	else
		return getPlaylistTracksByPID(item 1 of argv)
	end if
end run