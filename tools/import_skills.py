#!/usr/bin/env python3
"""Import skills from another repo into a plugin, normalizing only the frontmatter.

  python tools/import_skills.py <source skills dir> <plugin name> --from <label> [--only a,b] [--drop agents,commands]

Per skill: strip a UTF-8 BOM; move frontmatter keys outside the Agent Skills spec into
`metadata` as strings (so nothing is lost); add `metadata.imported_from`. The body is copied
byte-for-byte. Per-skill `.claude-plugin/` manifests are skipped (the plugin owns packaging).
Skills with no frontmatter are refused, never guessed at.
"""
import argparse, pathlib, re, shutil, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ["name", "description", "license", "compatibility", "metadata", "allowed-tools"]
ALWAYS_SKIP = {".claude-plugin"}


def normalize(text, label):
    text = text.lstrip("﻿")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        raise ValueError("no YAML frontmatter")
    fm = yaml.safe_load(m.group(1))
    if not isinstance(fm, dict) or "name" not in fm or "description" not in fm:
        raise ValueError("frontmatter lacks name/description")
    meta = {str(k): str(v) for k, v in (fm.get("metadata") or {}).items()}
    for k in [k for k in fm if k not in SPEC]:
        meta[k] = str(fm.pop(k))
    meta["imported_from"] = label
    fm["metadata"] = meta
    ordered = {k: fm[k] for k in SPEC if k in fm}
    head = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=10**6)
    return "---\n" + head + "---\n" + text[m.end():]


def import_skills(src, plugin, label, only=None, drop=()):
    dest_root = ROOT / "plugins" / plugin / "skills"
    done, refused = [], []
    for d in sorted(p for p in pathlib.Path(src).iterdir() if p.is_dir()):
        if only and d.name not in only:
            continue
        f = d / "SKILL.md"
        try:
            out = normalize(f.read_text(encoding="utf-8"), label)
        except (OSError, ValueError) as e:
            refused.append((d.name, str(e)))
            continue
        dest = dest_root / d.name
        shutil.copytree(d, dest, ignore=shutil.ignore_patterns(*ALWAYS_SKIP, *drop), dirs_exist_ok=True)
        (dest / "SKILL.md").write_text(out, encoding="utf-8")
        done.append(d.name)
    return done, refused


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("src"); a.add_argument("plugin"); a.add_argument("--from", dest="label", required=True)
    a.add_argument("--only", default=""); a.add_argument("--drop", default="")
    a = a.parse_args()
    done, refused = import_skills(a.src, a.plugin, a.label, set(filter(None, a.only.split(","))), tuple(filter(None, a.drop.split(","))))
    print("imported:", ", ".join(done) or "none")
    for n, why in refused:
        print(f"refused {n}: {why}")
    sys.exit(1 if refused else 0)
