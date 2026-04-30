import sys
import shutil
from pathlib import Path
from unittest.mock import patch


class TestLoadAgents:
    """Tests for load_agents()."""

    def test_loads_agent_metadata(self, temp_project):
        from main import load_agents
        agents = load_agents(project_root=temp_project)
        assert len(agents) == 2
        names = [a["name"] for a in agents]
        assert "@orchestrator" in names
        assert "@code-analyst" in names

    def test_agents_have_model(self, temp_project):
        from main import load_agents
        agents = load_agents(project_root=temp_project)
        orch = next(a for a in agents if a["name"] == "@orchestrator")
        assert orch["model"] == "opencode-go/mimo-v2.5-pro"
        assert orch["role"] == "Primary"

    def test_no_agents_dir_returns_empty(self, temp_empty_project):
        from main import load_agents
        agents = load_agents(project_root=temp_empty_project)
        assert agents == []

    def test_empty_dir_returns_empty(self, temp_empty_project):
        from main import load_agents
        agent_dir = temp_empty_project / ".opencode" / "agents"
        agent_dir.mkdir(parents=True)
        agents = load_agents(project_root=temp_empty_project)
        assert agents == []

    def test_invalid_yaml_is_skipped(self, temp_empty_project):
        from main import load_agents
        agent_dir = temp_empty_project / ".opencode" / "agents"
        agent_dir.mkdir(parents=True)
        # Frontmatter with invalid YAML
        (agent_dir / "broken.md").write_text("""---
: : : invalid yaml
---
body
""", encoding="utf-8")
        agents = load_agents(project_root=temp_empty_project)
        assert agents == []


class TestCheckDependencies:
    """Tests for check_dependencies()."""

    def test_all_present(self):
        from main import check_dependencies
        missing = check_dependencies()
        assert missing == []

    def test_missing_yaml(self):
        with patch.dict(sys.modules, {"yaml": None}):
            import builtins
            real_import = builtins.__import__

            def fake_import(name, *args, **kwargs):
                if name == "yaml":
                    raise ImportError("No yaml")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=fake_import):
                from importlib import reload
                import main
                reload(main)
                missing = main.check_dependencies()
                assert "PyYAML" in missing


class TestCheckOpencodeCli:
    """Tests for check_opencode_cli()."""

    def test_not_found(self):
        with patch("shutil.which", return_value=None):
            from main import check_opencode_cli
            assert check_opencode_cli() is False

    def test_found(self):
        with patch("shutil.which", return_value="/usr/bin/opencode"):
            from main import check_opencode_cli
            assert check_opencode_cli() is True


class TestInstallGlobal:
    """Tests for install_global()."""

    def test_copies_agent_files(self, temp_project):
        from main import install_global

        home_target = Path(temp_project) / "home" / ".opencode" / "agents"
        with patch("pathlib.Path.home", return_value=Path(temp_project) / "home"):
            result = install_global(project_root=temp_project)
            assert result is True
            assert home_target.exists()
            md_files = list(home_target.glob("*.md"))
            assert len(md_files) == 2

    def test_no_agents_dir_returns_false(self, temp_empty_project):
        from main import install_global
        result = install_global(project_root=temp_empty_project)
        assert result is False

    def test_no_md_files_returns_false(self, temp_empty_project):
        from main import install_global
        agent_dir = temp_empty_project / ".opencode" / "agents"
        agent_dir.mkdir(parents=True)
        result = install_global(project_root=temp_empty_project)
        assert result is False


class TestProjectRoot:
    """Tests for PROJECT_ROOT constant."""

    def test_project_root_is_parent_of_main(self):
        from main import PROJECT_ROOT
        main_file = PROJECT_ROOT / "main.py"
        assert main_file.exists()


class TestRunDoctor:
    """Tests for run_doctor()."""

    def test_runs_without_error(self, temp_project):
        from main import run_doctor
        run_doctor(project_root=temp_project)

    def test_runs_without_error_no_agents(self, temp_empty_project):
        from main import run_doctor
        run_doctor(project_root=temp_empty_project)
