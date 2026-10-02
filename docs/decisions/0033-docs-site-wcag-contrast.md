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
- `tools/site_contrast.py` lists 15 brand pairs (13 text at 4.5:1, 2 non-text UI at 3:1). **Both** colors of each pair are bound to the CSS rule and property that sets them, resolving `var(--pm-*)` tokens, including tokens inside tokens such as the button gradient. It exits 1 when a pair is below its threshold or when a rule no longer sets the listed foreground or background. CI's `docs-site` job runs it.
- The light theme now declares Bootstrap's `--bs-body-bg: #FFFFFF` and `--bs-tertiary-bg: #F8F9FA` explicitly, so those backgrounds can be bound too. The rendered colors are unchanged.
- The first version of the script only required each color to appear somewhere in the CSS. Its own before-fix run showed that was too weak: it passed the white-on-gradient button because navy appears elsewhere in the file. Binding each pair to its rule fixed that (recorded in the pull request).
- Loop 2 (law EC-009, Loop Until Done). The independent Checker's loop 1 verdict was **LOOP**, defect D1: backgrounds were constants in the script and were never checked against the CSS, so changing a gradient stop, the magenta token or the dark card color left the check green while real contrast fell to 1.95 to 3.19. Loop 2 binds backgrounds as well.

## Consequences

- Changing a brand color, or the rule that sets it, now fails CI until the pair list is updated and re-measured.
- Tested: the script's before-fix run (exit 1, the five pairs above) and after-fix run (exit 0, 15/15). Loop 2 mutants built from the current CSS all exit 1: button text back to white, coral gradient stop changed, magenta token changed, dark card background changed, light body background changed, and hero background changed.
- Not tested: contrast of docfx's own built-in colors outside this brand layer, text drawn inside the SVG art, color-blindness simulation, screen readers, and any WCAG criterion other than 1.4.3 and 1.4.11. This is not a full accessibility audit.
