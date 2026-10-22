"""Stream the ePSD2 Sumerian glossary out of the Oracc JSON archive.

gloss-sux.json is about 1.9 GB, so the entries array is decoded one object at a
time. For each lemma we keep the citation form (cf), guide word (gw), part of
speech, instance count, the meanings of its senses, its compound parts and the
first spelling forms. The output is a local JSONL table.

    python -I experiments/2026-10-21-rebus-base-rate/code/extract_epsd2.py
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "epsd2" / "epsd2.zip"
OUT = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1" / "epsd2-lemmas.jsonl"
CHUNK = 1 << 22


def entries(stream):
    dec = json.JSONDecoder()
    buf = ""
    started = False
    while True:
        if not started:
            chunk = stream.read(CHUNK)
            if not chunk:
                return
            buf += chunk.decode("utf-8")
            i = buf.find('"entries"')
            if i < 0:
                buf = buf[-64:]
                continue
            j = buf.find("[", i)
            buf = buf[j + 1:]
            started = True
        pos = 0
        while True:
            while pos < len(buf) and buf[pos] in " \r\n\t,":
                pos += 1
            if pos < len(buf) and buf[pos] == "]":
                return
            try:
                obj, end = dec.raw_decode(buf, pos)
            except json.JSONDecodeError:
                break
            yield obj
            pos = end
        buf = buf[pos:]
        chunk = stream.read(CHUNK)
        if not chunk:
            return
        # a multibyte character may be split across chunks
        while True:
            try:
                buf += chunk.decode("utf-8")
                break
            except UnicodeDecodeError:
                more = stream.read(1)
                if not more:
                    raise
                chunk += more


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    keys_seen = set()
    with zipfile.ZipFile(SRC) as z, z.open("epsd2/gloss-sux.json") as f, OUT.open("w", encoding="utf-8") as out:
        for e in entries(f):
            keys_seen.update(e.keys())
            senses = []
            for s in e.get("senses", []) or []:
                senses.append({"mng": s.get("mng"), "icount": s.get("icount"), "pos": s.get("pos")})
            parts = None
            if e.get("compound") or e.get("parts"):
                parts = e.get("compound") or e.get("parts")
            rec = {
                "id": e.get("id"), "headword": e.get("headword"), "cf": e.get("cf"), "gw": e.get("gw"),
                "pos": e.get("pos"), "icount": e.get("icount"), "senses": senses,
                "parts": parts, "n_forms": len(e.get("forms", []) or []),
                "forms": [fm.get("n") for fm in (e.get("forms", []) or [])[:20]],
                "periods": [p.get("n") if isinstance(p, dict) else p for p in (e.get("periods") or [])][:20] if isinstance(e.get("periods"), list) else None,
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(json.dumps({"entries": n, "keys_seen": sorted(keys_seen), "out": str(OUT.relative_to(ROOT)), "sha256": digest}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
