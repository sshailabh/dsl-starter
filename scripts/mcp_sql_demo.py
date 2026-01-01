#!/usr/bin/env python3
"""
SQL Subset demo using ANTLR4 MCP server.

Demonstrates parsing SQL-like queries and generating a parser.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_client import McpStdioClient


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SQL Subset demo")
    p.add_argument("--server", choices=["docker", "jar"], default="docker")
    p.add_argument("--image", default="antlr4-mcp-server:latest")
    p.add_argument("--out-dir", default="")
    p.add_argument("--target", default="python")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    grammar_path = repo_root / "dsl-starter" / "grammar" / "SqlSubset.g4"
    sample_path = repo_root / "dsl-starter" / "samples" / "queries.sql"

    if args.out_dir.strip():
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = repo_root / "dsl-starter" / "generated" / args.target

    grammar_text = grammar_path.read_text(encoding="utf-8")
    sample_input = (
        sample_path.read_text(encoding="utf-8")
        if sample_path.exists()
        else "SELECT name, email FROM users WHERE age > 25"
    )

    if args.server == "docker":
        cmd = ["docker", "run", "-i", "--rm", args.image]
    else:
        raise RuntimeError("Only docker mode supported")

    client = McpStdioClient.start(cmd)
    try:
        client.initialize()

        print("[1/3] Validating SQL grammar...")
        validation = client.call_tool("validate_grammar", {"grammar_text": grammar_text, "grammar_name": "SqlSubset"})
        if not validation.get("success"):
            print(json.dumps(validation, indent=2))
            return 1
        print("[ok] Grammar is valid")

        print("\n[2/3] Parsing SQL query...")
        parsed = client.call_tool(
            "parse_sample",
            {"grammar_text": grammar_text, "sample_input": sample_input, "start_rule": "statement", "show_tokens": False},
        )
        if parsed.get("success"):
            print(f"[ok] SQL parsed successfully")
            print(f"Parse tree: {parsed.get('parseTree', '')[:300]}...")
        else:
            print(f"[error] Parse failed")
            return 1

        print(f"\n[3/3] Generating {args.target} parser...")
        compiled = client.call_tool(
            "compile_grammar_multi_target",
            {
                "grammar_text": grammar_text,
                "target_language": args.target,
                "generate_listener": True,
                "generate_visitor": True,
                "include_generated_code": True,
            },
        )
        if not compiled.get("success"):
            print(json.dumps(compiled, indent=2))
            return 1

        files = compiled.get("files") or []
        out_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            file_name = f.get("fileName")
            content = f.get("content")
            if file_name and content is not None:
                (out_dir / file_name).parent.mkdir(parents=True, exist_ok=True)
                (out_dir / file_name).write_text(content, encoding="utf-8")

        print(f"[ok] Generated {len(files)} files to {out_dir}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
