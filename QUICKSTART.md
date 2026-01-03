# affective_playlists - Quick Start Guide

**Welcome to the unified affective_playlists project!**

This guide will get you up and running in 5 minutes.

## What is affective_playlists?

A unified suite of three complementary music tools:
- **4tempers** - Classify playlists by emotional temperament using AI
- **metad_enr** - Fill missing metadata in audio files
- **plsort** - Organize Apple Music playlists by genre

## Installation (5 minutes)

### 1. Prerequisites
- macOS (for Apple Music integration)
- Python 3.8+

### 2. Clone & Navigate
```bash
cd /Users/joeldebeljak/own_repos/affective_playlists
```

### 3. Run Setup Script
```bash
bash setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies
- Create necessary directories
- Verify shared modules
- Test Apple Music access

### 4. Configure Credentials
Edit `.env` with your API keys:

```bash
# Open the environment file
vim .env

# Or use any text editor
```

**Required for 4tempers:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys

**Optional:**
- `SPOTIFY_CLIENT_ID/SECRET` - Better metadata
- `LASTFM_API_KEY` - Last.fm data access

## Running affective_playlists

### Option 1: Interactive Menu (Recommended)
```bash
python main.py
```

Choose from the interactive menu:
```
1. 4tempers   - AI-based Playlist Temperament Analysis
2. metad_enr  - Metadata Filling and Enrichment
3. plsort     - Playlist Organization and Classification
0. Exit
```

### Option 2: Run Specific Subrepo
```bash
# Run 4tempers
python main.py 4tempers

# Run metad_enr with arguments
python main.py metad_enr --playlist "Favorites"

# Run plsort
python main.py plsort --dry-run
```

### Option 3: Direct Execution
```bash
# Run each subrepo directly
cd 4tempers
python temperament_analyzer.py

cd ../metad_enr
python -m src.metadata_fill --playlist "Favorites"

cd ../plsort
python plsort.py --help
```

## Project Structure

```
plMetaTemp/
├── main.py              # Main entry point
├── setup.sh             # Setup script
├── requirements.txt     # Unified dependencies
├── .env.example         # Environment template
├── REFACTORING_GUIDE.md # Detailed architecture
├── shared/              # Shared modules (used by all subrepos)
├── 4tempers/            # AI Temperament Analysis
├── metad_enr/           # Metadata Enrichment
└── plsort/              # Playlist Organization
```

## Key Features

### Unified Shared Modules
All three subrepos use shared code:
- `shared.apple_music.AppleMusicInterface` - Apple Music access
- `shared.normalizer.TextNormalizer` - Text normalization
- `shared.logger.setup_logger` - Logging

### Single Entry Point
One `main.py` to access all three tools with a consistent interface.

### Unified Configuration
Single `.env` file for all environment variables.

### Single Requirements File
All dependencies managed from root `requirements.txt`.

## Examples

### 4tempers - Analyze Playlist Temperament
```bash
python main.py 4tempers
```
Analyzes selected playlists using OpenAI GPT to classify them into:
- 🌧️ **Woe** (Melancholic) - Sadness, loneliness
- ☀️ **Frolic** (Sanguine) - Joy, celebration
- 😰 **Dread** (Phlegmatic) - Fear, tension
- 🔥 **Malice** (Choleric) - Rage, aggression

### metad_enr - Fill Missing Metadata
```bash
python main.py metad_enr --playlist "Favorites"
```
Fills BPM, Genre, Year by querying:
- MusicBrainz (most reliable)
- AcousticBrainz
- Discogs
- Wikidata
- Last.fm

### plsort - Organize by Genre
```bash
python main.py plsort --dry-run
python main.py plsort --execute
```
Organizes playlists into folders by genre:
- Hip-Hop
- Electronic
- Disco/Funk/Soul
- Jazz
- World
- Rock

## Troubleshooting

### Issue: "Python 3 not found"
**Solution:** Install Python 3.8+
```bash
# macOS
brew install python3

# Or download from https://www.python.org
```

### Issue: Apple Music not accessible
**Solution:** Grant AppleScript permissions
1. Go to System Preferences → Security & Privacy
2. Ensure osascript has Full Disk Access
3. Restart Music.app

### Issue: "ModuleNotFoundError: No module named 'requests'"
**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Issue: API key errors
**Solution:** Verify .env file
```bash
# Check that .env exists and has correct values
cat .env

# Verify python-dotenv is installed
pip list | grep python-dotenv
```

## Next Steps

1. **Read the full documentation:**
   ```bash
   cat docs/OVERVIEW.md
   ```

2. **Explore the specifications:**
   ```bash
   cat docs/requirements/SPEC_TEMPERAMENT_ANALYZER.md
   cat docs/requirements/SPEC_METADATA_ENRICHMENT.md
   cat docs/requirements/SPEC_PLAYLIST_ORGANIZATION.md
   ```

3. **View available commands:**
   ```bash
   python main.py --help
   python main.py temperament --help
   python main.py enrich --help
   python main.py organize --help
   ```

## Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review log files in `data/logs/` or `temperament_analyzer.log`
3. Verify `.env` configuration
4. Run with `--verbose` for detailed output

## Architecture Highlights

### Why Refactor?
- **Eliminate Duplication** - shared code used by all subrepos
- **Single Entry Point** - unified CLI interface
- **Easier Maintenance** - changes in shared modules propagate to all tools
- **Better Organization** - clear separation of concerns
- **Backwards Compatible** - old code still works

### Key Improvements
✓ Removed duplicate `apple_music.py` (was in 2 subrepos)
✓ Removed duplicate `normalizer.py` (was in plsort)
✓ Unified requirements.txt
✓ Comprehensive .env.example
✓ Main CLI with interactive menu
✓ Setup script for easy installation
✓ Proper package structure with shared modules

## Version Info

- **Project:** plMetaTemp 1.0.0
- **Date:** December 27, 2025
- **Python:** 3.8+
- **Platform:** macOS (Apple Music required)
- **License:** MIT

---

**Happy analyzing! 🎵**
