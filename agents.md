# Agent Status — oh-my-agents

This document describes the configuration, status, and architecture of the project's multi-agent system.

---

## 📋 System Overview

The project implements an **Orchestrator and Specialists** architecture on the default **OpenCode Go** plan, with dynamic adaptation capability to other plans (Zen, API, Enterprise, OpenRouter, Copilot, Ollama) via the `PlanManager`.

| Component | Description |
|------------|-------------|
| **Orchestrator** | Main agent that breaks down complex tasks and delegates to sub-agents |
| **Specialists** | Secondary agents with specific roles (code, QA, data) |
| **PlanManager** | Python module that detects the active plan and assigns models |
| **SessionManager** | Manages session logs, bitacora, and continuity between sessions |
| **SkillRegistry** | Downloads and manages skills from skills.sh ecosystem |

---

## 🤖 Configured Agents

| Agent | Role | Model (Go Plan) | Permissions | Description |
| :--- | :--- | :--- | :--- | :--- |
| **@orchestrator** | Main Coordinator | `opencode-go/mimo-v2.5-pro` | `Read, Task` | Breaks down complex tasks and delegates to sub-agents. Does NOT write code or execute commands. |
| **@code-analyst** | Senior Engineer | `opencode-go/deepseek-v4-pro` | `Edit, Bash, Read` | Clean code and architecture implementation. |
| **@validator** | QA Specialist | `opencode-go/kimi-k2.6` | `Read Only` | Validation, linting, and quality review. No editing or bash. |
| **@bulk-processor** | Data Processor | `opencode-go/deepseek-v4-flash` | `Edit, Bash, Read` | Repetitive, high-volume tasks (hidden). |
| **@subagent** | Debugger/Fallback | `opencode-go/glm-5.1` | `Edit, Bash, Read` | Generic agent for debugging and auxiliary tasks. |
| **@summarizer** | Session Analyst | `opencode-go/minimax-m2.5` | `Edit, Bash, Read` | Lightweight session summarizer, log analysis, and project continuity. |

### 🔍 Permission Details by Agent

| Agent | edit | bash | read | task |
|--------|:----:|:----:|:----:|:----:|
| **@orchestrator** | ❌ deny | ❌ deny | ✅ allow | ✅ allow |
| **@code-analyst** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |
| **@validator** | ❌ deny | ❌ deny | ✅ allow | ❌ deny |
| **@bulk-processor** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |
| **@subagent** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |
| **@summarizer** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |

---

## 🛠️ Code Infrastructure

### `plan_manager.py` — Dynamic Configuration Core

The `PlanManager` is the logical brain that manages agent configuration based on the detected plan:

- **Plan Detection:** Automatically identifies whether you are in `go`, `zen`, `api`, `enterprise`, `openrouter`, `copilot`, or `ollama` using environment variables and configuration files.
- **Model Mapping:** Maps each role (`orchestrator`, `code-analyst`, `validator`, `bulk-processor`, `subagent`, `summarizer`) to the optimal model for the active plan.
- **Fallbacks:** Provides backup models if the primary one is not available.
- **API Key Validation:** Verifies that external providers have the necessary credentials (only for `api` and `openrouter` plans).

**Default Models in Go Plan:**

| Role | Model |
|:---|:---|
| Orchestrator | `opencode-go/mimo-v2.5-pro` |
| Code Analyst | `opencode-go/deepseek-v4-pro` |
| Validator | `opencode-go/kimi-k2.6` |
| Bulk Processor | `opencode-go/deepseek-v4-flash` |
| Subagent | `opencode-go/glm-5.1` |
| Summarizer | `opencode-go/minimax-m2.5` |
| Fallback | `opencode-go/minimax-m2.5` |

### ~~`opencode.jsonc`~~ — Removed

> **Note:** The `opencode.jsonc` file was removed because it caused configuration conflicts. OpenCode reads configuration directly from the `.opencode/agents/*.md` files.

### `main.py` — System CLI

Command-line interface that:
- Displays the multi-agent system banner
- Runs the setup wizard (`--setup`) if no agents are defined
- Loads and displays agent status from `.opencode/agents/*.md`
- Diagnoses environment issues (`--doctor`) — now includes model ID validation, session history, and skills status
- Installs agents globally to `~/.opencode/agents/` (`--install-global`)
- Supports explicit project root override (`--dir DIR`)
- Uses `PROJECT_ROOT = Path(__file__).parent.resolve()` for path-independent operation
- **Session management:** `--sessions`, `--session <id>`, `--session-status`, `--summarize`
- **Skills management:** `--skills`, `--skills-search <query>`, `--skills-install <id>`, `--skills-remove <name>`

### `session_manager.py` — Session Bitacora

Manages session continuity:
- **`scan_logs()`** — Reads `.opencode/logs/` to extract errors, files changed, commands run
- **`save_session()`** — Saves session record as JSON in `.opencode/sessions/`
- **`inject_context()`** — Generates markdown context from recent sessions for `context.md`
- **`update_context_md()`** — Automatically updates `context.md` with session history
- Sessions are stored with: ID, timestamp, agent, summary, errors, pending tasks, files changed

### `skill_registry.py` — Skills Manager

Manages skills from the skills.sh ecosystem:
- **`search_skills(query)`** — Searches skills.sh for available skills
- **`install_skill(identifier)`** — Downloads skill from GitHub to `.opencode/skills/`
- **`inject_skills_context()`** — Generates markdown context from installed skills
- **`update_context_md()`** — Updates `context.md` with active skills

### `cli/wizard.py` — Setup Wizard

Interactive wizard that proposes default configurations or guides the user through manual agent creation. Assigns `opencode-go/mimo-v2.5-pro` to the orchestrator by default.

### `cli/ui.py` — User Interface

Visual components with `rich` for terminal: banners, agent tables, panels, and styled messages.

---

## ⚠️ Known Issue: Qwen Models Disabled (Resolved)

The **Qwen3.6 Plus** and **Qwen3.5 Plus** models are marked as `deprecated` in the OpenCode registry.

> **Applied solution:** They were removed from the available models list in `plan_manager.py`. The orchestrator model was changed to `opencode-go/mimo-v2.5-pro`. `opencode.jsonc` which caused conflicts was removed.

### Reference
- Issue: [#22644](https://github.com/anomalyco/opencode/issues/22644)

---

## 📝 Changelog

### v1.1.1 — Session Continuity & Skills (April 2026)

**New features:**
- **Session bitacora:** `session_manager.py` scans OpenCode logs, saves session records, and injects context for continuity between sessions
- **Skills system:** `skill_registry.py` downloads and manages skills from skills.sh ecosystem
- **@summarizer agent:** New lightweight agent (`opencode-go/minimax-m2.5`) for session analysis and project continuity
- **Global install automatic:** `setup.ps1` now installs agents globally by default — `opencode --agent orchestrator` works from any folder
- **Quick install:** `install.ps1` for fast setup on new machines

**New CLI commands:**
| Command | Description |
|---------|-------------|
| `--sessions` | List recorded sessions |
| `--session <id>` | Show details of a specific session |
| `--session-status` | Show summary of the last session |
| `--summarize` | Scan logs and save session record |
| `--skills` | List installed skills |
| `--skills-search <q>` | Search skills on skills.sh |
| `--skills-install <id>` | Install a skill from skills.sh |
| `--skills-remove <name>` | Remove an installed skill |

**New files:**
- `session_manager.py` — Session logging and continuity
- `skill_registry.py` — Skills download and management
- `utils.py` — Cross-platform helpers
- `install.ps1` — Quick installer for Windows
- `.opencode/agents/summarizer.md` — Summarizer agent definition

**Files modified:**
- `main.py` — 8 new CLI arguments, interactive menu updated
- `plan_manager.py` — Added `summarizer` role to all plans
- `cli/ui.py` — Session and skills UI components
- `cli/wizard.py` — Summarizer added to defaults
- `setup.ps1` — Global install now automatic
- `.opencode/context.md` — Session and skills documentation
- `requirements.txt` — Added `requests`
- `.gitignore` — Added `.opencode/sessions/`, `.opencode/skills/`

### v0.9.3.3 — Interactive Main Menu (April 2026)

**Problem:** Running `python main.py` without flags when agents were already configured would print the status table and exit immediately — no way to interact.

**Solution:** Added an interactive `questionary.select` menu that loops when configuration exists, offering:
- View agent status
- Run setup wizard (reconfigure)
- Run diagnostics (`--doctor`)
- Install globally (`--install-global`)
- Exit

CLI flags (`--setup`, `--doctor`, `--install-global`) still bypass the menu and work as direct commands. First-time (no config) still prompts to run the wizard.

**File modified:**
- `main.py` — Replaced linear flow with interactive menu loop in `main()`

### v0.9.3.2 — Global Install, Tests, Model Validation & CI (April 2026)

**Setup experience overhaul:** Global install is now the default. Agents work from ANY directory after setup — not just inside the project folder.

**Files modified:**
- `setup.ps1` — Global install prompts `[Yn]` (default yes) with clear explanation of why it matters
- `setup.sh` — Same improvement for Linux/Mac, renumbered steps to `[5/5]`
- `main.py` — Improved `install_global()` success message; `--doctor` now validates model IDs
- `plan_manager.py` — Added `validate_models()` method that checks agent models against the registry
- `README.md` — Updated Quick Start and global install docs with explanation of agent scope

**New files:**
- `tests/conftest.py` — Shared fixtures (temp_project, clean_env, mock_questionary)
- `tests/test_plan_manager.py` — 22 tests: plan detection, model mapping, validate_models()
- `tests/test_wizard.py` — 15 tests: init, defaults, permissions, save, format_md
- `tests/test_main.py` — 15 tests: load_agents, dependencies, install_global, doctor
- `.github/workflows/ci.yml` — CI pipeline: test matrix (Python 3.8–3.12) + ruff lint

**What `--doctor` now detects:**
- Invalid model IDs in agent `.md` files that don't match any known registry model
- Reports each mismatched agent and suggests re-running `--setup`

### v0.9.3.1 — Path Independence & Setup Fixes (April 2026)

**Critical fix:** All Python files now use `Path(__file__).parent` for path resolution instead of relative paths. The system works correctly regardless of the current working directory.

**Files modified:**
- `main.py` — Added `PROJECT_ROOT` constant, `--install-global`, `--dir` flags, `install_global()` function
- `cli/wizard.py` — Accepts `project_root` parameter, derives paths from script location (`Path(__file__).resolve().parent.parent`)
- `plan_manager.py` — Accepts `project_root` parameter for config file detection
- `setup.ps1` — Fixed ExecutionPolicy guidance, robust Python detection (`py -3` → `python3` → `python`), absolute paths, global install option
- `setup.sh` — Added `cd` to script directory, absolute paths, `--install-global` flag (checked before main.py runs)
- `README.md` — Documented new CLI args, global install section, ExecutionPolicy note, changelog entry

**New CLI arguments:**
| Argument | Description |
|----------|-------------|
| `--setup` | Force the setup wizard to reconfigure agents |
| `--doctor` | Diagnose environment issues (Python, deps, OpenCode CLI, agents) |
| `--install-global` | Copy agent `.md` files to `~/.opencode/agents/` for global use |
| `--dir DIR` | Override the auto-detected project root directory |

**How path resolution works now:**
- `PROJECT_ROOT = Path(__file__).parent.resolve()` in `main.py`
- `SetupWizard(project_root=...)` passes it to `PlanManager(project_root=...)`
- All `.opencode/agents/` references use `project_root / ".opencode" / "agents"` instead of `Path(".opencode/agents")`
- Scripts (`setup.ps1`, `setup.sh`) `cd` to their own directory before doing anything

### v0.9.2.3 — Full English Translation (April 2026)

Translated all documentation, comments, and user-facing strings from Spanish to English across the entire project for broader global reach.

**Files translated:**
- `.opencode/agents/*.md` — Agent descriptions and body text
- `.opencode/context.md` — Project context
- `agents.md` — Full documentation (278 lines)
- `plan_manager.py` — 14 comments and docstrings
- `main.py` — 31 comments, docstrings, and UI strings
- `cli/wizard.py` — 30 comments, prompts, and UI strings
- `cli/ui.py` — 7 UI labels and comments

**Note:** README.md was already in English.

### v0.9.2.1 — Subagent Model Fix + Multi-Plan Support (April 2026)

**Subagent model:** Changed from `opencode-go/mimo-v2.5-pro` to `opencode-go/glm-5.1` to eliminate duplication with the orchestrator.

**New plans supported in PlanManager:**
- `openrouter` — Configurable models via OPENROUTER_API_KEY
- `copilot` — GitHub Copilot models
- `ollama` — Self-hosted local models

**Documentation fixes:**
- AGENTS.md: Orchestrator permissions corrected to `read + task` (not edit/bash)
- AGENTS.md: Removed contradictory note about permission rollback
- AGENTS.md: GLM-5.1 references updated to mimo-v2.5-pro
- README.md: Subagent model updated

**Final models (no duplicates):**

| Agent | Model |
|--------|--------|
| @orchestrator | `opencode-go/mimo-v2.5-pro` |
| @code-analyst | `opencode-go/deepseek-v4-pro` |
| @validator | `opencode-go/kimi-k2.6` |
| @bulk-processor | `opencode-go/deepseek-v4-flash` |
| @subagent | `opencode-go/glm-5.1` |

---

### v0.9.2.0 — Rebrand to oh-my-agents (April 2026)

**New identity:** The project has been renamed from `multi-agentes-opencode` to `oh-my-agents` for better memorability, discoverability, and alignment with trending GitHub naming patterns.

- Renamed repository to `oh-my-agents`
- Updated all documentation and references
- Explicit OpenCode branding throughout
- Banner updated with VisualIA Consulting credit and MIT license

---

### v0.9.1.0 — Base Project Sync (April 2026)

**Critical model fix:** The `.opencode/agents/*.md` files were using display names (`GLM-5.1`, `DeepSeek V4 Pro`) instead of registry IDs (`opencode-go/mimo-v2.5-pro`, `opencode-go/deepseek-v4-pro`), causing `ProviderModelNotFoundError`.

| File | Before (broken) | After (correct) |
|---------|--------------|---------------------|
| `orchestrator.md` | `model: GLM-5.1` | `model: opencode-go/mimo-v2.5-pro` |
| `code-analyst.md` | `model: DeepSeek V4 Pro` | `model: opencode-go/deepseek-v4-pro` |
| `validator.md` | `model: Kimi K2.6` | `model: opencode-go/kimi-k2.6` |
| `bulk-processor.md` | `model: DeepSeek V4 Flash` | `model: opencode-go/deepseek-v4-flash` |
| `subagent.md` | `model: MiMo-V2.5-Pro` | `model: opencode-go/glm-5.1` |

**Additional changes:**
- Removed `opencode.jsonc` — caused conflicts; the base project doesn't use it
- Orchestrator model changed from `glm-5.1` to `mimo-v2.5-pro` (consistent with base project)
- Orchestrator permissions: `edit: deny`, `bash: deny`, `read: allow`, `task: allow`
- Updated documentation (`AGENTS.md`, `README.md`, `context.md`)

---

### v0.9.0.0 — Permission Audit (April 2026)

**Agent permission audit:** Verified that each agent has exactly the permissions that correspond to its role, removing excessive privileges that allowed write/execute where not appropriate.

| Agent | Change | Before | After |
|--------|--------|-------|---------|
| **@orchestrator** | `edit` | ✅ allow | ❌ deny |
| **@orchestrator** | `bash` | ✅ allow | ❌ deny |
| **@validator** | `edit` | ✅ allow | ❌ deny |
| **@validator** | `bash` | ✅ allow | ❌ deny |

**Final verified permissions:**

| Agent | edit | bash | read | task | Mode |
|--------|:----:|:----:|:----:|:----:|------|
| **@orchestrator** | ❌ deny | ❌ deny | ✅ allow | ✅ allow | Coordination — delegates to sub-agents |
| **@code-analyst** | ✅ allow | ✅ allow | ✅ allow | ❌ deny | Execution — writes and executes |
| **@validator** | ❌ deny | ❌ deny | ✅ allow | ❌ deny | Read Only — reviews and reports only |
| **@bulk-processor** | ✅ allow | ✅ allow | ✅ allow | ❌ deny | Execution — bulk processing |
| **@subagent** | ✅ allow | ✅ allow | ✅ allow | ❌ deny | Execution — debugging and fallback |

**Updated role descriptions:**
- **Orchestrator**: Now explicitly states *"You do NOT write code or execute commands directly — you delegate all implementation to sub-agents"*
- **Validator**: Now explicitly states *"You do NOT write or execute code. You only read and report findings"*

**Modified files:**
- `.opencode/agents/orchestrator.md` — permissions and description
- `.opencode/agents/validator.md` — permissions and description
- `AGENTS.md` — permission tables and fixes
- `README.md` — permission table

---

### v0.8.0 — Registry IDs and Fixes (April 2026)

- Fix: Model IDs changed from display names to registry IDs (`opencode-go/*`)
- Fix: Personal path removed from README
- Fix: `plan_manager.py` updated with registry IDs for all plans
- Fix: `_detect_plan()` fallback corrected from `api` to `go`
- Fix: Bare `except` → `(json.JSONDecodeError, OSError)`
- Add: `subagent.md`, `main.py`, `cli/` to the repository

---

## 🐛 Recent Fixes Applied (April 2026)

| # | Problem | File | Solution |
|---|----------|---------|----------|
| 1 | Inconsistent orchestrator: `plan_manager.py` pointed to `Qwen3.6 Plus` | `plan_manager.py` | Changed to `opencode-go/mimo-v2.5-pro` |
| 2 | Validator had edit/bash permissions despite being "Read Only" | `validator.md` | `edit: deny`, `bash: deny` |
| 3 | `_detect_plan()` returned `"api"` if `OPENCODE_API_KEY` existed | `plan_manager.py` | Removed from check; only `ANTHROPIC_API_KEY` → api |
| 4 | Bare `except` silenced all exceptions when reading JSON | `plan_manager.py` | Specified `(json.JSONDecodeError, OSError)` |
| 5 | Placeholder comments in `main.py` | `main.py` | Replaced with docstrings |
| 6 | Wizard proposed `Qwen3.6 Plus` as orchestrator | `cli/wizard.py` | Changed to `opencode-go/mimo-v2.5-pro` |
| 7 | Agents used display names instead of registry IDs | `*.md`, `plan_manager.py` | Changed to IDs `opencode-go/*` |
| 8 | Orchestrator had `edit/bash: allow` despite being plan mode | `orchestrator.md` | Changed to `deny` — only `read + task` |
| 9 | Validator had `edit/bash: allow` despite being "Read Only" | `validator.md` | Changed to `deny` |
| 10 | `opencode.jsonc` caused configuration conflicts | `opencode.jsonc` | Removed |
| 11 | Orchestrator model inconsistent with base project | `orchestrator.md` | Changed to `opencode-go/mimo-v2.5-pro` |
| 12 | All Python files used relative paths (`Path(".opencode/...")`) — broke when CWD ≠ project root | `main.py`, `wizard.py`, `plan_manager.py` | Changed to `Path(__file__).parent`-based resolution |
| 13 | `setup.ps1` had no ExecutionPolicy guidance, no `cd` to script dir, only tried `python` | `setup.ps1` | Added `Set-Location $ScriptDir`, `Find-Python` function, ExecutionPolicy comments |
| 14 | `setup.sh` had no `cd` to script dir, `--install-global` flag checked after `main.py` ran | `setup.sh` | Added `cd "$SCRIPT_DIR"`, moved flag check before `main.py` |

---

## 📁 File Structure

```
./
├── AGENTS.md                    # This document (agent status)
├── README.md                    # Main project documentation
├── plan_manager.py              # Model selection logic + model validation
├── main.py                      # Multi-agent system CLI
├── session_manager.py           # Session logging and continuity
├── skill_registry.py            # Skills download and management
├── utils.py                     # Cross-platform helpers
├── requirements.txt             # Python dependencies (now includes requests)
├── setup.ps1                    # Windows setup script (global install by default)
├── setup.sh                     # Linux/Mac setup script (global install by default)
├── install.ps1                  # Quick installer for Windows
├── cli/
│   ├── __init__.py
│   ├── wizard.py                # Interactive setup wizard
│   └── ui.py                    # Visual components (rich)
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_plan_manager.py     # 22 tests: plans, models, validation
│   ├── test_wizard.py           # 15 tests: defaults, permissions, save
│   └── test_main.py             # 15 tests: agents, deps, global install
├── .github/
│   └── workflows/
│       └── ci.yml               # CI pipeline (test matrix + lint)
└── .opencode/
    ├── context.md               # Global context injected to all agents
    └── agents/
        ├── orchestrator.md      # Main coordinator
        ├── code-analyst.md      # Senior software engineer
        ├── validator.md         # QA and code validation
        ├── bulk-processor.md    # Bulk processing (hidden)
        ├── subagent.md          # Debugger / fallback agent
        └── summarizer.md        # Session summarizer
```

---

## 🔧 PlanManager Usage

```python
from plan_manager import PlanManager

pm = PlanManager()
print(f"Plan detected: {pm.plan}")
print(f"Orchestrator model: {pm.get_model('orchestrator')}")
print(f"Available models: {pm.get_available_models()}")
```

### Supported Plans

| Plan | Detection Method | Orchestrator Model |
|------|---------------------|--------------------|
| **Go** (default) | Default or `OPENCODE_PLAN=go` | `opencode-go/mimo-v2.5-pro` |
| **Zen** | `GITHUB_TOKEN` or `COPILOT_TOKEN` | `opencode/claude-sonnet-4.5` |
| **API** | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4` (configurable) |
| **Enterprise** | `OPENCODE_PLAN=enterprise` | `opencode-go/mimo-v2.5-pro` (configurable) |
| **OpenRouter** | `OPENROUTER_API_KEY` | `openrouter/anthropic/claude-sonnet-4.5` (configurable) |
| **Copilot** | Active GitHub Copilot | `copilot/claude-sonnet-4` |
| **Ollama** | `OLLAMA_HOST` or Ollama running | `ollama/llama3.3:70b` (configurable) |

---

## 🚀 Suggested Next Steps

1. **Run tests locally:** `pytest tests/ -v` (58 tests, all current features covered)
2. **Connectivity Validation:** Run `python main.py` to verify that the PlanManager correctly detects the environment
3. **Delegation Tests:** Use `opencode --agent orchestrator` with a complex task to validate interaction between agents (works from any folder after global install)
4. **Model Health Check:** Run `python main.py --doctor` to verify all agent model IDs are valid
5. **Session Continuity:** Run `python main.py --summarize` after an OpenCode session to save the session record
6. **Skills Exploration:** Run `python main.py --skills-search database` to find relevant skills for your project

---

## 🔗 Links

- **Repository**: [visualiaconsulting/oh-my-agents](https://github.com/visualiaconsulting/oh-my-agents)
- **Organization**: [VisualIA Consulting](https://github.com/visualiaconsulting)
- **License**: MIT
