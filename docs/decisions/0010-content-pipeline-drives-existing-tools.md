# 0010: The content pipeline drives existing tools; the founder approves

Status: proposed · 2026-10-01 (owner: tools like OBS can do recording and editing, the founder is needed for very little)

## Decision
Do not build editing, recording or streaming software. The plugin owns the parts nobody else does: the script in the founder's voice, sourced claims, consent and disclosure, and the approval gate. Recording and editing are delegated to existing tools (OBS Studio, ffmpeg, an editor of the owner's choice) through their own automation interfaces. The founder's role is to approve and publish, and to supply the voice once under ADR 0008.

## Consequences
OPEN and unverified: which tools, and how to drive them. OBS Studio has a built-in WebSocket control interface in recent versions, and ffmpeg is scriptable, but neither was checked or tried here. A synthetic-voice engine is also unchosen. Every publish step stays a human action.
