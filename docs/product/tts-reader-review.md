# Review of the uploaded TTS Reader Chrome extension (0.1.0)

Status: read-only review on 2026-10-01 of two uploaded zips (an unpacked build and a source tree). Not installed, not run. Not a PMCR-O component yet.

## What it is

A Manifest V3 extension that reads page text aloud using Microsoft Edge's text-to-speech voices. The two zips match except locale strings, the background script (one has a clipboard-read path) and the content script.

## Findings

- **Text is sent to a third party.** To get audio it posts the text, voice and rate to `https://tts.webextools.com/tts`, a server this repo cannot vouch for. It tries that first, then a local proxy at `127.0.0.1:8787`, then a direct WebSocket that does not work in a browser. Anything you have it read, including private pages or the clipboard, goes to that server.
- **Broad permissions:** a content script on every page (`<all_urls>`), plus `tabs`, `scripting`, `activeTab`, `clipboardRead`, `notifications`, `contextMenus` and `storage`.
- **No other network calls found** in a text search for fetch, XMLHttpRequest, WebSocket, sendBeacon, eval and `new Function`; the only dynamic code load is `importScripts` of two bundled files. A text search is not a full audit.
- The settings page has a proxy URL override, so it can be pointed at a server the owner controls.

## Recommendation for the Round Table voices

Do not use the remote default for anything private. Run the local proxy (`127.0.0.1:8787`) or point the override at a server under the owner's control, and remove `clipboardRead` and `<all_urls>` if they are not needed. Treat it as a candidate until reviewed by a person; installing it is on the owner's always-ask list.
