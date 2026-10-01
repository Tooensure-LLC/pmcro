# dotagents convention

Status: CANDIDATE. Verified 2026-10-01 with `@sentry/dotagents` 3.2.0 (npm), against branch `claude/new-session-s40odu` at commit `31c7251`.

The owner is building a PMCR-O assistant (a "replica of Claude") on the dotagents convention. This page records what was actually run so that work can rely on it.

## What "dotagents" means here

[getsentry/dotagents](https://github.com/getsentry/dotagents) (npm `@sentry/dotagents`, beta): `agents.toml` declares skills and plugins, `agents.lock` pins each to a full commit, and `.agents/` holds the installed copies. It projects them to hosts (here claude, codex, cursor) through symlinks and generated manifests. Other projects share the name (dotagents.io, dotagentsprotocol.com); they are not what this repo targets.

## Verified (real runs)

| Step | Result |
| --- | --- |
| `init --agents claude,codex,cursor` | Created `agents.toml`, `.agents/skills/`, and a `.claude/skills` symlink |
| `add Tooensure-LLC/pmcro --ref <branch> --all` | Discovered all 3 plugins (`pmcro-core`, `pmcro-csuite`, `pmcro-dotnet`) straight from `plugins/*/plugin.json`; wrote a `[[plugins]]` entry each with `path` and `ref` |
| `agents.lock` | Each plugin locked to `resolved_commit` (full 40 characters) |
| Installed layout | `.agents/plugins/<name>/skills/...` with all skills present, including `trail-player` and `mcp-local-models` |
| `doctor` | All checks passed, exit 0 |

Re-run it any time: `python tools/dotagents_smoke.py --ref <ref>` (needs network and `npx`; no model calls).

## Consumer config (what a PMCR-O assistant's `agents.toml` looks like)

```toml
version = 1
agents = ["claude", "codex", "cursor"]

[[plugins]]
name = "pmcro-core"
source = "Tooensure-LLC/pmcro"
ref = "main"            # use a tag or commit once merged; a branch moves
path = "plugins/pmcro-core"
```

Add `pmcro-csuite`, `pmcro-dotnet` the same way. This file was produced by the tool, not hand-written.

## Not verified

- dotagents with the pinned **dotnet/skills** plugins: not run. It reads plugin folders directly, so our `git-subdir` marketplace entries (ADR 0004) do not apply to it; add `dotnet/skills` as its own source instead.
- Any host actually loading the projected files (Claude Code, Codex, Cursor): only the files' existence and `doctor` were checked.
- MCP and hook projection (`dotagents mcp`, per-host hooks): not exercised.
- The tested ref is a branch, which moves; lock to a commit or tag for real use.
- A `.pmcro/` or `models.json` convention (the separate aj47 ".agents Protocol") is not used.

## Open for the assistant build

Whether the assistant reads `agents.toml` itself or shells out to dotagents; where per-seat `agents.toml` files live; how `AGENTS.md` and trail tiers interact (private entries must never be projected to hosts).
