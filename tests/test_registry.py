from pathlib import Path

import pytest

from aipos.engine import WorkflowError
from aipos.io import load_agent_registry, load_workflow
from aipos.models import AgentCapability, AgentInput, AgentOutput
from aipos.registry import RegistryError


ROOT = Path(__file__).resolve().parents[1]


def write_registry(tmp_path, body: str) -> Path:
    path = tmp_path / "agents.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def write_workflow(tmp_path, body: str) -> Path:
    path = tmp_path / "workflow.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_loads_example_agent_registry():
    registry = load_agent_registry(ROOT / "examples/agents.yaml")

    assert [agent.id for agent in registry.list_agents()] == [
        "editorial.outline",
        "qa.editorial",
        "research.audience",
        "research.market",
        "writing.chapter",
    ]
    writer = registry.get("writing.chapter")
    assert isinstance(writer.capabilities[0], AgentCapability)
    assert isinstance(writer.inputs[0], AgentInput)
    assert isinstance(writer.outputs[0], AgentOutput)
    assert writer.constraints.max_retries == 2


def test_rejects_duplicate_agent_ids(tmp_path):
    registry_path = write_registry(
        tmp_path,
        """
agents:
  - id: research.market
    name: Market
    description: Research market.
    capabilities: [market-research]
    outputs:
      - path: research/market.md
        description: Market research.
  - id: research.market
    name: Duplicate
    description: Duplicate market research.
    capabilities: [market-research]
    outputs:
      - path: research/duplicate.md
        description: Duplicate research.
""",
    )

    with pytest.raises(RegistryError, match="unique"):
        load_agent_registry(registry_path)


def test_rejects_missing_required_agent_fields(tmp_path):
    registry_path = write_registry(
        tmp_path,
        """
agents:
  - id: research.market
    name: Market
    capabilities: [market-research]
    outputs:
      - path: research/market.md
        description: Market research.
""",
    )

    with pytest.raises(RegistryError, match="missing required fields"):
        load_agent_registry(registry_path)


def test_rejects_invalid_agent_contract_paths(tmp_path):
    registry_path = write_registry(
        tmp_path,
        """
agents:
  - id: research.market
    name: Market
    description: Research market.
    capabilities: [market-research]
    outputs:
      - path: ../market.md
        description: Market research.
""",
    )

    with pytest.raises(RegistryError, match="parent"):
        load_agent_registry(registry_path)


def test_workflow_loading_rejects_unknown_agents(tmp_path):
    registry = load_agent_registry(ROOT / "examples/agents.yaml")
    workflow_path = write_workflow(
        tmp_path,
        """
tasks:
  - id: research.market
    agent: research.unknown
    description: Research the market.
    outputs: [research/market.md]
""",
    )

    with pytest.raises(WorkflowError, match="unknown agents"):
        load_workflow(workflow_path, registry)


def test_workflow_loading_rejects_missing_required_task_fields(tmp_path):
    registry = load_agent_registry(ROOT / "examples/agents.yaml")
    workflow_path = write_workflow(
        tmp_path,
        """
tasks:
  - id: research.market
    description: Research the market.
    outputs: [research/market.md]
""",
    )

    with pytest.raises(WorkflowError, match="missing required fields"):
        load_workflow(workflow_path, registry)


def test_workflow_loading_rejects_invalid_task_output_paths(tmp_path):
    registry = load_agent_registry(ROOT / "examples/agents.yaml")
    workflow_path = write_workflow(
        tmp_path,
        """
tasks:
  - id: research.market
    agent: research.market
    description: Research the market.
    outputs: [/tmp/market.md]
""",
    )

    with pytest.raises(WorkflowError, match="project-relative"):
        load_workflow(workflow_path, registry)


def test_workflow_outputs_match_exact_and_glob_agent_contracts():
    registry = load_agent_registry(ROOT / "examples/agents.yaml")

    workflow = load_workflow(ROOT / "examples/book-project.yaml", registry)

    assert [task.id for task in workflow] == [
        "research.market",
        "research.audience",
        "editorial.outline",
        "writing.chapter-01",
        "qa.chapter-01",
    ]


def test_workflow_outputs_match_recursive_glob_contract(tmp_path):
    registry_path = write_registry(
        tmp_path,
        """
agents:
  - id: writing.chapter
    name: Chapter Writer
    description: Drafts chapter files.
    capabilities: [chapter-drafting]
    outputs:
      - path: manuscript/**/*.md
        description: Draft manuscript files.
""",
    )
    workflow_path = write_workflow(
        tmp_path,
        """
tasks:
  - id: writing.chapter-01
    agent: writing.chapter
    description: Draft chapter 1.
    outputs: [manuscript/chapters/01-introduction.md]
""",
    )

    registry = load_agent_registry(registry_path)

    assert load_workflow(workflow_path, registry)[0].id == "writing.chapter-01"


def test_workflow_rejects_outputs_outside_agent_contract(tmp_path):
    registry = load_agent_registry(ROOT / "examples/agents.yaml")
    workflow_path = write_workflow(
        tmp_path,
        """
tasks:
  - id: writing.chapter-01
    agent: writing.chapter
    description: Draft chapter 1.
    outputs: [manuscript/01-introduction.md]
""",
    )

    with pytest.raises(WorkflowError, match="output contracts"):
        load_workflow(workflow_path, registry)


def test_workflow_cannot_bypass_agent_approval_requirement(tmp_path):
    registry = load_agent_registry(ROOT / "examples/agents.yaml")
    workflow_path = write_workflow(
        tmp_path,
        """
tasks:
  - id: editorial.outline
    agent: editorial.outline
    description: Create the detailed book outline.
    outputs: [manuscript/outline.md]
    approval_required: false
""",
    )

    with pytest.raises(WorkflowError, match="must require approval"):
        load_workflow(workflow_path, registry)
