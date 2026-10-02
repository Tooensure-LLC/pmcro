#!/usr/bin/env python3
"""Search the skills in this repository's plugins by keyword, so a new skill is only made when no existing one fits.

  python find_skill.py WORD [WORD ...] [--plugins-dir plugins] [--limit 8]
Scores every skills/*/SKILL.md by how many of the words appear in its name (3 points), description (2) and body (1), and prints the best
matches as "score  plugin/skill  description". Matching is plain text, not meaning: try synonyms. It reads only this repository's
plugins; it does not look at dotnet/skills, the Agent Skills docs or any MCP server (the skill's steps say when to check those).
Output: matches, or "no match: ..." (exit 1) when nothing scores, which is the signal that creating a new skill may be right.
"""
import argparse, pathlib, re, sys


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        if k and not line.startswith(" "):
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, m.group(2)


def search(plugins_dir, words, limit=8):
    words = [w.lower() for w in words if w.strip()]
    rows = []
    for f in sorted(pathlib.Path(plugins_dir).glob("*/skills/*/SKILL.md")):
        meta, body = frontmatter(f.read_text())
        name, desc = meta.get("name", f.parent.name).lower(), meta.get("description", "").lower()
        body = body.lower()
        score = sum(3 * (w in name) + 2 * (w in desc) + (w in body) for w in words)
        if score:
            rows.append((score, f"{f.parent.parent.parent.name}/{f.parent.name}", meta.get("description", "")))
    rows.sort(key=lambda r: (-r[0], r[1]))
    return rows[:limit]


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("words", nargs="+"); p.add_argument("--plugins-dir", default="plugins"); p.add_argument("--limit", type=int, default=8)
    a = p.parse_args(argv)
    rows = search(a.plugins_dir, a.words, a.limit)
    if not rows:
        print("no match: nothing here covers those words; check the other sources in the skill, then a new skill may be right")
        return 1
    for score, ref, desc in rows:
        print(f"{score:3d}  {ref}  {desc[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
