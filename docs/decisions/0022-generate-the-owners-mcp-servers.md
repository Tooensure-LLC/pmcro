# 0022: Generate the owner's MCP servers; the owner wires the connections

Status: accepted (candidate) · 2026-10-01 (owner: "you generate my MCP servers, I'll set up the connection allowing you and what to do"). Resolves the approval question left open in ADR 0016.

## Decision
The company generates two read-only MCP servers: a Python server that serves every plugin's skills as `skill://` resources (the convention MAF reads) with optional read-only memory and inbox tools, and a template-driven .NET server in the pattern of the owner's existing servers (Configuration, Tools, Resources, Prompts, stateless HTTP). The owner decides which clients connect and with what permissions; the company never connects anything itself. Skills are served only from `SKILL.md`, `references/` and `assets/`; scripts, symbolic links, binaries and anything private are refused. Tool access uses a viewer fixed at start-up, so a caller cannot widen a tier. No write tool exists.

## Consequences
Stdio needs no network, so the servers work on the offline machine. MAF's MCP skills source is experimental and may change. MAF never executes scripts delivered over MCP, so scripts stay local. The authoring container cannot build .NET (no SDK, installer blocked), so CI builds it: it compiled on 2026-10-01 with 0 warnings and 0 errors, and a CI smoke test checks it at runtime. MCP projection in the company's architecture matrix is still marked OPEN there; this ADR makes the servers available, it does not make MCP a requirement for any skill. A remote server controls what instructions reach an agent, so servers are for the owner's own use.
