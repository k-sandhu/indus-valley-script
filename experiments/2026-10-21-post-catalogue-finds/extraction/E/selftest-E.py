"""Validate extraction structure, coverage, provenance and content limits."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re


def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        result=list(reader)
        assert all(None not in r and None not in r.values() for r in result), path.name
        return reader.fieldnames,result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",type=Path)
    ap.add_argument("raw",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("pdf",type=Path)
    args=ap.parse_args()
    failures=[]
    def check(name,ok,**details):
        if not ok:
            failures.append(dict(check=name,**details))
    sid="iar-1996-97-archive"
    expected="row_id site_code site site_as_published country baseline_volume baseline_year excavation season registration other_numbers findspot depth_or_layer period_or_phase object_type object_subtype material primary_publication publication_year page pdf_page plate_or_figure photo_published drawing_published transcription_published other_publications row_basis inscription_status catalogue_status excavated_before_baseline possible_duplicate_of extraction_note extracted_by".split()
    fields,objects=rows(args.output/"objects-E.csv")
    check("object_columns",fields==expected)
    controls=dict(object_type={"seal","sealing","tablet","tag","inscribed-pottery","inscribed-tool","other","uncertain"},
                  row_basis={"individual","enumerated-count"},inscription_status={"stated","uncertain"},
                  catalogue_status={"post-catalogue","possibly-in-cisi3","in-baseline-catalogue"},
                  excavated_before_baseline={"yes","no","unknown"},
                  photo_published={"yes","no","unknown"},drawing_published={"yes","no","unknown"},
                  transcription_published={"yes","no","unknown"})
    ids=[r["row_id"] for r in objects]
    check("unique_row_ids",len(set(ids))==len(ids))
    _,notes=rows(args.output/"site-notes-E.csv")
    note_by_code={r["site_code"]:r for r in notes}
    base=set()
    for p in [args.package/"acquisition"/"source-register-1a.csv",
              args.package/"acquisition-web"/"source-candidates-1b.csv"]:
        _,rs=rows(p)
        base.update(r["source_id"] for r in rs)
    proposals=json.loads((args.package/"acquisition-coordinator"/"manifest-proposals-coordinator.json").read_text(encoding="utf-8"))
    coordinator={r["id"]:r for r in proposals["sources"]}
    _,additions=rows(args.output/"source-register-additions-E.csv")
    additions_by_id={r["source_id"]:r for r in additions}
    all_sources=set(base)|set(additions_by_id)
    missing_base=set()
    for obj in objects:
        for field,values in controls.items():
            check("controlled_value",obj[field] in values,row_id=obj["row_id"],field=field)
        check("row_id_format",bool(re.fullmatch(r"XE-[A-Z]{3}-\d{3}",obj["row_id"])))
        check("site_note_present",obj["site_code"] in note_by_code)
        check("locator",bool(obj["pdf_page"] and (obj["page"] or obj["plate_or_figure"])))
        check("primary_page_exists",(args.raw/"text"/obj["primary_publication"]/f"p{int(obj['pdf_page']):04d}.txt").is_file())
        check("duplicate_reference",not obj["possible_duplicate_of"] or obj["possible_duplicate_of"] in ids)
        referenced=[obj["primary_publication"]]
        for ref in filter(None,obj["other_publications"].split(";")):
            referenced.append(ref.strip().split(":")[0])
        for source in referenced:
            if source not in base:
                missing_base.add(source)
            check("source_id_in_effective_register",source in all_sources,source_id=source)
    shared_register_check=not missing_base
    for source in missing_base:
        check("explicit_assignment_source",source==sid and source in coordinator and source in additions_by_id,source_id=source)
        if source in additions_by_id and source in coordinator:
            check("coordinator_source_hash",additions_by_id[source]["sha256"]==coordinator[source]["fetch"]["sha256"])
    for code,note in note_by_code.items():
        rs=[r for r in objects if r["site_code"]==code]
        for field,actual in dict(rows_individual=sum(r["row_basis"]=="individual" for r in rs),
                                 rows_enumerated=sum(r["row_basis"]=="enumerated-count" for r in rs),
                                 rows_uncertain_status=sum(r["inscription_status"]=="uncertain" for r in rs),
                                 rows_possibly_in_cisi3=sum(r["catalogue_status"]=="possibly-in-cisi3" for r in rs)).items():
            check("site_count",int(note[field])==actual,site_code=code,field=field)
    _,pages_read=rows(args.output/"pages-read-E.csv")
    read_pages={int(r["pdf_page"]) for r in pages_read}
    for r in pages_read:
        check("page_read_exists",(args.raw/"text"/r["source_id"]/f"p{int(r['pdf_page']):04d}.txt").is_file())
        check("page_purpose",r["purpose"] in {"candidate","context","plate","table"})
        check("image_viewed",r["image_viewed"] in {"yes","no"})
    _,candidates=rows(args.output/"candidate-pages-E.csv")
    check("all_candidates_and_neighbours_reviewed",{int(r["pdf_page"]) for r in candidates}<=read_pages)
    pfiles=sorted((args.raw/"text"/sid).glob("p????.txt"))
    check("all_337_pages",len(pfiles)==337 and {int(p.stem[1:]) for p in pfiles}==set(range(1,338)))
    empty=[]
    for p in pfiles:
        n=int(p.stem[1:])
        meta=json.loads((args.raw/"processing"/(p.stem+".json")).read_text(encoding="utf-8"))
        check("ocr_completion_hash",hashlib.sha256(p.read_bytes()).hexdigest()==meta["text_sha256"],pdf_page=n)
        if not p.stat().st_size:
            empty.append(n)
    check("only_confirmed_blank_pages_empty",empty==[2,6,337],pages=empty)
    check("temporary_renders_deleted",not any(p.is_file() for p in (args.raw/"temporary").rglob("*")))
    digest=hashlib.file_digest(args.pdf.open("rb"),"sha256").hexdigest()
    check("source_hash",digest=="3bb42d877df5a6c45367e7aacb9588206a71447dae4c32fde8f2ff9b5bba23c3")
    check("frozen_protocol",hashlib.sha256((args.package/"PROTOCOL.md").read_bytes()).hexdigest()==(args.package/"PROTOCOL.sha256").read_text().split()[0])
    forbidden_hex=["756e69636f726e","62756c6c","7268696e6f6365726f73","656c657068616e74","7469676572","62756666616c6f",
                   "7a656275","676f6174","616e74656c6f7065","6d6f746966","616e696d616c","7369676e2073657175656e6365","7265616473206173"]
    restricted=[re.compile(r"\b"+re.escape(bytes.fromhex(s).decode())+r"\b",re.I) for s in forbidden_hex]
    unit_pattern=re.compile(r"\b\d+(?:\.\d+)?\s*(?:mm|cm)\b",re.I)
    def words(s):
        return re.findall(r"\b[\w'-]+\b",s.lower())
    source_windows={}
    for p in pfiles:
        ws=words(p.read_text(encoding="utf-8"))
        for i in range(max(0,len(ws)-12)):
            source_windows.setdefault(tuple(ws[i:i+13]),int(p.stem[1:]))
    checked_files=[]
    csv_files=0
    json_files=0
    for p in sorted(args.output.iterdir()):
        if not p.is_file():
            continue
        content=p.read_text(encoding="utf-8")
        checked_files.append(p.name)
        if p.suffix==".csv":
            rows(p)
            csv_files+=1
        if p.suffix==".json":
            json.loads(content)
            json_files+=1
        check("restricted_terms",not any(r.search(content) for r in restricted),file=p.name)
        check("measurement_pattern",not unit_pattern.search(content),file=p.name)
        ws=words(content)
        matches=[source_windows[tuple(ws[i:i+13])] for i in range(max(0,len(ws)-12)) if tuple(ws[i:i+13]) in source_windows]
        check("no_13_word_source_copy",not matches,file=p.name,pdf_pages=sorted(set(matches)))
    summary=dict(result="pass-with-documented-register-exception" if not failures and not shared_register_check else "pass" if not failures else "fail",
                 data_and_content_checks_passed=not failures,
                 required_shared_register_membership_passed=shared_register_check,
                 missing_from_shared_registers=sorted(missing_base),
                 coordinator_manifest_and_local_addition_valid=all(s in coordinator and s in additions_by_id for s in missing_base),
                 registry_exception="The explicitly assigned source is in the coordinator manifest; its shared CSV integration is outside E ownership." if missing_base else "",
                 object_rows=len(objects),sites=len(notes),page_text_files=len(pfiles),empty_confirmed_blank_pages=empty,
                 source_sha256=digest,reviewed_pages=len(read_pages),unique_candidate_pages=len({int(r["pdf_page"]) for r in candidates if r["context_only"]=="0"}),
                 printed_page_labels=sum(bool(r["printed_page"]) for r in rows(args.output/"printed-pages-E.csv")[1]),
                 prospective_tracked_files_checked=len(checked_files),csv_files_parsed=csv_files,json_files_parsed=json_files,
                 source_pages_checked_for_copy=len(pfiles),source_windows_checked=len(source_windows),copy_window_words=13,
                 failure_count=len(failures),failures=failures)
    (args.output/"selftest-E.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
