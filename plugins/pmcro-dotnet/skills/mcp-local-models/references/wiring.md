# Wiring MCP into MAF

Status: Python rows tested against `agent-framework` 1.19.0 and `agent-framework-ollama` 1.0.0b260813 on 2026-10-01 (stdio fixture only; no live Ollama). .NET and GitHub rows are from docs and NOT run here.

## Python (tested)

```python
from agent_framework import MCPStdioTool, MCPStreamableHTTPTool
from agent_framework_ollama import OllamaChatClient

tool = MCPStdioTool("echo", "python", args=["server.py"],
                    allowed_tools=["read_note"],        # others are hidden from the model
                    approval_mode="always_require")      # human approves each call
agent = OllamaChatClient(host="http://localhost:11434", model="llama3.1").as_agent(
    name="maker", instructions="...", tools=[tool])
async with tool:          # connects, loads tools
    ...
```

- `MCPStreamableHTTPTool(name, url, static_headers=..., header_provider=...)` is the remote form. Build headers from environment variables at connect time; never store them.
- Other options on both: `tool_name_prefix`, `use_progressive_disclosure`, `always_load`, `request_timeout`.
- Pick an Ollama model that supports tool calling; tool use quality varies a lot by model and is not verified here.

## .NET (unverified)

Microsoft Learn: Agent Framework works with the official MCP C# SDK (`ModelContextProtocol` NuGet). Create a client, list the server's tools, convert each to an `AIFunction`, and give them to the agent; `Microsoft.Extensions.AI` wraps an `IChatClient` (for Ollama, OllamaSharp) with `FunctionInvokingChatClient` for automatic calls. An agent can also be exposed as an MCP server with `.AsAIFunction()` and an `McpServerTool`. Check names with `dotnet build` before relying on them.

## Servers worth wiring

| Server | Transport | Notes |
| --- | --- | --- |
| MSBuild binlog (`Microsoft.AITools.BinlogMcp`, run as `dotnet dnx Microsoft.AITools.BinlogMcp --yes --prerelease`) | stdio | Declared in dotnet/skills `dotnet-msbuild`. Read-only build analysis suits the Checker. Prerelease. |
| GitHub MCP | remote HTTP or local | Needs a token: pass the variable name only. Allow read tools (get, list, search) for Checker and Reflector; allow write tools (create PR, push) for the Maker only and always with approval. Confirm the tool names by listing them first; they are not verified here. |
| Filesystem, terminal | stdio | Treat as write-capable. Maker only. |

## Security

MCP tool results are untrusted data: never let a tool result change a role's allow-list or approvals. MAF's docs advise logging what is sent to remote servers and preferring servers run by the service provider over proxies. MCP Sampling and Roots are deprecated in spec 2026-07-28; do not depend on them.
