#!/usr/bin/env python3
"""Validate an Agent Skill folder.

Usage: python validate_skill.py <skill-dir>
Exit code 0 if valid, 1 otherwise. Standard library only.
"""
import re
import sys
from pathlib import Path

ALLOWED = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
SKIP_DIRS = {"__pycache__", "node_modules"}
OPTIONAL_DIRS = ("references", "scripts", "assets")


def parse_frontmatter(text):
    """Parse top-level `key: value` pairs; tolerates quotes and indented continuations."""
    m = re.match(r"^---\n(.*?)\n---(\n|$)", text, re.DOTALL)
    if not m:
        return None, None
    data, key = {}, None
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if top and not line.startswith((" ", "\t")):
            key = top.group(1)
            val = top.group(2).strip()
            if len(val) > 1 and val[0] in "\"'" and val[-1] == val[0]:
                val = val[1:-1]
            data[key] = val
        elif key and line.strip():
            data[key] = (data[key] + " " + line.strip()).strip()
    return data, text[m.end():]


def validate(skill_dir):
    errors, warnings = [], []
    root = Path(skill_dir)
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md not found"], warnings

    nested = [p for p in root.rglob("SKILL.md")
              if p != skill_md and not SKIP_DIRS & set(p.relative_to(root).parts)]
    if nested:
        errors.append("Nested SKILL.md files are not allowed: "
                      + ", ".join(str(p.relative_to(root)) for p in nested))

    fm, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm is None:
        return errors + ["Missing or malformed YAML frontmatter (must start and end with ---)"], warnings

    for k in sorted(set(fm) - ALLOWED):
        errors.append(f"Unexpected frontmatter key: {k}")

    name = fm.get("name", "")
    if not name:
        errors.append("Missing 'name'")
    else:
        if (not re.fullmatch(r"[a-z0-9-]+", name) or name.startswith("-")
                or name.endswith("-") or "--" in name):
            errors.append(f"Invalid name '{name}': use kebab-case without leading/trailing/double hyphens")
        if len(name) > 64:
            errors.append(f"Name too long ({len(name)} > 64)")
        if name != root.resolve().name:
            warnings.append(f"Folder name '{root.resolve().name}' differs from name '{name}'")

    desc = fm.get("description", "")
    if not desc:
        errors.append("Missing 'description'")
    else:
        if len(desc) > 1024:
            errors.append(f"Description too long ({len(desc)} > 1024)")
        if "<" in desc or ">" in desc:
            errors.append("Description must not contain angle brackets")
        if len(desc) < 60:
            warnings.append("Description is very short; say what the skill does and when to use it")
        if "use" not in desc.lower():
            warnings.append("Description may not say when to use the skill")

    comp = fm.get("compatibility", "")
    if comp and len(comp) > 500:
        errors.append(f"Compatibility too long ({len(comp)} > 500)")

    lines = body.count("\n")
    if lines > 500:
        warnings.append(f"SKILL.md body is {lines} lines; move detail into references/")

    for d in OPTIONAL_DIRS:
        sub = root / d
        if sub.is_dir():
            files = [p for p in sub.rglob("*")
                     if p.is_file() and not SKIP_DIRS & set(p.parts)]
            if not files:
                warnings.append(f"{d}/ is empty; remove it")
            for f in files:
                rel = f.relative_to(root).as_posix()
                if rel not in body and f.name not in body:
                    warnings.append(f"{rel} is not referenced from SKILL.md")
    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    errors, warnings = validate(sys.argv[1])
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        return 1
    print("Skill is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
