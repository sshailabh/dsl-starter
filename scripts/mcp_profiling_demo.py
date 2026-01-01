#!/usr/bin/env python3
"""
Grammar Performance Profiling Demo

Demonstrates the profile_grammar tool which uses ANTLR4's ProfilingATNSimulator
to gather detailed parsing statistics:
- Decision complexity and timing
- SLL vs LL lookahead analysis
- DFA state usage
- Optimization recommendations
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_client import McpStdioClient


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Grammar Profiling Demo")
    p.add_argument("--server", choices=["docker", "jar"], default="docker")
    p.add_argument("--image", default="sshailabh/antlr4-mcp-server:latest")
    p.add_argument("--jar-path", default="")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    return p.parse_args()


# Complex expression grammar to profile
EXPR_GRAMMAR = r"""
grammar ComplexExpr;

// Expression grammar with operators
program: statement* EOF ;

statement
    : VAR ID EQ expression SEMI
    | IF LPAREN expression RPAREN block (ELSE block)?
    | WHILE LPAREN expression RPAREN block
    | RETURN expression? SEMI
    | expression SEMI
    ;

block: LBRACE statement* RBRACE ;

expression
    : expression (MUL|DIV) expression
    | expression (PLUS|MINUS) expression
    | expression (LT|GT|LE|GE) expression
    | expression (EQEQ|NE) expression
    | expression AND expression
    | expression OR expression
    | NOT expression
    | MINUS expression
    | LPAREN expression RPAREN
    | TRUE | FALSE
    | STRING
    | NUMBER
    | ID
    ;

// Keywords
VAR    : 'var' ;
IF     : 'if' ;
ELSE   : 'else' ;
WHILE  : 'while' ;
RETURN : 'return' ;
TRUE   : 'true' ;
FALSE  : 'false' ;

// Operators
PLUS   : '+' ;
MINUS  : '-' ;
MUL    : '*' ;
DIV    : '/' ;
EQ     : '=' ;
EQEQ   : '==' ;
NE     : '!=' ;
LT     : '<' ;
GT     : '>' ;
LE     : '<=' ;
GE     : '>=' ;
AND    : '&&' ;
OR     : '||' ;
NOT    : '!' ;

// Punctuation
LPAREN : '(' ;
RPAREN : ')' ;
LBRACE : '{' ;
RBRACE : '}' ;
SEMI   : ';' ;

// Atoms
ID     : [a-zA-Z_][a-zA-Z_0-9]* ;
NUMBER : [0-9]+ ('.' [0-9]+)? ;
STRING : '"' (~["])* '"' ;
WS     : [ \t\r\n]+ -> skip ;
"""

# Sample code to parse
SAMPLE_CODE = """
var x = 1;
var y = 2 + 3 * 4;
var z = (x + y) * 2;

if (x > 0) {
    y = y + 1;
    if (y > 10) {
        z = z * 2;
    }
}

while (x < 100) {
    x = x + 1;
}

return x + y + z;
"""


def main() -> int:
    args = parse_args()
    
    if args.server == "docker":
        cmd = ["docker", "run", "-i", "--rm", args.image]
    else:
        repo_root = Path(args.repo_root).resolve()
        jar_path = args.jar_path.strip() or str(repo_root / "antlr4-mcp-server" / "target" / "antlr4-mcp-server-0.2.0.jar")
        cmd = ["java", "-jar", jar_path]

    print("="*70)
    print("  ANTLR4 Grammar Performance Profiling Demo")
    print("="*70)

    client = McpStdioClient.start(cmd)
    
    try:
        client.initialize()
        print("✓ Connected to MCP server\n")
        
        # First validate the grammar
        print("--- Validating Grammar ---")
        result = client.call_tool("validate_grammar", {
            "grammar_text": EXPR_GRAMMAR
        })
        print(f"Grammar: {result.get('grammarName', 'ComplexExpr')}")
        print(f"Valid: {result.get('success')}")
        
        # Profile the grammar
        print("\n" + "="*70)
        print("  PROFILING RESULTS")
        print("="*70)
        
        result = client.call_tool("profile_grammar", {
            "grammar_text": EXPR_GRAMMAR,
            "sample_input": SAMPLE_CODE,
            "start_rule": "program"
        })
        
        print(f"\nSuccess: {result.get('success')}")
        print(f"Grammar: {result.get('grammarName', 'N/A')}")
        
        # Aggregate statistics
        print("\n--- Aggregate Statistics ---")
        total_time_ms = result.get('totalTimeNanos', 0) / 1_000_000
        print(f"Total Parse Time:       {total_time_ms:.3f} ms")
        print(f"Total SLL Lookahead:    {result.get('totalSLLLookahead', 0)}")
        print(f"Total LL Lookahead:     {result.get('totalLLLookahead', 0)}")
        print(f"Total ATN Transitions:  {result.get('totalATNTransitions', 0)}")
        print(f"Total DFA States:       {result.get('totalDFAStates', 0)}")
        
        # SLL vs LL analysis
        sll = result.get('totalSLLLookahead', 0)
        ll = result.get('totalLLLookahead', 0)
        if sll > 0 or ll > 0:
            sll_pct = (sll / (sll + ll)) * 100 if (sll + ll) > 0 else 0
            print(f"\nSLL Success Rate:       {sll_pct:.1f}%")
            if ll > 0:
                print("  ⚠️  LL fallbacks detected - some decisions require extra lookahead")
            else:
                print("  ✓ All decisions resolved with SLL (fast path)")
        
        # Decision details
        if result.get('decisions'):
            decisions = result.get('decisions', [])
            
            print(f"\n--- Decision Analysis ({len(decisions)} decisions) ---")
            
            # Sort by time
            by_time = sorted(decisions, key=lambda x: x.get('timeNanos', 0), reverse=True)
            print("\nTop 5 Slowest Decisions:")
            print(f"{'#':<4} {'Rule':<20} {'Time(ms)':<10} {'Invocations':<12} {'LL Fallback':<12}")
            print("-" * 60)
            for dec in by_time[:5]:
                dec_num = dec.get('decisionNumber', '?')
                rule = dec.get('ruleName', 'unknown')
                time_ms = dec.get('timeNanos', 0) / 1_000_000
                invocations = dec.get('invocations', 0)
                ll_fallback = dec.get('llFallback', 0)
                print(f"{dec_num:<4} {rule:<20} {time_ms:<10.3f} {invocations:<12} {ll_fallback:<12}")
            
            # Find decisions with LL fallback
            ll_decisions = [d for d in decisions if d.get('llFallback', 0) > 0]
            if ll_decisions:
                print(f"\n⚠️  {len(ll_decisions)} decisions required LL fallback:")
                for dec in ll_decisions[:5]:
                    rule = dec.get('ruleName', 'unknown')
                    ll_fallback = dec.get('llFallback', 0)
                    ll_max = dec.get('llMaxLook', 0)
                    print(f"    {rule}: {ll_fallback} fallbacks, max lookahead: {ll_max}")
            
            # Find ambiguous decisions
            ambiguous = [d for d in decisions if d.get('ambiguityCount', 0) > 0]
            if ambiguous:
                print(f"\n⚠️  {len(ambiguous)} decisions had ambiguities:")
                for dec in ambiguous[:5]:
                    rule = dec.get('ruleName', 'unknown')
                    amb_count = dec.get('ambiguityCount', 0)
                    print(f"    {rule}: {amb_count} ambiguities")
            
            # DFA state analysis
            print("\n--- DFA State Usage ---")
            by_dfa = sorted(decisions, key=lambda x: x.get('dfaStates', 0), reverse=True)
            print(f"{'Rule':<25} {'DFA States':<12} {'SLL Trans':<12} {'LL Trans':<12}")
            print("-" * 65)
            for dec in by_dfa[:5]:
                rule = dec.get('ruleName', 'unknown')
                dfa_states = dec.get('dfaStates', 0)
                sll_trans = dec.get('sllDFATransitions', 0)
                ll_trans = dec.get('llDFATransitions', 0)
                print(f"{rule:<25} {dfa_states:<12} {sll_trans:<12} {ll_trans:<12}")
        
        # Insights and hints
        if result.get('insights'):
            print("\n--- Insights ---")
            for insight in result.get('insights', []):
                print(f"  • {insight}")
        
        if result.get('optimizationHints'):
            print("\n--- Optimization Hints ---")
            for hint in result.get('optimizationHints', []):
                print(f"  💡 {hint}")
        
        # Summary
        print("\n" + "="*70)
        print("  PERFORMANCE SUMMARY")
        print("="*70)
        print(f"""
Key Metrics:
  • Parse Time: {total_time_ms:.3f} ms for {len(SAMPLE_CODE)} bytes of input
  • SLL/LL Ratio: {sll}/{ll} (higher SLL = faster parsing)
  • DFA States: {result.get('totalDFAStates', 0)} (cached for reuse)

What to look for:
  1. High LL Fallback: Indicates grammar needs more lookahead
  2. Many Ambiguities: Grammar may have structural issues
  3. High DFA States: Complex decisions, but states are cached
  4. Long Max Lookahead: Parser must look far ahead to decide

Tips:
  • Use left-factoring to reduce lookahead requirements
  • Semantic predicates can resolve ambiguities
  • Consider rule restructuring for hot paths
""")
        
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
