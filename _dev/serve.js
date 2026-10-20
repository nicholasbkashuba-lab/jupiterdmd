// Local stand-in for Vercel: static files, folder index, 404.html, trailing-slash
// redirects, vercel.json redirects, and /api/reviews -> 204 (no API key locally).
const http = require("http"), fs = require("fs"), path = require("path"), zlib = require("zlib");
const ROOT = path.resolve(__dirname, "..");
const PORT = +process.argv[2] || 8833;
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "vercel.json"), "utf8"));
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif", ".woff2": "font/woff2", ".mp4": "video/mp4", ".webm": "video/webm", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8", ".xml": "application/xml", ".webmanifest": "application/manifest+json" };
function matchRedirect(p) {
  for (const r of cfg.redirects) {
    if (r.has) continue;
    const re = new RegExp("^" + r.source.replace(/:rest\*/, "(.*)").replace(/:path\*/, "(.*)") + "/?$");
    const m = p.match(re);
    if (m) return r.destination;
  }
  return null;
}
http.createServer((req, res) => {
  const u = new URL(req.url, "http://x");
  let p = decodeURIComponent(u.pathname);
  if (p === "/api/reviews" || p === "/api/reviews/") { res.writeHead(204); return res.end(); }
  const red = matchRedirect(p);
  if (red && red !== p) { res.writeHead(308, { Location: red }); return res.end(); }
  let f = path.join(ROOT, p);
  if (!f.startsWith(ROOT)) { res.writeHead(400); return res.end(); }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) {
    if (!p.endsWith("/")) { res.writeHead(308, { Location: p + "/" }); return res.end(); }
    f = path.join(f, "index.html");
  }
  if (!fs.existsSync(f)) {
    res.writeHead(404, { "Content-Type": TYPES[".html"] });
    return res.end(fs.readFileSync(path.join(ROOT, "404.html")));
  }
  const stat = fs.statSync(f), type = TYPES[path.extname(f)] || "application/octet-stream";
  const range = req.headers.range;
  if (range && type.startsWith("video")) {
    const [s, e] = range.replace("bytes=", "").split("-");
    const start = +s, end = e ? +e : stat.size - 1;
    res.writeHead(206, { "Content-Type": type, "Content-Range": `bytes ${start}-${end}/${stat.size}`, "Accept-Ranges": "bytes", "Content-Length": end - start + 1 });
    return fs.createReadStream(f, { start, end }).pipe(res);
  }
  // Compress text like Vercel does, so local Lighthouse numbers are comparable.
  if (/^(text|application\/(json|xml|manifest)|image\/svg)/.test(type) && /br/.test(req.headers["accept-encoding"] || "")) {
    const body = zlib.brotliCompressSync(fs.readFileSync(f));
    res.writeHead(200, { "Content-Type": type, "Content-Encoding": "br", "Content-Length": body.length, "Cache-Control": f.includes("/assets/") ? "public, max-age=31536000, immutable" : "public, max-age=0, must-revalidate" });
    return res.end(body);
  }
  res.writeHead(200, { "Content-Type": type, "Content-Length": stat.size, "Accept-Ranges": "bytes", "Cache-Control": f.includes("/assets/") ? "public, max-age=604800" : "public, max-age=0" });
  fs.createReadStream(f).pipe(res);
}).listen(PORT, () => console.log("serving " + ROOT + " on " + PORT));
