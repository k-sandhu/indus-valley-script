"""Join sealed visual observations and later catalogue alignment; keep details local."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
LOCAL = ROOT / "data/raw/2026-10-22-face-adjudication"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def image_meta(path):
    with Image.open(path) as im:
        width, height = im.size
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "width": width,
            "height": height, "display_transform": {"crop": None, "reflection": False, "rotation_degrees": 0}}


def main():
    visual = read(LOCAL / "visual-pass-1.json")
    freeze = read(PACKAGE / "VISUAL-PASS-1-FREEZE.json")
    assert sha(LOCAL / "visual-pass-1.json") == freeze["sha256"]
    manifest = read(LOCAL / "neutral-manifest.json")
    alignment = read(LOCAL / "alignment-observations.json")
    code_access = read(LOCAL / "catalogue-codes/source-access.json")
    code_rows = {r["review_id"]:r for r in read(LOCAL / "catalogue-codes/codes.json")}
    vmap = {r["id"]:r for r in visual["primary_observations"]}
    amap = {r["review_id"]:r for r in alignment["records"]}
    actual_paths = {Path(r["path"]).name for r in visual["access_log"]}
    actual_paths.update(Path(r["path"]).name for r in read(LOCAL / "later-image-access.json"))
    output = []
    for r in manifest:
        rid = r["review_id"]
        v, a = vmap[rid], amap[rid]
        alts = [x for x in visual["alternate_observations"] if x["id"] == rid]
        accepted = v["accepted"]
        confidence = v["confidence"]
        for alt in alts:
            if alt.get("accepted_change") is not None:
                accepted = alt["accepted_change"]
                confidence = alt["confidence"]
        alignment_result = {**a, "source_path": code_access["source_path"],
                            "source_sha256": code_access["source_sha256"],
                            "source_locator": "record_id=" + r["source_record_id"],
                            "source_font_path": code_access["font_path"], "source_font_sha256": code_access["font_sha256"],
                            "segment_lengths": list(map(len, code_rows[rid]["segments"])),
                            "source_code": code_rows[rid]["raw_code"],
                            "interpretation": "source-segment positions only; no linguistic traversal accepted"}
        alignment_result.update(read(LOCAL / "alignment-extra.json").get(rid, {}))
        images = [image_meta(ROOT / x["path"]) for x in r["images"] if Path(x["path"]).name in actual_paths]
        output.append({
            "review_id": rid, "face_id":r["face_id"], "object_id":r["object_id"],
            "source_record_id":r["source_record_id"], "cisi":r["cisi"], "source_locator":r["locator"],
            "observer":visual["observer"], "image_witnesses":images,
            "observations": {"primary_image":v["primary"], "group_bounds":v["groups"],
                             "coordinate_system":"approximate original-image pixels [x0,y0,x1,y1]",
                             "counts":v["counts"], "arrangement":v["arrangement"], "damage":v["damage"],
                             "note":v["note"], "alternate_observations":alts, "first_pass_sha256":freeze["sha256"]},
            "source_alignment":alignment_result,
            "proposed_traversal":{"status":"unresolved", "reason":"Physical group locations do not establish historic reading traversal."},
            "alternative_traversals":["upper-first", "lower-first", "another order consistent with source direction and layout"],
            "accepted_for_physical_layout":accepted, "physical_layout_confidence":confidence,
            "accepted_for_segment_order":a["accepted_for_segment_order"],
            "segment_order_scope":"provisional catalogue-segment to graphic-group localization; parent adjudication follows",
            "unresolved_reasons":["historical reading traversal unestablished"] + ([] if a["accepted_for_segment_order"] else [a["basis"]]),
            "exposure_record":{"historically_examined_corpus":True, "first_pass_masked_codes_and_prior_verdicts":True,
                               "historical_summary_exposure":True, "fresh_confirmation_claim":False,
                               "first_pass_seal":freeze["sealed_utc"], "catalogue_alignment_access":code_access["utc"],
                               "independent_parent_record_read_after_both_sealed":True,
                               "parent_visual_pass":"data/raw/2026-10-22-evidence-integration/root-visual-pass.jsonl",
                               "parent_visual_pass_sha256":"9b7c01803d5216cb6264f38ff4c09ec4d54c6868933f08fe87820b780ab2a479"},
        })
    assert len(output) == 29 and len({r["face_id"] for r in output}) == 29
    with (LOCAL / "face-reviews.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
        for r in output:
            stream.write(json.dumps(r, ensure_ascii=False) + "\n")
    supplement_specs = read(LOCAL / "supplemental-authored-observations.json")
    supplements=[]
    for r in supplement_specs:
        supplements.append({**{k:v for k,v in r.items() if k!="files"}, "image_witnesses":[image_meta(ROOT / "data/lipi/public/seal_images" / n) for n in r["files"]], "observer":visual["observer"], "review_status":"submitted-source-review; independent integration pending"})
    write(LOCAL / "supplemental-identity-reviews.json", supplements)
    access = visual["access_log"] + read(LOCAL / "later-image-access.json") + [code_access]
    access.append({"phase":"catalogue-code-display", "utc":None,
                   "time_basis":"Tool transcript places this first text display after the visual seal and before catalogue-font rendering.",
                   "source_path":code_access["source_path"], "source_sha256":code_access["source_sha256"]})
    write(LOCAL / "source-access-log.json", access)
    checks = {"all_29_dispositions":len(output)==29,
              "first_pass_hash_unchanged":sha(LOCAL / "visual-pass-1.json")==freeze["sha256"],
              "rendered_code_access_after_seal":code_access["utc"]>freeze["sealed_utc"],
              "all_source_images_hash_match":all(sha(ROOT / i["path"])==i["sha256"] for r in output+supplements for i in r["image_witnesses"]),
              "all_primary_geometry_within_image":all(0<=b[0]<b[2]<=next(i["width"] for i in r["image_witnesses"] if i["path"].endswith('/'+r["observations"]["primary_image"])) and 0<=b[1]<b[3]<=next(i["height"] for i in r["image_witnesses"] if i["path"].endswith('/'+r["observations"]["primary_image"])) for r in output for b in r["observations"]["group_bounds"]),
              "no_historical_reading_traversal_accepted":all(r["proposed_traversal"]["status"]=="unresolved" for r in output),
              "duplicate_impression_hash_confirmed":sha(ROOT / "data/lipi/public/seal_images/M-663_imp_a.jpg")==sha(ROOT / "data/lipi/public/seal_images/M-663_a_7g.jpg")}
    aggregate={"schema_version":"1.0", "status_class":"source-review", "faces":len(output),
               "accepted_physical_layout_observations":sum(r["accepted_for_physical_layout"] for r in output),
               "provisional_segment_to_group_maps":sum(r["accepted_for_segment_order"] for r in output),
               "historic_traversals_accepted":0, "supplemental_identity_cases":len(supplements),
               "primary_image_views":29, "first_pass_alternate_views":8,
               "layout_confidence":dict(Counter(r["physical_layout_confidence"] for r in output)),
               "checks":checks, "pass":all(checks.values()),
               "outputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in [LOCAL/"face-reviews.jsonl",LOCAL/"supplemental-identity-reviews.json",LOCAL/"source-access-log.json"]],
               "inputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in [LOCAL/"neutral-manifest.json",LOCAL/"visual-pass-1.json",LOCAL/"alignment-observations.json",LOCAL/"catalogue-codes/source-access.json"]],
               "code_sha256":sha(Path(__file__)), "built_utc":datetime.now(timezone.utc).isoformat()}
    write(PACKAGE / "results-v1.json", aggregate)
    print(json.dumps({k:v for k,v in aggregate.items() if k not in ["outputs","inputs"]},indent=2))


if __name__ == "__main__":
    main()
