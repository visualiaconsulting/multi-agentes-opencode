# Estado de Agentes — oh-my-agents

Este documento describe la configuración, estado y arquitectura del sistema multi-agente del proyecto.

---

## 📋 Resumen del Sistema

El proyecto implementa una arquitectura de **Orquestador y Especialistas** sobre el plan **OpenCode Go** por defecto, con capacidad de adaptación dinámica a otros planes (Zen, API, Enterprise, OpenRouter, Copilot, Ollama) mediante el `PlanManager`.

| Componente | Descripción |
|------------|-------------|
| **Orquestador** | Agente principal que divide tareas complejas y delega a subagentes |
| **Especialistas** | Agentes secundarios con roles específicos (código, QA, datos) |
| **PlanManager** | Módulo Python que detecta el plan activo y asigna modelos |

---

## 🤖 Agentes Configurados

| Agente | Rol | Modelo (Plan Go) | Permisos | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **@orchestrator** | Coordinador Principal | `opencode-go/mimo-v2.5-pro` | `Read, Task` | Divide tareas complejas y delega a subagentes. NO escribe código ni ejecuta comandos. |
| **@code-analyst** | Ingeniero Senior | `opencode-go/deepseek-v4-pro` | `Edit, Bash, Read` | Implementación de código limpio y arquitectura. |
| **@validator** | Especialista QA | `opencode-go/kimi-k2.6` | `Read Only` | Validación, linting y revisión de calidad. Sin edición ni bash. |
| **@bulk-processor** | Procesador de Datos | `opencode-go/deepseek-v4-flash` | `Edit, Bash, Read` | Tareas repetitivas y de gran volumen (oculto). |
| **@subagent** | Depurador/Reserva | `opencode-go/glm-5.1` | `Edit, Bash, Read` | Agente genérico para depuración y tareas auxiliares. |

### 🔍 Detalle de Permisos por Agente

| Agente | edit | bash | read | task |
|--------|:----:|:----:|:----:|:----:|
| **@orchestrator** | ❌ deny | ❌ deny | ✅ allow | ✅ allow |
| **@code-analyst** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |
| **@validator** | ❌ deny | ❌ deny | ✅ allow | ❌ deny |
| **@bulk-processor** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |
| **@subagent** | ✅ allow | ✅ allow | ✅ allow | ❌ deny |

---

## 🛠️ Infraestructura de Código

### `plan_manager.py` — Núcleo de Configuración Dinámica

El `PlanManager` es el cerebro lógico que gestiona la configuración de agentes según el plan detectado:

- **Detección de Plan:** Identifica automáticamente si se está en `go`, `zen`, `api`, `enterprise`, `openrouter`, `copilot` u `ollama` usando variables de entorno y archivos de configuración.
- **Mapeo de Modelos:** Asocia cada rol (`orchestrator`, `code-analyst`, `validator`, `bulk-processor`, `subagent`) con el modelo óptimo para el plan activo.
- **Fallbacks:** Proporciona modelos de respaldo si el principal no está disponible.
- **Validación de API Keys:** Verifica que los proveedores externos tengan las credenciales necesarias (solo para planes `api` y `openrouter`).

**Modelos por defecto en Plan Go:**

| Rol | Modelo |
|:---|:---|
| Orchestrator | `opencode-go/mimo-v2.5-pro` |
| Code Analyst | `opencode-go/deepseek-v4-pro` |
| Validator | `opencode-go/kimi-k2.6` |
| Bulk Processor | `opencode-go/deepseek-v4-flash` |
| Subagent | `opencode-go/glm-5.1` |
| Fallback | `opencode-go/minimax-m2.5` |

### ~~`opencode.jsonc`~~ — Eliminado

> **Nota:** El archivo `opencode.jsonc` fue eliminado porque causaba conflictos de configuración. OpenCode lee la configuración directamente de los archivos `.opencode/agents/*.md`.

### `main.py` — CLI del Sistema

Interfaz de línea de comandos que:
- Muestra el banner del sistema multi-agente
- Ejecuta el asistente de configuración (`--setup`) si no hay agentes definidos
- Carga y muestra el estado de los agentes desde `.opencode/agents/*.md`

### `cli/wizard.py` — Asistente de Configuración

Wizard interactivo que propone configuraciones por defecto o guía al usuario en la creación manual de agentes. Por defecto asigna `opencode-go/mimo-v2.5-pro` al orquestador.

### `cli/ui.py` — Interfaz de Usuario

Componentes visuales con `rich` para terminal: banners, tablas de agentes, paneles, y mensajes con estilo.

---

## ⚠️ Issue Conocido: Modelos Qwen Deshabilitados (Resuelto)

Los modelos **Qwen3.6 Plus** y **Qwen3.5 Plus** están marcados como `deprecated` en el registry de OpenCode.

> **Solución aplicada:** Se eliminaron de la lista de modelos disponibles en `plan_manager.py`. Se cambió el modelo del orquestador a `opencode-go/mimo-v2.5-pro`. Se eliminó `opencode.jsonc` que causaba conflictos.

### Referencia
- Issue: [#22644](https://github.com/anomalyco/opencode/issues/22644)

---

## 📝 Changelog

### v0.9.2.1 — Modelo Subagent Corregido + Preparación Multi-Plan (April 2026)

**Modelo subagent:** Cambiado de `opencode-go/mimo-v2.5-pro` a `opencode-go/glm-5.1` para eliminar duplicación con el orchestrator.

**Nuevos planes soportados en PlanManager:**
- `openrouter` — Modelos configurables vía OPENROUTER_API_KEY
- `copilot` — GitHub Copilot models
- `ollama` — Modelos locales auto-hospedados

**Correcciones de documentación:**
- AGENTS.md: Permisos del orchestrator corregidos a `read + task` (no edit/bash)
- AGENTS.md: Eliminada nota contradictoria sobre reversión de permisos
- AGENTS.md: Referencias a GLM-5.1 actualizadas a mimo-v2.5-pro
- README.md: Modelo del subagent actualizado

**Modelos finales (sin duplicados):**

| Agente | Modelo |
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

### v0.9.1.0 — Sincronización con Proyecto Base (Abril 2026)

**Corrección crítica de modelos:** Los archivos `.opencode/agents/*.md` usaban nombres de presentación (`GLM-5.1`, `DeepSeek V4 Pro`) en vez de IDs de registro (`opencode-go/mimo-v2.5-pro`, `opencode-go/deepseek-v4-pro`), causando `ProviderModelNotFoundError`.

| Archivo | Antes (roto) | Después (correcto) |
|---------|--------------|---------------------|
| `orchestrator.md` | `model: GLM-5.1` | `model: opencode-go/mimo-v2.5-pro` |
| `code-analyst.md` | `model: DeepSeek V4 Pro` | `model: opencode-go/deepseek-v4-pro` |
| `validator.md` | `model: Kimi K2.6` | `model: opencode-go/kimi-k2.6` |
| `bulk-processor.md` | `model: DeepSeek V4 Flash` | `model: opencode-go/deepseek-v4-flash` |
| `subagent.md` | `model: MiMo-V2.5-Pro` | `model: opencode-go/glm-5.1` |

**Cambios adicionales:**
- Eliminado `opencode.jsonc` — causaba conflictos; el proyecto base no lo usa
- Modelo del orquestador cambiado de `glm-5.1` a `mimo-v2.5-pro` (consistente con proyecto base)
- Permisos del orquestador: `edit: deny`, `bash: deny`, `read: allow`, `task: allow`
- Actualizada documentación (`AGENTS.md`, `README.md`, `context.md`)

---

### v0.9.0.0 — Verificación de Permisos (Abril 2026)

**Auditoría de permisos de agentes:** Se verificó que cada agente tiene exactamente los permisos que corresponden a su rol, eliminando privilegios excesivos que permitían escritura/ejecución donde no correspondía.

| Agente | Cambio | Antes | Después |
|--------|--------|-------|---------|
| **@orchestrator** | `edit` | ✅ allow | ❌ deny |
| **@orchestrator** | `bash` | ✅ allow | ❌ deny |
| **@validator** | `edit` | ✅ allow | ❌ deny |
| **@validator** | `bash` | ✅ allow | ❌ deny |

**Permisos finales verificados:**

| Agente | edit | bash | read | task | Modo |
|--------|:----:|:----:|:----:|:----:|------|
| **@orchestrator** | ❌ deny | ❌ deny | ✅ allow | ✅ allow | Coordinación — delega a subagentes |
| **@code-analyst** | ✅ allow | ✅ allow | ✅ allow | ❌ deny | Ejecución — escribe y ejecuta |
| **@validator** | ❌ deny | ❌ deny | ✅ allow | ❌ deny | Read Only — solo revisa y reporta |
| **@bulk-processor** | ✅ allow | ✅ allow | ✅ allow | ❌ deny | Ejecución — procesamiento masivo |
| **@subagent** | ✅ allow | ✅ allow | ✅ allow | ❌ deny | Ejecución — depuración y reserva |

**Descripciones de rol actualizadas:**
- **Orchestrator**: Ahora indica explícitamente *"NO escribes código ni ejecutas comandos directamente — delegas toda implementación a los subagentes"*
- **Validator**: Ahora indica explícitamente *"NO escribes ni ejecutas código. Solo lees y reportas hallazgos"*

**Archivos modificados:**
- `.opencode/agents/orchestrator.md` — permisos y descripción
- `.opencode/agents/validator.md` — permisos y descripción
- `AGENTS.md` — tablas de permisos y correcciones
- `README.md` — tabla de permisos

---

### v0.8.0 — IDs de Registro y Correcciones (Abril 2026)

- Fix: Model IDs cambiados de nombres de presentación a IDs de registro (`opencode-go/*`)
- Fix: Ruta personal eliminada del README
- Fix: `plan_manager.py` actualizado con IDs de registro para todos los planes
- Fix: `_detect_plan()` fallback corregido de `api` a `go`
- Fix: Bare `except` → `(json.JSONDecodeError, OSError)`
- Add: `subagent.md`, `main.py`, `cli/` al repositorio

---

## 🐛 Correcciones Recientes Aplicadas (Abril 2026)

| # | Problema | Archivo | Solución |
|---|----------|---------|----------|
| 1 | Orquestador inconsistente: `plan_manager.py` apuntaba a `Qwen3.6 Plus` | `plan_manager.py` | Cambiado a `opencode-go/mimo-v2.5-pro` |
| 2 | Validator con permisos de edición/bash pese a ser "Read Only" | `validator.md` | `edit: deny`, `bash: deny` |
| 3 | `_detect_plan()` retornaba `"api"` si existía `OPENCODE_API_KEY` | `plan_manager.py` | Removida del chequeo; solo `ANTHROPIC_API_KEY` → api |
| 4 | Bare `except` silenciaba todas las excepciones al leer JSON | `plan_manager.py` | Especificadas `(json.JSONDecodeError, OSError)` |
| 5 | Comentarios placeholder en `main.py` | `main.py` | Reemplazados por docstrings |
| 6 | Wizard proponía `Qwen3.6 Plus` como orquestador | `cli/wizard.py` | Cambiado a `opencode-go/mimo-v2.5-pro` |
| 7 | Agentes usaban nombres de presentación en vez de IDs de registro | `*.md`, `plan_manager.py` | Cambiados a IDs `opencode-go/*` |
| 8 | Orchestrator tenía `edit/bash: allow` pese a ser modo plan | `orchestrator.md` | Cambiado a `deny` — solo `read + task` |
| 9 | Validator tenía `edit/bash: allow` pese a ser "Read Only" | `validator.md` | Cambiado a `deny` |
| 10 | `opencode.jsonc` causaba conflictos de configuración | `opencode.jsonc` | Eliminado |
| 11 | Modelo del orquestador inconsistente con proyecto base | `orchestrator.md` | Cambiado a `opencode-go/mimo-v2.5-pro` |

---

## 📁 Estructura de Archivos

```
./
├── AGENTS.md                    # Este documento (estado de agentes)
├── README.md                    # Documentación principal del proyecto
├── plan_manager.py              # Lógica de selección de modelos
├── main.py                      # CLI del sistema multi-agente
├── cli/
│   ├── wizard.py                # Asistente de configuración interactivo
│   └── ui.py                    # Componentes visuales (rich)
└── .opencode/
    ├── context.md               # Contexto global inyectado a todos los agentes
    └── agents/
        ├── orchestrator.md      # Coordinador principal
        ├── code-analyst.md      # Ingeniero de software senior
        ├── validator.md         # QA y validación de código
        ├── bulk-processor.md    # Procesamiento masivo (oculto)
        └── subagent.md          # Depurador / agente de reserva
```

---

## 🔧 Uso del PlanManager

```python
from plan_manager import PlanManager

pm = PlanManager()
print(f"Plan detectado: {pm.plan}")
print(f"Modelo orquestador: {pm.get_model('orchestrator')}")
print(f"Modelos disponibles: {pm.get_available_models()}")
```

### Planes Soportados

| Plan | Método de Detección | Modelo Orquestador |
|------|---------------------|--------------------|
| **Go** (defecto) | Por omisión o `OPENCODE_PLAN=go` | `opencode-go/mimo-v2.5-pro` |
| **Zen** | `GITHUB_TOKEN` o `COPILOT_TOKEN` | `opencode/claude-sonnet-4.5` |
| **API** | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4` (configurable) |
| **Enterprise** | `OPENCODE_PLAN=enterprise` | `opencode-go/mimo-v2.5-pro` (configurable) |
| **OpenRouter** | `OPENROUTER_API_KEY` | `openrouter/anthropic/claude-sonnet-4.5` (configurable) |
| **Copilot** | GitHub Copilot activo | `copilot/claude-sonnet-4` |
| **Ollama** | `OLLAMA_HOST` o Ollama corriendo | `ollama/llama3.3:70b` (configurable) |

---

## 🚀 Próximos Pasos Sugeridos

1. **Validación de Conectividad:** Ejecutar `python main.py` para verificar que el PlanManager detecta correctamente el entorno.
2. **Pruebas de Delegación:** Usar `opencode --agent orchestrator` con una tarea compleja para validar la interacción entre agentes.
3. **Personalización de Contexto:** Actualizar `.opencode/CONTEXT.md` si el proyecto escala a un dominio específico.
4. **Integración Continua:** Agregar linters y validadores automáticos para mantener la consistencia de la configuración.

---

## 🔗 Enlaces

- **Repositorio**: [visualiaconsulting/oh-my-agents](https://github.com/visualiaconsulting/oh-my-agents)
- **Organización**: [VisualIA Consulting](https://github.com/visualiaconsulting)
- **Licencia**: MIT
