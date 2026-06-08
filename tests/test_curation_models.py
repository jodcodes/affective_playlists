from src.curation_models import (
    AssignmentSource,
    AssignmentType,
    CurationAssignment,
    TemperBucket,
    fav_playlist_name,
    normalize_genre_label,
)


def test_normalize_genre_label_keeps_short_names_readable():
    assert normalize_genre_label("hiphop") == "Hiphop"
    assert normalize_genre_label("disco_funk_soul") == "Disco Funk Soul"
    assert normalize_genre_label("Electronic") == "Electronic"


def test_fav_playlist_name_uses_requested_format():
    assert fav_playlist_name("hiphop", TemperBucket.FROLIC) == "Fav Hiphop Frolic"
    assert fav_playlist_name("electronic", TemperBucket.DREAD) == "Fav Electronic Dread"


def test_assignment_serializes_for_api():
    assignment = CurationAssignment(
        item_type=AssignmentType.FAV_TRACK,
        item_id="track-1",
        item_name="Track A",
        genre="hiphop",
        temperament=TemperBucket.FROLIC,
        source=AssignmentSource.AUTO,
        confidence=0.91,
    )

    assert assignment.to_dict() == {
        "item_type": "fav_track",
        "item_id": "track-1",
        "item_name": "Track A",
        "genre": "hiphop",
        "genre_label": "Hiphop",
        "temperament": "Frolic",
        "source": "auto",
        "confidence": 0.91,
        "manual_override": False,
        "target_path": ["Fav Songs", "Hiphop", "Fav Hiphop Frolic"],
    }
