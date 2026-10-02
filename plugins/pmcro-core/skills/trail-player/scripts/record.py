#!/usr/bin/env python3
"""Append-only trail writer with disclosure tiers.

Records one founder entry as numbered JSON, or replays entries for a tier.
  record:  record.py --tier private --kind habit --body-file entry.txt [--seats cfo,cto] [--summary S] [--refs 0007] [--cost-tokens N] [--cost-usd X]
  replay:  record.py --tier private --replay
Tiers: public and company -> trail/ (committable); roundtable and private -> .trail-local/ (gitignored).
Refuses (exit 1, "refused: ..."):
  - credential-shaped text or an absolute path in the body or summary, in every tier (EC-0001). The check is
    first proven able to fail on a sample built and serialized by this script's own code, and a refusal names
    the rule, never the matched text, so the secret is not echoed;
  - private or roundtable when its folder is not gitignored;
  - company unless the repo is declared private (git config pmcro.repoVisibility private); company files are
    committable, so the check fails closed;
  - roundtable without --seats; any overwrite.
Numbering: each tier counts on its own from 0001 and never reads another tier's folder, so a gap in one tier
cannot reveal entries in another. Replay prints the tier asked for; it cannot check who is calling.
Output: "recorded #NNNN tier=T -> path" on success.
"""
import argparse, datetime, json, pathlib, re, subprocess, sys

TIERS = {"public": "trail/public", "company": "trail/company",
         "roundtable": ".trail-local/roundtable", "private": ".trail-local/private"}
LOCAL_ONLY = {"roundtable", "private"}
KINDS = {"goal", "idea", "secret", "habit", "problem", "decision", "note"}

# Credential shapes: provider key prefixes, bearer tokens, PEM private keys, and key=value or "key": "value"
# assignments. Deliberately narrow; ordinary prose that mentions the word "password" is not refused.
SECRET = re.compile(
    r"\bsk-[A-Za-z0-9_-]{20,}|\bxai-[A-Za-z0-9]{20,}|\bgh[pousr]_[A-Za-z0-9]{30,}|\bAKIA[0-9A-Z]{16}\b"
    r"|\bBearer\s+[A-Za-z0-9._~+/=-]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|(?i:\b(?:password|passwd|api[_-]?key|secret|token)\b[\"']?\s*[:=]\s*[\"']?[^\s\"']{6,})")
# Absolute paths: Windows drive (C:\ or C:/), UNC share, and common POSIX roots. A URL path such as
# https://example.com/home/page is not matched, because the slash before "home" follows a host name.
ABS_PATH = re.compile(
    r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\[A-Za-z0-9._$-]+\\"
    r"|(?<![A-Za-z0-9._~/-])/(?:home|root|mnt|tmp|usr|etc|var|opt|srv|dev|run|data|media|private|Users|Volumes)/")


def root():
    return pathlib.Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def ignored(r, rel):
    return subprocess.run(["git", "-C", str(r), "check-ignore", "-q", rel + "/x"]).returncode == 0


def declared_private(r):
    """Fail closed: the company tier is committable, so it needs an explicit local declaration that the repo is private."""
    out = subprocess.run(["git", "-C", str(r), "config", "--get", "pmcro.repoVisibility"], capture_output=True, text=True)
    return out.stdout.strip().lower() == "private"


def next_id(d):
    """Next number inside one tier folder only; never reads another tier."""
    n = 0
    for f in d.glob("*.json"):
        try:
            n = max(n, int(f.name.split("-")[0]))
        except ValueError:
            pass
    return n + 1


def build_entry(i, tier, kind, body, summary="", seats=(), refs=()):
    return {"id": f"{i:04d}", "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "tier": tier, "kind": kind, "body": body, "summary": summary, "seats": list(seats), "refs": list(refs)}


def serialize(entry):
    return json.dumps(entry, indent=2)


def scan(text):
    """Names of the rules the text breaks, never the matched text."""
    return [name for name, rx in (("credential", SECRET), ("absolute path", ABS_PATH)) if rx.search(text)]


def prove_scanner():
    """EC-0001: the scan must catch a known-bad sample built by this script's own serializer, and pass a clean one."""
    bs = "\\"
    bad = serialize(build_entry(0, "private", "note", "key sk-" + "a1" * 12 + " at C:" + bs + "Users" + bs + "x",
                                "see /" + "home/x/y"))
    good = serialize(build_entry(0, "private", "note", "plain words about trail/public/0001-note.json"))
    if set(scan(bad)) != {"credential", "absolute path"} or scan(good):
        sys.exit("refused: the credential and path check is broken (it missed a known-bad sample or flagged a clean one)")


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
    if a.tier == "company" and not declared_private(r):
        sys.exit("refused: the company tier is committable and this repo is not declared private; if it is private, run "
                 "`git config pmcro.repoVisibility private` once, otherwise use roundtable or private")
    if a.tier == "roundtable" and not a.seats:
        sys.exit("refused: roundtable entries must name seats with --seats")
    prove_scanner()
    body = pathlib.Path(a.body_file).read_text()
    hits = scan(body + "\n" + a.summary)
    if hits:
        sys.exit("refused: the entry contains " + " and ".join(hits) + " (EC-0001); remove it or use a relative path, then record again")
    d.mkdir(parents=True, exist_ok=True)
    entry = build_entry(next_id(d), a.tier, a.kind, body, a.summary,
                        [s for s in a.seats.split(",") if s], [s for s in a.refs.split(",") if s])
    if a.tier == "roundtable":
        entry["note"] = "Shared in confidence with the listed seats. Do not disclose, summarize to others, or use for training. House rule, not a legal contract."
    if a.cost_tokens is not None or a.cost_usd is not None:
        entry["cost"] = {"tokens": a.cost_tokens, "usd": a.cost_usd}
    path = d / f"{entry['id']}-{a.kind}.json"
    with open(path, "x") as fh:  # 'x' refuses to overwrite: append-only
        fh.write(serialize(entry))
    print(f"recorded #{entry['id']} tier={a.tier} -> {path.relative_to(r)}")


if __name__ == "__main__":
    main()
