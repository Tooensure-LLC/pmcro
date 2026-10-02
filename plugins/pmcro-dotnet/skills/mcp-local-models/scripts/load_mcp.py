#!/usr/bin/env python3
"""Check an MCP server config and build MAF tools for a role.

  python load_mcp.py <config.json> --check
  python load_mcp.py <config.json> --role checker --list
Library: build_tools(config, role) -> list of MAF MCP tools (not yet connected).
"""
import argparse, asyncio, json, os, re, sys
from urllib.parse import urlparse

SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_\w{20,}|AKIA[0-9A-Z]{16}|Bearer\s+\S{12,}")
LOOPBACK = {"localhost", "127.0.0.1", "::1"}
ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")


def check(config):
    errors = []
    for name, s in config.get("servers", {}).items():
        if SECRET.search(json.dumps(s)):
            errors.append(f"{name}: credential-shaped text; pass an environment variable name instead")
        t = s.get("transport")
        if t == "http":
            u = urlparse(s.get("url", ""))
            if u.scheme != "https" and u.hostname not in LOOPBACK:
                errors.append(f"{name}: non-loopback url must use https")
        elif t == "stdio":
            if not s.get("command"):
                errors.append(f"{name}: stdio server needs a command")
        else:
            errors.append(f"{name}: transport must be http or stdio")
        for h, var in (s.get("headers_from_env") or {}).items():
            if not ENV_NAME.match(str(var)):
                errors.append(f"{name}: headers_from_env.{h} must be an environment variable NAME")
        if not s.get("roles"):
            errors.append(f"{name}: no roles listed; a server nobody may use should be removed")
        for role, r in (s.get("roles") or {}).items():
            if "allowed_tools" not in r:
                errors.append(f"{name}: role {role} needs allowed_tools (use [] for none)")
            if r.get("approval", "always_require") not in ("always_require", "never_require"):
                errors.append(f"{name}: role {role} approval must be always_require or never_require")
    return errors


def build_tools(config, role):
    from agent_framework import MCPStdioTool, MCPStreamableHTTPTool
    tools = []
    for name, s in config["servers"].items():
        r = (s.get("roles") or {}).get(role)
        if r is None or not r["allowed_tools"]:
            continue  # no access, or an empty list means no tools: skip the server entirely
        common = dict(allowed_tools=r["allowed_tools"], approval_mode=r.get("approval", "always_require"))
        if s["transport"] == "stdio":
            env = {k: os.environ[k] for k in s.get("env_from_env", []) if k in os.environ}
            tools.append(MCPStdioTool(name, s["command"], args=s.get("args", []), env=env or None, **common))
        else:
            headers = {h: os.environ[v] for h, v in (s.get("headers_from_env") or {}).items() if v in os.environ}
            tools.append(MCPStreamableHTTPTool(name, s["url"], static_headers=headers or None, **common))
    return tools


async def _list(config, role):
    n = 0
    for tool in build_tools(config, role):
        async with tool:
            for f in tool.functions:
                print(f"{tool.name}.{f.name} [{getattr(f, 'approval_mode', None)}]")
                n += 1
    print(f"{n} tools for role {role}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("config"); a.add_argument("--check", action="store_true")
    a.add_argument("--role"); a.add_argument("--list", action="store_true")
    a = a.parse_args()
    cfg = json.load(open(a.config))
    errs = check(cfg)
    if a.check or errs:
        for e in errs:
            print("ERROR", e)
        if errs:
            sys.exit(1)
        print(f"ok: {len(cfg.get('servers', {}))} servers")
    if a.list:
        if not a.role:
            sys.exit("--list needs --role")
        asyncio.run(_list(cfg, a.role))
