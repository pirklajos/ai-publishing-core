from __future__ import annotations

import json
from pathlib import Path

import yaml

from .models import ProjectState, TaskDefinition, TaskStatus


def load_workflow(path: str | Path) -> list[TaskDefinition]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [
        TaskDefinition(
            id=item["id"],
            agent=item["agent"],
            description=item.get("description", ""),
            depends_on=tuple(item.get("depends_on", [])),
            outputs=tuple(item.get("outputs", [])),
            approval_required=bool(item.get("approval_required", False)),
        )
        for item in data["tasks"]
    ]


def load_state(path: str | Path) -> ProjectState:
    state_path = Path(path)
    if not state_path.exists():
        return ProjectState()
    raw = json.loads(state_path.read_text(encoding="utf-8"))
    return ProjectState({key: TaskStatus(value) for key, value in raw.get("statuses", {}).items()})


def save_state(path: str | Path, state: ProjectState) -> None:
    payload = {"statuses": {key: value.value for key, value in sorted(state.statuses.items())}}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
