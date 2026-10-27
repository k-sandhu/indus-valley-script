"""Create a neutral image manifest without source codes or prior verdicts."""
import csv
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
LOCAL = ROOT / "data/raw/2026-10-22-face-adjudication"
QUEUE = ROOT / "data/raw/2026-10-22-unit-readiness/run-register-v2/divided-face-queue.csv"
IMAGES = ROOT / "data/lipi/public/seal_images"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    rows = [r for r in csv.DictReader(QUEUE.open(encoding="utf-8"))
            if r["audit_status"] == "read" and not r["physical_order"]]
    assert len(rows) == 29 and len({r["face_id"] for r in rows}) == 29
    LOCAL.mkdir(parents=True, exist_ok=True)
    result = []
    for number, r in enumerate(rows, 1):
        filenames = r["image_files"].split("|")
        primary = next((name for name in filenames if name.endswith("_imp_a.jpg")),
                       next((name for name in filenames if name.endswith("_A.jpg")), filenames[0]))
        image_rows = []
        for name in filenames:
            path = IMAGES / name
            with Image.open(path) as im:
                width, height = im.size
            image_rows.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                               "width": width, "height": height, "primary": name == primary})
        result.append({"review_id": f"F{number:02d}", "object_id": r["object_id"], "face_id": r["face_id"],
                       "source_record_id": r["source_record_id"], "cisi": r["cisi"],
                       "locator": r["source_locators"], "images": image_rows})
    write(LOCAL / "neutral-manifest.json", result)
    write(PACKAGE / "SOURCE-MANIFEST.json", {
        "selection": {"path": QUEUE.relative_to(ROOT).as_posix(), "sha256": sha(QUEUE), "rows": 29},
        "image_files": len({im["path"] for r in result for im in r["images"]}),
        "neutral_manifest": {"path": (LOCAL / "neutral-manifest.json").relative_to(ROOT).as_posix(), "sha256": sha(LOCAL / "neutral-manifest.json")},
        "protocol_sha256": sha(PACKAGE / "PROTOCOL.md"), "code_sha256": sha(Path(__file__)),
        "rights": "Existing CISI/Lipi image holdings; unresolved source rights, local-only images and detailed annotations",
    })
    print(json.dumps([{k:v for k,v in r.items() if k != "images"} | {"primary": next(im for im in r["images"] if im["primary"])} for r in result], indent=2))


if __name__ == "__main__":
    main()
