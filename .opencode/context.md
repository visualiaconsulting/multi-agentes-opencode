---
project: oh-my-agents
plan: go
version: 1.0
---

# Contexto del Proyecto

Este es un sistema multi-agente configurado para el plan OpenCode Go.
Los agentes disponibles son:

- **@orchestrator** — Coordinador. Delega tareas complejas a subagentes. Modelo: opencode-go/mimo-v2.5-pro
- **@code-analyst** — Ingeniero senior. Implementa código limpio y eficiente. Modelo: opencode-go/deepseek-v4-pro
- **@validator** — QA. Valida código y ejecuta pruebas (solo lectura). Modelo: opencode-go/kimi-k2.6
- **@bulk-processor** — Procesamiento masivo de datos (oculto). Modelo: opencode-go/deepseek-v4-flash
- **@subagent** — Depurador y agente de reserva para tareas auxiliares. Modelo: opencode-go/mimo-v2.5-pro

Para usar en otro proyecto, copia `.opencode/agents/` al proyecto destino
y modifica este `CONTEXT.md` con la descripción del proyecto real.
