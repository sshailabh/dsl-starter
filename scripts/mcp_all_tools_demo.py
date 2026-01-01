#!/usr/bin/env python3
"""
Comprehensive demo of ALL 9 ANTLR4 MCP Server tools.

Tools demonstrated:
1. validate_grammar     - Validate grammar syntax
2. parse_sample         - Parse input with grammar
3. compile_grammar_multi_target - Generate parser code
4. detect_ambiguity     - Find grammar ambiguities
5. analyze_left_recursion - Detect left recursion patterns
6. analyze_first_follow - Compute FIRST/FOLLOW sets
7. analyze_call_graph   - Generate rule dependency graph
8. profile_grammar      - Performance profiling
9. visualize_atn        - ATN state machine visualization
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_client import McpStdioClient


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test all 9 ANTLR4 MCP Server tools")
    p.add_argument("--server", choices=["docker", "jar"], default="docker")
    p.add_argument("--image", default="antlr4-mcp-server:latest")
    p.add_argument("--jar-path", default="")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    p.add_argument("--verbose", "-v", action="store_true", help="Show full responses")
    return p.parse_args()


# Sample grammar with interesting features for analysis
DEMO_GRAMMAR = """
grammar Expression;

// Parser rules - includes left recursion for precedence
prog: stat+ ;

stat: expr SEMI                    # exprStat
    | ID '=' expr SEMI             # assignStat
    | 'if' '(' expr ')' stat       # ifStat
    | 'if' '(' expr ')' stat 'else' stat  # ifElseStat
    | '{' stat* '}'                # blockStat
    ;

expr: expr ('*'|'/') expr          # mulDiv
    | expr ('+'|'-') expr          # addSub
    | expr ('=='|'!='|'<'|'>') expr  # compare
    | '(' expr ')'                 # parens
    | ID                           # id
    | INT                          # int
    | '-' expr                     # negate
    ;

// Lexer rules
ID   : [a-zA-Z_][a-zA-Z_0-9]* ;
INT  : [0-9]+ ;
SEMI : ';' ;
WS   : [ \\t\\r\\n]+ -> skip ;
"""

DEMO_INPUT = """
x = 1 + 2 * 3;
y = (x + 1) * 2;
if (x > 0) {
    y = y + 1;
}
"""


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main() -> int:
    args = parse_args()
    
    if args.server == "docker":
        cmd = ["docker", "run", "-i", "--rm", args.image]
    elif args.server == "jar":
        repo_root = Path(args.repo_root).resolve()
        jar_path = args.jar_path.strip()
        if not jar_path:
            jar_path = str(repo_root / "antlr4-mcp-server" / "target" / "antlr4-mcp-server-0.2.0.jar")
        cmd = ["java", "-jar", jar_path]
    else:
        raise RuntimeError(f"Unsupported server mode: {args.server}")

    print("="*60)
    print("  ANTLR4 MCP Server - All 9 Tools Demo")
    print("="*60)
    print(f"Server: {' '.join(cmd[:3])}...")

    client = McpStdioClient.start(cmd)
    results = {}
    
    try:
        client.initialize()
        
        # List tools
        tools_resp = client.request("tools/list")
        tools = tools_resp.get("result", {}).get("tools", [])
        print(f"\n✓ Connected to MCP server")
        print(f"✓ {len(tools)} tools available:")
        for t in tools:
            print(f"    - {t.get('name')}")

        # ============================================================
        # TOOL 1: validate_grammar
        # ============================================================
        print_section("Tool 1: validate_grammar")
        print("Validates ANTLR4 grammar syntax and reports errors.\n")
        
        result = client.call_tool("validate_grammar", {
            "grammar_text": DEMO_GRAMMAR,
            "grammar_name": "Expression"
        })
        results["validate_grammar"] = result
        
        print(f"  Grammar Name: {result.get('grammarName')}")
        print(f"  Success: {result.get('success')}")
        print(f"  Rule Count: {result.get('ruleCount', 'N/A')}")
        if result.get('rules'):
            print(f"  Rules: {', '.join(result.get('rules', []))}")
        
        # ============================================================
        # TOOL 2: parse_sample
        # ============================================================
        print_section("Tool 2: parse_sample")
        print("Parses sample input using the grammar.\n")
        
        result = client.call_tool("parse_sample", {
            "grammar_text": DEMO_GRAMMAR,
            "sample_input": "x = 1 + 2 * 3;",
            "start_rule": "stat",
            "show_tokens": True
        })
        results["parse_sample"] = result
        
        print(f"  Success: {result.get('success')}")
        print(f"  Parse Tree: {result.get('parseTree', 'N/A')[:100]}...")
        if result.get('tokens'):
            print(f"  Token Count: {len(result.get('tokens', []))}")
            if args.verbose:
                for tok in result.get('tokens', [])[:5]:
                    print(f"    {tok}")
        
        # ============================================================
        # TOOL 3: compile_grammar_multi_target
        # ============================================================
        print_section("Tool 3: compile_grammar_multi_target")
        print("Generates parser code for target languages.\n")
        
        for target in ["java", "python", "javascript"]:
            result = client.call_tool("compile_grammar_multi_target", {
                "grammar_text": DEMO_GRAMMAR,
                "target_language": target,
                "generate_listener": True,
                "generate_visitor": True,
                "include_generated_code": False
            })
            file_count = result.get('fileCount', 0)
            print(f"  {target.capitalize():12} → {file_count} files generated")
        
        results["compile_grammar_multi_target"] = result
        
        # ============================================================
        # TOOL 4: detect_ambiguity
        # ============================================================
        print_section("Tool 4: detect_ambiguity")
        print("Analyzes grammar for potential ambiguities.\n")
        
        result = client.call_tool("detect_ambiguity", {
            "grammar_text": DEMO_GRAMMAR
        })
        results["detect_ambiguity"] = result
        
        print(f"  Has Ambiguities: {result.get('hasAmbiguities', False)}")
        if result.get('ambiguities'):
            print(f"  Ambiguity Count: {len(result.get('ambiguities', []))}")
            for amb in result.get('ambiguities', [])[:3]:
                print(f"    - {amb.get('description', amb)[:60]}...")
        else:
            print("  No structural ambiguities detected")
            
        # Test with an ambiguous grammar
        ambiguous_grammar = """
grammar Ambig;
stat: expr ';' | ID '(' ')' ';' ;
expr: ID | ID '(' ')' ;
ID: [a-z]+ ;
"""
        result2 = client.call_tool("detect_ambiguity", {
            "grammar_text": ambiguous_grammar,
            "sample_inputs": ["foo();"]
        })
        print(f"\n  Testing ambiguous grammar:")
        print(f"  Has Ambiguities: {result2.get('hasAmbiguities', False)}")
        
        # ============================================================
        # TOOL 5: analyze_left_recursion
        # ============================================================
        print_section("Tool 5: analyze_left_recursion")
        print("Detects and analyzes left recursion patterns.\n")
        
        result = client.call_tool("analyze_left_recursion", {
            "grammar_text": DEMO_GRAMMAR
        })
        results["analyze_left_recursion"] = result
        
        print(f"  Has Left Recursion: {result.get('hasLeftRecursion', False)}")
        print(f"  Has Direct Left Recursion: {result.get('hasDirectLeftRecursion', False)}")
        print(f"  Has Indirect Left Recursion: {result.get('hasIndirectLeftRecursion', False)}")
        
        if result.get('leftRecursiveRules'):
            print(f"  Left Recursive Rules: {result.get('leftRecursiveRules')}")
        
        if result.get('analysis'):
            print("\n  Rule Analysis:")
            for rule, info in list(result.get('analysis', {}).items())[:3]:
                lr_type = info.get('leftRecursionType', 'none')
                print(f"    {rule}: {lr_type}")
        
        # ============================================================
        # TOOL 6: analyze_first_follow
        # ============================================================
        print_section("Tool 6: analyze_first_follow")
        print("Computes FIRST and FOLLOW sets for grammar rules.\n")
        
        result = client.call_tool("analyze_first_follow", {
            "grammar_text": DEMO_GRAMMAR,
            "rule_name": "expr"
        })
        results["analyze_first_follow"] = result
        
        print(f"  Success: {result.get('success')}")
        print(f"  Total Parser Rules: {result.get('totalParserRules', 'N/A')}")
        print(f"  Nullable Rule Count: {result.get('nullableRuleCount', 0)}")
        print(f"  Rules with Conflicts: {result.get('rulesWithConflicts', 0)}")
        
        if result.get('rules'):
            print("\n  Rule Analysis:")
            for rule_info in result.get('rules', [])[:3]:
                rule_name = rule_info.get('ruleName', 'unknown')
                first_set = rule_info.get('firstSet', [])
                follow_set = rule_info.get('followSet', [])
                nullable = rule_info.get('nullable', False)
                print(f"    {rule_name}:")
                print(f"      FIRST: {first_set[:5]}{'...' if len(first_set) > 5 else ''}")
                print(f"      FOLLOW: {follow_set[:5]}{'...' if len(follow_set) > 5 else ''}")
                print(f"      Nullable: {nullable}")
        
        # ============================================================
        # TOOL 7: analyze_call_graph
        # ============================================================
        print_section("Tool 7: analyze_call_graph")
        print("Generates rule dependency/call graph.\n")
        
        result = client.call_tool("analyze_call_graph", {
            "grammar_text": DEMO_GRAMMAR,
            "output_format": "mermaid"
        })
        results["analyze_call_graph"] = result
        
        print(f"  Success: {result.get('success', True)}")
        print(f"  Node Count: {result.get('nodeCount', 'N/A')}")
        print(f"  Edge Count: {result.get('edgeCount', 'N/A')}")
        
        if result.get('mermaid'):
            mermaid = result.get('mermaid', '')
            lines = mermaid.strip().split('\n')
            print(f"\n  Mermaid Diagram Preview:")
            for line in lines[:8]:
                print(f"    {line}")
            if len(lines) > 8:
                print(f"    ... ({len(lines) - 8} more lines)")
        
        # Also get DOT format
        result2 = client.call_tool("analyze_call_graph", {
            "grammar_text": DEMO_GRAMMAR,
            "output_format": "dot"
        })
        if result2.get('dot'):
            print(f"\n  DOT format also available ({len(result2.get('dot', ''))} chars)")
        
        # ============================================================
        # TOOL 8: profile_grammar
        # ============================================================
        print_section("Tool 8: profile_grammar")
        print("Profiles parsing performance.\n")
        
        result = client.call_tool("profile_grammar", {
            "grammar_text": DEMO_GRAMMAR,
            "sample_input": DEMO_INPUT,
            "start_rule": "prog"
        })
        results["profile_grammar"] = result
        
        print(f"  Success: {result.get('success')}")
        print(f"  Grammar Name: {result.get('grammarName', 'N/A')}")
        total_time_ms = result.get('totalTimeNanos', 0) / 1_000_000
        print(f"  Total Time: {total_time_ms:.2f} ms")
        print(f"  Total SLL Lookahead: {result.get('totalSLLLookahead', 0)}")
        print(f"  Total LL Lookahead: {result.get('totalLLLookahead', 0)}")
        print(f"  Total DFA States: {result.get('totalDFAStates', 0)}")
        
        if result.get('decisions'):
            print("\n  Top Decisions by Invocations:")
            decisions = sorted(
                result.get('decisions', []),
                key=lambda x: x.get('invocations', 0),
                reverse=True
            )[:5]
            for dec in decisions:
                rule = dec.get('ruleName', 'unknown')
                invocations = dec.get('invocations', 0)
                time_ms = dec.get('timeNanos', 0) / 1_000_000
                ll_fallback = dec.get('llFallback', 0)
                print(f"    {rule} (d{dec.get('decisionNumber')}): {invocations} calls, {time_ms:.2f}ms, LL fallback: {ll_fallback}")
        
        if result.get('insights'):
            print("\n  Insights:")
            for insight in result.get('insights', [])[:3]:
                print(f"    - {insight}")
        
        if result.get('optimizationHints'):
            print("\n  Optimization Hints:")
            for hint in result.get('optimizationHints', [])[:3]:
                print(f"    - {hint}")
        
        # ============================================================
        # TOOL 9: visualize_atn
        # ============================================================
        print_section("Tool 9: visualize_atn")
        print("Visualizes ATN (Augmented Transition Network) state machines.\n")
        
        result = client.call_tool("visualize_atn", {
            "grammar_text": DEMO_GRAMMAR,
            "rule_name": "expr",
            "format": "all"
        })
        results["visualize_atn"] = result
        
        print(f"  Rule: {result.get('ruleName', 'expr')}")
        print(f"  State Count: {result.get('stateCount', 'N/A')}")
        print(f"  Transition Count: {result.get('transitionCount', 'N/A')}")
        
        if result.get('mermaid'):
            mermaid = result.get('mermaid', '')
            lines = mermaid.strip().split('\n')
            print(f"\n  Mermaid ATN Preview:")
            for line in lines[:6]:
                print(f"    {line}")
            if len(lines) > 6:
                print(f"    ... ({len(lines) - 6} more lines)")
        
        if result.get('dot'):
            print(f"\n  DOT format: {len(result.get('dot', ''))} chars")
        
        if result.get('svg'):
            print(f"  SVG format: {len(result.get('svg', ''))} chars")
        
        # ============================================================
        # Summary
        # ============================================================
        print_section("Summary")
        
        all_passed = True
        for tool_name, res in results.items():
            success = res.get('success', True) if isinstance(res, dict) else True
            status = "✓" if success else "✗"
            if not success:
                all_passed = False
            print(f"  {status} {tool_name}")
        
        print(f"\n{'='*60}")
        if all_passed:
            print("  All 9 tools tested successfully! ✓")
        else:
            print("  Some tools had issues. Check verbose output for details.")
        print('='*60)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
