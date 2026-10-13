"use strict";
document.querySelectorAll(".listing").forEach(async listing => {
  const form = listing.querySelector("form");
  const elements = [...listing.querySelectorAll("[data-id]")];
  const count = listing.querySelector(".filter-count");
  let rows;
  try {
    const response = await fetch(listing.dataset.index);
    if (!response.ok) return;
    rows = new Map((await response.json()).map(row => [String(row.id), row]));
  } catch {
    // Local file previews and no-script use retain the complete server-rendered list.
    return;
  }
  function update() {
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
    count.textContent = `${shown} of ${elements.length} shown`;
  }
  form.addEventListener("submit", event => event.preventDefault());
  form.addEventListener("input", update);
  form.addEventListener("change", update);
  form.addEventListener("reset", () => setTimeout(update, 0));
});
