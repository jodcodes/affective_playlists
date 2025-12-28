# affective_playlists 🎵

**Unified suite for music analysis and organization**

A single, cohesive project that combines three powerful music tools into one streamlined application.

## Features

- 🎵 **Temperament Analysis** - AI-based playlist emotion classification (4 categories: Woe, Frolic, Dread, Malice)
- 📝 **Metadata Enrichment** - Automatic metadata filling (BPM, Genre, Year) from multiple databases
- 📁 **Playlist Organization** - Genre-based playlist classification and organization

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
vim .env

# 3. Run the unified CLI
python main.py
```

## Usage

**Interactive menu (default):**
```bash
python main.py
```

**Run specific feature:**
```bash
python main.py temperament    # Run temperament analysis
python main.py enrich         # Run metadata enrichment
python main.py organize       # Run playlist organization
```

**Show help:**
```bash
python main.py --help
```

## Project Structure

```
affective_playlists/
├── main.py              # Unified CLI entry point
├── requirements.txt     # All dependencies
├── .env.example         # Environment template
├── src/                 # All Python code
│   ├── temperament_analyzer.py      # 4tempers: AI temperament analysis
│   ├── metadata_fill.py              # metad_enr: Metadata enrichment
│   ├── plsort.py                     # plsort: Playlist organization
│   ├── apple_music.py                # Shared Apple Music interface
│   ├── normalizer.py                 # Text normalization
│   ├── logger.py                     # Logging utilities
│   ├── config.py                     # Configuration management
│   └── scripts/                      # AppleScript automation files
├── data/                # Centralized data & configs
│   ├── config/                       # All configuration files
│   │   ├── whitelist.json           # Whitelist config
│   │   └── playlist_whitelist.json
│   ├── artist_lists/                 # Genre artist lists (plsort)
│   ├── logs/                         # Application logs
│   └── ...
├── tests/               # Test files
└── ...
```

## Environment Variables

Create a `.env` file with:

```bash
# 4tempers (required for temperament analysis)
OPENAI_API_KEY=sk-your-key

# Optional: Better metadata
SPOTIFY_CLIENT_ID=your-id
SPOTIFY_CLIENT_SECRET=your-secret
LASTFM_API_KEY=your-key
```

## Whitelist Configuration

Control which playlists are processed in `data/config/whitelist.json`:

```json
{
  "enabled": false,
  "playlists": ["Playlist 1", "Playlist 2"]
}
```

- `enabled: false` - Process all playlists (default)
- `enabled: true` - Process only listed playlists

## Documentation

- **Temperament Analysis**: Classic emotion-based playlist classification using GPT
- **Metadata Enrichment**: Fills missing audio metadata from MusicBrainz, Spotify, and other sources
- **Playlist Organization**: Classifies and organizes playlists by genre (Hip-Hop, Electronic, Jazz, etc.)

All scripts and AppleScript files are in `src/scripts/`.
All configurations and data files are centralized in `data/`.

## License

MIT License - See [LICENSE](LICENSE) for details

---

**Made with ❤️ for Apple Music lovers**
