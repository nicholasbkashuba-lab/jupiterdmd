// Live Google reviews for the practice, via the Places API (New).
// Set GOOGLE_PLACES_API_KEY in the Vercel project (and optionally GOOGLE_PLACE_ID; without it the
// place is looked up by name and address once per cold start). With no key this returns 204 and the
// site shows only the testimonials the practice published itself. Nothing here is cached as fact:
// rating and count always come from Google at request time (edge-cached for 12 hours).
const QUERY = "Angelo Forte DMD, 654 W Indiantown Rd Suite 105, Jupiter, FL 33458";
let placeId = process.env.GOOGLE_PLACE_ID || "";

module.exports = async function handler(req, res) {
  const key = process.env.GOOGLE_PLACES_API_KEY;
  res.setHeader("X-Robots-Tag", "noindex");
  if (!key) { res.statusCode = 204; return res.end(); }
  try {
    if (!placeId) {
      const s = await fetch("https://places.googleapis.com/v1/places:searchText", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Goog-Api-Key": key, "X-Goog-FieldMask": "places.id" },
        body: JSON.stringify({ textQuery: QUERY }),
      });
      const sj = await s.json();
      placeId = (sj.places && sj.places[0] && sj.places[0].id) || "";
      if (!placeId) throw new Error("place not found");
    }
    const r = await fetch("https://places.googleapis.com/v1/places/" + encodeURIComponent(placeId), {
      headers: { "X-Goog-Api-Key": key, "X-Goog-FieldMask": "rating,userRatingCount,googleMapsUri,reviews" },
    });
    if (!r.ok) throw new Error("places " + r.status);
    const p = await r.json();
    const body = {
      rating: p.rating, count: p.userRatingCount, url: p.googleMapsUri,
      reviews: (p.reviews || []).filter((x) => x.rating >= 4 && x.text && x.text.text).slice(0, 6).map((x) => ({
        author: (x.authorAttribution && x.authorAttribution.displayName) || "Google user",
        rating: x.rating, text: x.text.text, when: x.relativePublishTimeDescription || "",
      })),
      source: "Google",
    };
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "public, s-maxage=43200, stale-while-revalidate=86400");
    res.statusCode = 200;
    res.end(JSON.stringify(body));
  } catch (e) {
    res.statusCode = 204;
    res.end();
  }
};
