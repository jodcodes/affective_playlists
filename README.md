# affective_playlists 🎵

**A unified suite of music analysis and organization tools for Apple Music.**

Integrates three complementary subprojects into one cohesive system:

- 🎵 **4tempers** - AI-based Playlist Temperament Analysis
- 📝 **metad_enr** - Metadata Filling and Enrichment  
- 📁 **plsort** - Playlist Organization and Classification

---

## 🚀 Quick Start (2 minutes)

```bash
# 1. Run setup
bash setup.sh

# 2. Configure credentials
cp .env.example .env
vim .env

# 3. Run the CLI
python main.py
```

**That's it!** See [QUICKSTART.md](QUICKSTART.md) for more details.

---

## 📋 What Each Tool Does

### 🎵 4tempers - AI Temperament Analysis
Classifies your playlists into 4 emotional categories using OpenAI GPT:
- **Woe** 🌧️ - Melancholic, sad, introspective
- **Frolic** ☀️ - Happy, joyful, celebratory
- **Dread** 😰 - Tense, fearful, ominous
- **Malice** 🔥 - Angry, aggressive, intense

**Requires:** OpenAI API key

### 📝 metad_enr - Metadata Enrichment
Automatically fills missing metadata in audio files by querying multiple databases:
- BPM, Genre, Year, Artist Info
- Supports: MP3, FLAC, OGG, M4A, WAV, AIFF
- Databases: MusicBrainz, AcousticBrainz, Spotify, Last.fm, Discogs, Wikidata

**Optional APIs:** Spotify, Last.fm

### 📁 plsort - Genre Organization
Automatically organizes your Apple Music playlists by genre:
- 6 supported genres (Hip-Hop, Electronic, Disco/Funk/Soul, Jazz, World, Rock)
- Uses rule-based scoring + ML fallback (TF-IDF)
- Dry-run mode before applying changes
- Zero external dependencies (uses Python stdlib only)

**No API keys needed!**

---

## 🏗️ Architecture

### Unified Structure
```
affective_playlists/
├── main.py              # Main CLI entry point
├── setup.sh             # Setup script
├── activate.sh          # Environment activation
├── requirements.txt     # All dependencies
├── .env.example         # Environment template
├── shared/              # Shared modules (used by all)
│   ├── apple_music.py   # Apple Music interface
│   ├── normalizer.py    # Text normalization
│   └── logger.py        # Logging utilities
├── 4tempers/            # AI Temperament Analysis
├── metad_enr/           # Metadata Enrichment
└── plsort/              # Playlist Organization
```

### Key Improvements
✅ **No Duplicate Code** - Common utilities in `shared/`  
✅ **Single Entry Point** - One `main.py` for all tools  
✅ **Unified Config** - One `.env` for all credentials  
✅ **Easy Setup** - One `setup.sh` script  
✅ **Backwards Compatible** - Old code still works  

---

## 📦 Installation

### Prerequisites
- **macOS** (Apple Music integration required)
- **Python 3.8+**

### Full Setup
```bash
# 1. Navigate to project
cd /Users/joeldebeljak/own_repos/affective_playlists

# 2. Run setup (creates venv, installs dependencies)
bash setup.sh

# 3. Activate environment
source activate.sh

# 4. Configure .env
vim .env

# 5. Run!
python main.py
```

### Alternative: Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

---

## 🎮 Usage

### Interactive Menu (Recommended)
```bash
python main.py
```

Select which tool to run:
```
1. 4tempers   - AI-based Playlist Temperament Analysis
2. metad_enr  - Metadata Filling and Enrichment
3. plsort     - Playlist Organization and Classification
0. Exit
```

### Command Line
```bash
# List available tools
python main.py --list

# Run specific tool
python main.py 4tempers
python main.py metad_enr --playlist "Favorites"
python main.py plsort --dry-run

# Get help for a tool
python main.py --help-4tempers
python main.py --help-plsort
```

### Direct Execution
```bash
# Run 4tempers
cd 4tempers && python temperament_analyzer.py

# Run metad_enr
cd metad_enr && python -m src.metadata_fill --playlist "Favorites"

# Run plsort
cd plsort && python plsort.py --help
```

---

## 🔑 Environment Setup

Edit `.env` with your API credentials:

```bash
# Required for 4tempers
OPENAI_API_KEY=sk-your-api-key

# Optional: Better metadata
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret

# Optional: Last.fm data
LASTFM_API_KEY=your-lastfm-key
```

Get API keys:
- OpenAI: https://platform.openai.com/api-keys
- Spotify: https://developer.spotify.com/dashboard
- Last.fm: https://www.last.fm/api/account/create

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start guide
- **[REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)** - Detailed architecture & migration guide
- **[4tempers/README.md](4tempers/README.md)** - AI temperament analysis details
- **[metad_enr/README.md](metad_enr/README.md)** - Metadata enrichment details
- **[plsort/README.md](plsort/README.md)** - Playlist organization details

---

## 🔧 Shared Modules

All three tools use shared utilities from `shared/`:

### AppleMusicInterface
```python
from shared.apple_music import AppleMusicInterface

ami = AppleMusicInterface()
playlists = ami.get_playlist_names()
tracks = ami.get_playlist_tracks("Favorites")
```

### TextNormalizer
```python
from shared.normalizer import TextNormalizer

normalizer = TextNormalizer()
clean_text = normalizer.normalize("  HELLO & World!  ")
# → "hello and world"
```

### Logger Setup
```python
from shared.logger import setup_logger

logger = setup_logger("my_app", log_file="logs/app.log")
logger.info("Starting analysis...")
```

---

## 🐛 Troubleshooting

### Apple Music Not Accessible
```bash
# Grant AppleScript permissions
# System Preferences → Security & Privacy → Full Disk Access
# Add Terminal/Python to the list

# Test access
osascript -e 'tell application "Music" to return name'
```

### Module Not Found Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/Users/joeldebeljak/own_repos/affective_playlists:$PYTHONPATH

# Or use activation script
source activate.sh
```

### API Key Issues
```bash
# Verify .env file exists and has correct format
cat .env

# Check python-dotenv is installed
pip list | grep python-dotenv

# Load keys in Python
from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv('OPENAI_API_KEY'))
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Total Code | ~6,500 lines |
| Shared Modules | 3 (apple_music, normalizer, logger) |
| External Dependencies | 2 (requests, python-dotenv) |
| Python Standard Library | 8,000+ (plsort uses stdlib only) |
| Supported Genres | 6 |
| Audio Formats | 6 |
| Temperament Categories | 4 |

---

## ✨ Features

### Common to All
- ✅ Native macOS Apple Music integration (no external tools)
- ✅ AppleScript automation (no developer account needed)
- ✅ Unified logging and error handling
- ✅ Text normalization and standardization
- ✅ Caching for performance

### 4tempers Specific
- ✅ OpenAI GPT-4o-mini analysis
- ✅ Multi-provider metadata enrichment
- ✅ JSON results export
- ✅ Cost-optimized with track caching

### metad_enr Specific
- ✅ Multi-format audio file support
- ✅ Multiple database sources (5 databases)
- ✅ Smart metadata merging
- ✅ Confidence scoring for each field
- ✅ Source tracking

### plsort Specific
- ✅ Zero external dependencies
- ✅ Rule-based + ML classification
- ✅ Interactive playlist selection
- ✅ Dry-run and execute modes
- ✅ Artist enrichment
- ✅ Web data enrichment (optional)

---

## 🤝 Contributing

When making changes:

1. **Update shared modules** in `shared/` for common code
2. **Keep subrepos independent** - avoid subrepo-specific dependencies
3. **Test all three** - ensure changes don't break other tools
4. **Document** - update README and REFACTORING_GUIDE.md
5. **Maintain backwards compatibility** - old imports should still work

---

## 📄 License

MIT License - See individual LICENSE files in each subrepo

---

## 👤 Author

Created by **Joel Debeljak**  
Last Updated: **December 27, 2025**  
Version: **1.0.0**

---

## 🎯 Next Steps

1. **[Run the setup script →](setup.sh)**
   ```bash
   bash setup.sh
   ```

2. **[Read the quick start →](QUICKSTART.md)**
   ```bash
   cat QUICKSTART.md
   ```

3. **[Launch the CLI →](main.py)**
   ```bash
   python main.py
   ```

---

**Enjoy analyzing your music! 🎵**
