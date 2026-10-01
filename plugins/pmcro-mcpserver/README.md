# pmcro-mcpserver

Generate the company's MCP servers: a read-only server that serves every plugin's skills with progressive disclosure, plus a .NET server generator in the owner's pattern.

## Skills

| Skill | Use it to |
| --- | --- |
| `mcp-server-factory` | Run a read-only MCP server that serves every plugin's skills with progressive disclosure (`scripts/pmcro_mcp.py`), optionally with memory and inbox tools; generate a .NET server in the owner's pattern (`scripts/generate_dotnet_server.py`). |

## Install

```
/plugin install pmcro-mcpserver@pmcro-plugins
```

## Status

CANDIDATE. The Python server is tested: MAF's own MCPSkillsSource discovers all skills and loads a body and a reference on demand over an in-memory MCP session; path traversal, symlinks, scripts, binary and oversized files, duplicate names and private roots are refused; the memory and inbox tools use a viewer fixed at start-up. NOT verified: the stdio and HTTP transports with an external client, the HTTP mode at all, any host other than MAF, and the generated .NET project, which has never been compiled (no .NET SDK here). See ADR 0022.
