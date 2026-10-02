"""Check frozen source links, frame accounting and reproducible summaries."""
from __future__ import annotations

from collections import Counter
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import runpy

from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: str) -> dict:
    return json.loads((BASE / path).read_text(encoding="utf-8"))


def equivalent(a: dict, b: dict) -> bool:
    # Creation time is intentionally different on a separately saved replay.
    return {k: v for k, v in a.items() if k != "created_utc"} == {k: v for k, v in b.items() if k != "created_utc"}


def main() -> None:
    target = BASE / "verification.json"
    if target.exists():
        raise FileExistsError(target)
    checks = []

    def check(name: str, condition: bool, detail=None) -> None:
        checks.append({"check": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(name)

    initial, data, display = read("initial/frame.json"), read("annotated/results.json"), read("display-summary/results.json")
    check("initial source unchanged", sha(ROOT / initial["input"]["path"]) == initial["input"]["sha256"])
    check("initial code snapshot", sha(BASE / "initial/code_snapshot.py") == initial["code_sha256"])
    check("annotation code snapshot", sha(BASE / "annotated/code_snapshot.py") == data["code_sha256"])
    check("display code snapshot", sha(BASE / "display-summary/code_snapshot.py") == display["code_sha256"])
    for item in data["inputs"]:
        check("annotation input hash: " + item["path"], sha(ROOT / item["path"]) == item["sha256"])
    check("display input hash", sha(ROOT / display["input_path"]) == display["input_sha256"])
    ledger = data["target_ledger"]
    check("81 distinct retained targets", len(ledger) == len({r["target_id"] for r in ledger}) == 81)
    check("four target group sizes", Counter(r["group"] for r in ledger) == {"copied_tablets": 22, "sealings_and_stopper": 7, "stamped_vessels": 40, "rectangular_seals": 12})
    check("export presence accounting", Counter(r["export_join_status"] for r in ledger) == {"unique-family": 72, "absent": 9})
    check("source coverage accounting", sum(r["primary_registration"] is not None for r in ledger) == 24)
    check("57 image gaps retained", len(data["summary"]["target_objects_without_image_observation"]) == 57)
    registrations = data["registration_ledger"]
    check("25 unique caption registrations", len(registrations) == len({r["source_registration"]["registration"] for r in registrations}) == 25)
    check("registration joins unambiguous", all(r["join"]["status"] == "unique-object" for r in registrations))
    physical = data["physical_objects"]
    check("29 visible objects, 24 in frame", len(physical) == 29 and sum(r["in_target_frame"] for r in physical) == 24)
    check("source witness types", Counter(r["witness_type"] for r in physical) == {"drawing": 25, "photograph": 4})
    check("observations retain material and action basis", all(r["material"].get("basis") and r["physical_action"].get("basis") for r in physical))
    tablets = [r for r in physical if r["type"] == "incised tablet"]
    check("22 tablets have three displayed faces", len(tablets) == 22 and all(r["displayed_inscribed_faces"] == 3 for r in tablets))
    check("sixteen distinct unit-8040 items", len({r["registration"]["item"] for r in tablets if r["registration"]["excavation_unit"] == "8040"}) == 16)
    check("source deposition categories", Counter(r["deposition_association"]["value"] for r in tablets) == {"clump": 16, "near-clump": 2, "scattered": 4})
    check("published engraver counts", Counter(r["published_engraver_group"]["value"] for r in tablets) == {1: 6, 2: 9, 3: 7})
    faces = data["face_observations"]
    check("73 displayed surfaces with bases and coordinates", len(faces) == 73 and all(r["basis"] and r["source_coordinate"] for r in faces))
    object_ids = {r["observation_id"] for r in tablets}
    tablet_faces = [r for r in faces if r["observation_id"] in object_ids]
    check("66 tablet surfaces", len(tablet_faces) == 66)
    check("three unresolved lower-face forms", sum(r["descriptive_form"] is None for r in tablet_faces) == 3)
    counted = [r for r in tablet_faces if r["separate_upright_stroke_count"] is not None]
    check("seven directly counted faces", len(counted) == 7 and Counter(r["separate_upright_stroke_count"] for r in counted) == {3: 5, 4: 2})
    for specimen in [8, 16]:
        sub = {r["side"]: r["separate_upright_stroke_count"] for r in counted if r["source_coordinate"]["specimen"] == specimen}
        check(f"specimen {specimen} direct stroke pattern", sub == {"top": 3, "middle": 4, "bottom": 3})
    check("eight supported display classes", len(display["patterns"]) == 8 and sum(r["count"] for r in display["patterns"]) == 19)
    check("three missing pairs retained", len(display["missing_pairs"]) == 3)
    check("reported fifth Beas fragment retained", data["reported_missing_image_object"]["status"] == "reported in source text, absent from acquired Figure 12 pixels")
    check("uncertain H1714 phase preserved", next(r for r in physical if r["target_id"] == "H-1714")["phase"]["value"] == "3C?")
    for manifest_name in ["figure4-crop-manifest.json", "figure4-native-crop-manifest.json"]:
        manifest = read(manifest_name)
        check(manifest_name + " specimen index", {r["specimen"] for r in manifest["crops"]} == set(range(1, 24)))
        for item in manifest["crops"]:
            check(f"{manifest_name} crop {item['specimen']}", sha(ROOT / item["path"]) == item["sha256"])
    with Image.open(BASE / "local-witness/meadow-kenoyer2001-figure4.gif") as im:
        refinement = read("source-format-refinement.json")
        check("GIF independent format refinement", im.format == refinement["format"] and list(im.size) == refinement["dimensions"] == [600, 566])

    # Snapshot location differs from src/six_hour, so supply the recorded workspace
    # paths explicitly. The snapshot itself is preserved and executed unchanged.
    scope = runpy.run_path(str(BASE / "annotated/code_snapshot.py"))
    scope["annotation_endpoint"].__globals__.update({"ROOT": ROOT, "BASE": BASE})
    annotation_replay = BASE / "local-witness/verification-replay-annotation"
    with redirect_stdout(io.StringIO()):
        scope["annotation_endpoint"](annotation_replay)
    replay = json.loads((annotation_replay / "results.json").read_text(encoding="utf-8"))
    check("frozen annotation snapshot replay", equivalent(data, replay), "creation time excluded; all content, input hashes and code hash match")
    scope = runpy.run_path(str(BASE / "display-summary/code_snapshot.py"))
    scope["display_summary"].__globals__.update({"ROOT": ROOT, "BASE": BASE})
    display_replay = BASE / "local-witness/verification-replay-display"
    with redirect_stdout(io.StringIO()):
        scope["display_summary"](BASE / "annotated/results.json", display_replay)
    replay = json.loads((display_replay / "results.json").read_text(encoding="utf-8"))
    check("frozen display snapshot replay", equivalent(display, replay), "creation time excluded; all other content matches")
    record = {"created_utc": datetime.now(timezone.utc).isoformat(), "verifier_sha256": sha(Path(__file__)), "checks": checks,
              "total": len(checks), "passed": sum(r["passed"] for r in checks), "failed": sum(not r["passed"] for r in checks),
              "replay_paths": [annotation_replay.relative_to(ROOT).as_posix(), display_replay.relative_to(ROOT).as_posix()],
              "scope": "source hashes, accounting, annotation lineage and deterministic computation; external graphic classification remains a one-observer source audit"}
    target.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ["total", "passed", "failed"]}))


if __name__ == "__main__":
    main()
