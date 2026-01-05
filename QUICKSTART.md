# affective_playlists - Quick Start Guide

## One-Command Installation ⚡

```bash
git clone https://github.com/sokkohai/affective_playlists.git
cd affective_playlists
bash install.sh
```

That's it! The script handles:
- Python version checking
- Virtual environment setup
- Dependency installation
- Package installation
- Test running
- Configuration setup

## First Run

### 1. Configure API Credentials (Required)

```bash
vim .env
```

Add at minimum:
```bash
OPENAI_API_KEY=sk-your-key-here
```

Get your key from: https://platform.openai.com/api-keys

### 2. Activate Environment

Every new terminal session:
```bash
source activate.sh
```

You should see:
```
✓ affective_playlists environment ready!

Available commands:
  affective-playlists                 # Interactive menu
  affective-playlists temperament     # AI-based Playlist Temperament Analysis
  affective-playlists enrich          # Metadata Filling and Enrichment
  affective-playlists organize        # Playlist Organization by Genre
```

### 3. Run the App

```bash
affective-playlists
```

Choose from the interactive menu.

## Usage Examples

### Interactive Menu
```bash
affective-playlists
```
Select option from menu.

### Temperament Analysis
```bash
# Interactive prompt for playlist selection
affective-playlists temperament

# With verbose logging
affective-playlists temperament -v
```

Analyzes emotional tone of playlists using OpenAI GPT.

### Metadata Enrichment
```bash
# Interactive prompt
affective-playlists enrich

# Specific playlist
affective-playlists enrich --playlist "My Playlist"

# Verbose mode
affective-playlists enrich --playlist "My Playlist" -v
```

Fills missing: BPM, Genre, Year, Cover Art

### Playlist Organization
```bash
# Interactive mode with confirmation
affective-playlists organize
```

Organizes playlists by genre (Hip-Hop, Jazz, Electronic, etc.)

## Configuration

### Environment Variables (.env)

**Required:**
```bash
OPENAI_API_KEY=sk-...
```

**Optional:**
```bash
SPOTIFY_CLIENT_ID=your-id
SPOTIFY_CLIENT_SECRET=your-secret
LASTFM_API_KEY=your-key
DISCOGS_TOKEN=your-token
```

### Whitelist Configuration

Control which playlists to process in `data/config/whitelist.json`:

```json
{
  "enabled": true,
  "playlists": [
    "My Playlist 1",
    "My Playlist 2"
  ]
}
```

- `enabled: false` - Process all playlists (default)
- `enabled: true` - Process only listed playlists

## Common Commands

```bash
# After first installation, activate with:
source activate.sh

# Then use any of these:
affective-playlists                  # Interactive menu
affective-playlists --help           # Show help
affective-playlists --version        # Show version
affective-playlists -v               # Verbose mode

# Or specific features:
affective-playlists temperament
affective-playlists enrich
affective-playlists organize
```

## File Locations

- **Config**: `.env`
- **Logs**: `data/logs/` or `temperament_analyzer.log`
- **Cache**: `data/cache/`
- **Whitelist**: `data/config/whitelist.json`
- **Data**: `data/` (all application data)

## Troubleshooting

### "affective-playlists: command not found"
```bash
# Activate environment first
source activate.sh
affective-playlists
```

### "OPENAI_API_KEY not found"
```bash
# Edit .env
vim .env

# Add your key:
OPENAI_API_KEY=sk-your-key
```

### "Python 3 not found"
```bash
# Install Python 3.10+
brew install python@3.10
```

### "Music.app not accessible"
1. System Preferences → Security & Privacy
2. Give Terminal Full Disk Access
3. Restart Music.app

## Running Tests

```bash
source activate.sh
pytest tests/ -v
```

All 136+ tests should pass.

## Documentation

- **[README.md](README.md)** - Full documentation
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Detailed setup
- **[docs/OVERVIEW.md](docs/OVERVIEW.md)** - Architecture
- **[docs/requirements/](docs/requirements/)** - Specifications
- **[docs/rules/](docs/rules/)** - Development standards

## Next Steps

1. ✅ Run `bash install.sh`
2. ✅ Edit `.env` with API keys
3. ✅ Run `source activate.sh`
4. ✅ Run `affective-playlists`
5. 📖 Read [README.md](README.md) for detailed info

---

**That's it! Enjoy managing your music library. 🎵**
