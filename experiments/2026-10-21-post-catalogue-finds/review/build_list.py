"""Apply the coordinator's join decisions and write the final list and per-site counts.

Inputs: matching/objects-merged.csv (run 3), review/dholavira-decisions.csv and
review/dholavira-added-rows.csv (match_dholavira.py), review/coordinator-decisions.csv, and
run 2D's identity tables for the added Dholavira rows. Outputs, in the package directory:
objects.csv, join-decisions.csv and sites.csv.

Counting rules (PROTOCOL.md, "Matching to the local corpus"; AMENDMENT-1.md):
- The main count is rows with catalogue_status post-catalogue and inscription_status stated.
- A row with possible_duplicate_of may be the same object as the row it names.
- absent_upper: main rows not matched.
- absent_lower: main absent rows that are not possible duplicates, plus the main candidate
  rows that are not possible duplicates in excess of the distinct local families named in
  their candidate sets and matched to no row.
- Rows whose candidates are all CISI-catalogued families (match_basis baseline-candidate) are
  post-catalogue unless they are one of those families; the same excess rule bounds them.
Usage: python -I build_list.py <repo root>
"""
import csv, json, pathlib, sys
from collections import Counter, defaultdict

root = pathlib.Path(sys.argv[1])
pkg = root / "experiments/2026-10-21-post-catalogue-finds"
merged = list(csv.DictReader(open(pkg / "matching/objects-merged.csv", encoding="utf-8")))
FIELDS = ["row_id", "site_code", "site", "site_as_published", "country", "baseline_volume", "baseline_year", "excavation", "season",
          "registration", "other_numbers", "findspot", "depth_or_layer", "period_or_phase", "object_type", "object_subtype", "material",
          "primary_publication", "publication_year", "page", "pdf_page", "plate_or_figure", "photo_published", "drawing_published",
          "transcription_published", "other_publications", "row_basis", "inscription_status", "catalogue_status", "excavated_before_baseline",
          "possible_duplicate_of", "cisi_in_baseline", "local_site_label", "local_match", "local_family_ids", "match_basis", "match_note",
          "context_join_family", "context_join_basis", "extracted_by", "reviewed_by"]
REVIEWER = "coordinator, Claude Opus 5.5"

rows = {}
for r in merged:
    out = {k: r.get(k, "") for k in FIELDS}
    out["match_note"] = "run 3 proposal"
    out["cisi_in_baseline"] = r.get("cisi_in_baseline", "")
    out["reviewed_by"] = REVIEWER + " (run 3 proposal accepted)"
    rows[r["row_id"]] = out

decisions = []
def decide(rid, local_match, fams, basis, reason, catalogue_status="", dup="", findspot=""):
    r = rows[rid]
    before = (r["local_match"], r["local_family_ids"], r["match_basis"], r["catalogue_status"], r["possible_duplicate_of"])
    r["local_match"], r["local_family_ids"], r["match_basis"] = local_match, fams, basis
    if catalogue_status:
        r["catalogue_status"] = catalogue_status
    if dup:
        r["possible_duplicate_of"] = dup
    if findspot:
        r["findspot"] = findspot
    r["match_note"] = reason
    r["reviewed_by"] = REVIEWER
    decisions.append({"row_id": rid, "run3_local_match": before[0], "run3_local_family_ids": before[1], "run3_match_basis": before[2],
                      "local_match": local_match, "local_family_ids": fams, "match_basis": basis,
                      "catalogue_status": r["catalogue_status"], "possible_duplicate_of": r["possible_duplicate_of"], "reason": reason})

for d in csv.DictReader(open(pkg / "review/dholavira-decisions.csv", encoding="utf-8")):
    decide(d["row_id"], d["local_match"], d["local_family_ids"], d["match_basis"], d["reason"])
for d in csv.DictReader(open(pkg / "review/coordinator-decisions.csv", encoding="utf-8")):
    decide(d["row_id"], d["local_match"], d["local_family_ids"], d["match_basis"], d["reason"],
           d["catalogue_status"], d["possible_duplicate_of"], d["findspot_correction"])
for rid, r in list(rows.items()):
    if r["site_code"] == "SKT" and r["object_type"] == "inscribed-pottery":
        decide(rid, "candidate", "3877|3878|3879|3880", "baseline-candidate",
               "CISI 1 catalogues four Surkotada potsherds (Sktd-3 to Sktd-6, families 3877-3880) without the report's catalogue numbers; this row is one of them or a post-catalogue object the corpus lacks.")
    if r["site_code"] in ("HRP", "MHJ") and r["catalogue_status"] == "in-baseline-catalogue":
        r["reviewed_by"] = REVIEWER + " (audit row; CISI number printed in the source)"

# Dholavira seals that run 2D excluded and the corpus holds.
table = {s["registration"].split()[0]: s for s in json.load(open(pkg / "extraction/D/seal-table-D.json", encoding="utf-8"))}
cat = {(c["kind"], c["catalogue"]): c for c in json.load(open(pkg / "extraction/D/catalogue-metadata-D.json", encoding="utf-8"))}
template = next(r for r in rows.values() if r["site_code"] == "DHV" and r["primary_publication"] == "bisht-2015-held")
n = max(int(rid.rsplit("-", 1)[1]) for rid in rows if rid.startswith("PCF-DHV-"))
for a in csv.DictReader(open(pkg / "review/dholavira-added-rows.csv", encoding="utf-8")):
    n += 1
    rid = f"PCF-DHV-{n:03d}"
    s = table.get(a["registration"], {})
    c = cat.get(("seal", a["catalogue_number"]), {})
    page = int(a["pdf_page"])
    rows[rid] = {k: "" for k in FIELDS} | {
        "row_id": rid, "site_code": "DHV", "site": "Dholavira", "site_as_published": template["site_as_published"], "country": "India",
        "baseline_volume": "CISI 1", "baseline_year": "1987", "excavation": template["excavation"], "registration": a["registration"],
        "other_numbers": f"seal catalogue {a['catalogue_number']}", "findspot": s.get("gsq", ""),
        "depth_or_layer": "; ".join(x for x in (f"stratum {s['stratum']}" if s.get("stratum") else "", f"Depth/3DR {s['depth']}" if s.get("depth") else "") if x),
        "object_type": "seal", "material": c.get("material", ""), "primary_publication": "bisht-2015-held", "publication_year": template["publication_year"],
        "page": str(page - 17), "pdf_page": str(page), "photo_published": "unknown", "drawing_published": "unknown", "transcription_published": "unknown",
        "row_basis": "individual", "inscription_status": "uncertain", "catalogue_status": "post-catalogue", "excavated_before_baseline": "no",
        "local_match": "matched", "local_family_ids": a["family"], "match_basis": "registration-normalised",
        "match_note": f"Run 2D excluded this seal ({a['exclusion_reason']}); its registration equals the digits of family {a['family']}'s DHR registration, and the corpus transcribes an inscription on that family. Printed page from the report's constant offset of 17.",
        "extracted_by": "coordinator, from run 2D's exclusion list and seal tables", "reviewed_by": REVIEWER}
    decisions.append({"row_id": rid, "run3_local_match": "", "run3_local_family_ids": "", "run3_match_basis": "", "local_match": "matched",
                      "local_family_ids": a["family"], "match_basis": "registration-normalised", "catalogue_status": "post-catalogue",
                      "possible_duplicate_of": "", "reason": "added row: " + rows[rid]["match_note"]})

# Baseline CISI numbers for the coordinator's containment decisions.
CISI = {"PCF-DSL-001": "Dlp-1 or Dlp-2", "PCF-DSL-002": "Dlp-1 or Dlp-2", "PCF-DSL-003": "Dlp-3",
        "PCF-SKT-001": "Sktd-1 or Sktd-2", "PCF-SKT-002": "Sktd-1 or Sktd-2", "PCF-NHT-001": "Grb-1"}
for rid, c in CISI.items():
    rows[rid]["cisi_in_baseline"] = c
LABEL = {"DSL": "Desalpur", "TKD": "Tarkhanewala-dera"}
for r in rows.values():
    r["local_site_label"] = LABEL.get(r["site_code"], r["site"])
rows["PCF-NHT-001"]["local_site_label"] = "Gharo Bhiro"

# The frozen protocol matches only on a registration or a cited plate or figure. A join that
# rests on find context alone is kept as a candidate under the protocol, and the context join
# is recorded beside it as a post-outcome refinement (README, "Context joins").
import json as _json
local = {}
with open(root / "data/normalized/lipi_observed_faces.jsonl", encoding="utf-8") as fh:
    for line in fh:
        d = _json.loads(line)
        m = d["metadata"]
        local.setdefault(d["object_family_id"], {"site": d["site"], "cisi": d["source_cisi"], "type": m.get("type") or "",
                                                 "idno": m.get("excavation-idno") or "", "material": m.get("material") or "",
                                                 "area": m.get("area-section") or "", "block": m.get("block-house") or ""})
HEAD = {"seal": {"SEAL"}, "sealing": {"TAG"}, "tag": {"TAG"}, "tablet": {"TAB"}, "inscribed-pottery": {"POT"},
        "other": {"MISC", "IMPL"}, "inscribed-tool": {"IMPL", "MISC"}, "uncertain": {"SEAL", "TAG", "TAB", "POT", "MISC", "IMPL"}}
id_matched = {r["local_family_ids"] for r in rows.values() if r["local_match"] == "matched" and r["match_basis"] not in ("context", "plate-number")}
import re as _re
def _grid(s):
    m = _re.search(r"(\d+)\s*[xX]\s*(\d+)(?:\s*[xX]\s*(\d+))?", s or "")
    return tuple(x for x in m.groups() if x) if m else ()
def _trenches(s):
    s = (s or "").upper().replace("TRENCH", " TR ").replace("TR.", " TR ")
    codes = {c.replace("I", "1").replace(" ", "") for c in _re.findall(r"\bTR\s*([A-Z]{0,2}\s?\d{1,3}[A-Z]?\d{0,3}(?:E\d+)?)", s)}
    codes |= {c.replace(" ", "") for c in _re.findall(r"\b(S\d+E\d+)\b", s)}
    return codes
def _areas(s):
    s = (s or "").upper().replace("MIDLE", "MIDDLE").replace("CITADEL", "CASTLE")
    found = set(_re.findall(r"\b(NORTH|SOUTH|EAST|WEST|CENTRAL)\b", s))
    found |= set(_re.findall(r"\b(CASTLE|BAILEY|MIDDLE TOWN|LOWER TOWN|ANNEXE)\b", s))
    return found
def _digits(s):
    runs = _re.findall(r"\d+", s or "")
    return runs[0] if runs else ""
def conflicts(r, fid):
    f = local[fid]
    if r["registration"] and f["idno"] and _re.fullmatch(r"-?DHR[-\s]*\d+", f["idno"].strip()):
        if _re.sub(r"\D", "", f["idno"]) != _digits(r["registration"]):
            return "registration"
    g1, g2 = _grid(r["findspot"]), _grid(f["block"])
    if r["site_code"] == "DHV" and g1 and g2 and g1 != g2:
        return "grid square"
    t1, t2 = _trenches(r["findspot"]), _trenches(f["area"] + " " + f["block"])
    if t1 and t2 and not (t1 & t2):
        return "trench"
    a1, a2 = _areas(r["findspot"]), _areas(f["area"])
    if a1 and a2 and not (a1 & a2):
        return "area"
    return ""

REFINEMENT = {"context", "plate-number"}
for r in rows.values():
    if r["match_basis"] in REFINEMENT:
        fam = r["local_family_ids"] if r["local_match"] == "matched" else ""
        r["context_join_family"] = fam
        r["context_join_basis"] = r["match_note"] if fam else ""
        if r["local_match"] == "matched":
            heads = HEAD.get(r["object_type"], set())
            mat = (r["material"] or "").lower()
            cands = sorted((fid for fid, f in local.items()
                            if f["site"] == r["local_site_label"] and f["type"].split(":")[0] in heads
                            and f["cisi"] in ("-", "", None) and fid not in id_matched and not conflicts(r, fid)
                            and not (mat and f["material"] not in ("-", "") and f["material"].lower() not in mat and mat not in f["material"].lower())),
                           key=int)
            r["local_match"] = "candidate"
            r["local_family_ids"] = "|".join(sorted(set(cands) | {fam}, key=int))
            r["match_note"] = ("Under the protocol a candidate of every compatible local object at the site whose registration, grid square, trench or area does not conflict; the join to family "
                               + fam + " is recorded in context_join_family. " + r["match_note"])

# Every candidate set, however it was formed, drops local objects whose registration, Dholavira
# grid square, trench or named area conflicts with the row (verification run 4, re-check). A row
# whose every candidate conflicts has no possible local counterpart and becomes absent.
for r in rows.values():
    if r["local_match"] != "candidate" or r["match_basis"] == "baseline-candidate":
        continue
    fams = [f for f in r["local_family_ids"].split("|") if f]
    keep = [f for f in fams if f == r["context_join_family"] or f not in local or not conflicts(r, f)]
    if len(keep) == len(fams):
        continue
    dropped = len(fams) - len(keep)
    if keep:
        r["local_family_ids"] = "|".join(keep)
        r["match_note"] += f" {dropped} candidate families with a conflicting registration, grid square, trench or area were removed."
    else:
        r["local_match"], r["local_family_ids"], r["match_basis"] = "absent", "", "conflict"
        r["match_note"] += f" All {dropped} candidate families conflict on registration, grid square, trench or area, so no local counterpart remains."

ordered = sorted(rows.values(), key=lambda r: (r["site_code"], r["row_id"]))
with open(pkg / "objects.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(ordered)
for d in decisions:
    r = rows[d["row_id"]]
    d["protocol_local_match"] = r["local_match"]
    d["context_join_family"] = r["context_join_family"]
with open(pkg / "join-decisions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(decisions[0])); w.writeheader(); w.writerows(decisions)

matched_fams = {r["local_family_ids"] for r in ordered if r["local_match"] == "matched"}
context_fams = matched_fams | {r["context_join_family"] for r in ordered if r["context_join_family"]}
def bounds(rows_main, with_context):
    fams = context_fams if with_context else matched_fams
    def is_matched(r):
        return r["local_match"] == "matched" or (with_context and r["context_join_family"])
    nondup = [r for r in rows_main if not r["possible_duplicate_of"]]
    cand = [r for r in nondup if not is_matched(r) and r["local_match"] == "candidate"]
    free = {f for r in cand for f in r["local_family_ids"].split("|") if f and f not in fams}
    absent = sum(1 for r in nondup if r["local_match"] == "absent")
    return (sum(1 for r in rows_main if is_matched(r)), len(free), absent + max(0, len(cand) - len(free)),
            sum(1 for r in rows_main if not is_matched(r)))
site_counts = []
by_site = defaultdict(list)
for r in ordered:
    by_site[(r["site_code"], r["site"])].append(r)
merged_counts = {r["site_code"]: r for r in csv.DictReader(open(pkg / "matching/site-counts.csv", encoding="utf-8"))} if (pkg / "matching/site-counts.csv").exists() else {}
for (code, site), rs in sorted(by_site.items(), key=lambda x: x[0][1]):
    main = [r for r in rs if r["catalogue_status"] == "post-catalogue" and r["inscription_status"] == "stated"]
    dup = [r for r in main if r["possible_duplicate_of"]]
    m0, free0, lo0, hi0 = bounds(main, False)
    m1, free1, lo1, hi1 = bounds(main, True)
    pubs = Counter(r["primary_publication"] for r in main)
    site_counts.append({
        "site_code": code, "site": site, "country": rs[0]["country"], "baseline": f"{rs[0]['baseline_volume']} ({rs[0]['baseline_year']})",
        "rows_total": len(rs), "rows_main": len(main), "possible_duplicates_main": len(dup),
        "rows_uncertain_status": sum(1 for r in rs if r["inscription_status"] == "uncertain" and r["catalogue_status"] == "post-catalogue"),
        "rows_in_baseline_catalogue": sum(1 for r in rs if r["catalogue_status"] == "in-baseline-catalogue"),
        "rows_possibly_in_cisi3": sum(1 for r in rs if r["catalogue_status"] == "possibly-in-cisi3"),
        "main_matched": sum(1 for r in main if r["local_match"] == "matched"),
        "main_candidate": sum(1 for r in main if r["local_match"] == "candidate"),
        "main_absent": sum(1 for r in main if r["local_match"] == "absent"),
        "free_candidate_families": free0,
        "absent_lower": lo0,
        "absent_upper": hi0,
        "matched_with_context_joins": m1,
        "absent_lower_with_context_joins": lo1,
        "absent_upper_with_context_joins": hi1,
        "primary_publications": "; ".join(f"{p} ({k})" for p, k in pubs.most_common()),
    })
fields = list(site_counts[0])
total = {k: "" for k in fields} | {"site_code": "ALL", "site": "All sites"}
for k in fields:
    if k.startswith(("rows_", "main_", "possible_", "absent_", "free_", "matched_")):
        total[k] = sum(int(s[k]) for s in site_counts)
with open(pkg / "sites.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(site_counts + [total])
print(json.dumps(total, indent=1))
print("decisions:", len(decisions), Counter(d["local_match"] for d in decisions))
