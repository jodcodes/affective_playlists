from __future__ import annotations

import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .curation_models import AssignmentType, CurationAssignment


def _strip_process_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace").strip()
    return str(value).strip()


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


class AppleMusicStructureApplier:
    def __init__(self, script_path: str | None = None) -> None:
        if script_path is None:
            script_path = str(Path(__file__).parent / "scripts" / "curation_structure.js")
        self.script_path = str(script_path)

    def apply_changes(
        self, changes: Iterable[AppleMusicChange], confirmed: bool
    ) -> dict[str, Any]:
        if not confirmed:
            return {
                "success": False,
                "error": "Confirmation required",
                "applied": 0,
                "failed": 0,
            }

        if not Path(self.script_path).is_file():
            return {
                "success": False,
                "error": f"Script not found: {self.script_path}",
                "applied": 0,
                "failed": 0,
            }

        applied = 0
        failed = 0
        errors: list[dict[str, Any]] = []

        for change in changes:
            command = [
                "osascript",
                "-l",
                "JavaScript",
                self.script_path,
                change.action,
                *change.path,
            ]
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                stdout = _strip_process_output(result.stdout)
                stderr = _strip_process_output(result.stderr)
            except subprocess.TimeoutExpired as exc:
                failed += 1
                errors.append(
                    {
                        "change": change.to_dict(),
                        "stdout": _strip_process_output(exc.output),
                        "stderr": _strip_process_output(exc.stderr) or str(exc),
                    }
                )
                continue
            except OSError as exc:
                failed += 1
                errors.append(
                    {
                        "change": change.to_dict(),
                        "stdout": "",
                        "stderr": str(exc),
                    }
                )
                continue

            if result.returncode == 0 and "SUCCESS" in stdout:
                applied += 1
                continue

            failed += 1
            errors.append(
                {
                    "change": change.to_dict(),
                    "stdout": stdout,
                    "stderr": stderr,
                }
            )

        return {
            "success": failed == 0,
            "applied": applied,
            "failed": failed,
            "errors": errors,
        }
