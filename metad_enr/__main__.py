"""
Metadata Fill/Enrichment Tool - __main__ entry point

Allows the module to be run as:
    python -m metad_fill --playlist "Favorites"
    python -m metad_fill --folder "/path/to/music"
"""

import sys
from src.metadata_fill import main

if __name__ == '__main__':
    main()
