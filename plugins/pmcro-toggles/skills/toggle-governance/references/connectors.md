# Connectors

Only real servers are listed, and none is wired into this plugin, because each needs an account and a credential.

| Service | What exists | Status here |
| --- | --- | --- |
| LaunchDarkly | A hosted MCP server documented at launchdarkly.com/docs/home/getting-started/mcp (flags, AI configs, observability; it mentions a flag removal readiness tool). A local server exists for federal and EU environments. | Not tested. Connecting it is the founder's decision: it needs a LaunchDarkly account and token, and any tool that changes a live flag must require approval. |
| OpenFeature CLI | A command-line tool (not an MCP server) that validates `flags.json` and generates typed flag accessors. | Compatible: this skill writes the manifest in its format. Not run here. |

If a connector is added later: give the Checker read-only tools only, keep tokens out of the repository (environment or the host's secret store), and record the tool list it was tested with.
