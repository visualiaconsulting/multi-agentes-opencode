import sys
import argparse
from pathlib import Path


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    missing = []
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
    try:
        import questionary
    except ImportError:
        missing.append("questionary")
    try:
        import rich
    except ImportError:
        missing.append("rich")
    return missing


def check_opencode_cli():
    """Verifica que OpenCode CLI esté disponible"""
    import shutil
    return shutil.which("opencode") is not None


def run_doctor():
    """Diagnostica problemas del entorno"""
    import platform
    from cli.ui import console

    console.print("\n[bold cyan]=== Diagnóstico del Sistema ===[/bold cyan]\n")

    # Python
    py_ver = platform.python_version()
    major, minor = map(int, py_ver.split(".")[:2])
    if major >= 3 and minor >= 8:
        console.print(f"  [green]✔[/green] Python {py_ver}")
    else:
        console.print(f"  [red]✖[/red] Python {py_ver} (se requiere 3.8+)")

    # Dependencias
    missing = check_dependencies()
    if missing:
        console.print(f"  [red]✖[/red] Dependencias faltantes: {', '.join(missing)}")
        console.print(f"    Ejecuta: [bold]pip install -r requirements.txt[/bold]")
    else:
        console.print(f"  [green]✔[/green] Dependencias instaladas (PyYAML, questionary, rich)")

    # OpenCode CLI
    if check_opencode_cli():
        console.print(f"  [green]✔[/green] OpenCode CLI disponible")
    else:
        console.print(f"  [yellow]⚠[/yellow] OpenCode CLI no encontrado")
        console.print(f"    Instala desde: [bold]https://opencode.ai[/bold]")

    # Agentes
    agent_dir = Path(".opencode/agents")
    if agent_dir.exists():
        agent_count = len(list(agent_dir.glob("*.md")))
        console.print(f"  [green]✔[/green] Agentes configurados: {agent_count}")
    else:
        console.print(f"  [yellow]⚠[/yellow] No hay directorio .opencode/agents/")

    console.print("\n[bold cyan]==============================[/bold cyan]\n")


def load_agents():
    """Carga las definiciones de agentes desde .opencode/agents/*.md"""
    import yaml
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
        except (yaml.YAMLError, OSError):
            continue
    return agents


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent CLI")
    parser.add_argument("--setup", action="store_true", help="Forzar la configuración inicial de agentes")
    parser.add_argument("--doctor", action="store_true", help="Diagnosticar problemas del entorno")
    args = parser.parse_args()

    # Verificar dependencias básicas
    missing = check_dependencies()
    if missing:
        print(f"\n  ERROR: Dependencias faltantes: {', '.join(missing)}")
        print(f"  Ejecuta: pip install -r requirements.txt\n")
        sys.exit(1)

    from cli.ui import print_header, print_agent_status, console
    from cli.wizard import SetupWizard

    # Modo doctor
    if args.doctor:
        run_doctor()
        return

    print_header()

    wizard = SetupWizard()

    # Verificar si hay configuración existente
    if args.setup or not wizard.check_existing_config():
        if args.setup:
            console.print("[yellow]Modo de reconfiguración forzado...[/yellow]\n")
        else:
            console.print("[yellow]No se detectó configuración previa de agentes.[/yellow]\n")

        # Preguntar al usuario antes de ejecutar el wizard
        import questionary
        run_wizard = questionary.confirm(
            "¿Desea ejecutar el asistente de configuración?",
            default=True
        ).ask()

        if run_wizard:
            wizard.run()
        else:
            console.print("\n[dim]Puedes ejecutar el asistente más tarde con: python main.py --setup[/dim]")
            return

    agents = load_agents()

    if agents:
        print_agent_status(agents)
        console.print("\n[bold green]Sistema listo.[/bold green] Usa `opencode --agent orchestrator` para empezar.")
    else:
        console.print("[red]Error: No se pudieron cargar los agentes.[/red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from cli.ui import console
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
        sys.exit(0)
