# 0034: The contrast check measures every background stop, not only the listed one

Date: 2026-10-02. Status: built; see Consequences. Taken autonomously ("continue entire complete"), from the Trail 0033 reflection (P7) and that cycle's Checker observation k14.

## Context

ADR 0033's `tools/site_contrast.py` bound each pair's background to its CSS rule, but measured contrast against the one stop the list named. The hero background is a three-stop gradient (`#1B1F4A`, the navy token, `#05071A`). Changing the unlisted stop `#05071A` to `#C0C4E8` left the check green, while the hero tagline on that stop would be 1.09:1.

## Decision

- For every pair, the script resolves the background declaration (including nested `var(--pm-*)` tokens), collects every `#RRGGBB` color in it, and reports the **worst** ratio. For a gradient, the worst stop decides, whether or not the list names it. Output shows `(worst stop #XXXXXX of N)`.
- The listed background is still required to be set by its rule (ADR 0033), so a missing or moved declaration still fails.
- No site colors changed. On the committed CSS every pair passes. The button gradient's worst stop is magenta at 4.66:1, and the hero's is `#1B1F4A`.

## Consequences

- Any gradient stop change that makes text unreadable fails CI, including stops nobody listed.
- Tested: 12 mutants built from the current CSS, each exit code captured directly. 11 harmful mutants exit 1:
  - unlisted hero stop;
  - navy token;
  - unlisted-in-role coral stop;
  - orange, magenta, dark tertiary, light body, light tertiary and hero ink stop backgrounds;
  - button text;
  - tagline text.

  One harmless change (a darker `#05071A`) exits 0, so the check does not fail on every edit.
- Not tested: `rgb()`/`hsl()` functions and 3-digit hex inside backgrounds (the site uses only `#RRGGBB`), images, transparency (alpha is not composited; the install box's 6% white overlay is not measured), and docfx's own built-in colors.
