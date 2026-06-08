from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


FAV_ROOT_FOLDER = "Fav Songs"


class TemperBucket(Enum):
    WOE = "Woe"
    FROLIC = "Frolic"
    DREAD = "Dread"
    MALICE = "Malice"


class AssignmentType(Enum):
    PLAYLIST = "playlist"
    FAV_TRACK = "fav_track"


class AssignmentSource(Enum):
    AUTO = "auto"
    MANUAL = "manual"


def normalize_genre_label(genre: str) -> str:
    parts = genre.replace("_", " ").replace("-", " ").strip().split()
    if not parts:
        return "Other"
    return " ".join(part.capitalize() for part in parts)


def fav_playlist_name(genre: str, temperament: TemperBucket) -> str:
    return f"Fav {normalize_genre_label(genre)} {temperament.value}"


@dataclass(frozen=True)
class CurationAssignment:
    item_type: AssignmentType
    item_id: str
    item_name: str
    genre: str
    temperament: TemperBucket
    source: AssignmentSource
    confidence: float
    manual_override: bool = False

    def target_path(self) -> list[str]:
        genre_label = normalize_genre_label(self.genre)
        if self.item_type == AssignmentType.FAV_TRACK:
            return [
                FAV_ROOT_FOLDER,
                genre_label,
                fav_playlist_name(self.genre, self.temperament),
            ]
        return [genre_label, self.temperament.value]

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_type": self.item_type.value,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "genre": self.genre,
            "genre_label": normalize_genre_label(self.genre),
            "temperament": self.temperament.value,
            "source": self.source.value,
            "confidence": round(self.confidence, 4),
            "manual_override": self.manual_override,
            "target_path": self.target_path(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CurationAssignment:
        return cls(
            item_type=AssignmentType(data["item_type"]),
            item_id=data["item_id"],
            item_name=data["item_name"],
            genre=data["genre"],
            temperament=TemperBucket(data["temperament"]),
            source=AssignmentSource(data["source"]),
            confidence=float(data["confidence"]),
            manual_override=bool(data.get("manual_override", False)),
        )
