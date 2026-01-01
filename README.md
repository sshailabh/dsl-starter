# DSL Starter Kit

Build parsers for your domain-specific languages without the pain.

---

## What This Solves

You have a custom format you need to parse:

```
route GET /users/{id} -> UserController.show;
```

```sql
SELECT name FROM users WHERE age > 25
```

```ini
[database]
host = localhost
port = 5432
```

You don't want to write regex spaghetti. You don't want to spend weeks learning parser theory.

**This kit lets you describe your language in plain English, and an AI generates a working parser.**

---

## How It Works

1. You describe your language to Claude (or Cursor)
2. The AI writes and validates the grammar
3. You test with sample inputs
4. The AI generates parser code in your language (Python, Java, TypeScript, etc.)

The magic: an MCP server gives the AI real parsing tools, so it validates instead of guessing.

---

## Setup

### 1. Pull the Docker Image

```bash
docker pull sshailabh1/antlr4-mcp-server:latest
```

### 2. Configure MCP server in MCP Client(Claude Desktop/ChatGPT)

<details>
<summary><b>Claude Desktop</b></summary>

Add to your config file: `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "antlr4": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "sshailabh1/antlr4-mcp-server:latest"]
    }
  }
}
```

Start Claude Desktop after saving.

</details>



</details>

### 3. Verify Setup

Ask MCP CLient(AI assistant):

> "List all available ANTLR4 tools"

You should see 9 tools listed.

---

## Try It

Ask Claude:

> "I need to parse config files like this:
> ```
> [server]
> port = 8080
> ```
> Write a grammar, validate it, and parse my example."

Claude will:
- Write the grammar
- Validate it (catching real errors)
- Show you the parse tree
- Generate a parser in your language

---

## Example Grammars Included

| File | What It Parses |
|------|----------------|
| `Hello.g4` | Simple greetings (learning example) |
| `Calculator.g4` | Math expressions with precedence |
| `RouteDsl.g4` | HTTP route definitions |
| `ConfigDsl.g4` | INI-style config files |
| `JsonSubset.g4` | JSON documents |
| `SqlSubset.g4` | Basic SQL queries |

Each has a matching sample file in `samples/`.

---

## Generate a Parser

Once your grammar works:

> "Generate a Python parser with visitor support."

Install the runtime and use it:

```bash
pip install antlr4-python3-runtime
```

```python
from antlr4 import CommonTokenStream, InputStream
from RouteDslLexer import RouteDslLexer
from RouteDslParser import RouteDslParser

lexer = RouteDslLexer(InputStream(text))
parser = RouteDslParser(CommonTokenStream(lexer))
tree = parser.file_()
```

---

## Supported Languages

Python, Java, JavaScript, TypeScript, Go, C#, C++, Swift, PHP, Dart

---

## What the AI Can Do

| Ask This | What Happens |
|----------|--------------|
| "Validate this grammar" | Checks for syntax errors |
| "Parse this input" | Shows the parse tree |
| "Check for ambiguities" | Finds parsing conflicts |
| "Generate a Python parser" | Creates working code |
| "Show the rule dependencies" | Visualizes grammar structure |


---

## License

Apache 2.0
