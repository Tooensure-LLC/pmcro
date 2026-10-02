# 0016: Self-reference by default: every capability is also served over MCP

Status: PROPOSED (corrected 2026-10-01 after reading the architecture matrix) · first written 2026-10-01 (owner: "the company should by default [be] self-referential... think MCP server, AI agents")

## Correction

I first recorded this as an accepted principle. The company's own Architecture Approval Matrix keeps MCP projection (`.agents/mcp.json`) OPEN, and the architecture keeps "capability is not authority": PMCR-O is not MCP, and no skill is required to use MCP. So this ADR proposes only that plugins be *servable* over MCP as an option. Servable never means authorized, required or exposed by default to anyone. Until the owner approves it, nothing is served and no server is built.

> Update: the owner approved generating the servers (ADR 0022). Servable-by-default for every skill is still not a mandate; MCP projection stays OPEN in the architecture matrix.

## Context
The company's design is self-referential: PMCR-O builds PMCR-O, trails train models on trails, the marketplace builds the marketplace. Figma's MCP already serves its own skills over `skill://index.json`, and MAF can consume that (`MCPSkillsSource`, experimental). The owner's existing .NET MCP servers use a Config / Tools / Resources / Prompts layout over stateless HTTP.

## Decision
By default every plugin is servable as an MCP server and every role as an agent. One generic, template-driven server reads `plugins/` and serves each skill's `SKILL.md`, references and assets as `skill://` resources (progressive disclosure), plus the deterministic scripts as tools only when a plugin opts in with an explicit tool manifest and an allow-list. MAF never executes scripts delivered over MCP, so tools are the opt-in path. New plugins are scaffolded so they are servable with no extra work.

## Consequences
The marketplace and the server share one source of truth. Serving skills exposes their text to whoever connects, so private-tier content must never be in a servable plugin. A remote server controls what instructions reach an agent, so consumers must trust it. The server is not built yet.
