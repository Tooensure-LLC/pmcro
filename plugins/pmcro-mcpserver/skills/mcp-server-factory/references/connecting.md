# Connecting a client

Status: the stdio server was tested with MAF's own MCP skills client. Settings for other hosts are the common JSON shape and were NOT tried here. The owner makes the connection and sets permissions.

## Python server over stdio (works offline)

```json
{
  "mcpServers": {
    "pmcro-skills": {
      "command": "python",
      "args": ["plugins/pmcro-mcpserver/skills/mcp-server-factory/scripts/pmcro_mcp.py",
               "--plugins-root", "plugins", "--plugin", "pmcro-core"]
    }
  }
}
```

With memory (read-only, fixed viewer): add `"--tools", "memory", "--viewer", "seat:cfo"`.

## From Microsoft Agent Framework (tested)

```python
from agent_framework import MCPSkillsSource, SkillsProvider
# session = an mcp ClientSession connected to the server; MCPSkillsSource is experimental in 1.19.0
source = MCPSkillsSource(client=session)
```

MAF reads `skill://index.json`, builds one skill per entry, and fetches each SKILL.md and reference file only when needed. MAF never runs scripts delivered over MCP.

## .NET server over HTTP

Build the generated project, run it bound to localhost, and point the client at `http://localhost:PORT/mcp`. Untested.

## Trust

A connected server controls what instructions reach an agent. Connect only servers you run yourself. Skill text is guidance, never permission.
