"""Encoding-damage scan for the package under review (read-only).

Run from the repository root:
    python experiments/2026-10-06-field-recommendations/review/encoding_scan.py

For each text file in the package directory (and the HEAD snapshot copies kept in the
local raw directory) it reports: BOM, strict UTF-8 decodability, mojibake sequences
(UTF-8 bytes read as Windows-1252, e.g. U+00E2 U+20AC), U+FFFD, and question marks that
replace a typographic character (curly apostrophe or quotation mark, en dash, accented
letter). Question marks inside URLs are ignored.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments" / "2026-10-06-field-recommendations"
TMP = ROOT / "data" / "raw" / "2026-10-06-field-recommendations" / "tmp"
OUT = PKG / "review" / "encoding-scan.json"

URL = re.compile(r"https?://[^\s\"'<>)\],]+")
MOJIBAKE = re.compile(
    "â[\u0080-¿€‚“”‘’•–—˜™ŠœŸŽšž]"
    "|Ã[\u0080-¿€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ]"
    "|Â[ -¿]")
# a "?" that replaced a character: letter?letter, digit?digit, ?word (opening quote), word?punct (closing quote)
QMARK_PATTERNS = [
    ("apostrophe-or-accent (letter?letter)", re.compile(r"(?<=[A-Za-z])\?(?=[A-Za-z])")),
    ("en dash (digit?digit)", re.compile(r"(?<=\d)\?(?=\d)")),
    ("en dash (letter?Letter, e.g. Indus?Oman)", re.compile(r"(?<=[a-z])\?(?=[A-Z])")),
    ("opening quote (?word)", re.compile(r"(?<![\w?])\?(?=[a-z])")),
    ("closing quote (,?)", re.compile(r"(?<=[,.])\?(?=\s|$)")),
]

def mask_urls(line):
    return URL.sub(lambda m: "\x00" * len(m.group(0)), line)

def scan_text(text):
    hits = {"mojibake": [], "replacement_char": []}
    for name, _ in QMARK_PATTERNS:
        hits[name] = []
    for lineno, raw_line in enumerate(text.splitlines(), 1):
        line = mask_urls(raw_line)
        for m in MOJIBAKE.finditer(line):
            hits["mojibake"].append({"line": lineno, "match": m.group(0), "context": raw_line[max(0, m.start() - 30):m.end() + 30]})
        seen_positions = set()
        for name, pat in QMARK_PATTERNS:
            for m in pat.finditer(line):
                if (lineno, m.start()) in seen_positions:   # a "?" matching two patterns counts once
                    continue
                seen_positions.add((lineno, m.start()))
                hits[name].append({"line": lineno, "context": raw_line[max(0, m.start() - 30):m.end() + 30]})
        if "\ufffd" in line:
            hits["replacement_char"].append({"line": lineno, "context": raw_line[:80]})
    return hits

def analyse(path):
    raw = path.read_bytes()
    info = {"file": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": len(raw), "bom": raw.startswith(b"\xef\xbb\xbf")}
    try:
        text = raw.decode("utf-8-sig")
        info["utf8_ok"] = True
    except UnicodeDecodeError as e:
        text = raw.decode("utf-8", errors="replace")
        info["utf8_ok"] = False
        info["utf8_error"] = str(e)
    info["non_ascii_chars"] = sum(1 for c in text if ord(c) > 127)
    hits = scan_text(text)
    info["counts"] = {k: len(v) for k, v in hits.items()}
    info["total_damaged"] = sum(info["counts"].values())
    info["examples"] = hits
    return info

def main():
    targets = sorted(p for p in PKG.iterdir() if p.is_file() and p.suffix.lower() in {".md", ".json", ".csv", ".py", ".txt"})
    if TMP.exists():
        targets += sorted(p for p in TMP.iterdir() if p.is_file() and ".HEAD." in p.name)
    results = [analyse(p) for p in targets]
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{'file':80s} {'BOM':>5s} {'nonASCII':>8s} {'damaged':>8s}")
    for r in results:
        print(f"{r['file']:80s} {str(r['bom']):>5s} {r['non_ascii_chars']:>8d} {r['total_damaged']:>8d}")
    print()
    for r in results:
        if r["total_damaged"]:
            print("==", r["file"], r["counts"])
            for k, v in r["examples"].items():
                for ex in v[:40]:
                    print(f"   [{k}] line {ex['line']:>4d}: ...{ex['context']}...")

if __name__ == "__main__":
    sys.exit(main())
