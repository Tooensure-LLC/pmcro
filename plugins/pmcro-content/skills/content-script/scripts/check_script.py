#!/usr/bin/env python3
"""Check a content script's structure. It verifies form, never truth.

  python check_script.py <script.md> [--wpm 150] [--tolerance 0.2]
Checks: front matter has title, duration_min, synthetic_voice, synthetic_image; the ## Script word
count is within tolerance of duration_min x wpm; ## Claims has at least one row and every row has a
source (a link, a path or the word opinion); synthetic voice or image requires a ## Disclosure that
says so; no private/roundtable trail markers or .trail-local paths appear anywhere in the file.
Output: one "ERROR <reason>" line per problem, then "ok: N words, M claims" if none. Exit 1 on error.
It never prints PASS, LOOP or HALT: only the Checker role issues verdicts.
"""
import argparse, re, sys

REQUIRED = ("title", "duration_min", "synthetic_voice", "synthetic_image")
LEAK = re.compile(r"tier:\s*(private|roundtable)|\.trail-local|\[(private|roundtable)\]", re.I)


def sections(body):
    out, name = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            name = m.group(1).strip().lower()
            out[name] = []
        elif name:
            out[name].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def check(text, wpm=150, tol=0.2):
    errs = []
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if not m:
        return ["ERROR missing front matter"], 0, 0
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    for k in REQUIRED:
        if k not in fm:
            errs.append(f"ERROR front matter missing {k}")
    sec = sections(text[m.end():])
    script = sec.get("script", "")
    words = len(script.split())
    try:
        target = float(fm["duration_min"]) * wpm
        if not script:
            errs.append("ERROR empty or missing ## Script")
        elif abs(words - target) > target * tol:
            errs.append(f"ERROR script is {words} words; {fm['duration_min']} min at {wpm} wpm is about {int(target)} (+/- {int(tol*100)}%)")
    except (KeyError, ValueError):
        errs.append("ERROR duration_min must be a number")
    rows = [ln for ln in sec.get("claims", "").splitlines() if ln.strip().startswith("|")][2:]
    rows = [r for r in rows if "example factual claim" not in r.lower()]
    if not rows:
        errs.append("ERROR ## Claims needs at least one row (use source 'opinion' for views)")
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[1]:
            errs.append(f"ERROR claim has no source: {cells[0][:50]}")
    if fm.get("synthetic_voice", "").lower() == "true" or fm.get("synthetic_image", "").lower() == "true":
        d = sec.get("disclosure", "").lower()
        if not d or not re.search(r"synthetic|ai-generated|ai generated", d):
            errs.append("ERROR synthetic voice or image needs a ## Disclosure that says so")
    if LEAK.search(text):
        errs.append("ERROR private/roundtable trail marker or .trail-local path found; never publish from those tiers")
    return errs, words, len(rows)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("script"); a.add_argument("--wpm", type=int, default=150); a.add_argument("--tolerance", type=float, default=0.2)
    a = a.parse_args()
    errs, words, claims = check(open(a.script, encoding="utf-8").read(), a.wpm, a.tolerance)
    print("\n".join(errs) if errs else f"ok: {words} words, {claims} claims")
    sys.exit(1 if errs else 0)
