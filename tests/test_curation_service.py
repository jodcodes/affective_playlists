from src.curation_models import (
    AssignmentSource,
    AssignmentType,
    CurationAssignment,
    TemperBucket,
)
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
