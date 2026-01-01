#!/usr/bin/env python3
"""
Route DSL demo using ANTLR4 MCP server.

Demonstrates:
- Grammar validation
- Route parsing
- Python parser generation
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import mcp_client
sys.path.insert(0, str(Path(__file__).parent))
from mcp_client import McpStdioClient


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Route DSL demo using ANTLR4 MCP server")
    p.add_argument("--server", choices=["docker", "jar"], default="docker",
                   help="Server mode: docker or jar")
    p.add_argument("--image", default="antlr4-mcp-server:latest",
                   help="Docker image to run (for --server docker)")
    p.add_argument("--jar-path", default="",
                   help="Path to antlr4-mcp-server JAR (for --server jar)")
    p.add_argument("--out-dir", default="",
                   help="Directory to write generated sources (default: dsl-starter/generated/python)")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]),
                   help="Repository root path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    grammar_path = repo_root / "dsl-starter" / "grammar" / "RouteDsl.g4"
    sample_path = repo_root / "dsl-starter" / "samples" / "routes.dsl"
    
    if args.out_dir.strip():
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = repo_root / "dsl-starter" / "generated" / "python"

    print(f"=== Route DSL Demo ===")
    print(f"Grammar: {grammar_path}")
    print(f"Sample:  {sample_path}")
    print(f"Output:  {out_dir}")
    print()

    grammar_text = grammar_path.read_text(encoding="utf-8")
    sample_input = sample_path.read_text(encoding="utf-8")

    # Build command based on server mode
    if args.server == "docker":
        cmd = ["docker", "run", "-i", "--rm", args.image]
    elif args.server == "jar":
        jar_path = args.jar_path.strip()
        if not jar_path:
            jar_path = str(repo_root / "antlr4-mcp-server" / "target" / "antlr4-mcp-server-0.2.0.jar")
        cmd = ["java", "-jar", jar_path]
    else:
        raise RuntimeError(f"Unsupported server mode: {args.server}")

    print(f"Starting MCP server: {' '.join(cmd)}")
    client = McpStdioClient.start(cmd)
    
    try:
        client.initialize()

        tools = client.request("tools/list")
        if "error" in tools:
            raise RuntimeError(f"tools/list failed: {tools['error']}")
        print(f"[ok] Connected to MCP server")

        # Step 1: Validate grammar
        print("\n--- Step 1: Validate Grammar ---")
        validation = client.call_tool(
            "validate_grammar",
            {"grammar_text": grammar_text, "grammar_name": "RouteDsl"},
        )
        print(f"[ok] validate_grammar success={validation.get('success')} grammarName={validation.get('grammarName')}")
        if not validation.get("success", False):
            print(json.dumps(validation, indent=2))
            return 1

        # Step 2: Parse sample input
        print("\n--- Step 2: Parse Sample Input ---")
        parsed = client.call_tool(
            "parse_sample",
            {"grammar_text": grammar_text, "sample_input": sample_input, "start_rule": "file", "show_tokens": False},
        )
        print(f"[ok] parse_sample success={parsed.get('success')}")
        if not parsed.get("success", False):
            print(json.dumps(parsed, indent=2))
            return 1

        # Step 3: Generate Python parser
        print("\n--- Step 3: Generate Python Parser ---")
        compiled = client.call_tool(
            "compile_grammar_multi_target",
            {
                "grammar_text": grammar_text,
                "target_language": "python",
                "generate_listener": True,
                "generate_visitor": True,
                "include_generated_code": True,
            },
        )
        print(f"[ok] compile_grammar_multi_target success={compiled.get('success')} fileCount={compiled.get('fileCount')}")
        if not compiled.get("success", False):
            print(json.dumps(compiled, indent=2))
            return 1

        # Write generated files
        files = compiled.get("files") or []
        out_dir.mkdir(parents=True, exist_ok=True)
        wrote = 0
        for f in files:
            file_name = f.get("fileName")
            content = f.get("content")
            if not file_name or content is None:
                continue
            dest = out_dir / file_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            wrote += 1
            print(f"  - {file_name}")

        print(f"\n[ok] Wrote {wrote} generated files to: {out_dir}")
        print("\n=== Next Steps ===")
        print("1. Install runtime: pip install antlr4-python3-runtime")
        print(f"2. Use the generated parser files in: {out_dir}")
        return 0
        
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
