#!/usr/bin/env python3
"""
affective_playlists - Unified CLI Entry Point

Unified application that combines:
1. 4tempers - AI-based playlist temperament analysis
2. metad_enr - Metadata filling and enrichment
3. plsort - Playlist organization and classification

Usage:
    python main.py                    # Interactive menu
    python main.py --help             # Show help
    python main.py temperament        # Run temperament analysis
    python main.py enrich             # Run metadata enrichment
    python main.py organize           # Run playlist organization
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from logger import setup_logger
from apple_music import AppleMusicInterface
from normalizer import TextNormalizer
from config import load_centralized_whitelist

# Import main modules
try:
    from temperament_analyzer import TemperamentAnalyzer
    from metadata_fill import MetadataFiller
    from plsort import PlaylistSorter
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")

logger = setup_logger("affective_playlists")


def run_temperament_analysis(args=None):
    """Run 4tempers - AI temperament analysis."""
    print("\n" + "="*70)
    print("🎵 TEMPERAMENT ANALYSIS - AI-based Playlist Emotion Classification")
    print("="*70 + "\n")
    
    try:
        analyzer = TemperamentAnalyzer()
        analyzer.run()
    except Exception as e:
        logger.error(f"Temperament analysis failed: {e}")
        return 1
    return 0


def run_metadata_enrichment(args=None):
    """Run metad_enr - metadata enrichment."""
    print("\n" + "="*70)
    print("📝 METADATA ENRICHMENT - Fill Missing Audio Metadata")
    print("="*70 + "\n")
    
    try:
        enricher = MetadataFiller()
        enricher.run()
    except Exception as e:
        logger.error(f"Metadata enrichment failed: {e}")
        return 1
    return 0


def run_playlist_organization(args=None):
    """Run plsort - playlist organization by genre."""
    print("\n" + "="*70)
    print("📁 PLAYLIST ORGANIZATION - Classify & Organize by Genre")
    print("="*70 + "\n")
    
    try:
        sorter = PlaylistSorter()
        sorter.run()
    except Exception as e:
        logger.error(f"Playlist organization failed: {e}")
        return 1
    return 0


def show_interactive_menu():
    """Show interactive menu to select and run a feature."""
    print("\n" + "="*70)
    print("affective_playlists - Unified Music Analysis & Organization")
    print("="*70)
    print("\nSelect a feature to run:\n")
    
    features = [
        ("1", "temperament", "🎵 AI-based Playlist Temperament Analysis"),
        ("2", "enrich", "📝 Metadata Filling and Enrichment"),
        ("3", "organize", "📁 Playlist Organization and Classification"),
    ]
    
    for num, name, description in features:
        print(f"  {num}. {description}")
    
    print("\n  0. Exit\n")
    print("-"*70)
    
    while True:
        try:
            choice = input("\nEnter your choice (0-3): ").strip()
            
            if choice == "0":
                print("\nGoodbye! 👋\n")
                return 0
            elif choice == "1":
                return run_temperament_analysis()
            elif choice == "2":
                return run_metadata_enrichment()
            elif choice == "3":
                return run_playlist_organization()
            else:
                print("Invalid choice. Please enter 0-3.")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye! 👋\n")
            return 130


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="affective_playlists",
        description="Unified music analysis and organization tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "feature",
        nargs="?",
        choices=["temperament", "enrich", "organize"],
        help="Feature to run (if not specified, shows interactive menu)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel("DEBUG")
    
    # Run selected feature
    if args.feature == "temperament":
        return run_temperament_analysis()
    elif args.feature == "enrich":
        return run_metadata_enrichment()
    elif args.feature == "organize":
        return run_playlist_organization()
    else:
        # Show interactive menu if no feature specified
        return show_interactive_menu()


if __name__ == "__main__":
    sys.exit(main())
