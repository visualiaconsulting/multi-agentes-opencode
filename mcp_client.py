"""
mcp_client.py — Model Context Protocol client for oh-my-agents

Implements JSON-RPC 2.0 over stdio to connect with MCP servers.
Supports tool listing, calling, and context injection.
"""
import os
import json
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

from utils import get_opencode_dir


class MCPServerConnection:
    """Manages a single MCP server connection via stdio."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._lock = threading.Lock()
        self._tools: List[dict] = []
        self._initialized = False

    def start(self) -> Tuple[bool, str]:
        """Start the MCP server subprocess and perform handshake."""
        command = self.config.get("command", [])
        if not command:
            return False, "No command configured"

        env = os.environ.copy()
        if "env" in self.config:
            env.update(self.config["env"])

        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
        except FileNotFoundError as e:
            return False, f"Command not found: {command[0]} ({e})"
        except Exception as e:
            return False, f"Failed to start server: {e}"

        # Perform initialize handshake
        ok, msg = self._initialize()
        if not ok:
            self.stop()
            return False, msg

        # List tools
        ok, tools = self._list_tools()
        if ok:
            self._tools = tools

        return True, f"Connected with {len(self._tools)} tool(s)"

    def stop(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass
            self.process = None
        self._initialized = False
        self._tools = []

    def _send_request(self, method: str, params: Optional[dict] = None) -> Tuple[bool, Any]:
        with self._lock:
            self._request_id += 1
            req_id = self._request_id

        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
        }
        if params is not None:
            request["params"] = params

        try:
            line = json.dumps(request) + "\n"
            self.process.stdin.write(line)
            self.process.stdin.flush()

            # Read response line
            response_line = self.process.stdout.readline()
            if not response_line:
                return False, "No response from server"

            response = json.loads(response_line)
            if "error" in response:
                return False, response["error"]
            return True, response.get("result")
        except Exception as e:
            return False, str(e)

    def _initialize(self) -> Tuple[bool, str]:
        ok, result = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "oh-my-agents", "version": "1.3.3"},
        })
        if not ok:
            return False, f"Initialize failed: {result}"

        # Send initialized notification
        try:
            notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            self.process.stdin.write(notif)
            self.process.stdin.flush()
        except Exception:
            pass

        self._initialized = True
        return True, "Initialized"

    def _list_tools(self) -> Tuple[bool, List[dict]]:
        ok, result = self._send_request("tools/list")
        if not ok:
            return False, []
        tools = result.get("tools", []) if isinstance(result, dict) else []
        return True, tools

    def call_tool(self, tool_name: str, arguments: dict) -> Tuple[bool, Any]:
        if not self._initialized:
            return False, "Server not initialized"
        ok, result = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments,
        })
        return ok, result

    @property
    def tools(self) -> List[dict]:
        return self._tools

    @property
    def is_connected(self) -> bool:
        return self.process is not None and self.process.poll() is None and self._initialized


class MCPClient:
    """Manages multiple MCP server connections and generates context."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.connections: Dict[str, MCPServerConnection] = {}

    def connect_server(self, config: dict) -> Tuple[bool, str]:
        name = config.get("name")
        if not name:
            return False, "Server config missing 'name'"

        # Disconnect existing
        if name in self.connections:
            self.connections[name].stop()

        conn = MCPServerConnection(name, config)
        ok, msg = conn.start()
        if ok:
            self.connections[name] = conn
        return ok, msg

    def disconnect_server(self, name: str):
        if name in self.connections:
            self.connections[name].stop()
            del self.connections[name]

    def disconnect_all(self):
        for conn in self.connections.values():
            conn.stop()
        self.connections.clear()

    def get_all_tools(self) -> List[dict]:
        tools = []
        for conn in self.connections.values():
            for tool in conn.tools:
                tool["_server"] = conn.name
                tools.append(tool)
        return tools

    def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Tuple[bool, Any]:
        if server_name not in self.connections:
            return False, f"Server '{server_name}' not connected"
        return self.connections[server_name].call_tool(tool_name, arguments)

    def inject_mcp_context(self) -> str:
        """Generate markdown context describing available MCP tools."""
        tools = self.get_all_tools()
        if not tools:
            return ""

        lines = ["## MCP Tools Available", ""]
        for tool in tools:
            name = tool.get("name", "unknown")
            desc = tool.get("description", "")
            server = tool.get("_server", "unknown")
            lines.append(f"### {name} (via {server})")
            lines.append("")
            if desc:
                lines.append(f"{desc}")
                lines.append("")
            schema = tool.get("inputSchema", {})
            if schema and isinstance(schema, dict):
                props = schema.get("properties", {})
                if props:
                    lines.append("**Parameters:**")
                    for prop_name, prop_info in props.items():
                        ptype = prop_info.get("type", "any")
                        pdesc = prop_info.get("description", "")
                        req = " (required)" if prop_name in schema.get("required", []) else ""
                        lines.append(f"- `{prop_name}` ({ptype}){req}: {pdesc}")
                    lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def update_context_md(self):
        """Update .opencode/context.md with MCP tools."""
        context_file = get_opencode_dir(self.project_root) / "context.md"
        if not context_file.exists():
            return

        try:
            with open(context_file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return

        mcp_context = self.inject_mcp_context()
        if not mcp_context:
            return

        marker = "## MCP Tools Available"
        if marker in content:
            import re
            content = re.sub(
                rf"{marker}.*?(?=---\n|$)",
                mcp_context.rstrip(),
                content,
                flags=re.DOTALL,
            )
        else:
            content = content.rstrip() + "\n\n" + mcp_context.rstrip()

        try:
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError:
            pass
