# AIPOS architecture

## MVP boundary

The first versions are deliberately deterministic. AIPOS plans work, validates dependencies and agent contracts, and persists state. It does not yet invoke model providers or publish externally.

## Components

1. **Workflow definition** - YAML task graph with dependencies, outputs, and approval gates.
2. **Agent registry** - YAML catalog of provider-agnostic agent definitions, capabilities, artifact contracts, and execution constraints.
3. **Planner** - identifies tasks whose dependencies are complete.
4. **State store** - human-readable JSON project state.
5. **Runner adapters** - future integrations for Codex, local commands, APIs, and human tasks.
6. **Artifact validator** - future checks that required files exist and pass quality rules before completion.

## Agent registry

Agent definitions describe what an agent can do, not how a provider should run it. The core registry includes:

- stable agent IDs such as `research.market`
- human-readable names and descriptions
- capabilities as plain provider-neutral strings
- input and output artifact contracts with explicit project-relative paths
- execution constraints such as retry limits, timeouts, and approval requirements

Workflow loading validates that every task references a registered agent. Registry loading rejects duplicate IDs, missing required fields, invalid artifact paths, empty capabilities, invalid retry limits, and invalid timeouts.

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
