"""Build SOURCES.json: the provenance record of every acquired file and derived table.

Hashes and sizes are recomputed from the files on disk. Retrieval times and URLs
come from the request logs; a page whose log line was lost to concurrent appends
is marked so, and its hash is still taken from disk.

    python experiments/2026-10-21-rebus-base-rate/code/manifest.py OUT_JSON
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate"
SRC = RAW / "sources-v1"

SOURCES = {
    "dedr": {
        "title": "T. Burrow and M. B. Emeneau, A Dravidian Etymological Dictionary, 2nd ed., Oxford: Clarendon Press, 1984; Digital Dictionaries of South Asia edition (data updated February 2021)",
        "url": "https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=N (N = 1..514)",
        "rights_status": "rights-unverified",
        "rights_observed": "DSAL front page (local witness rights/dsal-burrow-index.html): 'Copyright 1984 by Oxford University Press. No part of this publication may be stored, transmitted, retransmitted, lent, or reproduced in any form or medium without the permission of Oxford University Press.'",
        "handling": "local-only; derived tables local-only"},
    "cdial": {
        "title": "R. L. Turner, A Comparative Dictionary of the Indo-Aryan Languages, London: Oxford University Press, 1962-1966, with supplements 1969-1985; Digital Dictionaries of South Asia edition",
        "url": "https://dsal.uchicago.edu/cgi-bin/app/soas_query.py?page=N (N = 1..836)",
        "rights_status": "rights-unverified",
        "rights_observed": "DSAL front page (rights/dsal-soas-index.html): 'Copyright 1962-1985 by Sir Ralph Turner, Dorothy R. Turner, and Executors of the late Sir Ralph Lilley Turner. No part of this publication may be stored, transmitted, retransmitted, lent, or reproduced in any form or medium without the permission of the School of Oriental and African Studies, London University.'",
        "handling": "local-only; derived tables local-only"},
    "tamil-lex": {
        "title": "University of Madras, Tamil Lexicon, 6 vols. and supplement, Madras, 1924-1936; Digital Dictionaries of South Asia edition (data updated September 2023)",
        "url": "https://dsal.uchicago.edu/cgi-bin/app/tamil-lex_query.py?page=N",
        "rights_status": "explicit-license",
        "rights_observed": "DSAL front page (rights/dsal-tamil-lex-index.html): 'This work is licensed under a Creative Commons License', linked to CC BY-NC-ND 2.0.",
        "handling": "local-only (no-derivatives licence); derived compound tables local-only"},
    "epsd2": {
        "title": "electronic Pennsylvania Sumerian Dictionary, 2nd edition (ePSD2), Oracc JSON export epsd2.zip; gloss-sux.json timestamp 2023-01-19",
        "url": "https://oracc.museum.upenn.edu/json/epsd2.zip",
        "rights_status": "explicit-license",
        "rights_observed": "gloss-sux.json and metadata.json: 'This data is released under the CC0 license'.",
        "handling": "archive local (size); derived lemma table local, could be released under CC0"},
    "munda": {
        "title": "Felix Rau, Munda cognate set with proto-Munda reconstructions, Zenodo, 29 August 2019, doi:10.5281/zenodo.3380874",
        "url": "https://zenodo.org/api/records/3380874/files/pMunda_cognate_set_2019-08-29.csv/content",
        "rights_status": "explicit-license", "rights_observed": "Zenodo record licence cc-zero (CC0 1.0).",
        "handling": "local copy; CC0"},
    "backstrom": {
        "title": "Lexibank backstromnorthernpakistan v1.1, CLDF dataset derived from Backstrom and Radloff, Sociolinguistic Survey of Northern Pakistan, vol. 2 (1992)",
        "url": "https://github.com/lexibank/backstromnorthernpakistan/archive/refs/tags/v1.1.zip",
        "rights_status": "explicit-license", "rights_observed": "Repository LICENSE and metadata.json: CC BY 4.0.",
        "handling": "local copy; CC BY 4.0 with attribution"},
    "concepticon": {
        "title": "Concepticon 3.4.0 (concepticon-data, 25 February 2025), concepticon.tsv",
        "url": "https://raw.githubusercontent.com/concepticon/concepticon-data/v3.4.0/concepticondata/concepticon.tsv",
        "rights_status": "explicit-license", "rights_observed": "metadata.json dc:license CC BY 4.0.",
        "handling": "local copy; pool definitions tracked with attribution"},
    "norare": {
        "title": "NoRaRe 1.1, Brysbaert-2014-Concreteness mapping of Brysbaert, Warriner and Kuperman (2014) concreteness ratings to Concepticon",
        "url": "https://raw.githubusercontent.com/concepticon/norare-data/v1.1/datasets/Brysbaert-2014-Concreteness/Brysbaert-2014-Concreteness.tsv",
        "rights_status": "explicit-license", "rights_observed": "Repository LICENSE: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).",
        "handling": "local-only values; tracked pools omit them"},
    "sangam": {
        "title": "Project Madurai Unicode e-texts: Ainkurunuru (0028), Patirruppattu (0038), Purananuru (0057), Porunararruppatai (0063), Cirupanarruppatai (0064), Tirumurukarruppatai (0067), Perumpanarruppatai (0069), Netunalvatai (0070), Maturaikkanci (0071), Kurincippattu (0073), Pattinappalai (0077), Malaipatukatam (0078), Paripatal (0087), Kuruntokai (0110), Kalittokai (0221), Akananuru (0229), Narrinai (0296)",
        "url": "https://www.projectmadurai.org/pm_etexts/utf8/pmuniNNNN.html",
        "rights_status": "rights-unverified",
        "rights_observed": "HTML comment 'Project Madurai ... Copyright (c) 1998 - 2000 All Rights Reserved'; Project Madurai FAQ permits third-party distribution with the header page kept intact.",
        "handling": "local-only; only token counts are used"},
    "rights": {
        "title": "Rights witnesses: DSAL front pages of the Burrow, Turner and Tamil Lexicon dictionaries and the DSAL dictionary index",
        "url": "https://dsal.uchicago.edu/dictionaries/{burrow,soas,tamil-lex}/", "rights_status": "rights-unverified",
        "rights_observed": "witness pages", "handling": "local-only"},
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_log(source):
    recs = {}
    path = SRC / source / "requests.jsonl"
    bad = 0
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if r.get("local_path"):
                recs[r["local_path"]] = r
    return recs, bad


def main(out):
    out = Path(out)
    if out.exists():
        print("refusing to overwrite", out)
        return 1
    result = {"schema": "rebus-base-rate source manifest v1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "local_root": str(SRC.relative_to(ROOT)).replace("\\", "/"), "sources": {}, "derived": {}}
    for source, meta in SOURCES.items():
        d = SRC / source
        if not d.exists():
            continue
        recs, bad = load_log(source)
        files = sorted(p for p in d.rglob("*") if p.is_file() and p.name != "requests.jsonl" and "extracted" not in p.parts)
        listing, missing_log, mismatch, times, statuses = [], 0, 0, [], {}
        for p in files:
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            r = recs.get(rel)
            h = sha(p)
            if r is None:
                missing_log += 1
            else:
                times.append(r.get("finished_utc"))
                statuses[str(r.get("status"))] = statuses.get(str(r.get("status")), 0) + 1
                if r.get("sha256") and r["sha256"] != h:
                    mismatch += 1
            listing.append(f"{p.name}:{h}")
        digest = hashlib.sha256("\n".join(listing).encode()).hexdigest()
        entry = dict(meta)
        entry.update({"files": len(files), "bytes": sum(p.stat().st_size for p in files),
                      "files_digest_sha256": digest, "digest_rule": "SHA-256 of sorted 'name:sha256' lines",
                      "http_status_counts": statuses, "files_without_log_record": missing_log,
                      "log_hash_mismatches": mismatch,
                      "unparseable_log_lines": bad,
                      "retrieved_utc_first": min(t for t in times if t) if times else None,
                      "retrieved_utc_last": max(t for t in times if t) if times else None})
        if len(files) <= 30:
            entry["file_hashes"] = {str(p.relative_to(SRC)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in files}
        result["sources"][source] = entry
    for p in sorted((RAW / "derived-v1").glob("*")):
        result["derived"][p.name] = {"bytes": p.stat().st_size, "sha256": sha(p)}
    failed = RAW / "failed-v1"
    if failed.exists():
        result["failed_requests"] = {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(failed.glob("*"))}
        result["failed_requests_note"] = ("First attempts at the Concepticon LICENSE path and the NoRaRe "
                                          "Brysbaert-2014a dataset name returned HTTP 404; the files were fetched "
                                          "from metadata.json and the Brysbaert-2014-Concreteness path instead.")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v["files"], v["files_without_log_record"]) for k, v in result["sources"].items()}))

    # entries proposed for data/MANIFEST.json, in its existing fields
    proposal = []
    kinds = {"dedr": "comparative-corpus", "cdial": "comparative-corpus", "tamil-lex": "comparative-corpus",
             "epsd2": "comparative-corpus", "munda": "comparative-corpus", "backstrom": "comparative-corpus",
             "concepticon": "database", "norare": "database", "sangam": "comparative-corpus"}
    licences = {"tamil-lex": "CC BY-NC-ND 2.0", "epsd2": "CC0 1.0", "munda": "CC0 1.0", "backstrom": "CC BY 4.0",
                "concepticon": "CC BY 4.0", "norare": "CC BY-NC 4.0"}
    for source, e in result["sources"].items():
        if source == "rights":
            continue
        proposal.append({
            "id": f"rebus-{source}", "title": e["title"], "kind": kinds[source], "status": "held",
            "location": "local-only", "local_paths": [f"{result['local_root']}/{source}/"],
            "rights": {"status": e["rights_status"], "licence": licences.get(source), "detail": e["rights_observed"]},
            "fetch": {"method": "http", "url": e["url"],
                      "script": "experiments/2026-10-21-rebus-base-rate/code/acquire.py"},
            "hashes": {"files_digest_sha256": e["files_digest_sha256"], "digest_rule": e["digest_rule"]},
            "size": {"files": e["files"], "bytes": e["bytes"]},
            "notes": e["handling"] + "; acquired for experiments/2026-10-21-rebus-base-rate",
        })
    target = out.parent / "MANIFEST-PROPOSAL.json"
    if not target.exists():
        target.write_text(json.dumps({"proposed_for": "data/MANIFEST.json sources", "entries": proposal},
                                     ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
