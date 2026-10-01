---
name: find-skill
description: "Look for an existing skill before making a new one. Use before creating, copying or rewriting any skill, when the user asks whether a skill for something already exists, or says reuse before build; it searches this repository's skills and lists the other places to check (dotnet/skills, the Agent Skills docs server, MCP)."
license: MIT
---

# find-skill

Never reinvent the wheel: before a skill is made, check whether one already does the job. This is the first half of the workflow whose second half is `new-skill`.

## Do this

1. Run `python scripts/find_skill.py WORD [WORD ...]` with the nouns and verbs of the job (try synonyms). It scores this repository's skills by name, description and body.
2. If a good match exists, use or extend it. Extending is a plugin version bump and a CHANGELOG entry, not a new skill.
3. If nothing matches, check the other sources listed in `references/sources.md`, and write what you checked in the new skill's README under a "Prior art" heading.
4. Only then hand over to `new-skill`.

## Never

- Never copy another project's skill text into this repository: pin it as a reference with its licence instead.
- Never conclude "nothing exists" from one search word: say which words you tried.

## Output contract

The script prints ranked matches or `no match: ...` (exit 1). Your report names the matches considered, the sources checked and the decision: reuse, extend or create.
