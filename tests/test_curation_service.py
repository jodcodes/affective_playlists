from src.curation_models import (
    AssignmentSource,
    AssignmentType,
    CurationAssignment,
    TemperBucket,
)
from src.apple_music import AppleMusicInterface
from src.curation_service import CurationService
from src.curation_store import CurationStore


class FakeAppleMusic:
    def get_favourite_tracks(self):
        return [
            {
                "persistent_id": "track-1",
                "name": "Track A",
                "artist": "Artist A",
                "genre": "Hip-Hop",
            },
            {
                "persistent_id": "track-2",
                "name": "Track B",
                "artist": "Artist B",
                "genre": "Electronic",
            },
        ]


class FakeTemperClassifier:
    def classify_track(self, track):
        return (
            TemperBucket.FROLIC
            if track["persistent_id"] == "track-1"
            else TemperBucket.DREAD
        )


class StaticTemperClassifier:
    def classify_track(self, track):
        return TemperBucket.FROLIC


class FakeApplier:
    def __init__(self):
        self.calls = []

    def apply_changes(self, changes, confirmed):
        changes = list(changes)
        self.calls.append((changes, confirmed))
        return {
            "success": False,
            "applied": 0,
            "failed": 0,
            "confirmed": confirmed,
        }


class AppleMusicLikeTracks:
    def get_favourite_tracks(self):
        return [
            {
                "persistent_id": "apple-track-1",
                "title": "Apple Title",
                "artist": "Apple Artist",
                "genre": "Alt-Rock",
            }
        ]


class TracksWithMissingId:
    def get_favourite_tracks(self):
        return [
            {
                "persistent_id": "track-1",
                "title": "Track With ID",
                "artist": "Artist A",
                "genre": "Hip-Hop",
            },
            {
                "title": "Track Without ID",
                "artist": "Artist B",
                "genre": "Electronic",
            },
        ]


class FakeAppleMusicInterface(AppleMusicInterface):
    def __init__(self):
        self.requested_playlists = []

    def get_playlist_tracks(self, playlist_name):
        self.requested_playlists.append(playlist_name)
        return [{"title": "Track A", "persistent_id": "track-a"}]


def test_fav_preview_builds_assignments_and_changes():
    service = CurationService(
        apple_music=FakeAppleMusic(),
        temper_classifier=FakeTemperClassifier(),
    )

    preview = service.preview_fav_songs()

    targets = [a["target_path"] for a in preview["assignments"]]
    assert ["Fav Songs", "Hip Hop", "Fav Hip Hop Frolic"] in targets
    assert ["Fav Songs", "Electronic", "Fav Electronic Dread"] in targets
    assert preview["changes"][0]["action"] == "ensure_folder"


def test_fav_preview_uses_title_for_apple_music_track_names():
    service = CurationService(
        apple_music=AppleMusicLikeTracks(),
        temper_classifier=StaticTemperClassifier(),
    )

    preview = service.preview_fav_songs()

    assert preview["assignments"][0]["item_name"] == "Apple Title"
    assert preview["assignments"][0]["target_path"] == [
        "Fav Songs",
        "Alt Rock",
        "Fav Alt Rock Frolic",
    ]


def test_fav_preview_skips_tracks_without_stable_id_and_reports_them():
    service = CurationService(
        apple_music=TracksWithMissingId(),
        temper_classifier=StaticTemperClassifier(),
    )

    preview = service.preview_fav_songs()

    assert preview["total_assignments"] == 1
    assert preview["total_skipped"] == 1
    assert preview["skipped_tracks"] == [
        {
            "name": "Track Without ID",
            "artist": "Artist B",
            "genre": "Electronic",
            "reason": "missing_stable_id",
        }
    ]
    assert all(
        change["path"][0] != ""
        for change in preview["changes"]
        if change["action"] == "copy_track"
    )


def test_get_favourite_tracks_delegates_to_favourite_songs_playlist():
    apple_music = FakeAppleMusicInterface()

    tracks = apple_music.get_favourite_tracks()

    assert apple_music.requested_playlists == ["Favourite Songs"]
    assert tracks == [
        {"title": "Track A", "persistent_id": "track-a", "name": "Track A"}
    ]


def test_apply_fav_songs_delegates_to_applier_and_attaches_preview():
    applier = FakeApplier()
    service = CurationService(
        apple_music=FakeAppleMusic(),
        temper_classifier=FakeTemperClassifier(),
        applier=applier,
    )

    result = service.apply_fav_songs(confirmed=False)

    assert applier.calls
    changes, confirmed = applier.calls[0]
    assert confirmed is False
    assert changes[0].action == "ensure_folder"
    assert result["preview"]["total_assignments"] == 2
    assert result["preview"]["total_changes"] == len(changes)


def test_fav_preview_applies_store_overrides_over_auto_assignments(tmp_path):
    store = CurationStore(tmp_path / "assignments.json")
    store.save_override(
        CurationAssignment(
            item_type=AssignmentType.FAV_TRACK,
            item_id="track-1",
            item_name="Track A",
            genre="ambient",
            temperament=TemperBucket.WOE,
            source=AssignmentSource.MANUAL,
            confidence=1.0,
            manual_override=True,
        )
    )
    service = CurationService(
        apple_music=FakeAppleMusic(),
        temper_classifier=FakeTemperClassifier(),
        store=store,
    )

    preview = service.preview_fav_songs()

    overridden = next(a for a in preview["assignments"] if a["item_id"] == "track-1")
    assert overridden["target_path"] == ["Fav Songs", "Ambient", "Fav Ambient Woe"]
    assert overridden["source"] == "manual"
    assert overridden["manual_override"] is True
