import sys
import argparse
import shutil
from pathlib import Path

from update_manager import check_for_updates, run_update
from mcp_client import MCPClient
from mcp_config import MCPConfig, MCP_SERVER_TEMPLATES
from skill_recommender import SkillRecommender

SYSTEM_ROOT = Path(__file__).parent.resolve()


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
    try:
        import requests
    except ImportError:
        missing.append("requests")
    return missing


def check_opencode_cli():
    """Check that OpenCode CLI is available"""
    return shutil.which("opencode") is not None


def run_doctor(working_root=None):
    """Diagnose environment issues"""
    import platform
    from cli.ui import console
    from utils import resolve_working_root, find_agent_source

    if working_root is None:
        working_root = resolve_working_root()

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
    agent_dir = find_agent_source(working_root)
    if agent_dir:
        agent_count = len(list(agent_dir.glob("*.md")))
        console.print(f"  [green]✔[/green] Agents configured: {agent_count}")

        pm = PlanManager(project_root=working_root)
        valid, invalid = pm.validate_models()
        if invalid:
            console.print(f"  [red]✖[/red] Invalid model IDs detected:")
            for name, model in invalid:
                console.print(f"      @{name} → [red]{model}[/red] (not in registry)")
            console.print(f"    [dim]Run 'python main.py --setup' to reconfigure.[/dim]")
        elif valid:
            console.print(f"  [green]✔[/green] All agent model IDs valid ({len(valid)} models)")
    else:
        console.print(f"  [yellow]⚠[/yellow] No agent configuration found")

    from session_manager import SessionManager
    sm = SessionManager(project_root=working_root)
    sessions = sm.list_sessions(limit=1)
    if sessions:
        console.print(f"  [green]✔[/green] Session history active ({len(sm.list_sessions())} sessions)")
    else:
        console.print(f"  [dim]ℹ[/dim] No sessions recorded yet")

    from skill_registry import SkillRegistry
    sr = SkillRegistry(project_root=working_root)
    skills = sr.list_skills()
    if skills:
        console.print(f"  [green]✔[/green] Skills installed: {len(skills)}")
    else:
        console.print(f"  [dim]ℹ[/dim] No skills installed")

    console.print("\n[bold cyan]==============================[/bold cyan]\n")


def load_agents():
    """Load agent definitions from the best available source."""
    import yaml
    from utils import find_agent_source

    agent_dir = find_agent_source()
    agents = []
    if not agent_dir:
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


def install_global():
    """Copy agent .md files from repo .opencode/agents/ to ~/.opencode/agents/"""
    from cli.ui import console, print_success, print_error

    source_dir = SYSTEM_ROOT / ".opencode" / "agents"
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


def run_sessions_list(working_root=None):
    """List all recorded sessions"""
    from cli.ui import console, print_session_list
    from session_manager import SessionManager
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sm = SessionManager(project_root=working_root)
    sessions = sm.list_sessions()

    if not sessions:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        console.print("[dim]Sessions are created when you run --summarize after an OpenCode session.[/dim]")
        return

    print_session_list(sessions)


def run_session_detail(session_id: str, working_root=None):
    """Show details of a specific session"""
    from cli.ui import console, print_session_detail
    from session_manager import SessionManager
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sm = SessionManager(project_root=working_root)
    session = sm.get_session(session_id)

    if not session:
        console.print(f"[red]Session '{session_id}' not found.[/red]")
        return

    print_session_detail(session)


def run_session_status(working_root=None):
    """Show summary of the last session"""
    from cli.ui import console, print_session_detail
    from session_manager import SessionManager
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sm = SessionManager(project_root=working_root)
    session = sm.get_last_session()

    if not session:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        return

    console.print("[bold cyan]=== Last Session ===[/bold cyan]\n")
    print_session_detail(session)


def run_summarize(working_root=None):
    """Run the summarizer: scan logs and save session record"""
    from cli.ui import console, print_success, print_error
    from session_manager import SessionManager
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sm = SessionManager(project_root=working_root)
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


def run_skills_list(working_root=None):
    """List installed skills"""
    from cli.ui import console, print_skills_list
    from skill_registry import SkillRegistry
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sr = SkillRegistry(project_root=working_root)
    skills = sr.list_skills()

    if not skills:
        console.print("[yellow]No skills installed.[/yellow]")
        console.print("[dim]Search skills with: python main.py --skills-search <query>[/dim]")
        return

    print_skills_list(skills)


def run_skills_search(query: str, working_root=None):
    """Search for skills on skills.sh"""
    from cli.ui import console, print_skills_search
    from skill_registry import SkillRegistry
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sr = SkillRegistry(project_root=working_root)
    results = sr.search_skills(query)

    if not results:
        console.print(f"[yellow]No skills found for '{query}'.[/yellow]")
        return

    print_skills_search(results, query)


def run_skills_install(identifier: str, working_root=None):
    """Install a skill from skills.sh or local file"""
    from cli.ui import console, print_success, print_error
    from skill_registry import SkillRegistry
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sr = SkillRegistry(project_root=working_root)
    success = sr.install_skill(identifier)

    if success:
        name = identifier.split("/")[-1]
        print_success(f"Skill '{name}' installed to .opencode/skills/")
    else:
        print_error(f"Failed to install skill '{identifier}'. Check the identifier format.")
        console.print("[dim]Format: owner/repo/skill-name or /path/to/file.md[/dim]")


def run_skills_remove(name: str, working_root=None):
    """Remove an installed skill"""
    from cli.ui import console, print_success, print_error
    from skill_registry import SkillRegistry
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    sr = SkillRegistry(project_root=working_root)
    success = sr.remove_skill(name)

    if success:
        print_success(f"Skill '{name}' removed.")
    else:
        print_error(f"Skill '{name}' not found.")


def run_mcp_status(working_root=None):
    """Show MCP server status and available tools."""
    from cli.ui import console, print_success, print_error
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    config = MCPConfig(project_root=working_root)
    servers = config.get_servers()

    if not servers:
        console.print("[yellow]No MCP servers configured.[/yellow]")
        console.print("[dim]Add one with: python main.py --mcp-add <template_name>[/dim]")
        console.print(f"[dim]Available templates: {', '.join(MCP_SERVER_TEMPLATES.keys())}[/dim]")
        return

    console.print("\n[bold cyan]=== MCP Servers ===[/bold cyan]\n")
    client = MCPClient(project_root=working_root)
    for server_config in servers:
        name = server_config.get("name", "unknown")
        desc = server_config.get("description", "")
        console.print(f"  [bold]{name}[/bold] — {desc}")
        # Try to connect and list tools
        ok, msg = client.connect_server(server_config)
        if ok:
            tools = client.connections[name].tools
            console.print(f"    [green]✔ Connected[/green] ({len(tools)} tool(s))")
            for tool in tools:
                console.print(f"      • {tool.get('name', '?')}: {tool.get('description', '')[:60]}")
            client.disconnect_server(name)
        else:
            console.print(f"    [red]✖ {msg}[/red]")
    console.print("")


def run_mcp_add(template_name: str, working_root=None):
    """Add an MCP server from a template."""
    from cli.ui import console, print_success, print_error
    from utils import resolve_working_root

    if working_root is None:
        working_root = resolve_working_root()

    config = MCPConfig(project_root=working_root)
    template = config.get_template(template_name)
    if not template:
        print_error(f"Unknown template: '{template_name}'")
        console.print(f"[dim]Available: {', '.join(MCP_SERVER_TEMPLATES.keys())}[/dim]")
        return

    # Substitute {{project_root}} if present
    server_config = dict(template)
    cmd = server_config.get("command", [])
    server_config["command"] = [
        c.replace("{{project_root}}", str(working_root)) for c in cmd
    ]

    config.add_server(server_config)
    print_success(f"Added MCP server '{template_name}'")
    console.print(f"[dim]Run 'python main.py --mcp-status' to verify.[/dim]")


def run_skills_recommend(working_root=None, auto_install=False):
    """Analyze project and recommend skills."""
    from cli.ui import console, print_success, print_error
    from utils import resolve_working_root
    import questionary

    if working_root is None:
        working_root = resolve_working_root()

    recommender = SkillRecommender(project_root=working_root)
    recommendations = recommender.get_installable_recommendations()

    if not recommendations:
        console.print("[yellow]No new skill recommendations for this project.[/yellow]")
        return

    console.print("\n[bold cyan]=== Recommended Skills ===[/bold cyan]\n")
    for i, skill in enumerate(recommendations, 1):
        console.print(f"  {i}. [bold]{skill['name']}[/bold] — {skill['description']}")
        console.print(f"     Tags: {', '.join(skill.get('tags', []))}")

    if auto_install:
        results = recommender.install_recommendations(recommendations)
        for skill_id, success in results:
            if success:
                console.print(f"  [green]✔ Installed {skill_id}[/green]")
            else:
                console.print(f"  [red]✖ Failed {skill_id}[/red]")
        return

    console.print("")
    install = questionary.confirm("Install recommended skills?", default=True).ask()
    if install:
        results = recommender.install_recommendations(recommendations)
        installed = sum(1 for _, s in results if s)
        print_success(f"Installed {installed}/{len(results)} skill(s).")


def run_uninstall():
    """Remove global installation and optionally clean up data."""
    from cli.ui import console, print_success, print_error
    import questionary

    global_dir = Path.home() / ".opencode"
    agents_dir = global_dir / "agents"
    sessions_dir = global_dir / "sessions"
    skills_dir = global_dir / "skills"
    config_file = global_dir / "config.json"

    console.print("\n[bold red]=== Uninstall oh-my-agents ===[/bold red]\n")

    items_to_remove = []

    if agents_dir.exists():
        items_to_remove.append(("Global agents", agents_dir))
    if sessions_dir.exists():
        items_to_remove.append(("Global sessions", sessions_dir))
    if skills_dir.exists():
        items_to_remove.append(("Global skills", skills_dir))
    if config_file.exists():
        items_to_remove.append(("Global config", config_file))

    if not items_to_remove:
        console.print("[yellow]No global installation found.[/yellow]")
        console.print("[dim]Nothing to uninstall.[/dim]")
        return

    console.print("The following will be removed:")
    for label, path in items_to_remove:
        console.print(f"  [red]✖[/red] {label}: {path}")

    remove_all = questionary.confirm(
        "Remove ALL of the above (agents, sessions, skills, config)?",
        default=True
    ).ask()

    if not remove_all:
        for label, path in list(items_to_remove):
            if not questionary.confirm(f"Remove {label}?", default=True).ask():
                items_to_remove = [x for x in items_to_remove if x[1] != path]

    if not items_to_remove:
        console.print("[dim]Uninstall cancelled.[/dim]")
        return

    confirmed = questionary.confirm(
        "This action cannot be undone. Continue?",
        default=False
    ).ask()

    if not confirmed:
        console.print("[dim]Uninstall cancelled.[/dim]")
        return

    removed = 0
    for label, path in items_to_remove:
        try:
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            console.print(f"  [green]✔[/green] Removed {label}")
            removed += 1
        except OSError as e:
            print_error(f"Failed to remove {label}: {e}")

    if sys.platform != "win32":
        for wrapper_path in [Path("/usr/local/bin/oh-my-agents"), Path.home() / ".local" / "bin" / "oh-my-agents"]:
            if wrapper_path.exists():
                try:
                    wrapper_path.unlink()
                    console.print(f"  [green]✔[/green] Removed wrapper: {wrapper_path}")
                except OSError:
                    pass

    print_success(f"Uninstall complete. {removed} item(s) removed.")
    console.print("[dim]To remove the oh-my-agents repository itself, delete its folder manually.[/dim]")


def run_check_updates():
    """Check if updates are available and print status."""
    from cli.ui import console, print_success
    has_update, current, latest = check_for_updates()
    if has_update:
        console.print(f"\n[bold cyan]=== Update Available ===[/bold cyan]\n")
        console.print(f"  Current:  [dim]v{current}[/dim]")
        console.print(f"  Latest:   [bold green]v{latest}[/bold green]")
        console.print("")
        console.print("  Run [bold]python main.py --update[/bold] to install.")
    else:
        print_success(f"oh-my-agents is up to date (v{current}).")


def run_update_command(target_version=None):
    """Run the interactive update workflow."""
    success, message = run_update(target_version=target_version)
    if not success:
        from cli.ui import console
        console.print(f"\n[red]Update result: {message}[/red]\n")
        sys.exit(1)
    from cli.ui import console
    console.print(f"\n[green]{message}[/green]\n")


def main():
    parser = argparse.ArgumentParser(description="oh-my-agents — Multi-Agent Orchestration for OpenCode")
    parser.add_argument("--setup", action="store_true", help="Force initial agent configuration")
    parser.add_argument("--doctor", action="store_true", help="Diagnose environment issues")
    parser.add_argument("--install-global", action="store_true",
                        help="Copy agent .md files to ~/.opencode/agents/ for global use")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove global installation and optional data")
    parser.add_argument("--dir", type=str, default=None,
                        help="Explicitly set the project root directory (overrides auto-detection)")
    parser.add_argument("--update", action="store_true",
                        help="Update oh-my-agents to the latest version")
    parser.add_argument("--check-updates", action="store_true",
                        help="Check if a newer version is available")
    parser.add_argument("--version", action="store_true", help="Show current version")

    parser.add_argument("--sessions", action="store_true", help="List recorded sessions")
    parser.add_argument("--session", type=str, default=None, help="Show details of a specific session by ID")
    parser.add_argument("--session-status", action="store_true", help="Show summary of the last session")
    parser.add_argument("--summarize", action="store_true", help="Scan logs and save session record")

    parser.add_argument("--skills", action="store_true", help="List installed skills")
    parser.add_argument("--skills-search", type=str, default=None, help="Search skills on skills.sh")
    parser.add_argument("--skills-install", type=str, default=None, help="Install a skill (owner/repo/name)")
    parser.add_argument("--skills-remove", type=str, default=None, help="Remove an installed skill")

    parser.add_argument("--mcp-status", action="store_true", help="Show MCP servers and tools")
    parser.add_argument("--mcp-add", type=str, default=None, help="Add MCP server from template (filesystem, sqlite, github)")
    parser.add_argument("--skills-recommend", action="store_true", help="Analyze project and recommend skills")
    parser.add_argument("--skills-auto", action="store_true", help="Auto-install recommended skills without prompting")

    args = parser.parse_args()

    from utils import resolve_working_root

    working_root = resolve_working_root(args.dir)
    system_root = SYSTEM_ROOT

    if args.version:
        from update_manager import get_current_version
        current = get_current_version()
        from cli.ui import console
        console.print(f"[bold cyan]oh-my-agents[/bold cyan] v{current}")
        return

    if args.check_updates:
        run_check_updates()
        return

    if args.update:
        run_update_command()
        return

    if args.mcp_status:
        run_mcp_status(working_root=working_root)
        return

    if args.mcp_add:
        run_mcp_add(args.mcp_add, working_root=working_root)
        return

    if args.skills_recommend:
        run_skills_recommend(working_root=working_root)
        return

    if args.skills_auto:
        run_skills_recommend(working_root=working_root, auto_install=True)
        return

    missing = check_dependencies()
    if missing:
        print(f"\n  ERROR: Missing dependencies: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt\n")
        sys.exit(1)

    from cli.ui import print_header, print_agent_status, console
    from cli.wizard import SetupWizard

    if args.uninstall:
        run_uninstall()
        return

    if args.install_global:
        install_global()
        return

    if args.doctor:
        run_doctor(working_root=working_root)
        return

    if args.sessions:
        run_sessions_list(working_root=working_root)
        return

    if args.session:
        run_session_detail(args.session, working_root=working_root)
        return

    if args.session_status:
        run_session_status(working_root=working_root)
        return

    if args.summarize:
        run_summarize(working_root=working_root)
        return

    if args.skills:
        run_skills_list(working_root=working_root)
        return

    if args.skills_search:
        run_skills_search(args.skills_search, working_root=working_root)
        return

    if args.skills_install:
        run_skills_install(args.skills_install, working_root=working_root)
        return

    if args.skills_remove:
        run_skills_remove(args.skills_remove, working_root=working_root)
        return

    print_header()

    wizard = SetupWizard(project_root=working_root)

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

        agents = load_agents()
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
                "Check for updates",
                "MCP status",
                "Recommend skills",
                "Install globally",
                "Uninstall globally",
                "View sessions",
                "View skills",
                "Exit",
            ]
        ).ask()

        if choice is None or choice == "Exit":
            console.print("\n[dim]Goodbye![/dim]")
            break
        elif choice == "View agent status":
            agents = load_agents()
            if agents:
                print_agent_status(agents)
            else:
                console.print("[red]Error: Could not load agents.[/red]")
        elif choice == "Run setup wizard":
            wizard.run()
        elif choice == "Run diagnostics":
            run_doctor(working_root=working_root)
        elif choice == "Check for updates":
            run_check_updates()
            from update_manager import check_for_updates
            has_update, _, latest = check_for_updates()
            if has_update:
                import questionary
                do_update = questionary.confirm(
                    f"Install v{latest} now?",
                    default=True
                ).ask()
                if do_update:
                    run_update_command()
        elif choice == "Install globally":
            install_global()
        elif choice == "Uninstall globally":
            run_uninstall()
        elif choice == "MCP status":
            run_mcp_status(working_root=working_root)
        elif choice == "Recommend skills":
            run_skills_recommend(working_root=working_root)
        elif choice == "View sessions":
            run_sessions_list(working_root=working_root)
        elif choice == "View skills":
            run_skills_list(working_root=working_root)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from cli.ui import console
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
