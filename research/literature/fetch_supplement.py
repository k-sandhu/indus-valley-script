"""Supplemental primary-source downloads; append the retrieval history."""
from pathlib import Path
import json
import concurrent.futures
from fetch_sources import ROOT, retrieve

SUPPLEMENT = [
    ("tiwari_2026_structure", "2026-07", "published ACL workshop paper", "https://aclanthology.org/2026.nlp4dh-1.28.pdf"),
    ("oakes_2017_2019_tables", "2017 online; 2019 volume", "author manuscript of peer-reviewed paper", "https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download"),
    ("tamkiya_2025_2026_allographs", "2025-11-01 online; 2026 volume", "published Springer conference chapter; abstract only retrieved", "https://link.springer.com/chapter/10.1007/978-3-032-06744-9_19"),
    ("farmer_sproat_witzel_2004_author", "2004", "author copy of peer-reviewed journal essay", "https://safarmer.com/fsw2.pdf"),
    ("mahadevan_parpola_review", "1997-01", "published author research review reproduced at Harappa", "https://www.harappa.com/content/indus-script-0"),
    ("mahadevan_1997_review_full", "1997-01", "published author research review reproduced at Harappa", "https://www.harappa.com/script/maha15.html"),
    ("bhaskar_2024_anisotropy", "2024", "peer-reviewed paper", "https://www.harappa.com/sites/default/files/pdf/MarkersAndAgenciesOfAnisotropy.pdf"),
    ("bose_2026_falsification", "2026-09-09", "unreviewed SSRN preprint; landing page", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7436801"),
    ("indusvalleyscript_2026", "2026", "unreviewed independent project page", "https://indusvalleyscript.com/"),
    ("bose_2026_minimal_pairs_code", "2026; snapshot retrieved October1", "unreviewed independent code; pinned commit cd600349f6d3193a241c3eb87ff80a2a65377efc", "https://raw.githubusercontent.com/joyboseroy/indus_decipher/cd600349f6d3193a241c3eb87ff80a2a65377efc/analysis/minimal_pairs.py"),
    ("bose_2026_functional_class_results", "2026; snapshot retrieved October1", "unreviewed independent results; pinned commit cd600349f6d3193a241c3eb87ff80a2a65377efc", "https://raw.githubusercontent.com/joyboseroy/indus_decipher/cd600349f6d3193a241c3eb87ff80a2a65377efc/experiments/functional_class_signature_results.json"),
    ("bose_2026_substitution_graph_results", "2026; snapshot retrieved October1", "unreviewed independent results; pinned commit cd600349f6d3193a241c3eb87ff80a2a65377efc", "https://raw.githubusercontent.com/joyboseroy/indus_decipher/cd600349f6d3193a241c3eb87ff80a2a65377efc/experiments/substitution_graph_results.json"),
]

if __name__ == "__main__":
    path = ROOT / "source_retrieval_log.json"
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    done = {x["id"] for x in previous if x.get("http_status")==200 and "error" not in x}
    pending = [item for item in SUPPLEMENT if item[0] not in done]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(retrieve, pending))
    path.write_text(json.dumps(previous + records, indent=2), encoding="utf-8")
    for item in records:
        print(item["id"], item.get("http_status"), item.get("pages", "html"), item.get("text_chars", item.get("error")))
