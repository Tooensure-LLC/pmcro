---
name: maf-local-skills
description: Wire Agent Skills into Microsoft Agent Framework (MAF) so a small or local model gets them by progressive disclosure, and check that they load. Use when the user wants PMCR-O skills to run under MAF in Python or .NET, asks why a local model (Ollama, llama.cpp) ignores or misuses a skill, wants a skill's references, scripts or assets to load on demand, or needs the script allow-list and approval settings for a SkillsProvider or AgentSkillsProvider. Not for authoring a new skill (use skill-creator) or for Claude Code plugin packaging.
license: MIT
---

# MAF progressive disclosure for local models

A local model has a small context and follows long instructions poorly. MAF avoids that by
revealing a skill in three steps: it advertises only each skill's name and description, loads the
body when the model calls `load_skill`, and reads files from `references/` and `assets/` only when
the model calls `read_skill_resource`. Scripts run only through `run_skill_script`. So the way to
help a small model is to keep `SKILL.md` short and push detail into files it fetches on demand.

## Do this

1. Keep `SKILL.md` under 150 lines for local models (the hard limit is 500). Put the common path in the body and rare or large detail in `references/<topic>.md`, one level deep, each linked from the body with a line saying when to read it.
2. Put anything deterministic in `scripts/*.py`. Scripts are the only way a small model gets exact output (a number, a path, a verdict) without generating it. Document each script's arguments and its one-line output contract in the body.
3. Put templates and fixtures in `assets/`. MAF reads `.md .json .yaml .yml .csv .xml .txt` resources by default, so keep assets in those formats.
4. Load with the Python snippet in `scripts/list_skills.py` to confirm what the model will see: names, descriptions, resources and scripts. If a resource or script is missing from that list, the model cannot reach it.
5. Leave approvals on. In `SkillsProvider.from_paths` the three `disable_*_approval` flags default to `False`; do not set them. Pass a `script_filter` that allows only the scripts you listed.
6. Verify, do not assume: run `python scripts/list_skills.py <plugin>/skills` after every change and read its output.

## Never

- Never give a Checker-role agent a write tool or `run_skill_script` for scripts that write. Enforce it in middleware, not in the prompt (details in `references/maf-api.md`).
- Never rely on the sample subprocess script runners as a sandbox; MAF's docs call them demonstration only.
- Never claim the .NET wiring compiles unless you built it. The Python path is tested against `agent-framework` 1.19.0; the .NET path in `references/maf-api.md` is unverified.

## Output contract

Report the exact `list_skills.py` output, then one line per problem found (skill, what is
unreachable, fix). If nothing is wrong, say "all skills reachable" and list the counts.

Read `references/maf-api.md` for API names, the allow-list pattern and the .NET equivalents.
Use `assets/script-allowlist.example.json` as the starting allow-list.
