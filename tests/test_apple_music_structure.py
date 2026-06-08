from src.apple_music_structure import AppleMusicChange, AppleMusicStructurePlanner
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
