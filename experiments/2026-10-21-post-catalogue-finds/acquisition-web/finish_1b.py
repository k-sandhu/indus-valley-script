"""Write the run's volume-search record, new-site leads, and final report."""
import csv
import json
from collections import Counter
from pathlib import Path

OUT=Path("experiments/2026-10-21-post-catalogue-finds/acquisition-web")
RAW=Path("data/raw/2026-10-21-post-catalogue-finds/run1b")
def csv_write(name,fields,rows):
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

found={"2001-02":(114,2008,1),"2002-03":(112,2009,1),"2004-05":(116,2014,1),"2005-06":(113,2016,1),"2008-09":(20,2015,2),"2011-12":(17,2016,2)}
queries=json.loads((RAW/"queries.json").read_text(encoding="utf-8"))
volume_rows=[]
for volume in list(found)+[str(y)+"-"+str(y+1)[-2:] for y in range(2014,2027)]:
    years=volume.split("-")
    full=years[0]+"-"+str(int(years[0])+1)
    qids=[q["query_id"] for q in queries if q["site_code"]=="IAR" and (volume in q["query"] or full in q["query"] or years[0] in q["query"])]
    locations="https://asi.nic.in/pages/Publications/indianArchaelogyReports; https://nmma.nic.in/nmma/archReview.do (connection timed out); Internet Archive advanced search; web search"
    if volume in found:
        endpoint,pubyear,page=found[volume]
        url="https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/"+str(endpoint)
        outcome="found and downloaded"
        verify="Volume year and publication year "+str(pubyear)+" confirmed in PDF title/front matter, PDF p. "+str(page)
        notes="ASI current index supplies this file. No Internet Archive file acquired."
        if volume in {"2008-09","2011-12"}:
            notes+=" Earlier NMMA direct retrieval timed out; failed attempt preserved."
    else:
        url=""
        outcome="not found"
        verify="No open volume located; publication status is not established"
        notes="Current ASI IAR index ends at 2013-14. Per-volume web queries and a title-year Internet Archive sweep returned no copy."
        locations+="; assets.ctfassets.net targeted search; ASI Dehradun Circle search"
        if volume=="2026-27":
            notes+=" Reporting season is still in progress on the retrieval date."
    volume_rows.append({"volume":volume,"source_id":"iar-"+volume,"query_ids":";".join(qids),"locations_checked":locations,"download_url":url,"outcome":outcome,"verification":verify,"notes":notes})
csv_write("iar-volume-search-1b.csv","volume source_id query_ids locations_checked download_url outcome verification notes".split(),volume_rows)
new_sites=[
{"site_code":"MSD","site":"Masudpur","aliases":"","country":"India","baseline_year":"1987","source_ids":"msd-petrie-2009;new-masudpur-2009","evidence_status":"publisher-indexed report and further lead","notes":"The 2009 Puratattva report is verified by the publisher index; only its issue table of contents was supplied. The further lead remains unresolved."},
{"site_code":"MTL","site":"Mitathal","aliases":"Meetathal","country":"India","baseline_year":"1987","source_ids":"new-mitathal-2010","evidence_status":"journal-index lead","notes":"Report identified in the Man and Environment index; run 1A owns acquisition."},
{"site_code":"HUL","site":"Hulas","aliases":"","country":"India","baseline_year":"1987","source_ids":"new-hulas-report;iar-2008-09","evidence_status":"report acquired","notes":"Report copyright page gives 2020. Object qualification remains for extraction."},
{"site_code":"DHL","site":"Dhalewan","aliases":"","country":"India","baseline_year":"1987","source_ids":"new-dhalewan-report","evidence_status":"report acquired","notes":"2018 excavation report acquired. Object qualification remains for extraction."},
{"site_code":"TJB","site":"Taloor Ji Bhit","aliases":"","country":"Pakistan","baseline_year":"1991","source_ids":"nht-routes-2025","evidence_status":"context publication lead","notes":"Named with Garho Bhiro in the 2025 publication. Inscribed-object coverage is unverified; this lead establishes no qualifying find."}]
csv_write("new-site-leads-1b.csv","site_code site aliases country baseline_year source_ids evidence_status notes".split(),new_sites)
rows=list(csv.DictReader((OUT/"source-candidates-1b.csv").open(encoding="utf-8",newline="")))
summary=json.loads((RAW/"summary.json").read_text(encoding="utf-8"))
by_id={r["source_id"]:r for r in rows}
order="RGR FRM BHR SNL RPR KRP BJR BRR TKD BNW KNL KLB DHV KHR KNM SKP GDH NGW PDR BTD KNT JKR KBD NVN SKT NHT LKD GNW CHN WTW CHL RJP HRP MHJ".split()
best=dict(zip(order,["rgr-nath-2014","frm-shinde-2011","bhr-uesugi-2016","snl-sharma-2006","iar-2011-12","krp-preliminary-report","bjr-manjul-2017","brr-preliminary-2005","tkd-trivedi-2009","bnw-iar-1987-88","knl-konasukawa-2020",None,"dhv-bisht-2015","khr-nath-2014","knm-report-2012","skp-report-2009","gdh-jamison-2017","ngw-report-1988","pdr-shinde-1992-report","btd-report-1998","knt-report-1996","jkr-pramanik-2004","kbd-shirvalkar-2012",None,"skt-joshi-1990","nht-report-2018",None,"gnw-parpola-2016","chn-preliminary-2021","wtw-dawn-2012","chl-mughal-1997",None,"hrp-parpola-2019","hrp-parpola-2019"]))
best["KHR"]="khr-nath-2012"
best["KBD"]="kbd-shirvalkar-2012-pura"
order += ["MSD","MTL","HUL","DHL","TJB"]
best.update({"MSD":"msd-petrie-2009","MTL":"new-mitathal-2010","HUL":"new-hulas-report","DHL":"new-dhalewan-report","TJB":None})
counts=summary["publications_by_site"]
lines=[
"We recorded "+str(summary["publications"])+" publication records and "+str(summary["search_queries"])+" search queries. Each requested site code received at least five distinct queries. Counts below include bibliographic leads and context studies; they are not counts of qualifying finds. The named source is the strongest candidate located for object-level work, with unverified years marked.",
"",
"We downloaded "+str(summary["publication_files_downloaded"])+" files linked to publication records and "+str(summary["supplementary_files_downloaded"])+" auxiliary files: "+str(summary["downloaded_files"])+" files, "+str(summary["downloaded_bytes"])+" bytes, and "+str(summary["distinct_download_hashes"])+" distinct SHA256 values. These include cover files, issue tables of contents and landing pages whose partial coverage is stated in the records. The auxiliary files preserve a duplicate cover route, an unrelated search hit and an issue table of contents. All acquired files remain local.",
"",
"| Site code | Publications recorded | Best source candidate: title and year |",
"|---|---:|---|"]
for code in order:
    r=by_id.get(best.get(code))
    title=("["+r["title"]+"]("+r["url"]+") ("+r["year"]+")") if r else "No object-level source verified"
    lines.append("| "+code+" | "+str(counts.get(code,0))+" | "+title+" |")
lines += [
"",
"IAR volumes found and title-page verified: 2001-02, 2002-03, 2004-05, 2005-06, 2008-09 and 2011-12. No open copy was found for 2014-15, 2015-16, 2016-17, 2017-18, 2018-19, 2019-20, 2020-21, 2021-22, 2022-23, 2023-24, 2024-25, 2025-26 or the ongoing 2026-27 season. The volume-search CSV records locations and query IDs. No Internet Archive file was downloaded.",
"",
"New-site leads: Masudpur (MSD), Mitathal (MTL), Hulas (HUL), Dhalewan (DHL) and Taloor Ji Bhit (TJB). Hulas and Dhalewan reports were acquired. The others remain bibliographic or context leads; Masudpur's publisher-indexed report is represented by an issue table of contents. Their sources and unresolved coverage are recorded in new-site-leads-1b.csv.",
"",
"Selftest: SELFTEST_RESULT. Every saved download is checked against its CSV row, manifest proposal and acquisition record. The scan reports every prohibited-field hit by file and line.",
"",
"Deviations and limits: two publication titles have one word withheld to preserve the content restriction. Automatic previews reached source snippets, cover captions and descriptive content on a Harappa landing page; exposure-log-1b.csv records that exposure. No such content is copied into our authored records. Supplementary-assets-1b.csv records auxiliary acquisitions without counting them as additional publications. Both ASI Dholavira routes supplied only a two-page cover. The publisher Puratattva files supplied tables of contents, and the 2021 Chanhu-daro record supplied no full text. Several lead titles, dates and bylines remain explicitly unverified. Certificate, format and access failures are preserved locally; no access controls were bypassed.",
"",
"Tracked outputs, all under experiments/2026-10-21-post-catalogue-finds/acquisition-web/: source-candidates-1b.csv, search-log-1b.csv, new-site-leads-1b.csv, iar-volume-search-1b.csv, manifest-proposals-1b.json, exposure-log-1b.csv, selftest-1b.json, supplementary-assets-1b.csv, candidate-publication-locators-1b.json, RETROSPECTIVE-1b.md and final.md. Reusable acquisition, index, record-building, OCR and selftest scripts are in the same directory. Downloads and acquisition records are under data/raw/2026-10-21-post-catalogue-finds/run1b/sources/.",
"",
"We wrote only to the two owned directories. No git commit, branch, stash or reset was made."
]
test_path=OUT/"selftest-1b.json"
test=json.loads(test_path.read_text(encoding="utf-8")) if test_path.exists() else {}
test_result=(test.get("result", "pending")+"; "+str(len(test.get("hash_or_record_errors",[])))+" hash or record errors; "+str(len(test.get("forbidden_field_hits",[])))+" prohibited-field hits")
(OUT/"final.md").write_text("\n".join(lines).replace("SELFTEST_RESULT",test_result)+"\n",encoding="utf-8")
retrospective="""We searched site aliases, excavation seasons, report titles and the named journals, then followed open institutional and publisher links. The source register preserves the access route and remaining bibliographic uncertainty. We acquired the six requested pre-2014 IAR volumes from the current ASI index after NMMA links timed out. The later-volume search found no IAR copy from 2014-15 onward.

We checked titles and bylines in front matter or authoritative publication records. This corrected a Chanhu-daro year and volume conflict in an earlier bibliography and identified an unrelated search hit. The publisher title index supplied exact citations for Karanpura, Khirsara, Kotada Bhadli, Masudpur and the Bhirrana studies. Its archive PDFs supplied tables of contents. Both official Dholavira report routes delivered the same two-page cover. The complete report was not recovered through those routes. The 2021 Chanhu-daro institutional record explicitly offers no document.

Downloads were treated as data. The scripts ran with Python isolation, and no acquired code was executed or unpacked. Poppler supplied page counts and text to memory; one damaged title used a small OCR crop in memory. Automated scans emitted site codes and page locators without saving page text. Automatic search, cover and landing-page previews sometimes reached descriptive content; the exposure log records the source and page scope. The acquisition records retain bibliographic fields and locators.

Two titles contain a restricted descriptive word. We withheld that word in the tracked bibliography and kept the publisher PDF or DOI as its identifier. Search-result paths with restricted wording were also withheld. The register retains uncertain dates, incomplete bylines and unverified object coverage for the extraction run. It makes no catalogue-containment decision.

OneDrive file operations and Windows command-length limits interrupted early record writes. We switched to short encoded writes and rebuilt the records from the run's metadata. Failed HTTP attempts remain in the local run. The selftest verifies all held assets, including the auxiliary files, against the proposed manifest and CSVs, then scans every file in this directory.
"""
(OUT/"RETROSPECTIVE-1b.md").write_text(retrospective,encoding="utf-8")
print(json.dumps({"iar_rows":len(volume_rows),"new_site_leads":len(new_sites),"final_written":True}))
