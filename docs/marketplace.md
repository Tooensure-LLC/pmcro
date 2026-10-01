# Marketplace and CI

Status: CANDIDATE. Built 2026-10-01; no independent Checker has run.

## How it is put together

- **Source of truth:** `plugins/<name>/plugin.json` (Agent Plugins 1.0.0: `$schema`, `name`, explicit semver `version`) and `skills/`.
- **Generated adapters:** `python tools/pmcro.py gen` writes the Claude, Cursor, Codex and Copilot marketplace files and per-plugin manifests. CI fails if they drift. The Claude manifest omits `$schema` because Claude strips unknown keys with a warning.
- **Same shape as** [dotnet/skills](https://github.com/dotnet/skills): one folder per plugin, identical per-host manifests, marketplace file per host.
- **Marketplace name** `pmcro-plugins`. The validator rejects names containing claude, anthropic, grok, copilot, codex or agent-skills.

## Adding a plugin

`python tools/pmcro.py new-plugin pmcro-NAME --description "..." --skill SKILL --skill-description "..."` scaffolds `plugins/pmcro-NAME/` with `plugin.json`, `README.md`, `CHANGELOG.md` and one skill in the strict layout, then regenerates the adapters. The skill body is full of `TODO` markers on purpose: fill them, update the README Status with what was and was not verified, then run `validate`. The idea came from the simulated session in ADR 0013 (a `new-pmcro-plugin` scaffolder); this version is real and tested.

## Reusing dotnet/skills (pinned upstream)

`upstream.json` lists plugins we reuse from [dotnet/skills](https://github.com/dotnet/skills) (MIT) instead of copying them: MAUI, AI, MSBuild (with its binlog MCP server), test, ASP.NET Core, Blazor, data, NuGet, upgrade, diagnostics, template engine and .NET 11. `gen` writes each as a `git-subdir` entry pinned to a full 40-character commit (`973cffb`, 2026-10-01), so installs never move until we change the pin.

- **Install:** `/plugin install dotnet-maui@pmcro-plugins`. Install only what a seat needs; every installed skill adds to the model's menu.
- **Update:** change `sha` in `upstream.json`, run `python tools/pmcro.py gen`, review upstream's diff, push.
- **Rules (enforced):** sha must be a full lowercase commit, names must not clash with local plugins, paths must stay inside the repo.
- **Format:** `git-subdir` with `url`, `path` and `sha` is documented in Claude Code's marketplace reference. Only `.claude-plugin/marketplace.json` carries these entries; Cursor, Copilot and Codex support for object sources is unverified, so those files list local plugins only. Copilot users can add dotnet/skills directly.
- **Not verified here:** an actual install of a pinned entry (needs the `claude` CLI and network to GitHub).

## CI (no model spend)

`.github/workflows/ci.yml` runs the validator, the unit tests and a MAF reachability check on every push and pull request. It uses no secrets and calls no model, so it costs nothing in Grok or any other credits. Actions are pinned by tag (`@v4`, `@v5`), not by commit SHA; pin by SHA before treating CI as supply-chain safe.

## Why skills are built for local models

MAF discloses a skill in steps: name and description, then body (`load_skill`), then files (`read_skill_resource`), then scripts (`run_skill_script`). A small local model only has to hold one step at a time. So: short `SKILL.md`, detail in `references/`, exact work in `scripts/`, templates in `assets/`. The `maf-local-skills` skill and `tests/test_pmcro.py` check that every file is reachable.

## Not built yet (OPEN or needs tools this workspace lacks)

| Item | Why not |
| --- | --- |
| LLM evals (does a skill beat the no-skill baseline) | dotnet/skills uses `eval.yaml` graders; ours would need a model. Proposed: a manual `workflow_dispatch` job using a Grok key stored as a repository secret, or a local Ollama model. You add the secret; I never see it. |
| `dotagents` host loading and MCP/hook projection | install, lock and `doctor` are verified (see `docs/dotagents.md`); a host actually loading the result is not. |
| Signing and provenance (cosign or Ed25519) | Phase 6 of the plan. |
| `claude plugin validate`, .NET compile | CLI and SDK not available in this workspace. |
| Codex marketplace format | Generated copy follows the Claude shape; Codex's own layout is from secondary sources. |
| Publisher identity, pricing, ranking, version semantics | Human-owned and OPEN. |
