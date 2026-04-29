---
project: oh-my-agents
plan: go
version: 0.9.3.2
---

# Project Context

This is a multi-agent system configured for the OpenCode Go plan.
The available agents are:

- **@orchestrator** — Coordinator. Delegates complex tasks to sub-agents. Model: opencode-go/mimo-v2.5-pro
- **@code-analyst** — Senior engineer. Implements clean and efficient code. Model: opencode-go/deepseek-v4-pro
- **@validator** — QA. Validates code and runs tests (read-only). Model: opencode-go/kimi-k2.6
- **@bulk-processor** — Mass data processing (hidden). Model: opencode-go/deepseek-v4-flash
- **@subagent** — Debugger and backup agent for auxiliary tasks. Model: opencode-go/glm-5.1

To use in another project, copy `.opencode/agents/` to the target project
and modify this `CONTEXT.md` with the description of the actual project.
