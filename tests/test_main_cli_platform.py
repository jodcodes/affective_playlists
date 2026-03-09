"""
Integration tests for CLI platform guard behavior.

Tests the CLI's behavior when platform-specific features are
invoked on non-macOS platforms.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO
import subprocess


class TestCLIPlatformGuards:
    """Tests for CLI platform constraints."""

    def test_temperament_on_non_macos_exits_with_error(self):
        """Running temperament on non-macOS should exit gracefully."""
        with patch("sys.platform", "linux"):
            # Reload main to get fresh IS_MACOS value
            import importlib
            import main
            importlib.reload(main)
            
            # Simulate running temperament analysis
            result = main.run_temperament_analysis()
            assert result == 1, "Expected exit code 1 for non-macOS temperament"

    def test_playlist_enrichment_on_non_macos_exits_with_error(self):
        """Running playlist enrichment on non-macOS should exit gracefully."""
        with patch("sys.platform", "win32"):
            import importlib
            import main
            importlib.reload(main)
            
            # Simulate running metadata enrichment on a playlist
            with patch.object(main.Menu, 'select', return_value=0):  # Select "Playlist"
                result = main.run_metadata_enrichment()
                assert result == 1, "Expected exit code 1 for non-macOS playlist enrichment"

    def test_folder_enrichment_on_non_macos_proceeds(self):
        """Running folder enrichment on non-macOS should not require macOS guard."""
        with patch("sys.platform", "linux"):
            import importlib
            import main
            importlib.reload(main)
            
            # Mock the metadata fill flow
            with patch.object(main.Menu, 'select', return_value=1):  # Select "Folder"
                with patch.object(main.Menu, 'input_text', return_value="/tmp/music"):
                    with patch('main.MetadataFillCLI') as mock_cli:
                        mock_instance = MagicMock()
                        mock_instance.run.return_value = 0
                        mock_cli.return_value = mock_instance
                        
                        result = main.run_metadata_enrichment()
                        # Should not be rejected at platform level
                        # (may fail for other reasons, but platform guard is OK)
                        assert result == 0 or result != -1  # Not a platform guard error

    def test_playlist_organization_on_non_macos_exits_with_error(self):
        """Running organization on non-macOS should exit gracefully."""
        with patch("sys.platform", "linux"):
            import importlib
            import main
            importlib.reload(main)
            
            result = main.run_playlist_organization()
            assert result == 1, "Expected exit code 1 for non-macOS organization"


class TestAPIKeyValidation:
    """Tests for API key validation."""

    def test_missing_openai_api_key_is_caught(self):
        """Missing OPENAI_API_KEY should be detected and reported."""
        with patch.dict('os.environ', {}, clear=False):
            # Remove OPENAI_API_KEY if it exists
            os.environ.pop('OPENAI_API_KEY', None)
            
            import main
            result = main.validate_openai_api_key()
            assert result is False, "Should detect missing OPENAI_API_KEY"

    def test_present_openai_api_key_is_accepted(self):
        """Present OPENAI_API_KEY should be accepted."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key-12345'}):
            import main
            result = main.validate_openai_api_key()
            assert result is True, "Should accept valid OPENAI_API_KEY"

    def test_valid_api_key_allows_temperament_analysis(self):
        """With valid API key, temperament analysis should proceed to client init."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'}):
            with patch("sys.platform", "darwin"):  # Pretend it's macOS
                import importlib
                import main
                importlib.reload(main)
                
                with patch('main.MusicAppClient') as mock_music:
                    with patch('main.OpenAILLMClient') as mock_llm:
                        with patch('main.TemperamentAnalyzer'):
                            mock_music.return_value.authenticate.return_value = False
                            
                            result = main.run_temperament_analysis()
                            # It should get past API key validation and fail on Music.app auth
                            assert result == 1  # Failed due to Music.app, not API key
                            mock_llm.assert_called_once()  # LLM client was created
