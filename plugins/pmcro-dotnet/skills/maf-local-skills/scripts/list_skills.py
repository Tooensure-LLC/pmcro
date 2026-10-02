#!/usr/bin/env python3
"""List what a model would see from a skills directory under MAF.

Usage: python list_skills.py <skills-dir>
Output: one line per skill: name | description length | resources | scripts
Exit 1 if a skill fails to load or the directory has no skills.
"""
import asyncio, sys
from agent_framework import FileSkillsSource, SkillsSourceContext


# agent-framework 1.19.0 exposes no public list of a skill's files, so this reads the
# private _resources/_scripts attributes. Re-check after upgrading the package.
def names(items):
    return sorted(getattr(i, "name", str(i)) for i in (items or []))


async def main(path):
    ctx = SkillsSourceContext(None)  # no agent needed just to enumerate
    skills = await FileSkillsSource(path).get_skills(ctx)
    if not skills:
        print(f"no skills found under {path}")
        return 1
    for s in sorted(skills, key=lambda k: k.frontmatter.name):
        fm = s.frontmatter
        print(f"{fm.name} | desc {len(fm.description)} chars | "
              f"resources {names(getattr(s, '_resources', None))} | "
              f"scripts {names(getattr(s, '_scripts', None))}")
    print(f"{len(skills)} skills reachable")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(asyncio.run(main(sys.argv[1])))
