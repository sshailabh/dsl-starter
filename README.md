# DSL Starter Project

A comprehensive starter project demonstrating how to use the ANTLR4 MCP Server via Docker for language and DSL development.

## Prerequisites

- **Docker** (required) - Build the MCP server image first
- **Python 3.10+** (for demo scripts)

## Quick Start

### 1. Build the MCP Server Docker Image

```bash
cd ../antlr4-mcp-server
docker build -t antlr4-mcp-server:latest .
cd ../dsl-starter
```

Or use the build script:
```bash
cd ../antlr4-mcp-server && ./docker/build.sh && cd ../dsl-starter
```

### 2. Verify Docker is Working

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | \
  docker run -i --rm antlr4-mcp-server:latest
```

### 3. Run a DSL Example

```bash
python3 scripts/mcp_route_dsl_demo.py --server docker --image antlr4-mcp-server:latest
```

## What's Included

This starter project includes **6 complete DSL examples**:

| DSL | Grammar | Use Case |
|-----|---------|----------|
| **Hello** | `Hello.g4` | Learning ANTLR4 basics |
| **Route DSL** | `RouteDsl.g4` | Web routing configuration |
| **Calculator** | `Calculator.g4` | Arithmetic expressions |
| **JSON Parser** | `JsonSubset.g4` | Data format parsing |
| **SQL Subset** | `SqlSubset.g4` | Query language |
| **Config DSL** | `ConfigDsl.g4` | INI-like configuration |

## Examples

### 1. Route DSL (`grammar/RouteDsl.g4`)

A simple DSL for defining HTTP routes:

```dsl
route GET /users -> Users.list;
route POST /users -> Users.create;
route GET /users/{id} -> Users.get;
```

**Run it**:
```bash
python3 scripts/mcp_route_dsl_demo.py --server docker
```

### 2. Calculator DSL (`grammar/Calculator.g4`)

Arithmetic expression parser with operator precedence:

```
2 + 3 * 4      # = 14 (not 20)
(10 + 5) * 2   # = 30
```

**Run it**:
```bash
python3 scripts/mcp_calculator_demo.py --server docker
```

### 3. JSON Parser (`grammar/JsonSubset.g4`)

Complete JSON parser:

```json
{"name": "Alice", "age": 30, "tags": ["developer", "python"]}
```

**Run it**:
```bash
python3 scripts/mcp_json_demo.py --server docker
```

### 4. SQL Subset (`grammar/SqlSubset.g4`)

Basic SQL query language:

```sql
SELECT name, email FROM users WHERE age > 25
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')
```

**Run it**:
```bash
python3 scripts/mcp_sql_demo.py --server docker
```

### 5. Config DSL (`grammar/ConfigDsl.g4`)

Configuration file language:

```ini
[server]
host = localhost
port = 8080

[database]
url = postgresql://localhost/mydb
```

**Run it**:
```bash
python3 scripts/mcp_config_demo.py --server docker
```

## Project Structure

```
dsl-starter/
├── README.md               # This file
├── grammar/                # ANTLR4 grammar files
│   ├── Hello.g4
│   ├── RouteDsl.g4
│   ├── Calculator.g4
│   ├── JsonSubset.g4
│   ├── SqlSubset.g4
│   └── ConfigDsl.g4
├── samples/                # Sample input files
│   ├── hello.txt
│   ├── routes.dsl
│   ├── calculator.txt
│   ├── data.json
│   ├── queries.sql
│   └── config.ini
├── scripts/                # Python MCP client scripts
│   ├── mcp_client.py       # Reusable MCP client
│   ├── mcp_route_dsl_demo.py
│   ├── mcp_calculator_demo.py
│   ├── mcp_json_demo.py
│   ├── mcp_sql_demo.py
│   └── mcp_config_demo.py
├── configs/                # MCP client configurations
│   ├── claude-desktop.json
│   └── cursor-mcp.json
└── generated/              # Generated parser code (created by scripts)
    ├── python/
    ├── javascript/
    └── java/
```

## Using with AI Assistants

### Claude Desktop

Copy `configs/claude-desktop.json` to your Claude config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Then ask Claude:
- "Validate the Route DSL grammar"
- "Parse this JSON and show me the tree"
- "Generate a Python parser for the Calculator grammar"

### Cursor IDE

Copy `configs/cursor-mcp.json` to `.cursor/mcp.json` in your project.

## DSL Development Workflow

1. **Write your grammar** (`MyDsl.g4`)
2. **Create sample inputs** (`samples/test.dsl`)
3. **Validate** using MCP: `validate_grammar`
4. **Test parsing** using MCP: `parse_sample`
5. **Check for issues**: `detect_ambiguity`, `analyze_left_recursion`
6. **Generate parser**: `compile_grammar_multi_target`
7. **Use the generated parser** in your application

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `validate_grammar` | Check grammar syntax |
| `parse_sample` | Parse input and get tree |
| `detect_ambiguity` | Find parsing conflicts |
| `analyze_left_recursion` | Check recursion patterns |
| `analyze_first_follow` | Compute FIRST/FOLLOW sets |
| `analyze_call_graph` | Rule dependencies |
| `visualize_atn` | State machine diagrams |
| `compile_grammar_multi_target` | Generate parser code |
| `profile_grammar` | Performance analysis |

### Tool Coverage by Demo Script

| Script | Tools Demonstrated |
|--------|-------------------|
| `mcp_all_tools_demo.py` | **All 9 tools** – comprehensive test |
| `mcp_grammar_analysis_demo.py` | `analyze_left_recursion`, `analyze_first_follow`, `analyze_call_graph`, `visualize_atn` |
| `mcp_profiling_demo.py` | `validate_grammar`, `profile_grammar` |
| `mcp_calculator_demo.py` | `validate_grammar`, `parse_sample`, `detect_ambiguity`, `compile_grammar_multi_target` |
| `mcp_route_dsl_demo.py` | `validate_grammar`, `parse_sample`, `compile_grammar_multi_target` |
| `mcp_json_demo.py` | `validate_grammar`, `parse_sample`, `compile_grammar_multi_target` |
| `mcp_sql_demo.py` | `validate_grammar`, `parse_sample`, `compile_grammar_multi_target` |
| `mcp_config_demo.py` | `validate_grammar`, `parse_sample`, `compile_grammar_multi_target` |

Run the comprehensive test:
```bash
python3 scripts/mcp_all_tools_demo.py --server docker
```

## Troubleshooting

### Docker image not found

Build it first:
```bash
cd ../antlr4-mcp-server && docker build -t antlr4-mcp-server:latest . && cd ../dsl-starter
```

### Grammar validation fails

Check:
- Grammar name matches `grammar Name;` declaration
- Lexer rules start with UPPERCASE
- Parser rules start with lowercase
- All referenced rules are defined

### Generated parser not working

Install the runtime for your target language:
- **Python**: `pip install antlr4-python3-runtime`
- **JavaScript**: `npm install antlr4`
- **Java**: Add `org.antlr:antlr4-runtime:4.13.2` to Maven/Gradle

## Next Steps

- Explore the grammar files to understand ANTLR4 syntax
- Modify examples to create your own DSL
- Read the [ANTLR4 MCP Server documentation](../antlr4-mcp-server/README.md)
- Read the [Blog: Building DSLs with AI](docs/BLOG.md) for a comprehensive tutorial
- Check [ANTLR4 official documentation](https://www.antlr.org/)

## License

Apache License 2.0
