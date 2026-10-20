/* Angelo Forte, DMD: site behaviour. No dependencies. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* Header: solid once scrolled, hides on scroll down, returns on scroll up. */
  var header = $("[data-header]");
  var callbar = $("[data-callbar]");
  var lastY = window.scrollY;
  function onScroll() {
    var y = window.scrollY;
    if (header) {
      var hero = $(".hero");
      var threshold = hero ? hero.offsetHeight - 90 : 8;
      header.classList.toggle("scrolled", y > (header.classList.contains("on-dark") ? threshold : 8));
      var goingDown = y > lastY + 4, goingUp = y < lastY - 4;
      if (!document.body.classList.contains("nav-locked") && !header.contains(document.activeElement)) {
        if (goingDown && y > 500) header.classList.add("hide");
        else if (goingUp || y < 200) header.classList.remove("hide");
      }
    }
    if (callbar) callbar.classList.toggle("show", y > 420);
    lastY = y;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile menu. Closed sheet is visibility:hidden + inert, so it is out of the tab order. */
  var menuBtn = $("[data-menu]"), sheet = $("[data-sheet]");
  function setMenu(open) {
    if (!menuBtn || !sheet) return;
    menuBtn.setAttribute("aria-expanded", String(open));
    sheet.classList.toggle("open", open);
    if (open) sheet.removeAttribute("inert"); else sheet.setAttribute("inert", "");
    document.body.classList.toggle("nav-locked", open);
    if (open) { header.classList.remove("hide"); var first = $("a", sheet); if (first) first.focus(); }
  }
  if (sheet) sheet.setAttribute("inert", "");
  if (menuBtn) menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (menuBtn && menuBtn.getAttribute("aria-expanded") === "true") { setMenu(false); menuBtn.focus(); }
    $$(".has-mega.open").forEach(function (li) { li.classList.remove("open"); var b = $(".mega-btn", li); b.setAttribute("aria-expanded", "false"); b.focus(); });
  });
  window.matchMedia("(min-width: 1081px)").addEventListener("change", function (m) { if (m.matches) setMenu(false); });

  /* Services mega menu: hover on desktop, button for keyboard and touch. */
  $$(".mega-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-mega"), open = !li.classList.contains("open");
      li.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });
  document.addEventListener("click", function (e) {
    $$(".has-mega.open").forEach(function (li) {
      if (!li.contains(e.target)) { li.classList.remove("open"); $(".mega-btn", li).setAttribute("aria-expanded", "false"); }
    });
  });

  /* Scroll reveals. */
  var rv = $$(".rv");
  if ("IntersectionObserver" in window && !reduce.matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    rv.forEach(function (el) { io.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add("in"); });
  }

  /* Pointer-following light on cards and buttons. */
  $$(".intent, .svc-card, .btn").forEach(function (el) {
    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty("--mx", (e.clientX - r.left) + "px");
      el.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });

  /* Hero video. The poster is the LCP image; the video streams in after load, only on
     wider screens, never under reduced motion or Save-Data. */
  var hero = $(".hero"), video = $(".hero-video"), toggle = $("[data-video-toggle]");
  function canPlayVideo() {
    var c = navigator.connection || {};
    if (reduce.matches || c.saveData || /(^|-)2g$/.test(c.effectiveType || "")) return false;
    return window.matchMedia("(min-width: 768px)").matches;
  }
  // data-src-1080 / -720 have no camelCase dataset key (a dash before a digit isn't converted), so read attributes.
  var srcAttr = function (n) { return video.getAttribute("data-src-" + n) || ""; };
  function pickSource() {
    var px = window.innerWidth * Math.min(window.devicePixelRatio || 1, 2);
    var av1 = video.canPlayType('video/webm; codecs="av01.0.08M.08"');
    if (av1 === "probably" && px >= 1280 && srcAttr("av1").indexOf("pending") < 0) return srcAttr("av1");
    return px >= 1500 ? srcAttr("1080") : srcAttr("720");
  }
  function startVideo() {
    if (!video || !canPlayVideo()) return;
    var src = pickSource();
    if (!src || src.indexOf("pending") >= 0) return;
    // If the AV1 file can't be fetched or decoded (a browser can claim support and still fail),
    // drop to H.264, which every browser plays.
    var fellBack = false;
    var fallback = function () {
      if (fellBack || video.src.indexOf(".webm") < 0) return;
      fellBack = true;
      video.src = window.innerWidth * Math.min(window.devicePixelRatio || 1, 2) >= 1500 ? srcAttr("1080") : srcAttr("720");
      var p2 = video.play();
      if (p2 && p2.catch) p2.catch(function () {});
    };
    video.addEventListener("error", fallback);
    video.src = src;
    video.addEventListener("playing", function () { hero.classList.add("video-live"); if (toggle) toggle.hidden = false; }, { once: true });
    var p = video.play();
    if (p && p.catch) p.catch(function (err) { if (err && err.name === "NotSupportedError") fallback(); });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        if (toggle && toggle.getAttribute("aria-pressed") === "true") return;
        if (en[0].isIntersecting) video.play().catch(function () {}); else video.pause();
      }).observe(hero);
    }
  }
  if (video) {
    var kick = function () { ("requestIdleCallback" in window) ? requestIdleCallback(startVideo, { timeout: 2500 }) : setTimeout(startVideo, 800); };
    if (document.readyState === "complete") kick(); else window.addEventListener("load", kick);
  }
  if (toggle) toggle.addEventListener("click", function () {
    var paused = toggle.getAttribute("aria-pressed") === "true";
    toggle.setAttribute("aria-pressed", String(!paused));
    if (paused) video.play().catch(function () {}); else video.pause();
  });

  /* Philosophy statement: words light up as the section crosses the viewport. */
  var stmt = $("[data-words]");
  if (stmt && !reduce.matches) {
    var words = $$(".w", stmt), ticking = false;
    var paint = function () {
      ticking = false;
      var r = stmt.getBoundingClientRect(), vh = window.innerHeight;
      var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
      var n = Math.round(p * words.length);
      for (var i = 0; i < words.length; i++) words[i].classList.toggle("lit", i < n);
    };
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(paint); } }, { passive: true });
    paint();
  }

  /* Rolling photo strip: pause button (WCAG 2.2.2) and pause while off-screen. */
  var strip = $("[data-strip]"), stripBtn = $("[data-strip-toggle]");
  if (strip) {
    $$(".strip-track > li", strip).forEach(function (li, i, all) {
      if (i >= all.length / 2) { li.setAttribute("aria-hidden", "true"); $$("img", li).forEach(function (im) { im.alt = ""; }); }
    });
    if (stripBtn) stripBtn.addEventListener("click", function () {
      var on = stripBtn.getAttribute("aria-pressed") !== "true";
      stripBtn.setAttribute("aria-pressed", String(on));
      strip.classList.toggle("paused", on);
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        if (stripBtn && stripBtn.getAttribute("aria-pressed") === "true") return;
        strip.classList.toggle("paused", !en[0].isIntersecting);
      }).observe(strip);
    }
  }

  /* Table of contents highlight. */
  var tocLinks = $$(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var tocIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.remove("active"); });
        if (byId[en.target.id]) byId[en.target.id].classList.add("active");
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) tocIO.observe(el); });
  }

  /* Live Google reviews: rendered only when /api/reviews has data (GOOGLE_PLACES_API_KEY set). */
  var slots = $$("[data-greviews]");
  if (slots.length && window.fetch) {
    fetch("/api/reviews/", { headers: { accept: "application/json" } }).then(function (r) {
      return r.ok && r.status === 200 ? r.json() : null;
    }).then(function (d) {
      if (!d || !d.rating) return;
      var star = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>';
      var esc = function (s) { var e = document.createElement("span"); e.textContent = s || ""; return e.innerHTML; };
      slots.forEach(function (slot) {
        var stars = ""; for (var i = 0; i < Math.round(d.rating); i++) stars += star;
        var list = (d.reviews || []).slice(0, 3).map(function (rv) {
          return '<figure class="g-item"><blockquote><p>' + esc(rv.text) + '</p></blockquote><figcaption><cite>' + esc(rv.author) + "</cite> &middot; " + esc(rv.when) + "</figcaption></figure>";
        }).join("");
        slot.innerHTML = '<p class="g-sum"><span class="g-stars" aria-hidden="true">' + stars + "</span><span>" + d.rating.toFixed(1) + " on Google from " + d.count + ' reviews</span><a href="' + esc(d.url) + '" target="_blank" rel="noopener">See them on Google<span class="sr"> (opens in a new tab)</span></a></p><div class="g-list">' + list + "</div>";
        slot.hidden = false;
      });
    }).catch(function () {});
  }

  /* Conversion events: phone taps and form submits. Sent only where analytics is enabled. */
  function track(name, data) {
    if (typeof window.gtag === "function") window.gtag("event", name, data || {});
    if (typeof window.va === "function") window.va("event", { name: name, data: data || {} });
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"]');
    if (a) track("call_click", { location: a.getAttribute("data-track") || "link", page: location.pathname });
  });

  /* Appointment-request form (only rendered when FORM_ENDPOINT is configured). */
  var form = $("[data-form]");
  if (form) {
    var opened = Date.now(), status = $("[data-form-status]", form);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.querySelector('[name="_honey"]').value || Date.now() - opened < 3000) { status.textContent = "Thanks, we'll be in touch."; return; }
      status.textContent = "Sending…";
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { accept: "application/json" } }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        status.textContent = "Thank you. The office will call you back during business hours.";
        form.reset();
        track("form_submit", { form: "appointment_request" });
      }).catch(function () {
        status.textContent = "Sorry, that didn't send. Please call (561) 747-2134.";
      });
    });
  }
})();
