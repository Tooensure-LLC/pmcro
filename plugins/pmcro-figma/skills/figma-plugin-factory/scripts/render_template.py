#!/usr/bin/env python3
"""Render a Figma plugin template into code.ts and ui.html, with typed, escaped parameters.

  python render_template.py --list
  python render_template.py <template> --out DIR [--set name=value ...]
Templates live in ../assets/templates/<name>/ (template.json, code.ts.tmpl, ui.html.tmpl). Placeholders:
{{param|int}} (validated integer), {{param|js}} (a JS string literal, safe against quote and </script>
breakout), {{param|js_comment}} (single-line, no comment terminators), {{param|html}} (HTML-attribute safe).
Every int param also exposes {{param_min|int}} and {{param_max|int}}. Values are validated against
template.json (type, min, max, max_length); an unknown or invalid value is refused, never guessed.
Output: writes code.ts and ui.html into DIR and prints "rendered <template> -> DIR"; "refused: ..." and exit 1 otherwise.
It does not run Figma and cannot prove the plugin works there; run lint_plugin.py next.
"""
import argparse, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates"
PLACEHOLDER = re.compile(r"\{\{\s*([a-z_0-9]+)\s*\|\s*([a-z_]+)\s*\}\}")


def load(name):
    d = ROOT / name
    if not (d / "template.json").is_file():
        sys.exit(f"refused: unknown template {name!r}; try --list")
    return d, json.loads((d / "template.json").read_text())


def coerce(spec, raw):
    t = spec["type"]
    if t == "int":
        try:
            v = int(raw)
        except (TypeError, ValueError):
            sys.exit(f"refused: {spec['name']} must be an integer, got {raw!r}")
        if not spec.get("min", v) <= v <= spec.get("max", v):
            sys.exit(f"refused: {spec['name']}={v} outside {spec.get('min')}..{spec.get('max')}")
        return v
    s = str(raw)
    if len(s) > spec.get("max_length", 200):
        sys.exit(f"refused: {spec['name']} longer than {spec.get('max_length', 200)} characters")
    if "\n" in s or "\r" in s:
        sys.exit(f"refused: {spec['name']} must be a single line")
    return s


def values(meta, given):
    specs = {p["name"]: p for p in meta["params"]}
    for k in given:
        if k not in specs:
            sys.exit(f"refused: unknown parameter {k!r}; known: {', '.join(specs)}")
    out = {}
    for name, spec in specs.items():
        out[name] = coerce(spec, given.get(name, spec["default"]))
        if spec["type"] == "int":
            out[name + "_min"], out[name + "_max"] = spec.get("min", out[name]), spec.get("max", out[name])
    return out


def fmt(value, how):
    if how == "int":
        return str(int(value))
    if how == "js":
        return json.dumps(str(value)).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    if how == "js_comment":
        return re.sub(r"[\r\n*/]", " ", str(value))
    if how == "html":
        return html.escape(str(value), quote=True)
    sys.exit(f"refused: unknown filter {how!r}")


def render(text, vals):
    def sub(m):
        if m.group(1) not in vals:
            sys.exit(f"refused: template uses unknown parameter {m.group(1)!r}")
        return fmt(vals[m.group(1)], m.group(2))
    return PLACEHOLDER.sub(sub, text)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("template", nargs="?"); a.add_argument("--out"); a.add_argument("--list", action="store_true")
    a.add_argument("--set", action="append", default=[])
    a = a.parse_args()
    if a.list:
        for d in sorted(ROOT.iterdir()):
            if (d / "template.json").is_file():
                print(f"{d.name}: {json.loads((d / 'template.json').read_text())['description']}")
        return
    if not a.template or not a.out:
        sys.exit("refused: need a template name and --out DIR (or --list)")
    d, meta = load(a.template)
    given = dict(s.split("=", 1) for s in a.set if "=" in s)
    vals = values(meta, given)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for f in ("code.ts", "ui.html"):
        (out / f).write_text(render((d / (f + ".tmpl")).read_text(), vals))
    print(f"rendered {a.template} -> {a.out}")


if __name__ == "__main__":
    main()
