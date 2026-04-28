import sys
import argparse
from pathlib import Path


def check_dependencies():
    """Check that dependencies are installed"""
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
    """Check that OpenCode CLI is available"""
    import shutil
    return shutil.which("opencode") is not None


def run_doctor():
    """Diagnose environment issues"""
    import platform
    from cli.ui import console

    console.print("\n[bold cyan]=== System Diagnostics ===[/bold cyan]\n")

    # Python
    py_ver = platform.python_version()
    major, minor = map(int, py_ver.split(".")[:2])
    if major >= 3 and minor >= 8:
        console.print(f"  [green]✔[/green] Python {py_ver}")
    else:
        console.print(f"  [red]✖[/red] Python {py_ver} (requires 3.8+)")

    # Dependencies
    missing = check_dependencies()
    if missing:
        console.print(f"  [red]✖[/red] Missing dependencies: {', '.join(missing)}")
        console.print(f"    Run: [bold]pip install -r requirements.txt[/bold]")
    else:
        console.print(f"  [green]✔[/green] Dependencies installed (PyYAML, questionary, rich)")

    # OpenCode CLI
    if check_opencode_cli():
        console.print(f"  [green]✔[/green] OpenCode CLI available")
    else:
        console.print(f"  [yellow]⚠[/yellow] OpenCode CLI not found")
        console.print(f"    Install from: [bold]https://opencode.ai[/bold]")

    # Agents
    agent_dir = Path(".opencode/agents")
    if agent_dir.exists():
        agent_count = len(list(agent_dir.glob("*.md")))
        console.print(f"  [green]✔[/green] Agents configured: {agent_count}")
    else:
        console.print(f"  [yellow]⚠[/yellow] No .opencode/agents/ directory found")

    console.print("\n[bold cyan]==============================[/bold cyan]\n")


def load_agents():
    """Load agent definitions from .opencode/agents/*.md"""
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
    parser = argparse.ArgumentParser(description="oh-my-agents — Multi-Agent Orchestration for OpenCode")
    parser.add_argument("--setup", action="store_true", help="Force initial agent configuration")
    parser.add_argument("--doctor", action="store_true", help="Diagnose environment issues")
    args = parser.parse_args()

    # Check basic dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n  ERROR: Missing dependencies: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt\n")
        sys.exit(1)

    from cli.ui import print_header, print_agent_status, console
    from cli.wizard import SetupWizard

    # Doctor mode
    if args.doctor:
        run_doctor()
        return

    print_header()

    wizard = SetupWizard()

    # Check for existing configuration
    if args.setup or not wizard.check_existing_config():
        if args.setup:
            console.print("[yellow]Forced reconfiguration mode...[/yellow]\n")
        else:
            console.print("[yellow]No previous agent configuration detected.[/yellow]\n")

        # Ask user before running the wizard
        import questionary
        run_wizard = questionary.confirm(
            "Do you want to run the setup wizard?",
            default=True
        ).ask()

        if run_wizard:
            wizard.run()
        else:
            console.print("\n[dim]You can run the wizard later with: python main.py --setup[/dim]")
            return

    agents = load_agents()

    if agents:
        print_agent_status(agents)
        console.print("\n[bold green]System ready.[/bold green] Use `opencode --agent orchestrator` to get started.")
    else:
        console.print("[red]Error: Could not load agents.[/red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from cli.ui import console
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
