"""Record British Museum Indus records from saved witnesses.

On 13 October 2026 a scripted request to the British Museum collection search returned a
Cloudflare challenge (HTTP 403), as the census's requests did on 7 October. No attempt was
made to get round the challenge. This script therefore reads:
  * the search page saved by the data inventory on 12 October
    (data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html,
    keyword 'indus seal', 59 results), for museum number, object type, culture, date and findspot;
  * the object page for 1947,0416.7 saved by the same package;
  * the census's search-provider observations for six records
    (data/raw/2026-10-06-evidence-census/.../bm-record-observations.json);
  * search-engine results read on 13 October (recorded in BM_WEB_OBSERVATIONS below).
British Museum record text is not under an open licence (CC BY-NC-SA 4.0 applies only to
content marked with the CC logo), so the tracked file keeps identifiers, URLs, the
museum's 'Miscellaneous number' keys (field numbers used for joins), field-presence flags
and our classification; values stay local.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_bm.py
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, ROOT, sha256_file, write_json  # noqa: E402

SEARCH_WITNESS = ROOT / "data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html"
OBJECT_WITNESS = ROOT / "data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-object-A_1947-0416-7.html"
CENSUS_OBS = ROOT / ("data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/"
                     "bm-record-observations.json")
# Search-engine result text read on 2026-10-13 (WebSearch tool); used only for Miscellaneous numbers.
BM_WEB_OBSERVATIONS = {
    "1947,0416.7": {"misc_number": "DK 8528", "source": "saved object page 2026-10-12 and search result 2026-10-13"},
    "1947,0416.4": {"misc_number": "Hr 5635", "source": "census observation and search result 2026-10-13"},
}


def parse_search(path):
    s = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    lines = s.get_text("\n", strip=True).split("\n")
    start = lines.index("Results")
    recs, cur = [], None
    i = start + 1
    while i < len(lines):
        ln = lines[i]
        if ln == "Museum number":
            if cur:
                recs.append(cur)
            # object type label(s) precede 'Museum number'
            j = i - 1
            types = []
            while j > start and lines[j] not in ("|",) and not lines[j].startswith(("Found/Acquired", "Excavated", "Made in")) \
                    and not re.match(r"^\S+$", lines[j]) is None and len(types) < 4:
                if lines[j] == ";":
                    j -= 1
                    continue
                types.insert(0, lines[j])
                j -= 1
                if j > start and lines[j] != ";":
                    break
            cur = {"accession": lines[i + 1], "object_type_label": "; ".join(types)}
            i += 2
            continue
        if cur is not None:
            if ln == "Cultures/periods" and i + 2 < len(lines):
                cur.setdefault("culture", lines[i + 2])
            elif ln == "Production date" and i + 1 < len(lines):
                cur.setdefault("date", lines[i + 1])
            elif ln.startswith(("Found/Acquired", "Excavated/Findspot")) and i + 1 < len(lines):
                cur.setdefault("findspot", lines[i + 1])
            elif ln == "Made in:" and i + 1 < len(lines):
                cur.setdefault("made_in", []).append(lines[i + 1])
        if ln in ("Show", "Previous", "Next") and cur and len(recs) > 50:
            break
        i += 1
    if cur:
        recs.append(cur)
    return recs


def page_misc(path):
    lines = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml").get_text("\n", strip=True).split("\n")
    out = {}
    for k in ("Museum number", "Description", "Materials", "Miscellaneous number:"):
        if k in lines:
            out[k] = lines[lines.index(k) + 1]
    return out


def main():
    import json
    recs = parse_search(SEARCH_WITNESS)
    census = {r["accession"]: r for r in json.loads(CENSUS_OBS.read_text(encoding="utf-8"))}
    page7 = page_misc(OBJECT_WITNESS)
    out = []
    for r in recs:
        acc = r["accession"]
        label = r.get("object_type_label", "").lower()
        culture = r.get("culture", "")
        findspot = r.get("findspot", "")
        indus = "Indus Valley Civilisation" in culture
        cast = "cast" in label
        in_scope = indus and bool(re.search(r"seal|sealing|tablet|impression", label))
        misc = ""
        if acc in census and census[acc].get("excavation_raw"):
            misc = census[acc]["excavation_raw"]
        if acc in BM_WEB_OBSERVATIONS:
            misc = BM_WEB_OBSERVATIONS[acc]["misc_number"]
        if acc == page7.get("Museum number"):
            misc = page7.get("Miscellaneous number:", misc)
        url = "https://www.britishmuseum.org/collection/object/" + ("A_" if "," in acc else "W_") + \
              acc.replace(",", "-").replace(".", "-")
        out.append({
            "museum": "British Museum", "accession": acc, "url": url,
            "object_type_label": r.get("object_type_label", ""), "culture_label": culture, "findspot_label": findspot,
            "date_label": r.get("date", ""),
            "indus_attributed": indus, "object_class": "seal" if "seal" in label else "other",
            "originality": "cast-or-replica" if cast else "original", "in_scope": in_scope and not cast,
            "cast_in_scope": in_scope and cast,
            "misc_number": misc,
            "census_record": acc in census,
            "fields_present_census": sorted(k for k in ("material", "dimensions", "bibliography", "description")
                                            if census.get(acc, {}).get(k)),
            "witness": str(SEARCH_WITNESS.relative_to(ROOT)).replace("\\", "/"),
        })
    write_json(RAW / "bm" / "records-extracted.json", out)
    keep = ("museum", "accession", "url", "indus_attributed", "object_class", "originality", "in_scope", "cast_in_scope",
            "misc_number", "census_record", "fields_present_census", "witness")
    write_json(PKG / "harvest" / "bm-records.json", {
        "witness_sha256": sha256_file(SEARCH_WITNESS),
        "note": ("Identifiers, the Miscellaneous (field) numbers used as join keys, field-presence flags and our "
                 "classification; British Museum labels and text stay in the local extraction."),
        "records": [{k: r[k] for k in keep} for r in out],
    })
    for r in out:
        print(r["accession"], "|", r["object_type_label"], "|", r["culture_label"], "|", r["findspot_label"], "|", r["date_label"],
              "| IN" if r["in_scope"] else ("| cast" if r["cast_in_scope"] else "| out"), "|", r["misc_number"])
    print(len(out), "records;", sum(r["in_scope"] for r in out), "in-scope originals;", sum(r["cast_in_scope"] for r in out), "casts")


if __name__ == "__main__":
    main()
