# Blessington dog-walking site — draft redesign (design notes)

Status: **draft only**. Nothing here is live. See `PLAN.md` for findings, scope and launch blockers.

## Goal

Turn the current single page (prices list + placeholder blocks) into a photo-led brochure
that sells the *walks* — town, lake, forest, Greenway — in a way that is honest, calm and easy
to scan on a phone. No calculator, booking system, enquiry builder or other interactive tools.

## Audience and tone

Dog owners in and around Blessington looking for a local, small-scale walker. Tone is warm,
plain and local ("the lake", "the Greenway"), never corporate. No claims we cannot back up:
no insurance, qualifications, reviews, tracking promises or "they do not get lost".

## Page structure (one page, top to bottom)

1. **Draft ribbon** — thin bar saying this is a preview and not taking bookings. Remove at launch.
2. **Header** (sticky, one 61px row at every width) — brand, a quick **Prices** link
   (≥400px wide; "Walks & prices" from 560px) and a **Menu** button. The button discloses the
   five section links as 52px-tall touch rows (`aria-expanded`, `aria-controls`, Escape closes
   and returns focus, link tap closes, outside tap closes). Below 400px the quick link is
   dropped so the row still fits; the hero button and the menu's first row cover it.
   From 900px the button disappears and the links show inline as 44px pills. Without JS the
   button never renders and the links are simply listed, so nothing depends on the script.
   No bottom bar: it would hide content on short phones and the sticky Menu already gives
   one-tap access to every section without implying a booking or contact action.
3. **Hero** — full-bleed aerial of Poulaphouca Reservoir with a dark green gradient, kicker,
   one-line headline, one-line lede, two buttons (Walks & prices / Enquire).
4. **Walks & prices** — the five routes as photo cards. Each card: route photo, name, duration,
   price, two lines on what the walk is actually like. Below: an "Extras" strip for extra dog,
   bar collection and the two packs, with a footnote that pack/collection details are confirmed
   on enquiry.
5. **Where we walk** — short list of the real places (town, lakes, Greenway, Glen Ding, Russborough)
   with one wide lake photo and a "Blessington and nearby only" line.
6. **Happy dogs** — a simple photo grid of dogs (licensed, credited). Captions are generic and
   never claim a dog or place is a client or a Blessington route unless it is.
7. **How it works** — four short steps: say hello, quick meet, the walk, back to you.
   Group sizes from the brief (up to three small dogs, one or two bigger dogs), cash or Revolut.
8. **Enquire** — honest "contact details coming soon" card. No form, no fake button.
9. **Footer** — name, area, photo credits (required for CC BY-SA images), draft note.

## Visual system

- **Colours**: forest green `#2f4a32` (primary), deep green `#1c241c` (ink), warm cream
  `#f6f1e7` (background), card cream `#fffdf8`, sand line `#d8d0c0`, muted green-grey
  `#5a6456`, gold accent `#b8924e` (kickers only). All text pairs tested ≥ 4.5:1.
- **Type**: system stacks only, no font downloads. Serif display for headings
  (Iowan Old Style / Palatino / Georgia), humanist sans for body (system-ui).
- **Spacing**: 8-pt rhythm, sections padded `clamp(48px, 8vw, 96px)`, max content width 1120px,
  text measure ≤ 60ch.
- **Cards**: 20px radius, soft shadow, photo on top with a fixed aspect ratio so nothing jumps
  while images load.
- **Motion**: only a gentle hover lift and smooth anchor scrolling; both disabled under
  `prefers-reduced-motion: reduce`.

## Accessibility

- Skip link, landmarks (`header`, `nav`, `main`, `section` with headings, `footer`).
- All interactive elements are links or buttons with visible 3px focus rings.
- Every tappable control is at least 44×44 CSS px (menu button, nav rows, quick link, hero
  buttons, "Photo credits" summary, "Back to top"); only inline credit links in running text
  are exempt. Body text is 17px; nothing user-facing is below 15px.
- Hero grows with its copy (image is an absolute cover) so headlines never slide under the
  sticky header at 320px.
- Alt text describes the picture; decorative images use `alt=""`.
- Current section highlighted in the nav with `aria-current` (tiny inline script,
  page works without it).
- No horizontal overflow at 375 / 768 / 1440; verified in Playwright.

## Images

- Delivered as WebP at 640 / 1024 / 1600 widths with `srcset`/`sizes`, `loading="lazy"`
  except the hero, explicit `width`/`height`, and all metadata stripped.
- One JPG (`img/og-lake.jpg`) for the Open Graph preview.
- Sources and licences are listed in `img/CREDITS.md` and summarised in `PLAN.md`.
