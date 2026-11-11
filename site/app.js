/* The High Scalability Index — hash-routed SPA over window.HS_DATA. */
(function () {
  "use strict";

  const D = window.HS_DATA;
  const PAGE_SIZE = 8;

  const topicsBySlug = new Map(D.topics.map((t) => [t.slug, t]));
  const slugOf = new Map(); // topic slug -> ordered article indices (newest first)
  D.articles.forEach(function (a, i) {
    a.tp.forEach(function (s) {
      if (!slugOf.has(s)) slugOf.set(s, []);
      slugOf.get(s).push(i);
    });
  });
  // default ordering in data is date-desc already; keep it stable
  slugOf.forEach(function (list) {
    list.sort(function (x, y) {
      return D.articles[y].d < D.articles[x].d ? -1 : D.articles[y].d > D.articles[x].d ? 1 : 0;
    });
  });

  const el = function (id) { return document.getElementById(id); };
  const sectionsEl = el("sections");
  const railList = el("rail-list");
  const kicker = el("kicker");
  const sectionTitle = el("section-title");
  const standfirst = el("standfirst");
  const results = el("results");
  const emptyEl = el("empty");
  const resultsMeta = el("results-meta");
  const pager = el("pager");
  const prevBtn = el("prev");
  const nextBtn = el("next");
  const pageInfo = el("page-info");
  const continued = el("continued");
  const search = el("search");
  const yearSel = el("year");
  const sortSel = el("sort");
  const filterRow = el("filter-row");
  const volCounts = el("vol-counts");

  const state = {
    slug: "scalability-architecture-patterns",
    page: 0,
    q: "",
    year: "",
    sort: "new",
    searching: false,
    expanded: new Set(),
  };

  const GLOSS = {
    "scalability-architecture-patterns": "sharding, replication, partitioning, capacity",
    "link-roundups": "the weekly web roundup",
    "war-stories": "how real systems scale",
    "sponsored-posts": "from our partners",
    "papers-books-research": "papers and books worth reading",
  };

  function quintile(count, max) {
    if (max <= 0) return 1;
    const q = Math.ceil((count / max) * 5);
    return Math.min(5, Math.max(1, q));
  }

  function renderRail() {
    const max = D.topics.length ? D.topics[0].count : 1;
    const frag = document.createDocumentFragment();
    let bucketOpen = false;
    D.topics.forEach(function (t) {
      if (t.bucket && !bucketOpen) {
        bucketOpen = true;
        const head = document.createElement("li");
        head.className = "bucket-head";
        head.textContent = "Content types";
        frag.appendChild(head);
      }
      const li = document.createElement("li");
      li.className = t.slug === state.slug ? "on" : "";
      const a = document.createElement("a");
      a.href = "#/topic/" + t.slug;
      const name = document.createElement("span");
      name.textContent = t.name;
      const n = document.createElement("span");
      n.className = "n d" + quintile(t.count, max);
      n.textContent = String(t.count);
      a.appendChild(name);
      a.appendChild(n);
      li.appendChild(a);
      frag.appendChild(li);
    });
    railList.replaceChildren(frag);
  }

  function rowFor(article, no) {
    const li = document.createElement("li");
    li.id = "row-" + no;

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "row-main row-toggle";
    toggle.setAttribute("aria-expanded", state.expanded.has(no) ? "true" : "false");
    toggle.setAttribute("aria-controls", "x-" + no);

    const date = document.createElement("span");
    date.className = "row-date";
    date.textContent = fmtDate(article.d);
    const title = document.createElement("span");
    title.className = "row-title";
    const link = document.createElement("a");
    link.href = article.u;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = article.t;
    link.addEventListener("click", function (e) { e.stopPropagation(); });
    title.appendChild(link);
    const by = document.createElement("span");
    by.className = "row-by";
    by.textContent = article.a;
    const noEl = document.createElement("span");
    noEl.className = "row-no";
    noEl.textContent = "№ " + no;
    toggle.append(date, title, by, noEl);

    const exc = document.createElement("p");
    exc.className = "row-excerpt";
    exc.id = "x-" + no;
    exc.textContent = article.e ? article.e + " " : "";
    const open = document.createElement("a");
    open.href = article.u;
    open.target = "_blank";
    open.rel = "noopener noreferrer";
    open.textContent = "Read the original →";
    exc.appendChild(open);

    li.appendChild(toggle);
    li.appendChild(exc);
    if (state.expanded.has(no)) li.classList.add("expanded");
    toggle.addEventListener("click", function () {
      const on = li.classList.toggle("expanded");
      toggle.setAttribute("aria-expanded", on ? "true" : "false");
      if (on) state.expanded.add(no); else state.expanded.delete(no);
    });
    return li;
  }

  function fmtDate(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    if (!m) return iso;
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const day = String(parseInt(m[3], 10));
    return day + " " + months[parseInt(m[2], 10) - 1] + " " + m[1];
  }

  function applyFilters(list) {
    let out = list.filter(function (i) {
      const a = D.articles[i];
      if (state.year && a.d.slice(0, 4) !== state.year) return false;
      if (state.q) {
        const hay = (a.t + " " + a.a + " " + a.e).toLowerCase();
        if (hay.indexOf(state.q.toLowerCase()) === -1) return false;
      }
      return true;
    });
    if (state.sort === "old") out = out.slice().reverse();
    return out;
  }

  function searchAll() {
    const out = [];
    D.articles.forEach(function (a, i) {
      const hay = (a.t + " " + a.a + " " + a.e).toLowerCase();
      if (hay.indexOf(state.q.toLowerCase()) !== -1) out.push(i);
    });
    return out;
  }

  function renderYears(list) {
    const years = new Set(list.map(function (i) { return D.articles[i].d.slice(0, 4); }));
    const cur = state.year;
    yearSel.replaceChildren();
    const all = document.createElement("option");
    all.value = "";
    all.textContent = "All years";
    yearSel.appendChild(all);
    Array.from(years).sort().reverse().forEach(function (y) {
      const o = document.createElement("option");
      o.value = y;
      o.textContent = y;
      yearSel.appendChild(o);
    });
    if (cur && years.has(cur)) yearSel.value = cur; else { yearSel.value = ""; state.year = ""; }
  }

  function render() {
    renderRail();

    let list, label, roman;
    const topic = state.searching ? null : topicsBySlug.get(state.slug);

    if (state.searching) {
      list = searchAll();
      kicker.textContent = "Search";
      sectionTitle.textContent = "“" + state.q + "”";
      standfirst.textContent = list.length + " matching articles across all sections";
      roman = "";
    } else {
      list = slugOf.get(state.slug) || [];
      const latestYear = list.length ? D.articles[list[0]].d.slice(0, 4) : "";
      kicker.textContent = "Section " + romanOf(D.topics.findIndex(function (t) { return t.slug === state.slug; }) + 1) +
        (latestYear ? " · Arrived " + latestYear : "");
      sectionTitle.textContent = topic.name;
      standfirst.textContent = topic.count + " articles · " + (GLOSS[topic.slug] || "the complete section, newest first");
      roman = "";
    }

    renderYears(list);
    const filtered = applyFilters(list);
    const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    if (state.page >= pages) state.page = pages - 1;
    const start = state.page * PAGE_SIZE;
    const slice = filtered.slice(start, start + PAGE_SIZE);

    resultsMeta.textContent = filtered.length + " entries" +
      (state.page > 0 || filtered.length > PAGE_SIZE
        ? " · showing " + (start + 1) + "–" + (start + slice.length) : "");

    const frag = document.createDocumentFragment();
    const topicCount = topic ? topic.count : D.articles.length;
    slice.forEach(function (i, k) {
      const no = topic
        ? (state.sort === "old"
          ? topicCount - filtered.indexOf(i)
          : topicCount - (start + k))
        : filtered.length - (start + k);
      frag.appendChild(rowFor(D.articles[i], Math.max(1, no)));
    });
    results.replaceChildren(frag);
    // open the last row's summary, like a broadsheet's closing abstract
    if (slice.length) {
      const lastToggle = results.lastElementChild.querySelector(".row-toggle");
      if (lastToggle && lastToggle.getAttribute("aria-expanded") === "false") lastToggle.click();
    }
    if (filtered.length > 50) results.setAttribute("aria-busy", "false");

    emptyEl.hidden = filtered.length > 0;
    results.hidden = filtered.length === 0;
    pager.hidden = pages <= 1;
    prevBtn.disabled = state.page === 0;
    nextBtn.disabled = state.page >= pages - 1;
    pageInfo.textContent = "Page " + (state.page + 1) + " of " + pages;

    const remaining = filtered.length - start - slice.length;
    continued.textContent = remaining > 0
      ? "Continued · " + remaining + " earlier " + (remaining === 1 ? "entry" : "entries")
      : (filtered.length > PAGE_SIZE ? "End of the section" : "");

    filterRow.hidden = state.searching;
    document.title = (state.searching ? "Search" : topic.name) + " · The High Scalability Index";
  }

  function romanOf(n) {
    const r = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
      "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
      "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI"];
    return r[n - 1] || String(n);
  }

  function route() {
    const h = decodeURIComponent(location.hash || "#/");
    state.expanded.clear();
    state.page = 0;
    state.searching = false;
    if (h.indexOf("#/topic/") === 0) {
      const slug = h.slice(8).split("?")[0].replace(/\/+$/, "");
      state.slug = topicsBySlug.has(slug) ? slug : "scalability-architecture-patterns";
      state.q = "";
      search.value = "";
    } else if (h.indexOf("#/search/") === 0) {
      state.searching = true;
      state.q = h.slice(9).replace(/\/+$/, "");
      search.value = state.q;
    } else {
      state.slug = "scalability-architecture-patterns";
      state.q = "";
      search.value = "";
    }
    render();
  }

  search.addEventListener("input", function () {
    const q = search.value.trim();
    clearTimeout(search._t);
    search._t = setTimeout(function () {
      if (q.length >= 2) {
        state.q = q;
        state.searching = true;
        state.page = 0;
        history.replaceState(null, "", "#/search/" + encodeURIComponent(q));
        render();
      } else if (!q && state.searching) {
        location.hash = "#/topic/" + state.slug;
      }
    }, 180);
  });
  search.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && search.value.trim().length >= 2) {
      location.hash = "#/search/" + encodeURIComponent(search.value.trim());
    }
  });

  document.addEventListener("keydown", function (e) {
    const tag = (e.target.tagName || "").toLowerCase();
    const typing = tag === "input" || tag === "select" || tag === "textarea";
    if (e.key === "/" && !typing) { e.preventDefault(); search.focus(); search.select(); }
    if (e.key === "Escape" && tag === "input") {
      search.value = "";
      if (state.searching) location.hash = "#/topic/" + state.slug;
      search.blur();
    }
  });

  yearSel.addEventListener("change", function () { state.year = yearSel.value; state.page = 0; render(); });
  sortSel.addEventListener("change", function () { state.sort = sortSel.value; state.page = 0; render(); });
  prevBtn.addEventListener("click", function () { if (state.page > 0) { state.page -= 1; render(); window.scrollTo({ top: 0, behavior: "smooth" }); } });
  nextBtn.addEventListener("click", function () { state.page += 1; render(); window.scrollTo({ top: 0, behavior: "smooth" }); });
  el("reset").addEventListener("click", function () {
    state.year = ""; state.q = ""; state.page = 0; search.value = "";
    if (state.searching) location.hash = "#/topic/" + state.slug; else render();
  });
  window.addEventListener("hashchange", route);

  volCounts.textContent = "Vol. 2007–2024 · " + D.articles.length.toLocaleString("en-US") +
    " entries · " + D.topics.length + " sections";
  search.placeholder = "Search " + D.articles.length.toLocaleString("en-US") + " articles…";
  route();
})();
