from __future__ import annotations

from collections.abc import Iterable

from .models import ProjectState, TaskDefinition, TaskStatus


class WorkflowError(ValueError):
    pass


def validate_workflow(tasks: Iterable[TaskDefinition]) -> dict[str, TaskDefinition]:
    task_map = {task.id: task for task in tasks}
    if not task_map:
        raise WorkflowError("Workflow must contain at least one task")
    if len(task_map) != len(list(tasks)):
        raise WorkflowError("Task IDs must be unique")

    for task in task_map.values():
        missing = [dep for dep in task.depends_on if dep not in task_map]
        if missing:
            raise WorkflowError(f"Task {task.id} has missing dependencies: {missing}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise WorkflowError(f"Dependency cycle detected at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in task_map[task_id].depends_on:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in task_map:
        visit(task_id)
    return task_map


def runnable_tasks(tasks: Iterable[TaskDefinition], state: ProjectState) -> list[TaskDefinition]:
    task_list = list(tasks)
    task_map = validate_workflow(task_list)
    runnable: list[TaskDefinition] = []

    for task in task_map.values():
        if state.status_of(task.id) != TaskStatus.PENDING:
            continue
        if all(state.status_of(dep) == TaskStatus.COMPLETED for dep in task.depends_on):
            runnable.append(task)
    return runnable


def mark_completed(task_id: str, tasks: Iterable[TaskDefinition], state: ProjectState) -> None:
    task_map = validate_workflow(list(tasks))
    if task_id not in task_map:
        raise WorkflowError(f"Unknown task: {task_id}")
    task = task_map[task_id]
    incomplete = [dep for dep in task.depends_on if state.status_of(dep) != TaskStatus.COMPLETED]
    if incomplete:
        raise WorkflowError(f"Cannot complete {task_id}; dependencies incomplete: {incomplete}")
    state.statuses[task_id] = TaskStatus.COMPLETED
