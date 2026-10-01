# pmcro-content

Content creation for the PMCR-O company: scripts in the founder's own voice, with sourced claims and guardrails for synthetic voice and image.

## Skills

| Skill | Use it to |
| --- | --- |
| `content-script` | Write a video, podcast or short-form script from a template, fill a Claims table, add a disclosure line when synthetic media is used, and check structure with `scripts/check_script.py`. |

## Ghostwriter

This plugin is phase 1 of the Ghostwriter product line (`docs/product/ghostwriter.md`, ADR 0017): scripts now, lyrics later, voice only under signed licences.

## Pipeline (proposed, ADR 0010)

Script (this plugin) -> voice (founder's own, local) -> recording and editing in existing tools (OBS Studio, ffmpeg or an editor of your choice) -> founder approves and publishes. Only the first step is built. We do not build editing software.

## Install

```
/plugin install pmcro-content@pmcro-plugins
```

## Status

CANDIDATE. The checker is tested (structure only; it cannot tell whether a claim is true). Training a voice model, image generation and any text-to-speech tool are NOT built or tested here; model choice and licenses are OPEN. Rules for consent, local-only training and disclosure are in `skills/content-script/references/disclosure-and-consent.md` and ADR 0008. Not legal advice.
