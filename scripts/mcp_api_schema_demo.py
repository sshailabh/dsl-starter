#!/usr/bin/env python3
"""
API Schema DSL demo using ANTLR4 MCP server.

Demonstrates:
- Grammar validation for typed API definitions
- Parsing complex schema structures
- Multi-target code generation
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import mcp_client
sys.path.insert(0, str(Path(__file__).parent))
from mcp_client import McpStdioClient


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="API Schema DSL demo using ANTLR4 MCP server")
    p.add_argument("--server", choices=["docker", "jar"], default="docker",
                   help="Server mode: docker or jar")
    p.add_argument("--image", default="sshailabh/antlr4-mcp-server:latest",
                   help="Docker image to run (for --server docker)")
    p.add_argument("--jar-path", default="",
                   help="Path to antlr4-mcp-server JAR (for --server jar)")
    p.add_argument("--target", default="python",
                   choices=["python", "java", "javascript", "typescript", "go", "csharp"],
                   help="Target language for code generation")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]),
                   help="Repository root path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    grammar_path = repo_root / "dsl-starter" / "grammar" / "ApiSchema.g4"
    sample_path = repo_root / "dsl-starter" / "samples" / "api.schema"
    out_dir = repo_root / "dsl-starter" / "generated" / args.target

    print(f"=== API Schema DSL Demo ===")
    print(f"Grammar: {grammar_path}")
    print(f"Sample:  {sample_path}")
    print(f"Target:  {args.target}")
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
            {"grammar_text": grammar_text, "grammar_name": "ApiSchema"},
        )
        print(f"[ok] validate_grammar success={validation.get('success')} grammarName={validation.get('grammarName')}")
        if not validation.get("success", False):
            print("Validation errors:")
            for err in validation.get("errors", []):
                print(f"  - {err}")
            return 1

        # Step 2: Analyze grammar structure
        print("\n--- Step 2: Analyze Call Graph ---")
        call_graph = client.call_tool(
            "analyze_call_graph",
            {"grammar_text": grammar_text},
        )
        print(f"[ok] analyze_call_graph success={call_graph.get('success')}")
        print(f"     Rules: {call_graph.get('ruleCount', 'N/A')}")
        
        # Step 3: Parse sample input
        print("\n--- Step 3: Parse Sample Input ---")
        parsed = client.call_tool(
            "parse_sample",
            {"grammar_text": grammar_text, "sample_input": sample_input, "start_rule": "schema", "show_tokens": False},
        )
        print(f"[ok] parse_sample success={parsed.get('success')}")
        if not parsed.get("success", False):
            print("Parse errors:")
            for err in parsed.get("errors", []):
                print(f"  - {err}")
            return 1

        # Print a summary of what was parsed
        tree = parsed.get("parseTree", "")
        api_count = tree.count("apiDef")
        endpoint_count = tree.count("endpoint")
        type_count = tree.count("typeDef")
        print(f"     Parsed: {api_count} APIs, {endpoint_count} endpoints, {type_count} types")

        # Step 4: Check for ambiguity
        print("\n--- Step 4: Detect Ambiguity ---")
        ambiguity = client.call_tool(
            "detect_ambiguity",
            {"grammar_text": grammar_text, "sample_input": sample_input, "start_rule": "schema"},
        )
        if ambiguity.get("ambiguityDetected", False):
            print("[warn] Ambiguity detected!")
            for detail in ambiguity.get("ambiguityDetails", []):
                print(f"  - {detail}")
        else:
            print("[ok] No ambiguity detected")

        # Step 5: Generate parser code
        print(f"\n--- Step 5: Generate {args.target.title()} Parser ---")
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
        print(f"[ok] compile_grammar_multi_target success={compiled.get('success')} fileCount={compiled.get('fileCount')}")
        if not compiled.get("success", False):
            print("Compilation errors:")
            for err in compiled.get("errors", []):
                print(f"  - {err}")
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
        
        # Print next steps
        print("\n=== Next Steps ===")
        if args.target == "python":
            print("1. Install runtime: pip install antlr4-python3-runtime")
        elif args.target == "javascript" or args.target == "typescript":
            print("1. Install runtime: npm install antlr4")
        elif args.target == "java":
            print("1. Add to Maven: org.antlr:antlr4-runtime:4.13.2")
        elif args.target == "go":
            print("1. Install: go get github.com/antlr4-go/antlr/v4")
        elif args.target == "csharp":
            print("1. Install: dotnet add package Antlr4.Runtime.Standard")
            
        print(f"2. Use the generated parser files in: {out_dir}")
        print("3. See EXAMPLES.md for usage patterns")
        return 0
        
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())

