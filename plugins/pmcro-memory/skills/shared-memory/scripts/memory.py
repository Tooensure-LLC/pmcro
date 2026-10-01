#!/usr/bin/env python3
"""Shared, tiered, append-only memory (markdown files, stdlib only) for the founder and every agent.

  memory.py add --tier T --title "..." (--text "..." | --text-file F) [--tags a,b] [--source founder|agent]
                [--status candidate|accepted] [--seats cfo,cto] [--supersedes M0003]
  memory.py search "query words" [--viewer founder|public|company|seat:ID] [--tags a] [--all] [--limit 5]
  memory.py show M0003 [--viewer ...]
  memory.py list [--viewer ...] [--all]
Storage: <tier dir>/memory/M0001.md with front matter. Tiers match trail-player: public and company -> trail/,
roundtable and private -> .trail-local/ (must be gitignored). Entries are never edited: a correction is a new
entry with --supersedes, and superseded entries are hidden unless --all.
Who sees what (--viewer): founder sees every tier; seat:ID sees public, company and roundtable entries that
list that seat; company sees public and company; public sees public only. The default viewer is public.
Rules: credential-shaped text is refused; roundtable entries must name --seats; only --source founder may set
--status accepted (agents write candidate; acceptance of a lesson is human-owned). Search ranks title, tag and
body matches with a simple inverse-frequency weight; it is keyword search, not meaning search.
Output: one line per hit with id, tier, status, title and a snippet; "refused: ..." and exit 1 on a rule violation.
"""
import argparse, datetime, math, os, pathlib, re, subprocess, sys

TIERS = {"public": "trail/public", "company": "trail/company",
         "roundtable": ".trail-local/roundtable", "private": ".trail-local/private"}
LOCAL_ONLY = {"roundtable", "private"}
SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|Bearer\s+\S{12,}|password\s*[:=]|api[_-]?key\s*[:=]|secret\s*[:=]|token\s*[:=]|-----BEGIN [A-Z ]*PRIVATE KEY", re.I)
WORD = re.compile(r"[a-z0-9]+")


def root():
    return pathlib.Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def mem_dir(tier, create=False):
    r = root()
    rel = TIERS[tier]
    if tier in LOCAL_ONLY and subprocess.run(["git", "-C", str(r), "check-ignore", "-q", rel + "/x"]).returncode != 0:
        sys.exit(f"refused: {rel} is not gitignored; add it to .gitignore first")
    d = r / rel / "memory"
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def parse(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    meta["body"] = m.group(2).strip()
    meta["tags"] = [t for t in meta.get("tags", "").split(",") if t]
    meta["seats"] = [s for s in meta.get("seats", "").split(",") if s]
    return meta


def visible(meta, viewer):
    tier = meta["tier"]
    if viewer == "founder":
        return True
    if tier == "public":
        return True
    if viewer == "public":
        return False
    if tier == "company":
        return True
    if tier == "roundtable" and viewer.startswith("seat:"):
        return viewer.split(":", 1)[1] in meta["seats"]
    return False


def load_all(viewer, include_superseded=False):
    entries = []
    for tier in TIERS:
        d = root() / TIERS[tier] / "memory"
        if not d.is_dir():
            continue
        if tier in LOCAL_ONLY:
            mem_dir(tier)  # gitignore guard
        for f in sorted(d.glob("M[0-9][0-9][0-9][0-9].md")):
            m = parse(f)
            if visible(m, viewer):
                entries.append(m)
    gone = {e.get("supersedes") for e in entries if e.get("supersedes")}
    if not include_superseded:
        entries = [e for e in entries if e["id"] not in gone]
    for e in entries:
        e["superseded"] = e["id"] in gone
    return entries


def next_id():
    n = 0
    for tier in TIERS:
        d = root() / TIERS[tier] / "memory"
        if d.is_dir():
            for f in d.glob("M[0-9][0-9][0-9][0-9].md"):
                n = max(n, int(f.stem[1:]))
    return n + 1


def add(a):
    text = pathlib.Path(a.text_file).read_text() if a.text_file else (a.text or "")
    if not text.strip() or not a.title.strip():
        sys.exit("refused: title and text are required")
    if SECRET.search(a.title + text):
        sys.exit("refused: credential-shaped text; memory never stores credentials")
    if a.tier == "roundtable" and not a.seats:
        sys.exit("refused: roundtable memory must name --seats")
    if a.status == "accepted" and a.source != "founder":
        sys.exit("refused: only the founder can mark a memory accepted; agents write candidate")
    if a.supersedes:
        old = [e for e in load_all("founder", True) if e["id"] == a.supersedes]
        if not old:
            sys.exit(f"refused: no memory {a.supersedes} to supersede")
    d = mem_dir(a.tier, create=True)
    n = next_id()
    while True:
        i = f"M{n:04d}"
        try:
            fd = os.open(d / f"{i}.md", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            n += 1
    tags = ",".join(t.strip().lower() for t in a.tags.split(",") if t.strip())
    head = f"id: {i}\ntitle: {a.title.strip()}\ntier: {a.tier}\ntags: {tags}\nsource: {a.source}\nstatus: {a.status}\ncreated: {datetime.date.today().isoformat()}\n"
    if a.seats:
        head += f"seats: {a.seats}\n"
    if a.supersedes:
        head += f"supersedes: {a.supersedes}\n"
    with os.fdopen(fd, "w") as fh:
        fh.write(f"---\n{head}---\n{text.strip()}\n")
    print(f"remembered {i} tier={a.tier} status={a.status}")


def score(entries, query):
    terms = WORD.findall(query.lower())
    n = len(entries) or 1
    df = {t: sum(1 for e in entries if t in WORD.findall((e["title"] + " " + " ".join(e["tags"]) + " " + e["body"]).lower())) for t in terms}
    out = []
    for e in entries:
        title, body = WORD.findall(e["title"].lower()), WORD.findall(e["body"].lower())
        s = 0.0
        for t in terms:
            idf = math.log(1 + n / (1 + df[t]))
            s += idf * (3 * title.count(t) + 2 * e["tags"].count(t) + body.count(t))
        if s > 0:
            out.append((s, e))
    return sorted(out, key=lambda x: (-x[0], x[1]["id"]))


def line(e, snippet=""):
    flag = " [superseded]" if e.get("superseded") else ""
    return f"{e['id']} [{e['tier']}/{e['status']}]{flag} {e['title']}" + (f" - {snippet}" if snippet else "")


def snippet(e, query):
    body = " ".join(e["body"].split())
    for t in WORD.findall(query.lower()):
        i = body.lower().find(t)
        if i >= 0:
            return body[max(0, i - 40): i + 80]
    return body[:80]


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("add"); x.add_argument("--tier", required=True, choices=TIERS); x.add_argument("--title", required=True)
    x.add_argument("--text"); x.add_argument("--text-file"); x.add_argument("--tags", default="")
    x.add_argument("--source", default="agent", choices=["founder", "agent"]); x.add_argument("--status", default="candidate", choices=["candidate", "accepted"])
    x.add_argument("--seats", default=""); x.add_argument("--supersedes", default="")
    x = s.add_parser("search"); x.add_argument("query"); x.add_argument("--viewer", default="public"); x.add_argument("--tags", default="")
    x.add_argument("--all", action="store_true"); x.add_argument("--limit", type=int, default=5)
    x = s.add_parser("show"); x.add_argument("id"); x.add_argument("--viewer", default="public")
    x = s.add_parser("list"); x.add_argument("--viewer", default="public"); x.add_argument("--all", action="store_true")
    a = p.parse_args()
    if a.cmd == "add":
        return add(a)
    entries = load_all(a.viewer, include_superseded=getattr(a, "all", False) or a.cmd == "show")
    if a.cmd == "search":
        if a.tags:
            want = {t.strip().lower() for t in a.tags.split(",")}
            entries = [e for e in entries if want & set(e["tags"])]
        hits = score(entries, a.query)[: a.limit]
        for _, e in hits:
            print(line(e, snippet(e, a.query)))
        print(f"{len(hits)} hits")
    elif a.cmd == "show":
        e = next((e for e in entries if e["id"] == a.id), None)
        if not e:
            sys.exit(f"refused: no memory {a.id} visible to {a.viewer}")
        print(line(e) + "\n" + e["body"])
    else:
        for e in entries:
            print(line(e))
        print(f"{len(entries)} memories")


if __name__ == "__main__":
    main()
