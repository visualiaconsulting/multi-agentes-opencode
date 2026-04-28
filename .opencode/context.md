---
project: Multi-Agent System Template
plan: go
version: 1.0
---

# Contexto del Proyecto

Este es un sistema multi-agente configurado para el plan OpenCode Go.
Los agentes disponibles son:

- **@orchestrator** — Coordinador. Delega tareas complejas a subagentes.
- **@code-analyst** — Ingeniero senior. Implementa código limpio y eficiente.
- **@validator** — QA. Valida código y ejecuta pruebas (solo lectura).
- **@bulk-processor** — Procesamiento masivo de datos (oculto).

Para usar en otro proyecto, copia `.opencode/agents/` al proyecto destino
y modifica este `context.md` con la descripción del proyecto real.
