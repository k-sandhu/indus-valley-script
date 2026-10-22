"""Write the reviewed metadata extraction and its coverage records."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def ranges(values):
    values=sorted(set(values))
    result=[]
    start=last=values[0]
    for n in values[1:]:
        if n==last+1:
            last=n
        else:
            result.append(str(start) if start==last else f"{start}-{last}")
            start=last=n
    result.append(str(start) if start==last else f"{start}-{last}")
    return ",".join(result)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",type=Path)
    ap.add_argument("raw",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("pdf",type=Path)
    args=ap.parse_args()
    sid="iar-1996-97-archive"
    agent="codex gpt-6.1-sol run 2E"
    fields="row_id site_code site site_as_published country baseline_volume baseline_year excavation season registration other_numbers findspot depth_or_layer period_or_phase object_type object_subtype material primary_publication publication_year page pdf_page plate_or_figure photo_published drawing_published transcription_published other_publications row_basis inscription_status catalogue_status excavated_before_baseline possible_duplicate_of extraction_note extracted_by".split()
    obj=dict.fromkeys(fields,"")
    obj.update(row_id="XE-GDH-001",site_code="GDH",site="Gola Dhoro (Bagasra)",site_as_published="Bagasra",
               country="India",baseline_volume="CISI 1",baseline_year="1987",
               excavation="Department of Archaeology, M.S. University",season="1996-97",
               object_type="sealing",object_subtype="conical sealing",material="terracotta",
               primary_publication=sid,publication_year="2002",page="23",pdf_page="31",
               plate_or_figure="pl. IX",photo_published="unknown",drawing_published="unknown",
               transcription_published="no",row_basis="individual",inscription_status="stated",
               catalogue_status="post-catalogue",excavated_before_baseline="no",
               extraction_note="first individually described sealing; no registration printed",extracted_by=agent)
    write(args.output/"objects-E.csv",[obj],fields)
    note_fields="site_code site sources_read best_publication rows_individual rows_enumerated rows_uncertain_status rows_possibly_in_cisi3 season_blocks count_statements marks_outside_scope groups_without_count unread_sources notes".split()
    notes=[]
    def site(code,name,pages,**kwargs):
        r=dict.fromkeys(note_fields,"")
        r.update(site_code=code,site=name,sources_read=f"{sid}:PDF {pages}",best_publication=sid,
                 rows_individual=0,rows_enumerated=0,rows_uncertain_status=0,rows_possibly_in_cisi3=0)
        r.update(kwargs)
        notes.append(r)
    site("DHV","Dholavira","18-27",season_blocks=f"1996-97:{sid}",
         notes="The seasonal entry is on printed pp.11-19. The keyword hits concern excavation context; no qualifying inscribed object or inscribed-object total is stated. The shared final report is left to the matching run.")
    site("GDH","Gola Dhoro (Bagasra)","27-34",rows_individual=1,season_blocks=f"1996-97:{sid}",
         count_statements=f"sealing=3, total class count ({sid} p.23, PDF 31)",
         notes="The first of three individually described sealings has an explicit Harappan inscription attribution. The other two have no such attribution. The class total exceeds the eligible row count by two; it is not a conflicting total of inscribed objects. No anonymous rows are added. The plate reference is legible in the narrative; its image medium is unclassified.")
    site("KLB","Kalibangan","30-32",
         notes="Comparison with previously known tablets only; no new object or numerical total is reported. Baseline CISI 3.2, 2019; the 2002 publication gives no object rows under Amendment 1.")
    site("NGW","Nagwada","30-32",
         notes="Comparison with previously known tablets only; no newly found object or numerical total is reported.")
    site("BLU","Balu","38-41",season_blocks=f"1996-97:{sid}",
         notes="New unused code for the Harappan excavation heading on PDF 39. The following page mentions one seal without an explicit inscription attribution; it produces no row.")
    site("CHG","Chandigarh","6-8,39-41",
         notes="The site-name hits identify an administrative office or contents entry. No Chandigarh find is reported on these pages.")
    site("BLT","Balathal","98-102,107-109",season_blocks=f"1996-97:{sid}",
         notes="The excavation entry has no qualifying inscribed-object total. The comparison on PDF 108 belongs to the following Kodumanal entry. Baseline CISI 3.2, 2019; the 2002 publication gives no object rows under Amendment 1.")
    site("KDM","Kodumanal","107-109",season_blocks=f"1996-97:{sid}",
         groups_without_count=f"pottery marks compared with Harappan examples; no numerical or individual object count ({sid} p.100, PDF 108)",
         notes="New unused code for entry 44, which supplies a Harappan comparison outside the seed list. The comparison leaves the attribution open and the group uncounted, so no physical-object row can be formed. Other inscriptions in the entry are not attributed to Indus script.")
    site("BNW","Banawali","210-212",
         notes="The keyword hit belongs to an archaeobotanical study. No qualifying object or count is reported.")
    site("RPR","Rupar","218-220",
         notes="The hit is a museum activity entry under Ropar. The inscription keyword is in a different museum entry on the same page; no qualifying Rupar object is reported.")
    site("BRS","Brass","91-98",season_blocks=f"1996-97:{sid}",
         notes="New unused code for a supplementary check of an excavation with a Harappan phase. The uncounted sealings on printed p.87 belong to a later period and have no Indus inscription attribution.")
    site("KNL","Kunal","1-337 (automated site search)",best_publication="none in this volume",
         notes="No Kunal heading or site-name occurrence was found by the full-volume site search. No seasonal row is inferred from the existence of the longer campaign.")
    site("RJD","Rojdi","1-337 (automated site search)",best_publication="none in this volume",
         notes="No Rojdi or Rodji occurrence was found. Baseline CISI 3.2, 2019; the 2002 publication would supply count statements only.")
    write(args.output/"site-notes-E.csv",notes,note_fields)
    write(args.output/"merge-log-E.csv",[],["kept_row_id","merged_source","merged_page","basis"])
    with (args.output/"candidate-pages-E.csv").open(encoding="utf-8",newline="") as f:
        candidates=list(csv.DictReader(f))
    direct={int(r["pdf_page"]) for r in candidates if r["context_only"]=="0"}
    read=set(range(1,9)) | set(range(13,35)) | set(range(38,42)) | {72,73} | set(range(91,103)) | set(range(107,114)) | {120,130,143,150,180,198,199} | set(range(210,215)) | set(range(218,226)) | {235,261,267,271} | {335,336,337}
    # Include every indexed candidate and immediate neighbour in the review record.
    assert {int(r["pdf_page"]) for r in candidates} <= read
    plates={18,20,22,24,25,26,32,34,38,93,94,96,97,99,100,102,107,109,110,111,112,210,212,214,220}
    pages=[dict(source_id=sid,pdf_page=n,purpose="candidate" if n in direct else "plate" if n in plates else "context",image_viewed="no") for n in sorted(read)]
    write(args.output/"pages-read-E.csv",pages,["source_id","pdf_page","purpose","image_viewed"])
    exposure=[
        dict(source_id=sid,agent=agent,access="OCR and keyword search by script",pages="1-337",
             purpose="Full-volume rendering and English OCR; footer labels; site and keyword sweep. No page image was viewed."),
        dict(source_id=sid,agent=agent,access="restricted-vocabulary page-text review",pages=ranges(read),
             purpose="Bibliography, candidate pages, neighbours, entry boundaries and supplementary scope checks."),
        dict(source_id=sid,agent=agent,access="unfiltered bibliographic page-text review",pages="1-5",
             purpose="Confirm volume year, imprint and publication year."),
        dict(source_id=sid,agent=agent,access="automated context-fragment exposure",pages="40",
             purpose="An initial filter exposed a short descriptive fragment. The filter was corrected; the fragment is not retained in extraction outputs.")
    ]
    write(args.output/"exposure-log-E.csv",exposure,["source_id","agent","access","pages","purpose"])
    leads=[
        dict(source_id=sid,pdf_page=39,printed_page=31,site_code="BLU",site="Balu",entry_number=16,
             inclusion_basis="Harappan entry with a keyword hit continuing onto PDF 40"),
        dict(source_id=sid,pdf_page=108,printed_page=100,site_code="KDM",site="Kodumanal",entry_number=44,
             inclusion_basis="Harappan comparison under the excavation heading"),
        dict(source_id=sid,pdf_page=95,printed_page=87,site_code="BRS",site="Brass",entry_number=41,
             inclusion_basis="Supplementary keyword-only check of a site with a Harappan phase")
    ]
    write(args.output/"new-site-leads-E.csv",leads,["source_id","pdf_page","printed_page","site_code","site","entry_number","inclusion_basis"])
    proposal=json.loads((args.package/"acquisition-coordinator"/"manifest-proposals-coordinator.json").read_text(encoding="utf-8"))
    fetch=next(r["fetch"] for r in proposal["sources"] if r["id"]==sid)
    source=dict(source_id=sid,title="Indian Archaeology 1996-97 - A Review",authors_or_editors="Archaeological Survey of India",
                publication_year=2002,volume_year="1996-97",identifier="indianarchaeology199697areview_534_b",
                url=fetch["url"],bytes=args.pdf.stat().st_size,archive_md5=fetch["archive_md5"],archive_sha1=fetch["archive_sha1"],
                local_path=args.pdf.as_posix(),sha256=hashlib.file_digest(args.pdf.open("rb"),"sha256").hexdigest(),
                pdf_pages=337,text_basis="tesseract",rights_status="rights-unverified",
                register_basis="acquisition-coordinator/manifest-proposals-coordinator.json",
                notes="Source explicitly assigned to run 2E; not yet present in the two shared acquisition CSV registers. Imprint year is from PDF 3-4.")
    write(args.output/"source-register-additions-E.csv",[source],list(source))
    completeness=[]
    for n in range(1,338):
        p=args.raw/"text"/sid/f"p{n:04d}.txt"
        meta=json.loads((args.raw/"processing"/f"p{n:04d}.json").read_text(encoding="utf-8"))
        data=p.read_bytes()
        completeness.append(dict(pdf_page=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                                 matches_completed_ocr=hashlib.sha256(data).hexdigest()==meta["text_sha256"]))
    (args.output/"completeness-E.json").write_text(json.dumps(dict(pages=337,records=completeness),indent=2)+"\n",encoding="utf-8")
    summary=dict(source_id=sid,pdf_pages_ocr=337,direct_candidate_pages=len(direct),
                 pages_reviewed=len(read),individual_rows=1,enumerated_rows=0,sites_in_notes=len(notes),
                 empty_text_pages=[r["pdf_page"] for r in completeness if r["bytes"]==0],
                 completed_ocr_hashes_match=all(r["matches_completed_ocr"] for r in completeness))
    (args.output/"coverage-E.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    provenance_path=args.output/"ocr-provenance-E.json"
    provenance=json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance.update(volume_year="1996-97",volume_year_confirmed_pdf_pages=[1,3],
                      publication_year=2002,imprint_pdf_pages=[3,4],
                      fallback_pages=[224],fallback_reason="Initial empty OCR on nonblank page; sparse English OCR recovered text.")
    provenance_path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
