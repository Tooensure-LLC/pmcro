# 0033: Docs site brand colors meet WCAG 2.1 AA contrast, checked in CI

Date: 2026-10-02. Status: built; see Consequences for what was and was not tested. Taken autonomously under the founder's "continue autonomously" for a production-grade site (ADRs 0031, 0032).

## Context

A measurement of the site's brand colors with the WCAG 2.x relative-luminance formula found five text pairs below AA (4.5:1 for normal text):

| Pair | Before | After |
| --- | --- | --- |
| Light-mode link hover `#D65C16` on white | 3.89 | `#B04A10`: 5.48 |
| Light-mode role step label, brand magenta `#E0389A` on `#F8F9FA` | 3.83 | `#B01D70`: 6.12 |
| "Browse the plugins" button, white on the gradient's orange, coral and magenta stops | 2.35 / 2.97 / 4.04 | navy `#0B1026`: 8.02 / 6.33 / 4.66 |

The button label is 16px bold, which is not "large text" under WCAG, so 4.5:1 applies.

## Decision

- Fix the three colors above. The brand magenta and the gradient itself are unchanged; only text on them changed.
- `tools/site_contrast.py` lists 15 brand pairs (13 text at 4.5:1, 2 non-text UI at 3:1), each bound to the CSS rule and property that sets its foreground. It exits 1 when a pair is below its threshold or when that rule no longer sets the listed color (it resolves `var(--pm-*)` tokens). CI's `docs-site` job runs it.
- The first version of the script only required each color to appear somewhere in the CSS. Its own before-fix run showed that was too weak: it passed the white-on-gradient button because navy appears elsewhere in the file. Binding each pair to its rule fixed that (recorded in the pull request).

## Consequences

- Changing a brand color, or the rule that sets it, now fails CI until the pair list is updated and re-measured.
- Tested: the script's before-fix run (exit 1, the five pairs above), after-fix run (exit 0, 15/15), and two mutants (button text back to white, link hover reverted), both exit 1.
- Not tested: contrast of docfx's own built-in colors outside this brand layer, text drawn inside the SVG art, color-blindness simulation, screen readers, and any WCAG criterion other than 1.4.3 and 1.4.11. This is not a full accessibility audit.
