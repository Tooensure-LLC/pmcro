#!/usr/bin/env python3
"""Prove the dotagents convention can consume this repo (needs network and npx; not part of unit tests).

  python tools/dotagents_smoke.py [--ref <branch|tag|commit>] [--source owner/repo]
Creates a scratch project in a temp dir, runs `@sentry/dotagents@3.2.0` init, add --all, doctor and
list, and checks every plugin under plugins/ was installed and locked to a full commit.
Output: one "ok: ..." line per check, exit 0; or "FAIL: ..." and exit 1. Makes no model calls.
"""
import argparse, pathlib, re, subprocess, sys, tempfile

PKG = "@sentry/dotagents@3.2.0"  # pinned: the version the docs were verified against
ROOT = pathlib.Path(__file__).resolve().parent.parent


def run(cwd, *args, timeout=300):
    r = subprocess.run(["npx", "--yes", PKG, "--project", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--ref", default="main")
    a.add_argument("--source", default="Tooensure-LLC/pmcro")
    a = a.parse_args()
    expected = sorted(p.name for p in (ROOT / "plugins").iterdir() if (p / "plugin.json").is_file())
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", d], check=True)
        for step in (("init", "--agents", "claude,codex,cursor"), ("add", a.source, "--ref", a.ref, "--all")):
            rc, out = run(d, *step)
            if rc:
                sys.exit(f"FAIL: dotagents {step[0]} exited {rc}\n{out}")
            print(f"ok: dotagents {step[0]}")
        lock = (pathlib.Path(d) / "agents.lock").read_text()
        for name in expected:
            if f"[plugins.{name}]" not in lock:
                sys.exit(f"FAIL: plugin {name} missing from agents.lock")
            if not (pathlib.Path(d) / ".agents/plugins" / name / "plugin.json").is_file():
                sys.exit(f"FAIL: plugin {name} not installed under .agents/plugins")
        if not re.findall(r'resolved_commit = "[0-9a-f]{40}"', lock):
            sys.exit("FAIL: no full resolved_commit in agents.lock")
        print(f"ok: {len(expected)} plugins installed and locked: {', '.join(expected)}")
        rc, out = run(d, "doctor")
        if rc:
            sys.exit(f"FAIL: doctor exited {rc}\n{out}")
        print("ok: doctor passed")


if __name__ == "__main__":
    main()
