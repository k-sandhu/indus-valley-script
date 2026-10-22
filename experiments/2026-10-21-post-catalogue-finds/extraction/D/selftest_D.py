"""Validate part D tables, source locations, retained text and output content."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path

FIELDS="row_id site_code site site_as_published country baseline_volume baseline_year excavation season registration other_numbers findspot depth_or_layer period_or_phase object_type object_subtype material primary_publication publication_year page pdf_page plate_or_figure photo_published drawing_published transcription_published other_publications row_basis inscription_status catalogue_status excavated_before_baseline possible_duplicate_of extraction_note extracted_by".split()


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        header=reader.fieldnames
        data=list(reader)
    return header,data


def normal(text):
    return " ".join(text.split())


def main():
    ap=argparse.ArgumentParser()
    for value in ["out","raw","text1","text2","register1","register2","protocol","protocol-hash"]:
        ap.add_argument("--"+value,required=True)
    args=ap.parse_args()
    out=Path(args.out)
    failures=[]
    checks={}
    def check(name,value,detail=None):
        checks[name]=bool(value)
        if not value:
            failures.append({"check":name,"detail":detail})
    header,objects=read_csv(out/"objects-D.csv")
    check("exact_columns",header==FIELDS and all(None not in r and None not in r.values() for r in objects))
    controlled={
        "object_type":{"seal","sealing","tablet","tag","inscribed-pottery","inscribed-tool","other","uncertain"},
        "row_basis":{"individual","enumerated-count"},
        "inscription_status":{"stated","uncertain"},
        "catalogue_status":{"post-catalogue","possibly-in-cisi3","in-baseline-catalogue"},
        "excavated_before_baseline":{"yes","no","unknown"},
        "photo_published":{"yes","no","unknown"},"drawing_published":{"yes","no","unknown"},
        "transcription_published":{"yes","no","unknown"},
    }
    check("controlled_values",all(r[k] in allowed for r in objects for k,allowed in controlled.items()))
    check("row_identifiers",[r["row_id"] for r in objects]==[f"XD-DHV-{i:03d}" for i in range(1,len(objects)+1)])
    ids={r["row_id"] for r in objects}
    check("duplicate_links",all(not r["possible_duplicate_of"] or r["possible_duplicate_of"] in ids and r["possible_duplicate_of"]!=r["row_id"] for r in objects))
    check("site_baseline_and_authorship",all(r["site_code"]=="DHV" and r["site"]=="Dholavira" and
          r["country"]=="India" and r["baseline_volume"]=="CISI 1" and r["baseline_year"]=="1987" and
          r["extracted_by"]=="codex gpt-6.1-sol run 2D" for r in objects))
    registers=read_csv(args.register1)[1]+read_csv(args.register2)[1]
    sources={r["source_id"] for r in registers}
    check("primary_source_ids",all(r["primary_publication"] in sources for r in objects))
    refs=[part.strip() for r in objects for part in r["other_publications"].split(";") if part.strip()]
    check("secondary_source_ids",all(":" in ref and ref.split(":",1)[0] in sources for ref in refs))
    text_roots=[Path(args.text1),Path(args.text2)]
    def page_path(source,number):
        if not str(number).isdigit():
            return None
        return next((root/source/f"p{int(number):04d}.txt" for root in text_roots
                     if (root/source/f"p{int(number):04d}.txt").is_file()),None)
    check("primary_page_files",all(page_path(r["primary_publication"],r["pdf_page"]) for r in objects))
    check("nonempty_locators",all(r["primary_publication"] and any(r[k].strip() for k in ["page","pdf_page","plate_or_figure"]) for r in objects))
    site_notes=read_csv(out/"site-notes-D.csv")[1]
    check("one_site_note",len(site_notes)==1 and site_notes[0]["site_code"]=="DHV")
    site=site_notes[0]
    check("site_counts",int(site["rows_individual"])==sum(r["row_basis"]=="individual" for r in objects) and
          int(site["rows_enumerated"])==sum(r["row_basis"]=="enumerated-count" for r in objects) and
          int(site["rows_uncertain_status"])==sum(r["inscription_status"]=="uncertain" for r in objects) and
          int(site["rows_possibly_in_cisi3"])==sum(r["catalogue_status"]=="possibly-in-cisi3" for r in objects))
    ledger=read_csv(out/"pages-read-D.csv")[1]
    check("logged_pages_exist",all(r["source_id"] in sources and page_path(r["source_id"],r["pdf_page"]) for r in ledger))
    check("page_log_values",all(r["purpose"] in {"candidate","context","plate","table"} and r["image_viewed"] in {"yes","no"} for r in ledger))
    check("whole_inscription_range_logged",set(range(245,351))<={int(r["pdf_page"]) for r in ledger if r["source_id"]=="bisht-2015-held"})
    merges=read_csv(out/"merge-log-D.csv")[1]
    check("merge_log_references",all(r["kept_row_id"] in ids and r["merged_source"] in sources and r["merged_page"] and r["basis"] for r in merges))
    retained_errors=[]
    for directory in [out,Path(args.raw)]:
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            try:
                if path.suffix==".json":
                    json.loads(path.read_text(encoding="utf-8-sig"))
                elif path.suffix==".xml":
                    ET.fromstring(path.read_bytes())
                elif path.suffix==".csv":
                    cols,data=read_csv(path)
                    assert cols and all(None not in r and None not in r.values() for r in data)
                elif path.suffix==".py":
                    compile(path.read_text(encoding="utf-8-sig"),str(path),"exec")
            except Exception as error:
                retained_errors.append({"path":str(path),"error":type(error).__name__})
    check("retained_files_parse",not retained_errors,retained_errors)
    expected_hash=Path(args.protocol_hash).read_text().split()[0].lower()
    actual_hash=hashlib.sha256(Path(args.protocol).read_bytes()).hexdigest()
    check("frozen_protocol_hash",actual_hash==expected_hash)

    # Re-extract to memory and compare every retained page after whitespace normalization.
    source_by={r["source_id"]:r for r in registers}
    transformations=[]
    mismatch=[]
    for directory in sorted((Path(args.raw)/"text").iterdir()):
        if not directory.is_dir() or directory.name not in source_by:
            continue
        source=source_by[directory.name]
        pdf=Path(source["local_path"])
        result=subprocess.run(["pdftotext","-layout","-enc","UTF-8",str(pdf),"-"],capture_output=True,check=True)
        pages=result.stdout.decode("utf-8",errors="replace").split("\f")
        if not pages[-1].strip():
            pages.pop()
        files=list(directory.glob("p*.txt"))
        good=len(files)==len(pages)
        blank_source=[]
        for n,expected in enumerate(pages,1):
            path=directory/f"p{n:04d}.txt"
            if not path.exists() or normal(path.read_text(encoding="utf-8-sig",errors="replace"))!=normal(expected):
                mismatch.append({"source_id":directory.name,"pdf_page":n})
                good=False
            if not expected.strip():
                blank_source.append(n)
        digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
        check("source_hash_"+directory.name,digest==source["sha256"])
        transformations.append({"source_id":directory.name,"input_path":str(pdf),"input_sha256":digest,
                                "page_count":len(pages),"page_text_directory":str(directory),
                                "all_retained_pages_match":good,"blank_source_pages":blank_source,
                                "method":"pdftotext -layout -enc UTF-8; whitespace-normalized replay"})
    check("all_retained_page_text_replays",not mismatch and all(x["all_retained_pages_match"] for x in transformations),mismatch)
    (out/"text-extraction-manifest-D.json").write_text(json.dumps(transformations,indent=2)+"\n",encoding="utf-8")
    # The encoded vocabulary keeps this validator subject to the same output scan.
    encoded="756e69636f726e7c62756c6c7c7268696e6f6365726f737c656c657068616e747c74696765727c62756666616c6f7c7a6562757c676f61747c616e74656c6f70657c6d6f7469667c616e696d616c7c7369676e2073657175656e63657c7265616473206173"
    vocabulary=bytes.fromhex(encoded).decode().split("|")
    forbidden=re.compile(r"\b(?:"+"|".join(re.escape(v).replace(r"\ ",r"\s+") for v in vocabulary)+r")\b",re.I)
    unit=re.compile(r"\d+(?:\.\d+)?\s*(?:mm|cm)",re.I)
    violations=[]
    texts={}
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.suffix in {".py",".json",".csv",".md",".txt"}:
            text=path.read_text(encoding="utf-8-sig",errors="replace")
            texts[path]=text
            for pattern,label in [(forbidden,"blocked-token"),(unit,"number-unit")]:
                for match in pattern.finditer(text):
                    violations.append({"path":str(path),"line":text.count("\n",0,match.start())+1,"kind":label})
    check("forbidden_content_absent",not violations,violations)
    token=re.compile(r"\b\w+(?:['’]\w+)?\b",re.U)
    targets=defaultdict(set)
    first=set()
    for path,text in texts.items():
        words=token.findall(text.casefold())
        for i in range(len(words)-12):
            key=tuple(words[i:i+13])
            targets[key].add(str(path))
            first.add(words[i])
    copied=[]
    unique_pages=sorted({(r["source_id"],int(r["pdf_page"])) for r in ledger})
    for source,number in unique_pages:
        path=page_path(source,number)
        words=token.findall(path.read_text(encoding="utf-8-sig",errors="replace").casefold())
        matched=set()
        for i in range(len(words)-12):
            if words[i] not in first:
                continue
            matched.update(targets.get(tuple(words[i:i+13]),()))
        for target in matched:
            copied.append({"path":target,"source_id":source,"pdf_page":number})
    check("no_thirteen_word_source_copy",not copied,copied)
    result={"result":"PASS" if all(checks.values()) else "FAIL","checks":checks,
            "failure_count":len(failures),"failures":failures,"rows":len(objects),
            "site_row_counts":{"DHV":len(objects)},"source_pages_checked_for_copying":len(unique_pages),
            "prospective_tracked_text_files_checked":len(texts),"page_text_sources_replayed":len(transformations),
            "disk_free_bytes":shutil.disk_usage(out.resolve()).free,
            "scope":"Bookkeeping, locators, retained-file integrity and content checks; no local-corpus matching."}
    (out/"selftest-D.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
