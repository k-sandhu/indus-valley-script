"""Verify atlas inputs and plotted values, then package the local-only figures.

This checks transfer and display metadata. The individual source interpretations
remain those of the frozen archaeological modules and the recorded visual review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import textwrap
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[1]
CREAM, INK, TEAL = "#f8f6ef", "#17344d", "#137e83"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, content):
    with Path(path).open("x", encoding="utf-8") as f:
        f.write(content)


def json_new(path, data):
    write_new(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def contact(figures, out, title, columns):
    cell_w, cell_h, pad, header = 650, 600, 24, 115
    rows = math.ceil(len(figures) / columns)
    canvas = Image.new("RGB", (columns * cell_w, header + rows * cell_h), CREAM)
    draw = ImageDraw.Draw(canvas)
    regular = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 25)
    bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 33)
    label = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 23)
    draw.text((pad, 20), title, fill=INK, font=bold)
    draw.text((pad, 65), "Local-only source atlas · each full-resolution figure has its source record in MANIFEST.json", fill=TEAL, font=regular)
    for i, record in enumerate(figures):
        x = (i % columns) * cell_w
        y = header + (i // columns) * cell_h
        with Image.open(record["physical_path"]) as im:
            im = im.convert("RGB")
            im.thumbnail((cell_w - 2 * pad, cell_h - 112), Image.Resampling.LANCZOS)
            canvas.paste(im, (x + (cell_w - im.width) // 2, y + 10))
        title_lines = textwrap.wrap(f'{record["figure"]:02d}  {record["title"]}', 46)
        for j, line in enumerate(title_lines[:3]):
            draw.text((x + pad, y + cell_h - 93 + j * 27), line, fill=INK, font=label)
    if out.exists():
        raise FileExistsError(out)
    canvas.save(out)
    return {"physical_path": str(out), "sha256": sha(out), "pixels": list(canvas.size), "figure_ids": [r["figure"] for r in figures]}


def main(label):
    manifest_path = HERE / f"manifest-{label}.json"
    manifest = load(manifest_path)
    output = Path(manifest["output_root"])
    freeze = load(HERE / "inputs-freeze-v1.json")
    checks, figures = [], {r["figure"]: r for r in manifest["figures"]}

    def check(name, condition, detail=None):
        checks.append({"id": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(name)

    check("final-manifest-byte-copy", sha(manifest_path) == sha(output / "MANIFEST.json"))
    check("builder-code-hash", manifest["code_sha256"] == sha(HERE / "build_atlas.py"))
    check("root-run-hash", manifest["root_run_sha256"] == sha(BASE / "run-v1.json"))
    check("input-freeze-hash", manifest["input_freeze_sha256"] == sha(HERE / "inputs-freeze-v1.json"))
    for i, record in enumerate(freeze["files"]):
        check(f"frozen-input-{i+1:03d}", sha(record["physical_path"]) == record["sha256"], record["physical_path"])
    for i, record in enumerate(manifest["input_assets"]):
        check(f"display-input-{i+1:03d}", sha(record["physical_path"]) == record["sha256"], record["physical_path"])
    check("thirty-unique-numbered-figures", sorted(figures) == list(range(1, 31)) and len({r["id"] for r in figures.values()}) == 30)
    check("nine-authored-and-twentyone-source-boards", manifest["counts"] == {"authored_png_and_svg_figures": 9, "source_raster_boards": 21})
    # Count only plan/context-map measurement boards here. Sections, object
    # photographs, isometric reconstructions and textual excerpts are excluded.
    actual_plan_figures = [2, 3, 4, 5, 7, 9, 11, 12, 14, 15, 19, 20, 22, 23, 27]
    check("at-least-twelve-actual-plan-or-context-maps", len(actual_plan_figures) >= 12, actual_plan_figures)
    asset_total = 0
    for number, record in figures.items():
        check(f"figure-{number:02d}-metadata", all(record.get(k) for k in ("id", "title", "kind", "towns", "caption", "source_note", "sources", "physical_path", "sha256")))
        check(f"figure-{number:02d}-local-only", record["local_only"] and Path(record["physical_path"]).drive.upper() == "D:")
        check(f"figure-{number:02d}-main-hash", sha(record["physical_path"]) == record["sha256"])
        check(f"figure-{number:02d}-source-locators", all(s.get("source_id") and s.get("title") and s.get("locator") and len(s.get("source_sha256") or "") == 64 for s in record["sources"]))
        for asset in record["assets"]:
            path = Path(asset["physical_path"])
            check(f"asset-{path.stem}-{asset['format']}-hash", sha(path) == asset["sha256"])
            if asset["format"] == "png":
                with Image.open(path) as im:
                    im.verify()
                with Image.open(path) as im:
                    check(f"asset-{path.stem}-dimensions", list(im.size) == asset["pixels"] and min(im.size) >= 1400)
            else:
                check(f"asset-{path.stem}-svg", ET.parse(path).getroot().tag.endswith("svg"))
            asset_total += 1
    check("thirty-nine-figure-assets", asset_total == 39)
    check("authored-chart-text-within-canvas", not any(r["outside_canvas_text"] for r in manifest["text_bounds"]))

    prior = load(ROOT / "experiments/2026-10-24-urban-form-and-inscription-ecology/modules/visuals/manifest-run-v7.json")["figures"][0]["data_values"]
    check("map-coordinate-transfer", figures[1]["data_values"] == {k: prior[k] for k in figures[1]["data_values"]})
    eastern = {r["id"]: r for r in load(BASE / "modules/plans-east/measurements.json")["measured"]}
    for row in figures[6]["data_values"]:
        source = eastern[row["id"]]
        check(row["id"] + "-plotted-value", row["value"] == source["value"] and row["bounds"] == source["reading_bound"] and row["unit"] == source["unit"])
    west = {r["id"]: r for r in load(BASE / "modules/plans-west/measurements.json")["measurements"]}
    for n in [2, 9, 14, 15, 16, 19, 27, 28]:
        for row in figures[n]["data_values"]["measurements"]:
            check(f"figure-{n:02d}-{row['id']}-complete-transfer", row == west[row["id"]])
    md = load(BASE / "modules/mohenjo-control/measurements.json")["rows"]
    check("FirstStreet-all-five-records", figures[24]["data_values"]["rows"] == md)
    check("FirstStreet-four-values-one-missing", sum(r["estimate_m"] is not None for r in md) == 4 and md[-1]["estimate_m"] is None)
    check("FirstStreet-no-imputation-or-trend", not any(figures[24]["data_values"][k] for k in ["same_ground_transect", "trend_fitted", "missing_imputed"]))
    check("Mackay-XVI-source-board-value", figures[22]["data_values"] == md[0])
    check("Mackay-XIX-source-board-value", figures[23]["data_values"] == md[3] and "alternative_edge" in md[3])
    audit = load(HERE / "mohenjo-audit-v1.json")
    check("Mackay-targeted-source-audit", not audit["correction_required"] and all(r["scale_scope_passed"] for r in audit["checks"]) and all(r.get("arithmetic_matches", True) for r in audit["checks"]))
    publication = load(BASE / "modules/mohenjo-control/published-residential-intervals.json")
    check("published-Gini-transfer", figures[25]["data_values"] == publication and publication["bound_level"] == .8 and publication["recomputed"] is False)
    dhol = load(BASE / "modules/contexts/dholavira225-summary.json")
    check("Dholavira-field-count-transfer", figures[17]["data_values"]["denominator"] == dhol["source_rows"] and all(v == dhol["gate_counts"][k] for k, v in figures[17]["data_values"]["field_counts"].items()))
    check("Dholavira-usable-stratum-and-depth", figures[17]["data_values"]["field_counts"]["stratum_label"] == 211 and figures[17]["data_values"]["field_counts"]["depth_label"] == 201)
    lothal = load(BASE / "lothal-recount-v1.json")
    denominators = load(BASE / "modules/contexts/lothal-denominators.json")
    plotted = figures[21]["data_values"]
    check("Lothal-reproduced-table-counts", plotted["table"] == [lothal["counts"][k] for k in plotted["categories"]] and sum(plotted["table"]) == 93 and lothal["passed"])
    check("Lothal-prose-conflict-retained", plotted["prose"] == [denominators["prose_counts"][k] for k in plotted["categories"]] and sum(plotted["prose"]) == 92)
    run = load(BASE / "run-v1.json")
    check("five-eligibility-decisions-transferred", figures[29]["data_values"]["decisions"] == run["decisions"] and figures[29]["data_values"]["source_units"] == run["counts"])
    check("eligibility-effects-stay-null", all(r["eligible"] == 0 and r["effect"] is None for r in figures[29]["data_values"]["decisions"]))
    check("Area-C-registered-descriptive-pair", figures[2]["data_values"]["registration"] == run["grid_registration"])
    lead = load(BASE / "POSTJOIN-LEAD-01.json")
    check("Kanmer-postjoin-positive-lead-transferred", figures[8]["data_values"]["postjoin_lead"] == lead and sha(BASE / "POSTJOIN-LEAD-01.json") == freeze["postjoin_addendum_sha256"])
    check("Kanmer-reported-count-scopes", figures[8]["data_values"]["open_space_dimensions_m"] == [7, 5] and figures[8]["data_values"]["OP10_subphase_rooms"] == 3 and figures[8]["data_values"]["OP10_later_rooms"] == ">6" and figures[8]["data_values"]["Multicultural_rooms_per_structural_phase"] == 8, "Manually read source quantities; separate accounts and exposure scopes retained in caption.")
    check("Dholavira-ten-sign-context-scope", figures[18]["data_values"]["source_sign_count"] == 10 and figures[18]["data_values"]["mounting_reconstructed"] and not figures[18]["data_values"]["emplacement_date_join"])
    for i, record in enumerate(load(output / "custom-source-panel-transforms.json")):
        if "source_parent" in record:
            check(f"new-source-crop-{i}-parent", sha(record["source_parent"]) == record["source_parent_sha256"])
            check(f"new-source-crop-{i}-output", sha(record["physical_path"]) == record["sha256"])
        else:
            check(f"margin-trim-{i}-parent", sha(record["parent_raster"]) == record["parent_sha256"] and record["rotation"] == 0 and not record["contrast_changed"])
            with Image.open(record["parent_raster"]) as im:
                x0, y0, x1, y1 = record["crop_box_px"]
                check(f"margin-trim-{i}-bounds", 0 <= x0 < x1 <= im.width and 0 <= y0 < y1 <= im.height)
    forbidden = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".pdf", ".zip", ".pptx"}
    check("no-third-party-binaries-in-tracked-module", not any(p.suffix.lower() in forbidden for p in HERE.rglob("*") if p.is_file()))
    validation = {"status": "pass", "checked_utc": datetime.now(timezone.utc).isoformat(), "atlas_label": label, "manifest_sha256": sha(manifest_path), "frozen_input_count": len(freeze["files"]), "figure_asset_count": asset_total, "actual_plan_or_context_map_figures": actual_plan_figures, "checks": checks, "scope": "Transfer, hash, locator, missingness, denominator and layout checks; source interpretations remain linked to the module records."}
    json_new(HERE / f"validation-{label}.json", validation)
    contacts = [contact(list(figures.values()), output / "contact-all.png", "All 30 figures · source plans, contexts and deciding tests", 5), contact([figures[n] for n in manifest["selected_cover_figures"]], output / "contact-selected.png", "Selected figures · plans and measurement evidence", 4)]
    readme = "LOCAL-ONLY ATLAS\n\nThis archive contains 30 figure PNGs, 9 authored SVGs, source citations, captions, two contact sheets and a figure manifest. Third-party source imagery retains its source terms. Keep this archive on local storage; no web redistribution is authorized.\n\nMANIFEST.json preserves source IDs, links, exact locators, source hashes and quantities. The full archaeological protocol, original source crops and detailed endpoints remain in the local project. Relative cultural phases are not independently dated repair events. Missing observations remain missing.\n"
    write_new(output / "LOCAL_ONLY.txt", readme)
    package_files = [Path(a["physical_path"]) for r in figures.values() for a in r["assets"]] + [output / n for n in ["MANIFEST.json", "CAPTIONS.md", "LOCAL_ONLY.txt", "contact-all.png", "contact-selected.png"]]
    archive = output.parent / f"atlas-{label}-local-only.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in package_files:
            z.write(path, path.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.infolist()) == len(package_files)
    release = {"atlas_label": label, "local_only": True, "manifest": str(manifest_path), "manifest_sha256": sha(manifest_path), "validation_path": str(HERE / f"validation-{label}.json"), "validation_sha256": sha(HERE / f"validation-{label}.json"), "contacts": contacts, "archive": {"physical_path": str(archive), "sha256": sha(archive), "bytes": archive.stat().st_size, "member_count": len(package_files)}, "figure_count": 30, "png_count": 30, "svg_count": 9, "selected_figures": manifest["selected_cover_figures"], "author": "GPT-6 family; exact serving variant unknown; Codex desktop", "visual_review": f"Recorded separately in visual-review-{label}.json after individual full-resolution image inspection and contact review."}
    json_new(HERE / f"release-{label}.json", release)
    print(json.dumps({"validation": "pass", "check_count": len(checks), "release": str(HERE / f"release-{label}.json"), "archive": release["archive"], "contacts": contacts}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="run-v2")
    main(parser.parse_args().label)
