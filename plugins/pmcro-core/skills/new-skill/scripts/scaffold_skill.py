#!/usr/bin/env python3
"""Create a new skill inside an existing plugin, already in the templated shape (SKILL.md, references/, scripts/, assets/).

  python scaffold_skill.py --plugin pmcro-core --name my-skill --description "Use when ..." [--plugins-dir plugins]
Writes plugins/<plugin>/skills/<name>/ from assets/templates/ (the single source for the shape of every skill here) and adds the
skill to the plugin README's Skills table. It does not bump the plugin version: add a CHANGELOG entry and bump plugin.json yourself.
Refuses: a missing plugin, a name that is not kebab-case, a description over 1024 characters, a skill that already exists.
Output: "created PATH; ..." or "refused: ..." with exit 1. The text it writes still carries TODO markers to fill before committing.
"""
import argparse, json, pathlib, re, sys

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FILES = [("SKILL.md.tmpl", "SKILL.md"), ("design.md.tmpl", "references/design.md"), ("run.py.tmpl", "scripts/run.py"),
         ("output.md.tmpl.tmpl", "assets/templates/output.md.tmpl")]


class Refused(Exception):
    pass


def scaffold(plugins_dir, plugin, name, description):
    plugin_dir = pathlib.Path(plugins_dir) / plugin
    if not (plugin_dir / "plugin.json").is_file():
        raise Refused(f"no plugin {plugin!r} under {plugins_dir}; create a plugin first (python tools/pmcro.py new-plugin)")
    if not NAME_RE.match(name) or len(name) > 64:
        raise Refused("skill name must be kebab-case, at most 64 characters")
    if not 1 <= len(description) <= 1024:
        raise Refused("description must be 1 to 1024 characters")
    dest = plugin_dir / "skills" / name
    if dest.exists():
        raise Refused(f"{dest} already exists")
    for tmpl, rel in FILES:
        text = (TEMPLATES / tmpl).read_text().replace("{{name}}", name).replace("{{description_json}}", json.dumps(description))
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    readme = plugin_dir / "README.md"
    if readme.is_file():
        lines = readme.read_text().split("\n")
        row = f"| `{name}` | {description[:120]} |"
        try:
            i = lines.index("## Skills")
            j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("|"))
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            lines.insert(j, row)
            readme.write_text("\n".join(lines))
        except (ValueError, StopIteration):
            raise Refused("created the skill but could not find the Skills table in the README; add the row by hand")
    return dest


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--plugin", required=True); p.add_argument("--name", required=True)
    p.add_argument("--description", required=True); p.add_argument("--plugins-dir", default="plugins")
    a = p.parse_args(argv)
    try:
        dest = scaffold(a.plugins_dir, a.plugin, a.name, a.description)
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    print(f"created {dest}; fill every TODO, add a CHANGELOG entry and bump the plugin version, then run: python tools/pmcro.py validate")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
