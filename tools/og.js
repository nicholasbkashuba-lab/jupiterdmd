// Render the share cards (1200x630 JPG) listed in tools/og-cards.json, written by build.py.
// usage: PW=<playwright module> node tools/og.js
const { chromium } = require(process.env.PW || "playwright");
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "..");
const cards = JSON.parse(fs.readFileSync(path.join(ROOT, "tools/og-cards.json"), "utf8"));
const font = f => "data:font/woff2;base64," + fs.readFileSync(path.join(ROOT, "assets/fonts", f)).toString("base64");
const bg = "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, "assets/img/og-base.jpg")).toString("base64");
const mono = fs.readFileSync(path.join(ROOT, "tools/monogram-path.txt"), "utf8").trim();
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
(async () => {
  const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  fs.mkdirSync(path.join(ROOT, "assets/img/og"), { recursive: true });
  for (const [file, kicker, title] of cards) {
    await p.setContent(`<html><head><style>
@font-face{font-family:S;src:url(${font("instrument-serif-v2.woff2")})}
@font-face{font-family:N;src:url(${font("instrument-sans-v2.woff2")});font-weight:400 700}
body{margin:0;width:1200px;height:630px;position:relative;overflow:hidden;font-family:N;color:#fff;background:#0B1B22}
.bg{position:absolute;inset:0;background:url(${bg}) center/cover}
.sc{position:absolute;inset:0;background:linear-gradient(90deg,rgba(7,18,23,.92) 0%,rgba(7,18,23,.72) 48%,rgba(7,18,23,.15) 100%),linear-gradient(0deg,rgba(7,18,23,.6),rgba(7,18,23,0) 50%)}
.in{position:absolute;left:72px;top:64px;right:330px;bottom:64px;display:flex;flex-direction:column}
.wm{display:flex;align-items:center;gap:14px}.wm b{display:block;font:400 34px/1 S}.wm small{display:block;margin-top:6px;font:600 13px/1 N;letter-spacing:.2em;text-transform:uppercase;opacity:.8}
.k{margin-top:auto;font:600 17px/1.2 N;letter-spacing:.16em;text-transform:uppercase;color:#F2B866}
h1{margin:16px 0 0;font:400 72px/1.0 S;letter-spacing:-.01em}
.f{margin-top:28px;font:500 21px/1.3 N;opacity:.9}
</style></head><body><div class="bg"></div><div class="sc"></div><div class="in">
<div class="wm"><svg width="56" height="56" viewBox="0 0 40 40"><circle cx="20" cy="20" r="19.2" fill="none" stroke="#fff" stroke-opacity=".5"/><path transform="translate(10.2 26.4) scale(.0275)" fill="#fff" d="${mono}"/><path d="M8.5 31.2c3.8-2 7.7 2 11.5 0s7.7 2 11.5 0" fill="none" stroke="#F2B866" stroke-width="1.4" stroke-linecap="round"/></svg><div><b>Angelo Forte</b><small>DMD · Jupiter, Florida</small></div></div>
<div class="k">${esc(kicker)}</div><h1>${esc(title)}</h1><div class="f">(561) 747-2134 · 654 W. Indiantown Rd., Jupiter</div></div></body></html>`);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(ROOT, "assets/img/og", file + ".jpg"), type: "jpeg", quality: 82 });
  }
  await b.close();
  console.log("rendered", cards.length, "cards");
})();
