# 0015: The Figma plugin factory composes with Figma's MCP, it does not proxy it

Status: accepted (candidate) · 2026-10-01 (owner idea: template Figma plugins, then an MCP server others build Figma plugins through)

## Context
Figma's own MCP already creates and updates "generative plugins" (only `code.ts` and `ui.html` are replaceable) and serves its authoring skill over `skill://` resources. It authenticates each user with their own Figma account and plan.

## Decision
The company's server offers what Figma's does not: vetted templates, a deterministic linter that mechanizes Figma's pre-build checklist, escaped parameter rendering, and a human-approval step. It holds no Figma credentials and never calls Figma. The user's own agent sends the rendered files to Figma's MCP. Templates and linting are credential-free, stateless and work offline.

## Consequences
No user tokens to protect or leak. The factory cannot prove a plugin works in Figma, so every output says "rendered and linted only". Figma's rules can change; the reference records the date they were read. A public service for other people also needs abuse limits, licensing and support decisions (OPEN).
