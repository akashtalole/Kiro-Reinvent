/* Markdown rendering for lab and doc pages: front matter, links, headings, code, mermaid */
(function () {
  "use strict";
  var K = window.KRL;

  function stripFrontMatter(md) {
    if (md.indexOf("---") !== 0) return md;
    var end = md.indexOf("\n---", 3);
    return end === -1 ? md : md.slice(end + 4).replace(/^\s+/, "");
  }
  function slugify(t) {
    return t.toLowerCase().replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-").slice(0, 80);
  }

  // base: "labs/<slug>/" or "docs/"
  function rewriteLink(href, base) {
    if (!href || /^(https?:|mailto:|#|data:)/.test(href)) return href;
    var lab = /(?:^|\/)labs\/([^/]+)\/(?:README\.md)?(#.*)?$/.exec(href) || /^\.\.\/([^/]+)\/(?:README\.md)?(#.*)?$/.exec(href);
    if (lab && base.indexOf("labs/") === 0) return "lab.html?id=" + lab[1] + (lab[2] || "");
    if (/^(\.\.\/)*labs\/([^/]+)\/?(README\.md)?(#.*)?$/.test(href)) {
      var m = /labs\/([^/]+)/.exec(href); return "lab.html?id=" + m[1];
    }
    var doc = /(?:^|\/)docs\/([\w-]+)\.md(#.*)?$/.exec(href) || (base === "docs/" && /^(?:\.\/)?([\w-]+)\.md(#.*)?$/.exec(href));
    if (doc) return "doc.html?doc=" + doc[1] + (doc[2] || "");
    // any other relative file: point at the GitHub source so .py/.json/.ts files are viewable
    var clean = href.replace(/^\.\//, "");
    var repoPath = base.indexOf("labs/") === 0 ? base + clean : (base === "docs/" ? "docs/" + clean : clean);
    while (/[^/.][^/]*\/\.\.\//.test(repoPath)) repoPath = repoPath.replace(/[^/.][^/]*\/\.\.\//, "");
    return K.REPO + "/blob/main/" + repoPath;
  }

  function markdown(target, md, base) {
    var html = window.marked.parse(stripFrontMatter(md), { gfm: true });
    target.innerHTML = html;

    var seen = {};
    target.querySelectorAll("h1, h2, h3, h4").forEach(function (h) {
      var id = slugify(h.textContent) || "section";
      while (seen[id]) id += "-x";
      seen[id] = true; h.id = id;
    });
    target.querySelectorAll("a[href]").forEach(function (a) {
      var nh = rewriteLink(a.getAttribute("href"), base);
      a.setAttribute("href", nh);
      if (/^https?:/.test(nh) && nh.indexOf(location.host) === -1) a.setAttribute("rel", "noopener");
    });
    target.querySelectorAll("img[src]").forEach(function (img) {
      var s = img.getAttribute("src");
      if (!/^(https?:|data:)/.test(s)) img.setAttribute("src", base + s.replace(/^\.\//, ""));
    });

    var mermaidBlocks = [];
    target.querySelectorAll("pre > code").forEach(function (code) {
      var pre = code.parentElement;
      if (code.classList.contains("language-mermaid")) {
        var div = document.createElement("div");
        div.className = "mermaid";
        div.setAttribute("data-src", code.textContent);
        div.textContent = code.textContent;
        pre.replaceWith(div);
        mermaidBlocks.push(div);
        return;
      }
      if (window.hljs) { try { window.hljs.highlightElement(code); } catch (e) { /* unknown lang */ } }
      var btn = document.createElement("button");
      btn.className = "copy-btn"; btn.type = "button"; btn.textContent = "Copy";
      btn.addEventListener("click", function () {
        var done = function () { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1400); };
        if (navigator.clipboard) navigator.clipboard.writeText(code.textContent).then(done, function () {});
      });
      pre.appendChild(btn);
    });

    function drawMermaid() {
      if (!window.mermaid || !mermaidBlocks.length) return;
      var dark = K.theme() === "dark";
      window.mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "neutral", securityLevel: "strict", fontFamily: "Inter, system-ui, sans-serif" });
      mermaidBlocks.forEach(function (d) { d.removeAttribute("data-processed"); d.textContent = d.getAttribute("data-src"); });
      try { window.mermaid.run({ nodes: mermaidBlocks }); } catch (e) { /* leave source visible */ }
    }
    drawMermaid();
    document.addEventListener("krl-theme", drawMermaid);
  }

  window.KRLRender = { markdown: markdown, stripFrontMatter: stripFrontMatter };
})();
