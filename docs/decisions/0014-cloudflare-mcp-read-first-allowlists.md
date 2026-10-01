# 0014: Cloudflare MCP: read first, per-role allow-lists, no Code Mode by default

Status: accepted (candidate) · 2026-10-01 (owner has an existing site on Cloudflare; Cloudflare also publishes MCP servers)

## Context
Cloudflare's MCP servers (public repo, commit `ab883e5`) can read logs, builds and DNS settings, fetch pages, and also create or delete D1 databases and R2 buckets. A separate Code Mode server reaches the whole API through code execution.

## Decision
Agents learn the existing site by read-only tools first, recording findings as trail frames. Allow-lists are per role in the `mcp-local-models` format; the Checker has read tools only; no create, delete, start, cancel or kill tool is allowed anywhere by default; the Code Mode server is excluded. Tokens are scoped, live only in the human's environment, and the config holds only the variable name. A test enforces that no allow-list contains a changing tool.

## Consequences
Tool semantics were judged from names, not exercised; the docs server's tool names were not found in source; Workers Bindings has more tools than the regex found. Nothing was connected to a real account. A Maker allow-list for changes needs deliberate review.
