# Repository instructions

PMCR-O plugins live under `plugins/<name>/`. `plugin.json` and `skills/*/SKILL.md` are the source
of truth; everything else (`.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`,
`.github/plugin/`, `.agents/plugins/`) is generated. Never hand-edit generated files.

## New plugins

To add a skill to an existing plugin, use the `new-skill` skill (`plugins/pmcro-core/skills/new-skill/scripts/scaffold_skill.py`); its `assets/templates/` is the single template for the shape of every skill. To make a new plugin, start with `python tools/pmcro.py new-plugin pmcro-NAME --description "..."`; it creates a plugin that already satisfies every rule and uses the same template for its first skill. Fill every `TODO` before you commit. Every new skill starts with all three optional folders (`references/design.md`, `scripts/run.py`, `assets/templates/output.md.tmpl`) so the flow is templated and a small model does not have to guess; `validate` warns about prose-only skills.

## Before you push

```
python tools/pmcro.py gen        # after changing any plugin.json
python tools/pmcro.py validate   # must exit 0
python -m unittest discover -s tests
```

CI runs the same commands and makes no model calls.

## Skill rules (enforced by the validator)

- Frontmatter keys: only `name`, `description`, `license`, `compatibility`, `metadata` (string map), `allowed-tools`.
- `name` equals the directory; `description` is 1-1024 characters and says when to use the skill, in the user's words.
- `SKILL.md` under 500 lines (aim for 150 lines and about 5000 tokens so local models cope and skills stay small; `validate` warns past those targets). Detail goes in `references/` (one level deep), exact work in `scripts/`, templates in `assets/`.
- No absolute paths, symlinks or credential-shaped text.
- The role skills `orchestrate`, `plan`, `make`, `check`, `reflect` are byte-identical to the owner's skills drive. Do not edit them here.
- Marketplace and plugin names must not contain claude, anthropic, grok, copilot, codex or agent-skills.

## Documentation law (enforced; applies to agents and people equally)

Heavy documentation is mandatory, not optional. `python tools/pmcro.py validate` and CI fail when:

- a plugin has no `README.md` with `## Skills`, `## Install`, `## Status` and every skill named;
- a plugin's `CHANGELOG.md` has no `## <version>` entry for its current `plugin.json` version;
- a script has fewer than 2 docstring lines, or its skill never mentions it;
- a file under `docs/` is not linked from `docs/README.md`.

Also required, by this law though not machine-checked: record each decision as a numbered file in
`docs/decisions/`; state in the docs what was **not** tested or is unverified; change docs in the
same commit as the code they describe; bump the plugin version for any behavior change. An agent
that skips documentation has not finished the task.

## Laws that bind agents working here

Verify first. Log before act. Only the Checker issues PASS, LOOP or HALT. MaxLoops is 3.
Entries in `.trail-local/` are private: never read them into commits, summaries or training data.
