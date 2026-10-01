"""End-to-end smoke test of the generated .NET MCP skills server (run by CI; needs network to localhost only).

  python tests/smoke_dotnet_server.py http://127.0.0.1:5099/mcp <expected-skill-count-at-least>
Connects with the Python MCP client over Streamable HTTP, lists and reads skill resources, then checks that
scripts and path traversal are refused and that MAF's own MCPSkillsSource can discover the skills.
Exit 0 and "ok: ..." lines on success; an assertion error otherwise. Not collected by unittest discovery.
"""
import asyncio, json, sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(url, at_least):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("ok: initialized")
            index = json.loads((await session.read_resource("skill://index.json")).contents[0].text)
            names = {s["name"] for s in index["skills"]}
            assert len(names) >= at_least, f"only {len(names)} skills in the index"
            assert all(s["type"] == "skill-md" and s["url"] == f"skill://{s['name']}/SKILL.md" for s in index["skills"])
            print(f"ok: index lists {len(names)} skills")
            body = (await session.read_resource("skill://shared-memory/SKILL.md")).contents[0].text
            assert "name: shared-memory" in body
            print("ok: read a SKILL.md")
            ref = (await session.read_resource("skill://shared-memory/references/viewers.md")).contents[0].text
            assert "Viewers and tiers" in ref
            print("ok: read a reference file")
            for bad in ("skill://shared-memory/scripts/memory.py", "skill://shared-memory/references/..%2fSKILL.md", "skill://nope/SKILL.md"):
                try:
                    await session.read_resource(bad)
                except Exception:
                    continue
                raise AssertionError(f"server served {bad}")
            print("ok: scripts, encoded traversal and unknown skills are refused")
            from agent_framework import MCPSkillsSource, SkillsSourceContext
            skills = await MCPSkillsSource(client=session).get_skills(SkillsSourceContext(None))
            assert {s.frontmatter.name for s in skills} == names, "MAF did not discover the same skills"
            print(f"ok: MAF MCPSkillsSource discovered {len(skills)} skills from the .NET server")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], int(sys.argv[2])))
