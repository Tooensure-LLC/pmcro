#!/usr/bin/env python3
"""Seat roster for a round table or a single question, read from assets/seats.json (a snapshot of company.json).

  python run.py --list                 every seat: agent name, status, what it owns
  python run.py --seat cfo             one seat's card, to ask that seat alone
  python run.py --table executive      a configured round table, chair first
  python run.py --seats cfo,cto,cmo    an ad hoc table; the Chief of Staff is added as chair, at most 6 seats in all
Output: one numbered line per seat in speaking order ("pmcro-seats:<id>" is the agent to call), then the founder-first list.
Exit codes: 0 ok; 1 refused (unknown seat or table, more than 6 seats); 2 usage error.
"""
import argparse, json, pathlib, sys

SNAP = json.loads((pathlib.Path(__file__).resolve().parent.parent / "assets" / "seats.json").read_text())
SEATS = {s["id"]: s for s in SNAP["seats"]}
CHAIR = "chief-of-staff"
MAX_SEATS = 6  # company.json: a group chat holds at most 6 bots; kept as a boundary, not worked around


def line(n, s, chair=False):
    tag = " (chair)" if chair else ""
    return f"{n}. pmcro-seats:{s['id']}{tag} - {s['title']} [{s['status']}] owns: {s['owns']}"


def roster(ids):
    unknown = [i for i in ids if i not in SEATS]
    if unknown:
        sys.exit(f"refused: unknown seat(s) {', '.join(unknown)}; run --list for the 15 seat ids")
    order = [CHAIR] + [i for i in dict.fromkeys(ids) if i != CHAIR]
    if len(order) > MAX_SEATS:
        sys.exit(f"refused: {len(order)} seats including the chair; a round table holds at most {MAX_SEATS}. Split it into two tables.")
    return order


def main(argv):
    a = argparse.ArgumentParser()
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--seat")
    g.add_argument("--table")
    g.add_argument("--seats")
    a = a.parse_args(argv)
    if a.list:
        for n, s in enumerate(SNAP["seats"], 1):
            print(line(n, s))
        return 0
    if a.seat:
        if a.seat not in SEATS:
            sys.exit(f"refused: unknown seat {a.seat!r}; run --list for the 15 seat ids")
        s = SEATS[a.seat]
        print(line(1, s))
        print(f"   does not own: {s['does_not_own']}\n   reports to: {s['reports_to']}")
    else:
        if a.table:
            tables = {t["id"]: t for t in SNAP["round_tables"]}
            if a.table not in tables:
                sys.exit(f"refused: unknown table {a.table!r}; configured: {', '.join(tables)}")
            ids = tables[a.table]["members"]
        else:
            ids = [x.strip() for x in a.seats.split(",") if x.strip()]
        for n, i in enumerate(roster(ids), 1):
            print(line(n, SEATS[i], chair=(i == CHAIR)))
    print("Needs the founder, never decided by a seat: " + "; ".join(SNAP["always_ask_founder"]) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
