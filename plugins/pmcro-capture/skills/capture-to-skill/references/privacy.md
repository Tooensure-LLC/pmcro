# Privacy for captures

Status: company rules (ADR 0019). Not legal advice; recording people and screens is regulated differently in different places.

## What the script strips

- JPEG: Exif (camera, time, GPS location), XMP, Photoshop blocks and comments.
- PNG: text chunks (`tEXt`, `zTXt`, `iTXt`), Exif and modification time.

## What it cannot do

- It cannot see the picture. A password on a screen, a face, a street sign, a name tag or a document number stays in the pixels. Only a human review catches those; that is why `--confirm-reviewed` exists.
- It handles only PNG and JPEG. Other formats are refused, not copied.
- Stripped metadata does not prove an image is safe to publish.

## Rules

- The images stay on the company's own machine unless the founder decides otherwise. A servable skill (ADR 0016) exposes its images to whoever connects, so never put a capture of anything private into a servable plugin.
- Only the founder's own screens, devices and documents, or ones where the owner has agreed. Never a stranger, a customer or a workplace system without permission.
- Prefer a cropped or redacted image over a full screenshot.

## Not covered

A live recorder (clicks, window titles, OCR) like the old Windows Problem Steps Recorder. That is a different, riskier tool; see `docs/product/everything-as-agent.md` for the conditions it would need.
