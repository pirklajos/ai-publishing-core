# Codex instructions

## Mission
Build a reusable, deterministic orchestration core for AI-assisted publishing workflows.

## Rules
- Keep the core provider-agnostic. Do not hard-code OpenAI, Codex, or another model provider into domain objects.
- Workflow state must be persisted as plain JSON or YAML so humans and agents can inspect it.
- Agents may only run when all declared dependencies are complete.
- Every generated artifact must have an explicit path and owning task.
- Prefer small typed Python modules and pure functions.
- Add tests for dependency resolution and state transitions.
- Never silently overwrite completed artifacts.
- Avoid autonomous publishing or irreversible external actions. Human approval gates must remain possible.

## Definition of done
- `python -m pytest` passes.
- `aipos plan examples/book-project.yaml` prints runnable tasks.
- `aipos complete <task-id>` updates project state without corrupting unrelated tasks.
