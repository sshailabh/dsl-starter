#!/usr/bin/env python3
"""
Shared MCP stdio client for ANTLR4 MCP server.
Reusable across all DSL demo scripts.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class McpStdioClient:
    command: list[str]
    proc: subprocess.Popen[str]
    next_id: int = 1

    @classmethod
    def start(cls, command: list[str]) -> "McpStdioClient":
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        if proc.stdin is None or proc.stdout is None or proc.stderr is None:
            raise RuntimeError("Failed to open stdio pipes")
        return cls(command=command, proc=proc)

    def close(self) -> None:
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass

    def request(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        req_id = self.next_id
        self.next_id += 1

        req: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            req["params"] = params

        line = json.dumps(req, separators=(",", ":")) + "\n"
        assert self.proc.stdin is not None
        self.proc.stdin.write(line)
        self.proc.stdin.flush()

        assert self.proc.stdout is not None
        while True:
            out_line = self.proc.stdout.readline()
            if out_line == "":
                err = ""
                if self.proc.stderr is not None:
                    err = self.proc.stderr.read()
                raise RuntimeError(f"MCP server exited unexpectedly.\ncommand={self.command}\nstderr:\n{err}")

            out_line = out_line.strip()
            if not out_line:
                continue

            resp = json.loads(out_line)
            if resp.get("id") == req_id:
                return resp

    def notify(self, method: str, params: Optional[dict[str, Any]] = None) -> None:
        req: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            req["params"] = params

        line = json.dumps(req, separators=(",", ":")) + "\n"
        assert self.proc.stdin is not None
        self.proc.stdin.write(line)
        self.proc.stdin.flush()

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        resp = self.request("tools/call", {"name": name, "arguments": arguments})
        if "error" in resp:
            raise RuntimeError(f"tools/call error: {resp['error']}")

        result = resp.get("result") or {}
        content = result.get("content") or []
        if not content:
            raise RuntimeError(f"tools/call returned no content: {resp}")

        text = content[0].get("text")
        if not isinstance(text, str):
            raise RuntimeError(f"Unexpected content payload: {content[0]}")

        return json.loads(text)

    def initialize(self) -> None:
        """Perform MCP handshake."""
        init_resp = self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "dsl-starter", "version": "1.0"},
            },
        )
        if "error" in init_resp:
            raise RuntimeError(f"initialize failed: {init_resp['error']}")

        self.notify("notifications/initialized")
