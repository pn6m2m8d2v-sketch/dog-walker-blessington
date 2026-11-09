#!/usr/bin/env python3
"""Rebuild the optimised images in img/ from their recorded sources.

Usage:  python3 scripts/build-images.py [--src-cache /tmp/img-src]

Downloads each source once (Wikimedia Commons originals via the API, so licence metadata is
read from the file page rather than typed by hand), writes metadata-free WebP variants at the
listed widths, one JPG for the Open Graph preview, and regenerates img/CREDITS.md.
Requires Pillow with WebP support.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "img")
UA = {"User-Agent": "blessington-walkers-draft/1.0 (static site build script)"}

# name -> (Commons file title | "live:<url>", widths, quality, role note for credits[, crop])
# crop = (left, top, right, bottom) as fractions of the source, applied before resizing.
SOURCES = {
    "hero-lake-aerial": ("File:Poulaphouca Reservoir - aerial - 2025-07-12 02.jpg", (640, 1024, 1600), 76, "Hero"),
    "route-town": ("File:View of the skyline of Blessington from the Glen Ding Greenway 02.jpg", (640, 1024), 78, "Town walk card"),
    "route-lake": ("File:Dec2025. Poulaphouca Reservoir, County Wicklow, Ireland 02.jpg", (640, 1024), 78, "Lake walk card"),
    "route-forest": ("File:New walkway on old Blessington demesne, Co Wicklow 06.jpg", (640, 1024), 72, "Forest walk card"),
    "route-long": ("File:Dec2025. Poulaphouca Reservoir, County Wicklow, Ireland 06.jpg", (640, 1024), 78, "Long loop card"),
    "route-greenway": ("File:Dec2025. Views of Russborough House, County Wicklow, Ireland 01.jpg", (640, 1024), 78, "Greenway / Russborough card"),
    "area-lake": ("File:Dec2025. Poulaphouca Reservoir, County Wicklow, Ireland 04.jpg", (640, 1024, 1600), 76, "Where we walk"),
    "dog-golden": ("File:Dülmen, Hausdülmen, Golden Retriever -- 2022 -- 5945.jpg", (480, 960), 76, "Happy dogs grid"),
    "dog-forest": ("File:Münster, Wolbeck, Wolbecker Tiergarten, Hund -- 2014 -- 7130.jpg", (480, 960), 72, "Happy dogs grid"),
    "dog-dalmatian": ("File:Dalmatian fetching a stick.jpg", (480, 960), 76, "Happy dogs grid"),
    "dog-small": ("File:Dog at Nørre Vorupør Strand.jpg", (480, 960), 76, "Happy dogs grid"),
    "dog-terrier-coat": ("live:https://www.blessingtonwalkers.ie/img/puppy-web.jpg", (480, 960), 70, "Happy dogs grid", (0.05, 0.22, 0.95, 0.97)),
}
OG_IMAGE = ("hero-lake-aerial", 1200, 630)


def api(params):
    params["format"] = "json"
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return json.load(r)


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def commons_info(title):
    # A 2048px server-side thumbnail is plenty for 1600px output and avoids the stricter
    # rate limit on multi-megabyte originals.
    d = api({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 2048})
    page = next(iter(d["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    em = ii.get("extmetadata", {})
    return {
        "title": page["title"],
        "url": ii.get("thumburl") or ii["url"],
        "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ", "_")),
        "author": strip_html(em.get("Artist", {}).get("value")),
        "license": strip_html(em.get("LicenseShortName", {}).get("value")),
        "license_url": strip_html(em.get("LicenseUrl", {}).get("value")) or "https://creativecommons.org/publicdomain/zero/1.0/",
        "credit": strip_html(em.get("Credit", {}).get("value")),
    }


def download(url, dest):
    if os.path.exists(dest):
        return
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            time.sleep(1.5)
            return
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def write_variants(src_path, name, widths, quality, crop=None):
    im = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    if crop:
        l, t, r, b = crop
        im = im.crop((round(l * im.width), round(t * im.height), round(r * im.width), round(b * im.height)))
    out = []
    for w in widths:
        if w >= im.width:
            w = im.width
        h = round(im.height * w / im.width)
        dest = os.path.join(IMG_DIR, f"{name}-{w}.webp")
        im.resize((w, h), Image.LANCZOS).save(dest, "WEBP", quality=quality, method=6)
        out.append((w, h, os.path.getsize(dest)))
    return out


def write_og(src_path, w, h):
    im = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.45))
    dest = os.path.join(IMG_DIR, "og-lake.jpg")
    im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
    return os.path.getsize(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-cache", default="/tmp/img-src")
    args = ap.parse_args()
    os.makedirs(args.src_cache, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    credits = []
    for name, (source, widths, quality, role, *crop) in SOURCES.items():
        if source.startswith("live:"):
            url = source[5:]
            info = {"title": os.path.basename(url), "page": url, "author": "Site owner (existing live-site photo)",
                    "license": "Owner's own photo; re-used from the current live site", "license_url": "", "credit": ""}
        else:
            info = commons_info(source)
            url = info["url"]
        src = os.path.join(args.src_cache, name + os.path.splitext(url)[1].lower())
        print(f"{name}: {info['title']} [{info['license']}]", flush=True)
        download(url, src)
        variants = write_variants(src, name, widths, quality, crop[0] if crop else None)
        for w, h, size in variants:
            print(f"   {name}-{w}.webp {w}x{h} {size // 1024} KB")
        credits.append((name, info, role, variants))
        if name == OG_IMAGE[0]:
            print(f"   og-lake.jpg {write_og(src, OG_IMAGE[1], OG_IMAGE[2]) // 1024} KB")

    lines = [
        "# Image credits and licences",
        "",
        "Generated by `scripts/build-images.py`. Every image below was resized, re-encoded to WebP and",
        "stripped of metadata (a \"modification\" under Creative Commons terms). Blessington scenery is",
        "genuinely Blessington / Poulaphouca / Russborough. Dog photos are generic licensed photos and",
        "are never captioned as client dogs or as a specific Blessington route.",
        "",
        "| File set | Used for | Source | Author | Licence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, info, role, variants in credits:
        lic = f"[{info['license']}]({info['license_url']})" if info["license_url"] else info["license"]
        lines.append(f"| `{name}-*.webp` | {role} | [{info['title']}]({info['page']}) | {info['author']} | {lic} |")
    lines += [
        "",
        "Attribution lines used in the page footer follow each licence's requirements, e.g.",
        "`Dietmar Rabich / Wikimedia Commons / \"<title>\" / CC BY-SA 4.0`.",
    ]
    with open(os.path.join(IMG_DIR, "CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote img/CREDITS.md")


if __name__ == "__main__":
    sys.exit(main())
