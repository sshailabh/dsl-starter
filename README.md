# DSL Starter Kit

**Build domain-specific languages in hours, not weeks.** This is a hands-on starter project that demonstrates how AI assistants (Claude, Cursor) can accelerate ANTLR4 grammar development using the [ANTLR4 MCP Server](../antlr4-mcp-server/).

## The Problem

You're an engineer who needs to:
- Parse configuration files in a custom format
- Build a query language for your internal tools
- Create a routing DSL for your web framework
- Validate domain-specific input before it hits your backend

The traditional path: spend days learning ANTLR4 quirks, debugging cryptic error messages, manually testing edge cases, and generating parser code by hand. Most engineers give up and use regex soup or hand-rolled parsers.

## The Solution

The ANTLR4 MCP Server gives your AI assistant the ability to:

| Capability | What It Does |
|------------|--------------|
| **Validate grammars** | Catch syntax errors before you waste time |
| **Parse inputs** | See the parse tree without generating code |
| **Detect ambiguities** | Find subtle parsing conflicts automatically |
| **Generate parsers** | Output working code for Python, Java, TypeScript, Go, and 6 more languages |
| **Analyze structure** | Understand rule dependencies and recursion patterns |

**Result:** You describe what you want to parse in natural language, Claude writes the grammar, validates it, tests it with your samples, and generates working parser code—all in one conversation.

---

## Quick Start (5 minutes)

### 1. Pull the Docker Image

```bash
docker pull sshailabh/antlr4-mcp-server:latest
```

### 2. Configure Your AI Client

**For Claude Desktop** — Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "antlr4": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "sshailabh/antlr4-mcp-server:latest"]
    }
  }
}
```

**For Cursor IDE** — Copy `configs/cursor-mcp.json` to `.cursor/mcp.json` in your project.

### 3. Start Building

Ask Claude:
> "I need a grammar to parse HTTP route definitions like `GET /users/{id} -> UserController.show`. Validate it and show me the parse tree."

---

## What's Included

### 6 Production-Ready Grammar Examples

| Grammar | Purpose | Complexity |
|---------|---------|------------|
| `Hello.g4` | Learning the basics | Beginner |
| `Calculator.g4` | Arithmetic with operator precedence | Beginner |
| `RouteDsl.g4` | HTTP routing configuration | Intermediate |
| `ConfigDsl.g4` | INI-style configuration files | Intermediate |
| `JsonSubset.g4` | Complete JSON parsing | Intermediate |
| `SqlSubset.g4` | SELECT/INSERT/UPDATE/DELETE | Advanced |

### Automation Scripts

Python scripts that demonstrate the full MCP workflow:

```bash
# Validate, parse, and generate a Python parser for the Route DSL
python3 scripts/mcp_route_dsl_demo.py --server docker

# Run all demos
python3 scripts/mcp_all_tools_demo.py --server docker
```

---

## Real-World Examples

### 1. HTTP Route Configuration

**Grammar:** `grammar/RouteDsl.g4`

```dsl
route GET /users -> Users.list;
route POST /users -> Users.create;
route GET /users/{id} -> Users.get;
route DELETE /users/{id} -> Users.delete;
```

**Generated parse tree:**

```
(file
  (routeDecl route GET /users -> Users.list ;)
  (routeDecl route POST /users -> Users.create ;)
  ...
)
```

### 2. Calculator with Proper Precedence

**Grammar:** `grammar/Calculator.g4`

```
2 + 3 * 4      → 14 (not 20!)
(10 + 5) * 2   → 30
```

ANTLR4 handles operator precedence through rule ordering—multiplication before addition.

### 3. Configuration Files

**Grammar:** `grammar/ConfigDsl.g4`

```ini
[server]
host = localhost
port = 8080

[database]
url = postgresql://localhost/mydb
pool_size = 10
```

### 4. SQL Subset

**Grammar:** `grammar/SqlSubset.g4`

```sql
SELECT name, email FROM users WHERE age > 25
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')
UPDATE users SET email = 'new@email.com' WHERE id = 1
```

---

## The AI-Assisted Workflow

### Traditional DSL Development

```
1. Read ANTLR4 docs for hours
2. Write grammar, run antlr4 tool, get cryptic errors
3. Fix errors, regenerate, write test harness
4. Find ambiguity at runtime, debug for hours
5. Repeat steps 2-4 many times
6. Finally generate parser code
7. Integrate into application
```

**Time: Days to weeks**

### AI-Assisted Development

```
1. Describe your language to Claude
2. Claude writes grammar → validates → parses samples → detects issues
3. Iterate in conversation until parsing works correctly
4. Claude generates parser code for your target language
5. Integrate into application
```

**Time: Minutes to hours**

---

## Available MCP Tools

| Tool | What to Ask Claude |
|------|-------------------|
| `validate_grammar` | "Check if this grammar has any syntax errors" |
| `parse_sample` | "Parse this input and show me the tree" |
| `detect_ambiguity` | "Are there any parsing ambiguities in this grammar?" |
| `analyze_left_recursion` | "Check for left recursion issues" |
| `analyze_first_follow` | "Show me the FIRST/FOLLOW sets for debugging" |
| `analyze_call_graph` | "What rules depend on what?" |
| `visualize_atn` | "Generate a state diagram for this rule" |
| `compile_grammar_multi_target` | "Generate a Python parser with visitor support" |
| `profile_grammar` | "How does this grammar perform on large inputs?" |

---

## Project Structure

```
dsl-starter/
├── grammar/                 # ANTLR4 grammar files
│   ├── Hello.g4
│   ├── Calculator.g4
│   ├── RouteDsl.g4
│   ├── ConfigDsl.g4
│   ├── JsonSubset.g4
│   └── SqlSubset.g4
├── samples/                 # Test inputs for each grammar
│   ├── hello.txt
│   ├── calculator.txt
│   ├── routes.dsl
│   ├── config.ini
│   ├── data.json
│   └── queries.sql
├── scripts/                 # Python MCP client demos
│   ├── mcp_client.py        # Reusable MCP client library
│   ├── mcp_route_dsl_demo.py
│   └── ...
├── configs/                 # MCP client configurations
│   ├── claude-desktop.json
│   └── cursor-mcp.json
├── generated/               # Generated parser code (by demos)
├── BLOG.md                  # Engineering story & deep dive
└── EXAMPLES.md              # More examples & grammars-v4 reference
```

---

## Target Language Support

The MCP server can generate parsers for:

| Language | Runtime Package |
|----------|-----------------|
| Python | `pip install antlr4-python3-runtime` |
| Java | `org.antlr:antlr4-runtime:4.13.2` |
| JavaScript | `npm install antlr4` |
| TypeScript | `npm install antlr4` |
| Go | `github.com/antlr4-go/antlr/v4` |
| C# | `Antlr4.Runtime.Standard` |
| C++ | bundled with ANTLR4 |
| Swift | Swift Package Manager |
| PHP | `composer require antlr/antlr4-runtime` |
| Dart | `pub add antlr4` |

---

## Common Patterns

### Operator Precedence (Calculator Style)

```antlr
expr
    : expr ('*'|'/') expr    // Higher precedence (listed first)
    | expr ('+'|'-') expr    // Lower precedence
    | NUMBER
    | '(' expr ')'
    ;
```

### Keyword vs Identifier

```antlr
// Keywords must come before generic identifier
SELECT : 'SELECT' ;
FROM   : 'FROM' ;
WHERE  : 'WHERE' ;

IDENTIFIER : [a-zA-Z_][a-zA-Z0-9_]* ;
```

### Skipping Whitespace

```antlr
WS : [ \t\r\n]+ -> skip ;
```

### Comments

```antlr
COMMENT : '//' ~[\r\n]* -> skip ;
BLOCK_COMMENT : '/*' .*? '*/' -> skip ;
```

---

## Troubleshooting

### "Grammar validation fails"

- Ensure grammar name matches filename: `grammar Calculator;` in `Calculator.g4`
- Lexer rules must be UPPERCASE, parser rules lowercase
- All referenced rules must be defined

### "Parser generated but doesn't work"

- Install the correct runtime for your target language
- Ensure lexer rules don't overlap unexpectedly (keywords before identifiers)
- Check that whitespace is being skipped

### "Ambiguity detected"

- Use the `detect_ambiguity` tool to find the conflicting alternatives
- Reorder alternatives or add more specific patterns
- Consider using semantic predicates for context-sensitive parsing

---

## Resources

- **[BLOG.md](./BLOG.md)** — Deep dive: How AI transforms DSL development
- **[EXAMPLES.md](./EXAMPLES.md)** — More examples and grammars-v4 reference
- **[ANTLR4 MCP Server](../antlr4-mcp-server/)** — The MCP server powering this
- **[grammars-v4](../grammars-v4/)** — 600+ production grammars for reference
- **[ANTLR4 Official Docs](https://www.antlr.org/)** — Complete language reference

---

## License

Apache License 2.0
