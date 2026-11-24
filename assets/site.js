"use strict";

// Unhide JS-dependent controls only when JavaScript runs.
document.querySelectorAll(".js-only").forEach(el => { el.hidden = false; });

// 1. Navigation dropdown ergonomics (native <details> still works without JS).
const navMenus = [...document.querySelectorAll(".nav-menu")];
navMenus.forEach(menu => {
  const summary = menu.querySelector("summary");
  if (summary) summary.setAttribute("aria-expanded", String(menu.open));
  menu.addEventListener("toggle", () => {
    if (summary) summary.setAttribute("aria-expanded", String(menu.open));
    if (menu.open) {
      navMenus.forEach(other => {
        if (other !== menu) other.open = false;
      });
    }
  });
});
document.addEventListener("click", event => {
  navMenus.forEach(menu => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape") {
    navMenus.forEach(menu => { menu.open = false; });
  }
  if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey) {
    const tag = (document.activeElement?.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") return;
    const localSearch = document.querySelector('input[type="search"]');
    if (localSearch) {
      event.preventDefault();
      localSearch.focus();
      return;
    }
    const searchLink = document.querySelector(".header-actions .icon-link");
    if (searchLink) {
      event.preventDefault();
      window.location.href = searchLink.href;
    }
  }
});

// 2. Copy-to-clipboard buttons for agent prompts and share links.
function copyText(text, button, doneLabel) {
  const original = button.textContent;
  const finish = () => {
    button.textContent = doneLabel;
    setTimeout(() => { button.textContent = original; }, 1800);
  };
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).then(finish).catch(() => {});
  } else {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); finish(); } catch {}
    ta.remove();
  }
}

document.querySelectorAll(".copy-btn[data-copy-target]").forEach(button => {
  button.addEventListener("click", () => {
    const el = document.getElementById(button.dataset.copyTarget);
    if (el) copyText(el.textContent.trim(), button, "Copied!");
  });
});

document.querySelectorAll(".share-btn[data-share-url]").forEach(button => {
  button.addEventListener("click", () => {
    copyText(button.dataset.shareUrl, button, "Link copied!");
  });
});

// 3. Listing search, dropdowns, preset chips, and URL query persistence.
document.querySelectorAll(".listing").forEach(async listing => {
  const form = listing.querySelector("form");
  const elements = [...listing.querySelectorAll("[data-id]")];
  const count = listing.querySelector(".filter-count");
  const chips = [...listing.querySelectorAll(".quick-chips .chip")];
  let rows;
  try {
    const response = await fetch(listing.dataset.index);
    if (!response.ok) return;
    rows = new Map((await response.json()).map(row => [String(row.id), row]));
  } catch {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  let hasParam = false;
  for (const [k, v] of params.entries()) {
    const field = form.elements.namedItem(k);
    if (field) {
      field.value = v;
      hasParam = true;
    }
  }

  function syncChips(values) {
    chips.forEach(chip => {
      const preset = chip.dataset.preset;
      let active = false;
      if (preset === "all") {
        let anySet = false;
        for (const [, v] of values) { if (v) anySet = true; }
        active = !anySet;
      } else {
        try {
          const spec = JSON.parse(preset);
          const keys = Object.keys(spec);
          active = keys.every(k => String(values.get(k) || "") === String(spec[k]));
          for (const [k, v] of values) {
            if (v && !(k in spec)) active = false;
          }
        } catch {
          active = false;
        }
      }
      chip.classList.toggle("active", active);
      chip.setAttribute("aria-pressed", String(active));
    });
  }

  function update(pushUrl = false) {
    const values = new FormData(form);
    const query = String(values.get("search") || "").trim().toLocaleLowerCase();
    let shown = 0;
    elements.forEach(element => {
      const row = rows.get(element.dataset.id);
      let matches = !!row && (!query || JSON.stringify(row).toLocaleLowerCase().includes(query));
      for (const [field, value] of values) {
        if (field !== "search" && value && String(row?.[field] ?? "") !== value) matches = false;
      }
      element.hidden = !matches;
      if (matches) shown += 1;
    });
    listing.querySelectorAll("[data-group]").forEach(group => {
      group.hidden = ![...group.querySelectorAll("[data-id]")].some(element => !element.hidden);
    });
    count.textContent = `${shown} of ${elements.length} shown`;
    syncChips(values);
    if (pushUrl && window.history?.replaceState) {
      const next = new URLSearchParams();
      for (const [field, value] of values) {
        if (value) next.set(field, String(value));
      }
      const qs = next.toString();
      window.history.replaceState(null, "", qs ? `?${qs}` : window.location.pathname + window.location.hash);
    }
  }

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      form.reset();
      const preset = chip.dataset.preset;
      if (preset && preset !== "all") {
        try {
          const spec = JSON.parse(preset);
          for (const [k, v] of Object.entries(spec)) {
            const field = form.elements.namedItem(k);
            if (field) field.value = v;
          }
        } catch {}
      }
      update(true);
    });
  });

  form.addEventListener("submit", event => event.preventDefault());
  form.addEventListener("input", () => update(true));
  form.addEventListener("change", () => update(true));
  form.addEventListener("reset", () => setTimeout(() => update(true), 0));
  if (hasParam) update(false);
});

// 4. Site-wide search page.
document.querySelectorAll(".site-search").forEach(async box => {
  const form = box.querySelector("form");
  const list = box.querySelector(".search-results");
  const count = box.querySelector(".filter-count");
  let entries = [];
  try {
    const response = await fetch(box.dataset.index);
    if (!response.ok) return;
    entries = await response.json();
  } catch {
    return;
  }

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const params = new URLSearchParams(window.location.search);
  if (params.get("q")) form.elements.q.value = params.get("q");
  if (params.get("kind")) form.elements.kind.value = params.get("kind");

  function render() {
    const q = (form.elements.q.value || "").trim().toLocaleLowerCase();
    const kind = form.elements.kind.value || "";
    const terms = q ? q.split(/\s+/).filter(Boolean) : [];
    const matched = entries.filter(item => {
      if (kind && item.kind !== kind) return false;
      if (!terms.length) return true;
      const hay = `${item.id} ${item.title} ${item.summary} ${item.meta} ${item.kind}`.toLocaleLowerCase();
      return terms.every(t => hay.includes(t));
    });
    const shown = matched.slice(0, 80);
    count.textContent = matched.length === 0
      ? "No matching records found."
      : `Showing ${shown.length} of ${matched.length} matching records`;
    list.innerHTML = shown.map(item => (
      `<li>` +
      `<div class="search-meta"><span class="kind-pill">${esc(item.kind)}</span><code>${esc(item.id)}</code><span>${esc(item.meta)}</span></div>` +
      `<h2><a href="../${esc(item.path || item.url)}">${esc(item.title)}</a></h2>` +
      `<p>${esc(item.summary)}</p>` +
      `</li>`
    )).join("");
  }

  form.addEventListener("submit", event => event.preventDefault());
  form.addEventListener("input", render);
  form.addEventListener("change", render);
  form.addEventListener("reset", () => setTimeout(render, 0));
  render();
});
