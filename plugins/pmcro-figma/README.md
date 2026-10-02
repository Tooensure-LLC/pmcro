# pmcro-figma

Template-driven Figma plugins. Render a vetted template into `code.ts` and `ui.html`, lint it against Figma's authoring rules, then hand the files to Figma's own MCP.

## Skills

| Skill | Use it to |
| --- | --- |
| `figma-plugin-factory` | List templates, render one with validated parameters (`scripts/render_template.py`), and lint the result (`scripts/lint_plugin.py`). |

## Install

```
/plugin install pmcro-figma@pmcro-plugins
```

## Status

CANDIDATE. One template (`grid-frames`). The renderer and linter are tested, including hostile parameter values. NOT verified: the rendered plugin was never run in Figma; the template's Plugin API calls come from Figma's authoring guide and my knowledge, not from a test. Figma's rules were read from its MCP on 2026-10-01 and may change. A server that exposes this factory over MCP is designed (ADR 0015, 0016) but not built here.
