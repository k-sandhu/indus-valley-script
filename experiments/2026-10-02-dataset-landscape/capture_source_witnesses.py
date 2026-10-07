"""Preserve the public pages supporting the dataset comparison, locally."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ("caa2023.pdf", "https://2023.caaconference.org/wp-content/uploads/sites/29/2023/04/abstract_book_v13.pdf"),
    ("icit.html", "https://www.epigraphica.de/indus/menueindus.htm"),
    ("rmrl-irc.html", "https://www.rmrl.in/en/irc"),
    ("helsinki1979.html", "https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/"),
    ("helsinki1982.html", "https://researchportal.helsinki.fi/en/publications/a-concordande-to-the-texts-in-the-indus-script/"),
    ("mayig-LICENSE", "https://raw.githubusercontent.com/mayig/indus-valley-script-corpus/main/LICENSE"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    allowed = (ROOT / "data/raw").resolve()
    if not output.is_relative_to(allowed) or output == allowed:
        raise ValueError("Use a new child directory of data/raw")
    output.mkdir(parents=True, exist_ok=False)
    sources = list(SOURCES)
    discovery = ROOT / "data/raw/2026-10-02-dataset-landscape/discovery-v1"
    for index in range(3):
        data = json.loads((discovery / f"hf-dataset-{index}.json").read_text(encoding="utf-8"))
        sources.append((f"hf-card-{index}.md", "https://huggingface.co/datasets/" +
                        data["id"] + "/raw/" + data["sha"] + "/README.md"))

    def fetch(source):
        filename, url = source
        row = {"url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
               "rights_status": "rights-unverified", "handling": "local-only"}
        try:
            request = Request(url, headers={"User-Agent": "IndusResearchSourceAudit/0.1"})
            with urlopen(request, timeout=15) as response:
                payload = response.read()
                row.update(status=response.status, final_url=response.url,
                           content_type=response.headers.get("Content-Type"))
            target = output / filename
            target.write_bytes(payload)
            row.update(path=target.relative_to(ROOT).as_posix(), bytes=len(payload),
                       sha256=sha256(payload).hexdigest())
        except Exception as error:
            row.update(status=getattr(error, "code", None), error=str(error))
        return row

    with ThreadPoolExecutor(max_workers=4) as pool:
        assets = list(pool.map(fetch, sources))
    (output / "acquisition.json").write_text(
        json.dumps({"schema_version": 1, "assets": assets}, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps({"requested": len(assets),
                      "successful": sum(a.get("status") == 200 for a in assets),
                      "errors": [a for a in assets if a.get("status") != 200]}, indent=2))


if __name__ == "__main__":
    main()
