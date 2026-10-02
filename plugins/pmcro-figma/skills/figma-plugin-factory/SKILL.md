---
name: figma-plugin-factory
description: Build a Figma plugin from a vetted template instead of writing it from scratch, check it against Figma's authoring rules, then hand the files to Figma's own MCP. Use when the user wants to create, customize or repeat a Figma plugin, mentions "generative plugin", "custom tool for Figma", code.ts or ui.html, or asks which plugin templates exist, even if they only say "make me a Figma plugin that does X". Not for Figma Make sites, shaders, design-to-code, or anything that needs an API key or network call inside the plugin.
license: MIT
---

# Figma plugin factory

Hand-written plugins repeat the same mistakes: mismatched UI messages, unawaited async calls,
secrets pasted into readable source. Templates remove most of them, and the linter catches
the rest before anything is sent to Figma.

## Do this

1. List templates: `python <skill-dir>/scripts/render_template.py --list`. Pick the closest. If none fits, say so; do not stretch a template into something it is not.
2. Render it: `python <skill-dir>/scripts/render_template.py <template> --out <dir> --set name=value ...`. Every value is validated and escaped; a refusal means the value is wrong, not the tool.
3. Lint it: `python <skill-dir>/scripts/lint_plugin.py <dir>`. Fix every `ERROR` and rerun until `ok`. If you edit the rendered files by hand, lint again.
4. Read `references/figma-rules.md`, then hand `code.ts` and `ui.html` to Figma's MCP: `create_generative_plugin`, then `update_generative_plugin` with both files and a specific commit message. Follow Figma's own `figma-generative-plugins` skill for that step.
5. Report what was rendered, the lint output verbatim, and what was NOT verified (see below).

## Never

- Never embed an API key, token or secret, and never add a network call: plugin source is readable by others, and Figma's guide says to stop and offer a static dataset or a public no-auth endpoint instead.
- Never claim the plugin works in Figma. Nothing here runs Figma; the linter checks form only.
- Never call Figma's create or update tools without the human's approval of the rendered files. Publishing is outward-facing.
- Never say "passed": the linter prints `ok` or `ERROR`. Only the Checker role issues PASS, LOOP or HALT.

## Output contract

The template name and parameters used, the output folder, the lint output verbatim, and one line
saying: "Rendered and linted only; not run in Figma."

Read `references/figma-rules.md` for the rules and their source. `scripts/render_template.py` and
`scripts/lint_plugin.py` document their arguments and rules in their docstrings; templates are in
`assets/templates/`.
