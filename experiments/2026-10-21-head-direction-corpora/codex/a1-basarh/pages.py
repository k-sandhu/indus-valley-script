"""Index or render a downloaded PDF without executing its contents.

Commands:
  python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/pages.py index --pdf <scan> --out <local text JSON>
  python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/pages.py render --pdf <scan> --pages 1,5-9 --out <owned pages directory> --scan <identifier>
All PDF page numbers are one-based. Rendered PNG files have 300 dpi resolution.
"""
import argparse
import datetime
import hashlib
import json
import site
import sys
from pathlib import Path

sys.path.append(site.getusersitepackages())
import fitz


def numbers(spec):
    result = set()
    for part in spec.split(","):
        if "-" in part:
            first, last = map(int, part.split("-"))
            result.update(range(first, last + 1))
        else:
            result.add(int(part))
    return sorted(result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("index", "render"))
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pages")
    ap.add_argument("--scan")
    args = ap.parse_args()
    with fitz.open(args.pdf) as doc:
        if args.mode == "index":
            args.out.parent.mkdir(parents=True, exist_ok=True)
            data = {"scan": args.pdf.as_posix(), "pages": doc.page_count,
                    "page_text": [{"page_pdf": i + 1, "text": page.get_text()} for i, page in enumerate(doc)]}
            args.out.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
            print(json.dumps({"pages": doc.page_count, "text_pages": sum(bool(p["text"].strip()) for p in data["page_text"])}))
            return
        args.out.mkdir(parents=True, exist_ok=True)
        journal = args.out / (args.scan + "-render-log.jsonl")
        for number in numbers(args.pages):
            if number < 1 or number > doc.page_count:
                raise ValueError(number)
            target = args.out / (args.scan + "-p" + str(number).zfill(4) + ".png")
            if target.exists():
                print("exists " + target.name)
                continue
            pix = doc[number - 1].get_pixmap(dpi=300, alpha=False)
            pix.save(target)
            rec = {"scan": args.scan, "pdf": args.pdf.as_posix(), "page_pdf": number,
                   "dpi": 300, "width": pix.width, "height": pix.height,
                   "png": target.as_posix(), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                   "rendered_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            with journal.open("a", encoding="utf-8") as out:
                out.write(json.dumps(rec) + "\n")
            print(json.dumps({k: rec[k] for k in ("scan", "page_pdf", "width", "height")}), flush=True)


if __name__ == "__main__":
    main()
