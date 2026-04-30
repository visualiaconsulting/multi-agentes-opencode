"""
session_manager.py — Session bitacora and continuity for oh-my-agents

Manages session logs, saves session summaries, and injects context
for continuity between OpenCode sessions.
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from utils import (
    get_sessions_dir,
    get_logs_dir,
    get_opencode_dir,
    generate_session_id,
    format_timestamp,
    safe_json_load,
    safe_json_save,
    truncate_text,
)


class SessionManager:
    """Manages session logs and continuity context."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.sessions_dir = get_sessions_dir(self.project_root)
        self.logs_dir = get_logs_dir(self.project_root)

    def scan_logs(self) -> dict:
        """Scan .opencode/logs/ for session data and extract key information.

        Returns a dict with:
            - files_changed: list of file paths modified
            - errors: list of error messages found
            - warnings: list of warning messages found
            - commands_run: list of commands executed
            - raw_content: combined log text for summarization
        """
        result = {
            "files_changed": [],
            "errors": [],
            "warnings": [],
            "commands_run": [],
            "raw_content": "",
        }

        if not self.logs_dir.exists():
            return result

        log_files = sorted(self.logs_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not log_files:
            return result

        latest_log = log_files[0]
        try:
            with open(latest_log, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return result

        result["raw_content"] = content

        for line in content.splitlines():
            if re.search(r"(error|exception|failed|failure)", line, re.IGNORECASE):
                result["errors"].append(line.strip())
            elif re.search(r"(warning|warn)", line, re.IGNORECASE):
                result["warnings"].append(line.strip())
            elif re.search(r"(modified|created|deleted|wrote|edited)", line, re.IGNORECASE):
                match = re.search(r"[\w./\\-]+\.\w+", line)
                if match:
                    result["files_changed"].append(match.group(0))
            elif re.match(r"\$\s+", line) or re.search(r"Running:\s+", line, re.IGNORECASE):
                result["commands_run"].append(line.strip())

        result["files_changed"] = list(set(result["files_changed"]))
        result["errors"] = result["errors"][:50]
        result["warnings"] = result["warnings"][:50]
        result["commands_run"] = result["commands_run"][:50]

        return result

    def save_session(
        self,
        agent: str = "unknown",
        summary: str = "",
        errors: Optional[list] = None,
        pending_tasks: Optional[list] = None,
        files_changed: Optional[list] = None,
        decisions: Optional[list] = None,
        log_data: Optional[dict] = None,
    ) -> str:
        """Save a session record to .opencode/sessions/.

        Returns the session ID.
        """
        session_id = generate_session_id()
        now = format_timestamp()

        if log_data is None:
            log_data = self.scan_logs()

        session = {
            "session_id": session_id,
            "timestamp": now,
            "agent": agent,
            "summary": summary,
            "errors": errors or log_data.get("errors", []),
            "pending_tasks": pending_tasks or [],
            "files_changed": files_changed or log_data.get("files_changed", []),
            "decisions": decisions or [],
            "commands_run": log_data.get("commands_run", []),
            "warnings": log_data.get("warnings", []),
        }

        filepath = self.sessions_dir / f"{session_id}.json"
        safe_json_save(filepath, session)
        return session_id

    def get_last_session(self) -> Optional[dict]:
        """Return the most recent session, or None."""
        sessions = self.list_sessions()
        if not sessions:
            return None
        return sessions[0]

    def get_session(self, session_id: str) -> Optional[dict]:
        """Return a specific session by ID."""
        filepath = self.sessions_dir / f"{session_id}.json"
        return safe_json_load(filepath)

    def list_sessions(self, limit: int = 20) -> list:
        """List sessions sorted by most recent first."""
        if not self.sessions_dir.exists():
            return []

        session_files = sorted(
            self.sessions_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        sessions = []
        for sf in session_files[:limit]:
            data = safe_json_load(sf)
            if data:
                sessions.append(data)
        return sessions

    def inject_context(self, max_sessions: int = 3) -> str:
        """Generate a context string for injection into context.md.

        Returns a markdown-formatted string with the last N sessions.
        """
        sessions = self.list_sessions(limit=max_sessions)
        if not sessions:
            return ""

        lines = []
        lines.append("## Recent Session History")
        lines.append("")

        for i, session in enumerate(sessions, 1):
            ts = session.get("timestamp", "unknown")
            agent = session.get("agent", "unknown")
            summary = truncate_text(session.get("summary", ""), 300)
            errors = session.get("errors", [])
            pending = session.get("pending_tasks", [])

            lines.append(f"### Session {i} — {ts} (agent: @{agent})")
            lines.append("")
            if summary:
                lines.append(f"**Summary:** {summary}")
                lines.append("")
            if errors:
                lines.append(f"**Errors:** {len(errors)} issue(s)")
                for err in errors[:3]:
                    lines.append(f"- {truncate_text(err, 120)}")
                lines.append("")
            if pending:
                lines.append(f"**Pending tasks:**")
                for task in pending:
                    lines.append(f"- [ ] {truncate_text(task, 120)}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def update_context_md(self, max_sessions: int = 3):
        """Update .opencode/context.md with recent session history."""
        context_file = get_opencode_dir(self.project_root) / "context.md"
        if not context_file.exists():
            return

        try:
            with open(context_file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return

        session_context = self.inject_context(max_sessions)

        if not session_context:
            return

        marker = "## Recent Session History"
        if marker in content:
            content = re.sub(
                rf"{marker}.*?(?=---\n|$)",
                session_context.rstrip(),
                content,
                flags=re.DOTALL,
            )
        else:
            content = content.rstrip() + "\n\n" + session_context.rstrip()

        try:
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError:
            pass

    def delete_session(self, session_id: str) -> bool:
        """Delete a session file."""
        filepath = self.sessions_dir / f"{session_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def clear_old_sessions(self, keep: int = 10):
        """Delete all sessions except the most recent `keep`."""
        sessions = self.list_sessions()
        if len(sessions) <= keep:
            return
        for session in sessions[keep:]:
            self.delete_session(session["session_id"])
