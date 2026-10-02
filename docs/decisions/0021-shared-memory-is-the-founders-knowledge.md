# 0021: Shared memory is the founder's knowledge, tiered and human-accepted

Status: accepted (candidate) · 2026-10-01 (owner: agent memory is pretty much my shared memory; one person cannot remember so much, and that is my knowledge)

## Decision
`pmcro-memory` keeps knowledge as plain markdown files with front matter, searchable by a stdlib keyword search. It uses the same four tiers as the trail player, filters every read by a *viewer* fixed by the reader (founder, a named seat, company, public), is append-only (a correction supersedes an entry), refuses credentials, and lets only the founder mark a memory accepted; agents write candidates. This matches the company rule that learning is proposed by a role and accepted by a human, and the harness's file-memory idea without depending on it.

## Consequences
Memory is portable and model-independent. Keyword search misses differently worded facts; meaning search would need embeddings (OPEN). Local tiers are lost with a temporary container and need a backup the founder chooses. Anything exposed over MCP must fix the viewer on the server side (ADR 0022).
