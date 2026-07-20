from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True)
class TaskDefinition:
    id: str
    agent: str
    description: str
    depends_on: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    approval_required: bool = False


@dataclass
class ProjectState:
    statuses: dict[str, TaskStatus] = field(default_factory=dict)

    def status_of(self, task_id: str) -> TaskStatus:
        return self.statuses.get(task_id, TaskStatus.PENDING)
