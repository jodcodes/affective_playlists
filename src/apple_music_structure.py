from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from .curation_models import AssignmentType, CurationAssignment


@dataclass(frozen=True)
class AppleMusicChange:
    action: str
    path: Sequence[str]
    description: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", tuple(self.path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "path": list(self.path),
            "description": self.description,
        }


class AppleMusicStructurePlanner:
    def plan_fav_tracks(
        self, assignments: Iterable[CurationAssignment]
    ) -> list[AppleMusicChange]:
        changes: list[AppleMusicChange] = []
        seen: set[tuple[str, tuple[str, ...]]] = set()

        def add_change(action: str, path: Sequence[str], description: str) -> None:
            key = (action, tuple(path))
            if key in seen:
                return
            seen.add(key)
            changes.append(AppleMusicChange(action, path, description))

        for assignment in assignments:
            if assignment.item_type != AssignmentType.FAV_TRACK:
                continue

            root, genre_folder, playlist_name = assignment.target_path()
            add_change("ensure_folder", [root], f"Ensure folder {root}")
            add_change(
                "ensure_folder",
                [root, genre_folder],
                f"Ensure folder {root} / {genre_folder}",
            )
            add_change(
                "ensure_playlist",
                [root, genre_folder, playlist_name],
                f"Ensure playlist {playlist_name}",
            )
            add_change(
                "copy_track",
                [assignment.item_id, root, genre_folder, playlist_name],
                f"Copy {assignment.item_name} to {playlist_name}",
            )

        return changes
