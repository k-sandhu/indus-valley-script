"""Acquire bounded source witnesses locally into a fresh dated directory."""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import urllib.request
import urllib.error

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/memory"
TARGETS = [
    ("satapatha-flood-original.html", "https://original.sacred-texts.com/hin/sbr/sbe12/sbe1230.htm"),
    ("satapatha-flood.html", "https://sacred-texts.com/hin/sbr/sbe12/sbe1230.htm"),
    ("rigveda7-gretil.html", "https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/1_sam/1_rv/rv_hn07u.htm"),
    ("rigveda7-texas.html", "https://lrc.la.utexas.edu/books/rigveda/RV07"),
    ("rigveda10-texas.html", "https://lrc.la.utexas.edu/books/rigveda/RV10"),
    ("rigveda7-95-griffith.html", "https://sacred-texts.com/hin/rigveda/rv07095.htm"),
    ("rigveda10-75-griffith.html", "https://sacred-texts.com/hin/rigveda/rv10075.htm"),
    ("dn27-en.json", "https://raw.githubusercontent.com/suttacentral/bilara-data/published/translation/en/sujato/sutta/dn/dn27_translation-en-sujato.json"),
    ("dn27-pli.json", "https://raw.githubusercontent.com/suttacentral/bilara-data/published/root/pli/ms/sutta/dn/dn27_root-pli-ms.json"),
    ("singh2017.html", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5705636/"),
    ("chatterjee2019.html", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6868222/"),
    ("giosan2012-author-summary.html", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3387054/"),
    ("giosan2012.pdf", "https://landscapepartnership.org/maps-data/climate-context/cc-resources/ClimateSciPDFs/PNASGiosanetalsmall.pdf/app-download-file/file/PNASGiosanetalsmall.pdf"),
    ("witzel1997.pdf", "https://fid4sa-repository.ub.uni-heidelberg.de/110/1/VedicCanon_1997.pdf"),
    ("thomson2009.pdf", "https://rigveda.co.uk/asut1.pdf"),
    ("dave2019-record.html", "https://research.monash.edu/en/publications/revisiting-the-contemporaneity-of-a-mighty-river-and-the-harappan/"),
    ("vendidad2-attempt.html", "https://www.avesta.org/vendidad/vd2sbe.htm"),
]


def fetch(target, out):
    name, url = target
    record = {"name": name, "requested_url": url,
              "retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "rights_status": "unreviewed at acquisition; local-only",
              "method": "urllib HTTPS GET; bounded 25 MB; source code and pages not executed"}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Indus-source-review"})
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = response.read(25_000_001)
            record.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get("Content-Type", ""))
        if len(payload) > 25_000_000:
            raise ValueError("source response exceeded 25 MB bound")
        (out / name).write_bytes(payload)
        record.update(path=(out/name).relative_to(ROOT).as_posix(), bytes=len(payload),
                      sha256=hashlib.sha256(payload).hexdigest(), success=True)
    except Exception as exc:
        record.update(success=False, error_type=type(exc).__name__, error=str(exc))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="acquisition-v1")
    args = parser.parse_args()
    if Path(args.out).name != args.out:
        raise ValueError("Use one fresh directory name")
    out = RAW / args.out
    out.mkdir(parents=True, exist_ok=False)
    with ThreadPoolExecutor(max_workers=6) as executor:
        records = list(executor.map(lambda target: fetch(target, out), TARGETS))
    (out/"acquisition.json").write_text(json.dumps(records, indent=2)+"\n", encoding="utf-8")
    for record in records:
        print(record["name"], "received" if record["success"] else "failed", record.get("bytes", record.get("error_type")), flush=True)


if __name__ == "__main__":
    main()
