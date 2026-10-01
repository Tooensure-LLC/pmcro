# Design notes

## Tool, workflow, agent

- **Tool:** one fixed operation against one platform. This skill's output.
- **Workflow:** a deterministic sequence of steps and tool calls. It can guarantee that a Trail frame is written before and after each action, because it is code, not a model's choice.
- **Agent:** a model that decides which tool to call next. It can only call what its role's allow-list shows, and what a workflow lets it.

The owner's design puts the guarantees in workflows (the Trail is written by workflow code) and the judgment in agents. A generated server sits under both.

## Rules the generated code enforces

| Rule | Where |
| --- | --- |
| Token read from an environment variable at call time, never stored or logged | `PlatformClient` |
| Non-GET operations refused unless `Platform__AllowWrites=true` | `PlatformClient`, and the generator refuses unmarked non-GET operations |
| Base URL must be https (http allowed only for localhost, for tests) | `PlatformClient` |
| Request cannot leave the configured host; `.` and `..` path parameters refused | `PlatformClient` |
| Response truncated at 8000 characters | `PlatformClient` |

## Not covered

OAuth flows and token refresh (the token is supplied from outside), paging, retries and rate-limit handling, per-operation approval prompts (the MCP client's approval mode is the right place), non-JSON bodies, and any check that a spec's endpoints match the real platform. The CI job tests the example spec against a fake API, not against any real platform.
