"""Measure the frozen, manually read excavation-plan candidates.

Source images, endpoints and crop transforms remain in the local D: data tree.
This script writes authored aggregates here and annotated source panels on D:.
The reading bounds describe endpoint sensitivity, not survey accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import textwrap
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def read_length(row, multiplier=1):
    d = distance(*row["points"])
    b = distance(*row["scale_points"])
    e = row["endpoint_radius_px"] * multiplier
    eb = row["bar_endpoint_radius_px"] * multiplier
    s = row["scale_m"]
    return s * d / b, [s * max(0, d - 2 * e) / (b + 2 * eb),
                       s * (d + 2 * e) / (b - 2 * eb)]


def read_angle(row, multiplier=1):
    a, v, b = row["points"]
    u = (a[0] - v[0], a[1] - v[1])
    w = (b[0] - v[0], b[1] - v[1])
    lu, lw = math.hypot(*u), math.hypot(*w)
    value = math.degrees(math.acos(max(-1, min(1, (u[0]*w[0]+u[1]*w[1])/(lu*lw)))))
    e = row["endpoint_radius_px"] * multiplier
    # Each vector can move by at most 2e. The sum of its direction cones is
    # conservative even though the vectors share the vertex endpoint.
    delta = sum(math.degrees(math.asin(min(1, 2 * e / length))) for length in (lu, lw))
    return value, [max(0, value - delta), min(180, value + delta)]


def rounded(values):
    return [round(x, 3) for x in values]


def draw_panel(raw: Path, panel: dict, rows: list[dict], results: dict):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.open(raw / panel["render"])
    box = panel["crop_box_px"]
    factor = panel["display_scale"]
    cropped = image.crop(box)
    crop_path = raw / f'{panel["id"]}-untouched-crop.png'
    cropped.save(crop_path)
    picture = cropped.resize((round(cropped.width*factor), round(cropped.height*factor)))
    header, sidebar, footer = 125, 510, 100
    canvas = Image.new("RGB", (picture.width + sidebar, picture.height + header + footer), "#f8f6ef")
    canvas.paste(picture, (0, header))
    draw = ImageDraw.Draw(canvas)
    regular = "C:/Windows/Fonts/arial.ttf"
    bold = "C:/Windows/Fonts/arialbd.ttf"
    title_font = ImageFont.truetype(bold, 34)
    body_font = ImageFont.truetype(regular, 26)
    small_font = ImageFont.truetype(regular, 21)
    label_font = ImageFont.truetype(bold, 29)
    draw.text((24, 15), panel["title"], font=title_font, fill="#143f50")
    draw.text((24, 65), panel["subtitle"], font=body_font, fill="#294c56")
    palette = ["#ba2026", "#1265a0", "#7b348b", "#007d68"]
    cursor = header + 12
    selected = [r for r in rows if r["id"] in panel["measurement_ids"] and r["id"] in results]
    for i, row in enumerate(selected):
        color = palette[i % len(palette)]
        points = [((x-box[0])*factor, (y-box[1])*factor + header) for x, y in row["points"]]
        draw.line(points, fill=color, width=5)
        for x, y in points:
            draw.ellipse((x-6, y-6, x+6, y+6), fill="white", outline=color, width=3)
        mid = points[len(points)//2]
        if row["kind"] == "length":
            mid = ((points[0][0]+points[1][0])/2, (points[0][1]+points[1][1])/2)
        offset = panel.get("label_offsets", {}).get(row["label"], [10, 8])
        draw.text((mid[0]+offset[0], mid[1]+offset[1]), row["label"], font=label_font,
                  fill=color, stroke_width=3, stroke_fill="white")
        result = results[row["id"]]
        unit = "m" if row["kind"] == "length" else "degrees"
        text = f'{row["label"]}  {result["value"]:.2f} {unit}\nReading bound {result["reading_bound"][0]:.2f}-{result["reading_bound"][1]:.2f}'
        draw.multiline_text((picture.width+22, cursor), text, font=body_font, fill=color, spacing=8)
        cursor += 85
        for line in textwrap.wrap(row["description"], 33):
            draw.text((picture.width+22, cursor), line, font=small_font, fill="#203640")
            cursor += 27
        cursor += 22
    for note in panel["notes"]:
        for line in textwrap.wrap(note, 33):
            draw.text((picture.width+22, cursor), line, font=small_font, fill="#203640")
            cursor += 27
        cursor += 18
    for feature in panel.get("callouts", []):
        x, y = feature["point"]
        x, y = (x-box[0])*factor, (y-box[1])*factor + header
        tx, ty = feature["label_position"]
        tx, ty = (tx-box[0])*factor, (ty-box[1])*factor + header
        draw.line([(tx, ty+30), (x, y)], fill=feature["color"], width=4)
        draw.ellipse((x-7, y-7, x+7, y+7), outline=feature["color"], width=4)
        draw.text((tx, ty), feature["label"], font=label_font, fill=feature["color"],
                  stroke_width=3, stroke_fill="white")
    draw.text((24, canvas.height-80), panel["locator"], font=small_font, fill="#203640")
    draw.text((24, canvas.height-47), "Actual source plan. Reading bounds cover digitization only. All source imagery remains local.",
              font=small_font, fill="#203640")
    overlay = raw / f'{panel["id"]}-annotated.png'
    canvas.save(overlay)
    return crop_path, overlay


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-east"))
    args = parser.parse_args()
    out = Path(__file__).resolve().parent
    raw = args.raw
    endpoint_path = raw / "manual-endpoints-v1.json"
    inputs = json.loads(endpoint_path.read_text(encoding="utf-8"))
    freeze = out / "inventory-freeze.json"
    assert digest(freeze) == inputs["inventory_freeze_sha256"]
    rows = inputs["measurements"]
    quality_path = raw / "measurement-review.json"
    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    withdrawn = {r["id"]: r for r in quality["withdrawn"]}
    results = {}
    for row in rows:
        assert digest(raw / row["render"]) == row["render_sha256"]
        if row["id"] in withdrawn:
            continue
        fn = read_length if row["kind"] == "length" else read_angle
        value, bound = fn(row)
        _, sensitivity = fn(row, 2)
        record = {k: row[k] for k in ["id", "town", "phase", "window", "feature", "description", "locator"]}
        record.update({"source_id": "PE-S01" if row["town"] == "farmana" else "PE-S02" if row["town"] == "kanmer" else "PE-S03",
                       "kind": row["kind"], "value": round(value, 3),
                       "unit": "m" if row["kind"] == "length" else "degree",
                       "reading_bound": rounded(bound), "double_radius_sensitivity_bound": rounded(sensitivity),
                       "bound_type": "conservative digitization sensitivity; not a confidence interval",
                       "source_survey_accuracy": None,
                       "source_error_missing_reason": "Original survey accuracy and scan distortion are unspecified. These can exceed the reading bounds.",
                       "reported_value": row["reported"], "reported_unit": row["reported_unit"], "reported_scope": row["reported_scope"],
                       "endpoint_record": str(endpoint_path).replace("\\", "/") + "#" + row["id"],
                       "endpoint_file_sha256": digest(endpoint_path),
                       "endpoint_radius_px": row["endpoint_radius_px"],
                       "scale_metres": row["scale_m"],
                       "scale_bar_endpoint_radius_px": row.get("bar_endpoint_radius_px"),
                       "north_reference": "No north arrow on this detailed panel; source uses local excavation grid" if row["town"] == "farmana" else "N symbol present; true/grid/magnetic type unspecified",
                       "persistence_rate_eligible": False,
                       "scope": "One manually read transect or corner in one published panel. No matched episode survival denominator.",
                       "connectivity_inference": "Not measured by this geometric quantity. See episodes.json."})
        results[row["id"]] = record
    missing = [
        {"id":"PE-M009", "window":"FAR-E1", "town":"farmana", "feature":"FAR-E1-A1", "value":None, "unit":"m",
         "missing_reason":"Irregular bathing-platform outline meets the western exposure limit. A maximum drawn span would not reproduce the report's orthogonal dimensions or establish a former lane width.", "persistence_rate_eligible":False},
        {"id":"PE-M010", "window":"FAR-C2", "town":"farmana", "feature":"FAR-C2-R2", "value":None, "unit":"m",
         "missing_reason":"The selected junction contains later pits and a north cap. The lane's average width is reported in text, but a source-matched intact transect has not been identified here.", "persistence_rate_eligible":False}
    ]
    (out / "measurements.json").write_text(json.dumps({"schema_version":"1.0", "inventory_freeze_sha256":digest(freeze), "measured":list(results.values()), "unmeasured_candidates":missing,
        "withdrawn_after_visual_review": [{**r, "value":None, "unit":"degree", "town":"banawali", "persistence_rate_eligible":False,
            "retained_endpoint_record":str(endpoint_path).replace("\\", "/")+"#"+r["id"], "review_record":str(quality_path).replace("\\", "/"), "review_sha256":digest(quality_path)} for r in withdrawn.values()]}, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    specs = json.loads((raw / "panels-spec.json").read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in json.loads((out / "sources.json").read_text(encoding="utf-8"))}
    panel_rows = []
    for panel in specs:
        import fitz
        source = sources[panel["source_id"]]
        assert digest(Path(source["physical_path"])) == source["sha256"]
        pdf = fitz.open(source["physical_path"])
        page = pdf[panel["pdf_zero_based_index"]]
        cropped, annotated = draw_panel(raw, panel, rows, results)
        tracked = {k: panel[k] for k in ["id", "title", "subtitle", "source_id", "locator", "pdf_zero_based_index", "printed_page", "figure", "phase", "measurement_ids", "notes"]}
        tracked.update({"source_render":str(raw/panel["render"]).replace("\\", "/"), "source_render_sha256":digest(raw/panel["render"]),
                        "untouched_crop":str(cropped).replace("\\", "/"), "crop_sha256":digest(cropped),
                        "annotated_overlay":str(annotated).replace("\\", "/"), "overlay_sha256":digest(annotated),
                        "detailed_transform_record":str(raw/"panels-spec.json").replace("\\", "/")+"#"+panel["id"],
                        "transform_file_sha256":digest(raw/"panels-spec.json"),
                        "source_parent_pdf":source["physical_path"], "source_parent_sha256":source["sha256"],
                        "source_page_geometry":{"media_box":list(page.mediabox), "crop_box":list(page.cropbox), "rotation":page.rotation},
                        "render_transform":"MuPDF full-page 1.7x matrix; no additional rotation, warp or contrast change",
                        "north_reference":"No north symbol on this detailed panel; local excavation grid retained" if panel["source_id"]=="PE-S01" else "N symbol; true/grid/magnetic type unspecified",
                        "retained_measurement_ids":[x for x in panel["measurement_ids"] if x in results],
                        "withdrawn_measurement_ids":[x for x in panel["measurement_ids"] if x in withdrawn],
                        "rights":"local-only; no redistribution permission asserted", "persistence_rate_eligible":False})
        panel_rows.append(tracked)
    (out / "plan-panels.json").write_text(json.dumps(panel_rows,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"measured":len(results), "unmeasured":len(missing), "withdrawn":len(withdrawn), "panels":len(panel_rows), "values":{k:[v["value"],v["reading_bound"]] for k,v in results.items()}},indent=2))


if __name__ == "__main__":
    main()
