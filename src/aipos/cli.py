from __future__ import annotations

import argparse
from pathlib import Path

from .engine import mark_completed, runnable_tasks
from .io import load_state, load_workflow, save_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aipos")
    parser.add_argument("--state", default=".aipos-state.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="List tasks that are ready to run")
    plan.add_argument("workflow")

    complete = subparsers.add_parser("complete", help="Mark a task as completed")
    complete.add_argument("workflow")
    complete.add_argument("task_id")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workflow = load_workflow(args.workflow)
    state_path = Path(args.state)
    state = load_state(state_path)

    if args.command == "plan":
        ready = runnable_tasks(workflow, state)
        if not ready:
            print("No runnable tasks.")
            return
        for task in ready:
            gate = " [approval]" if task.approval_required else ""
            print(f"{task.id}: {task.agent}{gate} — {task.description}")
        return

    if args.command == "complete":
        mark_completed(args.task_id, workflow, state)
        save_state(state_path, state)
        print(f"Completed: {args.task_id}")


if __name__ == "__main__":
    main()
