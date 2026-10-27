"""Record bounded checks of acquired primary pages, preserving source bytes."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
RAW = Path("D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/living-towns")
LOGICAL = "data/raw/2026-10-26-indus-living-atlas/living-towns"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = HERE / "witness-inspection-v1.json"
    if out.exists():
        raise SystemExit("Refusing to overwrite witness-inspection-v1.json")
    selections = [
        ("LT-S06", "LT-S06-1.pdf", 31, ["Modern Harappa", "one quarter"], "Printed p. 57: modern town overlies approximately one quarter of the site."),
        ("LT-S07", "LT-S07-1.pdf", 12, ["800 BC", "four to"], "Printed p. xi: older chronology around 800 BCE and proposed earlier revision; source contains a suspect latitude."),
        ("LT-S08", "LT-S08-v2-1.pdf", 42, ["700 to 500", "Period"], "Printed p. 34: earliest Ujjain fortification Period I is dated c. 700–500 BCE."),
        ("LT-S09", "LT-S09-v2-1.pdf", 60, ["sixth century", "fourth century"], "Printed p. 53: Mathura's local Period I dates from sixth to late fourth century BCE."),
        ("LT-S10", "LT-S10-1.pdf", 27, ["600 and 1600", "four"], "Printed p. 22: four Patna City areas show a long sampled-sequence gap."),
        ("LT-S11", "LT-S11-v2-1.pdf", 18, ["245", "5730"], "Rajgir result printed using 5730-year half-life; retained without calendar conversion."),
        ("LT-S18", "LT-S18-1.pdf", 177, ["8th century BCE", "timber"], "Printed p. 134: earliest timber occupation at Tilaurakot; later urban form distinguished."),
    ]
    checks = []
    for sid, name, page, needles, observation in selections:
        source = RAW / name
        doc = fitz.open(source)
        text = doc[page - 1].get_text()
        target = RAW / f"{sid}-page-{page}-text.txt"
        if not target.exists():
            target.write_text(text, encoding="utf-8")
        checks.append(dict(source_id=sid, source_logical_path=f"{LOGICAL}/{name}", source_physical_path=source.as_posix(),
                           source_sha256=sha(source), pdf_page_1_based=page, observation=observation,
                           extraction="PyMuPDF Page.get_text; no source bytes altered", checked_fragments=needles,
                           fragments_present=all(n in text for n in needles),
                           local_text=dict(logical_path=f"{LOGICAL}/{target.name}", physical_path=target.as_posix(), sha256=sha(target), bytes=target.stat().st_size)))
    rendered = []
    parent = RAW / "LT-S19-1.pdf"
    for p in [1, 4, 5, 6, 7]:
        path = RAW / f"LT-S19-page-{p}.png"
        rendered.append(dict(logical_path=f"{LOGICAL}/{path.name}", physical_path=path.as_posix(), bytes=path.stat().st_size,
                             sha256=sha(path), parent_sha256=sha(parent), pdf_page_1_based=p,
                             transform="PyMuPDF render at 1.4 scale for pages 1/6 and 1.5 for pages 4/5/7; PNG; local-only",
                             visually_inspected=True))
    result = dict(schema_version="1.0", created_at=datetime.now(timezone.utc).isoformat(),
                  observer="GPT-6, Codex API workspace; not an independent second reader", checks=checks,
                  visual_record=dict(source_id="LT-S19", source_sha256=sha(parent),
                                     pages=rendered, observation="Title and authors on p. 73 checked. Printed p. 79 dates ASW2 Period K to 840–460 BCE and separately cites hunter-gatherer occupation on the broader mound c. 4000 BCE; no intervening settled sequence inferred."),
                  metadata_corrections=["IAR 1955–56 local copy: original 1956, reprint 1993, both printed on copyright page.",
                                        "IAR 1962–63 original title/copyright pages: 1965; Zenodo's 1963 publication metadata is not adopted.",
                                        "IAR 1975–76 original title/copyright pages: 1979.",
                                        "Garcia-Molsosa, Orengo and Petrie author order verified in ICAC's institutional bibliography."],
                  unresolved_access=["IGNCA Ropar and Srinagar PDFs failed legacy TLS renegotiation; search-indexed primary text only.",
                                     "DOI responses for LT-S03 and LT-S15 were redirect/login HTML; LT-S15 abstract and metadata were read at the institutional repository."])
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(primary_page_checks=len(checks), fragment_checks_passed=sum(c["fragments_present"] for c in checks), local_renders=len(rendered))))


if __name__ == "__main__":
    main()
