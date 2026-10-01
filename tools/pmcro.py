#!/usr/bin/env python3
"""PMCR-O plugin tooling.

  python tools/pmcro.py validate     check plugins, skills and adapters (CI gate)
  python tools/pmcro.py gen          regenerate vendor adapters from plugins/*/plugin.json
  python tools/pmcro.py gen --check  fail if generated files differ (never writes)

Source of truth: plugins/<name>/plugin.json and plugins/<name>/skills/*/SKILL.md.
Everything under .claude-plugin/, .cursor-plugin/, .codex-plugin/, .github/plugin/ and
.agents/plugins/ is generated and disposable.
"""
import json, pathlib, re, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
MARKETPLACE = "pmcro-plugins"
OWNER = {"name": "PMCR-O"}
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
# Official/impersonating names are refused by hosts; never use them.
RESERVED = re.compile(r"claude|anthropic|grok|copilot|codex|agent-skills|agentskills", re.I)
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY")
ABS_PATH = re.compile(r"(?<![\w.])(/home/|/root/|/Users/|[A-Z]:\\\\)")
LINK = re.compile(r"`((?:references|scripts|assets)/[^`\s]+)`|\]\(((?:references|scripts|assets)/[^)\s]+)\)")


def plugin_dirs():
    return sorted(p for p in PLUGINS.iterdir() if (p / "plugin.json").is_file())


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (yaml.safe_load(m.group(1)), text[m.end():]) if m else (None, text)


def check_skill(d, errors):
    f = d / "SKILL.md"
    where = f.relative_to(ROOT)
    if not f.is_file():
        errors.append(f"{where}: missing")
        return
    text = f.read_text()
    fm, body = split_frontmatter(text)
    if not isinstance(fm, dict):
        errors.append(f"{where}: no YAML frontmatter")
        return
    extra = set(fm) - SPEC_KEYS
    if extra:
        errors.append(f"{where}: non-spec frontmatter keys {sorted(extra)}")
    name, desc = fm.get("name"), fm.get("description")
    if name != d.name:
        errors.append(f"{where}: name {name!r} must equal directory {d.name!r}")
    if not isinstance(name, str) or not (1 <= len(name) <= 64) or not NAME_RE.match(name):
        errors.append(f"{where}: invalid name")
    if not isinstance(desc, str) or not (1 <= len(desc) <= 1024):
        errors.append(f"{where}: description must be 1-1024 chars")
    if "metadata" in fm and not (isinstance(fm["metadata"], dict) and all(isinstance(v, str) for v in fm["metadata"].values())):
        errors.append(f"{where}: metadata must be a string map")
    n = text.count("\n") + 1
    if n > 500:
        errors.append(f"{where}: {n} lines, limit 500")
    if SECRET.search(text):
        errors.append(f"{where}: credential-shaped text")
    for ref in {a or b for a, b in LINK.findall(body)}:
        if any(c in ref for c in "<>*"):  # placeholder in prose, not a link
            continue
        if ".." in ref or not (d / ref).is_file():
            errors.append(f"{where}: referenced file {ref} missing or outside skill")
    for sub in ("references", "scripts", "assets"):
        base = d / sub
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_symlink():
                    errors.append(f"{p.relative_to(ROOT)}: symlink not allowed")
                if p.is_file() and not p.is_symlink() and sub == "references" and len(p.relative_to(base).parts) > 1:
                    errors.append(f"{p.relative_to(ROOT)}: references must be one level deep")
                if p.is_file() and p.suffix in {".md", ".py", ".json", ".txt", ".yaml", ".yml"}:
                    t = p.read_text(errors="ignore")
                    if SECRET.search(t):
                        errors.append(f"{p.relative_to(ROOT)}: credential-shaped text")
                    if ABS_PATH.search(t):
                        errors.append(f"{p.relative_to(ROOT)}: absolute path")


def load_plugin(p, errors):
    where = (p / "plugin.json").relative_to(ROOT)
    try:
        m = json.loads((p / "plugin.json").read_text())
    except json.JSONDecodeError as e:
        errors.append(f"{where}: invalid JSON ({e})")
        return None
    if m.get("$schema") != SCHEMA:
        errors.append(f"{where}: $schema must be {SCHEMA}")
    if m.get("name") != p.name or not NAME_RE.match(str(m.get("name", ""))):
        errors.append(f"{where}: name must equal directory {p.name!r}")
    if RESERVED.search(str(m.get("name", ""))):
        errors.append(f"{where}: reserved or impersonating name")
    if not SEMVER.match(str(m.get("version", ""))):
        errors.append(f"{where}: version must be explicit semver")
    if not m.get("description"):
        errors.append(f"{where}: description required")
    for s in m.get("skills", []):
        if not s.startswith("./") or ".." in s or not (p / s).is_dir():
            errors.append(f"{where}: skills path {s!r} must start with ./ and exist inside the plugin")
    return m


def generated():
    """Return {relative path: content} for every generated file."""
    out = {}
    entries = []
    for p in plugin_dirs():
        m = json.loads((p / "plugin.json").read_text())
        rel = f"plugins/{p.name}"
        entries.append({"name": m["name"], "source": f"./{rel}", "description": m["description"]})
        claude = {k: v for k, v in m.items() if k != "$schema"}  # Claude strips unknown keys with a warning
        for sub in (".claude-plugin", ".cursor-plugin", ".codex-plugin"):
            out[f"{rel}/{sub}/plugin.json"] = json.dumps(claude, indent=2) + "\n"
    market = json.dumps({"name": MARKETPLACE, "owner": OWNER, "plugins": entries}, indent=2) + "\n"
    for path in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json", ".github/plugin/marketplace.json"):
        out[path] = market
    # Codex layout is from secondary sources; unverified. Keep it identical in shape until checked.
    out[".agents/plugins/marketplace.json"] = market
    return out


def cmd_gen(check):
    bad = []
    for rel, content in generated().items():
        path = ROOT / rel
        if check:
            if not path.is_file() or path.read_text() != content:
                bad.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if check and bad:
        print("generated files out of date (run: python tools/pmcro.py gen):\n  " + "\n  ".join(bad))
        return 1
    print("adapters up to date" if check else f"wrote {len(generated())} files")
    return 0


def cmd_validate():
    errors = []
    names = set()
    for p in plugin_dirs():
        m = load_plugin(p, errors)
        if m:
            names.add(m["name"])
        for sk in sorted((p / "skills").iterdir()) if (p / "skills").is_dir() else []:
            if sk.is_dir():
                check_skill(sk, errors)
    if RESERVED.search(MARKETPLACE):
        errors.append("marketplace name is reserved or impersonating")
    for e in errors:
        print("ERROR", e)
    if errors:
        return 1
    rc = cmd_gen(check=True)
    if rc == 0:
        print(f"ok: {len(names)} plugins validated")
    return rc


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["validate"]:
        sys.exit(cmd_validate())
    if a[:1] == ["gen"]:
        sys.exit(cmd_gen("--check" in a))
    sys.exit(__doc__)
