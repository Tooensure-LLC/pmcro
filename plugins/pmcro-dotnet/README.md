# pmcro-dotnet

.NET and Microsoft Agent Framework (MAF) skills built so small local models can use them by progressive disclosure.

## Skills

| Skill | Use it to |
| --- | --- |
| `maf-local-skills` | Load skills into MAF with a script allow-list and approvals left on, and confirm every file is reachable (`scripts/list_skills.py`). |
| `mcp-local-models` | Connect an Ollama-backed agent to MCP servers (GitHub MCP, the MSBuild binlog server, your own) with per-role tool allow-lists (`scripts/load_mcp.py`). |

For MAUI, AI, MSBuild, test, ASP.NET Core and the rest of the .NET skills, install the pinned dotnet/skills plugins listed in the marketplace (see `docs/marketplace.md`) rather than looking for them here.

## Install

```
/plugin install pmcro-dotnet@pmcro-plugins
```

## Status

CANDIDATE. Python paths are tested against `agent-framework` 1.19.0 and `mcp` 1.28.1 in CI (stdio fixture only). The .NET paths, a live Ollama model and the GitHub MCP server are NOT tested. See `references/` in each skill for the verified/unverified split.
