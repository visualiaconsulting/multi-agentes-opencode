# 💡 Ideas para el Futuro — oh-my-agents

> Roadmap de features, mejoras y extensiones posibles para el proyecto.
> Última actualización: abril 2026

---

## 🔌 Integraciones

| Idea | Descripción | Impacto |
|------|-------------|---------|
| **VS Code Extension** | Panel lateral que muestra agentes activos, sesiones, y permite ejecutar comandos sin terminal | Alto — accesibilidad |
| **GitHub Action** | CI/CD que ejecuta `--doctor` y tests en cada PR | Medio — calidad |
| **Slack/Discord Bot** | Notificaciones cuando una sesión termina con errores | Bajo — nice-to-have |
| **Web Dashboard** | UI web para ver sesiones, skills, y métricas de uso de agentes | Medio — visibilidad |

---

## 🤖 Agentes Nuevos

| Agente | Modelo Sugerido | Rol |
|--------|-----------------|-----|
| `@doc-writer` | Qwen 3.6 Plus (1M context) | Genera documentación automáticamente desde el código |
| `@security-auditor` | MiMo V2.5 Pro (94% precisión) | Escanea vulnerabilidades, OWASP, dependencias |
| `@translator` | MiniMax M2.5 | Traduce docs entre idiomas |
| `@refactorer` | DeepSeek V4 Pro | Refactoring de código legacy con análisis de impacto |
| `@test-generator` | Kimi K2.6 | Genera tests unitarios automáticamente |

---

## 🧩 Skills Avanzadas

| Idea | Descripción |
|------|-------------|
| **Auto-detección de skills** | ~~Analizar `package.json`, `requirements.txt`, `Cargo.toml` y sugerir skills automáticamente~~ → Implemented in v1.5.0 as `skill_recommender.py` ✅ |
| **Skills locales** | Permitir que el usuario cree sus propias skills en `.opencode/skills/custom/` |
| **Skill bundles** | Agrupar skills por stack (ej: "React Stack" = React + Tailwind + shadcn) |
| **Skills versioning** | Actualizar skills instaladas cuando hay nuevas versiones en skills.sh |

---

## 📝 Session Management

| Idea | Descripción |
|------|-------------|
| **Resumen automático** | Que el `@summarizer` se ejecute automáticamente al cerrar OpenCode (hook) |
| **Comparación de sesiones** | `--session-diff <id1> <id2>` para ver qué cambió entre sesiones |
| **Exportar bitácora** | `--session-export markdown` para compartir el historial |
| **Métricas de productividad** | Archivos por sesión, errores por día, tiempo promedio entre sesiones |
| **Tags de sesión** | Poner etiquetas a sesiones ("refactor", "bugfix", "feature") para filtrar |

---

## 🔧 CLI y UX

| Idea | Descripción |
|------|-------------|
| **`oma` CLI nativa** | Wrapper en Go/Rust compilado — más rápido que `python main.py` |
| **Shell completions** | Autocompletado para PowerShell y bash |
| **`--watch` mode** | Monitorear `.opencode/logs/` en tiempo real y actualizar bitácora automáticamente |
| **Configuración por proyecto** | `.opencode/oh-my-agents.yaml` con overrides por proyecto |
| **Modo interactivo de skills** | `python main.py --skills-browse` con navegación por categorías |

---

## 🏗️ Arquitectura

| Idea | Descripción |
|------|-------------|
| **Plugin system** | Permitir que terceros creen agentes como plugins instalables |
| **Multi-proyecto** | `~/.opencode/projects/` con bitácoras separadas por proyecto |
| **Agent marketplace** | Registry centralizado de agentes custom (como skills.sh pero para agentes) |
| **Config inheritance** | Heredar configuración de un proyecto base y override por proyecto |
| **Model fallback chain** | Si Kimi K2.6 no está disponible, usar automáticamente DeepSeek V4 Pro |

---

## 📊 Observabilidad

| Idea | Descripción |
|------|-------------|
| **Usage tracking** | Cuántos créditos consume cada agente por sesión |
| **Error patterns** | Detectar errores recurrentes y sugerir fixes automáticos |
| **Agent performance** | Qué agente resuelve más tareas, cuál falla más |
| **Cost dashboard** | Visualizar costo por modelo, por día, por proyecto |

---

## 🎯 Prioridad Sugerida

| Prioridad | Idea | Esfuerzo | Impacto |
|:---------:|------|:--------:|:-------:|
| 1 | ~~Auto-detección de skills por proyecto~~ → Implemented in v1.5.0 as `skill_recommender.py` ✅ | Bajo | Alto |
| 2 | Resumen automático al cerrar OpenCode | Bajo | Alto |
| 3 | Skills locales custom | Medio | Medio |
| 4 | `--session-diff` entre sesiones | Medio | Medio |
| 5 | Agent `@security-auditor` | Medio | Alto |
| 6 | Agent `@doc-writer` | Medio | Medio |
| 7 | Shell completions | Bajo | Medio |
| 8 | VS Code Extension | Alto | Alto |
| 9 | Web Dashboard | Alto | Medio |
| 10 | Agent marketplace | Alto | Alto |

---

## 📋 Notas

- Las ideas se pueden implementar de forma independiente
- Priorizar las de bajo esfuerzo y alto impacto primero
- Algunas ideas requieren cambios en OpenCode (hooks, API) — dependen del equipo de OpenCode
- Otras son puramente internas y se pueden implementar hoy

---

*Este documento es para referencia personal. No forma parte de la documentación oficial del proyecto.*
