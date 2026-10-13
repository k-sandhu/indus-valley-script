#!/usr/bin/env python3
"""Write sources.json: every web source consulted by this inventory.

Combines the web-check agent's record (data/raw/2026-10-12-data-inventory/
web-checks-v1/checks.json, local-only, with saved witnesses) and the checks
made directly during the inventory. Witness files stay local; this file holds
titles, URLs, access state, hashes and short findings.

    python -I experiments/2026-10-12-data-inventory/make_sources.py
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = "data/raw/2026-10-12-data-inventory"
CHECKS = ROOT / RAW / "web-checks-v1" / "checks.json"
OUT = pathlib.Path(__file__).resolve().parent / "sources.json"

DIRECT = [
    {
        "id": "D01",
        "item": "epachayan/indus-script repository (machine-readable Mackay 1938 and Marshall 1931 seal tables)",
        "title": "indus-script (GitHub repository epachayan/indus-script); README description begins 'Machine-readable Mohenjo-daro seal catalogues'",
        "url": "https://github.com/epachayan/indus-script",
        "opened": True,
        "snippet_only": False,
        "access_date": "2026-10-12",
        "method": "WebFetch summary of the repository page; GitHub REST API for the latest commit, repository metadata and file tree; raw README.md, docs/DATA_NOTICE.md, docs/DATASETS.md and LICENSE at the pinned commit saved locally",
        "pinned_commit": "5c14a01f44296a01256a34e7e5e5e9fd82d9a67f",
        "commit_date": "2026-10-10T11:58:09Z",
        "witnesses": [
            {"path": f"{RAW}/web-checks-own/epachayan-README.md", "sha256": "9ea875beafcbf3db9a4dfae41d580226df2aa614f6b15f3c5097adc3d77592e5"},
            {"path": f"{RAW}/web-checks-own/epachayan-docs_DATA_NOTICE.md", "sha256": "b10390ab9eea816b371dda058e47ecff08efcb95097e462ce0d60573d131255a"},
            {"path": f"{RAW}/web-checks-own/epachayan-docs_DATASETS.md", "sha256": "bfda616fec5edcbdc622e11c937029356315193877161ee966ddeb6fc143373d"},
            {"path": f"{RAW}/web-checks-own/epachayan-LICENSE", "sha256": "799612d75938aa9368d91f284920015b56c7a00af9a6c718d4907cb4e2e2c0cc"},
        ],
        "finding": "Repository created 2026-09-19; GitHub licence field MIT. File tree includes outputs/mackay_seal_table.csv, outputs/marshall_seal_table.csv, outputs/findspots_mackay.csv and per-page transcriptions. DATASETS.md describes Mackay (1938) vol. I 'Tabulation of Seals', printed pp. 369-391, 709 rows (Nos. 1-704), with size in inches, level relative to the DK datum and excavation field number; and Marshall (1931) vol. II 'Tabulation of Seals', printed pp. 402-405, 560 rows (Nos. 1-557), with size in inches and depth below the modern surface. DATA_NOTICE.md states that the MIT licence covers code in scripts/ only and that the committed transcribed tables are CC BY 4.0; it lists Mackay 1938 as out of copyright. The README reports AI transcription with OCR cross-checks (95.7% type agreement on 596 of 709 Mackay rows) and says depth and field numbers are not independently verified.",
        "reuse_terms": "Transcribed data CC BY 4.0 (DATA_NOTICE.md); code MIT",
    },
    {
        "id": "D02",
        "item": "Hugging Face dataset ksaw008/indus-reference-benchmarks visibility",
        "title": "Hugging Face Hub API, datasets/ksaw008/indus-reference-benchmarks",
        "url": "https://huggingface.co/api/datasets/ksaw008/indus-reference-benchmarks",
        "opened": True,
        "snippet_only": False,
        "access_date": "2026-10-12",
        "retrieved_utc": "2026-10-13T03:34:03Z",
        "method": "Anonymous HTTP GET with curl; status code only",
        "finding": "HTTP 401 to an anonymous request: the dataset is not public.",
    },
    {
        "id": "D03",
        "item": "Hugging Face dataset ksaw008/indus-research-data visibility",
        "title": "Hugging Face Hub API, datasets/ksaw008/indus-research-data",
        "url": "https://huggingface.co/api/datasets/ksaw008/indus-research-data",
        "opened": True,
        "snippet_only": False,
        "access_date": "2026-10-12",
        "retrieved_utc": "2026-10-13T03:34:03Z",
        "method": "Anonymous HTTP GET with curl; status code only",
        "finding": "HTTP 401 to an anonymous request: private, as recorded in REPRODUCING.md.",
    },
]


def main() -> int:
    checks = json.loads(CHECKS.read_text(encoding="utf-8"))
    agent = []
    for i, item in enumerate(checks["items"], 1):
        rec = {"id": f"W{i:02d}"}
        for key in ("item", "title", "url", "opened", "snippet_only", "access_date", "status", "contents",
                    "access_route", "reuse_terms", "metadata_it_would_add", "notes"):
            if key in item:
                rec[key] = item[key]
        if item.get("witness_path"):
            rec["witness"] = {"path": f"{RAW}/web-checks-v1/{item['witness_path']}",
                              "bytes": item.get("bytes"), "sha256": item.get("sha256")}
        agent.append(rec)
    out = {
        "package": "experiments/2026-10-12-data-inventory",
        "access_date_local": "2026-10-12",
        "retrieval_window_utc": "2026-10-13T03:25Z to 2026-10-13T03:59Z (late on 12 October local time, UTC-4)",
        "definitions": {
            "opened": "The page or API response was fetched and read.",
            "snippet_only": "The entry's main facts rest on search-result snippets. Entries with both flags true combine an opened check (often a negative search or catalogue record) with snippet-derived main facts; such details are marked as snippets in the text.",
        },
        "scope": "Web sources consulted on 12 October 2026 to check unheld or recent data sources. Earlier packages' source records are cited separately in knowledge/DATA.md. Saved witnesses are local-only; their manifest is data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/manifest.jsonl.",
        "agent_check_note": checks.get("note"),
        "direct_checks": DIRECT,
        "web_checks": agent,
        "counts": {"direct": len(DIRECT), "web_checks": len(agent),
                   "web_checks_opened": sum(1 for a in agent if a.get("opened")),
                   "web_checks_snippet_only": sum(1 for a in agent if a.get("snippet_only"))},
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out["counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
