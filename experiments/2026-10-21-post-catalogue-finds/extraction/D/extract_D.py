"""Identity-only inspection helpers for part D. Run with isolated Python."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def records(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def save_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def pagespec(value):
    out = []
    for part in value.split(","):
        ends = [int(x) for x in part.split("-")]
        out.extend(range(ends[0], ends[-1] + 1))
    return out


def load_page(args, number, purpose="candidate"):
    path = Path(args.text) / args.source / f"p{number:04d}.txt"
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    log = Path(args.out) / "pages-read-D.csv"
    rows = records(log) if log.exists() else []
    key = (args.source, str(number), purpose)
    if not any((r["source_id"], r["pdf_page"], r["purpose"]) == key for r in rows):
        rows.append(dict(source_id=args.source, pdf_page=number,
                         purpose=purpose, image_viewed="no"))
        save_csv(log, ["source_id", "pdf_page", "purpose", "image_viewed"], rows)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["toc", "ids", "structure", "extract-pdf", "inventory", "seal-table", "entry-meta", "bbox-head", "bbox-table", "bbox-detail"])
    parser.add_argument("--text")
    parser.add_argument("--source")
    parser.add_argument("--pages", default="1")
    parser.add_argument("--out", required=True)
    parser.add_argument("--input")
    parser.add_argument("--save")
    parser.add_argument("--cache")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.mode == "extract-pdf":
        destination = Path(args.text) / args.source
        destination.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", args.input, "-"],
                                check=True, capture_output=True)
        chunks = result.stdout.decode("utf-8", errors="replace").split("\f")
        if not chunks[-1].strip():
            chunks.pop()
        for n, chunk in enumerate(chunks, 1):
            (destination / f"p{n:04d}.txt").write_text(chunk, encoding="utf-8")
        print(json.dumps({"source": args.source, "pages": len(chunks),
                          "sha256": hashlib.sha256(Path(args.input).read_bytes()).hexdigest()}))
        return
    if args.mode == "inventory":
        rows = records(args.input)
        sources = {}
        for row in rows:
            if row["site_code"] == "DHV":
                sources.setdefault(row["source_id"], []).append(int(row["pdf_page"]))
        print(json.dumps(sources))
        return
    if args.mode.startswith("bbox-"):
        collected = []
        for number in pagespec(args.pages):
            load_page(args, number, "table")
            cached = Path(args.cache) / f"p{number:04d}.xml" if args.cache else None
            if cached and cached.exists():
                payload = cached.read_bytes()
            else:
                result = subprocess.run([
                    "C:/Users/sandh/Downloads/poppler-24.07.0/Library/bin/pdftotext.exe",
                    "-f", str(number), "-l", str(number), "-bbox-layout", args.input, "-"],
                    check=True, capture_output=True)
                payload = result.stdout
                if cached:
                    cached.parent.mkdir(parents=True, exist_ok=True)
                    cached.write_bytes(payload)
            root = ET.fromstring(payload)
            words = [{"text": w.text or "", **{k: float(v) for k, v in w.attrib.items()}}
                     for w in root.iter() if w.tag.endswith("word")]
            if args.mode == "bbox-head":
                keep = {"Sl.", "Acc", "Acc.", "No.", "GSQ", "Stratum", "Depth/3DR", "Size:",
                        "Area", "Stage", "Remarks", "Details", "Period", "Photograph"}
                print(json.dumps({"page": number, "headers": [w for w in words if w["text"] in keep]}))
                continue
            if args.mode == "bbox-detail":
                output = []
                for w in words:
                    if 55<=w["xMin"]<150 and re.fullmatch(r"\d+\.?",w["text"]):
                        output.append(w)
                if not args.quiet:
                    print(json.dumps({"page":number,"identifiers":output}))
                continue
            # The selected table's columns are fixed by physical coordinates.
            bounds = [(65,118),(118,200),(200,250),(250,335),(617,677),(677,740)]
            anchors = sorted([w for w in words if 30 <= w["xMin"] < 63 and
                              re.fullmatch(r"\d+\.?", w["text"])], key=lambda w:w["yMin"])
            for i, anchor in enumerate(anchors):
                end = anchors[i+1]["yMin"]-.5 if i+1<len(anchors) else 2000
                block = [w for w in words if anchor["yMin"]-.5 <= w["yMin"] < end]
                cells = []
                for a,b in bounds:
                    cell = sorted([w for w in block if a<=w["xMin"]<b],key=lambda w:(round(w["yMin"],1),w["xMin"]))
                    value = " ".join(w["text"] for w in cell)
                    value = re.sub(r"(?<=\d)\s*(?:c\s*m|m\s*m)", " [unit omitted]", value, flags=re.I)
                    cells.append(value)
                writing = " ".join(w["text"] for w in block if 537<=w["xMin"]<617)
                entry = {"page":number,"catalogue":anchor["text"].rstrip("."),
                         **dict(zip(["registration","gsq","stratum","depth","area","stage"],cells)),
                         "writing_cell_present":bool(writing.strip()),
                         "writing_cell_negative":bool(re.search(r"\bnil\b|\bno\b|\bnone\b|^\s*[-?]+\s*$",writing,re.I)),
                         "writing_status":("yes" if re.search(r"\byes\b",writing,re.I) else
                                           "no" if re.search(r"\bnil\b|\bno\b|\bnone\b",writing,re.I) else
                                           "blank" if not writing.strip() else
                                           "not-stated" if re.fullmatch(r"\s*[-?]+\s*",writing) else "stated"),
                         "writing_condition":[v for v in re.findall(r"[A-Za-z]+",writing)
                                              if v.lower() in {"yes","no","nil","none","not","available","broken","missing","lost","damaged","defaced","illegible","partly","partially","destroyed"}]}
                collected.append(entry)
                if not args.quiet:
                    print(json.dumps(entry))
        if args.save:
            Path(args.save).write_text(json.dumps(collected,indent=2)+"\n",encoding="utf-8")
        return
    for number in pagespec(args.pages):
        text = load_page(args, number, "context" if args.mode == "toc" else "candidate")
        output = {"pdf_page": number}
        if args.mode == "toc":
            output["entries"] = []
            for i, line in enumerate(text.splitlines()):
                if re.search(r"seal|inscrib|tablet|append|graffiti|contents", line, re.I):
                    # Table-of-contents locators only.
                    output["entries"].append({"line": i, "classes": re.findall(
                        r"sealings?|seals?|inscribed|tablets?|graffiti|contents", line, re.I),
                        "locators": re.findall(r"\b\d+(?:\s*[-–]\s*\d+)?\b", line)})
        elif args.mode == "ids":
            output["identifiers"] = []
            for i, line in enumerate(text.splitlines()):
                found = re.findall(r"\b(?:DHR|Dlv|DLV|Dhr)[\s.:/–-]*\d+(?:[/-]\d+)?\b", line)
                if found:
                    output["identifiers"].append({"line": i, "ids": found})
            output["entry_starts"] = [{"line": i, "catalogue": m.group(1)}
                for i, line in enumerate(text.splitlines())
                if (m := re.match(r"^\s*(\d+)\s*[.)]\s+", line))]
        elif args.mode == "seal-table":
            lines = text.splitlines()
            header = next(x for x in lines if "Acc" in x and "GSQ" in x)
            columns = {k: header.index(k) for k in ["GSQ", "Stratum", "Depth", "Size:", "Area", "Stage"]}
            output["rows"] = []
            for i, line in enumerate(lines):
                if not re.match(r"^\s*\d{1,3}\s+\d{2,6}\b", line):
                    continue
                first = line[:columns["Depth"]-1]
                depth = line[columns["Depth"]-1:columns["Size:"]-3]
                area = line[columns["Area"]-1:]
                output["rows"].append({"line": i, "identity": first.strip(),
                                       "context_value": depth.strip(), "area_stage": area.strip()})
        elif args.mode == "entry-meta":
            lines = text.splitlines()
            output["entries"] = []
            for i, line in enumerate(lines):
                match = re.match(r"^\s*(\d{1,3})\s+(\d{2,6})\s+", line)
                if match:
                    output["entries"].append({"line": i, "catalogue": match.group(1),
                                               "registration": match.group(2)})
        else:
            output["lines"] = []
            for i, line in enumerate(text.splitlines()):
                fields = {}
                for label, pattern in {
                    "registration": r"\b(?:DHR|Dlv|DLV|Dhr)[\s.:/–-]*\d+(?:[/-]\d+)?\b",
                    "plate": r"\b(?:Pls?\.?|Plate[s]?|Figs?\.?|Fig\.)\s*[.:]?\s*[IVXLC\d]+(?:[.:/–-][\dA-Za-z]+)*",
                    "season": r"\b(?:19|20)\d{2}\s*[-–]\s*(?:\d{2}|\d{4})\b",
                    "stage": r"\b(?:Stage|Phase|Period)\s*[IVX]+(?:\s*[A-C])?\b",
                    "material": r"\b(?:steatite|terracotta|faience|copper|stone|clay|sandstone)\b",
                }.items():
                    values = re.findall(pattern, line, re.I)
                    if values:
                        fields[label] = values
                if fields:
                    output["lines"].append({"line": i, **fields})
        print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
