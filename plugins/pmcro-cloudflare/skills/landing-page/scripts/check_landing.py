#!/usr/bin/env python3
"""Check a landing page's affiliate-disclosure basics. It verifies form, not law or truth.

  python check_landing.py <page.html> [--affiliate-domains a.com,b.com]
Checks: <title> and meta description exist; every link to an affiliate domain (or with a ref/aff/tag
query key) has rel containing sponsored; a disclosure sentence mentioning commission or affiliate
appears before the first affiliate link; no guaranteed-income phrasing; a privacy link exists; no
credential-shaped text (API tokens).
Output: one "ERROR <reason>" line per problem, else "ok: N affiliate links". Exit 1 on error.
It never prints PASS, LOOP or HALT: only the Checker role issues verdicts. It cannot judge clarity,
truth, program terms or legal compliance.
"""
import argparse, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs

RISKY = re.compile(r"guarantee[sd]?\s+(income|results|profit|earnings)|get rich|make \$?\d[\d,]*\s*(a|per)\s*(day|week|month)|risk[- ]free|you will earn", re.I)
DISCLOSE = re.compile(r"commission|affiliate", re.I)
SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|cf[a-z]*[_-]?token\s*[:=]\s*\S{20,}", re.I)
AFF_KEYS = {"ref", "aff", "aff_id", "affiliate", "tag", "partner"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = self.meta = False
        self.links, self.text, self.privacy = [], [], False
        self._in_title = False
        self._in_a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and a.get("name", "").lower() == "description" and a.get("content", "").strip():
            self.meta = True
        if tag == "a":
            self._in_a = a
            self.links.append((a.get("href", ""), a.get("rel", ""), len("".join(self.text))))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "a":
            self._in_a = None

    def handle_data(self, data):
        if self._in_title and data.strip():
            self.title = True
        elif self._in_a is not None and "privacy" in data.lower():
            self.privacy = True
        self.text.append(data)


def check(html, domains=()):
    errs = []
    p = Page()
    p.feed(html)
    if not p.title:
        errs.append("ERROR missing <title>")
    if not p.meta:
        errs.append("ERROR missing meta description")
    if not p.privacy:
        errs.append("ERROR no privacy policy link")
    if RISKY.search(html):
        errs.append("ERROR guaranteed-income or get-rich phrasing found")
    if SECRET.search(html):
        errs.append("ERROR credential-shaped text found")
    aff = []
    for href, rel, pos in p.links:
        u = urlparse(href)
        host = (u.hostname or "").lower()
        if any(host == d or host.endswith("." + d) for d in domains) or AFF_KEYS & set(parse_qs(u.query)):
            aff.append((href, rel, pos))
    for href, rel, _ in aff:
        if "sponsored" not in rel.lower().split():
            errs.append(f"ERROR affiliate link lacks rel=sponsored: {href[:60]}")
    if aff:
        before = "".join(p.text)[: min(pos for _, _, pos in aff)]
        if not DISCLOSE.search(before):
            errs.append("ERROR no commission/affiliate disclosure before the first affiliate link")
    return errs, len(aff)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("page"); a.add_argument("--affiliate-domains", default="")
    a = a.parse_args()
    errs, n = check(open(a.page, encoding="utf-8").read(), tuple(d for d in a.affiliate_domains.split(",") if d))
    print("\n".join(errs) if errs else f"ok: {n} affiliate links")
    sys.exit(1 if errs else 0)
