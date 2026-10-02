---
name: mcp-server-factory
description: "Generate and run the company's own MCP servers so any agent can load its skills on demand and, read-only, recall its memory and queue. Use when the user wants an MCP server for the marketplace, wants local or offline agents to reach skills, memory or the inbox over MCP, asks for a .NET MCP server project in the existing Config, Tools, Resources and Prompts pattern, or needs the client configuration to connect one. Not for write access, deploys, or exposing anything private."
license: MIT
---

# MCP server factory

A skill is only useful if an agent can find it and load just what it needs. MCP gives agents a
standard way to do that. This skill produces two read-only servers and the settings to connect them.
The owner connects the clients and decides which agents get access; this skill never connects anything.

## Do this

1. **Run the Python server** (works offline over stdio): `python <skill-dir>/scripts/pmcro_mcp.py --plugins-root plugins`. It serves `skill://index.json`, each `skill://NAME/SKILL.md`, and supporting `references/` and `assets/` files, one on demand. Check it without a client: add `--print-index`.
2. **Limit what it serves.** Add `--plugin pmcro-core` (repeatable) to serve only chosen plugins. Never point it at a folder with private material; it refuses `.trail-local`.
3. **Add read-only tools only if asked.** `--tools memory` adds memory search and show; `--tools inbox --tiers public,company` adds queue listing. Set `--viewer` to the reader's identity (`founder`, `seat:cfo`, `company`, `public`). The viewer is fixed when the server starts; a caller can never choose a broader one.
4. **Generate the .NET server when the owner wants one:** `python <skill-dir>/scripts/generate_dotnet_server.py --name Pmcro.Mcp.Skills --out <dir>`. It follows the owner's existing servers. Tell the owner plainly that it has not been compiled and must be built first.
5. **Hand over the connection settings** from `references/connecting.md`. The owner chooses the client, the agents and the permissions; do not guess them.

## Never

- Never serve scripts, anything outside a skill's SKILL.md, references and assets, symbolic links, or files over the size cap.
- Never add a write tool. If the owner wants writes, that is a new decision with approval on, not a flag here.
- Never set `--viewer founder` for an agent or a remote client; that exposes private memory.
- Never claim the .NET project works, or that a client connected, unless you built or ran it.

## Output contract

State which server you started or generated, its arguments, what it serves (count of skills), the
viewer and tiers if tools are on, and what was NOT verified (.NET compile, HTTP transport, any
real client other than MAF's).

Read `references/connecting.md` for client settings. Each script documents its arguments and
refusals in its docstring.
