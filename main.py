import sys
import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()


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
    return shutil.which("opencode") is not None


def run_doctor(project_root=None):
    """Diagnose environment issues"""
    import platform
    from cli.ui import console

    if project_root is None:
        project_root = PROJECT_ROOT

    console.print("\n[bold cyan]=== System Diagnostics ===[/bold cyan]\n")

    py_ver = platform.python_version()
    major, minor = map(int, py_ver.split(".")[:2])
    if major >= 3 and minor >= 8:
        console.print(f"  [green]✔[/green] Python {py_ver}")
    else:
        console.print(f"  [red]✖[/red] Python {py_ver} (requires 3.8+)")

    missing = check_dependencies()
    if missing:
        console.print(f"  [red]✖[/red] Missing dependencies: {', '.join(missing)}")
        console.print(f"    Run: [bold]pip install -r requirements.txt[/bold]")
    else:
        console.print(f"  [green]✔[/green] Dependencies installed (PyYAML, questionary, rich)")

    if check_opencode_cli():
        console.print(f"  [green]✔[/green] OpenCode CLI available")
    else:
        console.print(f"  [yellow]⚠[/yellow] OpenCode CLI not found")
        console.print(f"    Install from: [bold]https://opencode.ai[/bold]")

    from plan_manager import PlanManager
    agent_dir = project_root / ".opencode" / "agents"
    if agent_dir.exists():
        agent_count = len(list(agent_dir.glob("*.md")))
        console.print(f"  [green]✔[/green] Agents configured: {agent_count}")

        pm = PlanManager(project_root=project_root)
        valid, invalid = pm.validate_models()
        if invalid:
            console.print(f"  [red]✖[/red] Invalid model IDs detected:")
            for name, model in invalid:
                console.print(f"      @{name} → [red]{model}[/red] (not in registry)")
            console.print(f"    [dim]Run 'python main.py --setup' to reconfigure.[/dim]")
        elif valid:
            console.print(f"  [green]✔[/green] All agent model IDs valid ({len(valid)} models)")
    else:
        console.print(f"  [yellow]⚠[/yellow] No .opencode/agents/ directory found")

    from session_manager import SessionManager
    sm = SessionManager(project_root=project_root)
    sessions = sm.list_sessions(limit=1)
    if sessions:
        console.print(f"  [green]✔[/green] Session history active ({len(sm.list_sessions())} sessions)")
    else:
        console.print(f"  [dim]ℹ[/dim] No sessions recorded yet")

    from skill_registry import SkillRegistry
    sr = SkillRegistry(project_root=project_root)
    skills = sr.list_skills()
    if skills:
        console.print(f"  [green]✔[/green] Skills installed: {len(skills)}")
    else:
        console.print(f"  [dim]ℹ[/dim] No skills installed")

    console.print("\n[bold cyan]==============================[/bold cyan]\n")


def load_agents(project_root=None):
    """Load agent definitions from .opencode/agents/*.md"""
    import yaml

    if project_root is None:
        project_root = PROJECT_ROOT

    agent_dir = project_root / ".opencode" / "agents"
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


def install_global(project_root=None):
    """Copy agent .md files from project .opencode/agents/ to ~/.opencode/agents/"""
    from cli.ui import console, print_success, print_error

    if project_root is None:
        project_root = PROJECT_ROOT

    source_dir = project_root / ".opencode" / "agents"
    target_dir = Path.home() / ".opencode" / "agents"

    if not source_dir.exists():
        print_error(f"Source agent directory not found: {source_dir}")
        console.print("[dim]Run the setup wizard first with: python main.py --setup[/dim]")
        return False

    md_files = list(source_dir.glob("*.md"))
    if not md_files:
        print_error("No agent .md files found in source directory.")
        return False

    target_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for md_file in md_files:
        target_file = target_dir / md_file.name
        shutil.copy2(md_file, target_file)
        copied += 1
        console.print(f"  [green]✔[/green] {md_file.name}")

    print_success(f"Installed {copied} agent(s) globally to {target_dir}")
    console.print("[dim]Now opencode --agent orchestrator works from ANY folder on your system.[/dim]")
    return True


def run_sessions_list(project_root=None):
    """List all recorded sessions"""
    from cli.ui import console, print_session_list
    from session_manager import SessionManager

    if project_root is None:
        project_root = PROJECT_ROOT

    sm = SessionManager(project_root=project_root)
    sessions = sm.list_sessions()

    if not sessions:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        console.print("[dim]Sessions are created when you run --summarize after an OpenCode session.[/dim]")
        return

    print_session_list(sessions)


def run_session_detail(session_id: str, project_root=None):
    """Show details of a specific session"""
    from cli.ui import console, print_session_detail
    from session_manager import SessionManager

    if project_root is None:
        project_root = PROJECT_ROOT

    sm = SessionManager(project_root=project_root)
    session = sm.get_session(session_id)

    if not session:
        console.print(f"[red]Session '{session_id}' not found.[/red]")
        return

    print_session_detail(session)


def run_session_status(project_root=None):
    """Show summary of the last session"""
    from cli.ui import console, print_session_detail
    from session_manager import SessionManager

    if project_root is None:
        project_root = PROJECT_ROOT

    sm = SessionManager(project_root=project_root)
    session = sm.get_last_session()

    if not session:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        return

    console.print("[bold cyan]=== Last Session ===[/bold cyan]\n")
    print_session_detail(session)


def run_summarize(project_root=None):
    """Run the summarizer: scan logs and save session record"""
    from cli.ui import console, print_success, print_error
    from session_manager import SessionManager

    if project_root is None:
        project_root = PROJECT_ROOT

    sm = SessionManager(project_root=project_root)
    log_data = sm.scan_logs()

    if not log_data["raw_content"]:
        console.print("[yellow]No logs found in .opencode/logs/[/yellow]")
        console.print("[dim]Make sure OpenCode has been run in this project first.[/dim]")
        return

    session_id = sm.save_session(
        agent="summarizer",
        summary=f"Auto-summarized session. {len(log_data.get('files_changed', []))} files changed, {len(log_data.get('errors', []))} errors found.",
        errors=log_data.get("errors", []),
        files_changed=log_data.get("files_changed", []),
        log_data=log_data,
    )

    sm.update_context_md()

    print_success(f"Session saved: {session_id}")
    console.print(f"  [dim]Files changed: {len(log_data.get('files_changed', []))}[/dim]")
    console.print(f"  [dim]Errors found: {len(log_data.get('errors', []))}[/dim]")
    console.print(f"  [dim]Context updated in .opencode/context.md[/dim]")


def run_skills_list(project_root=None):
    """List installed skills"""
    from cli.ui import console, print_skills_list
    from skill_registry import SkillRegistry

    if project_root is None:
        project_root = PROJECT_ROOT

    sr = SkillRegistry(project_root=project_root)
    skills = sr.list_skills()

    if not skills:
        console.print("[yellow]No skills installed.[/yellow]")
        console.print("[dim]Search skills with: python main.py --skills-search <query>[/dim]")
        return

    print_skills_list(skills)


def run_skills_search(query: str, project_root=None):
    """Search for skills on skills.sh"""
    from cli.ui import console, print_skills_search
    from skill_registry import SkillRegistry

    if project_root is None:
        project_root = PROJECT_ROOT

    sr = SkillRegistry(project_root=project_root)
    results = sr.search_skills(query)

    if not results:
        console.print(f"[yellow]No skills found for '{query}'.[/yellow]")
        return

    print_skills_search(results, query)


def run_skills_install(identifier: str, project_root=None):
    """Install a skill from skills.sh or local file"""
    from cli.ui import console, print_success, print_error
    from skill_registry import SkillRegistry

    if project_root is None:
        project_root = PROJECT_ROOT

    sr = SkillRegistry(project_root=project_root)
    success = sr.install_skill(identifier)

    if success:
        name = identifier.split("/")[-1]
        print_success(f"Skill '{name}' installed to .opencode/skills/")
    else:
        print_error(f"Failed to install skill '{identifier}'. Check the identifier format.")
        console.print("[dim]Format: owner/repo/skill-name or /path/to/file.md[/dim]")


def run_skills_remove(name: str, project_root=None):
    """Remove an installed skill"""
    from cli.ui import console, print_success, print_error
    from skill_registry import SkillRegistry

    if project_root is None:
        project_root = PROJECT_ROOT

    sr = SkillRegistry(project_root=project_root)
    success = sr.remove_skill(name)

    if success:
        print_success(f"Skill '{name}' removed.")
    else:
        print_error(f"Skill '{name}' not found.")


def main():
    parser = argparse.ArgumentParser(description="oh-my-agents — Multi-Agent Orchestration for OpenCode")
    parser.add_argument("--setup", action="store_true", help="Force initial agent configuration")
    parser.add_argument("--doctor", action="store_true", help="Diagnose environment issues")
    parser.add_argument("--install-global", action="store_true",
                        help="Copy agent .md files to ~/.opencode/agents/ for global use")
    parser.add_argument("--dir", type=str, default=None,
                        help="Explicitly set the project root directory (overrides auto-detection)")

    parser.add_argument("--sessions", action="store_true", help="List recorded sessions")
    parser.add_argument("--session", type=str, default=None, help="Show details of a specific session by ID")
    parser.add_argument("--session-status", action="store_true", help="Show summary of the last session")
    parser.add_argument("--summarize", action="store_true", help="Scan logs and save session record")

    parser.add_argument("--skills", action="store_true", help="List installed skills")
    parser.add_argument("--skills-search", type=str, default=None, help="Search skills on skills.sh")
    parser.add_argument("--skills-install", type=str, default=None, help="Install a skill (owner/repo/name)")
    parser.add_argument("--skills-remove", type=str, default=None, help="Remove an installed skill")

    args = parser.parse_args()

    project_root = Path(args.dir).resolve() if args.dir else PROJECT_ROOT

    missing = check_dependencies()
    if missing:
        print(f"\n  ERROR: Missing dependencies: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt\n")
        sys.exit(1)

    from cli.ui import print_header, print_agent_status, console
    from cli.wizard import SetupWizard

    if args.install_global:
        install_global(project_root=project_root)
        return

    if args.doctor:
        run_doctor(project_root=project_root)
        return

    if args.sessions:
        run_sessions_list(project_root=project_root)
        return

    if args.session:
        run_session_detail(args.session, project_root=project_root)
        return

    if args.session_status:
        run_session_status(project_root=project_root)
        return

    if args.summarize:
        run_summarize(project_root=project_root)
        return

    if args.skills:
        run_skills_list(project_root=project_root)
        return

    if args.skills_search:
        run_skills_search(args.skills_search, project_root=project_root)
        return

    if args.skills_install:
        run_skills_install(args.skills_install, project_root=project_root)
        return

    if args.skills_remove:
        run_skills_remove(args.skills_remove, project_root=project_root)
        return

    print_header()

    wizard = SetupWizard(project_root=project_root)

    if args.setup or not wizard.check_existing_config():
        if args.setup:
            console.print("[yellow]Forced reconfiguration mode...[/yellow]\n")
        else:
            console.print("[yellow]No previous agent configuration detected.[/yellow]\n")

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

        agents = load_agents(project_root=project_root)
        if agents:
            print_agent_status(agents)
            console.print("\n[bold green]System ready.[/bold green] Use `opencode --agent orchestrator` to get started.")
        else:
            console.print("[red]Error: Could not load agents.[/red]")
        return

    import questionary
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "View agent status",
                "Run setup wizard",
                "Run diagnostics",
                "Install globally",
                "View sessions",
                "View skills",
                "Exit",
            ]
        ).ask()

        if choice is None or choice == "Exit":
            console.print("\n[dim]Goodbye![/dim]")
            break
        elif choice == "View agent status":
            agents = load_agents(project_root=project_root)
            if agents:
                print_agent_status(agents)
            else:
                console.print("[red]Error: Could not load agents.[/red]")
        elif choice == "Run setup wizard":
            wizard.run()
        elif choice == "Run diagnostics":
            run_doctor(project_root=project_root)
        elif choice == "Install globally":
            install_global(project_root=project_root)
        elif choice == "View sessions":
            run_sessions_list(project_root=project_root)
        elif choice == "View skills":
            run_skills_list(project_root=project_root)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from cli.ui import console
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
