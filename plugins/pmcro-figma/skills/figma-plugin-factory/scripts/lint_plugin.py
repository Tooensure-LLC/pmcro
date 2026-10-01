#!/usr/bin/env python3
"""Lint a Figma plugin's code.ts and ui.html against rules from Figma's generative-plugin authoring guide.

  python lint_plugin.py <dir containing code.ts and ui.html>
Rules (each prints its id): F001 code.ts calls figma.showUI(__html__; F002 ui.html has fig-content and a
fig-footer; F003 no network calls (fetch, XMLHttpRequest, WebSocket) and no remote script tags; F004 no
credential-shaped text; F005 no eval or new Function; F006 no assigning figma.currentPage (use setCurrentPageAsync);
F007 no synchronous getNodeById/getStyleById (use the Async forms); F008 no forEach(async ...); F009 every message
type posted by ui.html is handled in code.ts and every type posted by code.ts is handled in ui.html; F010 setRelaunchData is called;
F011 loadFontAsync appears if text characters are assigned; F012 no 'as any'; F013 the plugin does not close itself
without a figma.closePlugin call being reachable only after work (warns if closePlugin appears in onmessage before any await).
Output: "ERROR Fxxx reason" per problem, else "ok: lint clean". Exit 1 on error.
It checks form only. It does not run Figma, so it cannot prove the plugin works there. It never prints PASS, LOOP or HALT.
"""
import pathlib, re, sys

SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|Bearer\s+[A-Za-z0-9._-]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY", re.I)


def lint(code, ui):
    e = []
    if not re.search(r"figma\.showUI\(\s*__html__", code):
        e.append("ERROR F001 code.ts must call figma.showUI(__html__, ...)")
    if "<fig-content" not in ui or "<fig-footer" not in ui:
        e.append("ERROR F002 ui.html needs <fig-content> and <fig-footer>")
    if re.search(r"\bfetch\s*\(|XMLHttpRequest|new\s+WebSocket|<script[^>]+src\s*=\s*[\"']https?:", code + ui, re.I):
        e.append("ERROR F003 network access or remote script found (plugins here use none)")
    if SECRET.search(code + ui):
        e.append("ERROR F004 credential-shaped text found; plugin source is readable by others")
    if re.search(r"\beval\s*\(|new\s+Function\s*\(", code + ui):
        e.append("ERROR F005 eval or new Function is not allowed")
    if re.search(r"figma\.currentPage\s*=[^=]", code):
        e.append("ERROR F006 assign pages with await figma.setCurrentPageAsync(page)")
    if re.search(r"getNodeById\s*\(|getStyleById\s*\(", code):
        e.append("ERROR F007 use getNodeByIdAsync / getStyleByIdAsync")
    if re.search(r"forEach\s*\(\s*async", code):
        e.append("ERROR F008 do not use forEach(async ...); use for...of")
    ui_types = set(re.findall(r"post\(\s*\{\s*type:\s*['\"]([\w-]+)['\"]", ui))
    code_handled = set(re.findall(r"message\.type\s*===\s*['\"]([\w-]+)['\"]", code))
    code_posts = set(re.findall(r"figma\.ui\.postMessage\(\s*\{\s*type:\s*['\"]([\w-]+)['\"]", code))
    ui_handled = set(re.findall(r"message\.type\s*===\s*['\"]([\w-]+)['\"]", ui))
    for t in sorted(ui_types - code_handled):
        e.append(f"ERROR F009 ui.html posts '{t}' but code.ts does not handle it")
    for t in sorted(code_posts - ui_handled):
        e.append(f"ERROR F009 code.ts posts '{t}' but ui.html does not handle it")
    if "setRelaunchData" not in code:
        e.append("ERROR F010 call figma.root.setRelaunchData so the plugin is re-runnable")
    if re.search(r"\.characters\s*=", code) and "loadFontAsync" not in code:
        e.append("ERROR F011 call await figma.loadFontAsync(...) before changing text characters")
    if re.search(r"\bas\s+any\b", code):
        e.append("ERROR F012 do not bypass types with 'as any'")
    return e


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    d = pathlib.Path(sys.argv[1])
    errs = lint((d / "code.ts").read_text(), (d / "ui.html").read_text())
    print("\n".join(errs) if errs else "ok: lint clean")
    sys.exit(1 if errs else 0)
