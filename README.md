# Multi-Agentes OpenCode (Plan Go)

Sistema multi-agente para **OpenCode Go** con arquitectura de **Orquestador y Especialistas**. El orquestador analiza tareas complejas, las desglosa y delega a subagentes especializados, validando el resultado final.

---

## 🤖 Agentes Configurados

| Agente | Modelo (Plan Go) | Rol | Permisos |
|--------|:----------------:|-----|----------|
| **@orchestrator** | `glm-5.1` | Coordinador — divide tareas y delega | edit, read, task (sin bash) |
| **@code-analyst** | `deepseek-v4-pro` | Implementación — escribe código limpio | edit, bash, read |
| **@validator** | `kimi-k2.6` | QA — valida calidad y ejecuta pruebas | read only |
| **@bulk-processor** | `deepseek-v4-flash` | Datos masivos — tareas repetitivas (oculto) | edit, bash, read |
| **@subagent** | `mimo-v2.5-pro` | Depurador — tareas auxiliares y reserva | edit, bash, read |

---

## ⚠️ Issue Conocido: Modelos Qwen Deshabilitados

Los modelos **Qwen3.6 Plus** y **Qwen3.5 Plus** están marcados como `deprecated` en el registry de OpenCode. Para habilitarlos en el plan Go, se incluye `opencode.jsonc` con el workaround que fuerza el status `beta`.

### Solución en opencode.jsonc

```jsonc
"provider": {
  "opencode-go": {
    "models": {
      "glm-5.1": {
        "name": "GLM-5.1",
        "reasoning": true
      },
      "qwen3.6-plus": {
        "name": "Qwen3.6 Plus",
        "reasoning": true,
        "status": "beta"
      },
      "qwen3.5-plus": {
        "name": "Qwen3.5 Plus",
        "reasoning": true,
        "status": "beta"
      }
    }
  }
}
```

> **Nota:** Si el workaround no funciona, cambia el modelo del orquestador a `mimo-v2.5-pro` en `.opencode/agents/orchestrator.md`.

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
├── opencode.jsonc               # Configuración global de OpenCode
├── plan_manager.py              # Lógica de selección de modelos
├── main.py                      # CLI del sistema multi-agente
├── cli/
│   ├── wizard.py                # Asistente de configuración interactivo
│   └── ui.py                    # Componentes visuales (rich)
└── .opencode/
    ├── CONTEXT.md               # Contexto global inyectado a todos los agentes
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
| **Go** (defecto) | Por omisión o `OPENCODE_PLAN=go` | `opencode-go/glm-5.1` |
| **Zen** | `GITHUB_TOKEN` o `COPILOT_TOKEN` | `opencode/claude-sonnet-4.5` |
| **API** | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4` (configurable) |
| **Enterprise** | `OPENCODE_PLAN=enterprise` | `opencode-go/mimo-v2.5-pro` (configurable) |

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

---

## 🔗 Enlaces

- **Repositorio**: [visualiaconsulting/multi-agentes-opencode](https://github.com/visualiaconsulting/multi-agentes-opencode)
- **Organización**: [VisualIA Consulting](https://github.com/visualiaconsulting)

## 📄 Licencia

MIT
