import os
import questionary
from pathlib import Path
from rich.prompt import Prompt, Confirm
from cli.ui import console, print_step, print_success, print_error
from plan_manager import PlanManager

AGENT_DIR = Path(".opencode/agents")

class SetupWizard:
    def __init__(self):
        self.pm = PlanManager()
        self.agents = []

    def check_existing_config(self):
        if not AGENT_DIR.exists():
            return False
        return len(list(AGENT_DIR.glob("*.md"))) > 0

    def run(self):
        print_step("Bienvenido al Asistente de Configuración de Agentes")
        
        # Proponer configuración por defecto
        self.propose_defaults()
        
        accept = questionary.select(
            "¿Cómo deseas proceder?",
            choices=[
                {"name": "Aceptar configuración por defecto", "value": "default"},
                {"name": "Configurar cada agente manualmente", "value": "manual"}
            ]
        ).ask()

        if accept == "default":
            self.setup_defaults()
        else:
            # Limpiar por si acaso
            self.agents = []
            # 1. Definir Orquestador
            self.setup_agent(role="orchestrator", is_primary=True)
            
            # 2. Definir Subagentes
            add_more = True
            while add_more:
                self.setup_agent(role="subagent")
                add_more = questionary.confirm("¿Quieres añadir otro subagente?", default=True).ask()
        
        self.save_all()
        print_success("Configuración completada con éxito.")

    def propose_defaults(self):
        """Muestra la tabla de lo que se va a configurar por defecto"""
        from rich.table import Table
        table = Table(title="Configuración Sugerida (Plan Go)", border_style="accent")
        table.add_column("Agente", style="cyan")
        table.add_column("Modelo", style="white")
        table.add_column("Rol", style="dim")

        table.add_row("orchestrator", "GLM-5.1", "Primary")
        table.add_row("code-analyst", "DeepSeek V4 Pro", "Subagent")
        table.add_row("validator", "Kimi K2.6", "Subagent")
        table.add_row("bulk-processor", "DeepSeek V4 Flash", "Subagent")
        table.add_row("subagent", "MiMo-V2.5-Pro", "Reserva")
        table.add_row("fallback", "MiniMax M2.5", "Speed/Recovery")
        
        console.print(table)

    def setup_defaults(self):
        """Configura los agentes recomendados automáticamente"""
        self.agents = [] # Reset
        defaults = [
            {"name": "orchestrator", "role": "primary", "model": "GLM-5.1", "desc": "Orquestador central del sistema"},
            {"name": "code-analyst", "role": "subagent", "model": "DeepSeek V4 Pro", "desc": "Ingeniero de software senior"},
            {"name": "validator", "role": "subagent", "model": "Kimi K2.6", "desc": "QA y validador de código"},
            {"name": "bulk-processor", "role": "subagent", "model": "DeepSeek V4 Flash", "desc": "Procesamiento masivo de datos"},
            {"name": "subagent", "role": "subagent", "model": "MiMo-V2.5-Pro", "desc": "Agente de reserva y tareas genéricas"}
        ]

        for d in defaults:
            agent_config = {
                "name": d["name"],
                "description": d["desc"],
                "mode": d["role"],
                "model": d["model"],
                "permissions": {
                    "edit": "allow",
                    "bash": "allow",
                    "read": "allow",
                    "task": "allow" if d["role"] == "primary" else "deny"
                }
            }
            self.agents.append(agent_config)

    def setup_agent(self, role="subagent", is_primary=False):
        console.print(f"\n[bold accent]Configurando {'Orquestador' if is_primary else 'Subagente'}[/bold accent]")
        
        default_name = "@orchestrator" if is_primary else "@subagent"
        name = questionary.text("Nombre del agente:", default=default_name).ask()
        
        description = questionary.text("Descripción corta del rol:").ask()
        
        # Selección de modelo con flechas
        available_models = self.pm.get_available_models()
        default_model = self.pm.get_model("orchestrator" if is_primary else "code-analyst")
        
        model = questionary.select(
            f"Seleccione un modelo para el plan '{self.pm.plan}':",
            choices=available_models,
            default=default_model
        ).ask()
        
        # Permisos con confirmación elegante
        allow_edit = questionary.confirm("¿Permitir edición de archivos?", default=True).ask()
        allow_bash = questionary.confirm("¿Permitir ejecución de comandos bash?", default=True).ask()
        
        agent_config = {
            "name": name.replace("@", ""),
            "description": description,
            "mode": "primary" if is_primary else "subagent",
            "model": model,
            "permissions": {
                "edit": "allow" if allow_edit else "deny",
                "bash": "allow" if allow_bash else "deny",
                "read": "allow",
                "task": "allow" if is_primary else "deny"
            }
        }
        self.agents.append(agent_config)

    def save_all(self):
        AGENT_DIR.mkdir(parents=True, exist_ok=True)
        for agent in self.agents:
            file_path = AGENT_DIR / f"{agent['name']}.md"
            content = self._format_md(agent)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def _format_md(self, agent):
        return f"""---
name: {agent['name']}
description: {agent['description']}
mode: {agent['mode']}
model: {agent['model']}
temperature: 0.2
permission:
  edit: {agent['permissions']['edit']}
  bash: {agent['permissions']['bash']}
  read: {agent['permissions']['read']}
  task: {agent['permissions']['task']}
---

{agent['description']}. Tu objetivo es cumplir con las peticiones del usuario de manera eficiente.
"""
