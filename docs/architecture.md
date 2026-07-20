# AIPOS architecture

## MVP boundary

The first version is deliberately deterministic. It plans work, validates dependencies, and persists state. It does not yet invoke model providers or publish externally.

## Components

1. **Workflow definition** — YAML task graph with dependencies, outputs, and approval gates.
2. **Agent registry** — planned catalog of agent capabilities and input/output contracts.
3. **Planner** — identifies tasks whose dependencies are complete.
4. **State store** — human-readable JSON project state.
5. **Runner adapters** — future integrations for Codex, local commands, APIs, and human tasks.
6. **Artifact validator** — future checks that required files exist and pass quality rules before completion.

## Safety and control

- External publishing and paid actions require explicit human approval.
- Model-specific logic belongs in adapters, not the core domain.
- Completed outputs are immutable by default; revisions create a new task or version.
- Every task should be reproducible from versioned inputs and instructions.

## Planned milestones

- M1: deterministic workflow planner and CLI
- M2: agent registry and typed contracts
- M3: Codex task adapter and run manifests
- M4: artifact validation and QA gates
- M5: integration with `ai-publishing-factory`
- M6: dashboards, retries, budgets, and audit logs
