"""Check the docs site's brand colors against WCAG 2.1 AA contrast (ADR 0033).

Usage: python tools/site_contrast.py [css]    prints every pair; exits 1 if any pair is below its threshold
                                              or if a CSS rule no longer sets the listed foreground or background
Both colors of every pair are bound to the CSS rule and property that sets them in
site/templates/pmcro/public/main.css, so changing a color, a token, or the rule that uses it fails CI until
this list is updated and re-measured. Each pair is measured against every color in its background declaration
(all gradient stops, named or not), and the worst one decides (ADR 0034). #RRGGBB, #RGB, opaque rgb() and hsl()
are measured; a background color it cannot measure (named colors, transparency) fails the check (ADR 0035).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "site" / "templates" / "pmcro" / "public" / "main.css"

TEXT, UI = 4.5, 3.0  # WCAG 2.1 AA: normal text 4.5:1 (1.4.3); non-text UI parts 3:1 (1.4.11)

# Each pair binds BOTH colors to the CSS that sets them: (selector, property) for the foreground and for the
# background, exactly as written in main.css. var(--pm-*) tokens are resolved, including tokens inside tokens
# (the button gradient), so changing a color, a token, or the rule that uses it fails the check (ADR 0033).
LIGHT, DARK = '[data-bs-theme="light"]', '[data-bs-theme="dark"]'
HERO = (".pm-hero", "background")
GRADIENT = (".pm-btn-primary", "background")
PAIRS = [
    ("light link", (LIGHT, "--bs-link-color-rgb"), "#B01D70", (LIGHT, "--bs-body-bg"), "#FFFFFF", TEXT),
    ("light link hover", (LIGHT, "--bs-link-hover-color-rgb"), "#B04A10", (LIGHT, "--bs-body-bg"), "#FFFFFF", TEXT),
    ("light body text", (LIGHT, "--bs-body-color"), "#1A1A2E", (LIGHT, "--bs-body-bg"), "#FFFFFF", TEXT),
    ("light role step label on card", (".pm-role .pm-step", "color"), "#B01D70", (LIGHT, "--bs-tertiary-bg"), "#F8F9FA", TEXT),
    ("dark link", (DARK, "--bs-link-color-rgb"), "#FFA064", (DARK, "--bs-body-bg"), "#0B1026", TEXT),
    ("dark link hover", (DARK, "--bs-link-hover-color-rgb"), "#FF78B4", (DARK, "--bs-body-bg"), "#0B1026", TEXT),
    ("dark code text on block", (DARK + " article pre > code", "color"), "#F5F1FF", (DARK, "--bs-tertiary-bg"), "#12173A", TEXT),
    ("dark role step label on card", (DARK + " .pm-role .pm-step", "color"), "#FFC24B", (DARK, "--bs-tertiary-bg"), "#12173A", TEXT),
    ("hero tagline on hero (lightest stop)", (".pm-hero .pm-tag", "color"), "#CFCBE8", HERO, "#1B1F4A", TEXT),
    ("primary button text on orange stop", (".pm-btn-primary", "color"), "#0B1026", GRADIENT, "#FF8A3D", TEXT),
    ("primary button text on coral stop", (".pm-btn-primary", "color"), "#0B1026", GRADIENT, "#FF5C7A", TEXT),
    ("primary button text on magenta stop", (".pm-btn-primary", "color"), "#0B1026", GRADIENT, "#E0389A", TEXT),
    ("ghost button text on hero", (".pm-btn-ghost", "color"), "#FFD9C2", HERO, "#1B1F4A", TEXT),
    ("ghost button border on hero", (".pm-btn-ghost", "border"), "#FF8A3D", HERO, "#1B1F4A", UI),
    ("focus ring on hero", (".pm-btn:focus-visible", "outline"), "#FFC24B", HERO, "#1B1F4A", UI),
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


def resolve(value, tokens):
    """Replace var(--pm-*) references with their :root values, repeating so tokens inside tokens resolve too."""
    for _ in range(5):
        new = re.sub(r"var\((--pm-[\w-]+)\)", lambda m: tokens.get(m.group(1), m.group(0)), value)
        if new == value:
            break
        value = new
    return value


def sets_color(value, hex_color, tokens):
    """True when a declared value (hex, rgb triple, or var(--pm-*) token, resolved) contains the given color."""
    value = resolve(value, tokens)
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


# Words that may appear in a background declaration without being colors (gradient syntax and units).
NON_COLOR_WORDS = {
    "linear-gradient", "radial-gradient", "conic-gradient", "repeating-linear-gradient",
    "repeating-radial-gradient", "ellipse", "circle", "at", "to", "from", "in", "left", "right", "top",
    "bottom", "center", "closest-side", "closest-corner", "farthest-side", "farthest-corner", "deg", "turn",
    "rad", "grad", "px", "em", "rem", "vw", "vh", "srgb", "oklab", "none", "important",
}


def _hex6(r, g, b):
    """Format 0-255 channels as #RRGGBB."""
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in (r, g, b)))


def _hsl_to_hex(h, s, l):
    """Convert CSS hsl (degrees, percent, percent) to #RRGGBB with the standard library."""
    import colorsys
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l / 100, s / 100)
    return _hex6(r * 255, g * 255, b * 255)


def surface_colors(value, tokens):
    """Return (colors, unmeasurable) for a resolved background declaration (all stops of a gradient).

    colors: every color found, normalised to #RRGGBB, without repeats. #RRGGBB, #RGB, opaque rgb()/rgba() and
    hsl()/hsla() are measured. unmeasurable: anything color-like that cannot be measured as an opaque sRGB
    color (named colors, alpha below 1, #RGBA/#RRGGBBAA, other functions). The check fails closed on those
    instead of skipping them (ADR 0035).
    """
    text = resolve(value, tokens)
    colors, bad = [], []

    def add(c):
        if c not in colors:
            colors.append(c)

    def alpha_ok(a):
        a = a.strip()
        return float(a[:-1]) / 100 >= 1 if a.endswith("%") else float(a) >= 1

    for m in re.finditer(r"(rgba?|hsla?)\(([^)]*)\)", text, re.IGNORECASE):
        fn, parts = m.group(1).lower(), [p for p in re.split(r"[\s,/]+", m.group(2).strip()) if p]
        try:
            if len(parts) == 4 and not alpha_ok(parts[3]):
                bad.append(m.group(0))
            elif fn.startswith("rgb"):
                ch = [float(p[:-1]) * 2.55 if p.endswith("%") else float(p) for p in parts[:3]]
                add(_hex6(*ch))
            else:
                add(_hsl_to_hex(float(parts[0].rstrip("deg")), float(parts[1].rstrip("%")), float(parts[2].rstrip("%"))))
        except (ValueError, IndexError):
            bad.append(m.group(0))
    text = re.sub(r"(rgba?|hsla?)\([^)]*\)", " ", text, flags=re.IGNORECASE)
    for m in re.finditer(r"#([0-9A-Fa-f]+)\b", text):
        h = m.group(1)
        if len(h) == 6:
            add("#" + h.upper())
        elif len(h) == 3:
            add("#" + "".join(c * 2 for c in h).upper())
        else:
            bad.append(m.group(0))
    text = re.sub(r"#[0-9A-Fa-f]+\b", " ", text)
    text = re.sub(r"var\([^)]*\)", lambda m: bad.append(m.group(0)) or " ", text)
    for word in re.findall(r"[A-Za-z][A-Za-z-]*", text):
        if word.lower() not in NON_COLOR_WORDS:
            bad.append(word)
    return colors, bad


def main(argv):
    """Print each pair's worst-case ratio and verdict; return 1 on any contrast failure or unbound color."""
    css_path = Path(argv[1]) if len(argv) > 1 else CSS
    rules = parse_rules(css_path.read_text(encoding="utf-8"))
    tokens = {k: v for k, v in rules.get(":root", {}).items() if k.startswith("--pm-")}
    failures = 0
    for name, (fg_sel, fg_prop), fg, (bg_sel, bg_prop), bg, need in PAIRS:
        notes = []
        for sel, prop, color in ((fg_sel, fg_prop, fg), (bg_sel, bg_prop, bg)):
            declared = rules.get(sel, {}).get(prop)
            if declared is None or not sets_color(declared, color, tokens):
                notes.append(f"NOT SET: {sel} {{ {prop} }} is {declared!r}, expected {color}")
        # Judge the foreground against every color the background really contains (ADR 0034): a gradient is
        # only as readable as its worst stop, including stops this list does not name.
        declared_bg = rules.get(bg_sel, {}).get(bg_prop) or bg
        stops, unmeasurable = surface_colors(declared_bg, tokens)
        stops = stops or [bg.upper()]
        if unmeasurable:
            notes.append(f"UNMEASURABLE in {bg_sel} {{ {bg_prop} }}: {', '.join(unmeasurable)}")
        worst_stop = min(stops, key=lambda s: ratio(fg, s))
        r = ratio(fg, worst_stop)
        ok = r >= need and not notes
        failures += not ok
        where = f" (worst stop {worst_stop} of {len(stops)})" if len(stops) > 1 else ""
        note = ("  " + "; ".join(notes)) if notes else ""
        print(f"{'PASS' if ok else 'FAIL'}  {r:5.2f}:1 (need {need})  {name}  {fg} on {bg}{where}{note}")
    print(f"{len(PAIRS) - failures}/{len(PAIRS)} pairs pass WCAG 2.1 AA on every background stop, both colors set by their CSS rules")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
