"""Record completed individual image review and the local asset lineage.

The dispositions below record the run-v2 view_image inspections; this script does
not perform a visual review or authorize reuse for a later uninspected render.
"""
from datetime import datetime, timezone
from pathlib import Path

from validate_package import BASE, HERE, json_new, load, sha

LABEL = "run-v2"
manifest = load(HERE / f"manifest-{LABEL}.json")
release = load(HERE / f"release-{LABEL}.json")
output = Path(manifest["output_root"])
raw_root = Path("D:/projects/indus_valley_script")
notes = {
    1: "All seven site labels separate cleanly. Modern geography and coordinate accuracy limits are explicit.",
    2: "Area C cart tracks and independent grid controls remain visible. Mixed upper exposure and absent partition denominator are stated.",
    3: "Composite period legend and curving defence band remain visible. Withdrawn angle is not displayed as a retained measurement.",
    4: "E1 and E2 endpoints meet their scoped lane banks. Source bar, feature IDs and absence of a paired pre-change exposure are clear.",
    5: "Main Street, buttress, inner span and 4C passage have separate labels. North cap points to the building connection, with Lane 1 closure explicitly unreported.",
    6: "Six different local feature scopes remain separate. Bounds and the difference from the reported Lane 1 mean are visible.",
    7: "Short fort-corner arms, trenches and exposure gaps are visible. Broad angular sensitivity and absence of a graphic metre bar are clear.",
    8: "Boxes are labelled as source-ordered propositions. Partial exposure and distinct room-count conventions remain explicit. Postjoin floor lead is in the caption and data record.",
    9: "Three western drains and the later central drain remain distinct. Access replacement and renewed drainage are described without an uninterrupted-flow claim.",
    10: "Full Figure 11 caption and registration table are legible. Wall 15 date table, Trench 22 narrative and Trench 7/8 wash conflict remain separate.",
    11: "White-margin trim enlarges the complete workshop figure. Source grid, north arrow, 5 m bar and manufacturing features remain visible.",
    12: "Trim retains approximate find dots, Wall 296, north and 5 m bar. Secondary-deposit sequence is explicit.",
    13: "All illustrated seal identities and the locus table remain visible. Courtyard floor/fill, room floor and upper fill are separate.",
    14: "Both later-blocking source labels remain visible. Original N-right rotation to N-up is explicit. Interior clearance is separate from open-through-access.",
    15: "Source N-down symbol is retained. Earlier plaster, Late Harappan features and broad clearance bounds remain visible.",
    16: "Source schematic section and cultural-stage colours remain visible. Published dimensions are separate from new scale measurement.",
    17: "All seven field bars carry their values. The denominator is 225 rows. Parallel counts and zero qualified joins remain distinct.",
    18: "Find-position photograph, close-up and ten-sign source drawing remain intact. Fallen context, mounting reconstruction and missing event date are clear.",
    19: "Recovered Figure 17 shows both measured openings and its metric bar. Phase IV labels and missing earlier comparison are explicit.",
    20: "Source site and warehouse details retain their north arrows and both bars. The bounded discovery area remains a cohort location.",
    21: "Table counts sum to 93 and prose counts to 92. W1 inference, W2 broad trench and unknown category remain legible.",
    22: "Full Mackay Plate XVI and magnified street-bank endpoints are legible at source scan resolution. Unspecified source N and reading bounds remain stated.",
    23: "Two plausible Plate XIX western bank endpoints remain visible. The board keeps the combined sensitivity envelope and caption retains the separate alternative value.",
    24: "The missing fifth reading is separated from the axis baseline in run v2. Four chords and Plate XIX alternative are clear; no trend is fitted.",
    25: "Five published Gini intervals and residence sample sizes are legible. The 80% source level remains separate from the plan measurement bounds.",
    26: "Original rice-date paragraph remains readable. AD intervals preserve different reported probability coverage and the reworking interpretation.",
    27: "Well, two tanks, solid and dashed source connections and N-down symbol remain visible. Phase uncertainty is stated.",
    28: "Original isometric drawing remains identified as reconstruction. No projected-edge metre measurement is supplied.",
    29: "Five prediction rows retain zero qualified units and unestimated effects. Required evidence and distinct source units are clear.",
    30: "Four rival explanations have discriminating and challenging observations. The deciding test remains legible below the table."
}
rows = []
for f in manifest["figures"]:
    assert sha(f["physical_path"]) == f["sha256"]
    rows.append({"figure": f["figure"], "id": f["id"], "physical_path": f["physical_path"], "sha256": f["sha256"], "viewed_individually": True, "tool": "view_image", "disposition": "pass", "notes": notes[f["figure"]]})
contacts = [{**c, "viewed": True, "disposition": "pass", "notes": "All thumbnails fit without clipping; labels identify the source boards. Full figures are used for reading source detail."} for c in release["contacts"]]
review = {"atlas_label": LABEL, "reviewed_utc": datetime.now(timezone.utc).isoformat(), "authors": manifest["authors"], "manifest_sha256": sha(HERE / f"manifest-{LABEL}.json"), "prior_exposure": "Atlas author reused the frozen source modules and reviewed proposed measurements. Same-team visual QA; not blinded or external verification.", "figures": rows, "contacts": contacts, "all_30_figures_individually_viewed": True, "automated_validation": "validation-run-v2.json", "prose_scan": {"files_scanned": 6, "final_caption_flags": 3, "disposition": "Retained technical shorthand for IIa/IIb phase panels, unspecified true/grid/magnetic north categories and lower/upper interval bounds. Frozen source wording and prior-run captions remain unchanged."}}
json_new(HERE / f"visual-review-{LABEL}.json", review)

assets = []

def add(path, role, **extra):
    path = Path(path)
    assert path.drive.upper() == "D:"
    assets.append({"role": role, "logical_path": str(path.relative_to(raw_root)).replace("\\", "/"), "physical_path": str(path), "sha256": sha(path), "bytes": path.stat().st_size, "local_only": True, "rights": "Third-party source terms retained; local-only", **extra})

for f in manifest["figures"]:
    for a in f["assets"]:
        add(a["physical_path"], "final-figure", figure=f["figure"], figure_id=f["id"], format=a["format"])
for c in release["contacts"]:
    add(c["physical_path"], "contact-sheet", figures=c["figure_ids"])
add(release["archive"]["physical_path"], "local-figure-archive")
for name in ["MANIFEST.json", "CAPTIONS.md", "LOCAL_ONLY.txt", "custom-source-panel-transforms.json"]:
    add(output / name, "local-metadata")
for r in load(output / "custom-source-panel-transforms.json"):
    if "source_parent" in r:
        add(r["physical_path"], "new-source-crop-from-held-PDF", source_id=r["source_id"], source_parent=r["source_parent"], source_parent_sha256=r["source_parent_sha256"], printed_page=r["printed_page"], pdf_zero_based_index=r["pdf_index0"], locator=r["locator"], transform_record=str(output / "custom-source-panel-transforms.json"))
json_new(HERE / f"local-assets-{LABEL}.json", {"atlas_label": LABEL, "new_archaeological_acquisitions": 0, "assets": assets, "input_sources": "inputs-freeze-v1.json", "original_source_crops": "Original unannotated crops remain at the module paths linked in manifest-run-v2.json; no source crop is copied into the tracked directory."})

sources = {}
for f in manifest["figures"]:
    for s in f["sources"]:
        key = (s["source_id"], s["source_sha256"])
        entry = sources.setdefault(key, {k: s[k] for k in ["source_id", "title", "url", "source_sha256"]})
        entry.setdefault("uses", []).append({"figure": f["figure"], "locator": s["locator"]})
json_new(HERE / f"source-links-{LABEL}.json", {"sources": list(sources.values()), "local_only": True, "postjoin_positive_lead": {"record": str(BASE / "POSTJOIN-LEAD-01.json"), "sha256": sha(BASE / "POSTJOIN-LEAD-01.json"), "locator": "OP10 printed p. 86 / preview page 94; PDF index unavailable", "url": "https://html.scribdassets.com/8ekgg3ze685nvqwx/pages/94-6670b1f665.jsonp"}})
print("Recorded 30 individual figure dispositions, 2 contact reviews and", len(assets), "local assets.")
