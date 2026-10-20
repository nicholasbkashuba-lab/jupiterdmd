# jupiterdmd.com: Angelo Forte, DMD

Static site for **Angelo Forte, DMD**, a general and cosmetic dentist at 654 W. Indiantown Rd.,
Suite 105, Jupiter, FL 33458 · (561) 747-2134. Built by Design of Man to replace the practice's
Officite template site.

## How it works

- **`site_data.py` holds every fact and line of copy**: practice details, hours, services and their
  FAQs, testimonials, areas served. Sources are noted inline. Nothing in it is invented.
- **`build.py` renders it**: every page, the JSON-LD schema, `sitemap.xml`, `robots.txt`, `llms.txt`,
  `site.webmanifest` and `vercel.json` (redirects, security headers, cache rules). Stdlib only.
- Output is committed: `index.html`, `<page>/index.html`. Vercel serves the files as they are.

```bash
python3 build.py              # regenerate everything
python3 _dev/preflight.py     # hard-failing pre-deploy gate (exit 1 = do not deploy)
node _dev/serve.js 8833       # local stand-in for Vercel (redirects, brotli, /api stub)
PW=... AXE=... SCHEMES=light,dark node _dev/verify.js http://localhost:8833   # axe + errors + overflow, every page, 3 widths
```

Build switches are environment variables, read at build time: `GA4_ID`, `VERCEL_ANALYTICS=1`,
`FORM_ENDPOINT`, `SHARE_BASE` (see the docstring at the top of `build.py`).

## Assets

| What | Where | Notes |
|---|---|---|
| Hero video | `assets/video/inlet-{1080,720}.mp4`, `inlet-1080.webm` (AV1) | Jupiter Inlet sunset drone footage (Design of Man). Seamless 17.4 s loop. Phones get `inlet-portrait.{webm,mp4}` (3:4 crop framed like the phone poster, 1.6/1.9 MB). Rebuild with `tools/encode_hero.sh <source.mp4>`. Reduced motion, Save-Data and 2G get the poster only; video always starts after load, so the poster stays the LCP. |
| Hero posters | `assets/img/hero/` | Frame one of the loop. Portrait crop for phones. |
| Photo strip | `assets/img/strip/` + `manifest.json` | Stills from the same footage. **Swap for the practice's own photos** when they arrive: drop files in, update the manifest. |
| Share cards | `assets/img/og/` | Rendered by `tools/og.js` from `tools/og-cards.json` (written by the build). |
| Fonts | `assets/fonts/` | Instrument Serif + Instrument Sans (OFL), Latin subset. Renamed `-v2` because `/assets/fonts/*` is cached immutable: new bytes need a new filename. |
| Logo / favicon | `assets/img/favicon.svg`, `logo-*.png`, `/favicon.ico` | Monogram drawn from Instrument Serif Italic outlines (`tools/monogram-path.txt`). |

## Things that are deliberate

- **No online booking form until there is an inbox.** The old site had no form and no published
  email, so `/contact/` books by phone. Set `FORM_ENDPOINT` (e.g. a Formspree/FormSubmit URL that
  delivers to the practice) and rebuild: the request form appears with a honeypot, a timing trap
  and a "please don't include medical details" notice. Preflight blocks any `<form>` without a real endpoint.
- **No tracking on `/contact/`**, ever (HHS OCR guidance on tracking technologies). GA4 loads with
  Consent Mode defaults: ad storage always denied, analytics denied when the browser sends Global Privacy Control.
- **No `aggregateRating` in our own schema** (Google treats self-served LocalBusiness review stars as spam).
  Live Google reviews render through `/api/reviews` only when `GOOGLE_PLACES_API_KEY` is set in Vercel.
- **Testimonials are verbatim**, typos included, attributed exactly as the practice published them.
- **Languages (Italian, Spanish) and education (University of Florida)** appear on Healthgrades but
  not on the practice's own site, so they are held back in `site_data.py` until the practice confirms.
- **Canonical host is `https://www.jupiterdmd.com`** (the old site ranked on www). `vercel.json`
  308s the apex to www, and 301s all 130 URLs Common Crawl recorded on the old site to their new equivalents.

See `LAUNCH.md` for the cutover checklist and the list of facts the practice still needs to confirm.
