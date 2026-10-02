# 0004: Reuse dotnet/skills as a pinned upstream

Status: accepted (candidate) · 2026-10-01

## Context
dotnet/skills (MIT) has 15 maintained plugins (MAUI, AI, MSBuild with an MCP server, test, and more). Copying them forks maintenance.

## Decision
`upstream.json` pins each plugin to a full 40-character commit. `gen` writes `git-subdir` entries (documented in Claude Code's marketplace reference) into `.claude-plugin/marketplace.json` only. The validator rejects branches, short or uppercase shas, name clashes and path escapes.

## Consequences
Updates are a deliberate sha change plus review. Other hosts' support for object sources is unverified, so their files list local plugins only. An actual install of a pinned entry has not been run here.
