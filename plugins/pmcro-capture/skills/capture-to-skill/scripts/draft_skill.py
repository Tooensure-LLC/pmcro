#!/usr/bin/env python3
"""Draft an Agent Skill from a folder of screenshots or photos plus optional step notes.

  python draft_skill.py <capture_dir> --name NAME --description "..." --out DIR --confirm-reviewed
capture_dir holds .png/.jpg/.jpeg files (sorted by name = step order) and an optional steps.txt (one line per step,
matched to images in order). Writes DIR/NAME/{SKILL.md, assets/stepNN.ext, references/capture-notes.md}.
Safety: private metadata is ALWAYS stripped (JPEG Exif/XMP/comments, which can carry GPS location and device ids;
PNG text, time and Exif chunks). An image that cannot be parsed is refused, not copied. --confirm-reviewed is
required: it states that a human looked at every image and none shows passwords, personal data or other people;
the script cannot detect those. At most 40 images of 5 MB each. The draft is full of TODO markers on purpose and
records that the steps were NOT run.
Output: "drafted NAME: N steps -> DIR/NAME" or "refused: ..." (exit 1). It never records keystrokes or screens itself.
"""
import argparse, datetime, pathlib, re, struct, sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_IMAGES, MAX_BYTES = 40, 5 * 1024 * 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_DROP = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME"}


def strip_jpeg(b):
    if b[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    out, i = bytearray(b"\xff\xd8"), 2
    while i < len(b):
        if b[i] != 0xFF:
            raise ValueError("bad JPEG marker")
        marker = b[i + 1]
        if marker == 0xDA:  # start of scan: the rest is image data
            out += b[i:]
            return bytes(out)
        (length,) = struct.unpack(">H", b[i + 2:i + 4])
        seg = b[i:i + 2 + length]
        if len(seg) != 2 + length:
            raise ValueError("truncated JPEG")
        payload = seg[4:]
        drop = marker == 0xFE or marker == 0xED or (marker == 0xE1 and (payload.startswith(b"Exif") or b"xpacket" in payload[:80] or payload.startswith(b"http://ns.adobe.com")))
        if not drop:
            out += seg
        i += 2 + length
    raise ValueError("JPEG has no image data")


def strip_png(b):
    if b[:8] != PNG_SIG:
        raise ValueError("not a PNG")
    out, i, seen_end = bytearray(PNG_SIG), 8, False
    while i < len(b):
        (n,) = struct.unpack(">I", b[i:i + 4])
        kind, chunk = b[i + 4:i + 8], b[i:i + 12 + n]
        if len(chunk) != 12 + n:
            raise ValueError("truncated PNG")
        if kind not in PNG_DROP:
            out += chunk
        i += 12 + n
        seen_end = seen_end or kind == b"IEND"
    if not seen_end:
        raise ValueError("PNG has no IEND")
    return bytes(out)


def clean(path):
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"larger than {MAX_BYTES // 1024 // 1024} MB")
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return strip_jpeg(data), ".jpg"
    if ext == ".png":
        return strip_png(data), ".png"
    raise ValueError("only .png, .jpg and .jpeg are accepted")


def draft(src, name, description, out, confirmed):
    if not confirmed:
        sys.exit("refused: pass --confirm-reviewed after a human has looked at every image for passwords, personal data and other people")
    if not NAME_RE.match(name) or not 1 <= len(description) <= 1024:
        sys.exit("refused: name must be kebab-case and description 1-1024 characters")
    src, out = pathlib.Path(src), pathlib.Path(out)
    files = sorted(p for p in src.iterdir() if p.is_file() and p.name != "steps.txt")
    if not files or len(files) > MAX_IMAGES:
        sys.exit(f"refused: need 1 to {MAX_IMAGES} images, found {len(files)}")
    notes = [ln.strip() for ln in (src / "steps.txt").read_text().splitlines() if ln.strip()] if (src / "steps.txt").is_file() else []
    dest = out / name
    if dest.exists():
        sys.exit(f"refused: {dest} already exists")
    cleaned = []
    for p in files:
        try:
            cleaned.append(clean(p))
        except (ValueError, struct.error) as e:
            sys.exit(f"refused: {p.name}: {e}")
    (dest / "assets").mkdir(parents=True)
    (dest / "references").mkdir()
    steps = []
    for i, (data, ext) in enumerate(cleaned, 1):
        (dest / "assets" / f"step{i:02d}{ext}").write_bytes(data)
        text = notes[i - 1] if i <= len(notes) else "TODO: describe what to do in this step and what you should see"
        steps.append(f"{i}. {text}\n   ![Step {i}](assets/step{i:02d}{ext})")
    body = "\n".join(steps)
    safe_desc = description.replace('"', "'")
    (dest / "SKILL.md").write_text(f'''---
name: {name}
description: "{safe_desc}"
---

# {name}

TODO: two sentences on why this skill exists and who it is for.

## Steps

{body}

## Never

- TODO: what must never happen, and why (money, safety, other people's data).

## Output contract

TODO: what to report, and how to confirm the task actually worked.

Status: DRAFT from a capture. The steps were NOT run or verified. See `references/capture-notes.md`.
''')
    (dest / "references" / "capture-notes.md").write_text(f"""# Capture notes

- Drafted: {datetime.date.today().isoformat()} from {len(cleaned)} image(s).
- A human confirmed the images were reviewed for passwords, personal data and other people.
- Image metadata (Exif, XMP, comments, PNG text and time chunks) was stripped by the drafting script.
- Nothing here was run. Treat every step as unverified until someone follows it and a Checker confirms.
""")
    print(f"drafted {name}: {len(cleaned)} steps -> {dest}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("capture_dir"); a.add_argument("--name", required=True); a.add_argument("--description", required=True)
    a.add_argument("--out", required=True); a.add_argument("--confirm-reviewed", action="store_true")
    a = a.parse_args()
    draft(a.capture_dir, a.name, a.description, a.out, a.confirm_reviewed)
