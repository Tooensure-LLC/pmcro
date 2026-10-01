---
name: platform-api-mcp
description: "Generate a .NET MCP server that wraps a third-party HTTP API (Facebook-style social APIs, marketplaces, any REST API) from a small JSON spec, with credentials injected at call time and writes off by default. Use when the user wants to connect an agent to a platform's API, wrap an API as an MCP server, or give a role a short list of platform tools."
license: MIT
---

# Platform API as an MCP server

An MCP server over a platform API is a tool, not an agent: it does the same fixed thing every call and decides nothing. The agent (or workflow) decides when to call it. This skill generates that tool layer so a small model only sees a few named operations.

## Do this

1. If the platform publishes an OpenAPI document, convert it: `python scripts/openapi_to_spec.py --openapi API.json --name Acme.Mcp.Shop --platform "Acme Shop" --base-url-env ACME_BASE_URL --token-env ACME_TOKEN --out spec.json` (read-only by default; `--include-writes` keeps the rest, marked as writes; `--tag` narrows to 30 operations). Otherwise write a spec like `assets/examples/example-api.json` by hand from the platform's own documentation, never from memory. `assets/examples/example-openapi.json` shows the input shape.
2. Run `python scripts/generate_platform_mcp.py --spec SPEC.json --out DIR`. It refuses a bad spec and prints why.
3. Build with `dotnet build`, set the two environment variables, and run it. Writes stay refused until `Platform__AllowWrites=true` is set for that run.
4. Give each role only the operations it needs through the allow-list in `mcp-local-models`.

## Never

- Never put a token in the spec, the repo, a trail or chat. The server reads it from the environment at call time.
- Never mark a POST, PUT, PATCH or DELETE as read-only: the generator refuses it.
- Never use it to get around a platform's rules. Check the platform's API terms first; some APIs forbid whole classes of action (for example automated bidding).

## Output contract

`generated NAME -> DIR` or `refused: ...` with exit 1. The output is a Web project with `Configuration/PlatformClient.cs` (the only code that calls the platform), `Tools/PlatformTools.cs` (one MCP tool per operation) and a copy of the spec. Design notes and what is not covered are in `references/design.md`.
