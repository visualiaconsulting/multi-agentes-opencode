"""
mcp_config.py — MCP server configuration manager

Reads/writes .opencode/mcp.json and provides server templates.
"""
import json
from pathlib import Path
from typing import Optional, Dict, List

from utils import get_opencode_dir

DEFAULT_MCP_CONFIG = {
    "servers": [],
    "auto_connect": False,
}

MCP_SERVER_TEMPLATES = {
    "filesystem": {
        "name": "filesystem",
        "description": "Read and write files on the local filesystem",
        "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "{{project_root}}"],
        "transport": "stdio",
    },
    "sqlite": {
        "name": "sqlite",
        "description": "Query SQLite databases",
        "command": ["uvx", "mcp-server-sqlite", "--db-path", "{{db_path}}"],
        "transport": "stdio",
    },
    "github": {
        "name": "github",
        "description": "GitHub API operations",
        "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
        "transport": "stdio",
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "{{github_token}}"},
    },
}


class MCPConfig:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.config_path = get_opencode_dir(self.project_root) / "mcp.json"
        self._config = None

    def load(self) -> dict:
        if self._config is not None:
            return self._config
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                return self._config
            except (json.JSONDecodeError, OSError):
                pass
        self._config = dict(DEFAULT_MCP_CONFIG)
        return self._config

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get_servers(self) -> List[dict]:
        return self.load().get("servers", [])

    def add_server(self, server: dict):
        config = self.load()
        # Remove existing with same name
        config["servers"] = [s for s in config["servers"] if s.get("name") != server.get("name")]
        config["servers"].append(server)
        self.save()

    def remove_server(self, name: str) -> bool:
        config = self.load()
        original = len(config["servers"])
        config["servers"] = [s for s in config["servers"] if s.get("name") != name]
        if len(config["servers"]) < original:
            self.save()
            return True
        return False

    def get_template(self, name: str) -> Optional[dict]:
        return MCP_SERVER_TEMPLATES.get(name)

    def list_templates(self) -> Dict[str, dict]:
        return dict(MCP_SERVER_TEMPLATES)
