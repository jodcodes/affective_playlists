# affective_playlists 🎵

**Unified suite for music analysis and organization**

A powerful, single-command music tool that combines three complementary features into one streamlined application for Apple Music.

## ✨ Features

- 🎭 **Temperament Analysis** - AI-powered playlist emotion classification (Woe, Frolic, Dread, Malice)
- 📝 **Metadata Enrichment** - Automatic metadata filling (BPM, Genre, Year, Cover Art) from multiple sources
- 📚 **Playlist Organization** - Intelligent genre-based playlist classification and organization

## ⚡ Quick Start (One Command)

### Installation

Clone and install in one command:

```bash
git clone https://github.com/sokkohai/affective_playlists.git
cd affective_playlists
bash install.sh
```

That's it! The script will:
- ✓ Check Python version (3.10+)
- ✓ Create virtual environment
- ✓ Install all dependencies
- ✓ Install CLI commands
- ✓ Run tests
- ✓ Set up configuration directories

### First Time Setup

1. **Configure API credentials** (2 minutes):
   ```bash
   vim .env
   ```
   Add your OpenAI API key (required for temperament analysis):
   ```
   OPENAI_API_KEY=sk-your-key
   ```
   Optional APIs for better results:
   ```
   SPOTIFY_CLIENT_ID=your-id
   SPOTIFY_CLIENT_SECRET=your-secret
   LASTFM_API_KEY=your-key
   ```

2. **Activate environment** (every new terminal):
   ```bash
   source activate.sh
   ```

3. **Run the app**:
   ```bash
   affective-playlists
   ```

## 🎯 Usage

### Interactive Menu (Recommended)
```bash
affective-playlists
```

Choose from:
1. 🎭 **Temperament Analysis** - AI-based emotion classification
2. 📝 **Metadata Enrichment** - Fill missing audio metadata
3. 📚 **Playlist Organization** - Genre-based sorting

### Command Line

```bash
# Show interactive menu
affective-playlists

# Run temperament analysis
affective-playlists temperament

# Fill metadata for a playlist
affective-playlists enrich --playlist "My Playlist"

# Organize playlists by genre
affective-playlists organize

# Show help
affective-playlists --help

# Show version
affective-playlists --version

# Verbose output
affective-playlists -v
```

## 📁 Project Structure

```
affective_playlists/
├── install.sh              ← ONE-COMMAND SETUP
├── activate.sh             ← Activate environment
├── main.py                 ← CLI entry point
├── setup.py                ← Package setup
├── pyproject.toml          ← Modern Python config
├── requirements.txt        ← All dependencies
├── README.md               ← This file
├── QUICKSTART.md           ← Quick reference
├── .env.example            ← Environment template
│
├── src/                    ← All source code
│   ├── temperament_analyzer.py     ← 4tempers
│   ├── metadata_fill.py             ← metad_enr
│   ├── plsort.py                    ← Playlist organization
│   ├── apple_music.py               ← Shared Apple Music interface
│   ├── config.py                    ← Config management
│   ├── logger.py                    ← Logging
│   ├── normalizer.py                ← Text normalization
│   └── scripts/                     ← AppleScript files
│
├── tests/                  ← Test suite (136+ tests)
│   ├── test_*.py
│   └── ...
│
├── docs/                   ← Documentation
│   ├── rules/             ← Development standards
│   ├── requirements/      ← Feature specifications
│   └── summary/           ← Reports and guides
│
├── data/                   ← Centralized data
│   ├── config/            ← Configuration files
│   ├── logs/              ← Application logs
│   └── cache/             ← Cached metadata
│
└── venv/                   ← Virtual environment (created by install.sh)
```

## 🔧 System Requirements

- **OS**: macOS 10.13+ (for Apple Music integration)
- **Python**: 3.10 or higher
- **Dependencies**: Automatically installed by `install.sh`

## 🎯 Features Overview

### 1. Temperament Analysis (4tempers)
Classifies playlists into emotional categories using AI:
- 🌧️ **Woe** (Melancholic) - Sadness, loneliness, introspection
- ☀️ **Frolic** (Sanguine) - Joy, celebration, energy
- 😰 **Dread** (Phlegmatic) - Fear, tension, anxiety
- 🔥 **Malice** (Choleric) - Rage, aggression, intensity

Uses OpenAI GPT for intelligent classification.

### 2. Metadata Enrichment (metad_enr)
Automatically fills missing metadata using multiple sources:
- **Sources**: MusicBrainz, AcousticBrainz, Discogs, Wikidata, Last.fm
- **Fields**: BPM, Genre, Release Year, Cover Art
- **Strategy**: Per-field enrichment (stops searching once field is found)
- **Smart**: ~50% fewer API calls than traditional approaches

### 3. Playlist Organization (plsort)
Intelligently organizes playlists by genre:
- Hip-Hop, Electronic, Disco/Funk/Soul, Jazz, World, Rock
- Genre detection via track metadata
- One-command organization
- Undo support

## 🧪 Testing

The installation script runs the full test suite (136+ tests). To run manually:

```bash
source activate.sh
pytest tests/ -v
```

Test categories:
- Unit tests for core modules
- Integration tests for workflows
- End-to-end tests
- API mocking
- Edge case coverage

## 📊 Code Quality

All code follows professional Python standards:
- ✓ Type hints on all functions
- ✓ Comprehensive docstrings (Google style)
- ✓ Specific exception handling
- ✓ Centralized logging
- ✓ Proper code organization

See [docs/rules/CODE_QUALITY_STANDARDS.md](docs/rules/CODE_QUALITY_STANDARDS.md) for details.

## 🚀 Development

### Setup for Development
```bash
bash install.sh                    # Install everything
source activate.sh
pip install -e ".[dev]"           # Install dev tools
```

### Development Commands
```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
pylint src/

# Run tests
pytest tests/ -v --cov=src

# Run specific test
pytest tests/test_metadata_fill.py::TestMetadataFiller -v
```

## 🐛 Troubleshooting

### Installation Issues

**Problem: "Python 3 not found"**
```bash
# Install Python 3.10+
brew install python@3.10
# Or download from https://www.python.org
```

**Problem: "Permission denied" on install.sh**
```bash
chmod +x install.sh
bash install.sh
```

**Problem: Venv not activating**
```bash
source venv/bin/activate
export PYTHONPATH="$(pwd):${PYTHONPATH}"
```

### Apple Music Issues

**Problem: "Music.app not accessible"**
1. Open System Preferences → Security & Privacy
2. Grant Terminal Full Disk Access
3. Restart Music.app

**Problem: Playlist not found**
- Check that playlist exists in Apple Music
- Try exact spelling
- The tool uses fuzzy matching for common variations

### API Issues

**Problem: "OPENAI_API_KEY not found"**
```bash
# Check .env file
cat .env

# Ensure it has the key:
OPENAI_API_KEY=sk-your-actual-key
```

**Problem: API rate limits**
- The tool respects rate limits
- Metadata enrichment queues requests automatically
- Wait a few minutes and retry

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Detailed installation
- **[docs/OVERVIEW.md](docs/OVERVIEW.md)** - Architecture overview
- **[docs/requirements/](docs/requirements/)** - Feature specifications
- **[docs/rules/](docs/rules/)** - Development standards

## 🤝 Contributing

1. Clone the repository
2. Run `bash install.sh`
3. Follow [CODE_QUALITY_STANDARDS.md](docs/rules/CODE_QUALITY_STANDARDS.md)
4. Run tests before submitting PRs: `pytest tests/ -v`

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 🙋 Support

Having issues?

1. **Check the docs**: Start with relevant doc in `docs/`
2. **Check the logs**: View `data/logs/` or `temperament_analyzer.log`
3. **Verify configuration**: Review `.env` and `data/config/`
4. **Run with verbose mode**: `affective-playlists -v`
5. **Run tests**: `pytest tests/ -v`

## 🎵 Made for Apple Music Lovers

This tool is specifically designed for Apple Music, providing seamless integration and comprehensive music management features.

---

**Version**: 1.0.0  
**Last Updated**: January 4, 2026  
**Status**: Production Ready ✓

**Happy analyzing! 🎵**
