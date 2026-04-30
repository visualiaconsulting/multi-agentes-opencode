"""
utils.py — Cross-platform helpers for oh-my-agents

Windows-first, Linux-ready. All path operations use pathlib for portability.
"""
import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional


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
    return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def get_shell_config_file() -> Path:
    """Return the path to the shell config file for the current platform."""
    if is_windows():
        return Path.home() / ".opencode" / "config.json"
    return Path.home() / ".opencode" / "config.json"


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
