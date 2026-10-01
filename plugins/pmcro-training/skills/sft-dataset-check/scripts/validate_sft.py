#!/usr/bin/env python3
"""Check a PMCR-O SFT dataset (JSONL of {messages, meta}) against the owner's working schema.

Implements the section 9 validation profile of the Training Data Schema as errors (structure,
enums) and heuristic warnings (governance guards). It never sets eligibility: ELIGIBLE needs an
independent Dataset Checker verdict, which this script cannot give. Usage: validate_sft.py FILE...
[--json] [--allow-kind K] [--profile v2|candidate]. Exit 1 if any error; warnings do not fail.
"""
import argparse, collections, json, re, sys

KINDS = """section_recall status_resolution source_precedence matrix_lookup matrix_group authority_reasoning
routing_reasoning evidence_reasoning checker_reasoning marketplace_reasoning identity_reasoning
discovery_reasoning architecture_reasoning guard_reasoning contradiction_resolution""".split()
PROV = """CANONICAL_OR_REPOSITORY_AUTHORITY SOURCE_CORPUS_SNAPSHOT APPROVED_SESSION_DECISION
APPROVED_ARCHITECTURAL_BOUNDARY PROPOSED_ARCHITECTURE CANDIDATE OPEN""".split()
DISP = ["APPROVE_AS_ARCHITECTURAL_BOUNDARY", "KEEP_AS_CANDIDATE", "KEEP_OPEN", "REJECT"]
ELIG = ["CANDIDATE", "ELIGIBLE", "WITHHELD", "CANDIDATE_DATASET"]
SPLITS = ["train", "validation", "test"]
REQ = {"kind": str, "sources": list, "provenance": list, "source_state": list, "expected_state": (str, type(None)),
       "architecture_disposition": (str, type(None)), "invariants": list, "open_items": list,
       "candidate_items": list, "requires_correction": bool, "requires_refusal": bool,
       "difficulty": str, "domain": list, "tags": list}
V2_EXTRA = {"example_id": str, "schema_version": str, "split": str, "self_check_expected": bool,
            "independent_checker_required": bool, "eligibility_state": str}

# (code, regex over assistant text). A hit is a WARNING for a human/Checker to read, never a verdict.
GUARDS = [
    ("G10-maker-verdict", r"\bMaker\b[^.]{0,60}\b(issues?|gives?|assigns?|declares?)\b[^.]{0,30}\b(PASS|LOOP|HALT)\b"),
    ("G11-checker-repairs", r"\bChecker\b[^.]{0,40}\b(fixes|repairs|patches|edits|rewrites)\b"),
    ("G12-match-is-pass", r"\bMATCH\b\s*(=|equals|is|means)\s*(a\s+)?PASS\b"),
    ("G13-mismatch-is-loop", r"\bMISMATCH\b\s*(=|equals|is|means)\s*(a\s+)?(LOOP|HALT)\b"),
    ("G15-buyer-is-customer", r"\bBuyer\b\s*(=|equals|is the same as)\s*Customer\b"),
    ("G7-candidate-promoted", r"\bCANDIDATE\b[^.]{0,40}\b(is now|has become|becomes|promoted to)\b[^.]{0,20}\b(law|existing|approved)\b"),
    ("G6-open-resolved", r"\bOPEN\b[^.]{0,40}\b(is now|has been|is) resolved\b"),
    ("G17-evasion-taught", r"\b(bypass|evade|circumvent)\b[^.]{0,40}\b(rate limit|captcha|safety|moderation|platform)\b"),
]
CRED = re.compile(r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)")
NEG = re.compile(r"\b(not|never|no|cannot|must not|does not|doesn't|isn't|is not)\b", re.I)


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def check_record(i, r, profile, kinds):
    e, w = [], []
    if not isinstance(r, dict) or set(r) != {"messages", "meta"}:
        return [f"root keys must be exactly messages+meta, got {sorted(r) if isinstance(r, dict) else type(r).__name__}"], w
    m, meta = r["messages"], r["meta"]
    if not isinstance(m, list) or len(m) != 3:
        e.append("messages must be a list of exactly 3")
    else:
        for k, role in enumerate(["system", "user", "assistant"]):
            if not isinstance(m[k], dict) or m[k].get("role") != role:
                e.append(f"messages[{k}].role must be {role}")
            elif not isinstance(m[k].get("content"), str) or not m[k]["content"].strip():
                e.append(f"messages[{k}] has empty content")
    if not isinstance(meta, dict):
        return e + ["meta must be an object"], w
    for k, t in REQ.items():
        if k not in meta:
            e.append(f"meta.{k} missing")
        elif not isinstance(meta[k], t):
            e.append(f"meta.{k} has wrong type")
    if profile != "base":
        for k, t in V2_EXTRA.items():
            if k not in meta:
                e.append(f"meta.{k} missing")
            elif not isinstance(meta[k], t):
                e.append(f"meta.{k} has wrong type")
    if meta.get("kind") not in kinds:
        e.append(f"unknown kind {meta.get('kind')!r}")
    for p in meta.get("provenance", []) if isinstance(meta.get("provenance"), list) else []:
        if p not in PROV:
            e.append(f"unknown provenance class {p!r}")
    if meta.get("provenance") == []:
        e.append("provenance empty")
    d = meta.get("architecture_disposition")
    if d is not None and d not in DISP:
        e.append(f"unknown architecture_disposition {d!r}")
    if "split" in meta and meta["split"] not in SPLITS:
        e.append(f"unknown split {meta['split']!r}")
    if "eligibility_state" in meta and meta["eligibility_state"] not in ELIG:
        e.append(f"unknown eligibility_state {meta['eligibility_state']!r}")
    if meta.get("eligibility_state") == "ELIGIBLE":
        w.append("ELIGIBLE set in file: this script cannot confirm an independent Dataset Checker PASS")
    if meta.get("requires_refusal") is True and isinstance(m, list) and len(m) == 3:
        a = str(m[2].get("content", ""))
        if not NEG.search(a):
            w.append("requires_refusal true but answer has no refusal/negation wording")
    if isinstance(m, list) and len(m) == 3 and isinstance(m[2].get("content"), str):
        a = m[2]["content"]
        for code, rx in GUARDS:
            for hit in re.finditer(rx, a, re.I if code.startswith(("G17", "G15")) else 0):
                ctx = a[max(0, hit.start() - 60):hit.start()]
                if not NEG.search(ctx + hit.group(0)):
                    w.append(f"{code}: {hit.group(0)[:80]!r}")
        if CRED.search(json.dumps(r)):
            e.append("credential-shaped text")
        if isinstance(m[0].get("content"), str) and profile == "v2" and not m[0]["content"].lstrip().startswith("I AM"):
            w.append("system prompt lacks the first-person 'I AM' profile (Final Spec section 2)")
    return e, w


def check_file(path, profile, kinds):
    out = {"file": path, "records": 0, "errors": [], "warnings": [], "kinds": {}, "splits": {}, "eligibility": {}}
    rows = []
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except Exception as ex:
        out["errors"].append(f"cannot read: {ex}")
        return out
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            rows.append((n, json.loads(line)))
        except ValueError as ex:
            out["errors"].append(f"line {n}: invalid JSON ({ex})")
    out["records"] = len(rows)
    kc, sc, ec = collections.Counter(), collections.Counter(), collections.Counter()
    ids, users, answers = {}, {}, {}
    for n, r in rows:
        e, w = check_record(n, r, profile, kinds)
        out["errors"] += [f"line {n}: {x}" for x in e]
        out["warnings"] += [f"line {n}: {x}" for x in w]
        meta = r.get("meta", {}) if isinstance(r, dict) else {}
        if not isinstance(meta, dict):
            continue
        kc[meta.get("kind")] += 1
        sc[meta.get("split")] += 1
        ec[meta.get("eligibility_state")] += 1
        eid = meta.get("example_id")
        if eid is not None:
            if eid in ids:
                out["errors"].append(f"line {n}: duplicate example_id {eid} (first at line {ids[eid]})")
            ids.setdefault(eid, n)
        try:
            u, a = norm(r["messages"][1]["content"]), norm(r["messages"][2]["content"])
        except Exception:
            continue
        for table, key, label in ((users, u, "user prompt"), (answers, a, "assistant answer")):
            if key in table:
                p = table[key]
                same = p[1] == meta.get("split")
                (out["warnings"] if same else out["errors"]).append(
                    f"line {n}: identical {label} as line {p[0]}" + ("" if same else f" in split {p[1]} vs {meta.get('split')}: split leak"))
            else:
                table[key] = (n, meta.get("split"))
    out["kinds"], out["splits"], out["eligibility"] = dict(kc), dict(sc), dict(ec)
    missing = [k for k in KINDS if k not in kc]
    if profile == "v2" and missing:
        out["warnings"].append(f"coverage: {len(missing)} of 15 kinds absent: {', '.join(missing)}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--profile", choices=["v2", "base", "candidate"], default="v2",
                    help="v2: full contract incl. example_id/split/eligibility; base: meta of schema section 4 only; "
                         "candidate: v2 contract but any kind string accepted (reports kinds outside the 15)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    prof = "v2" if a.profile == "candidate" else a.profile
    bad = False
    reports = []
    for f in a.files:
        kinds = None if a.profile == "candidate" else KINDS
        if kinds is None:
            class Any:  # accept any kind but record that it is outside the 15
                def __contains__(self, x):
                    return isinstance(x, str)
            kinds = Any()
        rep = check_file(f, prof, kinds)
        if a.profile == "candidate":
            extra = sorted(k for k in rep["kinds"] if k not in KINDS)
            if extra:
                rep["warnings"].append(f"{len(extra)} kinds outside the 15 in the Final Spec (Checker must decide): {', '.join(map(str, extra))}")
        reports.append(rep)
        bad |= bool(rep["errors"])
    if a.json:
        print(json.dumps(reports, indent=1))
    else:
        for r in reports:
            print(f"{r['file']}: {r['records']} records, {len(r['errors'])} errors, {len(r['warnings'])} warnings")
            print("  kinds:", r["kinds"]); print("  splits:", r["splits"], " eligibility:", r["eligibility"])
            for tag, items in (("ERROR", r["errors"]), ("warn ", r["warnings"])):
                groups = collections.Counter(re.sub(r"^line \d+: ", "", x) for x in items)
                for msg, n in groups.most_common(25):
                    print(f"  {tag} x{n}: {msg}")
        print("NOTE: no ELIGIBLE verdict is possible here; independent Dataset Checker required.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
