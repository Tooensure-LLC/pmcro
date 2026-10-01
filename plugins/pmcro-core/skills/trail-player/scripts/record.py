#!/usr/bin/env python3
"""Append-only trail writer with disclosure tiers."""
import argparse, json, subprocess, sys, datetime, pathlib

TIERS = {"public": "trail/public", "company": "trail/company",
         "roundtable": ".trail-local/roundtable", "private": ".trail-local/private"}
LOCAL_ONLY = {"roundtable", "private"}
KINDS = {"goal", "idea", "secret", "habit", "problem", "decision", "note"}


def root():
    return pathlib.Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True).strip())


def ignored(r, rel):
    return subprocess.run(["git", "-C", str(r), "check-ignore", "-q", rel + "/x"]).returncode == 0


def next_id(r):
    n = 0
    for d in TIERS.values():
        for f in (r / d).glob("*.json"):
            try:
                n = max(n, int(f.name.split("-")[0]))
            except ValueError:
                pass
    return n + 1


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--tier", choices=TIERS, required=True)
    a.add_argument("--replay", action="store_true")
    a.add_argument("--kind", choices=sorted(KINDS))
    a.add_argument("--body-file")
    a.add_argument("--summary", default="")
    a.add_argument("--seats", default="")
    a.add_argument("--refs", default="")
    a.add_argument("--cost-tokens", type=int)
    a.add_argument("--cost-usd", type=float)
    a = a.parse_args()
    r = root()
    d = r / TIERS[a.tier]
    if a.replay:
        for f in sorted(d.glob("*.json")):
            e = json.loads(f.read_text())
            print(f"#{e['id']} {e['time']} [{e['tier']}/{e['kind']}]\n{e['body']}\n")
        return
    if not a.kind or not a.body_file:
        sys.exit("--kind and --body-file are required to record")
    if a.tier in LOCAL_ONLY and not ignored(r, TIERS[a.tier]):
        sys.exit(f"refused: {TIERS[a.tier]} is not gitignored; add it to .gitignore first")
    if a.tier == "roundtable" and not a.seats:
        sys.exit("refused: roundtable entries must name seats with --seats")
    d.mkdir(parents=True, exist_ok=True)
    i = next_id(r)
    entry = {"id": f"{i:04d}", "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "tier": a.tier, "kind": a.kind, "body": pathlib.Path(a.body_file).read_text(),
             "summary": a.summary, "seats": [s for s in a.seats.split(",") if s],
             "refs": [s for s in a.refs.split(",") if s]}
    if a.tier == "roundtable":
        entry["note"] = "Shared in confidence with the listed seats. Do not disclose, summarize to others, or use for training. House rule, not a legal contract."
    if a.cost_tokens is not None or a.cost_usd is not None:
        entry["cost"] = {"tokens": a.cost_tokens, "usd": a.cost_usd}
    path = d / f"{entry['id']}-{a.kind}.json"
    with open(path, "x") as fh:  # 'x' refuses to overwrite: append-only
        json.dump(entry, fh, indent=2)
    print(f"recorded #{entry['id']} tier={a.tier} -> {path.relative_to(r)}")


if __name__ == "__main__":
    main()
