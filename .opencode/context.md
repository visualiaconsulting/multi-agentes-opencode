---
project: Multi-Agent System Template
plan: go
version: 1.0
---

# Contexto del Proyecto

Este es un sistema multi-agente configurado para el plan OpenCode Go.
Los agentes disponibles son:

- **@orchestrator** — Coordinador. Delega tareas complejas a subagentes. Modelo: GLM-5.1
- **@code-analyst** — Ingeniero senior. Implementa código limpio y eficiente. Modelo: DeepSeek V4 Pro
- **@validator** — QA. Valida código y ejecuta pruebas (solo lectura). Modelo: Kimi K2.6
- **@bulk-processor** — Procesamiento masivo de datos (oculto). Modelo: DeepSeek V4 Flash
- **@subagent** — Depurador y agente de reserva para tareas auxiliares. Modelo: MiMo-V2.5-Pro

Para usar en otro proyecto, copia `.opencode/agents/` al proyecto destino
y modifica este `CONTEXT.md` con la descripción del proyecto real.
