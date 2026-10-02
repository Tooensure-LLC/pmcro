#!/usr/bin/env python3
"""Serve the marketplace's skills (and optionally read-only memory and inbox tools) over MCP.

  python pmcro_mcp.py [--plugins-root plugins] [--plugin NAME ...] [--repo-root .]
                      [--tools memory,inbox] [--viewer founder|seat:ID|company|public] [--tiers public,company]
                      [--http PORT] [--print-index]
Default transport is stdio, which needs no network. --http PORT serves stateless Streamable HTTP on 127.0.0.1 only
(untested here). --print-index prints skill://index.json and exits, which also works as an offline self-check.
Skills follow the SEP-2640 convention MAF reads: skill://index.json lists {name, type "skill-md", description, url};
skill://<skill>/SKILL.md returns the body; skill://<skill>/references/<file> and skill://<skill>/assets/<path> return
supporting text files. Scripts are never served or run.
Safety: read-only. Symlinks, path traversal, non-text files and files over 256 KB are refused; the plugins root may not
be inside .trail-local; duplicate skill names stop start-up. The memory and inbox tools are opt-in; the viewer is FIXED
at start-up and the caller cannot choose it, so a tier can never be widened by a request. --tiers limits which inbox
tiers the inbox tools may read and must not exceed what the viewer may see. Memory and inbox tools shell out to
the repo's own scripts with a fixed argument list.
Output: the MCP protocol on stdio; or the index JSON for --print-index. Exits 1 with "refused: ..." on a bad setup.
"""
import argparse, json, pathlib, re, subprocess, sys

TEXT_EXT = {".md", ".json", ".yaml", ".yml", ".txt", ".csv", ".xml", ".html", ".ts", ".tmpl"}
MAX_BYTES = 256 * 1024
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TIER_ORDER = {"public": 0, "company": 1, "roundtable": 2, "private": 3}
VIEWER_MAX = {"public": 0, "company": 1}


def frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text.lstrip("﻿"), re.S)
    if not m:
        return {}
    import yaml
    data = yaml.safe_load(m.group(1))
    return data if isinstance(data, dict) else {}


def has_symlink(path, stop):
    p = path
    while True:
        if p.is_symlink():
            return True
        if p == stop or p.parent == p:
            return False
        p = p.parent


class Catalog:
    def __init__(self, plugins_root, allow=None):
        self.root = pathlib.Path(plugins_root).resolve()
        if ".trail-local" in self.root.parts:
            sys.exit("refused: the plugins root may not be inside .trail-local")
        self.skills = {}
        for plug in sorted(p for p in self.root.iterdir() if (p / "plugin.json").is_file()):
            if allow and plug.name not in allow:
                continue
            for sk in sorted((plug / "skills").glob("*/SKILL.md")):
                d = sk.parent
                if has_symlink(d, self.root):
                    continue
                fm = frontmatter(sk.read_text(encoding="utf-8"))
                name = fm.get("name")
                if name != d.name or not NAME_RE.match(str(name)) or not fm.get("description"):
                    sys.exit(f"refused: {d} has invalid frontmatter (name must equal the folder, description required)")
                if name in self.skills:
                    sys.exit(f"refused: duplicate skill name {name!r} in {plug.name} and {self.skills[name]['plugin']}")
                self.skills[name] = {"plugin": plug.name, "dir": d, "description": str(fm["description"])}

    def index(self):
        return {"skills": [
            {"name": n, "type": "skill-md", "description": s["description"], "url": f"skill://{n}/SKILL.md"}
            for n, s in sorted(self.skills.items())]}

    def read(self, skill, rel):
        """Return text of SKILL.md or a file under references/ or assets/, or raise ValueError."""
        if skill not in self.skills:
            raise ValueError(f"unknown skill {skill!r}")
        base = self.skills[skill]["dir"]
        parts = pathlib.PurePosixPath(rel).parts
        if rel != "SKILL.md" and (len(parts) < 2 or parts[0] not in ("references", "assets") or ".." in parts or rel.startswith("/")):
            raise ValueError("only SKILL.md, references/* and assets/* are served")
        target = (base / rel)
        if has_symlink(target, base) or not target.is_file():
            raise ValueError("not found")
        resolved = target.resolve()
        if base.resolve() not in resolved.parents:
            raise ValueError("outside the skill folder")
        if target.suffix.lower() not in TEXT_EXT or target.stat().st_size > MAX_BYTES:
            raise ValueError("not a servable text file")
        return target.read_text(encoding="utf-8")


def run_script(repo, plugin_script, args):
    r = subprocess.run([sys.executable, str(plugin_script), *args], cwd=repo, capture_output=True, text=True, timeout=30)
    return (r.stdout + r.stderr).strip() or "(no output)"


def find_script(root, skill, name):
    for p in root.glob(f"*/skills/{skill}/scripts/{name}"):
        return p
    sys.exit(f"refused: {skill}/scripts/{name} not found under {root}")


def build_server(plugins_root="plugins", allow=None, repo_root=".", tools=(), viewer="public", tiers=()):
    from mcp.server.fastmcp import FastMCP
    cat = Catalog(plugins_root, allow)
    server = FastMCP("pmcro-skills", stateless_http=True)
    repo = pathlib.Path(repo_root).resolve()

    @server.resource("skill://index.json", mime_type="application/json")
    def index() -> str:
        return json.dumps(cat.index(), indent=2)

    def reader(skill, rel):
        try:
            return cat.read(skill, rel)
        except ValueError as e:
            raise ValueError(f"refused: {e}")

    @server.resource("skill://{skill}/SKILL.md", mime_type="text/markdown")
    def skill_md(skill: str) -> str:
        return reader(skill, "SKILL.md")

    @server.resource("skill://{skill}/{kind}/{a}")
    def res1(skill: str, kind: str, a: str) -> str:
        return reader(skill, f"{kind}/{a}")

    @server.resource("skill://{skill}/{kind}/{a}/{b}")
    def res2(skill: str, kind: str, a: str, b: str) -> str:
        return reader(skill, f"{kind}/{a}/{b}")

    @server.resource("skill://{skill}/{kind}/{a}/{b}/{c}")
    def res3(skill: str, kind: str, a: str, b: str, c: str) -> str:
        return reader(skill, f"{kind}/{a}/{b}/{c}")

    if viewer not in VIEWER_MAX and viewer != "founder" and not viewer.startswith("seat:"):
        sys.exit("refused: viewer must be founder, seat:ID, company or public")
    ceiling = 3 if viewer == "founder" else VIEWER_MAX.get(viewer, 1)  # a seat reads at most company tier through inbox
    for t in tiers:
        if t not in TIER_ORDER or TIER_ORDER[t] > ceiling:
            sys.exit(f"refused: tier {t!r} is not readable by viewer {viewer!r}")
    if "memory" in tools:
        mem = find_script(cat.root, "shared-memory", "memory.py")

        @server.tool(description=f"Search shared memory (read-only; results are filtered for viewer {viewer}). Keyword search only.")
        def memory_search(query: str, limit: int = 5) -> str:
            if not 1 <= len(query) <= 200:
                return "refused: query must be 1-200 characters"
            return run_script(repo, mem, ["search", query, "--viewer", viewer, "--limit", str(max(1, min(int(limit), 10)))])

        @server.tool(description=f"Show one memory entry by id such as M0003 (read-only; filtered for viewer {viewer}).")
        def memory_show(memory_id: str) -> str:
            if not re.fullmatch(r"[PMRV]\d{4}", memory_id):
                return "refused: id looks like M0003"
            return run_script(repo, mem, ["show", memory_id, "--viewer", viewer])
    if "inbox" in tools:
        q = find_script(cat.root, "inbox", "queue.py")
        if not tiers:
            sys.exit("refused: the inbox tools need --tiers")

        @server.tool(description="List queued inbox items (read-only) for the tiers this server was started with.")
        def inbox_list(status: str = "queued") -> str:
            if status not in ("queued", "claimed", "done", "deferred", "dropped"):
                return "refused: bad status"
            return "\n".join(run_script(repo, q, ["list", "--tier", t, "--status", status]) for t in tiers)

        @server.tool(description="Show the next queued inbox item (read-only) for the tiers this server was started with.")
        def inbox_next() -> str:
            return "\n".join(run_script(repo, q, ["next", "--tier", t]) for t in tiers)
    return server, cat


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--plugins-root", default="plugins"); a.add_argument("--plugin", action="append")
    a.add_argument("--repo-root", default="."); a.add_argument("--tools", default="")
    a.add_argument("--viewer", default="public"); a.add_argument("--tiers", default="")
    a.add_argument("--http", type=int); a.add_argument("--print-index", action="store_true")
    a = a.parse_args()
    tools = [t for t in a.tools.split(",") if t]
    tiers = [t for t in a.tiers.split(",") if t]
    unknown = set(tools) - {"memory", "inbox"}
    if unknown:
        sys.exit(f"refused: unknown tool group(s) {sorted(unknown)}; read-only groups are memory and inbox")
    server, cat = build_server(a.plugins_root, a.plugin, a.repo_root, tools, a.viewer, tiers)
    if a.print_index:
        print(json.dumps(cat.index(), indent=2))
        return
    if a.http:
        server.settings.host, server.settings.port = "127.0.0.1", a.http
        server.run("streamable-http")
    else:
        server.run("stdio")


if __name__ == "__main__":
    main()
