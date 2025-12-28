# plsort - Playlist Sorter

Automatically categorizes your music playlists into genres using artist-based classification.

## Features

- **Genre Classification**: Categorizes playlists into 6 genres (world, electronic, jazz, disco/funk/soul, rock, hip-hop)
- **Artist-Based**: Uses artist recognition to determine playlist genre
- **Metadata Enrichment**: Optional enrichment from MusicBrainz, Last.fm, Discogs, RateYourMusic
- **Apple Music Integration**: Organize playlists directly in Apple Music
- **Export Results**: Save classification results to JSON

## Genres

1. **World** - World music, global sounds, non-Western music
2. **Electronic** - Electronic, synth, house, techno, ambient, EDM
3. **Jazz** - Jazz, bebop, cool jazz, fusion
4. **Disco/Funk/Soul** - Disco, funk, soul, R&B, groove
5. **Rock** - Rock, hard rock, alternative rock, indie
6. **Hip-Hop** - Hip-hop, rap, trap, boom bap

## Usage

```bash
# Preview what would be categorized
python plsort.py --dry-run

# Execute categorization
python plsort.py --execute

# Process single playlist
python plsort.py --playlist "My Playlist"

# Enrich with web data
python plsort.py --enrich musicbrainz lastfm

# Export results
python plsort.py --export results.json

# Verbose output
python plsort.py --verbose
```

## Configuration

Edit `config/genre_mapping.json` to customize genre assignments.
