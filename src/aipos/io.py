from __future__ import annotations

import json
from pathlib import Path

import yaml

from .engine import WorkflowError, validate_workflow
from .models import AgentRegistry, ProjectState, TaskDefinition, TaskStatus
from .registry import RegistryError, agent_from_mapping, validate_agent_registry


def load_workflow(path: str | Path, registry: AgentRegistry | None = None) -> list[TaskDefinition]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise WorkflowError("Workflow file must contain a tasks list")

    tasks = [_task_from_mapping(item) for item in data["tasks"]]
    validate_workflow(tasks, registry)
    return tasks


def load_agent_registry(path: str | Path) -> AgentRegistry:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list):
        raise RegistryError("Agent registry file must contain an agents list")
    agents = [agent_from_mapping(item) for item in data["agents"]]
    return validate_agent_registry(agents)


def _task_from_mapping(item: object) -> TaskDefinition:
    if not isinstance(item, dict):
        raise WorkflowError("Workflow task entries must be mappings")
    missing = [field for field in ("id", "agent", "outputs") if field not in item]
    if missing:
        raise WorkflowError(f"Workflow task is missing required fields: {missing}")
    return TaskDefinition(
        id=item["id"],
        agent=item["agent"],
        description=item.get("description", ""),
        depends_on=tuple(item.get("depends_on", [])),
        outputs=tuple(item.get("outputs", [])),
        approval_required=bool(item.get("approval_required", False)),
    )


def load_state(path: str | Path) -> ProjectState:
    state_path = Path(path)
    if not state_path.exists():
        return ProjectState()
    raw = json.loads(state_path.read_text(encoding="utf-8"))
    return ProjectState({key: TaskStatus(value) for key, value in raw.get("statuses", {}).items()})


def save_state(path: str | Path, state: ProjectState) -> None:
    payload = {"statuses": {key: value.value for key, value in sorted(state.statuses.items())}}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
