#!/usr/bin/env python3
"""Accept or deny a request to this skill against its input shape (assets/templates/input.md.tmpl).

  python check_input.py [FILE]        reads the request from FILE, or from standard input
Prints ACCEPT (exit 0) when every required field has text. Otherwise prints DENY (exit 2) and then the shape, with everything the
request did supply filled in and each missing required field marked <missing>, so the request can be corrected and passed back.
A field is a line "NAME: text"; text may continue on following lines until the next field. This script only checks the shape:
it does not understand the request, so a model or a person fills in the missing fields.
"""
import pathlib, re, sys

SHAPE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates" / "input.md.tmpl"
FIELD = re.compile(r"^([A-Z][A-Z ]*[A-Z]):\s*(.*)$")


def read_shape():
    fields = []
    for line in SHAPE.read_text().splitlines():
        m = FIELD.match(line)
        if m and not line.startswith("#"):
            fields.append((m.group(1), m.group(2), "(optional)" in m.group(2)))
    return fields


def parse(text, names):
    got, cur = {}, None
    for line in text.splitlines():
        m = FIELD.match(line)
        if m and m.group(1) in names:
            cur = m.group(1)
            got[cur] = m.group(2).strip()
        elif cur and line.strip():
            got[cur] = (got[cur] + " " + line.strip()).strip()
    return got


def main(argv):
    shape = read_shape()
    text = pathlib.Path(argv[0]).read_text() if argv else sys.stdin.read()
    got = parse(text, {n for n, _, _ in shape})
    missing = [n for n, _, optional in shape if not optional and not got.get(n)]
    if not missing:
        print("ACCEPT")
        return 0
    print(f"DENY: missing {', '.join(missing)}. Fill the shape below and pass it back.\n")
    for name, hint, optional in shape:
        value = got.get(name) or ("<missing>" if not optional else "")
        print(f"{name}: {value if value else hint}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
