# ToDo Local MCP Server

A local MCP server for managing to-do tasks, built with [FastMCP](https://github.com/jlowin/fastmcp).

## Run

```bash
uv run main.py
```

## Tools

| Tool | Description |
|---|---|
| `add_todo` | Add a new task |
| `list_todos` | List tasks (filter by status, priority, tag) |
| `update_todo` | Update any field on a task |
| `complete_todo` | Mark a task as done |
| `delete_todo` | Delete a task permanently |
| `summarize_todos` | Count tasks grouped by status & priority |

## Resources

| Resource | Description |
|---|---|
| `todo://categories` | Available categories (editable in `categories.json`) |

## Connect to Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "TodoManager": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "D:\\MCP\\Project\\ToDo-LocalMCP\\main.py"
      ],
      "env": {},
      "transport": "stdio"
    }
  }
}
```

## Project Structure

```
ToDo-LocalMCP/
├── main.py          # MCP server & tools
├── categories.json  # Editable category list
├── todos.db         # SQLite database (auto-created on first run)
└── README.md
```
