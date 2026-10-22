"""Record acquisition totals, methods and observable repairs."""
import argparse
import collections
import csv
import datetime
import json
import pathlib


def main():
    parser = argparse.ArgumentParser()
    for name in ("root", "raw", "records"):
        parser.add_argument("--" + name, type=pathlib.Path, required=True)
    args = parser.parse_args()
    records = args.records.resolve()
    with (records / "source-register-1a.csv").open(encoding="utf-8", newline="") as f:
        sources = list(csv.DictReader(f))
    proposals_path = records / "manifest-proposals-1a.json"
    proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
    for entry in proposals["sources"]:
        pins = list(entry.get("hashes", {}).values())
        if pins:
            entry["fetch"]["sha256"] = pins[0]
    proposals_path.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")
    log = [json.loads(line) for line in (records / "acquisition-log-1a.jsonl").read_text(encoding="utf-8").splitlines()]
    states = json.loads((records / "processing-summary-1a.json").read_text(encoding="utf-8"))
    bibliographic = json.loads((records / "bibliography-validation-1a.json").read_text(encoding="utf-8"))
    sweep = json.loads((records / "sweep-summary-1a.json").read_text(encoding="utf-8"))
    result = dict(
        recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        agent="codex gpt-6.1-sol run 1A", source_count=len(sources),
        status_counts=dict(collections.Counter(r["status"] for r in sources)),
        held_verified_files=sum(r["route"] == "held" and bool(r["sha256"]) for r in sources),
        unswept_kanmer_witness_files=sum(bool(r.get("no_sweep")) for r in states),
        held_sources_swept=sum(r["route"] == "held" and not r.get("no_sweep") for r in states),
        acquired_assets=sum(r["status"] == "held" for r in proposals["sources"]),
        downloaded_asset_bytes=sum(r.get("actual_bytes", 0) for r in proposals["sources"]),
        total_network_bytes=sum(r["bytes"] for r in log), network_request_outcomes=len(log),
        network_status_counts=dict(collections.Counter(str(r["status"]) for r in log)),
        text_basis_counts=dict(collections.Counter(r["text_basis"] for r in sources if r["text_basis"])),
        page_text_files=sum(int(r.get("pdf_pages") or 0) for r in sources),
        failed_sources=[r["source_id"] for r in sources if r["status"] == "failed"],
        duplicates=[dict(source_id=r["source_id"], sha256=r["sha256"]) for r in sources if r["status"] == "duplicate"],
        wrong_volumes=[dict(source_id=r["source_id"], observed_year_or_volume=r["year_or_volume"]) for r in sources if r["status"] == "wrong-volume"],
        candidate_pages=sweep["unique_candidate_pages"], per_site_candidate_pages=sweep["per_site"],
        new_site_lead_rows=sweep["new_site_leads"],
        unresolved_iar_heading_pages=len(sweep.get("unresolved_iar_heading_pages", [])),
        bibliography=dict(title_confirmed=sum(r["title_confirmed"] for r in bibliographic),
                          authors_confirmed=sum(r["author_confirmed"] for r in bibliographic),
                          unresolved_or_metadata_only_fields="Recorded per source; unknown fields remain empty."),
        methods=dict(downloads="Repository fetch_http loaded by file path; archive MD5/SHA1 compared after acquisition.",
            extraction="Poppler text extraction; archive page OCR replaces PDF pages below the threshold; journal OCR is split by leaf.",
            tesseract="English, 300 dpi grayscale rendering; three pages per source and up to three sources concurrently; completed pages cached locally.",
            keyword_matching="Case-insensitive matching tolerates spacing and hyphenation; normalized text prefilters the regular expressions.",
            printed_pages="Automatic header/footer detection; no manual page-image review.",
            source_text="Page files and snippets stay local. No objects were extracted or classified."),
        observable_repairs=[
            "PyMuPDF was unavailable under isolated Python; Poppler supplied PDF text and rendering.",
            "The first sequential OCR pass was interrupted. The replacement runner caches each completed page and processes page batches concurrently.",
            "Bibliographic checks exposed OCR year errors. Usable PDF text is retained and annual year ranges must span consecutive years.",
            "Unconfirmed archive creators and non-name OCR fragments were removed from author/editor fields.",
            "The duplicate mirror file and the requested archive replacement are both retained."
        ],
        deviations=[
            "The first import wrote tools/__pycache__/fetch_data.cpython-313.pyc outside the owned paths. Bytecode writing was then disabled. The source tool was not edited.",
            "The unswept Kanmer witness exposure rows record bytes hashed by script because their text was not read.",
            "The existing Kanmer artifact manifest was consulted to resolve the local witnesses named by the source register."
        ],
        page_images_viewed=0,
        command_workdir=records.parent.relative_to(args.root.resolve()).as_posix(),
        command_parameters=dict(ROOT=str(args.root.resolve()), RAW=str(args.raw.resolve()), RECORDS=str(records),
            SEED=str(records.parent / "selection/sites-seed.csv")),
        reproduction_commands=[
            "python -I acquisition/fetch_proposed.py discover --root ROOT --raw RAW --records RECORDS",
            "python -I acquisition/fetch_proposed.py fetch --root ROOT --raw RAW --records RECORDS",
            "python -I acquisition/process_sources.py held --root ROOT --raw RAW --records RECORDS --seed SEED",
            "python -I acquisition/process_sources.py duplicates --root ROOT --raw RAW --records RECORDS --seed SEED",
            "python -I acquisition/process_sources.py extract --root ROOT --raw RAW --records RECORDS --seed SEED",
            "python -I acquisition/process_sources.py supplemental --root ROOT --raw RAW --records RECORDS --seed SEED",
            "python -I acquisition/fetch_proposed.py fetch --root ROOT --raw RAW --records RECORDS",
            "python -I acquisition/archive_ocr_iar.py --root ROOT --raw RAW --records RECORDS",
            "python -I acquisition/fetch_proposed.py fetch --root ROOT --raw RAW --records RECORDS",
            "python -I acquisition/process_sources.py extract --ocr --root ROOT --raw RAW --records RECORDS --seed SEED",
            "python -I acquisition/bibliography.py --root ROOT --raw RAW --records RECORDS",
            "python -I acquisition/process_sources.py sweep --root ROOT --raw RAW --records RECORDS --seed SEED",
            "python -I acquisition/selftest-1a.py --root ROOT --raw RAW --records RECORDS"
        ])
    result["tracked_outputs"] = sorted(p.relative_to(args.root.resolve()).as_posix() for p in records.iterdir() if p.is_file())
    (records / "run-record-1a.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("source_count", "status_counts", "downloaded_asset_bytes", "total_network_bytes", "text_basis_counts", "candidate_pages", "new_site_lead_rows")}))


if __name__ == "__main__":
    main()
