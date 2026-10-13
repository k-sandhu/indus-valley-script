"""Verify local witness integrity and locator hooks, not historical interpretations."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import hashlib
import json
import logging
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/coordinator/sources-v1"

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, value):
        self.parts.append(value)

def html_text(path: Path) -> str:
    data = path.read_bytes()
    encoding = "utf-8" if b"utf-8" in data[:3000].lower() else "latin-1"
    parser = Text()
    parser.feed(data.decode(encoding, errors="replace"))
    return re.sub(r"\s+", " ", " ".join(parser.parts))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Output exists; preserve it and use a fresh path.")
    checks = []
    def check(name: str, ok: bool, scope: str = "documentary integrity or locator hook"):
        checks.append({"name": name, "pass": bool(ok), "scope": scope})
    acquisitions = json.loads((RAW / "acquisition.json").read_text(encoding="utf-8"))
    ids = {r["id"]: r for r in acquisitions}
    check("five acquired witness IDs are unique", len(ids) == len(acquisitions) == 5)
    for r in acquisitions:
        p = ROOT / r["path"]
        check(r["id"] + " successful HTTP acquisition", r.get("status") == 200)
        check(r["id"] + " bytes match recorded length", p.stat().st_size == r["bytes"])
        check(r["id"] + " SHA256 matches recorded bytes",
              hashlib.sha256(p.read_bytes()).hexdigest() == r["sha256"])
        if p.suffix == ".pdf":
            check(r["id"] + " PDF signature", p.read_bytes().startswith(b"%PDF"))
    bibliography = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))["sources"]
    obs = json.loads((HERE / "observations.json").read_text(encoding="utf-8"))["observations"]
    bib_ids = {s["id"] for s in bibliography}
    check("twelve observation IDs are unique", len({o["id"] for o in obs}) == len(obs) == 12)
    check("all observation sources and locators resolve",
          all(o["source"] in bib_ids and o["locator"] for o in obs))
    check("overlapping JB PDFs treated as one source",
          len([s for s in bibliography if s["id"] == "JB2014"]) == 1
          and len(next(s for s in bibliography if s["id"] == "JB2014")["witness_ids"]) == 2)
    gretil = html_text(ROOT / ids["SB11-GRETIL"]["path"])
    for n in range(1, 18):
        check(f"GRETIL SB11.5.1.{n} locator present", f"11.5.1.[{n}]" in gretil)
    check("GRETIL mechanically added numbering disclosed", "mechanically" in gretil)
    check("GRETIL reference-only scope disclosed", "REFERENCE PURPOSES ONLY" in gretil)
    eggeling = html_text(ROOT / ids["SB11-EGGELING"]["path"])
    for n in range(1, 18):
        check(f"Eggeling SB11.5.1.{n} locator present", f"11:5:1:{n}" in eggeling)
    rv = html_text(ROOT / ids["RV1095-UNIVERSITY"]["path"])
    check("RV10.95.1 locus present", "10.95.1" in rv)
    check("RV10.95.2–5 loci present", all(f"10.095.0{n}" in rv for n in range(2, 6)))
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    from pypdf import PdfReader
    intro1 = PdfReader(ROOT / ids["JB2014-INTRO-1"]["path"])
    intro2 = PdfReader(ROOT / ids["JB2014-INTRO-2"]["path"])
    check("first excerpt has 15 PDF pages", len(intro1.pages) == 15)
    check("second excerpt has 10 PDF pages", len(intro2.pages) == 10)
    p5 = intro1.pages[4].extract_text()
    p18 = intro2.pages[5].extract_text()
    check("printedp5 date hooks present", "1400" in p5 and "1000" in p5)
    check("printedp18 primary loci and author assessment hooks present",
          "XI.5.1" in p18 and "X.95" in p18 and "distorts" in p18)
    result = {"scope": "Hash, metadata, source dependency and locator checks. Passing hooks do not automate philological interpretation or establish historical continuity.",
              "pass": sum(c["pass"] for c in checks), "fail": sum(not c["pass"] for c in checks),
              "checks": checks,
              "observation_sha256": hashlib.sha256((HERE / "observations.json").read_bytes()).hexdigest(),
              "bibliography_sha256": hashlib.sha256((HERE / "sources.json").read_bytes()).hexdigest()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "fail": result["fail"]}))
    if result["fail"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
