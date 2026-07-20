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


@dataclass(frozen=True)
class ArtifactContract:
    path: str
    description: str
    required: bool = True


@dataclass(frozen=True)
class AgentInput(ArtifactContract):
    pass


@dataclass(frozen=True)
class AgentOutput(ArtifactContract):
    pass


@dataclass(frozen=True)
class AgentCapability:
    name: str
    description: str = ""


@dataclass(frozen=True)
class ExecutionConstraints:
    max_retries: int = 0
    timeout_minutes: int | None = None
    requires_approval: bool = False


@dataclass(frozen=True)
class AgentDefinition:
    id: str
    name: str
    description: str
    capabilities: tuple[AgentCapability, ...]
    inputs: tuple[AgentInput, ...] = ()
    outputs: tuple[AgentOutput, ...] = ()
    constraints: ExecutionConstraints = field(default_factory=ExecutionConstraints)


@dataclass(frozen=True)
class AgentRegistry:
    agents: dict[str, AgentDefinition]

    def has_agent(self, agent_id: str) -> bool:
        return agent_id in self.agents

    def get(self, agent_id: str) -> AgentDefinition:
        return self.agents[agent_id]

    def list_agents(self) -> list[AgentDefinition]:
        return [self.agents[agent_id] for agent_id in sorted(self.agents)]


@dataclass
class ProjectState:
    statuses: dict[str, TaskStatus] = field(default_factory=dict)

    def status_of(self, task_id: str) -> TaskStatus:
        return self.statuses.get(task_id, TaskStatus.PENDING)
