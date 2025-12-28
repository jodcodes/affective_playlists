#!/usr/bin/env python3
"""
plMetaTemp - Unified CLI Entry Point

Main entry point for the plMetaTemp project, which unifies three subprojects:
1. 4tempers - AI-based playlist temperament analysis
2. metad_enr - Metadata filling and enrichment
3. plsort - Playlist organization and classification

This CLI provides an interactive menu to select and run any of the three subprojects.

Usage:
    python main.py              # Interactive menu
    python main.py --help       # Show help
    python main.py 4tempers     # Run 4tempers directly
    python main.py metad_enr    # Run metad_enr directly
    python main.py plsort       # Run plsort directly
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_subrepo_entry_point(subrepo: str) -> Optional[str]:
    """Get the entry point script for a subrepo."""
    entry_points = {
        '4tempers': 'temperament_analyzer.py',
        'metad_enr': '__main__.py',
        'plsort': 'plsort.py',
    }
    return entry_points.get(subrepo)


def run_subrepo(subrepo: str, args: list = None) -> int:
    """
    Run a subrepo with given arguments.
    
    Args:
        subrepo: Name of the subrepo ('4tempers', 'metad_enr', or 'plsort')
        args: Command-line arguments to pass to the subrepo
        
    Returns:
        Exit code from the subrepo
    """
    if subrepo not in ['4tempers', 'metad_enr', 'plsort']:
        print(f"ERROR: Unknown subrepo '{subrepo}'")
        print(f"Available subrepos: 4tempers, metad_enr, plsort")
        return 1
    
    subrepo_path = PROJECT_ROOT / subrepo
    if not subrepo_path.exists():
        print(f"ERROR: Subrepo directory not found: {subrepo_path}")
        return 1
    
    entry_point = get_subrepo_entry_point(subrepo)
    if not entry_point:
        print(f"ERROR: No entry point found for subrepo '{subrepo}'")
        return 1
    
    script_path = subrepo_path / entry_point
    if not script_path.exists():
        print(f"ERROR: Entry point not found: {script_path}")
        return 1
    
    # Build command
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*70}")
    print(f"Running: {subrepo.upper()}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, cwd=str(subrepo_path))
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"ERROR: Failed to run subrepo: {e}")
        return 1


def show_subrepo_arguments(subrepo: str) -> None:
    """Show available arguments for a subrepo."""
    arguments = {
        '4tempers': [
            "--help              Show help message",
            "--llm MODEL          Specify LLM model (default: gpt-4o-mini)",
            "--metadata SOURCE    Metadata source: spotify, musicbrainz, mock (default: mock)",
            "--output FILE        Save results to JSON file",
            "--log-level LEVEL    Logging level: DEBUG, INFO, WARNING, ERROR",
        ],
        'metad_enr': [
            "--help               Show help message",
            "--playlist NAME      Process single playlist by name",
            "--folder PATH        Process music folder",
            "--dry-run            Dry-run mode (default)",
            "--execute            Execute and write metadata",
            "--database SOURCE    Priority: musicbrainz, acousticbrainz, discogs, wikidata, lastfm",
            "--output FILE        Export results to JSON",
        ],
        'plsort': [
            "--help               Show help message",
            "--dry-run            Dry-run mode (default - don't modify)",
            "--execute            Execute and move playlists in Apple Music",
            "--verbose, -v        Enable verbose logging",
            "--playlist NAME      Process single playlist by name",
            "--enrich SOURCES     Enrich data from web (musicbrainz, lastfm, discogs, rym)",
            "--export FILE        Export results to JSON file",
            "--config-dir PATH    Configuration directory (default: config)",
        ],
    }
    
    if subrepo in arguments:
        print(f"\nAvailable arguments for {subrepo}:\n")
        for arg in arguments[subrepo]:
            print(f"  {arg}")


def show_interactive_menu() -> int:
    """Show interactive menu to select and run a subrepo."""
    print("\n" + "="*70)
    print("plMetaTemp - Unified Music Analysis & Organization")
    print("="*70)
    print("\nSelect a subproject to run:\n")
    
    subrepos = [
        ("4tempers", "🎵 AI-based Playlist Temperament Analysis"),
        ("metad_enr", "📝 Metadata Filling and Enrichment"),
        ("plsort", "📁 Playlist Organization and Classification"),
    ]
    
    for i, (name, description) in enumerate(subrepos, 1):
        print(f"{i}. {name:<12} - {description}")
    
    print("\n0. Exit")
    print("\n" + "-"*70)
    
    while True:
        try:
            choice = input("Enter your choice (0-3): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("Goodbye!")
                return 0
            
            if 1 <= choice_num <= len(subrepos):
                selected_subrepo = subrepos[choice_num - 1][0]
                
                # Show available arguments
                show_subrepo_arguments(selected_subrepo)
                
                # Ask for additional arguments
                print(f"\n(Tip: Use --help to see full help message)")
                print(f"\nCommon arguments for {selected_subrepo}:")
                if selected_subrepo == 'plsort':
                    print("  --dry-run   Don't modify Apple Music (default)")
                    print("  --execute   Actually move playlists (requires confirmation)")
                    print("  --verbose   Show detailed logging output")
                elif selected_subrepo == 'metad_enr':
                    print("  --dry-run   Preview changes without writing (default)")
                    print("  --execute   Write metadata to audio files")
                    print("  --playlist  Process specific playlist")
                elif selected_subrepo == '4tempers':
                    print("  --metadata  Data source (spotify, musicbrainz, mock)")
                    print("  --output    Save results to JSON file")
                
                args_input = input(f"\nEnter additional arguments (or press Enter for default behavior): ").strip()
                args = args_input.split() if args_input else []
                
                return run_subrepo(selected_subrepo, args)
            else:
                print(f"Invalid choice. Please enter 0-{len(subrepos)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            return 130


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="plMetaTemp - Unified Music Analysis & Organization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'subrepo',
        nargs='?',
        choices=['4tempers', 'metad_enr', 'plsort'],
        help='Subrepo to run (if not specified, shows interactive menu)'
    )
    
    parser.add_argument(
        'args',
        nargs=argparse.REMAINDER,
        help='Arguments to pass to the subrepo'
    )
    
    parser.add_argument(
        '--help-4tempers',
        action='store_true',
        help='Show help for 4tempers'
    )
    
    parser.add_argument(
        '--help-metad_enr',
        action='store_true',
        help='Show help for metad_enr'
    )
    
    parser.add_argument(
        '--help-plsort',
        action='store_true',
        help='Show help for plsort'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available subrepos'
    )
    
    # Custom parsing to handle subrepo-specific help
    args, remaining = parser.parse_known_args()
    
    # Handle list command
    if args.list:
        print("\nAvailable subrepos:\n")
        print("1. 4tempers")
        print("   - AI-based Playlist Temperament Analysis")
        print("   - Uses OpenAI GPT to classify playlists")
        print("")
        print("2. metad_enr")
        print("   - Metadata Filling and Enrichment")
        print("   - Fills missing metadata from external databases")
        print("")
        print("3. plsort")
        print("   - Playlist Organization and Classification")
        print("   - Organizes playlists by genre")
        return 0
    
    # Handle subrepo-specific help
    if args.help_4tempers:
        return run_subrepo('4tempers', ['--help'])
    if args.help_metad_enr:
        return run_subrepo('metad_enr', ['--help'])
    if args.help_plsort:
        return run_subrepo('plsort', ['--help'])
    
    # If subrepo specified, run it
    if args.subrepo:
        return run_subrepo(args.subrepo, remaining)
    
    # Otherwise show interactive menu
    return show_interactive_menu()


if __name__ == '__main__':
    sys.exit(main())
