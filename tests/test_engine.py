import pytest

from aipos.engine import WorkflowError, mark_completed, runnable_tasks, validate_workflow
from aipos.models import ProjectState, TaskDefinition, TaskStatus


def sample_tasks():
    return [
        TaskDefinition(id="research", agent="research.market", description="Research"),
        TaskDefinition(id="outline", agent="editorial.outline", description="Outline", depends_on=("research",)),
    ]


def test_only_dependency_free_task_is_initially_runnable():
    ready = runnable_tasks(sample_tasks(), ProjectState())
    assert [task.id for task in ready] == ["research"]


def test_completing_dependency_unlocks_next_task():
    state = ProjectState()
    mark_completed("research", sample_tasks(), state)
    assert state.status_of("research") == TaskStatus.COMPLETED
    assert [task.id for task in runnable_tasks(sample_tasks(), state)] == ["outline"]


def test_cannot_complete_blocked_task():
    with pytest.raises(WorkflowError):
        mark_completed("outline", sample_tasks(), ProjectState())


def test_cycles_are_rejected():
    tasks = [
        TaskDefinition(id="a", agent="x", description="A", depends_on=("b",)),
        TaskDefinition(id="b", agent="x", description="B", depends_on=("a",)),
    ]
    with pytest.raises(WorkflowError):
        validate_workflow(tasks)
