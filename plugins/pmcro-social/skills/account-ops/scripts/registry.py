#!/usr/bin/env python3
"""Credential-free registry of the founder's accounts, with an append-only log and a "needs you" brief.

  registry.py add --platform P --handle H --purpose "..." [--cadence-days N] [--owner founder|company]
  registry.py import FILE.csv            columns: platform,handle,purpose,cadence_days,owner (header row required)
  registry.py posted ID [--date YYYY-MM-DD] [--note N]     record a post or other activity (a human did it)
  registry.py retire ID --reason "..."   mark an account retired (never deletes anything)
  registry.py list [--all]               active accounts (--all includes retired)
  registry.py review                     hygiene flags: no purpose, no cadence, never active, quiet too long
  registry.py brief [--today YYYY-MM-DD] what needs a human now, most overdue first
Storage: .trail-local/private/accounts/accounts.jsonl (gitignored; refuses to write otherwise). Events only
append; state is derived. Ids are A01, A02, ...
Rules: it never stores or accepts credentials (password, token, key, secret fields or credential-shaped text are
refused). It cannot post anywhere; it only records what a human did. "Review" flags are suggestions for a human,
never actions: nothing here retires or changes an account on its own.
Output: one line per result; "refused: ..." and exit 1 on a rule violation.
"""
import argparse, csv, datetime, json, pathlib, re, subprocess, sys

REL = ".trail-local/private/accounts"
SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|Bearer\s+\S{12,}|password\s*[:=]|api[_-]?key\s*[:=]|secret\s*[:=]|token\s*[:=]", re.I)
BAD_COLUMNS = {"password", "token", "secret", "key", "api_key", "apikey", "credential", "credentials", "cookie", "2fa"}


def root():
    return pathlib.Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def store():
    r = root()
    if subprocess.run(["git", "-C", str(r), "check-ignore", "-q", REL + "/x"]).returncode != 0:
        sys.exit(f"refused: {REL} is not gitignored; add it to .gitignore first")
    d = r / REL
    d.mkdir(parents=True, exist_ok=True)
    return d / "accounts.jsonl"


def today():
    return datetime.date.today().isoformat()


def load(f):
    return [json.loads(x) for x in f.read_text().splitlines()] if f.is_file() else []


def state(events):
    acc = {}
    for e in events:
        if e["event"] == "added":
            acc[e["id"]] = {**e["data"], "id": e["id"], "status": "active", "last_active": None, "added": e["date"]}
        elif e["event"] == "posted" and e["id"] in acc:
            acc[e["id"]]["last_active"] = max(filter(None, [acc[e["id"]]["last_active"], e["date"]]))
        elif e["event"] == "retired" and e["id"] in acc:
            acc[e["id"]]["status"] = "retired"
    return acc


def clean(text):
    if SECRET.search(text or ""):
        sys.exit("refused: credential-shaped text; this registry never stores credentials")
    return (text or "").strip()


def append(f, **ev):
    with open(f, "a") as fh:
        fh.write(json.dumps({"date": ev.pop("date", today()), **ev}) + "\n")


def add_one(f, platform, handle, purpose, cadence, owner):
    events = load(f)
    for a in state(events).values():
        if a["platform"].lower() == platform.lower() and a["handle"].lower() == handle.lower() and a["status"] == "active":
            print(f"duplicate: {platform} {handle} is already {a['id']}")
            return
    i = f"A{len(state(events)) + 1:02d}"
    data = {"platform": clean(platform), "handle": clean(handle), "purpose": clean(purpose),
            "cadence_days": cadence, "owner": owner}
    append(f, event="added", id=i, data=data)
    print(f"added {i} {platform} {handle}")


def need(acc, day):
    flags = []
    if not acc["purpose"]:
        flags.append("no purpose")
    if not acc["cadence_days"]:
        flags.append("no cadence set")
    if acc["last_active"] is None:
        flags.append("no activity recorded")
    elif acc["cadence_days"]:
        gap = (day - datetime.date.fromisoformat(acc["last_active"])).days
        if gap > acc["cadence_days"]:
            flags.append(f"{gap - acc['cadence_days']} days overdue (every {acc['cadence_days']} days)")
    return flags


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("add"); x.add_argument("--platform", required=True); x.add_argument("--handle", required=True)
    x.add_argument("--purpose", default=""); x.add_argument("--cadence-days", type=int, default=0); x.add_argument("--owner", default="founder", choices=["founder", "company"])
    x = s.add_parser("import"); x.add_argument("file")
    x = s.add_parser("posted"); x.add_argument("id"); x.add_argument("--date", default=None); x.add_argument("--note", default="")
    x = s.add_parser("retire"); x.add_argument("id"); x.add_argument("--reason", required=True)
    x = s.add_parser("list"); x.add_argument("--all", action="store_true")
    s.add_parser("review")
    x = s.add_parser("brief"); x.add_argument("--today", default=None)
    a = p.parse_args()
    f = store()
    if a.cmd == "add":
        add_one(f, a.platform, a.handle, a.purpose, a.cadence_days, a.owner)
    elif a.cmd == "import":
        with open(a.file, newline="", encoding="utf-8-sig") as fh:
            rd = csv.DictReader(fh)
            cols = {c.strip().lower() for c in (rd.fieldnames or [])}
            if cols & BAD_COLUMNS:
                sys.exit(f"refused: column(s) {sorted(cols & BAD_COLUMNS)} look like credentials; remove them")
            if not {"platform", "handle"} <= cols:
                sys.exit("refused: CSV needs at least platform and handle columns")
            for row in rd:
                row = {k.strip().lower(): (v or "") for k, v in row.items() if k}
                add_one(f, row["platform"], row["handle"], row.get("purpose", ""), int(row.get("cadence_days") or 0), row.get("owner") or "founder")
    elif a.cmd in ("posted", "retire"):
        acc = state(load(f))
        if a.id not in acc:
            sys.exit(f"refused: no account {a.id}")
        if a.cmd == "posted":
            d = a.date or today()
            datetime.date.fromisoformat(d)
            append(f, event="posted", id=a.id, date=d, note=clean(a.note))
            print(f"recorded activity for {a.id} on {d}")
        else:
            append(f, event="retired", id=a.id, reason=clean(a.reason))
            print(f"retired {a.id}")
    else:
        acc = state(load(f))
        day = datetime.date.fromisoformat(getattr(a, "today", None) or today())
        shown = [v for v in acc.values() if getattr(a, "all", False) or v["status"] == "active"]
        if a.cmd == "list":
            for v in shown:
                print(f"{v['id']} [{v['status']}] {v['platform']} {v['handle']} every {v['cadence_days'] or '?'}d last {v['last_active'] or 'never'} ({v['owner']})")
            print(f"{len(shown)} accounts")
        elif a.cmd == "review":
            n = 0
            for v in shown:
                fl = need(v, day)
                if fl:
                    n += 1
                    print(f"{v['id']} {v['platform']} {v['handle']}: {'; '.join(fl)}")
            print(f"{n} of {len(shown)} accounts have flags (suggestions for a human, not actions)")
        else:
            rows = []
            for v in shown:
                fl = need(v, day)
                od = [int(x.split()[0]) for x in fl if "overdue" in x]
                if fl:
                    rows.append((-(od[0] if od else 0), v["id"], v, fl))
            for _, _, v, fl in sorted(rows):
                print(f"{v['id']} {v['platform']} {v['handle']}: {'; '.join(fl)}")
            print(f"{len(rows)} need you ({len(shown)} active). Drafts wait in the approval queue; you post or approve.")


if __name__ == "__main__":
    main()
