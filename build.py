#!/usr/bin/env python3
"""Generate every page of jupiterdmd.com from site_data.py.

    python3 build.py

Stdlib only, so a clean checkout always builds. Output is written in place
(index.html, <slug>/index.html, sitemap.xml, robots.txt, llms.txt, vercel.json)
and committed; Vercel serves the files as they are.

Build-time switches (environment variables, all optional):
  GA4_ID=G-XXXXXXX      emit Google Analytics 4 (never on /contact/)
  VERCEL_ANALYTICS=1    emit Vercel Web Analytics + Speed Insights (enable them in
                        the Vercel dashboard first, or the scripts 404)
  FORM_ENDPOINT=https://...  turn on the appointment-request form (see README)
  SHARE_BASE=https://...     host for og:image until www.jupiterdmd.com points here
"""

import datetime
import hashlib
import html
import json
import os
import re
import subprocess

from site_data import (AREAS, CONFIRM_EDUCATION, CONFIRM_LANGUAGES, FAQS, GROUPS,
                       HOME_FAQ_COUNT, HOURS, HOURS_NOTES, INTENTS, NEARBY, PRACTICE,
                       SERVICES, TESTIMONIALS)

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.jupiterdmd.com"          # canonical host: the old site already ranks on www
SHARE_BASE = os.environ.get("SHARE_BASE", "https://jupiterdmd.vercel.app")
GA4_ID = os.environ.get("GA4_ID", "").strip()
VERCEL_ANALYTICS = os.environ.get("VERCEL_ANALYTICS") == "1"
FORM_ENDPOINT = os.environ.get("FORM_ENDPOINT", "").strip()
SITE_UPDATED = "2026-10-19"

# Marks <html class="js"> before first paint so reveal animations never flash. Its hash is in the CSP.
JS_FLAG_CODE = "document.documentElement.classList.add('js')"
JS_FLAG = "<script>%s</script>" % JS_FLAG_CODE
JS_FLAG_HASH = "'sha256-%s'" % __import__("base64").b64encode(hashlib.sha256(JS_FLAG_CODE.encode()).digest()).decode()

P = PRACTICE
SVC = {s["slug"]: s for s in SERVICES}
WRITTEN = []          # (url_path, file) for the sitemap
PAGES_META = []       # (url_path, title) for llms.txt


def esc(s):
    return html.escape(s, quote=True)


def asset_v(rel):
    """Content hash for cache-busting. Missing files build as 'pending'."""
    path = os.path.join(ROOT, rel.lstrip("/"))
    if not os.path.exists(path):
        return "pending"
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:10]


def A(rel):
    """Versioned asset URL."""
    return "%s?v=%s" % (rel, asset_v(rel))


_LASTMOD = None


def page_lastmod(rel_file):
    """Date of the last commit that touched a generated file; today's build date otherwise."""
    global _LASTMOD
    if _LASTMOD is None:
        _LASTMOD = {}
        try:
            out = subprocess.run(["git", "log", "--name-only", "--format=@%cs"], cwd=ROOT,
                                 capture_output=True, text=True, timeout=30).stdout
            day = None
            for line in out.splitlines():
                if line.startswith("@"):
                    day = line[1:]
                elif line and line not in _LASTMOD:
                    _LASTMOD[line] = day
        except Exception:
            pass
    return _LASTMOD.get(rel_file, SITE_UPDATED)


# --- Icons (inline SVG, stroke-based, decorative) --------------------------------

ICON = {
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "card": '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18M7 15h4"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    "chev": '<path d="M6 9l6 6 6-6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "quote": '<path d="M9 7H5v6h4l-2 4M19 7h-4v6h4l-2 4"/>',
    "pause": '<path d="M9 6v12M15 6v12"/>',
    "play": '<path d="M8 5l11 7-11 7z"/>',
    "map": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "tooth": '<path d="M7 3c-2.5 0-4 2-4 4.5 0 3 1.5 4.5 2 7 .6 3 1 6.5 3 6.5s1.5-5 4-5 2 5 4 5 2.4-3.5 3-6.5c.5-2.5 2-4 2-7C21 5 19.5 3 17 3c-2 0-3 1-5 1S9 3 7 3z"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
}


def icon(name, cls="ic"):
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>'
            % (cls, ICON[name]))


MONOGRAM = open(os.path.join(ROOT, "tools/monogram-path.txt")).read().strip()


def wordmark(cls="wordmark"):
    return ('<span class="%s"><svg class="mark" viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
            '<circle cx="20" cy="20" r="19.2" fill="none" stroke="currentColor" stroke-width="1" opacity=".45"/>'
            '<path transform="translate(10.2 26.4) scale(.0275)" fill="currentColor" d="%s"/>'
            '<path d="M8.5 31.2c3.8-2 7.7 2 11.5 0s7.7 2 11.5 0" fill="none" stroke="var(--sun)" stroke-width="1.4" stroke-linecap="round"/>'
            '</svg><span class="wm-text"><span class="wm-name">Angelo Forte</span>'
            '<span class="wm-sub">DMD &middot; Jupiter</span></span></span>' % (cls, MONOGRAM))


# --- Images -------------------------------------------------------------------

def picture(base, widths, alt, sizes, cls="", w=None, h=None, eager=False, exts=("avif", "webp")):
    """<picture> for files named <base>-<width>.<ext> (jpg fallback)."""
    srcset = lambda ext: ", ".join("%s-%d.%s %dw" % (base, x, ext, x) for x in widths)
    dims = (' width="%d" height="%d"' % (w, h)) if w and h else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    sources = "".join('<source type="image/%s" srcset="%s" sizes="%s">' % (e, srcset(e), sizes) for e in exts)
    return ('<picture class="%s">%s<img src="%s-%d.jpg" srcset="%s" sizes="%s" alt="%s"%s%s></picture>'
            % (cls, sources, base, widths[-1], srcset("jpg"), sizes, esc(alt), dims, load))


def strip_manifest():
    path = os.path.join(ROOT, "assets/img/strip/manifest.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


# --- Schema -----------------------------------------------------------------------

ORG_ID = BASE + "/#practice"
DOC_ID = BASE + "/#dr-angelo-forte"
SITE_ID = BASE + "/#website"


def opening_hours():
    return [{"@type": "OpeningHoursSpecification", "dayOfWeek": "https://schema.org/" + d,
             "opens": o, "closes": c} for d, _, o, c in HOURS]


def org_node():
    return {
        "@type": "Dentist",
        "@id": ORG_ID,
        "name": P["name"],
        "legalName": P["legal_name"],
        "description": "General and cosmetic dentist in Jupiter, Florida: cleanings and exams, fillings, crowns and bridges, dental implants, porcelain veneers, teeth whitening, Invisalign, root canals, gum disease treatment, dentures, TMJ care and dental emergencies.",
        "url": BASE + "/",
        "telephone": P["phone_e164"],
        "faxNumber": "+15617472122",
        "image": SHARE_BASE + "/assets/img/og/og-home.jpg",
        "logo": {"@type": "ImageObject", "url": SHARE_BASE + "/assets/img/logo-512.png", "width": 512, "height": 512},
        "address": {"@type": "PostalAddress", "streetAddress": P["street_schema"], "addressLocality": P["city"],
                    "addressRegion": P["region"], "postalCode": P["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": P["lat"], "longitude": P["lng"]},
        "hasMap": P["maps_url"],
        "openingHoursSpecification": opening_hours(),
        "isAcceptingNewPatients": True,
        "medicalSpecialty": "https://schema.org/Dentistry",
        "paymentAccepted": "Cash, Check, Credit Card, CareCredit",
        "currenciesAccepted": "USD",
        "areaServed": [{"@type": "City", "name": n} for n in
                       ["Jupiter", "Tequesta", "Juno Beach", "Palm Beach Gardens", "North Palm Beach",
                        "Hobe Sound", "Jupiter Inlet Colony"]] + [{"@type": "Place", "name": "Abacoa"},
                                                                  {"@type": "Place", "name": "Jupiter Farms"}],
        "employee": {"@id": DOC_ID},
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Dental services",
            "itemListElement": [{"@type": "Offer", "itemOffered": {
                "@type": "MedicalProcedure", "name": s["name"], "url": "%s/services/%s/" % (BASE, s["slug"])}}
                for s in SERVICES]},
        "sameAs": [P["healthgrades_url"], P["npi_url"]],
    }


def doctor_node():
    return {
        "@type": "Person",
        "@id": DOC_ID,
        "name": P["doctor_full"],
        "givenName": "Angelo",
        "familyName": "Forte",
        "honorificPrefix": "Dr.",
        "honorificSuffix": "DMD",
        "jobTitle": "Dentist",
        "worksFor": {"@id": ORG_ID},
        "url": BASE + "/about/",
        "identifier": {"@type": "PropertyValue", "propertyID": "NPI", "value": P["npi"]},
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree",
             "name": "Doctor of Dental Medicine (DMD)"},
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "license",
             "name": "Florida dental license DN14440",
             "recognizedBy": {"@type": "GovernmentOrganization", "name": "Florida Board of Dentistry"}},
        ],
        "sameAs": [P["healthgrades_url"], P["npi_url"]],
    }


def website_node():
    return {"@type": "WebSite", "@id": SITE_ID, "url": BASE + "/", "name": P["name"],
            "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}


def breadcrumb_node(url, crumbs):
    return {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + p} for i, (n, p) in enumerate(crumbs)]}


def faq_node(url, faqs):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def graph(*nodes):
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context": "https://schema.org", "@graph": [n for n in nodes if n]}, ensure_ascii=False,
        separators=(",", ":")).replace("</", "<\\/")


# --- Page chrome --------------------------------------------------------------------

NAV = [
    ("Services", "/services/"),
    ("About", "/about/"),
    ("New patients", "/new-patients/"),
    ("Insurance", "/insurance-financing/"),
    ("Reviews", "/reviews/"),
    ("Contact", "/contact/"),
]


def tel(label=None, cls="", track="call"):
    return '<a class="%s" href="tel:%s" data-track="%s">%s</a>' % (
        cls, P["phone_e164"], track, label or P["phone"])


def header(path, dark_hero):
    groups = ""
    for gkey, glabel, _ in GROUPS:
        items = "".join('<li><a href="/services/%s/">%s</a></li>' % (s["slug"], esc(s["nav"]))
                        for s in SERVICES if s["group"] == gkey)
        groups += '<div class="mega-col"><p class="mega-h">%s</p><ul>%s</ul></div>' % (esc(glabel), items)
    links = ""
    for label, href in NAV:
        cur = ' aria-current="page"' if path == href else ""
        if href == "/services/":
            links += ('<li class="has-mega"><a href="/services/"%s>Services</a>'
                      '<button class="mega-btn" aria-expanded="false" aria-controls="mega" aria-label="Show all services">%s</button>'
                      '<div class="mega" id="mega"><div class="mega-in">%s'
                      '<a class="mega-all" href="/services/">All services %s</a></div></div></li>'
                      % (cur, icon("chev"), groups, icon("arrow")))
        else:
            links += '<li><a href="%s"%s>%s</a></li>' % (href, cur, label)
    return """
<a class="skip" href="#main">Skip to content</a>
<header class="site-header%s" data-header>
  <div class="hd-in">
    <a class="brand" href="/">%s<span class="sr">, home</span></a>
    <nav class="nav" aria-label="Main">
      <ul class="nav-list">%s</ul>
    </nav>
    <div class="hd-cta">
      %s
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="sheet" data-menu>
        <span class="menu-open">%s<span class="sr">Open menu</span></span>
        <span class="menu-close">%s<span class="sr">Close menu</span></span>
      </button>
    </div>
  </div>
  <div class="sheet" id="sheet" data-sheet>
    <nav aria-label="Mobile">
      <ul class="sheet-list">%s</ul>
      <div class="sheet-foot">
        %s
        <p>%s<br>%s, %s %s</p>
      </div>
    </nav>
  </div>
</header>""" % (
        " on-dark" if dark_hero else "", wordmark(), links,
        tel('%s<span>%s</span>' % (icon("phone"), P["phone"]), "btn btn-call hd-call"),
        icon("menu"), icon("close"),
        "".join('<li><a href="%s">%s</a></li>' % (h, l) for l, h in [("Home", "/")] + NAV),
        tel("Call %s" % P["phone"], "btn btn-primary btn-block"),
        esc(P["street"]), P["city"], P["region"], P["zip"])


def hours_list(cls="hours"):
    rows = "".join('<li><span>%s</span><span>%s</span></li>' % (d, "8:00 AM &ndash; 5:00 PM") for d, *_ in HOURS)
    rows += '<li><span>Friday</span><span>By appointment</span></li>'
    rows += '<li><span>Saturday &amp; Sunday</span><span>Closed</span></li>'
    return '<ul class="%s">%s</ul><p class="hours-note">Closed for lunch 1:00 &ndash; 2:00 PM, Monday to Thursday.</p>' % (cls, rows)


def cta_band(heading="Book a visit with Dr. Forte.", text=None):
    text = text or "Call the office to book a cleaning, a consultation or a first visit. If something hurts, say so when you call."
    return """
<section class="cta-band" aria-labelledby="cta-h">
  <div class="wrap cta-in">
    <div>
      <p class="eyebrow on-dark">%s &middot; Jupiter, FL</p>
      <h2 id="cta-h" class="display">%s</h2>
      <p class="cta-text">%s</p>
    </div>
    <div class="cta-actions">
      %s
      <a class="btn btn-ghost-light" href="/contact/">Directions &amp; hours %s</a>
    </div>
  </div>
</section>""" % (esc(P["street"]), heading, text,
                 tel('%s Call %s' % (icon("phone"), P["phone"]), "btn btn-sun btn-lg"), icon("arrow"))


def footer(path):
    svc = "".join('<li><a href="/services/%s/">%s</a></li>' % (s["slug"], esc(s["nav"])) for s in SERVICES)
    areas = "".join('<li><a href="/areas-we-serve/%s/">%s</a></li>' % (a["slug"], a["name"]) for a in AREAS)
    year = datetime.date.today().year
    return """
<footer class="site-footer">
  <div class="wrap ft-grid">
    <div class="ft-brand">
      <a class="brand" href="/">%s<span class="sr">, home</span></a>
      <p>General, restorative and cosmetic dentistry for families in Jupiter and the surrounding towns.</p>
      <address>
        <a href="%s" rel="noopener" target="_blank">%s<br>%s, %s %s<span class="sr"> (opens Google Maps in a new tab)</span></a>
      </address>
      <p class="ft-phone">%s<br><span class="muted">Fax %s</span></p>
    </div>
    <div>
      <p class="ft-h">Services</p>
      <ul class="ft-list cols">%s</ul>
    </div>
    <div>
      <p class="ft-h">Practice</p>
      <ul class="ft-list">
        <li><a href="/about/">About Dr. Forte</a></li>
        <li><a href="/new-patients/">New patients</a></li>
        <li><a href="/insurance-financing/">Insurance &amp; financing</a></li>
        <li><a href="/reviews/">Patient reviews</a></li>
        <li><a href="/faq/">Questions</a></li>
        <li><a href="/contact/">Contact &amp; directions</a></li>
      </ul>
      <p class="ft-h">Areas we serve</p>
      <ul class="ft-list">%s<li><a href="/areas-we-serve/">All areas</a></li></ul>
    </div>
    <div>
      <p class="ft-h">Hours</p>
      %s
    </div>
  </div>
  <div class="wrap ft-legal">
    <p>&copy; %d %s. All rights reserved.</p>
    <ul>
      <li><a href="/privacy/">Privacy</a></li>
      <li><a href="/accessibility/">Accessibility</a></li>
      <li><a href="/sitemap.xml">Sitemap</a></li>
    </ul>
  </div>
</footer>
<nav class="callbar" data-callbar aria-label="Quick contact">
  %s
  <a class="callbar-btn alt" href="/contact/">%s Directions</a>
</nav>""" % (wordmark(), P["maps_url"], esc(P["street"]), P["city"], P["region"], P["zip"],
             tel(P["phone"], "ft-tel"), P["fax"], svc, areas, hours_list("hours hours-ft"), year, esc(P["legal_name"]),
             tel('%s Call' % icon("phone"), "callbar-btn", "call-mobile-bar"), icon("pin"))


def head(path, title, desc, schema, og=None, preload_hero=False, noindex=False, analytics=True, extra_head=""):
    url = BASE + path
    og = og or "/assets/img/og/og-home.jpg"
    og_abs = SHARE_BASE + og
    pre = ""
    if preload_hero:
        # Poster is the LCP element: preload the variant each breakpoint will paint.
        # On phones the H1 text is the LCP element, so the poster must not compete with the fonts there.
        pre = ('<link rel="preload" as="image" type="image/avif" fetchpriority="high" media="(min-width: 768px)" '
               'imagesrcset="/assets/img/hero/inlet-poster-1280.avif 1280w, /assets/img/hero/inlet-poster-1920.avif 1920w" imagesizes="100vw">')
    if preload_hero:
        pre += '<link rel="preload" href="/assets/fonts/instrument-serif-italic-v2.woff2" as="font" type="font/woff2" crossorigin>'
    tracking = ""
    if analytics and GA4_ID:
        tracking += ('<script src="%s" data-ga="%s" defer></script>' % (A("/assets/js/consent.js"), esc(GA4_ID)))
    if analytics and VERCEL_ANALYTICS:
        tracking += '<script defer src="/_vercel/insights/script.js"></script><script defer src="/_vercel/speed-insights/script.js"></script>'
    robots = "noindex, follow" if noindex else "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
    return """<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="%s">
<meta name="robots" content="%s">
<link rel="canonical" href="%s">
<meta name="theme-color" content="#0B1B22">
<meta name="color-scheme" content="light dark">
<meta name="geo.region" content="US-FL"><meta name="geo.placename" content="Jupiter"><meta name="geo.position" content="%s;%s"><meta name="ICBM" content="%s, %s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%s">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="%s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%s">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/instrument-serif-v2.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-sans-v2.woff2" as="font" type="font/woff2" crossorigin>
%s
%s
<link rel="stylesheet" href="%s">
<script src="%s" defer></script>
%s
%s
%s
</head>""" % (esc(title), esc(desc), robots, url, P["lat"], P["lng"], P["lat"], P["lng"], esc(P["name"]),
               esc(title), esc(desc), url, og_abs, esc(title), esc(title), esc(desc), og_abs,
               pre, JS_FLAG, A("/assets/css/site.css"), A("/assets/js/site.js"), tracking, extra_head, schema)


def write(path, doc):
    rel = "index.html" if path == "/" else (path.strip("/") + "/index.html" if path.endswith("/") else path.lstrip("/"))
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    doc = re.sub(r"\n\s*\n+", "\n", doc)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)
    return rel


def page(path, title, desc, body, schema_nodes, crumbs=None, og=None, dark_hero=False, preload_hero=False,
         noindex=False, analytics=True, sitemap=True, extra_head=""):
    url = BASE + path
    # The practice and Dr. Forte are on every page so each graph is self-contained.
    nodes = [website_node(), org_node(), doctor_node()] + [n for n in schema_nodes if n.get("@id") != DOC_ID]
    if crumbs:
        nodes.append(breadcrumb_node(url, crumbs))
    doc = (head(path, title, desc, graph(*nodes), og, preload_hero, noindex, analytics, extra_head)
           + '<body class="%s">' % ("has-dark-hero" if dark_hero else "")
           + header(path, dark_hero)
           + '<main id="main" tabindex="-1">' + body + "</main>"
           + footer(path) + "</body></html>")
    rel = write(path, doc)
    if sitemap and not noindex:
        WRITTEN.append((path, rel))
        PAGES_META.append((path, title))
    return rel


def webpage_node(path, title, desc, kind="WebPage", about=None, extra=None, crumbs=True):
    url = BASE + path
    n = {"@type": kind, "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "isPartOf": {"@id": SITE_ID}, "inLanguage": "en-US",
         "dateModified": page_lastmod(("index.html" if path == "/" else path.strip("/") + "/index.html"))}
    if crumbs and path != "/":
        n["breadcrumb"] = {"@id": url + "#breadcrumb"}
    if about:
        n["about"] = about
    if extra:
        n.update(extra)
    return n


def crumbs_html(crumbs):
    items = []
    for i, (name, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            items.append('<li aria-current="page">%s</li>' % esc(name))
        else:
            items.append('<li><a href="%s">%s</a></li>' % (href, esc(name)))
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>%s</ol></nav>' % "".join(items)


def page_hero(crumbs, lead, h1, lede, actions=True, aside=""):
    acts = ""
    if actions:
        acts = '<div class="ph-actions">%s<a class="btn btn-quiet" href="/contact/">Hours &amp; directions %s</a></div>' % (
            tel('%s Call %s' % (icon("phone"), P["phone"]), "btn btn-primary"), icon("arrow"))
    return """
<section class="page-hero">
  <div class="ph-glow" aria-hidden="true"></div>
  <div class="wrap ph-in%s">
    <div class="ph-copy">
      %s
      <h1><span class="h1-lead">%s</span> <span class="h1-main">%s</span></h1>
      <p class="lede">%s</p>
      %s
    </div>
    %s
  </div>
</section>""" % (" has-aside" if aside else "", crumbs_html(crumbs), esc(lead), h1, lede, acts, aside)


def faq_block(faqs, heading="Questions patients ask", hid="faq-h", intro=""):
    items = "".join(
        '<details class="qa rv"><summary><span>%s</span>%s</summary><div class="qa-a"><p>%s</p></div></details>'
        % (esc(q), icon("chev", "ic qa-ic"), esc(a)) for q, a in faqs)
    return """
<section class="section faq" aria-labelledby="%s">
  <div class="wrap faq-grid">
    <div class="faq-head rv">
      <p class="eyebrow">FAQ</p>
      <h2 id="%s" class="display-sm">%s</h2>
      %s
      <p class="faq-call">Still wondering? %s</p>
    </div>
    <div class="qa-list">%s</div>
  </div>
</section>""" % (hid, hid, heading, ('<p class="muted">%s</p>' % intro) if intro else "",
                 tel("Call %s" % P["phone"], "link-strong"), items)


def testimonial_cards(items, cls="quotes"):
    out = ""
    for i, (q, who) in enumerate(items):
        out += ('<figure class="quote rv" style="--i:%d"><blockquote><p>%s</p></blockquote>'
                '<figcaption>%s</figcaption></figure>' % (i % 4, esc(q), esc(who)))
    return '<div class="%s">%s</div>' % (cls, out)


def live_reviews_slot():
    """Filled by site.js from /api/reviews when GOOGLE_PLACES_API_KEY is set; stays hidden otherwise."""
    return '<div class="g-reviews" data-greviews hidden aria-live="polite"></div>'


# --- Pages --------------------------------------------------------------------------

def build_home():
    path = "/"
    title = "Dentist in Jupiter, FL | Angelo Forte, DMD | Indiantown Rd"
    desc = ("Angelo Forte, DMD is a general and cosmetic dentist in Jupiter, FL: cleanings, crowns, implants, "
            "veneers, whitening, Invisalign and emergency care. Call (561) 747-2134.")
    services_marquee = "".join('<li>%s</li>' % esc(s["name"]) for s in SERVICES)
    intents = "".join(
        '<a class="intent rv" style="--i:%d" href="/services/%s/"><span class="intent-n">%02d</span>'
        '<span class="intent-t">%s</span><span class="intent-d">%s</span><span class="intent-go">%s</span></a>'
        % (i % 3, slug, i + 1, esc(t), esc(d), icon("arrow")) for i, (t, d, slug) in enumerate(INTENTS))
    groups_html = ""
    for gi, (gkey, glabel, gname) in enumerate(GROUPS):
        items = "".join('<li><a href="/services/%s/"><span>%s</span>%s</a></li>' % (s["slug"], esc(s["name"]), icon("arrow"))
                        for s in SERVICES if s["group"] == gkey)
        groups_html += ('<div class="svc-group rv" style="--i:%d"><p class="svc-k">%s</p><h3>%s</h3><ul>%s</ul></div>'
                        % (gi % 3, esc(gname), esc(glabel), items))
    strip = strip_manifest()
    def strip_li(m, dup):
        return '<li class="strip-item" style="--ar:%d/%d"%s>%s</li>' % (
            m["w"], m["h"], ' aria-hidden="true"' if dup else "",
            picture("/assets/img/strip/" + m["slug"], [480, 960], "" if dup else m["alt"],
                    "(max-width: 767px) 60vw, 28vw", w=m["w"], h=m["h"]))
    # The second copy exists only so the loop is seamless; it is hidden from assistive tech.
    strip_items = "".join(strip_li(m, False) for m in strip) + "".join(strip_li(m, True) for m in strip)
    statement = ("Our philosophy is to treat the whole person, with a special focus on how your teeth and gums "
                 "relate to your total body health.")
    words = " ".join('<span class="w">%s</span>' % esc(w) for w in statement.split())
    nearby = "".join('<li><span>%s</span><span>%s mi &middot; ~%d min</span></li>' % (n, m, t) for n, m, t in NEARBY[:4])
    home_faqs = FAQS[:HOME_FAQ_COUNT]
    body = """
<section class="hero" aria-labelledby="hero-h">
  <div class="hero-media" aria-hidden="true">
    <picture class="hero-poster">
      <source media="(max-width: 767px)" type="image/avif" srcset="/assets/img/hero/inlet-poster-portrait-720.avif 720w, /assets/img/hero/inlet-poster-portrait-1080.avif 1080w" sizes="100vw">
      <source media="(max-width: 767px)" type="image/webp" srcset="/assets/img/hero/inlet-poster-portrait-720.webp 720w, /assets/img/hero/inlet-poster-portrait-1080.webp 1080w" sizes="100vw">
      <source media="(max-width: 767px)" srcset="/assets/img/hero/inlet-poster-portrait-720.jpg 720w, /assets/img/hero/inlet-poster-portrait-1080.jpg 1080w" sizes="100vw">
      <source type="image/avif" srcset="/assets/img/hero/inlet-poster-1280.avif 1280w, /assets/img/hero/inlet-poster-1920.avif 1920w" sizes="100vw">
      <source type="image/webp" srcset="/assets/img/hero/inlet-poster-1280.webp 1280w, /assets/img/hero/inlet-poster-1920.webp 1920w" sizes="100vw">
      <img src="/assets/img/hero/inlet-poster-1920.jpg" srcset="/assets/img/hero/inlet-poster-1280.jpg 1280w, /assets/img/hero/inlet-poster-1920.jpg 1920w" sizes="100vw" alt="" width="1920" height="1080" fetchpriority="low">
    </picture>
    <video class="hero-video" muted loop playsinline preload="none" disablepictureinpicture
      data-src-1080="%s" data-src-720="%s" data-src-av1="%s" data-src-portrait="%s" data-src-portrait-av1="%s"></video>
  </div>
  <div class="wrap hero-in">
    <h1 id="hero-h" class="hero-h">
      <span class="h1-lead"><span class="dot" aria-hidden="true"></span>Dentist in Jupiter, FL &middot; General &amp; cosmetic care</span>
      <span class="hero-line"><span>A neighborhood dentist</span></span>
      <span class="hero-line"><span>with <em>exacting</em> standards.</span></span>
    </h1>
    <p class="hero-lede">Dr. Angelo Forte and his team look after cleanings, fillings, crowns, implants, veneers, whitening and Invisalign from one office on Indiantown Road, and they help when a tooth breaks or starts to hurt.</p>
    <div class="hero-actions">
      %s
      <a class="btn btn-ghost-light btn-lg" href="/new-patients/">First visit? Start here %s</a>
    </div>
    <ul class="hero-facts">
      <li>%s<span>%s, Jupiter</span></li>
      <li>%s<span>Mon&ndash;Thu 8&ndash;5 &middot; Fri by appointment</span></li>
      <li>%s<span>Most traditional insurance filed for you</span></li>
    </ul>
  </div>
  <button class="hero-toggle" type="button" data-video-toggle hidden aria-pressed="false">
    <span class="t-pause">%s<span class="sr">Pause background video</span></span>
    <span class="t-play">%s<span class="sr">Play background video</span></span>
  </button>
</section>

<div class="ticker" aria-hidden="true"><ul class="ticker-track">%s</ul></div>

<section class="section intents" aria-labelledby="intents-h">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Where to start</p>
      <h2 id="intents-h" class="display">What brings you in?</h2>
      <p class="sec-lede">Pick the closest match. Each page explains what the visit involves, what it can and can't do, and what to ask.</p>
    </div>
    <div class="intent-grid">%s</div>
  </div>
</section>

<section class="statement" aria-label="Practice philosophy">
  <div class="wrap">
    <p class="statement-text" data-words>%s</p>
    <p class="statement-src">From the practice&rsquo;s welcome to new patients</p>
  </div>
</section>

<section class="section doctor" aria-labelledby="doc-h">
  <div class="wrap doctor-grid">
    <div class="doc-card rv" aria-hidden="true">
      <div class="doc-mono">
        <span class="doc-initials">AF</span>
        <span class="doc-ring"></span>
      </div>
      <p class="doc-card-name">Angelo G. Forte, DMD</p>
      <p class="doc-card-sub">Doctor of Dental Medicine</p>
    </div>
    <div class="doc-copy rv" style="--i:1">
      <p class="eyebrow">Your dentist</p>
      <h2 id="doc-h" class="display">Dr. Angelo Forte</h2>
      <p class="big">At Angelo Forte, DMD the aim is to make sure your smile meets your goals for comfort, function and appearance, and that you understand every step of the way there.</p>
      <p>From the moment you walk in, you are looked after by a caring team in a relaxed setting where the whole family can feel at ease. Patients describe Dr. Forte as kind, caring and smart, and more than one says he &ldquo;knows his stuff.&rdquo;</p>
      <dl class="creds">
        <div><dt>Degree</dt><dd>Doctor of Dental Medicine (DMD)</dd></div>
        <div><dt>Florida license</dt><dd>DN14440 &middot; <a href="%s" rel="noopener" target="_blank">Verify<span class="sr"> (Florida Department of Health, opens in a new tab)</span></a></dd></div>
        <div><dt>NPI</dt><dd>%s</dd></div>
      </dl>
      <a class="link-arrow" href="/about/">More about the practice %s</a>
    </div>
  </div>
</section>

<section class="section steps-sec" aria-labelledby="steps-h">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">How it works</p>
      <h2 id="steps-h" class="display">Your first visit, step by step.</h2>
    </div>
    <ol class="steps">
      <li class="step rv"><span class="step-n">1</span><h3>Call the office</h3><p>Ring %s. The team takes your details and insurance information and finds a time that suits you.</p></li>
      <li class="step rv" style="--i:1"><span class="step-n">2</span><h3>Get to know each other</h3><p>Your first visit covers your medical and dental history, an exam and digital X-rays, and time to talk about any concerns.</p></li>
      <li class="step rv" style="--i:2"><span class="step-n">3</span><h3>A plan you understand</h3><p>Dr. Forte explains what he found and your options. The office files your insurance and walks you through payment choices.</p></li>
    </ol>
  </div>
</section>

<section class="section svc-sec" aria-labelledby="svc-h">
  <div class="wrap svc-layout">
    <div class="svc-intro rv">
      <p class="eyebrow">Services</p>
      <h2 id="svc-h" class="display">All of your routine dental needs, in one place.</h2>
      <p>From regular cleanings and exams to advanced restorative treatment, the practice handles it under one roof, so your history, X-rays and plan stay together.</p>
      <a class="btn btn-primary" href="/services/">See every service %s</a>
    </div>
    <div class="svc-groups">%s</div>
  </div>
</section>

<section class="section money" aria-labelledby="money-h">
  <div class="wrap money-grid">
    <div class="rv">
      <p class="eyebrow">Insurance &amp; payment</p>
      <h2 id="money-h" class="display-sm">Straight answers about cost.</h2>
      <p>The practice accepts most traditional insurance plans and files your claims for you. It does not take part in HMO plans, but if your plan lets you choose your own dentist, the office will file for your reimbursement.</p>
      <a class="link-arrow" href="/insurance-financing/">Insurance &amp; financing %s</a>
    </div>
    <ul class="money-list">
      <li class="rv">%s<div><h3>Claims filed for you</h3><p>Bring your card; the office handles the paperwork.</p></div></li>
      <li class="rv" style="--i:1">%s<div><h3>CareCredit financing</h3><p>For treatment your insurance doesn&rsquo;t cover.</p></div></li>
      <li class="rv" style="--i:2">%s<div><h3>Flexible payment plan</h3><p>Ask the Financial Coordinator how it works.</p></div></li>
    </ul>
  </div>
</section>

<section class="section reviews-sec" aria-labelledby="rev-h">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow on-dark">In their words</p>
      <h2 id="rev-h" class="display">&ldquo;He truly cares about his patients.&rdquo;</h2>
      <p class="sec-lede">Patient testimonials published by the practice, quoted exactly as written.</p>
    </div>
    %s
    %s
    <a class="btn btn-ghost-light" href="/reviews/">Read all reviews %s</a>
  </div>
</section>

<section class="section visit" aria-labelledby="visit-h">
  <div class="wrap visit-grid">
    <div class="rv">
      <p class="eyebrow">Find us</p>
      <h2 id="visit-h" class="display-sm">654 W. Indiantown Road, Suite 105</h2>
      <p>On Indiantown Road in Jupiter, a short way east of Military Trail and about a mile from Alternate A1A and US-1.</p>
      <ul class="nearby">%s</ul>
      <p class="fine">Drive times are routing estimates outside rush hour.</p>
      <div class="visit-actions">
        <a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%s Get directions<span class="sr"> (opens Google Maps in a new tab)</span></a>
        %s
      </div>
    </div>
    <figure class="route-map rv" style="--i:1">
      %s
      <figcaption>Not to scale. Distances measured along Indiantown Road.</figcaption>
    </figure>
  </div>
</section>

%s

<section class="strip-sec" aria-labelledby="strip-h">
  <div class="wrap strip-head">
    <h2 id="strip-h" class="eyebrow">Jupiter, from above</h2>
    <button class="strip-toggle" type="button" data-strip-toggle aria-pressed="false">
      <span class="t-pause">%s Pause</span><span class="t-play">%s Play</span>
    </button>
  </div>
  <div class="strip" data-strip>
    <ul class="strip-track">%s</ul>
  </div>
</section>
%s""" % (
        A("/assets/video/inlet-1080.mp4"), A("/assets/video/inlet-720.mp4"), A("/assets/video/inlet-1080.webm"),
        A("/assets/video/inlet-portrait.mp4"), A("/assets/video/inlet-portrait.webm"),
        tel('%s Call %s' % (icon("phone"), P["phone"]), "btn btn-sun btn-lg", "call-hero"), icon("arrow"),
        icon("pin"), "654 W. Indiantown Rd.", icon("clock"), icon("shield"),
        icon("pause"), icon("play"),
        services_marquee * 2,
        intents,
        words,
        P["license_verify_url"], P["npi"], icon("arrow"),
        tel(), icon("arrow"), groups_html, icon("arrow"),
        icon("shield"), icon("card"), icon("calendar"),
        testimonial_cards(TESTIMONIALS[:3], "quotes quotes-3"), live_reviews_slot(), icon("arrow"),
        nearby, P["maps_url"], icon("map"), tel("Call %s" % P["phone"], "btn btn-quiet"), route_svg(),
        faq_block(home_faqs, "Quick answers", "home-faq-h"),
        icon("pause"), icon("play"), strip_items,
        cta_band())
    schema = [webpage_node(path, title, desc, about={"@id": ORG_ID}, extra={
        "primaryImageOfPage": SHARE_BASE + "/assets/img/og/og-home.jpg",
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".hero-h", ".hero-lede"]}}),
              doctor_node(), faq_node(BASE + path, home_faqs)]
    page(path, title, desc, body, schema, dark_hero=True, preload_hero=True)


def route_svg():
    """Schematic of Indiantown Road around the office. Distances from OSRM routes."""
    return """<svg class="route" viewBox="0 0 560 300" role="img" aria-labelledby="route-t route-d">
  <title id="route-t">Map sketch of the office location</title>
  <desc id="route-d">Indiantown Road runs east to west. Military Trail crosses it about 0.2 miles west of the office. Alternate A1A crosses about 0.7 miles east, and US-1 just beyond that.</desc>
  <defs><linearGradient id="rg" x1="0" x2="1"><stop offset="0" stop-color="var(--map-land)"/><stop offset="1" stop-color="var(--map-land2)"/></linearGradient></defs>
  <rect width="560" height="300" rx="18" fill="url(#rg)"/>
  <path d="M520 0 C 500 80, 530 160, 505 300 L560 300 L560 0 Z" fill="var(--map-water)"/>
  <path d="M0 150 H560" stroke="var(--map-road)" stroke-width="14" stroke-linecap="round"/>
  <path d="M0 150 H560" stroke="var(--map-road-c)" stroke-width="1.5" stroke-dasharray="8 8"/>
  <path d="M150 0 V300" stroke="var(--map-road2)" stroke-width="9"/>
  <path d="M398 0 C 400 90, 395 200, 404 300" stroke="var(--map-road2)" stroke-width="8" fill="none"/>
  <path d="M452 0 C 448 100, 456 200, 450 300" stroke="var(--map-road2)" stroke-width="9" fill="none"/>
  <g class="route-labels" font-family="Instrument Sans, system-ui, sans-serif" font-size="13" fill="var(--map-text)">
    <text x="16" y="138">Indiantown Rd</text>
    <text x="158" y="22">Military Trail</text>
    <text x="300" y="285">Alt A1A</text>
    <text x="460" y="22">US-1</text>
    <text x="508" y="292" font-size="11" opacity=".8">ICW</text>
  </g>
  <g class="pin">
    <circle cx="196" cy="150" r="30" fill="var(--sun)" opacity=".18"><animate attributeName="r" values="18;34;18" dur="3.2s" repeatCount="indefinite"/></circle>
    <circle cx="196" cy="150" r="11" fill="var(--sun)" stroke="var(--ink)" stroke-width="3"/>
    <rect x="166" y="170" width="132" height="44" rx="10" fill="var(--ink)"/>
    <text x="178" y="189" font-family="Instrument Sans, system-ui, sans-serif" font-size="13" font-weight="600" fill="#fff">Angelo Forte, DMD</text>
    <text x="178" y="205" font-family="Instrument Sans, system-ui, sans-serif" font-size="11" fill="#cfe0dd">654 W. Indiantown Rd.</text>
  </g>
  <g font-family="Instrument Sans, system-ui, sans-serif" font-size="11" fill="var(--map-text)" opacity=".85">
    <text x="156" y="122">0.2 mi</text>
    <text x="280" y="122">0.7 mi to Alt A1A</text>
  </g>
  <g transform="translate(520 54)" font-family="Instrument Sans, system-ui, sans-serif" font-size="11" fill="var(--map-text)"><path d="M0 -14 L6 4 L0 0 L-6 4 Z" fill="currentColor"/><text x="-4" y="18">N</text></g>
</svg>"""


def build_services_hub():
    path = "/services/"
    title = "Dental Services in Jupiter, FL | Angelo Forte, DMD"
    desc = ("Cleanings, fillings, crowns, implants, veneers, whitening, Invisalign, root canals, gum care, "
            "dentures, TMJ and emergency care at Angelo Forte, DMD in Jupiter, FL.")
    crumbs = [("Home", "/"), ("Services", "/services/")]
    groups = ""
    for gkey, glabel, gname in GROUPS:
        cards = "".join(
            '<a class="svc-card rv" style="--i:%d" href="/services/%s/"><h3>%s</h3><p>%s</p><span class="svc-go">%s</span></a>'
            % (i % 3, s["slug"], esc(s["name"]), esc(s["short"]), icon("arrow"))
            for i, s in enumerate([s for s in SERVICES if s["group"] == gkey]))
        groups += ('<section class="svc-block" aria-labelledby="g-%s"><div class="svc-block-head rv"><p class="eyebrow">%s</p>'
                   '<h2 id="g-%s" class="display-sm">%s</h2></div><div class="svc-cards">%s</div></section>'
                   % (gkey, esc(gname), gkey, esc(glabel), cards))
    body = page_hero(crumbs, "Dental services in Jupiter", "Everything your teeth need, under one roof.",
                     "Regular dental visits catch problems, from tooth decay to oral cancer, while they are small. When more is needed, the practice handles restorative and cosmetic treatment in the same office.") + \
        '<div class="section"><div class="wrap">%s</div></div>' % groups + cta_band()
    schema = [webpage_node(path, title, desc, "CollectionPage", extra={"mainEntity": {
        "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": "%s/services/%s/" % (BASE, s["slug"]),
                                                  "name": s["name"]} for i, s in enumerate(SERVICES)]}})]
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-services.jpg")


def build_service(s):
    path = "/services/%s/" % s["slug"]
    crumbs = [("Home", "/"), ("Services", "/services/"), (s["name"], path)]
    toc = "".join('<li><a href="#s%d">%s</a></li>' % (i, esc(h)) for i, (h, _) in enumerate(s["sections"]))
    sections = "".join('<section class="prose-sec rv" id="s%d" aria-labelledby="s%d-h"><h2 id="s%d-h">%s</h2>%s</section>'
                       % (i, i, i, esc(h), body) for i, (h, body) in enumerate(s["sections"]))
    related = "".join('<li><a href="/services/%s/"><span>%s</span><small>%s</small>%s</a></li>'
                      % (r, esc(SVC[r]["name"]), esc(SVC[r]["short"]), icon("arrow")) for r in s["related"])
    aside = """<aside class="ph-card rv" aria-label="Book this visit">
  <p class="ph-card-k">Book by phone</p>
  %s
  <p class="ph-card-m">%s<br>Mon&ndash;Thu 8:00 AM&ndash;5:00 PM<br>Fri by appointment</p>
  <a class="link-arrow" href="/insurance-financing/">Insurance &amp; financing %s</a>
</aside>""" % (tel(P["phone"], "ph-card-tel", "call-service"), esc(P["street"]), icon("arrow"))
    body = page_hero(crumbs, s["h1_lead"], esc(s["h1"]), esc(s["lede"]), aside=aside) + """
<div class="section article">
  <div class="wrap article-grid">
    <nav class="toc" aria-label="On this page"><p class="toc-h">On this page</p><ol>%s<li><a href="#faq-h">Questions</a></li></ol></nav>
    <div class="prose">%s
      <p class="review-note">This page explains treatment in general terms. It isn&rsquo;t a diagnosis; Dr. Forte will tell you what applies to you after an exam.</p>
    </div>
  </div>
</div>
%s
<section class="section related" aria-labelledby="rel-h">
  <div class="wrap">
    <h2 id="rel-h" class="display-sm rv">Often considered alongside</h2>
    <ul class="related-list">%s</ul>
  </div>
</section>
%s""" % (toc, sections, faq_block(s["faqs"]), related, cta_band())
    procedure = {"@type": "MedicalProcedure", "@id": BASE + path + "#procedure", "name": s["name"],
                 "description": s["lede"], "url": BASE + path,
                 "relevantSpecialty": "https://schema.org/Dentistry",
                 "provider": {"@id": ORG_ID}}
    about = [{"@id": BASE + path + "#procedure"}] + [{"@type": "MedicalCondition", "name": c} for c in s["about"]]
    schema = [webpage_node(path, s["title"], s["desc"], "MedicalWebPage", about=about, extra={
        "specialty": "https://schema.org/Dentistry", "audience": {"@type": "Patient"},
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".page-hero h1", ".page-hero .lede"]}}),
              procedure, faq_node(BASE + path, s["faqs"])]
    page(path, s["title"], s["desc"], body, schema, crumbs, og="/assets/img/og/og-%s.jpg" % s["slug"])


def build_about():
    path = "/about/"
    title = "Dr. Angelo Forte, DMD | About Our Jupiter Dental Practice"
    desc = ("Meet Dr. Angelo Forte, DMD, and the practice on W. Indiantown Rd. in Jupiter, FL: its approach to "
            "whole-person dental care, its mission and its team. Call (561) 747-2134.")
    crumbs = [("Home", "/"), ("About", "/about/")]
    mission = ["Listening to those we are privileged to serve.",
               "Earning the trust and respect of patients, profession and community.",
               "Exceeding your expectations.",
               "Keeping a creative, challenging and compassionate professional environment.",
               "Striving for continuous improvement at all levels."]
    body = page_hero(crumbs, "About Dr. Angelo Forte, DMD", "Whole-person dentistry, in Jupiter.",
                     "The practice's philosophy is to treat the whole person, with a special focus on how your teeth and gums relate to your total body health.") + """
<section class="section" aria-labelledby="dr-h">
  <div class="wrap doctor-grid">
    <div class="doc-card rv" aria-hidden="true">
      <div class="doc-mono"><span class="doc-initials">AF</span><span class="doc-ring"></span></div>
      <p class="doc-card-name">Angelo G. Forte, DMD</p>
      <p class="doc-card-sub">General &amp; cosmetic dentistry</p>
    </div>
    <div class="prose rv" style="--i:1">
      <h2 id="dr-h" class="display-sm">Dr. Angelo Forte</h2>
      <p>Dr. Forte practices general, restorative and cosmetic dentistry at 654 W. Indiantown Road in Jupiter. He wants every patient to be confident that their smile meets their goals for comfort, function and appearance.</p>
      <p>Choosing a dentist is an important decision; your smile says a lot about your overall health. The practice uses up-to-date dental technology and techniques, including digital X-rays and Invisalign clear aligners, so it can offer thorough preventive care and treatment close to home.</p>
      <p>Patients who have written about Dr. Forte return to the same few words: kind, caring, and that he &ldquo;knows his stuff.&rdquo; One wrote that he &ldquo;truly cares about his patients and does what is best for the patient.&rdquo;</p>
      <dl class="creds">
        <div><dt>Degree</dt><dd>Doctor of Dental Medicine (DMD)</dd></div>
        <div><dt>Florida dental license</dt><dd>DN14440 &middot; <a href="%s" target="_blank" rel="noopener">Look it up<span class="sr"> (Florida Department of Health, opens in a new tab)</span></a></dd></div>
        <div><dt>National Provider Identifier</dt><dd><a href="%s" target="_blank" rel="noopener">%s<span class="sr"> (NPI registry, opens in a new tab)</span></a></dd></div>
        <div><dt>Practice</dt><dd>%s</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section mission" aria-labelledby="mission-h">
  <div class="wrap mission-grid">
    <div class="rv">
      <p class="eyebrow on-dark">Mission</p>
      <h2 id="mission-h" class="display">Uncompromising excellence in dentistry.</h2>
      <p>The practice works toward a shared vision of uncompromising excellence. To get there, the team commits to:</p>
    </div>
    <ol class="mission-list">%s</ol>
  </div>
</section>

<section class="section" aria-labelledby="team-h">
  <div class="wrap two-col">
    <div class="rv">
      <p class="eyebrow">The team</p>
      <h2 id="team-h" class="display-sm">A caring team in a relaxed office.</h2>
    </div>
    <div class="prose rv" style="--i:1">
      <p>Everyone at the practice keeps up their training and continuing education to stay current with dentistry. From the moment you walk in you will be welcomed by the team in a relaxed, stress-free setting where the whole family can feel at ease.</p>
      <p>The office has a Financial Coordinator who can explain insurance benefits, CareCredit financing and the practice's flexible payment plan before treatment starts.</p>
      <p><a class="link-arrow" href="/new-patients/">What to expect at your first visit %s</a></p>
    </div>
  </div>
</section>
%s
%s""" % (P["license_verify_url"], P["npi_url"], P["npi"], esc(P["legal_name"]),
         "".join('<li class="rv" style="--i:%d"><span>%02d</span>%s</li>' % (i % 3, i + 1, esc(m)) for i, m in enumerate(mission)),
         icon("arrow"),
         '<section class="section reviews-sec" aria-label="Patient testimonials"><div class="wrap">%s<a class="btn btn-ghost-light" href="/reviews/">All reviews %s</a></div></section>'
         % (testimonial_cards(TESTIMONIALS[1:4], "quotes quotes-3"), icon("arrow")),
         cta_band())
    schema = [webpage_node(path, title, desc, "AboutPage", about={"@id": DOC_ID}, extra={"mainEntity": {"@id": DOC_ID}}),
              doctor_node()]
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-about.jpg")


def build_new_patients():
    path = "/new-patients/"
    title = "New Patients | Your First Dental Visit in Jupiter, FL"
    desc = ("New to Angelo Forte, DMD? What happens at your first dental visit in Jupiter, what to bring, "
            "insurance and payment, and how to book. Call (561) 747-2134.")
    crumbs = [("Home", "/"), ("New patients", "/new-patients/")]
    bring = ["Your dental insurance card and a photo ID",
             "A list of the medications and supplements you take",
             "Any recent X-rays or records from your previous dentist, if you have them",
             "Questions you want to ask; write them down so none get forgotten"]
    body = page_hero(crumbs, "New patients in Jupiter", "Your first visit sets the foundation.",
                     "Your first visit is where we learn your medical history, look carefully at your teeth and gums, and give you time to get to know your dentist. Here is what to expect.") + """
<section class="section" aria-labelledby="first-h">
  <div class="wrap">
    <div class="sec-head rv"><p class="eyebrow">At the visit</p><h2 id="first-h" class="display-sm">What happens at your first appointment</h2></div>
    <ol class="steps steps-4">
      <li class="step rv"><span class="step-n">1</span><h3>Your history</h3><p>Your medical and dental history and medications, because your general health and your mouth affect each other.</p></li>
      <li class="step rv" style="--i:1"><span class="step-n">2</span><h3>An exam</h3><p>Teeth, gums, bite and the soft tissues of the mouth, including an oral cancer screening.</p></li>
      <li class="step rv" style="--i:2"><span class="step-n">3</span><h3>Digital X-rays</h3><p>When they are due, so problems between teeth and below the gumline aren&rsquo;t missed.</p></li>
      <li class="step rv" style="--i:3"><span class="step-n">4</span><h3>Your options</h3><p>What Dr. Forte found, what he recommends and why, and what insurance is likely to cover.</p></li>
    </ol>
  </div>
</section>
<section class="section tint" aria-labelledby="bring-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">Before you come</p><h2 id="bring-h" class="display-sm">What to bring</h2>
      <p>Being prepared means Dr. Forte has everything he needs, and it can take some of the nerves out of the visit too.</p></div>
    <ul class="checklist rv" style="--i:1">%s</ul>
  </div>
</section>
<section class="section" aria-labelledby="forms-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">Paperwork</p><h2 id="forms-h" class="display-sm">Patient forms</h2></div>
    <div class="prose rv" style="--i:1">
      <p>Printable new-patient forms will be posted here. Until then, arrive a little early for your first appointment to complete them at the office, or call %s to ask about filling them in ahead of time.</p>
      <p>If you can&rsquo;t keep an appointment or are running late, please call as soon as you can.</p>
    </div>
  </div>
</section>
<section class="section tint" aria-labelledby="hours-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">When</p><h2 id="hours-h" class="display-sm">Office hours</h2>
      <p>%s<br>%s, %s %s</p></div>
    <div class="rv" style="--i:1">%s</div>
  </div>
</section>
%s
%s""" % ("".join('<li>%s<span>%s</span></li>' % (icon("tooth"), esc(b)) for b in bring), tel(),
         esc(P["street"]), P["city"], P["region"], P["zip"], hours_list(),
         faq_block([FAQS[0], FAQS[3], FAQS[5], FAQS[7]]), cta_band("Book your first visit."))
    schema = [webpage_node(path, title, desc, about={"@id": ORG_ID}), faq_node(BASE + path, [FAQS[0], FAQS[3], FAQS[5], FAQS[7]])]
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-new-patients.jpg")


def build_insurance():
    path = "/insurance-financing/"
    title = "Dental Insurance & Financing | Angelo Forte, DMD, Jupiter"
    desc = ("Angelo Forte, DMD in Jupiter accepts most traditional dental insurance, files claims for you and "
            "offers CareCredit financing and a flexible payment plan. No HMO plans.")
    crumbs = [("Home", "/"), ("Insurance & financing", "/insurance-financing/")]
    faqs = [FAQS[3], FAQS[4], FAQS[5],
            ("Does insurance cover dental implants or veneers?", "It depends on your plan. Many plans cover part of restorative treatment such as crowns and sometimes implants, while purely cosmetic work like whitening and veneers is often not covered. The office will check your benefits with you before treatment."),
            ("What is CareCredit?", "CareCredit is a health care credit card you apply for separately. Depending on the offer, it can spread the cost of treatment over time. See carecredit.com for terms; the office can tell you more.")]
    body = page_hero(crumbs, "Dental insurance & financing", "Know the cost before you start.",
                     "The practice accepts most traditional insurance plans and files your claims for you. Payment options and financing cover the rest.") + """
<section class="section" aria-labelledby="ins-h">
  <div class="wrap money-cards">
    <article class="mcard rv">%s<h2 id="ins-h">Insurance</h2>
      <p>Most traditional dental insurance plans are accepted. Call with your plan details and the office will verify your coverage.</p>
      <p>The practice does not participate in Health Maintenance Organizations (HMOs). If your plan allows you to choose your own dentist, the office will gladly file your insurance claim for your reimbursement.</p></article>
    <article class="mcard rv" style="--i:1">%s<h2>Payment</h2>
      <p>Cash, checks and credit cards are accepted. A flexible payment plan is available; the Financial Coordinator can explain how it works and whether it fits your treatment.</p></article>
    <article class="mcard rv" style="--i:2">%s<h2>CareCredit financing</h2>
      <p>CareCredit is a health care credit card that can help with treatment your insurance doesn&rsquo;t cover. Promotional financing may be available on qualifying purchases, subject to credit approval.</p>
      <p><a class="link-arrow" href="https://www.carecredit.com/" target="_blank" rel="noopener">Learn more at carecredit.com<span class="sr"> (opens in a new tab)</span> %s</a></p></article>
  </div>
</section>
<section class="section tint" aria-labelledby="est-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">No surprises</p><h2 id="est-h" class="display-sm">Talk it through first</h2></div>
    <div class="prose rv" style="--i:1">
      <p>Before treatment begins, Dr. Forte explains what he recommends and why, and the office goes over what your insurance is expected to cover and what you will owe. Benefits differ from plan to plan, so the figure from the office is an estimate until your insurer processes the claim.</p>
      <p>If cost is a concern, say so. There is often more than one way to treat a problem, and Dr. Forte will explain the trade-offs.</p>
    </div>
  </div>
</section>
%s
%s""" % (icon("shield", "ic ic-lg"), icon("card", "ic ic-lg"), icon("calendar", "ic ic-lg"), icon("arrow"),
         faq_block(faqs), cta_band("Check your coverage with one call."))
    schema = [webpage_node(path, title, desc, about={"@id": ORG_ID}), faq_node(BASE + path, faqs)]
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-insurance.jpg")


def build_reviews():
    path = "/reviews/"
    title = "Patient Reviews | Angelo Forte, DMD, Dentist in Jupiter, FL"
    desc = ("Read what patients say about Dr. Angelo Forte and his team in Jupiter, FL, in their own words, "
            "and find out where to leave a review of your own visit.")
    crumbs = [("Home", "/"), ("Reviews", "/reviews/")]
    body = page_hero(crumbs, "Patient reviews", "In their own words.",
                     "Testimonials the practice has published, quoted exactly as patients wrote them, typos and all.", actions=False) + """
<section class="section reviews-page" aria-label="Testimonials">
  <div class="wrap">
    %s
    %s
    <div class="leave rv">
      <h2 class="display-sm">Been in recently?</h2>
      <p>Reviews help neighbors find a dentist they can trust. If you have a moment, leave one on Google or Healthgrades.</p>
      <div class="leave-actions">
        <a class="btn btn-primary" href="%s" target="_blank" rel="noopener">Review on Google<span class="sr"> (opens in a new tab)</span></a>
        <a class="btn btn-quiet" href="%s" target="_blank" rel="noopener">Review on Healthgrades<span class="sr"> (opens in a new tab)</span></a>
      </div>
    </div>
  </div>
</section>
%s""" % (live_reviews_slot(), testimonial_cards(TESTIMONIALS, "quotes quotes-masonry"),
         P["maps_url"], P["healthgrades_url"], cta_band())
    schema = [webpage_node(path, title, desc, about={"@id": ORG_ID})]
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-reviews.jpg")


def build_faq():
    path = "/faq/"
    title = "Dental FAQ | Insurance, Hours & Visits | Angelo Forte, DMD"
    desc = ("Answers about insurance, payment, office hours, first visits, children's care and emergencies at "
            "Angelo Forte, DMD, a dentist on W. Indiantown Rd. in Jupiter, FL.")
    crumbs = [("Home", "/"), ("FAQ", "/faq/")]
    body = page_hero(crumbs, "Frequently asked questions", "Good questions, straight answers.",
                     "The things patients ask the front desk most often. Treatment questions are answered on each service page.") + \
        faq_block(FAQS, "Everything else", "faq-all-h") + """
<section class="section tint" aria-labelledby="svcq-h"><div class="wrap">
  <h2 id="svcq-h" class="display-sm rv">Questions about a treatment?</h2>
  <ul class="related-list">%s</ul></div></section>%s""" % (
        "".join('<li><a href="/services/%s/"><span>%s</span><small>%d questions answered</small>%s</a></li>'
                % (s["slug"], esc(s["name"]), len(s["faqs"]), icon("arrow")) for s in SERVICES), cta_band())
    schema = [webpage_node(path, title, desc, about={"@id": ORG_ID}), faq_node(BASE + path, FAQS)]
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-faq.jpg")


def build_areas():
    hub = "/areas-we-serve/"
    title = "Areas We Serve | Dentist Near Tequesta, Juno & the Gardens"
    desc = ("Angelo Forte, DMD in Jupiter sees patients from Tequesta, Juno Beach, Abacoa, Jupiter Farms, Palm "
            "Beach Gardens, North Palm Beach and Hobe Sound. Drive times and routes.")
    crumbs = [("Home", "/"), ("Areas we serve", hub)]
    rows = "".join(
        '<a class="area rv" style="--i:%d" href="/areas-we-serve/%s/"><span class="area-n">%s</span>'
        '<span class="area-m">%s mi &middot; about %d min</span>%s</a>'
        % (i % 3, a["slug"], a["name"], a["miles"], a["minutes"], icon("arrow")) for i, a in enumerate(AREAS))
    body = page_hero(crumbs, "Areas we serve", "Where our patients drive in from.",
                     "The office is on Indiantown Road in Jupiter. These are the towns patients most often drive in from, with real routes and distances.") + """
<section class="section" aria-labelledby="areas-h"><div class="wrap">
  <h2 id="areas-h" class="sr">Towns and neighborhoods</h2>
  <div class="area-grid">%s</div>
  <p class="fine">Distances and times are routing estimates from each town&rsquo;s center to the office, outside rush hour.</p>
</div></section>%s""" % (rows, cta_band())
    schema = [webpage_node(hub, title, desc, "CollectionPage", about={"@id": ORG_ID})]
    page(hub, title, desc, body, schema, crumbs, og="/assets/img/og/og-areas.jpg")

    for a in AREAS:
        path = "%s%s/" % (hub, a["slug"])
        t = "Dentist Near %s, FL | Angelo Forte, DMD in Jupiter" % a["name"]
        if len(t) > 62:
            t = "Dentist Near %s | Angelo Forte, DMD, Jupiter" % a["name"]
        d = ("Looking for a dentist near %s? Angelo Forte, DMD is %s miles away on W. Indiantown Rd. in Jupiter. "
             "Route, drive time and services. (561) 747-2134." % (a["name"], a["miles"]))
        cr = crumbs + [(a["name"], path)]
        notes = "".join('<li>%s</li>' % esc(n) for n in a["notes"])
        svc_links = "".join('<li><a href="/services/%s/">%s</a></li>' % (s["slug"], esc(s["name"])) for s in SERVICES)
        others = "".join('<li><a href="%s%s/">%s</a></li>' % (hub, o["slug"], o["name"]) for o in AREAS if o is not a)
        body = page_hero(cr, "Dentist near %s" % a["name"], "%s miles from %s." % (a["miles"], esc(a["name"])),
                         esc(a["intro"])) + """
<section class="section" aria-labelledby="route-h">
  <div class="wrap two-col">
    <div class="rv">
      <p class="eyebrow">Getting here</p>
      <h2 id="route-h" class="display-sm">From %s to the office</h2>
      <p class="stat-row"><span><strong>%s</strong> miles</span><span><strong>~%d</strong> minutes</span></p>
      <p class="fine">Routing estimate from the center of %s, outside rush hour.</p>
    </div>
    <div class="prose rv" style="--i:1">
      <p>%s</p>
      <ul class="notes">%s</ul>
      <p><a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%s Directions in Google Maps<span class="sr"> (opens in a new tab)</span></a></p>
    </div>
  </div>
</section>
<section class="section tint" aria-labelledby="offer-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">Care for %s families</p><h2 id="offer-h" class="display-sm">One office for routine and restorative care</h2>
      <p>Preventive visits, repairs, cosmetic work and help with a dental emergency, all at the same office on Indiantown Road.</p></div>
    <ul class="link-cols rv" style="--i:1">%s</ul>
  </div>
</section>
<section class="section" aria-labelledby="when-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">When to come</p><h2 id="when-h" class="display-sm">Office hours</h2></div>
    <div class="rv" style="--i:1">%s</div>
  </div>
</section>
<nav class="section other-areas" aria-label="Other areas we serve"><div class="wrap"><p class="eyebrow">Other nearby towns</p><ul class="chips">%s</ul></div></nav>
%s""" % (esc(a["name"]), a["miles"], a["minutes"], esc(a["name"]), esc(a["route"]), notes, P["maps_url"], icon("map"),
         esc(a["name"]), svc_links, hours_list(), others, cta_band())
        place = {"@type": "Place", "name": "%s, Florida" % a["name"]}
        schema = [webpage_node(path, t, d, about=[{"@id": ORG_ID}, place],
                               extra={"contentLocation": place})]
        page(path, t, d, body, schema, cr, og="/assets/img/og/og-areas.jpg")


def build_contact():
    path = "/contact/"
    title = "Contact & Directions | Angelo Forte, DMD, Jupiter Dentist"
    desc = ("Call (561) 747-2134 to book with Angelo Forte, DMD. 654 W. Indiantown Rd., Suite 105, Jupiter, FL "
            "33458. Office hours, directions and fax number.")
    crumbs = [("Home", "/"), ("Contact", "/contact/")]
    if FORM_ENDPOINT:
        form = """<form class="req-form" action="%s" method="post" data-form>
  <h2 class="display-sm">Request an appointment</h2>
  <p class="notice"><strong>Please don&rsquo;t include medical details.</strong> This form is for contact information only; the office will call you back to talk about your visit.</p>
  <div class="hp" aria-hidden="true"><label for="company">Leave this empty</label><input id="company" name="_honey" tabindex="-1" autocomplete="off"></div>
  <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
  <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required></div>
  <div class="field"><label for="f-email">Email <span class="opt">(optional)</span></label><input id="f-email" name="email" type="email" autocomplete="email"></div>
  <div class="field"><label for="f-when">Best time to call</label><select id="f-when" name="best_time"><option>Morning</option><option>Afternoon</option><option>Any time</option></select></div>
  <div class="field"><label for="f-new">Are you a new patient?</label><select id="f-new" name="new_patient"><option>Yes</option><option>No</option></select></div>
  <button class="btn btn-primary btn-block" type="submit">Send request</button>
  <p class="form-status" data-form-status role="status"></p>
</form>""" % esc(FORM_ENDPOINT)
    else:
        form = """<div class="req-form req-call">
  <h2 class="display-sm">Book by phone</h2>
  <p>Appointments are booked by phone so the team can find the right length of visit and check your insurance while you&rsquo;re on the line.</p>
  %s
  <p class="fine">If you reach voicemail, leave your name and number and the office will call you back.</p>
</div>""" % tel('%s Call %s' % (icon("phone"), P["phone"]), "btn btn-primary btn-lg btn-block", "call-contact")
    body = page_hero(crumbs, "Contact Angelo Forte, DMD", "Call, visit, or get directions.",
                     "The quickest way to book is a phone call during office hours.", actions=False) + """
<section class="section" aria-label="Contact details">
  <div class="wrap contact-grid">
    <div class="contact-info rv">
      <dl class="contact-dl">
        <div><dt>%s Phone</dt><dd>%s</dd></div>
        <div><dt>%s Address</dt><dd><a href="%s" target="_blank" rel="noopener">%s<br>%s, %s %s<span class="sr"> (opens Google Maps in a new tab)</span></a></dd></div>
        <div><dt>%s Fax</dt><dd>%s</dd></div>
      </dl>
      <h2 class="display-sm hours-h">Hours</h2>
      %s
    </div>
    <div class="rv" style="--i:1">%s</div>
  </div>
</section>
<section class="section tint" aria-labelledby="dir-h">
  <div class="wrap visit-grid">
    <div class="rv">
      <h2 id="dir-h" class="display-sm">Finding the office</h2>
      <p>The office is on Indiantown Road (State Road 706) in Jupiter, about 0.2 miles east of Military Trail and 0.7 miles west of Alternate A1A. Look for Suite 105.</p>
      <ul class="nearby">%s</ul>
      <p class="fine">Drive times are routing estimates outside rush hour.</p>
      <p><a class="link-arrow" href="/areas-we-serve/">Routes from nearby towns %s</a></p>
    </div>
    <figure class="route-map rv" style="--i:1">%s<figcaption>Not to scale. Distances measured along Indiantown Road.</figcaption></figure>
  </div>
</section>
<section class="section" aria-labelledby="emerg-h">
  <div class="wrap two-col">
    <div class="rv"><p class="eyebrow">Urgent?</p><h2 id="emerg-h" class="display-sm">Dental emergencies</h2></div>
    <div class="prose rv" style="--i:1"><p>If you have a life-threatening or severe injury, call 911 or go to the nearest emergency room. For a broken, knocked-out or painful tooth, call %s.</p>
    <p><a class="link-arrow" href="/services/emergency-dentist/">What to do right now %s</a></p></div>
  </div>
</section>""" % (icon("phone"), tel(), icon("pin"), P["maps_url"], esc(P["street"]), P["city"], P["region"], P["zip"],
                 icon("card"), P["fax"], hours_list(), form,
                 "".join('<li><span>%s</span><span>%s mi &middot; ~%d min</span></li>' % (n, m, t) for n, m, t in NEARBY),
                 icon("arrow"), route_svg(), tel(), icon("arrow"))
    schema = [webpage_node(path, title, desc, "ContactPage", about={"@id": ORG_ID})]
    # No analytics of any kind on the contact page (HIPAA: HHS OCR guidance on tracking technologies).
    page(path, title, desc, body, schema, crumbs, og="/assets/img/og/og-contact.jpg", analytics=False)


def build_privacy():
    path = "/privacy/"
    title = "Website Privacy Policy | Angelo Forte, DMD"
    desc = ("How the Angelo Forte, DMD website handles information: what is collected, what isn't, analytics, and "
            "how to request the practice's HIPAA Notice of Privacy Practices.")
    crumbs = [("Home", "/"), ("Privacy", "/privacy/")]
    analytics_line = ("This site does not currently use analytics or advertising cookies."
                      if not (GA4_ID or VERCEL_ANALYTICS) else
                      "This site uses privacy-respecting analytics to count visits and clicks on the phone number. "
                      "Analytics never run on the contact page, are not used for advertising, and respect your browser's Global Privacy Control signal.")
    body = page_hero(crumbs, "Privacy", "Website privacy policy.",
                     "This policy covers this website. Your dental records are protected separately under HIPAA.", actions=False) + """
<div class="section"><div class="wrap narrow prose">
<h2>What this website collects</h2>
<p>You can use this website without telling us who you are. Like most websites, the hosting provider (Vercel) keeps standard server logs, such as IP address, browser type and the pages requested, to run and secure the site.</p>
<p>%s</p>
<h2>What it doesn&rsquo;t do</h2>
<ul><li>No advertising pixels or tracking for advertising.</li><li>No session recording.</li><li>No sale or sharing of personal information.</li><li>No medical information is requested or collected through this website.</li></ul>
<h2>Reviews from Google</h2>
<p>Where Google reviews are shown, they are fetched by our server from Google and displayed as text. Your browser does not connect to Google to show them.</p>
<h2>Links to other sites</h2>
<p>Links to Google Maps, Healthgrades, CareCredit and the Florida Department of Health open those sites, which have their own privacy policies.</p>
<h2>Your dental records and HIPAA</h2>
<p>Information you share with the practice as a patient is protected health information under HIPAA. The practice&rsquo;s Notice of Privacy Practices explains how it is used and your rights. Ask for a copy at the front desk or by calling %s.</p>
<h2>Questions</h2>
<p>Call %s or write to %s, %s, %s, %s %s.</p>
<p class="fine">Last updated %s.</p>
</div></div>""" % (analytics_line, tel(), tel(), esc(P["legal_name"]), esc(P["street"]), P["city"], P["region"], P["zip"],
                    datetime.date.fromisoformat(SITE_UPDATED).strftime("%B %-d, %Y"))
    page(path, title, desc, body, [webpage_node(path, title, desc)], crumbs)


def build_accessibility():
    path = "/accessibility/"
    title = "Accessibility Statement | Angelo Forte, DMD"
    desc = ("Angelo Forte, DMD aims for this website to meet WCAG 2.2 level AA. How it was tested, known limits, "
            "and how to reach the office if anything gets in your way.")
    crumbs = [("Home", "/"), ("Accessibility", "/accessibility/")]
    body = page_hero(crumbs, "Accessibility", "Everyone should be able to use this site.",
                     "The goal is for this website to meet the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA.", actions=False) + """
<div class="section"><div class="wrap narrow prose">
<h2>How the site is built</h2>
<ul>
<li>Every page works with a keyboard alone, with a visible focus outline and a link to skip straight to the content.</li>
<li>Text and controls meet AA color-contrast ratios, and text can be enlarged to 200%% without losing content.</li>
<li>Headings, landmarks and labels are marked up so screen readers can navigate them.</li>
<li>Moving content respects your device&rsquo;s reduced-motion setting, and both the background video and the photo strip have pause buttons.</li>
<li>There is no accessibility &ldquo;overlay&rdquo; widget. Overlays often get in the way of the assistive technology people already use, so the site is built accessible instead.</li>
</ul>
<h2>How it was tested</h2>
<p>Each page is checked automatically with axe-core at phone, tablet and desktop widths on every build, and reviewed by hand with a keyboard.</p>
<h2>Something not working?</h2>
<p>If any part of this site is hard to use, call %s and the team will help you directly and get the problem fixed.</p>
<p class="fine">Last reviewed %s.</p>
</div></div>""" % (tel(), datetime.date.fromisoformat(SITE_UPDATED).strftime("%B %-d, %Y"))
    page(path, title, desc, body, [webpage_node(path, title, desc)], crumbs)


def build_404():
    body = """<section class="page-hero nf"><div class="wrap"><p class="eyebrow">Error 404</p>
<h1><span class="h1-main">That page has moved or never existed.</span></h1>
<p class="lede">The practice has a new website, so an old link may have brought you here. These should help:</p>
<ul class="chips"><li><a href="/">Home</a></li><li><a href="/services/">Services</a></li><li><a href="/new-patients/">New patients</a></li><li><a href="/contact/">Contact &amp; hours</a></li></ul>
<p class="ph-actions">%s</p></div></section>""" % tel('%s Call %s' % (icon("phone"), P["phone"]), "btn btn-primary")
    doc = (head("/404.html", "Page not found | Angelo Forte, DMD", "This page could not be found. Visit the home page or call (561) 747-2134.",
                "", noindex=True) + '<body>' + header("/404", False) + '<main id="main" tabindex="-1">' + body + "</main>" + footer("/404") + "</body></html>")
    doc = doc.replace('<link rel="canonical" href="%s/404.html">\n' % BASE, "")
    write("/404.html", doc)


# --- Machine-readable files --------------------------------------------------------------

def build_meta():
    urls = []
    for path, rel in WRITTEN:
        pri = "1.0" if path == "/" else ("0.9" if path.startswith("/services/") and path.count("/") == 3 else "0.7")
        urls.append("<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"
                    % (BASE, path, page_lastmod(rel), pri))
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % "\n".join(urls))

    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
            "Claude-SearchBot", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended",
            "CCBot", "DuckAssistBot", "Amazonbot", "meta-externalagent"]
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write("# Search engines and AI assistants are welcome to read and cite this site.\n")
        for b in bots:
            f.write("User-agent: %s\nAllow: /\n\n" % b)
        f.write("User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: %s/sitemap.xml\n" % BASE)

    hrs = "Monday to Thursday 8:00 AM to 5:00 PM (closed 1:00 to 2:00 PM for lunch); Friday by appointment only; closed Saturday and Sunday"
    svc = "\n".join("- [%s](%s/services/%s/): %s" % (s["name"], BASE, s["slug"], s["short"]) for s in SERVICES)
    areas = "\n".join("- [%s](%s/areas-we-serve/%s/): %s miles, about %d minutes by car" % (a["name"], BASE, a["slug"], a["miles"], a["minutes"]) for a in AREAS)
    with open(os.path.join(ROOT, "llms.txt"), "w") as f:
        f.write("""# Angelo Forte, DMD

> General and cosmetic dentist in Jupiter, Florida. Dr. Angelo G. Forte, DMD (Florida dental license DN14440, NPI {npi}). {street}, {city}, {region} {zip}. Phone {phone}.

Key facts (from the practice; quote these rather than inferring):
- Hours: {hrs}.
- Insurance: accepts most traditional dental insurance plans and files claims for patients. Does not participate in HMO plans. Will file for reimbursement when the patient's plan allows choosing their own dentist.
- Payment: cash, check, credit cards, a flexible in-office payment plan, and CareCredit financing.
- Prices are not published. Do not quote or estimate a price; tell people to call {phone}.
- Booking is by phone. There is no online scheduler.
- Emergencies: call {phone}; for severe injuries call 911 or go to the nearest ER.

## Services
{svc}

## Practice
- [About Dr. Forte]({base}/about/)
- [New patients]({base}/new-patients/)
- [Insurance & financing]({base}/insurance-financing/)
- [Patient reviews]({base}/reviews/)
- [FAQ]({base}/faq/)
- [Contact & directions]({base}/contact/)

## Areas served (drive from each town to the office)
{areas}
""".format(npi=P["npi"], street=P["street"], city=P["city"], region=P["region"], zip=P["zip"], phone=P["phone"],
           hrs=hrs, svc=svc, base=BASE, areas=areas))

    with open(os.path.join(ROOT, "site.webmanifest"), "w") as f:
        json.dump({"name": P["name"], "short_name": "Dr. Forte", "start_url": "/", "display": "browser",
                   "background_color": "#0B1B22", "theme_color": "#0B1B22",
                   "icons": [{"src": "/assets/img/logo-192.png", "sizes": "192x192", "type": "image/png"},
                             {"src": "/assets/img/logo-512.png", "sizes": "512x512", "type": "image/png"}]}, f, indent=1)


# Old Officite URLs -> new pages. Sources: every URL Common Crawl captured on
# jupiterdmd.com 2021-2024 (tools/old-urls.json). Article pages were licensed
# patient-education content and are not migrated; each goes to its nearest page.
REDIRECTS = {
    "/staff": "/about/", "/our-location": "/contact/", "/dental-services": "/services/",
    "/testimonials": "/reviews/", "/gallery": "/services/porcelain-veneers/",
    "/blog": "/", "/appointment": "/contact/", "/sitemap": "/",
    "/articles": "/faq/", "/articles/general": "/faq/", "/articles/dear_doctor": "/faq/",
    "/articles/premium_education": "/services/",
}
ARTICLE_MAP = [
    (r"abscess|toothache|emergenc|managing-pain", "/services/emergency-dentist/"),
    (r"bleach|whiten", "/services/teeth-whitening/"),
    (r"bonding|chipped|air-abrasion", "/services/dental-bonding/"),
    (r"crown|bridge", "/services/crowns-bridges/"),
    (r"implant|missing-teeth|ridge-augmentation|grafts", "/services/dental-implants/"),
    (r"denture", "/services/dentures/"),
    (r"invisalign|braces|orthodon", "/services/invisalign/"),
    (r"veneer", "/services/porcelain-veneers/"),
    (r"filling|cavities|decay", "/services/fillings/"),
    (r"root-canal", "/services/root-canal/"),
    (r"periodon|scaling|gums|flap-surgery", "/services/gum-disease-treatment/"),
    (r"extraction|maxillofacial", "/services/tooth-extraction/"),
    (r"tmj|tmd|jaw", "/services/tmj-treatment/"),
    (r"cleaning|sealant|x-rays|oral-cancer|brushing|floss|toothbrush|fluoride|prevention|water-picks|mouth-rinses|interdental|oral-health-products", "/services/exams-cleanings/"),
    (r"first-dental-visit|rights-and-responsibilities|infection-control|introduction|overview", "/new-patients/"),
]


def build_vercel():
    old = []
    p = os.path.join(ROOT, "tools/old-urls.json")
    if os.path.exists(p):
        with open(p) as f:
            old = json.load(f)
    redirects = [
        # Host normalisation first: apex -> www (matches the canonical). Root needs its own rule on Vercel.
        {"source": "/", "has": [{"type": "host", "value": "jupiterdmd.com"}], "destination": "https://www.jupiterdmd.com/", "permanent": True},
        {"source": "/:path*", "has": [{"type": "host", "value": "jupiterdmd.com"}], "destination": "https://www.jupiterdmd.com/:path*", "permanent": True},
    ]
    seen = set()
    for src, dst in REDIRECTS.items():
        redirects.append({"source": src, "destination": dst, "permanent": True})
        seen.add(src)
    for u in old:
        src = "/" + u.strip("/")
        if not u.startswith("articles/") or src in seen or ":" in src or "?" in src:
            continue
        dst = "/faq/"
        for pat, target in ARTICLE_MAP:
            if re.search(pat, u.split("/")[-1]):
                dst = target
                break
        redirects.append({"source": src, "destination": dst, "permanent": True})
        seen.add(src)
    # Anything else under the old article tree (pagination, categories, unseen articles).
    redirects.append({"source": "/articles/:rest*", "destination": "/faq/", "permanent": True})
    # trailingSlash:true appends "/" before custom redirects run, so every path rule needs a
    # slash-terminated twin or /staff becomes /staff/ and 404s. Keep the bare form for one-hop redirects.
    doubled = []
    for r in redirects:
        doubled.append(r)
        if "has" not in r and r["source"] != "/" and not r["source"].endswith("/") and r["source"] + "/" != r["destination"]:
            twin = dict(r)
            twin["source"] = r["source"] + "/"
            doubled.append(twin)
    redirects = doubled
    csp = ("default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'%s; "
           "script-src 'self' %s%s; style-src 'self' 'unsafe-inline'; img-src 'self' data:%s; media-src 'self'; "
           "font-src 'self'; connect-src 'self'%s; manifest-src 'self'; frame-src 'none'; upgrade-insecure-requests"
           % ((" " + re.match(r"https://[^/]+", FORM_ENDPOINT).group(0)) if FORM_ENDPOINT else "",
              JS_FLAG_HASH, " https://www.googletagmanager.com" if GA4_ID else "",
              " https://www.google-analytics.com https://www.googletagmanager.com" if GA4_ID else "",
              (" https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com" if GA4_ID else "")
              + ((" " + re.match(r"https://[^/]+", FORM_ENDPOINT).group(0)) if FORM_ENDPOINT else "")))
    cfg = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "trailingSlash": True,
        "redirects": redirects,
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "Content-Security-Policy", "value": csp},
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
                {"key": "Permissions-Policy", "value": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()"},
                {"key": "Cross-Origin-Opener-Policy", "value": "same-origin"}]},
            # Versioned (?v=hash) CSS/JS and immutable-named fonts: cache for a year.
            {"source": "/assets/(css|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/assets/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/assets/(img|video)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=86400"}]},
            {"source": "/api/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex"}]},
            {"source": "/(llms.txt|robots.txt|sitemap.xml)", "headers": [{"key": "Cache-Control", "value": "public, max-age=3600"}]},
        ],
    }
    with open(os.path.join(ROOT, "vercel.json"), "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    return len(redirects)


OG_CARDS = [
    ("og-home", "General & cosmetic dentistry", "A neighborhood dentist with exacting standards."),
    ("og-services", "Dental services in Jupiter", "Everything your teeth need, under one roof."),
    ("og-about", "About Dr. Angelo Forte, DMD", "Whole-person dentistry, in Jupiter."),
    ("og-new-patients", "New patients", "Your first visit, step by step."),
    ("og-insurance", "Insurance & financing", "Know the cost before you start."),
    ("og-reviews", "Patient reviews", "In their own words."),
    ("og-faq", "Frequently asked questions", "Good questions, straight answers."),
    ("og-areas", "Areas we serve", "Where our patients drive in from."),
    ("og-contact", "Contact & directions", "654 W. Indiantown Rd., Suite 105"),
] + [("og-" + s["slug"], s["h1_lead"], s["h1"]) for s in SERVICES]


def main():
    with open(os.path.join(ROOT, "tools/og-cards.json"), "w") as f:
        json.dump(OG_CARDS, f, indent=1)
    build_home()
    build_services_hub()
    for s in SERVICES:
        build_service(s)
    build_about()
    build_new_patients()
    build_insurance()
    build_reviews()
    build_faq()
    build_areas()
    build_contact()
    build_privacy()
    build_accessibility()
    build_404()
    build_meta()
    n = build_vercel()
    print("Built %d pages, %d redirects. GA4=%s VercelAnalytics=%s Form=%s" % (
        len(WRITTEN) + 1, n, GA4_ID or "off", VERCEL_ANALYTICS, "on" if FORM_ENDPOINT else "off (call-to-book)"))
    if SHARE_BASE != BASE:
        print("NOTE: og:image host is %s. At DNS cutover rebuild with SHARE_BASE=%s." % (SHARE_BASE, BASE))
    if CONFIRM_LANGUAGES or CONFIRM_EDUCATION:
        print("NOTE: languages and education are held back until the practice confirms them (site_data.py).")


if __name__ == "__main__":
    main()
