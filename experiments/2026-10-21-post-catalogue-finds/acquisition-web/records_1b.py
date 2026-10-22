"""Build the run's bibliographic records and proposed manifest entries."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

FIELDS="source_id site_codes title authors year venue volume_issue_pages url access downloaded local_path bytes sha256 rights_notice_observed seasons_covered reported_inscribed_counts pages_of_object_descriptions gives_registrations gives_photographs notes".split()

def csv_write(path,fields,rows):
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

ap=argparse.ArgumentParser()
ap.add_argument("repo",type=Path)
ap.add_argument("raw",type=Path)
ap.add_argument("out",type=Path)
args=ap.parse_args()
root=args.repo.resolve()
rows=json.loads((args.raw/"candidates.json").read_text(encoding="utf-8"))
aux=json.loads((args.raw/"aux-assets.json").read_text(encoding="utf-8"))
locators=json.loads((args.raw/"candidate-locators.json").read_text(encoding="utf-8"))
locator_by_id={r["source_id"]:r for r in locators}
proposals=[]
exposure=[]
front={"bhr-uesugi-2016":"PDF 1","frm-uesugi-jamison-2020":"PDF 1","frm-uesugi-jamison-2024":"PDF 1","gdh-jamison-2017":"PDF 1","khr-report-2014":"PDF 1","khr-nath-2014":"PDF 1","knl-konasukawa-2020":"PDF 1-3","chn-didier-2017":"PDF 1","chn-desset-2022":"PDF 1 text layer; empty","skp-report-2009":"PDF 1","gnw-parpola-2016":"PDF 1 top block","bjr-manjul-2017":"PDF 1 text layer and title-area OCR","snl-prabhakar-2013":"PDF 1","new-hulas-report":"PDF 1-2","new-dhalewan-report":"PDF 1 text layer; empty"}
for row in rows+aux:
    for field in FIELDS:
        row.setdefault(field,"")
    row["downloaded"]="no"
    if not row["reported_inscribed_counts"]:
        row["reported_inscribed_counts"]="unstated"
    if row["source_id"] in locator_by_id and row["source_id"].startswith("iar-"):
        hit=locator_by_id[row["source_id"]]["site_candidate_pages"]
        row["pages_of_object_descriptions"]="; ".join(code+": candidate PDF "+",".join(map(str,hit.get(code,[]))) for code in row["site_codes"].split(";") if code in hit) or "not located by automated scan"
        row["notes"]+=" Locators are keyword co-occurrences, not verified object descriptions; OCR may miss sites."
    if row["source_id"]=="new-hulas-report":
        row["year"]="2020"
        row["notes"]+=" The acquired copyright page and Google Books give 2020; WorldCat gives 2021."
    directory=args.raw/"sources"/row["source_id"]
    record_path=directory/"acquisition.json"
    if not record_path.exists():
        row["rights_notice_observed"]="not inspected"
        exposure.append({"source_id":row["source_id"],"agent":"codex gpt-6.1-sol run 1B","access":"web search results or bibliographic metadata only","pages":"not paginated; no local document read","purpose":"Identify publication and access route"})
        continue
    acq=json.loads(record_path.read_text(encoding="utf-8"))
    path=directory/acq["filename"]
    relative=path.resolve().relative_to(root).as_posix()
    notice=acq.get("rights_notice_observed","")
    if "pending" in notice or "not yet checked" in notice:
        notice="None was shown in the inspected access material."
    acq.update(title=row["title"],authors=row["authors"],year=row["year"],rights_notice_observed=notice,local_path=relative,bibliographic_notes=row["notes"])
    if row["source_id"]=="bjr-manjul-2017":
        acq["transformations"]=[{"method":"title-area crop rendered in memory and OCR with Tesseract; only title line returned","parent_sha256":acq["sha256"],"derivative_saved":False}]
    if row["source_id"] in locator_by_id:
        acq["transformations"]=[{"method":"pdftotext to memory; site and keyword co-occurrences only","parent_sha256":acq["sha256"],"output":"data/raw/2026-10-21-post-catalogue-finds/run1b/candidate-locators.json","page_text_saved":False}]
    record_path.write_text(json.dumps(acq,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    row.update(downloaded="yes",local_path=relative,bytes=acq["bytes"],sha256=acq["sha256"],rights_notice_observed=notice)
    item={"id":row["source_id"],"title":row["title"],"authors":row["authors"],"year":row["year"],"kind":"publication" if row in rows else "supplementary-asset","local_paths":[relative],"size":{"bytes":acq["bytes"],"pages":acq["page_count"]},"rights":{"status":"rights-unverified","licence":None,"detail":notice,"notice_url":acq.get("rights_notice_url",row["url"])},"fetch":{"method":"http","url":acq["url"],"filename":acq["filename"],"bytes":acq["bytes"],"sha256":acq["sha256"],"verify":{acq["filename"]:acq["sha256"]}},"hashes":{relative:acq["sha256"]},"questions":["Q-1026"],"status":"held","location":"local-only","evidence":[record_path.resolve().relative_to(root).as_posix()],"notes":row["notes"]}
    for key in ["archive_md5","archive_sha1","archive_identifier","archive_filename"]:
        if key in acq:
            item["fetch"][key]=acq[key]
    proposals.append(item)
    pages=front.get(row["source_id"],"none; bytes and document page count only")
    access="byte-only acquisition"
    if row["source_id"] in front:
        access="bibliographic text-layer preview"
    if row["source_id"]=="hrp-parpola-2019":
        access="Harappa landing-page text preview included descriptive content; downloaded PDF acquired by bytes only"
        pages="web page excerpts; no PDF page images opened"
    if row["source_id"].startswith("iar-"):
        pages="PDF 1-5 front matter; automated keyword scan of all pages"
        access="front-matter preview and automated text-layer scan"
    elif row["source_id"] in locator_by_id:
        pages+="; automated keyword scan of all pages"
        access+="; automated text-layer scan"
    elif acq["content_type"].startswith("text/html"):
        access="publication landing-page HTML and bibliographic metadata"
        pages="web page; no page images"
    exposure.append({"source_id":row["source_id"],"agent":"codex gpt-6.1-sol run 1B","access":access,"pages":pages,"purpose":"Bibliography and acquisition verification; automated scans emitted locators only"})
csv_write(args.out/"source-candidates-1b.csv",FIELDS,rows)
csv_write(args.out/"supplementary-assets-1b.csv",FIELDS,aux)
(args.out/"manifest-proposals-1b.json").write_text(json.dumps(proposals,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
queries=json.loads((args.raw/"queries.json").read_text(encoding="utf-8"))
search_rows=[]
for query in queries:
    urls=[x["url"] for x in query["results"]]
    matched=[r["source_id"] for r in rows if r["url"] in urls]
    search_rows.append({"query_id":query["query_id"],"site_code":query["site_code"],"query":query["query"],"date_utc":query["date_utc"],"results_considered":"; ".join(urls) if urls else "No results returned","sources_recorded":";".join(sorted(set(matched)))})
csv_write(args.out/"search-log-1b.csv","query_id site_code query date_utc results_considered sources_recorded".split(),search_rows)
exposure.append({"source_id":"search-results-and-previews-1b","agent":"codex gpt-6.1-sol run 1B","access":"search snippets and automatic previews","pages":"Queries 1B-PRE-001 to 1B-PRE-005; IAR front matter PDF 1-5; publication title previews listed above","purpose":"Bibliographic discovery. Some automatic previews reached source snippets and cover captions before filtering was tightened; no inscription content was copied to these outputs."})
exposure.append({"source_id":"publisher-title-index-35-48","agent":"codex gpt-6.1-sol run 1B","access":"publisher bibliographic title index via web text","pages":"PDF 5-6, 8-11, 14-15, 17","purpose":"Verify titles, authors, issue years and pagination; https://indarchaeology.org/Index/4_Title%20Index%20Nos.%2035-48.pdf"})
csv_write(args.out/"exposure-log-1b.csv","source_id agent access pages purpose".split(),exposure)
(args.out/"candidate-publication-locators-1b.json").write_text(json.dumps(locators,indent=2)+"\n",encoding="utf-8")
counts=Counter(code for row in rows for code in row["site_codes"].split(";") if code)
summary={"publications":len(rows),"publications_by_site":dict(sorted(counts.items())),"publication_files_downloaded":sum(r["downloaded"]=="yes" for r in rows),"supplementary_files_downloaded":sum(r["downloaded"]=="yes" for r in aux),"downloaded_files":len(proposals),"downloaded_bytes":sum(p["size"]["bytes"] for p in proposals),"distinct_download_hashes":len({p["fetch"]["sha256"] for p in proposals}),"search_queries":len(queries)}
(args.raw/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
