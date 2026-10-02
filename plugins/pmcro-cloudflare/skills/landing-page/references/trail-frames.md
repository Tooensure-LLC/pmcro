# Trail frames for site setup

Record every step so the work can be replayed, audited and costed. One frame per step. Use the trail player from `pmcro-core` with the `company` tier (never `private`):

```
python <pmcro-core trail-player dir>/scripts/record.py --tier company --kind decision --body-file step.txt --summary "landing page: disclosure added" --cost-tokens 1800 --cost-usd 0.0
```

| Step | Kind | Body should say |
| --- | --- | --- |
| Brief | goal | offer, audience, what the page must not claim |
| Draft | note | what was written, which claims have sources |
| Check | note | checker output verbatim, errors fixed |
| Dry run | note | the dry-run command and output |
| Approval | decision | who approved, when (the human writes this) |
| Deploy | decision | written by the human after they deploy |
| Result | note | measured outcome later (visits, clicks, revenue, cost) |

## Rules

- Include cost on every frame where you know it: tokens, model, seconds, dollars. Unknown cost is left blank, never invented.
- Frames are append-only: a correction is a new frame referencing the old (`--refs`).
- Only a human writes the Approval and Deploy frames.
- Revenue and cost frames are what the economic gates read; they flag poor results for a human and never act on their own.
