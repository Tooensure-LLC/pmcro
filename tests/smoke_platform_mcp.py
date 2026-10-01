"""Smoke test of a generated platform MCP server against tests/fixtures/fake_platform_api.py (run by CI).

  python tests/smoke_platform_mcp.py MCP_URL denied|allowed
Lists the tools, calls a read tool (proving the token env var reached the platform), checks that a path parameter of ".." is refused,
and checks that the write tool is refused when writes are disabled ("denied") or reaches the platform when enabled ("allowed").
Not collected by unittest discovery. Exit 0 with "ok:" lines, or an assertion error.
"""
import asyncio, json, sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(url, mode):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()
            tools = {t.name for t in (await s.list_tools()).tools}
            assert tools == {"GetThing", "ListThings", "CreateThing"}, tools
            print("ok: tools", sorted(tools))
            r = (await s.call_tool("GetThing", {"id": "abc", "fields": "x y"})).content[0].text
            assert r.startswith("status 200") and '"abc"' in r and "fields=x%20y" in r, r
            print("ok: read tool reached the platform with the injected token")
            r = (await s.call_tool("GetThing", {"id": ".."})).content[0].text
            assert r.startswith("refused"), r
            print("ok: '..' path parameter refused")
            r = (await s.call_tool("CreateThing", {"body": json.dumps({"n": 1})})).content[0].text
            if mode == "denied":
                assert r.startswith("refused: write operations are disabled"), r
                print("ok: write refused while writes are disabled")
            else:
                assert r.startswith("status 201") and '"n": 1' in r, r
                print("ok: write reached the platform when enabled")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
