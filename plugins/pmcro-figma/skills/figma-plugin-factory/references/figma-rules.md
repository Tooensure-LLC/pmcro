# Figma generative plugin rules

Status: read on 2026-10-01 from Figma's MCP server resources `skill://figma/figma-generative-plugins/SKILL.md` and `.../references/authoring.md`. Figma may change them; re-read before relying on this. Nothing here was run inside Figma.

## The surface

- Figma's MCP can create a plugin (`create_generative_plugin`, which makes a square-drawing scaffold) and update it (`update_generative_plugin`). An update can replace only the existing `code.ts` and `ui.html`; it cannot change `manifest.json`, add files, add dependencies or take a diff. It requires a commit message and returns build errors.
- Every plugin needs functional UI with a clear primary action. Use Figma's `fig-*` controls inside `<fig-content>` and `<fig-footer>`.
- `code.ts` owns `figma.*`; `ui.html` owns the DOM; they talk only by messages.

## What the linter checks (and the guide's reason)

| Rule | Reason |
| --- | --- |
| F001, F002 | the update contract keeps `figma.showUI(__html__, ...)` and the UI structure |
| F003, F004 | source is readable by others; no secrets, no authenticated calls |
| F005, F012 | no eval, no type bypass |
| F006, F007, F008 | dynamic-page access: async getters and setters; promises handled |
| F009 | UI and sandbox message types must agree exactly |
| F010 | every plugin must be re-runnable (relaunch data) |
| F011 | fonts must be loaded before text changes |

## What it cannot check

Whether the layers come out right, bounded work, geometry and placement, fonts that are missing, selection edge cases, wording of status text. Those need a human trying the plugin in Figma, which the completion step in Figma's guide makes easy (it gives a link that opens a new file with the unpublished plugin).

## Templates

Each template is `template.json` (typed parameters with limits), `code.ts.tmpl` and `ui.html.tmpl`. Add one with the same shape and a test; limits in `template.json` must match the clamps in the template's `code.ts`.
