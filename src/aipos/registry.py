from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import (
    AgentCapability,
    AgentDefinition,
    AgentInput,
    AgentOutput,
    AgentRegistry,
    ArtifactContract,
    ExecutionConstraints,
    TaskDefinition,
)
from .validation import require_non_empty_string, validate_artifact_path


class RegistryError(ValueError):
    pass


def validate_agent_registry(agents: Iterable[AgentDefinition]) -> AgentRegistry:
    agent_list = list(agents)
    agent_map = {agent.id: agent for agent in agent_list}
    if not agent_map:
        raise RegistryError("Agent registry must contain at least one agent")
    if len(agent_map) != len(agent_list):
        raise RegistryError("Agent IDs must be unique")

    for agent in agent_list:
        _validate_agent(agent)
    return AgentRegistry(agent_map)


def validate_task_agents(tasks: Iterable[TaskDefinition], registry: AgentRegistry) -> None:
    unknown = sorted({task.agent for task in tasks if not registry.has_agent(task.agent)})
    if unknown:
        raise RegistryError(f"Workflow references unknown agents: {unknown}")


def agent_from_mapping(item: Mapping[str, object]) -> AgentDefinition:
    if not isinstance(item, Mapping):
        raise RegistryError("Agent definition entries must be mappings")
    missing = [field for field in ("id", "name", "description", "capabilities", "outputs") if field not in item]
    if missing:
        raise RegistryError(f"Agent definition is missing required fields: {missing}")

    try:
        return AgentDefinition(
            id=require_non_empty_string(item["id"], "agent id"),
            name=require_non_empty_string(item["name"], "agent name"),
            description=require_non_empty_string(item["description"], "agent description"),
            capabilities=_parse_capabilities(item["capabilities"]),
            inputs=_parse_contracts(item.get("inputs", []), "inputs", AgentInput),
            outputs=_parse_contracts(item["outputs"], "outputs", AgentOutput),
            constraints=_parse_constraints(item.get("constraints", {})),
        )
    except ValueError as exc:
        raise RegistryError(str(exc)) from exc


def _validate_agent(agent: AgentDefinition) -> None:
    require_non_empty_string(agent.id, "agent id")
    require_non_empty_string(agent.name, "agent name")
    require_non_empty_string(agent.description, "agent description")
    if not agent.capabilities:
        raise RegistryError(f"Agent {agent.id} must declare at least one capability")
    for capability in agent.capabilities:
        require_non_empty_string(capability.name, f"capability for {agent.id}")
    if not agent.outputs:
        raise RegistryError(f"Agent {agent.id} must declare at least one output contract")
    for contract in [*agent.inputs, *agent.outputs]:
        try:
            validate_artifact_path(contract.path, f"artifact path for {agent.id}")
        except ValueError as exc:
            raise RegistryError(str(exc)) from exc
    if agent.constraints.max_retries < 0:
        raise RegistryError(f"Agent {agent.id} max_retries must not be negative")
    if agent.constraints.timeout_minutes is not None and agent.constraints.timeout_minutes <= 0:
        raise RegistryError(f"Agent {agent.id} timeout_minutes must be positive")


def _parse_capabilities(value: object) -> tuple[AgentCapability, ...]:
    if not isinstance(value, list):
        raise ValueError("agent capabilities must be a list")
    parsed = tuple(_parse_capability(item) for item in value)
    if not parsed:
        raise ValueError("agent capabilities must not be empty")
    return parsed


def _parse_capability(value: object) -> AgentCapability:
    if isinstance(value, str):
        return AgentCapability(name=require_non_empty_string(value, "agent capability"))
    if isinstance(value, Mapping):
        if "name" not in value:
            raise ValueError("capability entries must include name")
        return AgentCapability(
            name=require_non_empty_string(value["name"], "agent capability"),
            description=str(value.get("description", "")),
        )
    raise ValueError("capability entries must be strings or mappings")


def _parse_contracts(
    value: object,
    field_name: str,
    contract_type: type[AgentInput] | type[AgentOutput],
) -> tuple[ArtifactContract, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")

    contracts: list[ArtifactContract] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name} entries must be mappings")
        if "path" not in item:
            raise ValueError(f"{field_name} entries must include path")
        contracts.append(
            contract_type(
                path=validate_artifact_path(item["path"], f"{field_name} path"),
                description=require_non_empty_string(item.get("description", ""), f"{field_name} description"),
                required=bool(item.get("required", True)),
            )
        )
    return tuple(contracts)


def _parse_constraints(value: object) -> ExecutionConstraints:
    if not isinstance(value, Mapping):
        raise ValueError("constraints must be a mapping")

    max_retries = _parse_non_negative_int(value.get("max_retries", 0), "max_retries")
    timeout_value = value.get("timeout_minutes")
    timeout_minutes = None
    if timeout_value is not None:
        timeout_minutes = _parse_non_negative_int(timeout_value, "timeout_minutes")
        if timeout_minutes == 0:
            raise ValueError("timeout_minutes must be positive")

    return ExecutionConstraints(
        max_retries=max_retries,
        timeout_minutes=timeout_minutes,
        requires_approval=bool(value.get("requires_approval", False)),
    )


def _parse_non_negative_int(value: object, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative")
    return value
