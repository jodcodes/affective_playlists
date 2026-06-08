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

    @patch.object(AppleMusicInterface, "_run_applescript")
    def test_get_favourite_tracks_normalizes_track_identity(self, mock_run):
        captured = {}

        def fake_run(script):
            captured["script"] = script
            return (
                True,
                "{title:Track A, artist:Artist A, genre:Hip-Hop, persistent_id:ABC123}",
            )

        mock_run.side_effect = fake_run

        result = self.client.get_favourite_tracks()

        script = " ".join(captured["script"].split())
        self.assertIn(
            "set trackInfo to {title:name of trk, name:name of trk, "
            "persistent_id:persistent ID of trk, artist:artist of trk, "
            "album:album of trk, genre:genre of trk, bpm:bpm of trk, "
            "year:year of trk, composer:composer of trk, duration:duration of trk}",
            script,
        )
        self.assertEqual(result[0]["title"], "Track A")
        self.assertEqual(result[0]["name"], "Track A")
        self.assertEqual(result[0]["persistent_id"], "ABC123")


if __name__ == "__main__":
    unittest.main()
