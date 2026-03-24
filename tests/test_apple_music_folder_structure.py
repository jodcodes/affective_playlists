import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from apple_music import AppleMusicInterface


class TestAppleMusicFolderStructure(unittest.TestCase):
    def setUp(self):
        self.client = AppleMusicInterface()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")

    def _read_fixture(self, name: str) -> str:
        path = os.path.join(self.fixture_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @patch.object(AppleMusicInterface, "_run_applescript")
    def test_get_playlist_folder_structure_valid(self, mock_run):
        mock_run.return_value = (True, self._read_fixture("apple_music_folder_structure_valid.txt"))

        result = self.client.get_playlist_folder_structure()

        self.assertEqual(
            result,
            {
                "Focus": ["Morning Chill", "Late Night Mix"],
                "Workout": ["Cardio Hits"],
                "Empty Folder": [],
            },
        )

    @patch.object(AppleMusicInterface, "_run_applescript")
    def test_get_playlist_folder_structure_empty(self, mock_run):
        mock_run.return_value = (True, "")

        result = self.client.get_playlist_folder_structure()

        self.assertEqual(result, {})

    @patch.object(AppleMusicInterface, "_run_applescript")
    def test_get_playlist_folder_structure_malformed(self, mock_run):
        mock_run.return_value = (
            True,
            self._read_fixture("apple_music_folder_structure_malformed.txt"),
        )

        result = self.client.get_playlist_folder_structure()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
