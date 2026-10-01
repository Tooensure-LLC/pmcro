---
name: create-skill
description: Create a new Agent Skill (a folder with a SKILL.md plus optional references/, scripts/, assets/) for any domain. Use whenever the user wants to make, scaffold, draft, or turn a workflow into a skill, even if they only say "make this repeatable" or "package this as a skill". Not for editing an existing skill's evals or benchmarking it.
---

# create-skill

Produce a small, well-scoped Agent Skill that a future Claude can load and follow without extra context.

## Workflow

1. **Capture intent.** Establish four things, inferring from the conversation before asking anything:
   - What task the skill enables
   - What user requests should trigger it
   - What the output looks like
   - What the skill must *not* cover
2. **Choose a name.** Lowercase kebab-case, specific, under 64 characters.
3. **Write the description first.** It is the only text always in context, so it decides whether the skill ever triggers. State what the skill does and when to use it, and err toward slightly pushy phrasing, because skills tend to under-trigger. No angle brackets, 1024 characters max.
4. **Start from `assets/SKILL.template.md`** and fill in the body.
5. **Split content by when it is needed** (see below).
6. **Validate** with `python scripts/validate_skill.py <skill-dir>` and fix every error.
7. **Report** the structure, and any assumptions made.

## Keeping SKILL.md lean

SKILL.md loads in full every time the skill triggers, so it should hold only what is needed on every run: the workflow, key decisions, and pointers to deeper material. Aim for well under 500 lines. Write in the imperative and explain *why* a rule matters rather than shouting it; a model that understands the reason generalizes better than one following a bare command.

## Progressive disclosure

Content loads in three levels. Place each piece at the cheapest level that still works:

| Level | Loaded | Holds |
|---|---|---|
| Metadata | Always | `name`, `description` |
| SKILL.md body | When the skill triggers | Core workflow and pointers |
| Bundled files | Only when read or run | Everything else |

Every bundled file must be linked from SKILL.md with a note on *when* to open it. An unreferenced file will never be found.

## Bundled directories (create only if needed)

- **`references/`**: detailed knowledge read on demand: specs, domain rules, long examples. Split by variant or topic so only the relevant file is read. Add a table of contents to any file over about 300 lines.
- **`scripts/`**: code for steps that must be exact or repeat identically, such as validation, conversion, or scaffolding. Scripts run without being read into context. Prefer them over prose when the same code would otherwise be rewritten each time.
- **`assets/`**: files used in the output rather than read for guidance: templates, boilerplate, images, fonts.

If a skill needs none of these, ship SKILL.md alone. An empty directory is clutter.

For frontmatter fields, structure rules, and a description-writing checklist, read `references/skill-format.md`.

## Boundaries

Keep the skill generic to its domain. Do not invent plugin, marketplace, or repository formats around it: a skill is just a folder with one SKILL.md. Never include malicious or misleading content; a skill's behavior should match what its description says.
