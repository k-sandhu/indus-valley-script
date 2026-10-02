"""Retrieve accession notices locally and retain hashes without acquiring images."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import json


ROOT = Path(__file__).resolve().parent
TARGETS = (
    ("https://collections.louvre.fr/ark:/53355/cl010175973.json", "Louvre-SB1940.txt"),
    ("https://collections.louvre.fr/ark:/53355/cl010175973", "Louvre-SB1940.html"),
    ("https://essentiels.bnf.fr/fr/image/2a59ae81-76d6-4921-b648-c21a8ae51c7e-bulle-enveloppe-scellee-et-calculi", "BnF-SB1940.html"),
)


def main():
    output = ROOT / "source-acquisition.json"
    if output.exists():
        raise FileExistsError(output)
    sources = ROOT / "sources"
    sources.mkdir(exist_ok=True)
    records = []
    for url, name in TARGETS:
        destination = sources / name
        if destination.exists():
            raise FileExistsError(destination)
        record = {"url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                  "rights_status": "rights-unverified", "handling": "local-only",
                  "image_acquisition": "none"}
        try:
            with urlopen(Request(url, headers={"User-Agent": "Indus research source witness"}), timeout=30) as response:
                payload = response.read()
                destination.write_bytes(payload)
                record.update(resolved_url=response.url, http_status=response.status,
                              content_type=response.headers.get("Content-Type"),
                              local_path=destination.relative_to(Path.cwd()).as_posix(),
                              bytes=len(payload), sha256=sha256(payload).hexdigest())
                if name.endswith(".txt"):
                    notice = json.loads(payload)
                    record["notice_modified"] = notice.get("modified ")
                    record["image_rights_notices"] = sorted({item.get("copyright", "") for item in notice["image"]})
        except Exception as error:
            record.update(status="retrieval-failed", error_type=type(error).__name__, error=str(error),
                          alternative_observation="Web search reader returned an accession-linked BnF caption; full-page reader returned HTTP 403.")
        records.append(record)
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: v for k, v in record.items() if k != "image_rights_notices"} for record in records], indent=2))


if __name__ == "__main__":
    main()
