"""Check the delivered PPTX against the frozen presentation inputs."""
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/presentation")
RUN = sys.argv[1] if len(sys.argv) > 1 else "v2"
NS = {
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numbers(series, key):
    return [float(n.text) for n in series.findall(f"c:{key}/c:numRef/c:numCache/c:pt/c:v", NS)]


def close(actual, expected):
    assert len(actual) == len(expected), (actual, expected)
    assert all(math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10) for a, b in zip(actual, expected)), (actual, expected)


def main():
    evidence = LOCAL / "build" / f"evidence-{RUN}.json"
    d = json.loads(evidence.read_text(encoding="utf-8"))
    manifest = json.loads((HERE / f"input-manifest-{RUN}.json").read_text(encoding="utf-8"))
    assert sha(evidence) == manifest["evidence_sha256"]
    for r in manifest["inputs"]:
        assert sha(ROOT / r["logical_path"]) == r["sha256"], r["logical_path"]
    deck = LOCAL / "output" / f"indus-urban-form-2026-10-24-{RUN}.pptx"
    receipt = json.loads((LOCAL / "build" / RUN / "validation.json").read_text(encoding="utf-8"))
    assert sha(deck) == receipt["finalSha256"]
    assert receipt["packageIntegrity"]["status"] == "pass"
    assert receipt["firstPartyImport"]["passed"]
    assert receipt["presentationLayout"]["finding_count"] == 0
    md = d["md_series"]
    stages = [r for r in d["observations"] if r["town"] == "dholavira" and r["feature"] == "occupation_interval" and r["source_id"] == "W-S01"]
    orientation = d["synthetic"]["orientation"]
    prior = next(r["values"] for r in d["prior"]["results"] if r["id"] == "PR-03")
    # Source-derived values and explicit derivations, mapped to the final slide numbers.
    expected = {
        2: [{"val": [126, 118, 43]}],
        9: [{"val": [2.8, 4.5]}],
        10: [{"val": [10, 49 - 10]}],
        12: [{"val": [r["longer_to_shorter_ratio"] for r in d["shape"]["rows"]]}],
        13: [{"val": [3000 - r["start_bce"] for r in stages]}, {"val": [r["start_bce"] - r["end_bce"] for r in stages]}],
        14: [{"val": [r["gini"] for r in md]}],
        15: [{"val": [r["median_area_m2"] for r in md]}],
        16: [{"val": [1, 60, 56, 45, 225 - 1 - 60 - 56 - 45]}],
        17: [{"val": [139, 225 - 139]}],
        20: [{"val": [41, 65 - 41]}],
        21: [{"xVal": prior["/variant_prediction/primary/component_bootstrap_95_interval"], "yVal": [1, 1]},
             {"xVal": [prior["/variant_prediction/primary/mean_gain_bits"]], "yVal": [1]}],
        22: [{"xVal": [r["district_offset_degrees"] for r in orientation], "yVal": [1] * 4},
             {"xVal": [r["district_offset_degrees"] for r in orientation], "yVal": [r["global_q4"] for r in orientation]}],
        24: [{"val": [r["credence"] for r in d["cards"]]}],
    }
    charts_checked = []
    table_slides = []
    notes_checked = []
    numeric_points = 0
    with ZipFile(deck) as z:
        names = z.namelist()
        slides = [n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        assert len(slides) == 26
        assert not [n for n in names if n.startswith("ppt/media/")]
        assert len([n for n in names if n.endswith(".xlsx")]) == 13
        for i in range(1, 27):
            xml = ET.fromstring(z.read(f"ppt/slides/slide{i}.xml"))
            if xml.findall(".//a:tbl", NS):
                table_slides.append(i)
            notes = ET.fromstring(z.read(f"ppt/notesSlides/notesSlide{i}.xml"))
            text = "\n".join(t.text or "" for t in notes.findall(".//a:t", NS))
            assert len(text) > 200 and "undefined" not in text, i
            notes_checked.append(i)
            rels = ET.fromstring(z.read(f"ppt/slides/_rels/slide{i}.xml.rels"))
            chart_targets = [r.attrib["Target"].lstrip("/") for r in rels if r.attrib["Type"].endswith("/chart")]
            if i not in expected:
                assert not chart_targets
                continue
            assert len(chart_targets) == 1
            chart = ET.fromstring(z.read(chart_targets[0]))
            series = chart.findall(".//c:ser", NS)
            assert len(series) == len(expected[i]), i
            for s, exp in zip(series, expected[i]):
                for key, vals in exp.items():
                    close(numbers(s, key), vals)
                    numeric_points += len(vals)
                for smooth in s.findall("c:smooth", NS):
                    assert smooth.attrib["val"] == "0", i
            charts_checked.append(i)
    assert table_slides == [3, 4, 6, 7, 8, 11, 15, 17, 18, 19, 21, 23, 25]
    assert len(charts_checked) == 13 and len(notes_checked) == 26
    native = json.loads((LOCAL / "build" / RUN / "powerpoint" / "native-review.json").read_text(encoding="utf-8-sig"))
    assert native["exportedSlides"] == 26 and len(native["sampleChartsEditedResizedSavedReopened"]) == 3
    assert not native["finalFileChanged"]
    out = dict(status="pass", run=RUN, final_path=str(deck), final_sha256=sha(deck),
               input_files_hash_checked=len(manifest["inputs"]), frozen_assertions=len(d["observations"]),
               slides=26, native_charts=13, native_tables=13, note_pages=26,
               acquired_source_images_embedded=0, chart_numeric_points_source_checked=numeric_points,
               chart_slides_checked=charts_checked, table_slides_checked=table_slides,
               native_powerpoint_rendered_slides=26, native_chart_edit_reopen_samples=3,
               claim_boundary="Chart caches checked against the frozen register and stated derivations. Source acquisition and archaeological interpretations remain in the study's separate reviews.")
    target = HERE / f"verification-{RUN}.json"
    target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
