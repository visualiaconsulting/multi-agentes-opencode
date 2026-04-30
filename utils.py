"""
utils.py — Cross-platform helpers for oh-my-agents

Windows-first, Linux-ready. All path operations use pathlib for portability.
"""
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

SYSTEM_ROOT = Path(__file__).parent.resolve()


def get_system_root() -> Path:
    """Return the directory where oh-my-agents is installed (system root)."""
    return SYSTEM_ROOT


def resolve_working_root(explicit_dir: Optional[str] = None) -> Path:
    """Return the active project directory.

    Priority:
    1. explicit_dir if provided
    2. Path.cwd() (current working directory)
    """
    if explicit_dir:
        return Path(explicit_dir).resolve()
    return Path.cwd().resolve()


def find_agent_source(working_root: Optional[Path] = None) -> Optional[Path]:
    """Find the directory containing agent .md files.

    Search order:
    1. working_root/.opencode/agents/ (local project override)
    2. ~/.opencode/agents/ (global install)
    3. system_root/.opencode/agents/ (repo bundled agents)

    Returns the first directory that exists and contains at least one .md file,
    or None if nothing found.
    """
    candidates = []
    if working_root:
        candidates.append(working_root / ".opencode" / "agents")
    candidates.append(Path.home() / ".opencode" / "agents")
    candidates.append(get_system_root() / ".opencode" / "agents")

    for candidate in candidates:
        if candidate.exists() and any(candidate.glob("*.md")):
            return candidate
    return None


def get_opencode_dir(project_root: Optional[Path] = None) -> Path:
    """Return the .opencode directory path."""
    root = project_root or Path(__file__).parent
    return root / ".opencode"


def get_sessions_dir(project_root: Optional[Path] = None) -> Path:
    """Return the .opencode/sessions directory path."""
    d = get_opencode_dir(project_root) / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_skills_dir(project_root: Optional[Path] = None) -> Path:
    """Return the .opencode/skills directory path."""
    d = get_opencode_dir(project_root) / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_logs_dir(project_root: Optional[Path] = None) -> Path:
    """Return the .opencode/logs directory path."""
    return get_opencode_dir(project_root) / "logs"


def get_global_agents_dir() -> Path:
    """Return the global agents directory (~/.opencode/agents/)."""
    return Path.home() / ".opencode" / "agents"


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())[:8]


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a datetime for display."""
    dt = dt or datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_timestamp(ts_str: str) -> datetime:
    """Parse a timestamp string back to datetime."""
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.min


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def get_shell_config_file() -> Path:
    """Return the path to the shell config file for the current platform."""
    if is_windows():
        return Path.home() / ".opencode" / "config.json"
    return Path.home() / ".config" / "opencode" / "config.json"


def safe_json_load(filepath: Path, default=None):
    """Safely load a JSON file, returning default on error."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def safe_json_save(filepath: Path, data: dict):
    """Safely save data as JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def inject_markdown_section(content: str, marker: str, new_content: str) -> str:
    """Inject or replace a marked section in markdown content.

    If `marker` exists, replaces everything from the marker to the
    next `---` separator or end-of-file. If not, appends new_content
    at the end.

    Returns the updated content.
    """
    import re
    if marker in content:
        content = re.sub(
            rf"{re.escape(marker)}.*?(?=---\n|$)",
            new_content.rstrip(),
            content,
            flags=re.DOTALL,
        )
    else:
        content = content.rstrip() + "\n\n" + new_content.rstrip()
    return content


def update_context_md_file(project_root: Path, section_marker: str, section_content: str) -> bool:
    """Update .opencode/context.md with a new section.

    Reads the file, injects/replaces the section identified by section_marker
    with section_content, and writes it back.

    Returns True if the file was updated, False if context.md doesn't exist.
    """
    context_file = get_opencode_dir(project_root) / "context.md"
    if not context_file.exists():
        return False

    try:
        content = context_file.read_text(encoding="utf-8")
    except OSError:
        return False

    if not section_content:
        return False

    content = inject_markdown_section(content, section_marker, section_content)

    try:
        context_file.write_text(content, encoding="utf-8")
        return True
    except OSError:
        return False
