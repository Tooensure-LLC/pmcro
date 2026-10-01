# pmcro-capture

Turn a captured demonstration (screenshots or photos plus notes) into a draft skill, with private metadata stripped and a human review gate.

## Skills

| Skill | Use it to |
| --- | --- |
| `capture-to-skill` | Turn screenshots or photos plus short notes into a draft Agent Skill, with private metadata stripped and a human review gate (`scripts/draft_skill.py`). |

## Install

```
/plugin install pmcro-capture@pmcro-plugins
```

## Status

CANDIDATE. `draft_skill.py` is tested, including metadata stripping on a JPEG carrying an Exif block and a PNG with text chunks, refusal without human confirmation, and refusal of unparsable or non-image files. NOT built: any live recorder, OCR, or vision step; the steps in a draft are never run or verified. A human must review every image; the script cannot see what is in the pixels. See ADR 0019 and `docs/product/everything-as-agent.md`.
