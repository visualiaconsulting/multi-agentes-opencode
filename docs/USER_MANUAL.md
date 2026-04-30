# 📖 Manual de Usuario — oh-my-agents v1.2.2

> Guía completa para instalar, configurar y usar el sistema de agentes multi-especialista en OpenCode.

---

## Tabla de Contenidos

1. [Instalación desde Cero](#1-instalación-desde-cero)
2. [Los 8 Agentes](#2-los-8-agentes)
3. [Session Management (Bitácora)](#3-session-management-bitácora)
4. [Skills System](#4-skills-system)
5. [Referencia CLI](#5-referencia-cli)
6. [PlanManager](#6-planmanager)
7. [Troubleshooting](#7-troubleshooting)
8. [Quick Reference Card](#8-quick-reference-card)

---

## 1. Instalación desde Cero

### Requisitos Previos

| Requisito | Versión | Cómo verificar |
|-----------|---------|----------------|
| Python | 3.8+ | `python --version` |
| OpenCode CLI | Última | `opencode --version` |
| Suscripción Go | Activa | [opencode.ai/es/go](https://opencode.ai/es/go) |

### Opción A: Instalación Completa (recomendada)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/visualiaconsulting/oh-my-agents.git
cd oh-my-agents

# 2. Ejecutar setup (instala dependencias, configura agentes, instala global)
.\setup.ps1

# 3. Verificar
python main.py --doctor
```

**¿Qué hace setup.ps1?**
1. Busca Python 3.8+ en tu sistema
2. Instala dependencias (PyYAML, questionary, rich, requests, pytest)
3. Verifica que OpenCode CLI esté disponible
4. Ejecuta el wizard interactivo para configurar agentes
5. Instala los agentes globalmente en `~/.opencode/agents/`

### Opción B: Instalación Rápida

```powershell
git clone https://github.com/visualiaconsulting/oh-my-agents.git
cd oh-my-agents
.\install.ps1
```

**¿Qué hace install.ps1?**
- Instala dependencias
- Instala agentes globalmente
- Sin wizard interactivo — usa la configuración por defecto (8 agentes)

### Verificar Instalación

```powershell
python main.py --doctor
```

Output esperado:
```
=== System Diagnostics ===

  ✔ Python 3.14.4
  ✔ Dependencies installed (PyYAML, questionary, rich)
  ✔ OpenCode CLI available
  ✔ Agents configured: 8
  ✔ All agent model IDs valid (8 models)
  ℹ No sessions recorded yet
  ℹ No skills installed

==============================
```

### Instalación Global — ¿Qué es?

OpenCode busca agentes en `.opencode/agents/` del directorio actual. La instalación global copia los agentes a `~/.opencode/agents/` para que `opencode --agent orchestrator` funcione desde **cualquier carpeta**.

```powershell
# Verificar que los agentes están instalados globalmente
ls ~/.opencode/agents/
```

Output esperado:
```
bulk-processor.md
code-analyst.md
frontend.md
ml-specialist.md
orchestrator.md
subagent.md
summarizer.md
validator.md
```

---

## 2. Los 8 Agentes

### Tabla de Agentes

| # | Agente | Modelo | Benchmark | Rol |
|---|--------|--------|-----------|-----|
| 1 | `@orchestrator` | Kimi K2.6 | SWE-Bench Pro 58.6% | Coordinador — descompone tareas y delega |
| 2 | `@code-analyst` | DeepSeek V4 Pro | GPQA Diamond 90.1% | Ingeniero senior — código y arquitectura |
| 3 | `@validator` | MiMo V2.5 Pro | 94% math precision | QA — verificación y edge cases |
| 4 | `@bulk-processor` | DeepSeek V4 Flash | MMLU-Pro 87.5% | Procesamiento masivo (oculto) |
| 5 | `@subagent` | GLM-5.1 | Generalista | Fallback y debugging |
| 6 | `@summarizer` | MiniMax M2.5 | Ligero | Análisis post-sesión y bitácora |
| 7 | `@frontend` | Qwen 3.6 Plus | SWE-Bench Verified 78.8% | UI — React, TypeScript, Tailwind |
| 8 | `@ml-specialist` | MiniMax M2.7 | MLE-Bench Lite 66.6% | ML — training, inference, pipelines |

### Permisos

| Agente | edit | bash | read | task |
|--------|:----:|:----:|:----:|:----:|
| @orchestrator | ❌ | ❌ | ✅ | ✅ |
| @code-analyst | ✅ | ✅ | ✅ | ❌ |
| @validator | ❌ | ❌ | ✅ | ❌ |
| @bulk-processor | ✅ | ✅ | ✅ | ❌ |
| @subagent | ✅ | ✅ | ✅ | ❌ |
| @summarizer | ✅ | ✅ | ✅ | ❌ |
| @frontend | ✅ | ✅ | ✅ | ❌ |
| @ml-specialist | ✅ | ✅ | ✅ | ❌ |

### Flujo Típico

```
Usuario: "Refactoriza el pipeline de datos para usar async, añade tests"
    ↓
@orchestrator (Kimi K2.6)
    ├── Analiza la tarea
    ├── Descompone en subtareas
    ├── Delega a @code-analyst (DeepSeek V4 Pro)
    │       └── Implementa async + tests
    ├── Delega a @validator (MiMo V2.5 Pro)
    │       └── Verifica lógica, edge cases
    └── Retorna resultado consolidado
```

---

## 3. Session Management (Bitácora)

### ¿Qué es?

El sistema de bitácora guarda un registro de cada sesión de trabajo para que no pierdas contexto entre sesiones. Cuando cierras OpenCode y vuelves al día siguiente, el sistema recuerda qué hiciste, qué errores hubo, y qué quedó pendiente.

### Flujo Completo

```
Día 1: Trabajas en OpenCode
    ↓
Cierras OpenCode
    ↓
python main.py --summarize    ← Escanea logs y guarda la sesión
    ↓
Día 2: Abres OpenCode
    ↓
El orquestador lee context.md ← Sabe lo que pasó ayer
    ↓
Continúas donde lo dejaste
```

### Comandos

#### `--summarize` — Guardar sesión

```powershell
python main.py --summarize
```

Output:
```
✔ Session saved: a3f8b2c1
  Files changed: 12
  Errors found: 2
  Context updated in .opencode/context.md
```

**¿Qué hace?**
1. Lee `.opencode/logs/` (logs de OpenCode)
2. Extrae: errores, archivos modificados, comandos ejecutados
3. Guarda JSON en `.opencode/sessions/a3f8b2c1.json`
4. Actualiza `context.md` con las últimas 3 sesiones

#### `--sessions` — Ver historial

```powershell
python main.py --sessions
```

Output:
```
Session History
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━┓
┃ ID       ┃ Timestamp          ┃ Agent      ┃ Summary            ┃ Errs ┃ Files┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━┩
│ a3f8b2c1 │ 2026-04-29 14:32   │ @summarizer│ Auto-summarized... │  2   │  12  │
│ b7c2d4e5 │ 2026-04-28 10:15   │ @summarizer│ Auto-summarized... │  0   │   5  │
└──────────┴────────────────────┴────────────┴────────────────────┴──────┴──────┘
```

#### `--session-status` — Última sesión

```powershell
python main.py --session-status
```

Output:
```
=== Last Session ===

  Session: a3f8b2c1
  Time:    2026-04-29 14:32:00
  Agent:   @summarizer

  Summary:
  Auto-summarized session. 12 files changed, 2 errors found.

  Errors (2):
    • TypeError: cannot read property 'x' of undefined
    • Failed to compile src/components/Header.tsx

  Files Changed (12):
    • src/components/Header.tsx
    • src/utils/api.ts
    • ...
```

#### `--session <id>` — Detalle de sesión específica

```powershell
python main.py --session a3f8b2c1
```

### Formato JSON de una Sesión

Cada sesión se guarda en `.opencode/sessions/<id>.json`:

```json
{
  "session_id": "a3f8b2c1",
  "timestamp": "2026-04-29 14:32:00",
  "agent": "summarizer",
  "summary": "Auto-summarized session. 12 files changed, 2 errors found.",
  "errors": ["TypeError: cannot read property 'x' of undefined"],
  "pending_tasks": ["Fix header responsive layout"],
  "files_changed": ["src/components/Header.tsx"],
  "commands_run": ["npm run build"],
  "warnings": ["Deprecated API usage"]
}
```

### Ejemplo Práctico Paso a Paso

```powershell
# 1. Trabaja en OpenCode durante 2 horas
opencode --agent orchestrator
# ... haces tu trabajo ...
# Sales de OpenCode

# 2. Guarda la sesión
python main.py --summarize
# ✔ Session saved: x1y2z3w4

# 3. Al día siguiente, verifica qué hiciste
python main.py --session-status
# Muestra resumen de la última sesión

# 4. Abre OpenCode — el orquestador ya sabe lo que pasó
opencode --agent orchestrator
# Lee context.md y continúa donde lo dejaste
```

---

## 4. Skills System

### ¿Qué son las Skills?

Las skills son **capacidades reutilizables** para agentes AI. Proveen conocimiento procedural, mejores prácticas, y guías específicas de dominio.

Browse skills en: [skills.sh](https://skills.sh)
Documentación: [skills.sh/docs](https://skills.sh/docs)

### Comandos

#### `--skills-search <query>` — Buscar skills

```powershell
python main.py --skills-search database
```

Output:
```
Skills Search: 'database'
┏━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃# ┃ Name                   ┃ Description ┃ Repo                        ┃
┡━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│1 │ neon-postgres          │ —           │ neondatabase/agent-skills   │
│2 │ prisma-database-setup  │ —           │ prisma/skills               │
│3 │ postgres               │ —           │ planetscale/database-skills │
│4 │ database-migration     │ —           │ wshobson/agents             │
│5 │ database               │ —           │ railwayapp/railway-skills   │
└──┴────────────────────────┴─────────────┴─────────────────────────────┘

Install with: python main.py --skills-install owner/repo/name
```

#### `--skills-install <owner/repo/name>` — Instalar skill

```powershell
python main.py --skills-install neondatabase/agent-skills/neon-postgres
```

Output:
```
✔ Skill 'neon-postgres' installed to .opencode/skills/
```

**¿Qué hace?**
1. Descarga el archivo `.md` desde GitHub
2. Lo guarda en `.opencode/skills/neon-postgres.md`
3. La próxima vez que se ejecute un agente, la skill se inyecta en `context.md`

#### `--skills` — Ver skills instaladas

```powershell
python main.py --skills
```

Output:
```
Installed Skills
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name          ┃ Description                ┃ Source               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ neon-postgres │ Best practices for Neon    │ neondatabase/agent-skills
└───────────────┴────────────────────────────┴──────────────────────┘
```

#### `--skills-remove <name>` — Remover skill

```powershell
python main.py --skills-remove neon-postgres
```

Output:
```
✔ Skill 'neon-postgres' removed.
```

### Ejemplo Práctico Completo

```powershell
# 1. Busca skills de React
python main.py --skills-search react

# 2. Instala la que necesites
python main.py --skills-install vercel-labs/agent-skills/vercel-react-best-practices

# 3. Verifica que se instaló
python main.py --skills

# 4. Usa OpenCode — la skill ya está en el contexto
opencode --agent orchestrator
# El orquestador y todos los agentes ahora conocen las mejores prácticas de React

# 5. Si ya no la necesitas
python main.py --skills-remove vercel-react-best-practices
```

### Dónde se Guardan

| Contenido | Directorio |
|-----------|------------|
| Skills instaladas | `.opencode/skills/*.md` |
| Contexto inyectado | `.opencode/context.md` (sección "Active Skills") |

---

## 5. Referencia CLI

### Todos los Argumentos

| Argumento | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--setup` | Fuerza el wizard de configuración | `python main.py --setup` |
| `--doctor` | Diagnóstico del entorno | `python main.py --doctor` |
| `--install-global` | Copia agentes a `~/.opencode/agents/` | `python main.py --install-global` |
| `--dir DIR` | Override del directorio raíz | `python main.py --dir C:\proyecto` |
| `--sessions` | Lista sesiones grabadas | `python main.py --sessions` |
| `--session <id>` | Detalle de sesión específica | `python main.py --session a3f8b2c1` |
| `--session-status` | Resumen de la última sesión | `python main.py --session-status` |
| `--summarize` | Escanea logs y guarda sesión | `python main.py --summarize` |
| `--skills` | Lista skills instaladas | `python main.py --skills` |
| `--skills-search <q>` | Busca skills en skills.sh | `python main.py --skills-search database` |
| `--skills-install <id>` | Instala skill desde skills.sh | `python main.py --skills-install owner/repo/name` |
| `--skills-remove <name>` | Remueve skill instalada | `python main.py --skills-remove neon-postgres` |

### Menú Interactivo

Si ejecutas `python main.py` sin argumentos (con agentes ya configurados):

```
? What would you like to do?
  ❯ View agent status
    Run setup wizard
    Run diagnostics
    Install globally
    View sessions
    View skills
    Exit
```

---

## 6. PlanManager

### ¿Qué es?

El PlanManager detecta automáticamente qué plan de OpenCode estás usando y asigna los modelos óptimos a cada agente.

### Planes Soportados

| Plan | Detección | Orchestrator |
|------|-----------|-------------|
| **Go** (default) | Default o `OPENCODE_PLAN=go` | `opencode-go/kimi-k2.6` |
| **Zen** | `GITHUB_TOKEN` o `COPILOT_TOKEN` | `opencode/claude-sonnet-4.5` |
| **API** | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4` |
| **Enterprise** | `OPENCODE_PLAN=enterprise` | `opencode-go/kimi-k2.6` |
| **OpenRouter** | `OPENROUTER_API_KEY` | `openrouter/anthropic/claude-sonnet-4.5` |
| **Copilot** | GitHub Copilot activo | `copilot/claude-sonnet-4` |
| **Ollama** | `OLLAMA_HOST` | `ollama/llama3.3:70b` |

### Cambiar de Plan

```powershell
# Forzar plan Go
$env:OPENCODE_PLAN="go"
python main.py --doctor

# Forzar plan API con Anthropic
$env:ANTHROPIC_API_KEY="sk-ant-..."
python main.py --doctor
```

---

## 7. Troubleshooting

### "OpenCode CLI not found"

```
⚠ OpenCode CLI not found
  Install from: https://opencode.ai
```

**Solución:** Instala OpenCode desde [opencode.ai/download](https://opencode.ai/download)

### "Execution policy error" en Windows

```
.\setup.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada
```

**Solución:**
```powershell
# Opción 1: Ejecutar con bypass
powershell -ExecutionPolicy Bypass -File setup.ps1

# Opción 2: Cambiar política (una sola vez, como Admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "No agents configured"

```
No previous agent configuration detected.
```

**Solución:**
```powershell
python main.py --setup
```

### "Invalid model IDs detected"

```
✖ Invalid model IDs detected:
    @orchestrator → opencode-go/old-model (not in registry)
```

**Solución:**
```powershell
python main.py --setup
# Esto regenera los agentes con modelos válidos
```

### "No logs found in .opencode/logs/"

```
No logs found in .opencode/logs/
Make sure OpenCode has been run in this project first.
```

**Solución:** Ejecuta OpenCode al menos una vez antes de `--summarize`:
```powershell
opencode --agent orchestrator
# Haz algo, luego sale
python main.py --summarize
```

### "requests library not installed"

```
requests library not installed. Run: pip install requests
```

**Solución:**
```powershell
pip install requests
```

---

## 8. Quick Reference Card

### Los 10 Comandos Más Usados

| # | Comando | Qué hace |
|---|---------|----------|
| 1 | `opencode --agent orchestrator` | Inicia el orquestador |
| 2 | `python main.py --doctor` | Diagnóstico completo |
| 3 | `python main.py --summarize` | Guarda bitácora de sesión |
| 4 | `python main.py --sessions` | Ver historial de sesiones |
| 5 | `python main.py --session-status` | Última sesión |
| 6 | `python main.py --skills-search <q>` | Buscar skills |
| 7 | `python main.py --skills-install <id>` | Instalar skill |
| 8 | `python main.py --skills` | Ver skills instaladas |
| 9 | `python main.py --install-global` | Instalar agentes globalmente |
| 10 | `python main.py --setup` | Reconfigurar agentes |

### Flujo de Trabajo Diario

```powershell
# Mañana
opencode --agent orchestrator    # Trabajar

# Al cerrar
python main.py --summarize       # Guardar bitácora

# Día siguiente
opencode --agent orchestrator    # Continuar donde lo dejaste
```

### Instalación en Nueva PC

```powershell
git clone https://github.com/visualiaconsulting/oh-my-agents.git
cd oh-my-agents
.\install.ps1
opencode --agent orchestrator
```

---

## Información del Proyecto

| Dato | Valor |
|------|-------|
| Repositorio | [visualiaconsulting/oh-my-agents](https://github.com/visualiaconsulting/oh-my-agents) |
| Versión | 1.2.2 |
| Licencia | MIT |
| Skills | [skills.sh](https://skills.sh) |
| OpenCode | [opencode.ai](https://opencode.ai) |
