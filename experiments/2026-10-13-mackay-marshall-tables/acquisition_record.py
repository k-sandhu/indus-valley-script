"""Write the acquisition record for the epachayan tables and the printed witnesses.

Run from the repository root:
    python -P experiments/2026-10-13-mackay-marshall-tables/acquisition_record.py

Reads the local clone and scans under data/raw/2026-10-13-mackay-marshall-tables/ and
writes experiments/2026-10-13-mackay-marshall-tables/acquisition.json. Hashes of files in
the clone are taken from the committed blob (`git show <commit>:<path>`), which is what a
fresh clone on any platform reproduces, and also from the working tree, which differs
where Git converted line endings on checkout.
"""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-13-mackay-marshall-tables"
CLONE = RAW / "epachayan-indus-script"
OUT = Path(__file__).resolve().parent / "acquisition.json"
COMMIT = "5c14a01f44296a01256a34e7e5e5e9fd82d9a67f"

TRACKED_FILES = [
    "outputs/mackay_seal_table.csv",
    "outputs/marshall_seal_table_transcribed.csv",
    "outputs/marshall_seal_table.csv",
    "outputs/findspots_mackay.csv",
    "transcriptions/mackay1938_plates/matches.csv",
    "transcriptions/mackay1938_plates/photo_codings.csv",
    "transcriptions/mackay1938_seal_table/NOTES.md",
    "transcriptions/marshall1931_seal_table/NOTES.md",
    "LICENSE",
    "LICENSE-DATA",
    "docs/DATA_NOTICE.md",
    "docs/DATASETS.md",
    "README.md",
    "CITATION.cff",
]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(CLONE), *args], check=True, capture_output=True).stdout


def csv_shape(b: bytes):
    rows = list(csv.reader(io.StringIO(b.decode("utf-8"))))
    return {"rows_excluding_header": len(rows) - 1, "columns": rows[0]}


def main():
    head = git("rev-parse", "HEAD").decode().strip()
    files = []
    for rel in TRACKED_FILES:
        blob = git("show", f"{COMMIT}:{rel}")
        wt = (CLONE / rel).read_bytes()
        rec = {
            "path": rel,
            "bytes_committed": len(blob),
            "sha256_committed": sha256(blob),
            "sha256_working_tree": sha256(wt),
        }
        if rel.endswith(".csv"):
            rec.update(csv_shape(blob))
        files.append(rec)
    n_tracked = len(git("ls-files").decode().splitlines())

    mackay_pdf = RAW / "mackay1938/mackay1938_vol1_dli70071.pdf"
    marshall_alt = ROOT / "data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/marshall-alt-pdf.body"
    marshall_gov = ROOT / "research/literature/sources/marshall_1931_govscan_14985.pdf"

    rec = {
        "package": "2026-10-13-mackay-marshall-tables",
        "repository": {
            "url": "https://github.com/epachayan/indus-script",
            "pinned_commit": COMMIT,
            "checked_out_head": head,
            "commit_date": git("log", "-1", "--format=%cI", COMMIT).decode().strip(),
            "commit_subject": git("log", "-1", "--format=%s", COMMIT).decode().strip(),
            "commits_in_history_at_pin": len(git("log", "--format=%H", COMMIT).decode().split()),
            "files_tracked_at_pin": n_tracked,
            "clone_started_utc": (RAW / "clone-started-utc.txt").read_text().strip(),
            "clone_finished_utc": (RAW / "clone-finished-utc.txt").read_text().strip(),
            "local_path": "data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/",
            "method": "git clone --no-checkout, then git checkout of the pinned commit",
            "files": files,
            "rights": {
                "status": "explicit-license",
                "data_licence": "CC BY 4.0",
                "data_licence_scope": "LICENSE-DATA at the pin: transcriptions/mackay1938_seal_table/, transcriptions/marshall1931_seal_table/, transcriptions/mackay1938_plates/, and outputs/mackay_seal_table.csv, outputs/marshall_seal_table.csv, outputs/marshall_seal_table_transcribed.csv, outputs/findspots_mackay.csv, outputs/concordance_parpola_G.csv, outputs/concordance_m77_G_inferred.csv, outputs/constraints.csv",
                "data_attribution_required": "Nitin Stephen Koshy, \"Indus script: seal catalogues and text-structure analysis\" (2026), https://github.com/epachayan/indus-script",
                "code_licence": "MIT (LICENSE, Copyright (c) 2026 Nitin Stephen Koshy); DATA_NOTICE.md says it covers scripts/ only",
                "zenodo_record": "10.5281/zenodo.22852769 (concept DOI in README and CITATION.cff); the 12 October inventory opened version record 10.5281/zenodo.23281781, CC BY 4.0, which holds only the preprint PDF",
                "notice_files": ["LICENSE-DATA", "docs/DATA_NOTICE.md", "LICENSE", "CITATION.cff"],
            },
        },
        "witnesses": [
            {
                "id": "mackay-1938-vol1-dli",
                "title": "Further Excavations At Mohenjo-daro Vol-i Text (archive.org title), Mackay 1938",
                "url": "https://archive.org/download/in.ernet.dli.2015.70071/2015.70071.Further-Excavations-At-Mohenjo-daro-Vol-i-Text.pdf",
                "retrieved_utc": (RAW / "mackay1938/retrieved-utc.txt").read_text().strip(),
                "local_path": str(mackay_pdf.relative_to(ROOT)).replace("\\", "/"),
                "bytes": mackay_pdf.stat().st_size,
                "sha256": sha256(mackay_pdf.read_bytes()),
                "sha1_archive_metadata": "fc554d3dbcc44f6851d4749193cde56a27141f8f",
                "pdf_pages": 746,
                "table_pages": "printed pp. 369-391 = PDF pages 392-414 (1-based); PDF index = printed page + 22",
                "rights_observed": "archive.org item metadata carries a DLI record with 'dc.rights: Out_of_copyright' in its description; no licenceurl field. Copyright status of the 1938 Government of India publication is not settled here.",
                "rights_status": "rights-unverified",
                "handling": "local-only",
            },
            {
                "id": "marshall-1931-vol2-dli",
                "title": "Mohenjo-daro And The Indus Civilization 1931 (archive.org item in.ernet.dli.2015.62023), vol. II",
                "local_path": str(marshall_alt.relative_to(ROOT)).replace("\\", "/"),
                "bytes": marshall_alt.stat().st_size,
                "sha256": sha256(marshall_alt.read_bytes()),
                "acquired_by": "2026-10-06 evidence census (focused pass, 7 October); used unchanged",
                "table_pages": "printed pp. 402-405 = PDF pages 53-56 (1-based)",
                "rights_status": "rights-unverified",
                "handling": "local-only",
            },
            {
                "id": "marshall-1931-vol2-olmh",
                "title": "Mohenjo Daro And The Indus Civilization Edited By Sir John Marshall, Vol. 2, 1931 (archive.org item OLMh_mohenjo-daro-and-the-indus-civilization-edited-by-sir-john-marshall-vol.-2-1931-; Gurukul Kangri University Haridwar collection, digitized by S3 Foundation)",
                "url": "https://iiif.archive.org/iiif/3/OLMh_mohenjo-daro-and-the-indus-civilization-edited-by-sir-john-marshall-vol.-2-1931-/manifest.json",
                "retrieved_utc": (RAW / "marshall1931/olmh/retrieved-utc.txt").read_text().split()[-1],
                "files": [
                    {"canvas": c, "printed_page": p, "local_path": f"data/raw/2026-10-13-mackay-marshall-tables/marshall1931/olmh/canvas_{c}.jpg",
                     "bytes": (RAW / f"marshall1931/olmh/canvas_{c}.jpg").stat().st_size,
                     "sha256": sha256((RAW / f"marshall1931/olmh/canvas_{c}.jpg").read_bytes())}
                    for c, p in [(53, 396), (54, 397), (55, 398), (56, 399), (59, 402), (60, 403), (61, 404), (62, 405)]
                ],
                "note": "Canvases 53-56 were fetched first on a wrong page estimate (they hold pp. 396-399); 59-62 hold the tabulation. Printed pages for 53-55 are inferred from canvas 56 = p. 399. The manifest response is cached at data/raw/2026-10-13-mackay-marshall-tables/web/olmh-iiif-info.json.",
                "rights_status": "rights-unverified",
                "handling": "local-only",
            },
            {
                "id": "marshall-1931-govscan",
                "local_path": str(marshall_gov.relative_to(ROOT)).replace("\\", "/"),
                "bytes": marshall_gov.stat().st_size,
                "sha256": sha256(marshall_gov.read_bytes()),
                "note": "Held; 428 pages at 917x1190 px. PDF page 61 (1-based) is printed p. 19 headed 'THE BUILDINGS', so this is vol. I and does not contain the vol. II tabulation; not used for checking.",
                "rights_status": "rights-unverified",
                "handling": "local-only",
            },
        ],
    }
    OUT.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
