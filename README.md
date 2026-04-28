# Multi-Agentes OpenCode (Plan Go) 🚀

Sistema multi-agente para **OpenCode Go** con arquitectura de **Orquestador y Especialistas**. El orquestador analiza tareas complejas, las desglosa y delega a subagentes especializados, validando el resultado final.

## 🤖 Agentes Configurados

| Agente | Modelo | Rol | Permisos |
|--------|--------|-----|----------|
| **@orchestrator** | `mimo-v2.5-pro` | Coordinador — divide tareas y delega | full (edit, bash, read, task) |
| **@code-analyst** | `deepseek-v4-pro` | Implementación — escribe código limpio | edit, bash, read |
| **@validator** | `kimi-k2.6` | QA — valida calidad, solo lectura | read only |
| **@bulk-processor** | `deepseek-v4-flash` | Datos masivos — tareas repetitivas | edit, bash, read (hidden) |

---

## 🛠️ Instalación

### Requisitos
- **OpenCode CLI** instalado
- Suscripción activa a **OpenCode Go**
- API key configurada vía `/connect` o variable de entorno

### Uso directo desde este repositorio

```powershell
cd C:\Users\ekrde\OneDrive\ML2025\Investigacion\agentes
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
Contexto del proyecto aquí..." > proyecto\.opencode\context.md

# 4. Ejecutar desde el proyecto
cd proyecto
opencode --agent orchestrator
```

---

## 📁 Estructura

```
.opencode/
├── context.md                 # Contexto global del proyecto
└── agents/
    ├── orchestrator.md        # Coordinador principal
    ├── code-analyst.md        # Implementación de código
    ├── validator.md           # QA y validación
    └── bulk-processor.md      # Procesamiento masivo (hidden)
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

Utilidad para detectar automáticamente el plan de OpenCode activo (go, zen, api, enterprise) y seleccionar los modelos adecuados para cada rol. Soporta override por variables de entorno.

```python
from plan_manager import PlanManager
pm = PlanManager()
print(pm.get_model("orchestrator"))  # Modelo según plan detectado
```

---

## 🔗 Enlaces

- **Repositorio**: [visualiaconsulting/multi-agentes-opencode](https://github.com/visualiaconsulting/multi-agentes-opencode)
- **Organización**: [VisualIA Consulting](https://github.com/visualiaconsulting)

## 📄 Licencia

MIT
