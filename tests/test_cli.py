import json
import sys
from pathlib import Path

from aipos.cli import main


ROOT = Path(__file__).resolve().parents[1]


def run_cli(monkeypatch, *args: str) -> None:
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "argv", ["aipos", *args])
    main()


def test_plan_prints_runnable_tasks(monkeypatch, capsys):
    run_cli(monkeypatch, "plan", "examples/book-project.yaml")

    output = capsys.readouterr().out
    assert "research.market: research.market - Research the Hungarian market" in output
    assert "research.audience: research.audience - Define the target audience" in output


def test_agents_list_prints_registered_agents(monkeypatch, capsys):
    run_cli(monkeypatch, "agents", "list")

    output = capsys.readouterr().out
    assert "research.market: Market Research - market-research, competitor-analysis, positioning" in output
    assert "qa.editorial: Editorial QA - editorial-review, consistency-checking, claim-review" in output


def test_agents_validate_prints_summary(monkeypatch, capsys):
    run_cli(monkeypatch, "agents", "validate")

    assert capsys.readouterr().out == "Agent registry valid: 5 agents\n"


def test_complete_task_id_uses_default_workflow(monkeypatch, tmp_path, capsys):
    state_path = tmp_path / "state.json"

    run_cli(monkeypatch, "--state", str(state_path), "complete", "research.market")

    assert capsys.readouterr().out == "Completed: research.market\n"
    assert json.loads(state_path.read_text(encoding="utf-8")) == {
        "statuses": {"research.market": "completed"}
    }


def test_complete_preserves_unrelated_state(monkeypatch, tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"statuses": {"research.audience": "blocked"}}),
        encoding="utf-8",
    )

    run_cli(monkeypatch, "--state", str(state_path), "complete", "research.market")

    assert json.loads(state_path.read_text(encoding="utf-8")) == {
        "statuses": {
            "research.audience": "blocked",
            "research.market": "completed",
        }
    }
