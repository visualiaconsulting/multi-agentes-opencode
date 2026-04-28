<div align="center">

# 🤖 oh-my-agents

### The multi-agent orchestration framework for [OpenCode](https://opencode.ai)

[![OpenCode](https://img.shields.io/badge/Built_for-OpenCode_Go-00D4AA?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTVNMiAxN2wxMCA1IDEwLTVNMiAxMmwxMCA1IDEwLTUiLz48L3N2Zz4=)](https://opencode.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/visualiaconsulting/oh-my-agents?style=for-the-badge&logo=github)](https://github.com/visualiaconsulting/oh-my-agents/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/visualiaconsulting/oh-my-agents?style=for-the-badge&logo=github)](https://github.com/visualiaconsulting/oh-my-agents/issues)

**Stop writing boilerplate. Start shipping with an AI workforce.**

*oh-my-agents* gives you a production-ready **orchestrator-specialists architecture** for [OpenCode](https://opencode.ai). One orchestrator analyzes your tasks, breaks them down, and delegates to specialized sub-agents — each with the right model and permissions for the job.

[Quick Start](#-quick-start) · [Agents](#-agents) · [Examples](#-examples) · [Configuration](#%EF%B8%8F-planmanager) · [Contributing](#-contributing)

---

</div>

## ✨ Why oh-my-agents?

| Feature | Description |
|---------|-------------|
| 🧠 **Smart Orchestration** | The orchestrator analyzes complex tasks, decomposes them, and delegates to the right specialist |
| 🎯 **Specialist Agents** | Each agent has a focused role: coding, QA validation, data processing, debugging |
| 🔐 **Least-Privilege Permissions** | Validator is read-only. Orchestrator only delegates. Code-analyst writes and executes. |
| 🔄 **Multi-Plan Support** | Works with OpenCode Go, Zen, API, and Enterprise plans via `PlanManager` |
| 🚀 **Zero Config Start** | Clone, run setup, start coding. The wizard handles the rest |
| 📦 **Portable** | Copy agents to any project — they adapt via `context.md` |

---

## 🤖 Agents

| Agent | Model (Go Plan) | Role | Permissions |
|-------|:----------------:|------|:-----------:|
| **@orchestrator** | `mimo-v2.5-pro` | 🎼 Coordinator — decomposes tasks, delegates to specialists | `read` `task` |
| **@code-analyst** | `deepseek-v4-pro` | 💻 Senior Engineer — writes clean code, implements features | `edit` `bash` `read` |
| **@validator** | `kimi-k2.6` | 🔍 QA Specialist — validates quality, reviews code | `read` only |
| **@bulk-processor** | `deepseek-v4-flash` | ⚡ Data Processor — handles repetitive, high-volume tasks (hidden) | `edit` `bash` `read` |
| **@subagent** | `glm-5.1` | 🛠️ Debugger — auxiliary tasks and fallback agent | `edit` `bash` `read` |

> **How it works:** You give a task to `@orchestrator`. It analyzes, plans, and delegates to the right specialist(s). The validator checks quality before returning results.

---

## 🚀 Quick Start

### Prerequisites

- [OpenCode CLI](https://opencode.ai) installed
- Active **OpenCode Go** subscription
- API key configured via `/connect` or environment variable

### Install (3 steps)

```bash
# 1. Clone the repository
git clone https://github.com/visualiaconsulting/oh-my-agents.git
cd oh-my-agents

# 2. Run setup (installs deps and configures agents)
.\setup.ps1        # Windows
# or
./setup.sh         # Linux/Mac

# 3. Start the orchestrator
opencode --agent orchestrator
```

### Copy agents to another project

```bash
# Create agents directory in your project
mkdir -p myproject/.opencode/agents

# Copy agent definitions
cp .opencode/agents/*.md myproject/.opencode/agents/

# Create a context.md for your project
cat > myproject/.opencode/CONTEXT.md << 'EOF'
---
project: My Project
plan: go
version: 1.0
---
Describe your project context here...
EOF

# Run from your project
cd myproject
opencode --agent orchestrator
```

---

## 💡 Examples

### Training a YOLO model

```
> complete the training of YOLO26n to 25 epochs with MuSGD and GPU 0
```

The orchestrator:
1. Asks `@code-analyst` to prepare/complete the training script
2. Asks `@validator` to verify parameters are correct
3. Executes the consolidated command

### Analyzing results

```
> review the results of the last training and compare with previous ones
```

The orchestrator:
1. Reads CSV/results.csv
2. Asks `@code-analyst` to extract metrics
3. Asks `@validator` to verify targets are met
4. Returns a comparative summary

### Multi-step task

```
> refactor the data pipeline to use async processing, add error handling, and write tests
```

The orchestrator:
1. Asks `@code-analyst` to refactor with async patterns
2. Asks `@validator` to review the refactored code
3. Asks `@code-analyst` to add error handling and tests
4. Asks `@validator` to run and validate tests
5. Returns consolidated results

---

## ⚙️ PlanManager

The `PlanManager` automatically detects your active OpenCode plan and selects the optimal models for each agent role.

```python
from plan_manager import PlanManager

pm = PlanManager()
print(f"Plan detected: {pm.plan}")
print(f"Orchestrator model: {pm.get_model('orchestrator')}")
print(f"Available models: {pm.get_available_models()}")
```

### Supported Plans

| Plan | Detection Method | Orchestrator Model |
|------|------------------|-------------------|
| **Go** (default) | Default or `OPENCODE_PLAN=go` | `opencode-go/mimo-v2.5-pro` |
| **Zen** | `GITHUB_TOKEN` or `COPILOT_TOKEN` | `opencode/claude-sonnet-4.5` |
| **API** | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4` (configurable) |
| **Enterprise** | `OPENCODE_PLAN=enterprise` | `opencode-go/mimo-v2.5-pro` (configurable) |

---

## 📁 Project Structure

```
oh-my-agents/
├── README.md                    # This file
├── AGENTS.md                    # Detailed agent state & changelog
├── plan_manager.py              # Model selection logic per plan
├── main.py                      # CLI for the multi-agent system
├── requirements.txt             # Python dependencies
├── setup.ps1                    # Windows setup script
├── setup.sh                     # Linux/Mac setup script
├── cli/
│   ├── wizard.py                # Interactive configuration wizard
│   └── ui.py                    # Rich terminal UI components
└── .opencode/
    ├── context.md               # Global context injected to all agents
    └── agents/
        ├── orchestrator.md      # Main coordinator
        ├── code-analyst.md      # Senior software engineer
        ├── validator.md         # QA and code validation
        ├── bulk-processor.md    # High-volume data processing (hidden)
        └── subagent.md          # Debugger / fallback agent
```

---

## 📝 Changelog

### v0.9.2.3 — Full English Translation (April 2026)

- Translated all documentation and code comments from Spanish to English
- Agent definitions, context.md, AGENTS.md, main.py, wizard.py, ui.py, plan_manager.py
- Goal: broader global reach for the project

### v0.9.2.1 — Subagent Model Fix + Multi-Plan Support (April 2026)

- Subagent model changed from `mimo-v2.5-pro` to `glm-5.1` (no more duplicates)
- New plans added to PlanManager: OpenRouter, Copilot, Ollama
- All agent permissions verified and documented correctly
- Deprecated Qwen models removed from available models list

### v0.9.2.0 — Rebrand to oh-my-agents (April 2026)

**New identity:** Renamed from `multi-agentes-opencode` to `oh-my-agents` for better memorability and alignment with trending GitHub naming patterns.

- Updated all documentation and references
- Explicit OpenCode branding throughout
- Banner updated with VisualIA Consulting credit and MIT license

### v0.9.1.0 — Base Project Sync (April 2026)

Fixed critical model ID mismatch — agents were using display names instead of registry IDs (`opencode-go/*`), causing `ProviderModelNotFoundError`.

### v0.9.0.0 — Permission Audit (April 2026)

Removed excessive write/execute permissions from agents that don't need them. Orchestrator is now strictly `read + task`. Validator is `read` only.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for contribution

- 🔌 Add support for new OpenCode plans
- 🤖 Create new specialist agents (e.g., `@doc-writer`, `@security-auditor`)
- 🎨 Improve the CLI wizard UI
- 📖 Translate documentation
- 🧪 Add integration tests

---

## 🔗 Links

- **Repository**: [visualiaconsulting/oh-my-agents](https://github.com/visualiaconsulting/oh-my-agents)
- **Organization**: [VisualIA Consulting](https://github.com/visualiaconsulting)
- **OpenCode**: [opencode.ai](https://opencode.ai)
- **Issues**: [Report a bug](https://github.com/visualiaconsulting/oh-my-agents/issues)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the [OpenCode](https://opencode.ai) community**

*If you find this useful, give it a ⭐ — it helps others discover it!*

</div>
