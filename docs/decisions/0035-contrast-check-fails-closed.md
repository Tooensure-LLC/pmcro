# 0035: The contrast check measures every CSS color notation it can and fails closed on the rest

Date: 2026-10-02. Status: built; see Consequences. Taken autonomously ("continue entire complete"), from the Trail 0034 Checker's observation.

## Context

After ADR 0034 the check measured every `#RRGGBB` stop in a background. A stop written another way (`#CCC`, `white`, `rgb(200, 200, 230)`) was not collected at all, so an unreadable background could pass silently.

## Decision

- **Measured:** `#RRGGBB`, `#RGB`, opaque `rgb()` and `rgba()` (alpha 1), and `hsl()` and `hsla()`. hsl uses the standard library's `colorsys`. Each color is normalised to `#RRGGBB` and enters the worst-stop calculation.
- **Fail closed:** any other color-like token in a bound background is reported as `UNMEASURABLE` and fails the pair, rather than being skipped. That covers named colors (`white`, `black`), alpha below 1 (`rgba(…, 0.5)`, `#RRGGBBAA`), and unresolved `var()`. A named color fails even when it would be readable, because the check cannot measure it without a name table. Write it as hex instead.
- Gradient syntax words (`radial-gradient`, `ellipse`, `at`, units and similar) are on an allow-list and are not treated as colors.

## Consequences

- The site's committed CSS is unchanged and still passes 15 of 15.
- Tested with 13 mutants of the hero's dark stop, each exit code captured directly:
  - light `#CCC`, `rgb(200,200,230)` and `hsl(230,30%,80%)` exit 1 on contrast;
  - `white`, `black`, `rgba(…,0.5)` and `#05071A80` exit 1 as UNMEASURABLE;
  - dark `#000`, `rgb(0,0,0)`, `hsl(230,50%,5%)` and `rgba(…,1)` exit 0;
  - 0034's k14 mutant and a foreground mutant still exit 1.
- Not tested: CSS Color 4 spaces (`oklch()`, `lab()`, `color()`). Those are reported as UNMEASURABLE, because the function name is not on the allow-list. Images and `background-image` URLs are not measured.
