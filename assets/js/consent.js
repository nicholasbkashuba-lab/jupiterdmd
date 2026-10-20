/* Google Analytics 4, loaded only when the build sets GA4_ID. Consent Mode v2 defaults:
   no advertising storage ever; analytics off when the browser sends Global Privacy Control. */
(function () {
  var s = document.currentScript, id = s && s.getAttribute("data-ga");
  if (!id) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  var gpc = navigator.globalPrivacyControl === true;
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: gpc ? "denied" : "granted" });
  gtag("js", new Date());
  gtag("config", id, { allow_google_signals: false, allow_ad_personalization_signals: false });
  function load() { var g = document.createElement("script"); g.async = true; g.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id); document.head.appendChild(g); }
  if (document.readyState === "complete") setTimeout(load, 1500); else window.addEventListener("load", function () { setTimeout(load, 1500); });
})();
