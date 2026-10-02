---
name: new-skill
description: "Create a new skill inside an existing plugin, already in the PMCR-O templated shape (SKILL.md, references/, scripts/, assets/templates/). Use when the user wants to add a skill, turn a workflow into a repeatable skill, or says 'make this a skill', for any domain. Use create-skill for the writing guidance and this one to lay the folders down."
license: MIT
---

# new-skill

A skill that makes skills: it lays down the one shape every skill here shares, so the flow is the same each time and a smaller model never has to guess where things go. The shape is defined once, in `assets/templates/`, and every other way of making a skill (including `new-plugin`) reads it from there.

## Do this

1. Run `find-skill` first (reuse before build). Then read the owner's `create-skill` for how to capture intent, choose a name and write the description, and, if the Agent Skills documentation server is connected, look up the specification and best practices there instead of recalling them. This skill only lays down the folders.
2. Run `python scripts/scaffold_skill.py --plugin PLUGIN --name SKILL-NAME --description "Use when ..."` from the repo root.
3. Fill every TODO in the new skill's files: its SKILL.md, design notes, run script, output template and input shape (the fields a request must have; the generated check accepts a request or denies it with the shape to fill in). Delete a folder only if you can say why the skill needs none of it.
4. Add a CHANGELOG entry, bump the plugin version in `plugin.json`, then run `python tools/pmcro.py gen` and `python tools/pmcro.py validate`.

## Never

- Never create a second copy of the template inside a script: change `assets/templates/` and every skill made afterwards follows.
- Never edit the role skills (`orchestrate`, `plan`, `make`, `check`, `reflect`) or `create-skill`: they are byte-identical to the owner's drive.
- Never leave a TODO in a skill you ship.

## Output contract

`created PATH; ...` or `refused: ...` (exit 1) naming the rule: missing plugin, bad name, description over 1024 characters, or the skill exists. The new skill is added to the plugin README's Skills table; the version bump is yours. Why the shape is what it is: `references/design.md`.
