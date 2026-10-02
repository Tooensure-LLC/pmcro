"""Check the docs site's brand colors against WCAG 2.1 AA contrast (ADR 0033).

Usage: python tools/site_contrast.py [css]    prints every pair; exits 1 if any pair is below its threshold
                                              or if its CSS rule no longer sets the listed color
Each pair is bound to the CSS rule and property that sets its foreground in site/templates/pmcro/public/main.css,
so changing a color, or the rule that sets it, fails CI until this list is updated and re-measured.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "site" / "templates" / "pmcro" / "public" / "main.css"

TEXT, UI = 4.5, 3.0  # WCAG 2.1 AA: normal text 4.5:1 (1.4.3); non-text UI parts 3:1 (1.4.11)

# Each pair names the CSS rule (selector, exactly as written in main.css) and the property that sets the
# foreground. The check resolves var(--pm-*) tokens and fails if that rule does not set that color, so a pair
# cannot pass just because the color appears somewhere else in the file. Backgrounds are the measured surface:
# Bootstrap's light defaults (#FFFFFF body, #F8F9FA tertiary) or the site's own navy, ink and gradient stops.
PAIRS = [
    ("light link", '[data-bs-theme="light"]', "--bs-link-color-rgb", "#B01D70", "#FFFFFF", TEXT),
    ("light link hover", '[data-bs-theme="light"]', "--bs-link-hover-color-rgb", "#B04A10", "#FFFFFF", TEXT),
    ("light body text", '[data-bs-theme="light"]', "--bs-body-color", "#1A1A2E", "#FFFFFF", TEXT),
    ("light role step label on card", ".pm-role .pm-step", "color", "#B01D70", "#F8F9FA", TEXT),
    ("dark link", '[data-bs-theme="dark"]', "--bs-link-color-rgb", "#FFA064", "#0B1026", TEXT),
    ("dark link hover", '[data-bs-theme="dark"]', "--bs-link-hover-color-rgb", "#FF78B4", "#0B1026", TEXT),
    ("dark code text on block", '[data-bs-theme="dark"] article pre > code', "color", "#F5F1FF", "#12173A", TEXT),
    ("dark role step label on card", '[data-bs-theme="dark"] .pm-role .pm-step', "color", "#FFC24B", "#12173A", TEXT),
    ("hero tagline on hero (lightest stop)", ".pm-hero .pm-tag", "color", "#CFCBE8", "#1B1F4A", TEXT),
    ("primary button text on orange stop", ".pm-btn-primary", "color", "#0B1026", "#FF8A3D", TEXT),
    ("primary button text on coral stop", ".pm-btn-primary", "color", "#0B1026", "#FF5C7A", TEXT),
    ("primary button text on magenta stop", ".pm-btn-primary", "color", "#0B1026", "#E0389A", TEXT),
    ("ghost button text on hero", ".pm-btn-ghost", "color", "#FFD9C2", "#1B1F4A", TEXT),
    ("ghost button border on hero", ".pm-btn-ghost", "border", "#FF8A3D", "#1B1F4A", UI),
    ("focus ring on hero", ".pm-btn:focus-visible", "outline", "#FFC24B", "#1B1F4A", UI),
]


def parse_rules(css):
    """Return {selector: {property: value}} for every innermost rule; a comma list is split into each selector."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = {}
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        decls = {}
        for part in body.split(";"):
            if ":" in part:
                k, v = part.split(":", 1)
                decls[k.strip()] = v.strip()
        for one in sel.split(","):
            key = " ".join(one.split())
            rules.setdefault(key, {}).update(decls)
    return rules


def sets_color(value, hex_color, tokens):
    """True when a declared value (hex, rgb triple, or var(--pm-*) token) is the given color."""
    for name, token_value in tokens.items():
        value = value.replace(f"var({name})", token_value)
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (re.search(rf"#{h}\b", value, re.IGNORECASE) is not None
            or re.search(rf"^\s*{r},\s*{g},\s*{b}\b", value) is not None)


def luminance(hex_color):
    """WCAG 2.x relative luminance of an sRGB hex color such as #1A2B3C."""
    h = hex_color.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(fg, bg):
    """WCAG contrast ratio between two colors, from 1.0 to 21.0."""
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main(argv):
    """Print each pair with its ratio and verdict; return 1 on any contrast failure or unbound color."""
    css_path = Path(argv[1]) if len(argv) > 1 else CSS
    rules = parse_rules(css_path.read_text(encoding="utf-8"))
    tokens = {k: v for k, v in rules.get(":root", {}).items() if k.startswith("--pm-")}
    failures = 0
    for name, selector, prop, fg, bg, need in PAIRS:
        r = ratio(fg, bg)
        declared = rules.get(selector, {}).get(prop)
        bound = declared is not None and sets_color(declared, fg, tokens)
        ok = r >= need and bound
        failures += not ok
        note = "" if bound else f"  NOT SET: {selector} {{ {prop} }} is {declared!r}, expected {fg}"
        print(f"{'PASS' if ok else 'FAIL'}  {r:5.2f}:1 (need {need})  {name}  {fg} on {bg}{note}")
    print(f"{len(PAIRS) - failures}/{len(PAIRS)} pairs pass WCAG 2.1 AA and are set by their CSS rule")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
