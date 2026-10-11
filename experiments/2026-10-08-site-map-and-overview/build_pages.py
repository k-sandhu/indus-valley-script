"""Build the find-site map and the findings slide deck.

Inputs (all in this directory unless noted):
  data/sites-census.json        site table copied from the evidence census (build_site_table.py)
  data/dating-south-asia.json   sourced phase dates for South Asian sites
  data/abroad-sites.json        sourced locations and dates for finds outside South Asia
  ../2026-10-06-evidence-census/sites-deep/*/  census source lists, used to turn source ids into citations
  site_map_template.html        map page with a /*__DATA__*/ placeholder
  slides_shell.html, slides/*.html

Outputs:
  data/map-data.json            the merged records the map displays
  site-map.html                 self-contained map page (loads Leaflet and map tiles from the web)
  indus-research-overview.html  slide deck

Run: python build_pages.py
"""
import base64
import glob
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CENSUS = HERE.parent / "2026-10-06-evidence-census" / "sites-deep"
BATCH_DIRS = {"A": "a-pakistan-afghanistan", "B": "b-gujarat-kutch-maharashtra", "C": "c-north-india", "D": "d-finds-abroad"}


def load(name):
    p = DATA / name
    if not p.exists():
        print(f"note: {name} not found; continuing without it")
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def num(v):
    try:
        return None if v is None else int(round(float(v)))
    except (TypeError, ValueError):
        return None


# ---------- citations ----------

def source_index():
    """Map census source ids to bibliographic records, per batch with a global fallback."""
    per_batch, merged = {}, {}
    for b, d in BATCH_DIRS.items():
        idx = {}
        for f in sorted(glob.glob(str(CENSUS / d / "**" / "*sources*.json"), recursive=True)):
            try:
                data = json.loads(Path(f).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            items = data if isinstance(data, list) else data.get("sources", []) if isinstance(data, dict) else []
            if isinstance(items, dict):
                items = list(items.values())
            for it in items:
                if isinstance(it, dict) and it.get("id") and (it.get("title") or it.get("authors")):
                    idx.setdefault(it["id"], it)
        per_batch[b] = idx
        for k, v in idx.items():
            merged.setdefault(k, v)
    return per_batch, merged


SRC_BATCH, SRC_ALL = source_index()
NOISE = re.compile(r"snippet|access|failed|search|witness|query|queries|local|census|coordinator|reused|ocr|extraction|field\b|aggregate|row\b", re.I)
PAGEISH = re.compile(r"\b(pp?\.|pages?|table|fig\.?|figure|pl\.|plate|no\.|nos\.|chapter|§)\s*[\divxlc]", re.I)


def clean_loc(loc):
    """Keep short page, table or figure references; drop process notes."""
    if not loc:
        return ""
    loc = re.sub(r"/?\s*PDF\s*p?\.?\s*\d+", "", str(loc))
    loc = re.sub(r"\[census id[^\]]*\]", "", loc)
    parts = [p.strip(" ,;") for p in re.split(r";", loc)]
    keep = [p for p in parts if p and PAGEISH.search(p) and not NOISE.search(p) and len(p) <= 60]
    return "; ".join(keep[:2])


def fmt_authors(a):
    if not a:
        return ""
    if isinstance(a, list):
        a = [str(x) for x in a if x]
        if len(a) > 2:
            return f"{a[0]} et al."
        return " and ".join(a)
    return str(a)


def cite_record(r):
    au = fmt_authors(r.get("authors") or r.get("author"))
    yr = r.get("year")
    title = (r.get("title") or "").strip()
    head = " ".join(x for x in (au, f"{yr}" if yr else "") if x)
    return ". ".join(x for x in (head, title) if x)


def cite_ids(ids, locator="", batch=None):
    if not ids:
        return ""
    out = []
    for part in re.split(r"\s*[;,]\s*", str(ids)):
        part = part.strip()
        if not part:
            continue
        rec = (SRC_BATCH.get(batch) or {}).get(part) or SRC_ALL.get(part)
        if rec:
            c = cite_record(rec)
            if c and c not in out:
                out.append(c)
    loc = clean_loc(locator)
    text = "; ".join(out)
    return f"{text}, {loc}" if text and loc else text


def cite_obj(x):
    """Format a source given as a dict, list or string by the dating and abroad research."""
    if not x:
        return ""
    if isinstance(x, list):
        return "; ".join(filter(None, (cite_obj(i) for i in x)))
    if isinstance(x, dict):
        c = cite_record(x)
        loc = clean_loc(x.get("locator") or x.get("page") or "")
        if not c and x.get("source_id"):
            return cite_ids(x["source_id"], loc)
        return f"{c}, {loc}" if loc else c
    s = str(x)
    s = re.sub(r"\s*\[census id[^\]]*\]", "", s)
    s = re.sub(r"\s*\(accessed [^)]*\)", "", s)
    s = re.sub(r"\s*\(text read from[^)]*\)", "", s)
    s = re.sub(r";?\s*local (text|file)[^;]*", "", s)
    s = re.sub(r"research/[^\s;,]+|data/raw/[^\s;,]+", "", s)
    return s.strip(" ;,")


# ---------- phases ----------

PROCESS_NOTE = re.compile(r"snippet|fetch|failed|witness|search", re.I)


def note(t):
    """Drop notes about how a source was retrieved; keep notes about the place or the point."""
    return "" if not t or PROCESS_NOTE.search(t) else t


def phase_rec(p):
    s, e = num(p.get("start_bce")), num(p.get("end_bce"))
    if s is None or e is None:
        return None
    if s < e:
        s, e = e, s
    basis = p.get("basis") or ""
    text = " ".join(str(p.get(k) or "") for k in ("label", "quote_or_locator", "confidence")).lower()
    convention = "convention" in text or bool(p.get("phase_attribution_source")) or basis == "conventional"
    return {
        "label": p.get("label") or "phase",
        "start_bce": s,
        "end_bce": e,
        "approx": bool(p.get("approx", True)),
        "basis": basis.replace("typological/conventional", "typological"),
        "source": cite_obj(p.get("source")),
        "convention": convention,
    }


CLASS_NAMES = {"SEAL": "seals", "TAB": "tablets", "POT": "pottery", "POsT": "pottery", "TAG": "tags and sealings", "BNGL": "bangles",
               "ROD": "rods", "IMPL": "tools", "BEAD": "beads", "MDLN": "medallions", "MISC": "other"}


def readable_classes(d):
    if not d:
        return None
    out = {}
    for k, v in d.items():
        name = CLASS_NAMES.get(k, CLASS_NAMES.get(k.split(":")[0], k.lower()))
        out[name] = out.get(name, 0) + v
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def fieldwork_list(events, batch):
    out, seen = [], set()
    for f in events:
        a, z = f.get("start_year"), f.get("end_year")
        years = (f"{a}–{z}" if z and z != a else f"{a}") if a else (f.get("years") or "")
        row = {"years": years, "label": f.get("label"), "source": cite_ids(f.get("source_id"), f.get("locator"), f.get("batch") or batch)}
        k = (row["years"], row["label"], row["source"])
        if k not in seen:
            seen.add(k)
            out.append(row)
    return out


def main():
    census = load("sites-census.json")
    if census is None:
        sys.exit("data/sites-census.json is required")
    sa = load("dating-south-asia.json") or {"sites": []}
    ab = load("abroad-sites.json") or {"sites": []}
    sa_by = {key(r.get("name")): r for r in sa.get("sites", [])}
    ab_by = {key(r.get("name") or r.get("site")): r for r in ab.get("sites", [])}

    out, used_sa, used_ab = [], set(), set()
    for s in census["sites"]:
        b = s.get("batch")
        names = [s["name"]] + list(s.get("alternative_spellings") or [])
        dsa = next((sa_by[key(n)] for n in names if key(n) in sa_by), None)
        dab = next((ab_by[key(n)] for n in names if key(n) in ab_by), None)
        if dsa:
            used_sa.add(key(dsa.get("name")))
        if dab:
            used_ab.add(key(dab.get("name") or dab.get("site")))

        c = s.get("counts") or {}
        ll = c.get("local_lipi") or {}
        reported = []
        for r in (c.get("icit") or []):
            reported.append({"text": f"ICIT-based count {r.get('count_date') or ''}: {r.get('value')} {r.get('unit') or ''}".strip(), "source": cite_ids(r.get("source_id"), r.get("locator"), r.get("batch") or b)})
        for r in (c.get("other_reported") or []):
            reported.append({"text": f"{r.get('object_class')}: {r.get('value')}{(' ' + r['unit']) if r.get('unit') else ''}{(' (' + str(r['count_date']) + ')') if r.get('count_date') else ''}", "source": cite_ids(r.get("source_id"), r.get("locator"), r.get("batch") or b)})
        cisi = "; ".join(f"{r.get('volume')} {r.get('range')}" for r in (c.get("cisi") or []) if r.get("range"))
        m77 = (c.get("m77") or [{}])[0].get("value") if c.get("m77") else None
        size_n = max(v for v in (ll.get("faces") or 0, m77 or 0, c.get("published_indus_related_minimum_objects") or 0) if isinstance(v, (int, float)))

        events = s.get("fieldwork") or []
        found = s.get("first_fieldwork_year")
        first_ev = next((f for f in events if f.get("start_year") == found and f.get("counts_for_first_year", True)), None)
        if s.get("first_fieldwork_upper_bound"):
            found_basis = "earliest published report; fieldwork no later than this"
        else:
            found_basis = (first_ev or {}).get("label") or ""

        status = s.get("coord_status") or ""
        rec = {
            "id": s["id"],
            "name": s["name"],
            "alts": s.get("alternative_spellings") or [],
            "batch": b or "X",
            "region": s.get("region"),
            "country": s.get("country"),
            "province": s.get("province"),
            "lat": s.get("lat"),
            "lon": s.get("lon"),
            "coord_kind": "site coordinate" if status == "census-verified" else "approximate coordinate" if status == "census-partial" else "",
            "coord_source": cite_ids(s.get("coord_source_id"), s.get("coord_locator"), b),
            "coord_note": note(s.get("coord_note")),
            "found_year": found,
            "found_basis": found_basis,
            "fieldwork": fieldwork_list(events, b),
            "counts": {
                "lipi_faces": ll.get("faces"),
                "families": ll.get("object_families"),
                "classes": readable_classes(ll.get("object_classes")),
                "im77": m77,
                "cisi": cisi,
                "reported": reported,
            },
            "size_n": size_n,
            "dating_notes": [{"text": n.get("text"), "source": cite_ids(n.get("source_id"), n.get("locator"), n.get("batch") or b)} for n in (s.get("dating_notes") or [])],
            "phases": [],
            "inscribed_dating": [],
        }

        if dsa:
            raw = dsa.get("phases") or []
            uncal = [p for p in raw if any(w in (str(p.get("label")) + str(p.get("quote_or_locator"))).lower() for w in ("uncorrected", "uncalibrated"))]
            rec["phases"] = [x for x in (phase_rec(p) for p in raw if p not in uncal) if x]
            for p in uncal:
                rec["dating_notes"].append({"text": f"{p.get('label')}: {p.get('start_bce')}–{p.get('end_bce')} BCE in uncalibrated radiocarbon years (not drawn on the time axis)", "source": cite_obj(p.get("source"))})
            ins = dsa.get("inscribed_dating")
            ins = ins if isinstance(ins, list) else [ins] if isinstance(ins, dict) else []
            rec["inscribed_dating"] = [x for x in (phase_rec(p) for p in ins) if x]
            fif = dsa.get("first_inscribed_find")
            if isinstance(fif, dict) and fif.get("year"):
                rec["first_inscribed_find"] = {"year": fif.get("year"), "source": cite_obj(fif.get("source"))}
            cm = dsa.get("coordinates_if_missing")
            if rec["lat"] is None and isinstance(cm, dict) and cm.get("lat") is not None:
                rec["lat"], rec["lon"] = float(cm["lat"]), float(cm["lon"])
                rec["coord_kind"] = "gazetteer coordinate"
                rec["coord_source"] = cite_obj(cm.get("source"))
                rec["coord_note"] = note(cm.get("precision") or cm.get("precision_note"))

        if dab:
            if rec["lat"] is None and dab.get("lat") is not None:
                rec["lat"], rec["lon"] = float(dab["lat"]), float(dab["lon"])
                rec["coord_kind"] = "gazetteer coordinate"
                rec["coord_source"] = cite_obj(dab.get("coord_source"))
                rec["coord_note"] = note(dab.get("precision_note"))
            rec["finds_summary"] = cite_obj(dab.get("finds_summary"))
            if not rec["phases"]:
                rec["phases"] = [x for x in (phase_rec(p) for p in (dab.get("dating") or [])) if x]
            evs = dab.get("find_events") or []
            for e in evs:
                rec["fieldwork"].append({"years": "–".join(str(v) for v in (e.get("year_start"), e.get("year_end")) if v), "label": e.get("label"), "source": cite_obj(e.get("source"))})
            if rec["found_year"] is None:
                ys = [num(e.get("year_start")) for e in evs if num(e.get("year_start"))]
                if ys:
                    rec["found_year"] = min(ys)
                    rec["found_basis"] = "earliest recorded find"

        out.append(rec)

    located = [r for r in out if r["lat"] is not None]
    summary = {
        "sites": len(out),
        "located": len(located),
        "located_site_coordinate": sum(1 for r in located if r["coord_kind"] == "site coordinate"),
        "located_approximate": sum(1 for r in located if r["coord_kind"] == "approximate coordinate"),
        "located_gazetteer": sum(1 for r in located if r["coord_kind"] == "gazetteer coordinate"),
        "with_found_year": sum(1 for r in out if r["found_year"] is not None),
        "with_phases": sum(1 for r in out if r["phases"]),
        "with_site_specific_phases": sum(1 for r in out if any(not p["convention"] for p in r["phases"])),
        "earliest_found_year": min((r["found_year"] for r in out if r["found_year"]), default=None),
        "unmatched_dating_rows": sorted(set(sa_by) - used_sa),
        "unmatched_abroad_rows": sorted(set(ab_by) - used_ab),
    }

    notes_html = (
        "<h2>About the data</h2>"
        "<p>The map covers every place recorded in a site-by-site census of Indus inscribed objects in four regions: Pakistan and Afghanistan; "
        "Gujarat, Kutch and Maharashtra; north India; and finds outside South Asia. Coordinates come from published site gazetteers and excavation "
        "reports. A <i>site coordinate</i> is a published point for the site itself; an <i>approximate coordinate</i> stands for a nearby locality, "
        "an island or a site complex; a <i>gazetteer coordinate</i> comes from a general gazetteer such as Pleiades.</p>"
        "<p><b>First investigated</b> is the earliest recorded fieldwork at the place: discovery, survey or excavation. It is not always the year "
        "the first inscribed object was recovered; where a source gives that year, it appears separately in the site details.</p>"
        "<p><b>Age of layers</b> uses the dated phases of each site's Indus-period occupation, from site reports and dating studies. No individual "
        "inscribed object in the corpus carries a calendar date, so the dates describe the layers and periods the objects belong to. Where a source "
        "places a site in the Early, Mature or Late Harappan phase without site-specific dates, the regional phase ranges (about 3200–2600, "
        "2600–1900 and 1900–1300 BCE) are applied and the site is drawn pale or dashed. Uncalibrated radiocarbon ranges are listed in the site "
        "details and left off the time axis.</p>"
        "<p>Circle size follows the number of inscribed faces in the main machine-readable corpus, or the largest published count for places "
        "absent from it. Counts from different catalogues are shown side by side; they count different things and are not reconciled.</p>"
    )

    payload = {"summary": summary, "notes_html": notes_html, "sites": out}
    (DATA / "map-data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    tpl = (HERE / "site_map_template.html").read_text(encoding="utf-8")
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    (HERE / "site-map.html").write_text(tpl.replace("/*__DATA__*/null", blob), encoding="utf-8")

    shell = (HERE / "slides_shell.html").read_text(encoding="utf-8")
    parts = "\n".join(p.read_text(encoding="utf-8") for p in sorted((HERE / "slides").glob("*.html")))

    def inline_asset(m):
        f = HERE / "assets" / m.group(1)
        return 'src="data:image/png;base64,' + base64.b64encode(f.read_bytes()).decode() + '"'

    parts = re.sub(r'src="asset:([\w.-]+)"', inline_asset, parts)
    deck_sites = [[r["name"], round(r["lat"], 4), round(r["lon"], 4), r["batch"], r["size_n"]] for r in out if r["lat"] is not None]
    sites_js = json.dumps(deck_sites, ensure_ascii=False).replace("</", "<\\/")
    deck = shell.replace("<!--SLIDES-->", parts).replace("/*__SITES__*/[]", sites_js)
    (HERE / "indus-research-overview.html").write_text(deck, encoding="utf-8")

    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
