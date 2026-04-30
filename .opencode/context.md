---
project: oh-my-agents
plan: go
version: 1.5.0
---

# Project Context

This is a multi-agent system configured for the OpenCode Go plan.
The available agents are:

- **@orchestrator** — Coordinator. Delegates complex tasks to sub-agents. Model: opencode-go/kimi-k2.6 (SWE-Bench Pro 58.6%)
- **@code-analyst** — Senior engineer. Implements clean and efficient code. Model: opencode-go/deepseek-v4-pro (GPQA Diamond 90.1%)
- **@validator** — QA. Validates code and runs tests (read-only). Model: opencode-go/mimo-v2.5-pro (94% math precision)
- **@bulk-processor** — Mass data processing (hidden). Model: opencode-go/deepseek-v4-flash (MMLU-Pro 87.5%)
- **@subagent** — Debugger and backup agent for auxiliary tasks. Model: opencode-go/glm-5.1
- **@summarizer** — Session summarizer and project analyst (lightweight). Model: opencode-go/minimax-m2.5
- **@frontend** — UI specialist — React, TypeScript, Tailwind. Model: opencode-go/qwen3.6-plus (SWE-Bench Verified 78.8%)
- **@ml-specialist** — ML and data pipeline specialist. Model: opencode-go/minimax-m2.7 (MLE-Bench Lite 66.6%)

To use in another project, copy `.opencode/agents/` to the target project
and modify this `CONTEXT.md` with the description of the actual project.

## Session Continuity

This project supports session continuity. After each OpenCode session, run:
- `python main.py --summarize` to scan logs and save the session record
- `python main.py --sessions` to view session history
- `python main.py --session-status` to see the last session summary

Session data is stored in `.opencode/sessions/` and context is automatically
injected into this file for continuity between sessions.

## Skills

Skills from skills.sh can be installed to extend agent capabilities:
- `python main.py --skills-search <query>` to search skills.sh
- `python main.py --skills-install owner/repo/name` to install a skill
- `python main.py --skills` to list installed skills

Installed skills are stored in `.opencode/skills/` and injected into context.

## MCP Support

This project supports MCP (Model Context Protocol) servers.
Configure servers in `.opencode/mcp.json`.
