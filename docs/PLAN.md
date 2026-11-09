# Draft redesign — findings, plan and launch blockers

Status: **draft only**. Not merged, not deployed. Production at https://www.blessingtonwalkers.ie
is unchanged by this branch.

## 1. Does this repo match the live site?

Partly. The live page (`Blessington Lake Walks`, Netlify) matches the brief in this repo
(`CHAT-BRIEF.md`, `README.md`): same name, same nine prices, same sections (Walks, Russborough,
Walkers, GPS, Book). But the repo holds **no site source** — only the two markdown briefs. The
commit "Add ChatGPT brief and current index.html" did not actually add `index.html`. The live
HTML and `/img/*.jpg` were fetched from the public site for comparison and are the only source
of the current design.

## 2. Deployment safety check

- No GitHub Actions workflows, no `netlify.toml`, no deployments or commit statuses recorded on
  GitHub for this repo.
- The repo has no `index.html`, yet the live site serves a full page, so Netlify is **not**
  deploying this repo's `main` (it would 404 otherwise). The site is most likely a manual/drag-drop
  Netlify deploy.
- Conclusion: pushing a feature branch and opening a PR cannot change production. If Netlify is
  later linked to this repo, only `main` would be the production branch; this work stays on
  `cursor/photo-route-draft-6f0b` until the parent reviews it.

## 3. What the live page gets wrong (fixed in the draft)

| Live site | Draft |
| --- | --- |
| Hero copy "Two boys. One lake…", "Twin walkers" section, `boys-web.jpg`, `prices-pup-web.jpg` (child's face) | Removed. No children's names, faces or school/home references anywhere. |
| "Every dog has GPS. They do not get lost." + three "add tracker" placeholder fields | Removed. One optional, hedged line: a tracker can be fitted on request. No GPS fields. |
| Book section: "Numbers go here when you send them" + four "add number" placeholders | Honest "contact details coming soon" card, no fake booking button. |
| Kaleidoscope "3 to 5 July 2026" event text | Removed (stale, off-topic). |
| `white-dog-web.jpg` studio stock photo captioned "White dog on the Blessington walk" | Removed — generic photo falsely labelled as a Blessington route. |
| Prices as a bare list | Five route cards with photo + description, extras strip, same prices. |

## 4. Prices (verified against live HTML on 2026-11-08, unchanged)

Town 30 min €14 · Lake 1 hour €20 · Forest 90 min €27 · Long 2 hours €34 ·
Russborough / Greenway €27 one way, €34 if we stay and walk back · Extra dog +€5 ·
Bar collect €12 · 3-pack €54 · 5-pack €85.

**Awaiting confirmation (shown as-is, not reinterpreted):** which walks a 3-/5-pack covers,
whether "Bar collect €12" is a flat collection fee or a short walk from the pub, and whether
"Extra dog" applies per walk. The draft footnotes these as "confirmed on enquiry".

## 5. Assets

### Reviewed existing live assets

| File | Review | Decision |
| --- | --- | --- |
| `lake-1/2/3-web.jpg` | Genuine aerial shots of Poulaphouca at sunset. Not listed in the brief's "real photos"; owner/licence unknown. | Not used. Replaced with CC-licensed equivalents. Parent may swap back if these are their own drone shots. |
| `russborough-web.jpg` | Russborough facade, provenance unknown. | Not used; CC0 replacement. |
| `white-dog-web.jpg` | Studio stock dog with a tie; not a Blessington walk. | Not used. |
| `puppy-web.jpg` | Real small dog in a coat on a path; no people (photographer's shadow only); no EXIF. Listed in brief as a real photo. | **Kept** (re-encoded, metadata-free) as `img/dog-terrier-coat-*.webp`. |
| `prices-pup-web.jpg`, `boys-web.jpg` | Identifiable children. | Excluded, not downloaded into the repo. |

No live image carried EXIF/GPS metadata; all new derivatives are written without metadata.

### Sourced photos (Wikimedia Commons, own-work uploads only)

Full list with links, authors and licences in `img/CREDITS.md`. All Blessington scenery is
genuinely Blessington (Poulaphouca Reservoir, Glen Ding Greenway, old Blessington demesne,
Russborough House). Dog photos are generic licensed photos and are captioned generically.
CC BY-SA images are credited in the page footer as the licence requires; CC0 images are credited
anyway. Three "unknown author / sent to me" CC0 dog photos were rejected for weak provenance.

## 6. Launch blockers (not fixable in this draft)

1. **No business contact method.** The brief lists the children's personal mobiles and the
   household number; none can be published. A dedicated business WhatsApp/phone or email is
   needed before the Enquire section can do anything.
2. **Price extras ambiguity** (section 4) needs the parent's answer.
3. **Draft ribbon and `<meta name="robots" content="noindex">`** must be removed at launch.
4. **Repo hygiene (outside this draft's scope, flagged only):** `README.md` and `CHAT-BRIEF.md`
   in this *public* repo contain the children's names and personal phone numbers.

## 7. Implementation plan (this branch)

1. `docs/DESIGN.md`, `docs/PLAN.md` — this.
2. `img/` — optimised WebP sets + `og-lake.jpg` + `CREDITS.md`; `scripts/build-images.py`
   regenerates them from the recorded sources.
3. `index.html`, `styles.css` — the page.
4. `scripts/check.py` — static checks: every referenced asset exists, no forbidden strings
   (names, phone numbers, "GPS", "insured", "do not get lost"), no external image URLs.
5. Playwright checks at 320 / 375 / 390 / 768 / 1440: no horizontal overflow, every visible
   control ≥ 44×44 px, menu keyboard flow (Enter/Tab/Escape/focus return), outside-tap and
   touch-pointer close, reduced motion, screenshots saved to `/opt/cursor/artifacts/`.

## 8. Mobile access pass (second iteration)

Requested after the first draft: "easier access/controls on mobile". Changes:

- Replaced the horizontal-scrolling pill strip (which hid "Enquire" off-screen on phones) with a
  sticky single-row header: brand + quick Prices link + Menu button (details in `DESIGN.md`).
- Touch targets: all controls ≥ 44×44 px; menu rows 52 px.
- Type: footnotes, captions, footer and credits raised to ≥ 15 px; body stays 17 px.
- Hero re-laid so copy never overlaps the header at 320 px; two-part Greenway price wraps.
- Added a 44 px "Back to top" link in the footer.
- Deliberately **not** added: bottom/sticky action bar (would cover content on short screens and
  the only honest actions are already one tap away), any booking or contact control.

Test matrix (Playwright, local `python3 -m http.server`): widths 320, 360, 375, 390, 400, 480,
560, 768, 899, 1440 — no horizontal overflow at any; header stays one row at all; 0 controls
under 44 px at 320/375/390/768; menu `aria-expanded` toggles correctly via click, keyboard and
synthetic touch pointer events; Escape returns focus to the button; link activation closes the
menu and scrolls to the section; reduced-motion disables transitions and smooth scroll.
