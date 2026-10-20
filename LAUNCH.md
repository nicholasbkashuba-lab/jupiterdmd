# Launch checklist: jupiterdmd.com

## Confirm with the practice before DNS moves
- [ ] **Hours.** Site shows Mon–Thu 8:00–5:00 (lunch 1–2), Fri by appointment, from the old site. The old
      site's own schema contradicted it (Fri 9–5 in one block, "Fr 0:00" in another).
- [ ] **Dr. Forte's bio and photo.** The old site said "Bio Coming Soon". A portrait replaces the monogram card
      on the homepage and /about/.
- [ ] **Office and team photos** for the rolling strip (currently Jupiter Inlet stills from the drone footage).
- [ ] **Languages spoken** (Healthgrades lists English, Italian, Spanish) and **dental school**
      (Healthgrades/Sharecare: University of Florida). Flip on in `site_data.py` once confirmed.
- [ ] **An inbox for appointment requests** → `FORM_ENDPOINT`.
- [ ] **Patient forms** (old site: "Coming Soon"). PDFs or a HIPAA-eligible form provider.
- [ ] **Clinical copy sign-off.** Service pages are general patient education written for this site.
      Dr. Forte should read them; nothing is marked "medically reviewed" until he has.
- [ ] **Delta Dental Medicare Advantage** participation (listed in Delta's directory, not on the site yet).
- [ ] **The "New Clients Receive 15% Off" offer** on the old /blog page: still valid? Not carried over.
- [ ] **Google Business Profile** URL and owner access, for `sameAs` and the Places review feed.

## Cutover
1. `SHARE_BASE=https://www.jupiterdmd.com python3 build.py`, commit, deploy.
2. Add `jupiterdmd.com` and `www.jupiterdmd.com` to the Vercel project; point DNS (currently Cloudflare → Officite).
3. **Turn off the Cloudflare bot challenge** if Cloudflare stays in front: today every automated
   visitor (Lighthouse, Common Crawl, AI crawlers, link previews) gets a 403 "Just a moment..." page.
4. Check `https://jupiterdmd.com/` → 308 → `https://www.jupiterdmd.com/`, and spot-check old URLs
   (`/staff`, `/our-location`, `/articles/general/502402-implants`).
5. Search Console: verify the domain property, submit `/sitemap.xml`. Bing Webmaster Tools: import from GSC.
6. Set `GOOGLE_PLACES_API_KEY` (and optionally `GOOGLE_PLACE_ID`) in Vercel for live reviews.
7. Optional analytics: enable Web Analytics in Vercel, then `VERCEL_ANALYTICS=1`; or `GA4_ID=G-…`. Rebuild.
8. Update directory listings to the same NAP: Healthgrades, WebMD, Vitals, CareCredit locator, NPPES.
