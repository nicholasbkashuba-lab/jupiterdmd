// Browser-verify every page: axe (WCAG 2.2 AA), console/JS errors, failed requests,
// broken images, horizontal overflow, at 375 / 768 / 1440. Exits non-zero on any failure.
// usage: PW=<playwright module> AXE=<@axe-core/playwright module> node _dev/verify.js [baseURL] [--shots dir]
const { chromium } = require(process.env.PW || "playwright");
const { default: AxeBuilder } = require(process.env.AXE || "@axe-core/playwright");
const fs = require("fs"), path = require("path");
const BASE = process.argv[2] || "http://localhost:8833";
const shotsIdx = process.argv.indexOf("--shots"), SHOTS = shotsIdx > 0 ? process.argv[shotsIdx + 1] : null;
const ROOT = path.resolve(__dirname, "..");
const sm = fs.readFileSync(path.join(ROOT, "sitemap.xml"), "utf8");
const paths = [...sm.matchAll(/<loc>https:\/\/www\.jupiterdmd\.com([^<]*)<\/loc>/g)].map(m => m[1]).concat(["/this-page-does-not-exist/"]);
const WIDTHS = [[375, 812], [768, 1024], [1440, 900]];
const schemes = (process.env.SCHEMES || "light").split(",");
(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
  let fails = 0, checked = 0, axeRuns = 0;
  const report = [];
  for (const scheme of schemes) for (const [w, h] of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, reducedMotion: process.env.REDUCED ? "reduce" : "no-preference" });
    for (const p of paths) {
      const page = await ctx.newPage();
      const errors = [];
      page.on("console", m => { if (m.type() === "error" && !(p.includes("this-page-does-not-exist") && m.text().includes("404"))) errors.push("console: " + m.text()); });
      page.on("pageerror", e => errors.push("pageerror: " + e.message));
      page.on("requestfailed", r => { const u = r.url(); if (!/\.(mp4|webm)(\?|$)/.test(u) && (r.failure() || {}).errorText !== "net::ERR_ABORTED") errors.push("requestfailed: " + u + " " + (r.failure() || {}).errorText); });
      page.on("response", r => { if (r.status() >= 400 && !r.url().includes("this-page-does-not-exist")) errors.push("http " + r.status() + ": " + r.url()); });
      await page.goto(BASE + p, { waitUntil: "load" });
      await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } window.scrollTo(0, 0); });
      await page.waitForTimeout(300);
      const probe = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.currentSrc).map(i => i.currentSrc),
        h1: document.querySelectorAll("h1").length,
      }));
      const axe = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]).analyze();
      axeRuns++;
      const v = axe.violations.map(x => `${x.id} (${x.nodes.length}): ${x.nodes.slice(0, 2).map(n => n.target.join(" ")).join(" | ")}`);
      const bad = [];
      if (probe.overflow > 0) bad.push("horizontal overflow " + probe.overflow + "px");
      if (probe.broken.length) bad.push("broken images " + probe.broken.join(", "));
      if (probe.h1 !== 1) bad.push("h1 count " + probe.h1);
      bad.push(...v.map(x => "axe " + x), ...errors);
      checked++;
      if (bad.length) { fails++; report.push(`[${scheme} ${w}] ${p}\n   - ` + bad.join("\n   - ")); }
      if (SHOTS && (p === "/" || p.split("/").length <= 3 || p.includes("dental-implants") || p.includes("tequesta"))) {
        fs.mkdirSync(SHOTS, { recursive: true });
        await page.screenshot({ path: path.join(SHOTS, `${scheme}-${w}${p.replace(/\//g, "_") || "_"}.png`), fullPage: true });
      }
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  console.log(report.join("\n"));
  console.log(`\n${checked} page-views checked (${paths.length} pages x ${WIDTHS.length} widths x ${schemes.length} schemes), ${axeRuns} axe runs, ${fails} with problems.`);
  process.exit(fails ? 1 : 0);
})();
