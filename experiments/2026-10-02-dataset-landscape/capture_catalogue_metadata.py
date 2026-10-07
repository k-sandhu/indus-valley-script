"""Capture public discovery metadata without acquiring a new inscription corpus.

Responses stay below data/raw and are excluded from Git. Run against a new
output directory to preserve each discovery endpoint. No account is used.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import argparse
import json


ROOT = Path(__file__).resolve().parents[2]
QUERIES = ["indus-script", "indus-valley", "indus script", "harappa", "p316-p147"]
KNOWN_DATASETS = [
    "hellosindh/indus-script-synthetic",
    "Zer0pa/Indus-Valley-lane-state",
    "junafinity/p316-p147-p217-indus-branch-audit-20260609",
]
REPOSITORIES = [
    "mayig/indus-valley-script-corpus",
    "yajnadevam/lipi",
    "field-cady/indus_valley_script_corpus",
    "jocchanon-prog/induscorpus",
    "premkumar2306/open-indus-lab",
    "HimanshuAttri/IndusValleyScriptDataset",
    "tpsatish95/indus-script-ocr",
]


def acquire(item, destination):
    name, url = item
    record = {
        "id": name,
        "requested_url": url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "rights_status": "rights-unverified",
        "handling": "local-only discovery metadata or source witness",
    }
    try:
        request = Request(url, headers={"User-Agent": "IndusResearchSourceAudit/0.1"})
        with urlopen(request, timeout=15) as response:
            payload = response.read()
            record.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get("Content-Type"))
        target = destination / (name + ".json")
        target.write_bytes(payload)
        record.update(path=target.relative_to(ROOT).as_posix(),
                      bytes=len(payload), sha256=sha256(payload).hexdigest())
    except HTTPError as error:
        record.update(status=error.code, error=str(error))
    except Exception as error:
        record.update(status=None, error=str(error))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True,
                        help="New directory below data/raw for immutable witnesses")
    args = parser.parse_args()
    destination = (ROOT / args.output).resolve()
    allowed = (ROOT / "data/raw").resolve()
    if not destination.is_relative_to(allowed) or destination == allowed:
        raise ValueError("Output must be a child directory of data/raw")
    destination.mkdir(parents=True, exist_ok=False)
    endpoints = []
    for index, query in enumerate(QUERIES):
        parameters = urlencode({"search": query, "limit": 100, "full": "true"})
        endpoints.append((f"hf-search-{index}",
                          "https://huggingface.co/api/datasets?" + parameters))
    for index, dataset in enumerate(KNOWN_DATASETS):
        endpoints.append((f"hf-dataset-{index}",
                          "https://huggingface.co/api/datasets/" + quote(dataset, safe="/")))
    for index, repository in enumerate(REPOSITORIES):
        endpoints.append((f"github-repository-{index}",
                          "https://api.github.com/repos/" + repository))
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda item: acquire(item, destination), endpoints))
    manifest = {"schema_version": 1, "queries": QUERIES,
                "query_limit": 100, "known_datasets": KNOWN_DATASETS,
                "repositories": REPOSITORIES, "assets": records,
                "limitations": [
                    "Discovery is bounded by query strings and public API indexing.",
                    "Repository or card licenses do not clear every inherited asset.",
                    "No private, gated or missing dataset was inspected internally.",
                ]}
    (destination / "acquisition.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"directory": destination.relative_to(ROOT).as_posix(),
                      "requested": len(records),
                      "successful": sum(r.get("status") == 200 for r in records),
                      "errors": [{"id": r["id"], "status": r["status"],
                                  "error": r.get("error")}
                                 for r in records if r.get("status") != 200]}, indent=2))


if __name__ == "__main__":
    main()
