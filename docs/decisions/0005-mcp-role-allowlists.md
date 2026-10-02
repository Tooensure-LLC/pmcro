# 0005: MCP access is per role, by allow-list

Status: accepted (candidate) · 2026-10-01

## Context
Small local models cope badly with many tools, and a Checker must never write.

## Decision
Each role names its MCP tools in a config (`allowed_tools`, approval default `always_require`). MAF's `allowed_tools` hides every other tool from the model. Secrets are environment variable names only; plain `http` to a non-loopback host is rejected.

## Consequences
Tested over stdio with a fixture server: the Checker sees only the read tool. GitHub MCP tool names, a live Ollama model and the .NET path are untested.
