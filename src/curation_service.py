from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.apple_music import AppleMusicInterface
from src.apple_music_structure import (
    AppleMusicStructureApplier,
    AppleMusicStructurePlanner,
)
from src.curation_models import (
    AssignmentSource,
    AssignmentType,
    CurationAssignment,
    TemperBucket,
)
from src.curation_store import CurationStore


class KeywordTemperClassifier:
    def classify_track(self, track: Dict[str, Any]) -> TemperBucket:
        text = " ".join(
            str(track.get(field) or "") for field in ("name", "artist", "genre")
        ).lower()

        if any(
            keyword in text
            for keyword in ("dark", "dread", "night", "bass", "industrial")
        ):
            return TemperBucket.DREAD
        if any(
            keyword in text for keyword in ("sad", "lonely", "melancholy", "blue")
        ):
            return TemperBucket.WOE
        if any(
            keyword in text for keyword in ("rage", "hard", "aggressive", "drill")
        ):
            return TemperBucket.MALICE
        return TemperBucket.FROLIC


class CurationService:
    def __init__(
        self,
        apple_music: Optional[AppleMusicInterface] = None,
        temper_classifier: Optional[KeywordTemperClassifier] = None,
        store: Optional[CurationStore] = None,
        planner: Optional[AppleMusicStructurePlanner] = None,
        applier: Optional[AppleMusicStructureApplier] = None,
    ) -> None:
        self.apple_music = apple_music or AppleMusicInterface()
        self.temper_classifier = temper_classifier or KeywordTemperClassifier()
        self.store = store or CurationStore()
        self.planner = planner or AppleMusicStructurePlanner()
        self.applier = applier or AppleMusicStructureApplier()

    def preview_fav_songs(self) -> Dict[str, Any]:
        tracks = self.apple_music.get_favourite_tracks()
        assignments: List[CurationAssignment] = []

        for track in tracks:
            raw_genre = str(track.get("genre") or "other").strip() or "other"
            assignments.append(
                CurationAssignment(
                    item_type=AssignmentType.FAV_TRACK,
                    item_id=str(track.get("persistent_id") or track.get("id") or ""),
                    item_name=str(track.get("name") or "Unknown Track"),
                    genre=raw_genre.lower().replace(" ", "_"),
                    temperament=self.temper_classifier.classify_track(track),
                    source=AssignmentSource.AUTO,
                    confidence=0.75,
                )
            )

        assignments = self.store.apply_overrides(assignments)
        changes = self.planner.plan_fav_tracks(assignments)

        return {
            "assignments": [assignment.to_dict() for assignment in assignments],
            "changes": [change.to_dict() for change in changes],
            "total_assignments": len(assignments),
            "total_changes": len(changes),
        }

    def apply_fav_songs(self, confirmed: bool) -> Dict[str, Any]:
        preview = self.preview_fav_songs()
        assignments = [
            CurationAssignment.from_dict(assignment)
            for assignment in preview["assignments"]
        ]
        changes = self.planner.plan_fav_tracks(assignments)
        result = self.applier.apply_changes(changes, confirmed=confirmed)
        result["preview"] = preview
        return result
