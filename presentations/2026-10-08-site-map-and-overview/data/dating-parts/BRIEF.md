# Brief for site-dating subagents

Repository: C:\Users\sandh\OneDrive\Projects\indus_valley_script (private research knowledge base).
Read AGENTS.md and knowledge/editorial/WRITING.md first. Do NOT edit or create any file inside the repository and do not commit. Write ONLY your assigned output file in this scratch directory.

Writing requirement (project rule): maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Notes fields should be short, concrete, plain.

## Task
For each assigned site (names must match the census `canonical_name` exactly), find sourced chronology of the site's occupation phases relevant to the Indus tradition, any dating of the inscribed objects specifically, the year the first inscribed object from the site was found or published (if a source states it), and coordinates where the census has none.

Census rows (read the row for your sites first; they already contain phase statements, source ids and coordinates):
- batch A: experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/site-rows.json (dict, key 'sites'); sources in sources.json there.
- batch B: experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/site-rows.json (list); sources.json there (list).
- batch C: experiments/2026-10-06-evidence-census/sites-deep/c-north-india/site-rows.json (dict, key 'rows'); sources.json there (key 'sources').
Each batch folder also has notes/REPORT files.

Local source text already in the repository (local-only raw material; you may read it):
- CISI 2 (Shah & Parpola 1991, Corpus of Indus Seals and Inscriptions 2, Collections in Pakistan): data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pages.json (list of {pdf_page,text}; introduction pp. XIV–XIX = list indices 16–21 has a site-by-site catalogue with period labels; p. XXVIII = index 30 defines Early Harappan c. 3000–2500 B.C., Mature c. 2500–2000 B.C.).
- CISI 1 (Joshi & Parpola 1987, Collections in India): data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/CISI1OCR.txt and CISI1.pages.json (introduction has a site catalogue for Indian sites).
- Uesugi 2010 Pakistan chapter (Japanese gazetteer with site periods, sometimes dates; 前 2600 年 = 2600 BCE): data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/afghan-minor-revision/gazetteer4.txt ; Afghanistan chapter gazetteer-afghanistan.pages.json in the same folder.
- Uesugi 2018 "Current state of research and issues of Indus Archaeology" (source id GAZETTEER2018): data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/GAZETTEER2018.pages.json.
- Kenoyer 2020 "Origin and Development of the Indus Script" Table 1 (research/literature/sources/kenoyer2020_origin.txt): includes Nausharo Period IV 2100–2000 BCE, Mehrgarh Period VIII 2000–1700 BCE.
- Other raw files under data/raw/2026-10-06-evidence-census/sites-deep/<batch>/ (excavation reports, IAR pages, Dholavira 2015 report text, Frontiers 2025, etc.) and research/literature/sources/ (e.g. mackay_1943_chandaro.txt, marshall_1931_govscan_14985.txt, vats_1940...). Search them with grep.

Then use WebSearch/WebFetch for site-specific excavation reports, radiocarbon studies (e.g. Possehl's radiocarbon lists, Indian Archaeology – A Review, Puratattva, Man and Environment, Radiocarbon journal, Quaternary Geochronology, Antiquity, Asian Perspectives, harappa.com, ASI pages, Pleiades, peer-reviewed site papers). Prefer sources already in the repository and cite them with their source ids. Do not enter credentials, accept terms, or download executables. Spend effort proportional to site importance: the major sites first, then every remaining site. Do not skip any assigned site; use 'not found' where needed.

## Regional convention (used by the coordinator)
Where no site-specific dates exist but a source establishes that the site has a phase, the coordinator applies this convention; you should still record the phase with its convention dates and mark it as convention:
- Early Harappan / Regionalization (Kot Diji-type Pre-Urban): 3000–2600 BCE — Uesugi 2018, GAZETTEER2018, printed p. 12, Figure 8 caption "Pre-Urban Indus period (c. 3000 - 2600 BCE)".
- Mature Harappan / Integration: 2600–1900 BCE — Kenoyer 2020, Table 1, printed p. 219 ("Harappan Phase 2600 to 1900 BCE").
- Late Harappan / Localization: 1900–1300 BCE — Kenoyer 2020, Table 1, printed p. 219 ("Late Harappan Phase ca. 1900 to 1300 BCE").
Use basis 'typological/conventional' and approx true for such entries, plus a `phase_attribution_source` field citing the source that says the site has that phase.

## Output
Write a JSON list to your assigned output path. One object per site:
{
 "name": "<census canonical_name>",
 "country": "...",
 "census_batch": "A"|"B"|"C",
 "phases": [ {"label": "...", "start_bce": int, "end_bce": int, "approx": bool,
              "basis": "radiocarbon"|"typological/conventional"|"report-stated",
              "source": {"source_id": "<repo source id or null>", "author": "...", "year": int|null, "title": "<exact title>", "locator": "page/table/figure", "url": "..."},
              "quote_or_locator": "<quote under 15 words, or a locator>",
              "phase_attribution_source": {...same source shape...}   // only for convention entries
            } ],
 "inscribed_dating": null | [ same shape as phases, describing the dated inscribed objects (e.g. 'seals from Period 3A–3C') ],
 "first_inscribed_find": null | {"year": int, "event": "found"|"published", "description": "...", "source": {...}, "quote_or_locator": "..."},
 "coordinates_if_missing": null | {"lat": float, "lon": float, "source": {...}, "precision_note": "...", "gazetteer_type": "excavation report|published gazetteer|Pleiades|Wikidata/Wikipedia (last resort)"},
 "confidence": "site-specific source"|"regional convention applied"|"not found",
 "notes": "<one or two plain sentences: what was searched, conflicts, what is missing>"
}
Rules: start_bce >= end_bce (BCE counts down; use negative numbers for CE). 'basis':'radiocarbon' only when the source ties the range to 14C dates; 'report-stated' when an excavation report states calendar dates without showing 14C; 'typological/conventional' for convention or ceramic-typological ranges. Keep every quote under 15 words. Never invent page numbers; if you only saw a search snippet, say so in the locator. confidence = 'site-specific source' if at least one phase has a site-specific date from a source; 'regional convention applied' if all dates come from the convention; 'not found' if no phase can be attributed. coordinates_if_missing only for sites where the census coordinate is null, unresolved, partial, a bounding box, or malformed; otherwise null. Label Wikipedia/Wikidata coordinates as last resort.

When finished, reply with: output path, a compact table (name | phases | confidence), sources you added that are not in the repository, and any sites you could not resolve.
