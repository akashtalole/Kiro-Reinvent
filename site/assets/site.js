/* Kiro Reinvent Labs — shared chrome (header, footer, theme, search) and data helpers */
(function () {
  "use strict";
  var REPO = "https://github.com/akashtalole/Kiro-Reinvent";
  var root = document.documentElement;

  // ---------- theme ----------
  try {
    var saved = localStorage.getItem("krl-theme");
    if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);
  } catch (e) { /* storage unavailable */ }
  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function toggleTheme() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("krl-theme", next); } catch (e) { /* ignore */ }
    document.dispatchEvent(new CustomEvent("krl-theme", { detail: next }));
  }

  // ---------- data ----------
  var cache = {};
  function getJSON(url) {
    if (!cache[url]) cache[url] = fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " → " + r.status);
      return r.json();
    });
    return cache[url];
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function levelChip(level) {
    var cls = level === "Beginner" ? "ok" : level === "Advanced" ? "warm" : "accent";
    return '<span class="chip ' + cls + '">' + esc(level) + "</span>";
  }
  function labHref(lab) { return "lab.html?id=" + encodeURIComponent(lab.slug); }
  function labCard(lab, opts) {
    opts = opts || {};
    var services = (lab.services || []).slice(0, opts.maxServices || 3)
      .map(function (s) { return '<span class="chip">' + esc(s) + "</span>"; }).join("");
    return '<a class="card lab-card" href="' + labHref(lab) + '">' +
      '<div class="top"><span class="lab-num">LAB ' + esc(lab.id) + " · " + esc(lab.category) + "</span></div>" +
      "<h3>" + esc(lab.title) + "</h3><p>" + esc(lab.summary) + "</p>" +
      '<div class="meta">' + levelChip(lab.level) + '<span class="chip">⏱ ' + esc(lab.duration) + "</span>" + services + "</div></a>";
  }

  // ---------- chrome ----------
  var page = document.body.getAttribute("data-page") || "";
  function nav(href, label, key) {
    return '<a href="' + href + '"' + (page === key ? ' aria-current="page"' : "") + ">" + label + "</a>";
  }
  var PRIMARY = [
    ["labs.html", "All labs", "labs"],
    ["index.html#paths", "Learning paths", ""],
    ["use-cases.html", "Use cases", "usecases"],
    ["scenarios.html", "Scenarios", "scenarios"],
    ["doc.html?doc=ai-first-saas-playbook", "AI-first SaaS", "aifirst"],
    ["doc.html?doc=kiro-in-the-field", "From the field", "field"]
  ];
  var EXTRA = [
    ["index.html", "Home", "home"],
    ["doc.html?doc=landscape", "Landscape", "landscape"],
    ["doc.html?doc=architecture-patterns", "Architecture patterns", "patterns"],
    ["doc.html?doc=advanced-scenarios", "Scenarios (markdown)", "advanced-scenarios"],
    ["doc.html?doc=setup", "Setup guide", "setup"],
    [REPO, "GitHub repository", "github"]
  ];
  var header = document.createElement("header");
  header.className = "site-header";
  header.innerHTML =
    '<div class="wrap">' +
    '<a class="brand" href="index.html"><span class="brand-mark">K</span><span>Kiro Reinvent Labs</span></a>' +
    '<nav class="nav" aria-label="Primary">' + PRIMARY.map(function (x) { return nav(x[0], x[1], x[2]); }).join("") + "</nav>" +
    '<span class="header-spacer"></span>' +
    '<button class="search-btn" type="button" id="open-search" aria-label="Search labs">' +
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
    '<span class="label">Search labs</span><kbd>Ctrl K</kbd></button>' +
    '<button class="icon-btn menu-btn" type="button" id="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav">' +
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>' +
    '<button class="icon-btn" type="button" id="theme-toggle" aria-label="Toggle colour theme" title="Toggle theme">' +
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>' +
    '<a class="icon-btn gh-btn" href="' + REPO + '" aria-label="GitHub repository" title="GitHub">' +
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.6 18.3 5 18.3 5c.7 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .5z"/></svg></a>' +
    "</div>";
  var mnav = document.createElement("nav");
  mnav.className = "mobile-nav"; mnav.id = "mobile-nav"; mnav.setAttribute("aria-label", "Menu"); mnav.hidden = true;
  mnav.innerHTML = '<div class="wrap">' + PRIMARY.concat(EXTRA).map(function (x) { return nav(x[0], x[1], x[2]); }).join("") + "</div>";
  header.appendChild(mnav);
  document.body.insertBefore(header, document.body.firstChild);
  var menuBtn = header.querySelector("#menu-toggle");
  function setMenu(open) {
    mnav.hidden = !open; menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }
  menuBtn.addEventListener("click", function () { setMenu(mnav.hidden); });
  mnav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !mnav.hidden) { setMenu(false); menuBtn.focus(); } });

  var footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.innerHTML =
    '<div class="wrap"><div class="cols">' +
    '<div><a class="brand" href="index.html"><span class="brand-mark">K</span><span>Kiro Reinvent Labs</span></a>' +
    '<p style="max-width:360px">Hands-on labs for building end-to-end solutions with Kiro, AWS MCP servers, Strands Agents and Amazon Bedrock AgentCore.</p></div>' +
    "<div><h5>Learn</h5><ul>" +
    '<li><a href="labs.html">All labs</a></li><li><a href="index.html#paths">Learning paths</a></li>' +
    '<li><a href="use-cases.html">Use cases</a></li><li><a href="scenarios.html">Advanced scenarios</a></li><li><a href="index.html#field">From the field</a></li><li><a href="doc.html?doc=setup">Setup guide</a></li></ul></div>' +
    "<div><h5>Reference</h5><ul>" +
    '<li><a href="doc.html?doc=landscape">Product landscape</a></li><li><a href="doc.html?doc=architecture-patterns">Architecture patterns</a></li>' +
    '<li><a href="doc.html?doc=aws-mcp-catalog">AWS MCP catalog</a></li><li><a href="doc.html?doc=kiro-in-the-field">Kiro in the field</a></li><li><a href="doc.html?doc=frontier-engineering-teams">Frontier engineering teams</a></li><li><a href="doc.html?doc=kiro-features-in-this-repo">Kiro features in this repo</a></li><li><a href="doc.html?doc=kiro-ide-cli-internals">IDE vs CLI vs Crew</a></li><li><a href="doc.html?doc=kiro-crew-internals">Kiro Crew internals</a></li><li><a href="doc.html?doc=ai-first-saas-playbook">AI-first SaaS playbook</a></li><li><a href="doc.html?doc=troubleshooting">Troubleshooting</a></li></ul></div>' +
    "<div><h5>Contribute</h5><ul>" +
    '<li><a href="' + REPO + '">GitHub</a></li><li><a href="doc.html?doc=authoring">Authoring guide</a></li>' +
    '<li><a href="' + REPO + '/tree/main/.kiro/skills/lab-creator">Lab-creator skill</a></li>' +
    '<li><a href="' + REPO + '/issues/new">Report an issue</a></li></ul></div>' +
    "</div>" +
    '<p class="disclaimer">Community project. Not affiliated with, endorsed by, or an official resource of Amazon Web Services. Product names are trademarks of their owners. ' +
    "Features evolve quickly — every lab links to the official docs; verify against them before production use. MIT licensed.</p></div>";
  document.body.appendChild(footer);

  document.getElementById("theme-toggle").addEventListener("click", toggleTheme);

  // ---------- search dialog ----------
  var dlg = document.createElement("dialog");
  dlg.className = "search";
  dlg.innerHTML = '<input type="search" placeholder="Search labs, services, tags…" aria-label="Search labs"><ul></ul>';
  document.body.appendChild(dlg);
  var input = dlg.querySelector("input"), list = dlg.querySelector("ul"), active = 0;
  function render(q) {
    getJSON("data/labs.json").then(function (data) {
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      var hits = data.labs.filter(function (l) {
        var hay = [l.id, l.title, l.summary, l.category, l.level].concat(l.services || [], l.tags || []).join(" ").toLowerCase();
        return terms.every(function (t) { return hay.indexOf(t) !== -1; });
      }).slice(0, 12);
      active = 0;
      list.innerHTML = hits.length ? hits.map(function (l, i) {
        return '<li><a href="' + labHref(l) + '"' + (i === 0 ? ' class="active"' : "") + '><span class="lab-num">' + esc(l.id) +
          "</span><span>" + esc(l.title) + "</span><small>" + esc(l.category) + "</small></a></li>";
      }).join("") : '<li class="muted" style="padding:14px">No labs match.</li>';
    });
  }
  function openSearch() { if (!dlg.open) { dlg.showModal(); input.value = ""; render(""); input.focus(); } }
  document.getElementById("open-search").addEventListener("click", openSearch);
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
  });
  input.addEventListener("input", function () { render(input.value); });
  input.addEventListener("keydown", function (e) {
    var links = list.querySelectorAll("a");
    if (!links.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      links[active].classList.remove("active");
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
      links[active].classList.add("active");
      links[active].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") { location.href = links[active].getAttribute("href"); }
  });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });

  window.KRL = { getJSON: getJSON, esc: esc, labCard: labCard, labHref: labHref, levelChip: levelChip, REPO: REPO, theme: currentTheme };
})();
