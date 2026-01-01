#!/usr/bin/env python3
"""
Calculator DSL demo using ANTLR4 MCP server.

Demonstrates:
- Grammar validation
- Expression parsing
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
    p = argparse.ArgumentParser(description="Calculator DSL demo")
    p.add_argument("--server", choices=["docker", "jar"], default="docker")
    p.add_argument("--image", default="sshailabh/antlr4-mcp-server:latest")
    p.add_argument("--jar-path", default="")
    p.add_argument("--out-dir", default="", help="Output directory for generated code")
    p.add_argument("--target", default="python", help="Target language (python, javascript, java, etc.)")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    grammar_path = repo_root / "dsl-starter" / "grammar" / "Calculator.g4"
    sample_path = repo_root / "dsl-starter" / "samples" / "calculator.txt"

    if args.out_dir.strip():
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = repo_root / "dsl-starter" / "generated" / args.target

    grammar_text = grammar_path.read_text(encoding="utf-8")
    sample_input = sample_path.read_text(encoding="utf-8") if sample_path.exists() else "2 + 3 * 4"

    if args.server == "docker":
        cmd = ["docker", "run", "-i", "--rm", args.image]
    elif args.server == "jar":
        jar_path = args.jar_path.strip()
        if not jar_path:
            jar_path = str(repo_root / "antlr4-mcp-server" / "target" / "antlr4-mcp-server-0.2.0.jar")
        cmd = ["java", "-jar", jar_path]
    else:
        raise RuntimeError(f"Unsupported server mode: {args.server}")

    client = McpStdioClient.start(cmd)
    try:
        client.initialize()

        # List available tools
        tools = client.request("tools/list")
        if "error" in tools:
            raise RuntimeError(f"tools/list failed: {tools['error']}")
        print(f"[ok] Connected to MCP server, {len(tools.get('result', {}).get('tools', []))} tools available")

        # Validate grammar
        print("\n[1/4] Validating grammar...")
        validation = client.call_tool(
            "validate_grammar",
            {"grammar_text": grammar_text, "grammar_name": "Calculator"},
        )
        print(f"[ok] Grammar validation: success={validation.get('success')}")
        if not validation.get("success", False):
            print(json.dumps(validation, indent=2))
            return 1

        # Parse sample
        print("\n[2/4] Parsing sample input...")
        parsed = client.call_tool(
            "parse_sample",
            {
                "grammar_text": grammar_text,
                "sample_input": sample_input,
                "start_rule": "expr",
                "show_tokens": False,
            },
        )
        print(f"[ok] Parse result: success={parsed.get('success')}")
        if parsed.get("success"):
            print(f"Parse tree: {parsed.get('parseTree', 'N/A')}")

        # Detect ambiguities
        print("\n[3/4] Checking for ambiguities...")
        ambiguity = client.call_tool(
            "detect_ambiguity",
            {"grammar_text": grammar_text},
        )
        has_ambiguities = ambiguity.get("hasAmbiguities", False)
        print(f"[ok] Ambiguity check: hasAmbiguities={has_ambiguities}")
        if has_ambiguities:
            print("⚠️  Ambiguities detected:")
            for amb in ambiguity.get("ambiguities", []):
                print(f"  - {amb.get('description', 'Unknown')}")

        # Generate parser
        print(f"\n[4/4] Generating {args.target} parser...")
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
        print(f"[ok] Code generation: success={compiled.get('success')} fileCount={compiled.get('fileCount')}")
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

        print(f"\n[ok] Wrote {wrote} generated files to: {out_dir}")
        print("\nNext steps:")
        if args.target == "python":
            print("  pip install antlr4-python3-runtime")
            print(f"  python3 -c \"from {out_dir.name}.CalculatorLexer import CalculatorLexer\"")
        elif args.target == "javascript":
            print("  npm install antlr4")
        elif args.target == "java":
            print("  Add antlr4-runtime dependency to your project")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
