"""Build a source-defined object frame and preserve bounded acquisition records."""
from __future__ import annotations

import argparse
from collections import defaultdict, Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/2026-10-02-six-hour/harappa-object-frame"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cisi_base(s: str) -> str | None:
    m = re.fullmatch(r"([A-Za-z]+)-?(\d+)(?:[A-Za-z])?", s.strip())
    return f"{m.group(1).upper()}-{int(m.group(2))}" if m else None


def build_frame(output: Path) -> None:
    source = ROOT / "data/normalized/lipi_observed_faces.jsonl"
    indexed = defaultdict(list)
    rows = [json.loads(s) for s in source.read_text(encoding="utf-8").splitlines() if s.strip()]
    for row in rows:
        base = cisi_base(row["source_cisi"])
        if base:
            indexed[base].append(row)
    groups = {"copied_tablets": range(2218, 2240), "sealings_and_stopper": range(1719, 1726),
              "stamped_vessels": range(1727, 1767), "rectangular_seals": range(1704, 1716)}
    frame, hints = [], []
    for group, numbers in groups.items():
        for n in numbers:
            target = f"H-{n}"
            matches = indexed.get(target, [])
            families = sorted({row["object_family_id"] for row in matches}, key=int)
            frame.append({"target_id": target, "group": group, "export_family_ids": families,
                          "export_face_ids": [r["record_id"] for r in matches], "export_face_count": len(matches),
                          "export_join_status": "absent" if not matches else "unique-family" if len(families) == 1 else "ambiguous-family",
                          "primary_registration": None, "primary_excavation_unit": None, "primary_item": None,
                          "primary_museum_accession": None, "primary_source_links": [], "source_image_status": "not-yet-coded"})
            for row in matches:
                hints.append({"target_id": target, "record_id": row["record_id"], "metadata": row["metadata"]})
    assert len(frame) == 81 and len({r["target_id"] for r in frame}) == 81
    assert Counter(r["group"] for r in frame) == {"copied_tablets": 22, "sealings_and_stopper": 7, "stamped_vessels": 40, "rectangular_seals": 12}
    payload = {"created_utc": now(), "protocol": "experiments/2026-10-02-six-hour/harappa-object-frame/PROTOCOL.md",
               "code_sha256": sha(Path(__file__)), "input": {"path": source.relative_to(ROOT).as_posix(), "sha256": sha(source)},
               "frame_size": len(frame), "join_statuses": dict(Counter(r["export_join_status"] for r in frame)), "objects": frame,
               "provenance": "Target IDs follow the published groups; export links are computed joins, with source assertions added in a separate endpoint."}
    write_json(output / "frame.json", payload)
    shutil.copyfile(Path(__file__), output / "code_snapshot.py")
    write_json(BASE / "local-witness/export-hints.json", {"source_sha256": sha(source), "rights_status": "derivative metadata local-only", "rows": hints})
    print(json.dumps({"output": str(output), "frame_size": len(frame), "join_statuses": payload["join_statuses"]}, indent=2))


def acquire(url: str, source_id: str, extension: str) -> None:
    import requests
    if not re.fullmatch(r"[a-z0-9_-]+", source_id):
        raise ValueError("source_id must be a plain lowercase identifier")
    target = BASE / "local-witness" / f"{source_id}.{extension.lstrip('.')}"
    record_path = BASE / "acquisition" / f"{source_id}.json"
    if target.exists() or record_path.exists():
        raise FileExistsError(source_id)
    record = {"source_id": source_id, "url": url, "requested_utc": now(), "access_method": "ordinary HTTPS request",
              "rights_status": "rights-unverified; local-only witness"}
    try:
        response = requests.get(url, timeout=50)
        record.update({"final_url": response.url, "http_status": response.status_code, "bytes": len(response.content),
                       "content_type": response.headers.get("content-type")})
        if response.status_code == 200:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(response.content)
            record.update({"local_path": target.relative_to(ROOT).as_posix(), "sha256": sha(target)})
            if response.content.startswith(b"%PDF"):
                import fitz
                record["format_verified"] = "PDF"
                record["pages"] = len(fitz.open(target))
            elif extension.lower() in {"jpg", "jpeg", "png"}:
                from PIL import Image
                with Image.open(target) as im:
                    record.update({"format_verified": im.format, "dimensions": list(im.size)})
            else:
                record["format_verified"] = "HTML or text; identity requires inspection"
    except Exception as exc:
        record.update({"error_type": type(exc).__name__, "error": str(exc)})
    record["completed_utc"] = now()
    write_json(record_path, record)
    print(json.dumps(record, indent=2))


def render(source: Path, pages: list[int], source_id: str, dpi: int = 180) -> None:
    binary = shutil.which("pdftoppm")
    if not binary:
        raise FileNotFoundError("pdftoppm not found; use the bundled Poppler binary")
    out = BASE / "local-witness" / "renders"
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for page in pages:
        prefix = out / f"{source_id}-pdf{page}"
        target = Path(str(prefix) + ".png")
        if target.exists():
            raise FileExistsError(target)
        subprocess.run([binary, "-f", str(page), "-l", str(page), "-r", str(dpi), "-singlefile", "-png", str(source), str(prefix)], check=True, capture_output=True)
        from PIL import Image
        with Image.open(target) as im:
            size = list(im.size)
        records.append({"pdf_page_one_based": page, "path": target.relative_to(ROOT).as_posix(), "sha256": sha(target), "dimensions": size})
    write_json(BASE / "acquisition" / f"{source_id}-renders.json", {"source_path": source.relative_to(ROOT).as_posix(), "source_sha256": sha(source),
               "rendered_utc": now(), "renderer": "Poppler pdftoppm", "dpi": dpi, "pages": records})
    print(json.dumps(records, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    frame = sub.add_parser("frame")
    frame.add_argument("--output", type=Path, default=BASE / "initial")
    fetch = sub.add_parser("acquire")
    fetch.add_argument("--url", required=True)
    fetch.add_argument("--source-id", required=True)
    fetch.add_argument("--extension", required=True)
    draw = sub.add_parser("render")
    draw.add_argument("--source", type=Path, required=True)
    draw.add_argument("--source-id", required=True)
    draw.add_argument("--pages", type=int, nargs="+", required=True)
    draw.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()
    if args.command == "frame":
        build_frame(args.output)
    elif args.command == "acquire":
        acquire(args.url, args.source_id, args.extension)
    elif args.command == "render":
        render(args.source.resolve(), args.pages, args.source_id, args.dpi)


if __name__ == "__main__":
    main()
