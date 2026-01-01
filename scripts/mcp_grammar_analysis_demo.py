#!/usr/bin/env python3
"""
Grammar Analysis Demo - Deep dive into ANTLR4 grammar structure.

Demonstrates:
- analyze_left_recursion: Detect direct/indirect left recursion
- analyze_first_follow: FIRST/FOLLOW sets and LL(1) conflicts
- analyze_call_graph: Rule dependency visualization
- visualize_atn: ATN state machine diagrams
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_client import McpStdioClient


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Grammar Analysis Demo")
    p.add_argument("--server", choices=["docker", "jar"], default="docker")
    p.add_argument("--image", default="sshailabh1/antlr4-mcp-server:latest")
    p.add_argument("--jar-path", default="")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    p.add_argument("--output-dir", default="", help="Directory to save visualizations")
    return p.parse_args()


# Expression grammar with left recursion for precedence handling
EXPR_GRAMMAR = """
grammar Expr;

// Parser rules with operator precedence via left recursion
prog: (stat SEMI)* ;

stat: ID '=' expr      # assign
    | expr             # bareExpr
    ;

expr: expr '*' expr    # mul
    | expr '+' expr    # add
    | expr '==' expr   # eq
    | '(' expr ')'     # paren
    | ID               # var
    | INT              # int
    ;

ID   : [a-zA-Z]+ ;
INT  : [0-9]+ ;
SEMI : ';' ;
WS   : [ \\t\\r\\n]+ -> skip ;
"""

# Alternative grammar with indirect left recursion
INDIRECT_LR_GRAMMAR = """
grammar IndirectLR;

a: b 'x' | 'y' ;
b: c 'z' ;
c: a 'w' | 'v' ;  // Indirect: a -> b -> c -> a

ID: [a-z]+ ;
"""


def main() -> int:
    args = parse_args()
    
    if args.server == "docker":
        cmd = ["docker", "run", "-i", "--rm", args.image]
    else:
        repo_root = Path(args.repo_root).resolve()
        jar_path = args.jar_path.strip() or str(repo_root / "antlr4-mcp-server" / "target" / "antlr4-mcp-server-0.2.0.jar")
        cmd = ["java", "-jar", jar_path]
    
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("  ANTLR4 Grammar Analysis Demo")
    print("="*70)

    client = McpStdioClient.start(cmd)
    
    try:
        client.initialize()
        print("✓ Connected to MCP server\n")

        # ============================================================
        # 1. Left Recursion Analysis
        # ============================================================
        print("="*70)
        print("  1. LEFT RECURSION ANALYSIS")
        print("="*70)
        print("\nLeft recursion is used in ANTLR4 for operator precedence.")
        print("ANTLR4 rewrites direct left recursion into efficient loops.\n")
        
        # Analyze expression grammar (direct left recursion)
        print("--- Expression Grammar (Direct Left Recursion) ---")
        result = client.call_tool("analyze_left_recursion", {
            "grammar_text": EXPR_GRAMMAR
        })
        
        print(f"Has Left Recursion: {result.get('hasLeftRecursion', False)}")
        print(f"Has Direct Left Recursion: {result.get('hasDirectLeftRecursion', False)}")
        print(f"Has Indirect Left Recursion: {result.get('hasIndirectLeftRecursion', False)}")
        
        if result.get('leftRecursiveRules'):
            print(f"Left Recursive Rules: {result.get('leftRecursiveRules')}")
        
        if result.get('analysis'):
            print("\nRule-by-Rule Analysis:")
            for rule, info in result.get('analysis', {}).items():
                lr_type = info.get('leftRecursionType', 'none')
                if lr_type != 'none':
                    print(f"  {rule}: {lr_type}")
                    if info.get('leftRecursiveAlternatives'):
                        print(f"    Alternatives: {info.get('leftRecursiveAlternatives')}")
        
        # Analyze indirect left recursion grammar
        print("\n--- Indirect Left Recursion Grammar ---")
        result2 = client.call_tool("analyze_left_recursion", {
            "grammar_text": INDIRECT_LR_GRAMMAR
        })
        
        print(f"Has Indirect Left Recursion: {result2.get('hasIndirectLeftRecursion', False)}")
        if result2.get('cycles'):
            print(f"Cycles Found: {result2.get('cycles')}")

        # ============================================================
        # 2. FIRST/FOLLOW Set Analysis
        # ============================================================
        print("\n" + "="*70)
        print("  2. FIRST/FOLLOW SET ANALYSIS")
        print("="*70)
        print("\nFIRST(A) = terminals that can begin strings derived from A")
        print("FOLLOW(A) = terminals that can appear after A in any derivation\n")
        
        result = client.call_tool("analyze_first_follow", {
            "grammar_text": EXPR_GRAMMAR
        })
        
        print(f"Total Parser Rules: {result.get('totalParserRules', 'N/A')}")
        print(f"Nullable Rules: {result.get('nullableRuleCount', 0)}")
        print(f"Rules with LL(1) Conflicts: {result.get('rulesWithConflicts', 0)}")
        print(f"Total Decisions: {result.get('totalDecisions', 'N/A')}")
        print(f"Ambiguous Decisions: {result.get('ambiguousDecisions', 0)}")
        
        if result.get('rules'):
            print("\n--- Rule Analysis ---")
            for rule_info in result.get('rules', []):
                rule_name = rule_info.get('ruleName', 'unknown')
                first_set = rule_info.get('firstSet', [])
                follow_set = rule_info.get('followSet', [])
                nullable = rule_info.get('nullable', False)
                has_conflict = rule_info.get('hasLL1Conflict', False)
                alt_count = rule_info.get('alternativeCount', 0)
                
                print(f"\n  {rule_name}:")
                print(f"    Alternatives: {alt_count}")
                print(f"    Nullable: {nullable}")
                print(f"    LL(1) Conflict: {has_conflict}")
                print(f"    FIRST: {', '.join(first_set[:8])}{'...' if len(first_set) > 8 else ''}")
                print(f"    FOLLOW: {', '.join(follow_set[:8])}{'...' if len(follow_set) > 8 else ''}")
        
        if result.get('decisions'):
            print("\n--- Decision Point Analysis ---")
            for dec in result.get('decisions', [])[:3]:
                dec_num = dec.get('decisionNumber', '?')
                rule_name = dec.get('ruleName', 'unknown')
                alt_count = dec.get('alternativeCount', 0)
                ambiguous = dec.get('hasAmbiguousLookahead', False)
                print(f"  Decision {dec_num} in {rule_name}: {alt_count} alternatives, ambiguous={ambiguous}")

        # ============================================================
        # 3. Call Graph Analysis
        # ============================================================
        print("\n" + "="*70)
        print("  3. RULE CALL GRAPH")
        print("="*70)
        print("\nVisualize which rules call which other rules.\n")
        
        # Get Mermaid format
        result = client.call_tool("analyze_call_graph", {
            "grammar_text": EXPR_GRAMMAR,
            "output_format": "mermaid"
        })
        
        print(f"Success: {result.get('success', True)}")
        
        if result.get('mermaid'):
            mermaid = result.get('mermaid', '')
            print("\n--- Mermaid Diagram ---")
            print(mermaid)
            
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / "call_graph.mmd").write_text(mermaid)
                print(f"\nSaved to: {output_dir / 'call_graph.mmd'}")
        
        # Get DOT format
        result2 = client.call_tool("analyze_call_graph", {
            "grammar_text": EXPR_GRAMMAR,
            "output_format": "dot"
        })
        
        if result2.get('dot'):
            dot = result2.get('dot', '')
            print("\n--- DOT Format (Graphviz) ---")
            lines = dot.strip().split('\n')
            for line in lines[:10]:
                print(line)
            if len(lines) > 10:
                print(f"... ({len(lines) - 10} more lines)")
            
            if output_dir:
                (output_dir / "call_graph.dot").write_text(dot)
                print(f"\nSaved to: {output_dir / 'call_graph.dot'}")
                print("Render with: dot -Tpng call_graph.dot -o call_graph.png")

        # ============================================================
        # 4. ATN Visualization
        # ============================================================
        print("\n" + "="*70)
        print("  4. ATN (Augmented Transition Network) VISUALIZATION")
        print("="*70)
        print("\nThe ATN is ANTLR's internal state machine representation.\n")
        
        result = client.call_tool("visualize_atn", {
            "grammar_text": EXPR_GRAMMAR,
            "rule_name": "expr",
            "format": "all"
        })
        
        print(f"Rule: {result.get('ruleName', 'expr')}")
        print(f"State Count: {result.get('stateCount', 'N/A')}")
        print(f"Transition Count: {result.get('transitionCount', 'N/A')}")
        
        if result.get('mermaid'):
            mermaid = result.get('mermaid', '')
            print("\n--- ATN State Diagram (Mermaid) ---")
            lines = mermaid.strip().split('\n')
            for line in lines[:15]:
                print(line)
            if len(lines) > 15:
                print(f"... ({len(lines) - 15} more lines)")
            
            if output_dir:
                (output_dir / "atn_expr.mmd").write_text(mermaid)
                print(f"\nSaved to: {output_dir / 'atn_expr.mmd'}")
        
        if result.get('dot'):
            if output_dir:
                (output_dir / "atn_expr.dot").write_text(result.get('dot', ''))
                print(f"Saved DOT to: {output_dir / 'atn_expr.dot'}")
        
        # Also visualize 'stat' rule
        print("\n--- ATN for 'stat' rule ---")
        result2 = client.call_tool("visualize_atn", {
            "grammar_text": EXPR_GRAMMAR,
            "rule_name": "stat",
            "format": "mermaid"
        })
        
        print(f"State Count: {result2.get('stateCount', 'N/A')}")
        print(f"Transition Count: {result2.get('transitionCount', 'N/A')}")

        # ============================================================
        # Summary
        # ============================================================
        print("\n" + "="*70)
        print("  SUMMARY")
        print("="*70)
        print("""
These analysis tools help you:

1. LEFT RECURSION: Understand how ANTLR4 handles operator precedence
   through left-recursive rules and detects problematic indirect cycles.

2. FIRST/FOLLOW: Debug LL(k) parsing conflicts by examining which
   tokens can start or follow each rule.

3. CALL GRAPH: Visualize rule dependencies to understand grammar
   structure and find unused or circular rules.

4. ATN VISUALIZATION: Inspect ANTLR's internal state machine to
   understand exactly how the parser will process input.
""")
        
        if output_dir:
            print(f"Visualization files saved to: {output_dir}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
