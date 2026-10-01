# Repository instructions

PMCR-O plugins live under `plugins/<name>/`. `plugin.json` and `skills/*/SKILL.md` are the source
of truth; everything else (`.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`,
`.github/plugin/`, `.agents/plugins/`) is generated. Never hand-edit generated files.

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
- `SKILL.md` under 500 lines (aim for 150 so local models cope). Detail goes in `references/` (one level deep), exact work in `scripts/`, templates in `assets/`.
- No absolute paths, symlinks or credential-shaped text.
- The role skills `orchestrate`, `plan`, `make`, `check`, `reflect` are byte-identical to the owner's skills drive. Do not edit them here.
- Marketplace and plugin names must not contain claude, anthropic, grok, copilot, codex or agent-skills.

## Laws that bind agents working here

Verify first. Log before act. Only the Checker issues PASS, LOOP or HALT. MaxLoops is 3.
Entries in `.trail-local/` are private: never read them into commits, summaries or training data.
