# plsort - Quick Start

## About plsort

plsort categorizes your music playlists into genres:
- **world** - World music and global sounds
- **electronic** - Electronic, synth, house, techno
- **jazz** - Jazz, bebop, fusion
- **disco_funk_soul** - Disco, funk, soul, R&B
- **rock** - Rock, alternative, indie
- **hiphop** - Hip-hop, rap, trap

## Usage

Basic dry-run (preview):
```bash
python plsort.py
```

Show help:
```bash
python plsort.py --help
```

Process specific playlist:
```bash
python plsort.py --playlist "My Favorite Songs"
```

Enable verbose logging:
```bash
python plsort.py --verbose
```

Export results to JSON:
```bash
python plsort.py --export results.json
```

## Configuration

Edit `config.json` to customize:
- Genre categories
- Apple Music integration
- Enrichment sources (MusicBrainz, Last.fm, Discogs)
