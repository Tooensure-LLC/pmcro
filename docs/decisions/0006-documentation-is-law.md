# 0006: Documentation is law

Status: accepted · 2026-10-01 (owner instruction: "always by law heavy documentation")

## Decision
The validator and CI fail when: a plugin lacks `README.md` (with `## Skills`, `## Install`, `## Status`, every skill named); a plugin's `CHANGELOG.md` lacks an entry for its current version; a script has fewer than 2 docstring lines or is not mentioned in its skill; a tool lacks a docstring; a file under `docs/` is not linked from `docs/README.md`. Every decision gets a numbered record here. The rule binds agents, including Claude, as much as people (see `AGENTS.md`).

## Consequences
Changing a skill or plugin means updating its README and CHANGELOG in the same commit, and bumping the version for behavior changes. Docs must say what was NOT tested.
