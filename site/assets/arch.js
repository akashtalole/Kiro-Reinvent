/* Clickable architecture diagram for the home page.
   Every tile is a link to the lab that teaches it; hover/focus shows a live preview of that lab. */
(function () {
  "use strict";
  var P = {
    building: "M4 21V5l8-3 8 3v16M9 21v-4h6v4M8 8h2M14 8h2M8 12h2M14 12h2",
    key: "M14 7a4 4 0 1 1-3.9 4.9L3 19v2h3v-2h2v-2h2l1.1-1.1A4 4 0 0 1 14 7zM15.5 8.5h.01",
    shield: "M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3zM9 12l2 2 4-4",
    filter: "M3 5h18l-7 8v6l-4 2v-8L3 5z",
    bug: "M8 8a4 4 0 0 1 8 0v1H8V8zM6 9h12v5a6 6 0 0 1-12 0V9zM12 9v11M3 13h3M18 13h3M4 7l3 2M20 7l-3 2M4 19l3-2M20 19l-3-2",
    user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
    users: "M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 20a7 7 0 0 1 14 0M16 4.5a3.5 3.5 0 0 1 0 6.5M18 20a6 6 0 0 0-2.5-5",
    layers: "M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5M3 17l9 5 9-5",
    code: "M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16",
    spark: "M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2L12 3z",
    check: "M4 12l5 5L20 6",
    pulse: "M3 12h4l3-7 4 14 3-7h4",
    lock: "M6 11h12v10H6V11zM8 11V7a4 4 0 0 1 8 0v4",
    coin: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM15 9.5c-.5-1-1.6-1.5-3-1.5-1.8 0-3 .9-3 2s1 1.7 3 2 3 .9 3 2-1.2 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6.5V8M12 16v1.5",
    chat: "M4 5h16v11H9l-5 4V5z",
    doc: "M6 3h9l4 4v14H6V3zM14 3v5h5M9 13h7M9 17h7",
    compass: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM15.5 8.5l-2 5-5 2 2-5 5-2z",
    puzzle: "M9 4h3a2 2 0 1 1 4 0h3v5a2 2 0 1 1 0 4v6h-5a2 2 0 1 0-4 0H4v-5a2 2 0 1 0 0-4V4h5z",
    hook: "M12 3v10a4 4 0 1 1-4-4M12 3l3 3",
    bot: "M6 9h12v10H6V9zM12 5v4M12 4h.01M9.5 13h.01M14.5 13h.01M9 16h6M3 13v3M21 13v3",
    plug: "M9 3v5M15 3v5M6 8h12v4a6 6 0 0 1-12 0V8zM12 18v3",
    terminal: "M4 5h16v14H4V5zM7 9l3 3-3 3M12 15h5",
    flow: "M5 6a2 2 0 1 0 0 .01M19 18a2 2 0 1 0 0 .01M7 6h6a3 3 0 0 1 3 3v6a3 3 0 0 0 3 3",
    clock: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2",
    rocket: "M5 15c-1 2-1 4-1 4s2 0 4-1M9 15l-3-3c1-4 5-9 12-9 0 7-5 11-9 12zM15 9h.01",
    memory: "M6 4h12v16H6V4zM9 8h6M9 12h6M9 16h3M3 8h3M3 16h3M18 8h3M18 16h3",
    db: "M12 8c4.4 0 8-1.3 8-3s-3.6-3-8-3-8 1.3-8 3 3.6 3 8 3zM4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
    cloud: "M7 18a5 5 0 1 1 1-9.9A6 6 0 0 1 19 10a4 4 0 0 1-1 8H7z",
    chip: "M7 7h10v10H7V7zM10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4",
    eye: "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
  };
  function icon(name) {
    return '<svg class="arch-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="' + (P[name] || P.spark) + '"/></svg>';
  }

  function render(root, A, byId, K) {
    var esc = K.esc;
    function item(it, cls) {
      var lab = byId[it.lab];
      if (!lab) return "";
      return '<a class="arch-item ' + (cls || "") + '" href="' + K.labHref(lab) + '" data-lab="' + lab.id + '">' + icon(it.icon) +
        '<span class="arch-txt"><span class="arch-lbl">' + esc(it.label) + '</span><span class="arch-lab">Lab ' + lab.id + "</span></span></a>";
    }
    function band(b, pos) {
      return '<div class="arch-band arch-' + pos + '"><div class="arch-band-lbl">' + esc(b.label) + '</div><div class="arch-band-items">' +
        b.items.map(function (it) { return item(it, "chip"); }).join("") + "</div></div>";
    }
    function panel(g, cls) {
      return '<div class="arch-panel ' + (cls || "") + '"><div class="arch-panel-lbl">' + esc(g.label) + "</div>" +
        '<div class="arch-list">' + g.items.map(function (it) { return item(it); }).join("") + "</div></div>";
    }
    root.innerHTML =
      band(A.top, "top") +
      '<div class="arch-vline" aria-hidden="true"></div>' +
      '<div class="arch-row">' +
        panel(A.left, "arch-left") +
        '<div class="arch-arrow" aria-hidden="true"></div>' +
        '<div class="arch-hub"><div class="arch-hub-head"><span class="arch-hub-mark">K</span><span class="arch-hub-title">' + esc(A.hub.label) +
          '</span><span class="arch-badge">' + esc(A.hubBadge) + '</span></div><div class="arch-grid">' +
          A.hub.items.map(function (it) { return item(it); }).join("") + "</div>" +
          (A.surfaces ? '<div class="arch-surfaces"><div class="arch-panel-lbl">' + esc(A.surfaces.label) + '</div><div class="arch-band-items">' +
            A.surfaces.items.map(function (it) { return item(it, "chip"); }).join("") + "</div></div>" : "") + "</div>" +
        '<div class="arch-arrow" aria-hidden="true"></div>' +
        '<div class="arch-right">' + panel(A.rightTop) + panel(A.rightBottom) + "</div>" +
      "</div>" +
      '<div class="arch-vline" aria-hidden="true"></div>' +
      band(A.bottom, "bottom") +
      '<div class="arch-preview" aria-live="polite"><span class="muted">Select any part to preview the lab that teaches it.</span></div>';

    var preview = root.querySelector(".arch-preview");
    function show(el) {
      var lab = byId[el.getAttribute("data-lab")];
      if (!lab) return;
      root.querySelectorAll(".arch-item.on").forEach(function (x) { x.classList.remove("on"); });
      root.querySelectorAll('.arch-item[data-lab="' + lab.id + '"]').forEach(function (x) { x.classList.add("on"); });
      preview.innerHTML = '<span class="lab-num">LAB ' + lab.id + " · " + esc(lab.category) + "</span>" +
        '<a class="arch-pv-title" href="' + K.labHref(lab) + '">' + esc(lab.title) + " →</a>" +
        '<span class="arch-pv-sum">' + esc(lab.summary) + "</span>" +
        '<span class="arch-pv-meta">' + K.levelChip(lab.level) + '<span class="chip">⏱ ' + esc(lab.duration) + "</span></span>";
    }
    root.addEventListener("mouseover", function (e) { var a = e.target.closest(".arch-item"); if (a) show(a); });
    root.addEventListener("focusin", function (e) { var a = e.target.closest(".arch-item"); if (a) show(a); });
  }

  window.KRLArch = { render: render };
})();
