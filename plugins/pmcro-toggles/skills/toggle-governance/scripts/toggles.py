#!/usr/bin/env python3
"""Govern feature toggles kept in an OpenFeature flag manifest (flags.json) plus a governance sidecar.

  toggles.py add NAME --type boolean|string|integer|float|object --default JSON --description D
                 --owner SEAT --expires YYYY-MM-DD --stages "internal,10%,50%,100%" [--manifest flags.json]
  toggles.py check [--manifest flags.json] [--src DIR] [--today YYYY-MM-DD]        read-only; changes nothing
  toggles.py retire-plan NAME [--manifest flags.json] [--src DIR]                    read-only; prints the plan
The manifest follows the OpenFeature CLI schema (flags.<name>.flagType, defaultValue, description). Governance lives in
the sidecar flags.governance.json next to it (owner, created, expires, stages), so the manifest stays standard.
check reports: a flag without governance, governance without a flag, an expired flag, a default value of the wrong
type, and (with --src) how many source files still name each flag. Exit codes: 0 clean or done; 1 findings or
refused; 2 usage error. Nothing here sets a policy limit (such as a maximum flag age); the owner sets expires.
"""
import argparse, datetime, json, pathlib, re, sys

SCHEMA = "https://raw.githubusercontent.com/open-feature/cli/refs/heads/main/schema/v0/flag-manifest.json"
TYPES = {"boolean": bool, "string": str, "integer": int, "float": (int, float), "object": dict}
NAME_RE = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
SRC_SUFFIXES = {".py", ".cs", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt", ".rb", ".php", ".razor", ".cshtml"}


def paths(manifest):
    m = pathlib.Path(manifest)
    return m, m.with_name(m.stem + ".governance.json")


def load(manifest):
    m, g = paths(manifest)
    flags = json.loads(m.read_text()) if m.is_file() else {"$schema": SCHEMA, "flags": {}}
    gov = json.loads(g.read_text()) if g.is_file() else {"flags": {}}
    return flags, gov


def type_ok(flag_type, value):
    want = TYPES.get(flag_type)
    if want is None:
        return False
    if flag_type in ("integer", "float") and isinstance(value, bool):
        return False  # bool is an int in Python; a flag default of true is not a number
    return isinstance(value, want)


def references(src, names):
    """Count source files that mention each flag name as a whole word."""
    counts = {n: 0 for n in names}
    if not src:
        return counts
    pats = {n: re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(n) + r"(?![A-Za-z0-9_-])") for n in names}
    for f in sorted(pathlib.Path(src).rglob("*")):
        if f.is_file() and f.suffix in SRC_SUFFIXES and ".git" not in f.parts:
            text = f.read_text(errors="ignore")
            for n, p in pats.items():
                if p.search(text):
                    counts[n] += 1
    return counts


def cmd_add(a):
    if not NAME_RE.match(a.name):
        sys.exit("refused: flag name must be lowercase letters, digits and hyphens, starting with a letter")
    try:
        default = json.loads(a.default)
        expires = datetime.date.fromisoformat(a.expires)
    except (json.JSONDecodeError, ValueError) as e:
        sys.exit(f"refused: --default must be JSON and --expires YYYY-MM-DD ({e})")
    if not type_ok(a.type, default):
        sys.exit(f"refused: default value {a.default} is not a {a.type}")
    if not a.owner.strip() or not a.description.strip():
        sys.exit("refused: every flag needs an owner and a description")
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
    if expires <= today:
        sys.exit("refused: --expires must be after today; a flag without a future removal date is permanent by accident")
    stages = [s.strip() for s in a.stages.split(",") if s.strip()]
    if not stages:
        sys.exit("refused: name at least one rollout stage")
    flags, gov = load(a.manifest)
    if a.name in flags["flags"] or a.name in gov["flags"]:
        sys.exit(f"refused: flag {a.name!r} already exists; flags are not redefined, retire it and add a new one")
    flags["flags"][a.name] = {"flagType": a.type, "defaultValue": default, "description": a.description.strip()}
    gov["flags"][a.name] = {"owner": a.owner.strip(), "created": today.isoformat(), "expires": expires.isoformat(),
                            "stages": stages}
    m, g = paths(a.manifest)
    m.write_text(json.dumps(flags, indent=2) + "\n")
    g.write_text(json.dumps(gov, indent=2) + "\n")
    print(f"added {a.name} ({a.type}, default {a.default}) owner={a.owner} expires={expires} -> {m.name}, {g.name}")
    return 0


def findings(flags, gov, src, today):
    out = []
    names = sorted(set(flags["flags"]) | set(gov["flags"]))
    refs = references(src, names)
    for n in names:
        f, g = flags["flags"].get(n), gov["flags"].get(n)
        if f is None:
            out.append(f"{n}: governance record but no flag in the manifest (remove the record or restore the flag)")
            continue
        if g is None:
            out.append(f"{n}: flag has no governance record (no owner, no expiry)")
        elif datetime.date.fromisoformat(g["expires"]) < today:
            out.append(f"{n}: expired on {g['expires']} (owner {g['owner']}); plan its removal")
        if not type_ok(f.get("flagType"), f.get("defaultValue")):
            out.append(f"{n}: default value {json.dumps(f.get('defaultValue'))} is not a {f.get('flagType')}")
    return out, refs


def cmd_check(a):
    flags, gov = load(a.manifest)
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
    out, refs = findings(flags, gov, a.src, today)
    for line in out:
        print(line)
    if a.src:
        for n, c in refs.items():
            print(f"{n}: named in {c} source file(s)")
    print(f"{len(flags['flags'])} flag(s) checked; {len(out)} finding(s)")
    return 1 if out else 0


def cmd_retire_plan(a):
    flags, gov = load(a.manifest)
    if a.name not in flags["flags"]:
        sys.exit(f"refused: no flag {a.name!r} in the manifest")
    refs = references(a.src, [a.name])[a.name] if a.src else None
    g = gov["flags"].get(a.name, {})
    f = flags["flags"][a.name]
    print(f"Retire plan for {a.name} (owner {g.get('owner', 'none recorded')}, expires {g.get('expires', 'never set')})")
    print(f"1. Decide the final value; the current default is {json.dumps(f['defaultValue'])}.")
    if refs is None:
        print("2. Find code that reads the flag (run again with --src to count it).")
    else:
        print(f"2. Remove the flag from {refs} source file(s), keeping only the final value's code path.")
    print("3. Remove the flag from the manifest and its governance record in one change, with its trail frame.")
    print("4. A separate Checker reruns `check --src` and confirms the flag is named in 0 source files.")
    return 0


def main(argv):
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("add"); x.add_argument("name"); x.add_argument("--type", required=True, choices=TYPES)
    x.add_argument("--default", required=True); x.add_argument("--description", required=True)
    x.add_argument("--owner", required=True); x.add_argument("--expires", required=True)
    x.add_argument("--stages", required=True); x.add_argument("--today")
    for name in ("check", "retire-plan"):
        y = s.add_parser(name)
        if name == "retire-plan":
            y.add_argument("name")
        y.add_argument("--src"); y.add_argument("--today")
    for sub in s.choices.values():
        sub.add_argument("--manifest", default="flags.json")
    a = p.parse_args(argv)
    return {"add": cmd_add, "check": cmd_check, "retire-plan": cmd_retire_plan}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
