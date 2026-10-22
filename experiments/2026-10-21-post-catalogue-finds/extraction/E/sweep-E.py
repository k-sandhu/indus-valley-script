"""Index page references, footer labels and site/keyword co-occurrences."""
import argparse
import csv
import json
from pathlib import Path
import re


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("seed", type=Path)
    args = ap.parse_args()
    sid = "iar-1996-97-archive"
    with args.seed.open(encoding="utf-8-sig", newline="") as f:
        sites = {r["site_code"]: [r["site"], *r["aliases"].split("|")] for r in csv.DictReader(f)}
    extra = dict(MSD="Masudpur", MTL="Mitathal", HUL="Hulas", DHL="Dhalewan", ALG="Alamgirpur",
                 CHG="Chandigarh", LHR="Lohari Ragho", BLT="Balathal", JNK="Juna Khatiya",
                 PBM="Pabumath", PTH="Pithad", NGS="Nageshwar", KNW="Kanewal", RNG="Rangpur", PRB="Prabhas Patan")
    for code, name in extra.items():
        sites[code] = [name]
    kws = "seal sealing tablet inscri script sign character letter legend graffit tag impression".split()
    patterns = {k: re.compile(r"(?<![a-z])"+r"[\s\-\u00ad]*".join(k)+r"[a-z]*", re.I) for k in kws}
    site_patterns = {code: [re.compile(r"(?<![a-z0-9])"+r"[\s\-\u00ad\u2010-\u2014]*".join(re.escape(c) for c in re.sub(r"[^a-z0-9]", "", t.lower()))+r"(?![a-z0-9])", re.I) for t in terms if t] for code, terms in sites.items()}
    files = sorted(p for p in (args.raw / "text" / sid).glob("p[0-9][0-9][0-9][0-9].txt")
                   if (args.raw / "processing" / (p.stem+".json")).exists())
    pmap = {}
    page_records = []
    footer_path = args.raw / "footer-labels.json"
    footer_map = json.loads(footer_path.read_text(encoding="utf-8")) if footer_path.exists() else {}
    for path in files:
        n = int(path.stem[1:])
        meta = json.loads((args.raw / "processing" / f"p{n:04d}.json").read_text(encoding="utf-8"))
        bottom = [r for r in meta["edge_numbers"] if r["top"] > 2800]
        label = bottom[-1]["value"] if len(bottom) == 1 else ""
        basis = "footer OCR" if label else "no isolated footer label detected"
        if str(n) in footer_map:
            label = footer_map[str(n)]["printed_page"]
            basis = footer_map[str(n)]["basis"]
        pmap[n] = label
        page_records.append(dict(source_id=sid, pdf_page=n, printed_page=label,
                                 basis=basis))
    write(args.output / "printed-pages-E.csv", page_records, ["source_id", "pdf_page", "printed_page", "basis"])
    (args.raw / "text" / sid / "printed_page_map.json").write_text(json.dumps(pmap, indent=2)+"\n", encoding="utf-8")
    rows = []
    direct = {}
    headings = []
    for path in files:
        n = int(path.stem[1:])
        t = path.read_text(encoding="utf-8")
        counts = {k: len(p.findall(t)) for k, p in patterns.items() if p.search(t)}
        hits = {c: sum(len(p.findall(t)) for p in ps) for c, ps in site_patterns.items()}
        hits = {c: v for c, v in hits.items() if v}
        generic = bool(re.search(r"harappan", t, re.I) and counts)
        # Heading text is inspected separately; this index contains no source prose.
        heading_numbers = re.findall(r"(?m)^\s*(\d{1,3})\.\s+(?:EXCAVATION|EXPLORATION)", t, re.I)
        if generic and any(k in counts for k in ["seal", "inscri", "script"]):
            headings.append(dict(pdf_page=n, heading_numbers=heading_numbers, site_codes=list(hits)))
        if counts and (hits or generic):
            codes = list(hits) or ["GENERIC"]
            direct[n] = codes
            for code in codes:
                rows.append(dict(source_id=sid, pdf_page=n, printed_page=pmap[n], site_code=code,
                                 generic_harappan_hit=int(generic), n_site_terms=hits.get(code, 0),
                                 n_keywords=sum(counts.values()), keyword_classes="|".join(counts), context_only=0))
    # Confirmed entry headings supply the site for continuation-page generic hits.
    heading_sites = {21: "DHV", 31: "GDH", 39: "BLU", 40: "BLU", 108: "KDM"}
    for n, code in heading_sites.items():
        if n not in direct or code in direct[n]:
            continue
        t = (args.raw / "text" / sid / f"p{n:04d}.txt").read_text(encoding="utf-8")
        counts = {k: len(p.findall(t)) for k,p in patterns.items() if p.search(t)}
        direct[n].append(code)
        rows.append(dict(source_id=sid, pdf_page=n, printed_page=pmap[n], site_code=code,
                         generic_harappan_hit=1, n_site_terms=0, n_keywords=sum(counts.values()),
                         keyword_classes="|".join(counts), context_only=0))
    context = set()
    for n, codes in direct.items():
        for neighbor in [n-1, n+1]:
            if neighbor not in pmap:
                continue
            for code in codes:
                if code not in direct.get(neighbor, []) and (neighbor, code) not in context:
                    context.add((neighbor, code))
                    rows.append(dict(source_id=sid, pdf_page=neighbor, printed_page=pmap[neighbor], site_code=code,
                                     generic_harappan_hit=0, n_site_terms=0, n_keywords=0, keyword_classes="", context_only=1))
    fields = "source_id pdf_page printed_page site_code generic_harappan_hit n_site_terms n_keywords keyword_classes context_only".split()
    write(args.output / "candidate-pages-E.csv", sorted(rows, key=lambda r:(r["pdf_page"],r["site_code"])), fields)
    summary = dict(pages_ocr=len(files), direct_pages=sorted(direct), context_pages=sorted({n for n,c in context}),
                   generic_heading_checks=headings, printed_labels_detected=sum(bool(v) for v in pmap.values()),
                   confirmed_heading_assignments=heading_sites)
    (args.output / "sweep-summary-E.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
