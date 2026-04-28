import sys
import argparse
from pathlib import Path
import yaml
from cli.ui import print_header, print_agent_status, console
from cli.wizard import SetupWizard

def load_agents():
    """Carga las definiciones de agentes desde .opencode/agents/*.md"""
    agent_dir = Path(".opencode/agents")
    agents = []
    if not agent_dir.exists():
        return agents
    
    for md_file in agent_dir.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---')
                    if len(parts) >= 3:
                        metadata = yaml.safe_load(parts[1])
                        name = metadata.get('name', md_file.stem)
                        agents.append({
                            'name': f"@{name}",
                            'role': metadata.get('mode', 'subagent').capitalize(),
                            'model': metadata.get('model', 'unknown'),
                        })
        except Exception as e:
            continue
    return agents

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent CLI")
    parser.add_argument("--setup", action="store_true", help="Forzar la configuración inicial de agentes")
    args = parser.parse_args()

    print_header()
    
    wizard = SetupWizard()
    
    # Ejecutar si se pide por parámetro o si no hay configuración
    if args.setup or not wizard.check_existing_config():
        if args.setup:
            console.print("[yellow]Modo de reconfiguración forzado...[/yellow]\n")
        else:
            console.print("[yellow]No se detectó configuración previa. Iniciando asistente...[/yellow]\n")
        wizard.run()
    
    agents = load_agents()
    # Mostrar estado de los agentes cargados
    
    if agents:
        print_agent_status(agents)
        console.print("\n[bold green]Sistema listo.[/bold green] Usa `opencode --agent orchestrator` para empezar.")
    else:
        console.print("[red]Error: No se pudieron cargar los agentes.[/red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
        sys.exit(0)
