from __future__ import annotations

import argparse
from pathlib import Path

from .engine import mark_completed, runnable_tasks
from .io import load_agent_registry, load_state, load_workflow, save_state

DEFAULT_WORKFLOW = "examples/book-project.yaml"
DEFAULT_AGENTS = "examples/agents.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aipos")
    parser.add_argument("--state", default=".aipos-state.json")
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    parser.add_argument("--agents", default=DEFAULT_AGENTS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="List tasks that are ready to run")
    plan.add_argument("workflow")

    complete = subparsers.add_parser("complete", help="Mark a task as completed")
    complete.add_argument("args", metavar="ARG", nargs="+", help="TASK_ID or WORKFLOW TASK_ID")

    agents = subparsers.add_parser("agents", help="Inspect and validate the agent registry")
    agents_subparsers = agents.add_subparsers(dest="agents_command", required=True)
    agents_subparsers.add_parser("list", help="List registered agents")
    agents_subparsers.add_parser("validate", help="Validate the agent registry")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "agents":
        registry = load_agent_registry(args.agents)
        if args.agents_command == "list":
            for agent in registry.list_agents():
                capabilities = ", ".join(capability.name for capability in agent.capabilities)
                print(f"{agent.id}: {agent.name} - {capabilities}")
            return
        if args.agents_command == "validate":
            print(f"Agent registry valid: {len(registry.agents)} agents")
            return

    registry = load_agent_registry(args.agents)
    state = load_state(Path(args.state))

    if args.command == "plan":
        ready = runnable_tasks(load_workflow(args.workflow, registry), state, registry)
        if not ready:
            print("No runnable tasks.")
            return
        for task in ready:
            gate = " [approval]" if task.approval_required else ""
            print(f"{task.id}: {task.agent}{gate} - {task.description}")
        return

    if args.command == "complete":
        workflow_path, task_id = resolve_complete_args(args.args, args.workflow)
        mark_completed(task_id, load_workflow(workflow_path, registry), state, registry)
        save_state(Path(args.state), state)
        print(f"Completed: {task_id}")


def resolve_complete_args(values: list[str], default_workflow: str) -> tuple[str, str]:
    if len(values) == 1:
        return default_workflow, values[0]
    if len(values) == 2:
        return values[0], values[1]
    raise SystemExit("complete expects TASK_ID or WORKFLOW TASK_ID")


if __name__ == "__main__":
    main()
