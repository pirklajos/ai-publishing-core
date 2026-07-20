# AI Publishing Core

Reusable workflow engine for AI-assisted publishing projects.

This repository contains the orchestration layer, agent registry, workflow definitions, project state handling, and validation rules used by book projects such as `ai-publishing-factory`.

## CLI

```bash
aipos agents validate
aipos agents list
aipos plan examples/book-project.yaml
aipos complete research.market
```

By default the CLI reads the example agent registry from `examples/agents.yaml` and project state from `.aipos-state.json`. Use `--agents` or `--state` to point at another registry or state file.
