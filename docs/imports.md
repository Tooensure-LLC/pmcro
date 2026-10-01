# Imports from older repos

Status: CANDIDATE. Imported 2026-10-01 with `tools/import_skills.py`; bodies are byte-identical to the source.

| Source | Visibility | Imported | Not imported |
| --- | --- | --- | --- |
| ShawnDelaineBellazanLoop/PMCR-O-Marketplace @ a25f7f0 | public | `pmcro-csuite`: ceo, cfo, chief-of-staff, chro, clo, cmo, coo, cro, cto | `pmcro-engine` and `pmcro-specialty` (see below) |
| Tooensure-LLC/ProjectName @ 1a003e9 | **private** | nothing | everything; this repo is public, so copying needs an explicit decision |

## Changes made on import

- Frontmatter only: BOM removed; `version` moved into `metadata` (it is not an Agent Skills key); `metadata.imported_from` added; per-skill `.claude-plugin/` manifests skipped.
- `ceo/SKILL.md`: removed one bullet linking `references/okr-methodology.md`. The file does not exist in the source either.

## Defects found in the source (not fixed)

1. All 9 C-Suite skills link to `../../../pmcro-engine/skills/orchestrator/references/pattern-d-macro-loop.md`. A plugin installed on its own cannot resolve that path. Fix by bundling the file or rewriting the pointer. The validator prints a WARN for each.
2. In the unimported `pmcro-engine` and `pmcro-specialty`, MAF 1.19.0 silently skips 6 of 31 skills (missing frontmatter, or a `metadata` value that is not a string, such as `mcp_primitives`).
3. The C-Suite here has 9 seats; ProjectName's seat bot reads 15 Chiefs from a private company repo. Reconcile before generating seat bots.
