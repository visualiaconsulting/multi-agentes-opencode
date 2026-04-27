# Multi-Agentes OpenCode (Plan Go) 🚀

Este repositorio contiene una implementación avanzada de un **Sistema Multi-Agente** optimizado para la suscripción **OpenCode Go**. La arquitectura permite la orquestación inteligente de tareas complejas mediante la delegación entre agentes especializados.

## 📋 Descripción del Sistema

El sistema utiliza el modelo de "Orquestador y Especialistas". El Orquestador analiza la petición del usuario y, si es compleja, desglosa la tarea y la delega a los subagentes pertinentes, validando finalmente el resultado.

### 🤖 Agentes Configurados

| Agente | Modelo Principal | Rol y Especialidad |
| :--- | :--- | :--- |
| **@orchestrator** | `mimo-v2.5-pro` | Coordinación, toma de decisiones y gestión de tareas (`task`). |
| **@code-analyst** | `deepseek-v4-pro` | Escritura de código, refactorización y análisis de arquitectura. |
| **@validator** | `kimi-k2.6` | Control de calidad (QA), testing y revisión de seguridad. |
| **@bulk-processor** | `deepseek-v4-flash` | Tareas repetitivas de alto volumen y procesamiento de datos. |

---

## 🛠️ Instalación y Uso

### 1. Requisitos Previos
*   **OpenCode CLI** instalado y actualizado.
*   Suscripción activa a **OpenCode Go**.
*   Git para control de versiones.

### 2. Configuración Local
Si acabas de clonar este repositorio, registra los agentes en tu sistema local:

```powershell
# Registrar el orquestador principal
opencode agent create --name orchestrator --path .opencode/agents --model opencode-go/mimo-v2.5-pro --mode primary

# Los subagentes se detectan automáticamente por el orquestador si están en .opencode/agents/
```

### 3. Ejecución
Inicia la sesión de trabajo con el comando:
```powershell
opencode --agent orchestrator
```

---

## 📁 Estructura del Repositorio

*   `/.opencode/agents/`: Definiciones de agentes (Prompts y configuraciones).
*   `/.opencode/context.md`: Contexto compartido global del proyecto.
*   `plan_manager.py`: Herramienta para migrar configuraciones entre diferentes planes de OpenCode.
*   `README.md`: Documentación principal.

---

## 🔗 Enlaces de Interés
*   **Repositorio Oficial**: [multi-agentes-opencode](https://github.com/visualiaconsulting/multi-agentes-opencode)
*   **Organización**: [VisualIA Consulting](https://github.com/visualiaconsulting)

---

## 📄 Licencia
Distribuido bajo la Licencia MIT. Para más detalles, ver el archivo `LICENSE`.
