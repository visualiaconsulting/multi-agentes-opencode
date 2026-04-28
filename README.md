# Multi-Agentes OpenCode (Plan Go)

Sistema multi-agente para **OpenCode Go** con arquitectura de **Orquestador y Especialistas**. El orquestador analiza tareas complejas, las desglosa y delega a subagentes especializados, validando el resultado final.

---

## 🤖 Agentes Configurados

| Agente | Modelo (Plan Go) | Rol | Permisos |
|--------|:----------------:|-----|----------|
| **@orchestrator** | `mimo-v2.5-pro` | Coordinador — divide tareas y delega | edit, bash, read, task |
| **@code-analyst** | `deepseek-v4-pro` | Implementación — escribe código limpio | edit, bash, read |
| **@validator** | `kimi-k2.6` | QA — valida calidad y revisa código | read only |
| **@bulk-processor** | `deepseek-v4-flash` | Datos masivos — tareas repetitivas (oculto) | edit, bash, read |
| **@subagent** | `mimo-v2.5-pro` | Depurador — tareas auxiliares y reserva | edit, bash, read |

---

## 🚀 Inicio Rápido (3 pasos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/visualiaconsulting/multi-agentes-opencode.git
cd multi-agentes-opencode

# 2. Ejecutar el setup (instala deps y configura agentes)
.\setup.ps1        # Windows
# o
./setup.sh         # Linux/Mac

# 3. ¡Listo! El asistente te guía para configurar tus agentes
```

> **¿Ya tienes OpenCode CLI?** El setup te dirá si falta. Instálalo desde [opencode.ai](https://opencode.ai).

---

## ⚠️ Issue Conocido: Modelos Qwen Deshabilitados (Resuelto)

Los modelos **Qwen3.6 Plus** y **Qwen3.5 Plus** están marcados como `deprecated` en el registry de OpenCode.

> **Solución aplicada:** Se cambió el modelo del orquestador a `opencode-go/mimo-v2.5-pro` (igual que el proyecto base que funciona sin errores). Se eliminó `opencode.jsonc` que causaba conflictos.

### Referencia
- Issue: [#22644](https://github.com/anomalyco/opencode/issues/22644)

---

## 🛠️ Instalación

### Requisitos
- **OpenCode CLI** instalado
- Suscripción activa a **OpenCode Go**
- API key configurada vía `/connect` o variable de entorno

### Uso directo desde este repositorio

```bash
# Clonar el repositorio
git clone https://github.com/visualiaconsulting/multi-agentes-opencode.git
cd multi-agentes-opencode
opencode --agent orchestrator
```

### Cómo copiar los agentes a otro proyecto

Para usar estos agentes en otro proyecto (ej. `carbon_footprint_tracker`):

```powershell
# 1. Crear directorio en el proyecto destino
mkdir proyecto\.opencode\agents

# 2. Copiar agentes
copy agentes\.opencode\agents\*.md proyecto\.opencode\agents\

# 3. Crear context.md adaptado al proyecto
echo "---
project: Mi Proyecto
plan: go
version: 1.0
---
Contexto del proyecto aquí..." > proyecto\.opencode\CONTEXT.md

# 4. Ejecutar desde el proyecto
cd proyecto
opencode --agent orchestrator
```

---

## 📁 Estructura del Proyecto

```
./
├── AGENTS.md                    # Estado detallado de agentes
├── README.md                    # Este documento
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

## 🧠 Ejemplos de uso

### Tarea de entrenamiento YOLO

```
> completa el entrenamiento de YOLO26n a 25 epochs con MuSGD y GPU 0
```

El orquestador:
1. Pide a `@code-analyst` preparar/completar el script de entrenamiento
2. Pide a `@validator` revisar que los parámetros sean correctos
3. Ejecuta el comando final consolidado

### Tarea de análisis

```
> revisa los resultados del último entrenamiento y compáralos con los anteriores
```

El orquestador:
1. Lee los CSV/results.csv
2. Pide a `@code-analyst` extraer métricas
3. Pide a `@validator` verificar si se cumplen los targets
4. Devuelve un resumen comparativo

---

## 🔧 plan_manager.py

Utilidad para detectar automáticamente el plan de OpenCode activo (`go`, `zen`, `api`, `enterprise`) y seleccionar los modelos adecuados para cada rol. Soporta override por variables de entorno.

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

---

## 📝 Changelog

### v9.0 — Sincronización con Proyecto Base (Abril 2026)

**Corrección crítica de modelos:** Los archivos `.opencode/agents/*.md` usaban nombres de presentación en vez de IDs de registro, causando `ProviderModelNotFoundError`.

| Archivo | Antes (roto) | Después (correcto) |
|---------|--------------|---------------------|
| `orchestrator.md` | `model: GLM-5.1` | `model: opencode-go/mimo-v2.5-pro` |
| `code-analyst.md` | `model: DeepSeek V4 Pro` | `model: opencode-go/deepseek-v4-pro` |
| `validator.md` | `model: Kimi K2.6` | `model: opencode-go/kimi-k2.6` |
| `bulk-processor.md` | `model: DeepSeek V4 Flash` | `model: opencode-go/deepseek-v4-flash` |
| `subagent.md` | `model: MiMo-V2.5-Pro` | `model: opencode-go/mimo-v2.5-pro` |

**Cambios adicionales:**
- Eliminado `opencode.jsonc` — causaba conflictos; el proyecto base no lo usa
- Modelo del orquestador: `glm-5.1` → `mimo-v2.5-pro` (consistente con proyecto base)
- Permisos del orquestador: `edit: allow`, `bash: allow` (como en el proyecto base)

### v8.0.1 — Verificación de Permisos (Abril 2026)

Auditoría de permisos: se eliminaron privilegios excesivos de escritura/ejecución en agentes que no los necesitan.

| Agente | Cambio | Antes | Después |
|--------|--------|-------|---------|
| **@orchestrator** | `edit` / `bash` | ✅ allow | ❌ deny |
| **@validator** | `edit` / `bash` | ✅ allow | ❌ deny |

El orquestador ahora es estrictamente **modo plan** (solo `read + task`), y el validator es **read only** (solo `read`). Toda escritura y ejecución se delega a los subagentes de ejecución.

### v0.8 — IDs de Registro y Correcciones (Abril 2026)

- Fix: Model IDs cambiados de nombres de presentación a IDs de registro (`opencode-go/*`)
- Fix: Ruta personal eliminada del README
- Fix: `plan_manager.py` actualizado con IDs de registro para todos los planes

---

## 🐛 Correcciones Recientes (Abril 2026)

| # | Problema | Solución |
|---|----------|----------|
| 1 | Orquestador apuntaba a `Qwen3.6 Plus` en vez de `GLM-5.1` | Sincronizado a `GLM-5.1` en `plan_manager.py` |
| 2 | Validator tenía permisos de edición/bash pese a ser "Read Only" | Permisos corregidos a `edit: deny`, `bash: deny` |
| 3 | `_detect_plan()` detectaba `api` erróneamente con `OPENCODE_API_KEY` | Removida del chequeo; solo `ANTHROPIC_API_KEY` → api |
| 4 | Bare `except` silenciaba errores al leer JSON | Especificadas excepciones concretas |
| 5 | Comentarios placeholder en `main.py` | Reemplazados por docstrings |
| 6 | Wizard proponía `Qwen3.6 Plus` como orquestador | Cambiado a `GLM-5.1` |
| 7 | Agentes usaban nombres de presentación en vez de IDs de registro | Cambiados a `opencode-go/*` |
| 8 | Orchestrator tenía `edit/bash: allow` pese a ser modo plan | Cambiado a `deny` — solo `read + task` |
| 9 | Validator tenía `edit/bash: allow` pese a ser "Read Only" | Cambiado a `deny` |
| 10 | `opencode.jsonc` causaba conflictos de configuración | Eliminado — el proyecto base no lo usa |
| 11 | Modelo del orquestador `glm-5.1` inconsistente con proyecto base | Cambiado a `opencode-go/mimo-v2.5-pro` |

---

## 🔗 Enlaces

- **Repositorio**: [visualiaconsulting/multi-agentes-opencode](https://github.com/visualiaconsulting/multi-agentes-opencode)
- **Organización**: [VisualIA Consulting](https://github.com/visualiaconsulting)

## 📄 Licencia

MIT
