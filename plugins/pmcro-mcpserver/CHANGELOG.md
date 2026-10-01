# Changelog: pmcro-mcpserver

## 0.3.0

- `platform-api-mcp`: `openapi_to_spec.py` converts an OpenAPI 3 document into a generator spec (read-only by default, writes marked, 30-operation limit with `--tag`); CI builds a server from the example OpenAPI file.

## 0.2.0

- Added `platform-api-mcp`: generator for MCP servers that wrap a third-party HTTP API from a JSON spec; CI job `platform-mcp`.

## 0.1.0

- Scaffolded with `tools/pmcro.py new-plugin`.
- Filled the scaffold: `pmcro_mcp.py` (read-only skills, memory and inbox server), `generate_dotnet_server.py` with templates, connection reference, tests (see ADR 0022).
