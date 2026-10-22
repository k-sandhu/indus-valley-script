"""Coordinator review: decide Dholavira joins on registration digits and one-to-one grid squares.

Inputs: matching/objects-merged.csv (run 3), extraction/D/seal-table-D.json and
extraction/D/catalogue-metadata-D.json (run 2D's identity tables for all 225 seals and 61
sealings in the report, including those it excluded), extraction/D/exclusions-D.csv, and the
local corpus read for identity fields only (no sign, motif or size field).

Rules, written before applying them:
1. Registration. A row or an excluded report object and a local family agree when the leading
   digit run of the report registration equals the whole digit run of the family's
   excavation-idno written DHR-<n> or DHR <n>. Prefix containment is not agreement.
2. One-to-one grid square. When no registration ties a row, it is matched to a family when the
   row's grid square (digit triple or pair) is held by exactly one object of the same kind in
   the report's tables and by exactly one family of compatible type in the corpus, and the
   depths do not conflict where both are given.
3. Otherwise the row is a candidate of every compatible family at its grid square, or of every
   compatible family at the site not matched elsewhere.
Excluded report objects whose registration agrees with a local family become rows with
inscription_status "uncertain": the report's table does not state an inscription, and the
corpus transcribes one.

Writes review/dholavira-decisions.csv and review/dholavira-added-rows.csv.
Usage: python -I match_dholavira.py <repo root>
"""
import csv, json, pathlib, re, sys
from collections import Counter, defaultdict

root = pathlib.Path(sys.argv[1])
pkg = root / "experiments/2026-10-21-post-catalogue-finds"
keep = ["excavation-idno", "area-section", "block-house", "room-grid", "depth", "period", "time", "material", "type"]
fams = {}
with open(root / "data/normalized/lipi_observed_faces.jsonl", encoding="utf-8") as fh:
    for line in fh:
        d = json.loads(line)
        if d["site"] == "Dholavira":
            m = d["metadata"]
            fams.setdefault(d["object_family_id"], {"cisi": d["source_cisi"], **{k: m.get(k) for k in keep}})

def lead_digits(s):
    runs = re.findall(r"\d+", s or "")
    return runs[0] if runs else ""

def grid(s):
    m = re.search(r"(\d+)\s*[xX]\s*(\d+)(?:\s*[xX]\s*(\d+))?", s or "")
    return tuple(x for x in m.groups() if x) if m else ()

KIND = {"seal": "SEAL", "sealing": "TAG", "tag": "TAG", "tablet": "TAB", "inscribed-pottery": "POT", "other": "MISC", "inscribed-tool": "IMPL"}
def compatible(row_type, fam_type):
    head = (fam_type or "").split(":")[0]
    return head == KIND.get(row_type) or (row_type in ("other", "inscribed-tool") and head in ("MISC", "IMPL"))

def fam_depth_cm(fid):
    m = re.match(r"\s*(\d+)\s*cm", fams[fid]["depth"] or "")
    return m.group(1) if m else None

fam_reg = {fid: re.sub(r"\D", "", f["excavation-idno"]) for fid, f in fams.items()
           if re.fullmatch(r"-?DHR[-\s]*\d+", (f["excavation-idno"] or "").strip())}
reg_to_fam = defaultdict(list)
for fid, r in fam_reg.items():
    reg_to_fam[r].append(fid)

seal_table = json.load(open(pkg / "extraction/D/seal-table-D.json", encoding="utf-8"))
catalogue = json.load(open(pkg / "extraction/D/catalogue-metadata-D.json", encoding="utf-8"))
report_grids = Counter()
for s in seal_table:
    g = grid(s.get("gsq"))
    if g:
        report_grids[("seal", g)] += 1
for c in catalogue:
    if c["kind"] == "sealing":
        gs = {grid(x) for x in (c.get("gsq") or []) + (c.get("context_gsq") or []) if grid(x)}
        for g in gs:
            report_grids[("sealing", g)] += 1

rows = [r for r in csv.DictReader(open(pkg / "matching/objects-merged.csv", encoding="utf-8")) if r["site_code"] == "DHV"]
decisions, claimed = {}, defaultdict(list)
for r in rows:
    reg = lead_digits(r["registration"])
    hits = reg_to_fam.get(reg, []) if reg else []
    if len(hits) == 1 and compatible(r["object_type"], fams[hits[0]]["type"]):
        decisions[r["row_id"]] = ("matched", hits[0], "registration-normalised", f"report registration {reg} equals the digits of the family's DHR registration; object type agrees")
        claimed[hits[0]].append(r["row_id"])
for r in rows:
    if r["row_id"] in decisions:
        continue
    g = grid(r["findspot"])
    kind = "seal" if r["object_type"] == "seal" else "sealing" if r["object_type"] in ("sealing", "tag") else r["object_type"]
    at_grid = [fid for fid, f in fams.items() if g and grid(f["block-house"]) == g and compatible(r["object_type"], f["type"]) and fid not in claimed]
    reg = lead_digits(r["registration"])
    at_grid = [fid for fid in at_grid if not (fid in fam_reg and reg and fam_reg[fid] != reg)]
    if g and len(at_grid) == 1 and report_grids.get((kind, g), 0) == 1:
        fid = at_grid[0]
        dc = fam_depth_cm(fid)
        nums = set(re.findall(r"\d+", r["depth_or_layer"] or ""))
        if dc and nums and dc not in nums:
            decisions[r["row_id"]] = ("candidate", fid, "context", f"grid square {'x'.join(g)} is one-to-one, but the family's depth {dc} cm is not among the row's depth values")
        else:
            decisions[r["row_id"]] = ("matched", fid, "context", f"grid square {'x'.join(g)} holds one {kind} in the report's tables and one compatible family in the corpus; depth {'agrees' if dc and nums else 'not comparable'}")
            claimed[fid].append(r["row_id"])
    elif g and at_grid:
        decisions[r["row_id"]] = ("candidate", "|".join(at_grid), "context", f"grid square {'x'.join(g)}: {report_grids.get((kind, g), 0)} report objects of this kind, {len(at_grid)} compatible families")
for r in rows:
    if r["row_id"] in decisions:
        continue
    free = [fid for fid, f in fams.items() if compatible(r["object_type"], f["type"]) and fid not in claimed and f["cisi"] in ("-", "", None)]
    g = grid(r["findspot"])
    free = [fid for fid in free if not (g and grid(fams[fid]["block-house"]) and grid(fams[fid]["block-house"]) != g)
            and not (fid in fam_reg)]
    if free:
        decisions[r["row_id"]] = ("candidate", "|".join(free), "type-only", f"{len(free)} compatible families at the site with no conflicting grid square or registration")
    else:
        decisions[r["row_id"]] = ("absent", "", "all-families-assigned", "no compatible family remains")

added = []
for e in csv.DictReader(open(pkg / "extraction/D/exclusions-D.csv", encoding="utf-8")):
    reg = lead_digits(e["registration"])
    hits = reg_to_fam.get(reg, []) if reg else []
    if len(hits) == 1 and hits[0] not in claimed:
        added.append({"registration": e["registration"], "object_class": e["object_class"], "catalogue_number": e["catalogue_number"],
                      "pdf_page": e["pdf_page"], "exclusion_reason": e["reason"], "family": hits[0], "family_type": fams[hits[0]]["type"]})
        claimed[hits[0]].append("added:" + reg)

with open(pkg / "review/dholavira-decisions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["row_id", "local_match", "local_family_ids", "match_basis", "reason"])
    for rid in sorted(decisions):
        w.writerow([rid, *decisions[rid]])
with open(pkg / "review/dholavira-added-rows.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["registration", "object_class", "catalogue_number", "pdf_page", "exclusion_reason", "family", "family_type"])
    w.writeheader(); w.writerows(added)

print("decisions:", Counter((v[0], v[2]) for v in decisions.values()))
print("families matched twice:", {k: v for k, v in claimed.items() if len(v) > 1})
print("rows added from exclusions:", len(added), Counter(a["exclusion_reason"] for a in added))
print("DHR families still unexplained:", sorted(fid for fid in fam_reg if fid not in claimed))
