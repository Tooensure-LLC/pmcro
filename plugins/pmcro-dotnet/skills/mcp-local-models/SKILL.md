---
name: mcp-local-models
description: Connect a local Ollama model to MCP servers (GitHub MCP, .NET MCP servers such as the MSBuild binlog server, filesystem, your own) through Microsoft Agent Framework, with a per-role tool allow-list and approvals. Use when the user wants a local model or seat bot to call GitHub MCP or any MCP server, asks to expose or consume MCP tools from .NET or Python, needs a Checker that can read but never write through MCP, or sees a small model flooded or confused by too many MCP tools. Not for building a new MCP server from scratch, and not for Claude Code's own `.mcp.json` hosting.
license: MIT
---

# MCP for local models

A local model cannot cope with a server that advertises dozens of tools, and an agent with every
tool can do harm. So each role gets a short, explicit list. MAF hides everything not on the list
from the model (verified: a tool outside `allowed_tools` never appears in the tool list), and
`approval_mode="always_require"` makes a human approve any call that is allowed.

## Do this

1. Describe servers once in a config file shaped like `assets/mcp-servers.example.json`: transport, command or url, the **names** of environment variables for secrets (never values), and per-role `allowed_tools`.
2. Run `python <skill-dir>/scripts/load_mcp.py <config> --check`. It rejects inline credentials, plain `http://` to a non-loopback host, and any server with no allow-list for a role that has access.
3. Build tools for a role with `load_mcp.build_tools(config, role)` and pass them to `OllamaChatClient(host=..., model=...).as_agent(tools=tools)`. Read `references/wiring.md` for the exact calls.
4. List what a role will see with `python <skill-dir>/scripts/load_mcp.py <config> --role checker --list`. Read that output before trusting it.
5. Keep each role to roughly 10 tools or fewer for small models. If a server needs more, set `use_progressive_disclosure` so MAF loads schemas on demand.

## Never

- Never put a token, key or password in the config, in `mcp.json`, or in a trail frame. Pass the variable name; the loader reads the environment when connecting.
- Never give the Checker a tool that writes. The Checker's list is read tools only, and write tools stay off it even if the server offers them.
- Never claim a model "talked to" a server unless you ran it and saw the call. Only the loader and the stdio fixture are tested here; a live Ollama and the GitHub server are not.

## Output contract

For `--check`: print `ok: N servers` or one `ERROR <server>: <reason>` per problem, exit 1 on any
error. For `--list`: one line per tool, `server.tool [approval]`, then a count.

Read `references/wiring.md` for Python and .NET calls and the GitHub and .NET server notes.
