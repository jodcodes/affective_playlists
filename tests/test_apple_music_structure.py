import shutil
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.apple_music_structure import (
    AppleMusicChange,
    AppleMusicStructureApplier,
    AppleMusicStructurePlanner,
)
from src.curation_models import (
    AssignmentSource,
    AssignmentType,
    CurationAssignment,
    TemperBucket,
)


def fav_assignment(track_id: str, genre: str, temper: TemperBucket) -> CurationAssignment:
    return CurationAssignment(
        item_type=AssignmentType.FAV_TRACK,
        item_id=track_id,
        item_name=f"Track {track_id}",
        genre=genre,
        temperament=temper,
        source=AssignmentSource.AUTO,
        confidence=0.8,
    )


def playlist_assignment(item_id: str, genre: str, temper: TemperBucket) -> CurationAssignment:
    return CurationAssignment(
        item_type=AssignmentType.PLAYLIST,
        item_id=item_id,
        item_name=f"Playlist {item_id}",
        genre=genre,
        temperament=temper,
        source=AssignmentSource.AUTO,
        confidence=0.8,
    )


def test_change_to_dict_returns_path_copy():
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    payload = change.to_dict()
    payload["path"].append("Mutated")

    assert payload["path"] == ["Fav Songs", "Mutated"]
    assert change.path == ("Fav Songs",)


def test_plan_creates_fav_folder_genre_folder_playlist_and_copy():
    planner = AppleMusicStructurePlanner()
    changes = planner.plan_fav_tracks(
        [fav_assignment("1", "hiphop", TemperBucket.FROLIC)]
    )

    assert AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs") in changes
    assert AppleMusicChange(
        "ensure_folder", ["Fav Songs", "Hiphop"], "Ensure folder Fav Songs / Hiphop"
    ) in changes
    assert AppleMusicChange(
        "ensure_playlist",
        ["Fav Songs", "Hiphop", "Fav Hiphop Frolic"],
        "Ensure playlist Fav Hiphop Frolic",
    ) in changes
    assert AppleMusicChange(
        "copy_track",
        ["1", "Fav Songs", "Hiphop", "Fav Hiphop Frolic"],
        "Copy Track 1 to Fav Hiphop Frolic",
    ) in changes


def test_plan_deduplicates_folder_and_playlist_changes():
    planner = AppleMusicStructurePlanner()
    changes = planner.plan_fav_tracks(
        [
            fav_assignment("1", "hiphop", TemperBucket.FROLIC),
            fav_assignment("2", "hiphop", TemperBucket.FROLIC),
        ]
    )

    ensure_playlist = [c for c in changes if c.action == "ensure_playlist"]
    copy_track = [c for c in changes if c.action == "copy_track"]

    assert len(ensure_playlist) == 1
    assert len(copy_track) == 2


def test_plan_ignores_non_fav_track_assignments():
    planner = AppleMusicStructurePlanner()

    changes = planner.plan_fav_tracks(
        [playlist_assignment("playlist-1", "hiphop", TemperBucket.FROLIC)]
    )

    assert changes == []


def test_plan_deduplicates_structural_changes_but_keeps_distinct_track_copies():
    planner = AppleMusicStructurePlanner()
    changes = planner.plan_fav_tracks(
        [
            fav_assignment("1", "hiphop", TemperBucket.FROLIC),
            fav_assignment("2", "hiphop", TemperBucket.FROLIC),
        ]
    )

    ensure_root_folder = [
        c for c in changes if c.action == "ensure_folder" and c.path == ("Fav Songs",)
    ]
    ensure_genre_folder = [
        c
        for c in changes
        if c.action == "ensure_folder" and c.path == ("Fav Songs", "Hiphop")
    ]
    ensure_playlist = [c for c in changes if c.action == "ensure_playlist"]
    copy_track = [c for c in changes if c.action == "copy_track"]

    assert len(ensure_root_folder) == 1
    assert len(ensure_genre_folder) == 1
    assert len(ensure_playlist) == 1
    assert len(copy_track) == 2


def test_applier_rejects_without_confirmation(tmp_path):
    script_path = tmp_path / "curation_structure.js"
    script_path.write_text("// test script", encoding="utf-8")
    applier = AppleMusicStructureApplier(script_path=str(script_path))
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    with patch("src.apple_music_structure.subprocess.run") as run:
        result = applier.apply_changes([change], confirmed=False)

    run.assert_not_called()
    assert result["success"] is False
    assert result["error"] == "Confirmation required"
    assert result["applied"] == 0
    assert result["failed"] == 0


def test_applier_runs_confirmed_changes_with_jxa(tmp_path):
    script_path = tmp_path / "curation_structure.js"
    script_path.write_text("// test script", encoding="utf-8")
    applier = AppleMusicStructureApplier(script_path=str(script_path))
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    with patch("src.apple_music_structure.subprocess.run") as run:
        run.return_value = SimpleNamespace(returncode=0, stdout="SUCCESS", stderr="")
        result = applier.apply_changes([change], confirmed=True)

    run.assert_called_once_with(
        [
            "osascript",
            "-l",
            "JavaScript",
            str(script_path),
            "ensure_folder",
            "Fav Songs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result["success"] is True
    assert result["applied"] == 1
    assert result["failed"] == 0


def test_applier_records_subprocess_failures(tmp_path):
    script_path = tmp_path / "curation_structure.js"
    script_path.write_text("// test script", encoding="utf-8")
    applier = AppleMusicStructureApplier(script_path=str(script_path))
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    with patch("src.apple_music_structure.subprocess.run") as run:
        run.return_value = SimpleNamespace(
            returncode=1,
            stdout="partial output\n",
            stderr="failed to create folder\n",
        )
        result = applier.apply_changes([change], confirmed=True)

    assert result["success"] is False
    assert result["applied"] == 0
    assert result["failed"] == 1
    assert result["errors"] == [
        {
            "change": change.to_dict(),
            "stdout": "partial output",
            "stderr": "failed to create folder",
        }
    ]


def test_applier_records_timeout_failures(tmp_path):
    script_path = tmp_path / "curation_structure.js"
    script_path.write_text("// test script", encoding="utf-8")
    applier = AppleMusicStructureApplier(script_path=str(script_path))
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    with patch("src.apple_music_structure.subprocess.run") as run:
        run.side_effect = subprocess.TimeoutExpired(
            cmd=["osascript"],
            timeout=120,
            output="partial output\n",
            stderr="timed out\n",
        )
        result = applier.apply_changes([change], confirmed=True)

    assert result["success"] is False
    assert result["applied"] == 0
    assert result["failed"] == 1
    assert result["errors"] == [
        {
            "change": change.to_dict(),
            "stdout": "partial output",
            "stderr": "timed out",
        }
    ]


def test_applier_records_os_errors(tmp_path):
    script_path = tmp_path / "curation_structure.js"
    script_path.write_text("// test script", encoding="utf-8")
    applier = AppleMusicStructureApplier(script_path=str(script_path))
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    with patch("src.apple_music_structure.subprocess.run") as run:
        run.side_effect = OSError("osascript unavailable")
        result = applier.apply_changes([change], confirmed=True)

    assert result["success"] is False
    assert result["applied"] == 0
    assert result["failed"] == 1
    assert result["errors"] == [
        {
            "change": change.to_dict(),
            "stdout": "",
            "stderr": "osascript unavailable",
        }
    ]


def test_applier_reports_missing_script_and_rejects_directories(tmp_path):
    script_path = tmp_path / "script_directory"
    script_path.mkdir()
    applier = AppleMusicStructureApplier(script_path=str(script_path))
    change = AppleMusicChange("ensure_folder", ["Fav Songs"], "Ensure folder Fav Songs")

    with patch("src.apple_music_structure.subprocess.run") as run:
        result = applier.apply_changes([change], confirmed=True)

    run.assert_not_called()
    assert result["success"] is False
    assert result["error"].startswith("Script not found:")
    assert result["applied"] == 0
    assert result["failed"] == 0


def test_curation_structure_no_arg_guard_returns_fast_error():
    if shutil.which("osascript") is None:
        pytest.skip("osascript is not available")

    result = subprocess.run(
        [
            "osascript",
            "-l",
            "JavaScript",
            "src/scripts/curation_structure.js",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "ERROR: action and path required"
