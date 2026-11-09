#!/usr/bin/env python3
"""Static checks for the draft site. Run from the repo root: python3 scripts/check.py

Checks: referenced local assets exist, in-page anchors resolve, every <img> has alt text and
dimensions, no external image sources, forbidden strings (private data, unsupported claims) are
absent from the rendered page, and the core colour pairs in styles.css meet WCAG AA contrast.
Exit code 1 on any failure.
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
CSS = os.path.join(ROOT, "styles.css")

# Strings that must never appear in the public page (case-insensitive).
FORBIDDEN = [
    # children's names / family framing
    "enzzo", "william", "twin", "boys", "lads", "kids", "school",
    # phone numbers and contact placeholders
    "085 181", "0851813", "087 485", "0874857", "+353", "wa.me", "whatsapp",
    # unsupported claims / removed features
    "every dog has gps", "do not get lost", "don't get lost", "add tracker", "add number",
    "insured", "insurance", "qualified", "certified", "review", "testimonial",
    "kaleidoscope", "july 2026",
    # private-asset filenames
    "boys-web", "prices-pup",
]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs, self.ids, self.hrefs, self.text = [], set(), [], []
        self.srcs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "img":
            self.imgs.append(a)
            self.srcs.append(a.get("src", ""))
            for cand in (a.get("srcset") or "").split(","):
                cand = cand.strip().split(" ")[0]
                if cand:
                    self.srcs.append(cand)
        if tag == "link" and a.get("rel") in ("stylesheet", "preload"):
            self.srcs.append(a.get("href", ""))
            for cand in (a.get("imagesrcset") or "").split(","):
                cand = cand.strip().split(" ")[0]
                if cand:
                    self.srcs.append(cand)
        if tag == "meta" and a.get("property") == "og:image":
            self.srcs.append(a.get("content", ""))
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

    def handle_data(self, data):
        self.text.append(data)


def rel_lum(hexcol):
    hexcol = hexcol.lstrip("#")
    r, g, b = (int(hexcol[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    failures = []
    html = open(HTML, encoding="utf-8").read()
    css = open(CSS, encoding="utf-8").read()
    p = Page()
    p.feed(html)

    # Assets
    for src in p.srcs:
        if re.match(r"https?://", src):
            if src.endswith((".webp", ".jpg", ".png")):
                failures.append(f"external image source: {src}")
            continue
        if not os.path.exists(os.path.join(ROOT, src)):
            failures.append(f"missing asset: {src}")
    for m in re.finditer(r"url\(([^)]+)\)", css):
        u = m.group(1).strip("'\"")
        if not u.startswith("data:") and not os.path.exists(os.path.join(ROOT, u)):
            failures.append(f"missing css asset: {u}")

    # Anchors
    for h in p.hrefs:
        if h.startswith("#") and h[1:] not in p.ids:
            failures.append(f"dangling anchor: {h}")

    # Images
    for a in p.imgs:
        if "alt" not in a:
            failures.append(f"img without alt: {a.get('src')}")
        if not (a.get("width") and a.get("height")):
            failures.append(f"img without width/height: {a.get('src')}")

    # Forbidden strings in rendered text + attributes (strip tags but keep attribute values)
    rendered = " ".join(p.text).lower() + " " + " ".join(re.findall(r'(?:alt|title|content|aria-label)="([^"]*)"', html)).lower()
    for word in FORBIDDEN:
        # "review" check should not trip on "preview"
        pattern = r"(?<![a-z])" + re.escape(word) if word in ("review",) else re.escape(word)
        if re.search(pattern, rendered):
            failures.append(f"forbidden string present: {word!r}")
    if re.search(r"\b0?8[3-9][\s-]?\d{3}[\s-]?\d{4}\b", rendered):
        failures.append("looks like an Irish mobile number in the page")

    # Contrast (AA: 4.5 normal text, 3.0 large text / UI)
    def var(name):
        m = re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{6})", css)
        return m.group(1)
    pairs = [
        ("ink on cream", var("ink"), var("cream"), 4.5),
        ("muted on cream", var("muted"), var("cream"), 4.5),
        ("muted on card", var("muted"), var("card"), 4.5),
        ("muted on cream-deep", var("muted"), var("cream-deep"), 4.5),
        ("accent kicker on cream", var("accent"), var("cream"), 4.5),
        ("moss on card (price)", var("moss"), var("card"), 4.5),
        ("white on moss", "#ffffff", var("moss"), 4.5),
        ("gold kicker on moss", var("gold"), var("moss"), 4.5),
        ("places text on moss", "#f3eee3", var("moss"), 4.5),
        ("where-note on moss", "#dfe6d6", var("moss"), 4.5),
        ("figcaption on moss", "#cfd8c6", var("moss"), 4.5),
        ("ribbon text", "#fff6ea", "#7a3b12", 4.5),
        ("nav pill text on card", var("ink"), var("card"), 4.5),
        ("hero lede on dark gradient", "#f0ebdf", "#1f2b1f", 4.5),
    ]
    for label, fg, bg, need in pairs:
        c = contrast(fg, bg)
        status = "ok" if c >= need else "FAIL"
        print(f"contrast {label}: {c:.2f} ({status})")
        if c < need:
            failures.append(f"contrast too low: {label} = {c:.2f}")

    print(f"\nchecked {len(p.imgs)} images, {len(set(p.srcs))} asset refs, {len(p.hrefs)} links")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(" -", f)
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
