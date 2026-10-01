# 0026: Platform APIs become MCP tools, generated from a spec

Date: 2026-10-01. Status: built, CI-tested against a fake API; owner direction ("build our own API, then wrap it as an MCP server").

## Context

The owner wants the company to reach third-party platforms (social networks, marketplaces) through APIs it controls, exposed to agents as MCP servers, the way an MCP server wraps Playwright elsewhere in their work. The owner also clarified that such a wrapper is a workflow or tool, not an agent: it does a fixed thing, and guarantees (a Trail frame written every time) belong to workflow code, not to a model's choice.

## Decision

Add `platform-api-mcp` to `pmcro-mcpserver`: a generator that turns a small JSON spec (platform, two environment variable names, operations) into a .NET MCP server. The generated server is a tool layer only. It injects the token from the environment at call time, refuses every non-GET operation unless `Platform__AllowWrites=true`, requires https, and cannot leave the configured host. CI job `platform-mcp` builds the example and exercises it against a fake API.

## Consequences

- A new platform costs one spec file, and endpoints in it must come from that platform's own documentation (unverified here).
- Whether a platform allows the use at all is checked first (for example Upwork's API does not allow submitting proposals).
- Which workflow calls the tool, and which agent decides to, is decided elsewhere; see the macro and micro workflow note in `docs/product/company-model.md`.
