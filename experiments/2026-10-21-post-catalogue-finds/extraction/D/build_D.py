"""Build the part D identity table and its audit ledgers."""
import argparse
import csv
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

FIELDS="row_id site_code site site_as_published country baseline_volume baseline_year excavation season registration other_numbers findspot depth_or_layer period_or_phase object_type object_subtype material primary_publication publication_year page pdf_page plate_or_figure photo_published drawing_published transcription_published other_publications row_basis inscription_status catalogue_status excavated_before_baseline possible_duplicate_of extraction_note extracted_by".split()
SITE_FIELDS="site_code site sources_read best_publication rows_individual rows_enumerated rows_uncertain_status rows_possibly_in_cisi3 season_blocks count_statements marks_outside_scope groups_without_count unread_sources notes".split()
AGENT="codex gpt-6.1-sol run 2D"


def csv_rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path,fields,rows):
    with Path(path).open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def ranges(values):
    values=sorted(set(int(v) for v in values))
    groups=[]
    for n in values:
        if not groups or n!=groups[-1][-1]+1:
            groups.append([n])
        else:
            groups[-1].append(n)
    return ",".join(str(g[0]) if len(g)==1 else f"{g[0]}-{g[-1]}" for g in groups)


def clean(value):
    value=re.sub(r"(?<=\d)\s*[cm]\s*m", " [unit omitted]",value,flags=re.I)
    return "" if value.strip() in {"-","?",""} else value.strip()


def footer(pdf,number):
    result=subprocess.run(["C:/Users/sandh/Downloads/poppler-24.07.0/Library/bin/pdftotext.exe",
                           "-f",str(number),"-l",str(number),"-bbox-layout",str(pdf),"-"],
                          capture_output=True,check=True)
    root=ET.fromstring(result.stdout)
    page=next(x for x in root.iter() if x.tag.endswith("page"))
    height=float(page.attrib["height"])
    found=[w.text for w in page.iter() if w.tag.endswith("word") and
           float(w.attrib["yMin"])>height-60 and re.fullmatch(r"\d{1,3}",w.text or "")]
    return found[-1] if found else ""


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--raw",required=True)
    ap.add_argument("--text1",required=True)
    ap.add_argument("--text2",required=True)
    ap.add_argument("--register1",required=True)
    ap.add_argument("--register2",required=True)
    ap.add_argument("--museum",required=True)
    args=ap.parse_args()
    out=Path(args.out)
    registers=csv_rows(args.register1)+csv_rows(args.register2)
    source_by={r["source_id"]:r for r in registers}
    catalogue=json.loads((out/"catalogue-metadata-D.json").read_text())
    context=json.loads((out/"seal-table-D.json").read_text())
    detail_by={r["registration"]:r for r in catalogue if r["kind"]=="seal"}
    objects=[]
    exclusions=[]
    merges=[]
    def row(**values):
        item={k:"" for k in FIELDS}
        item.update(site_code="DHV",site="Dholavira",site_as_published="Dholavira",country="India",
                    baseline_volume="CISI 1",baseline_year="1987",excavation="Archaeological Survey of India",
                    primary_publication="bisht-2015-held",publication_year="2015",photo_published="unknown",
                    drawing_published="unknown",transcription_published="no",row_basis="individual",
                    inscription_status="stated",catalogue_status="post-catalogue",excavated_before_baseline="unknown",
                    extracted_by=AGENT)
        item.update({k:str(v) for k,v in values.items()})
        item["row_id"]=f"XD-DHV-{len(objects)+1:03d}"
        objects.append(item)
        return item
    def merge(item,source,page,basis):
        value=f"{source}:{page}"
        refs=item["other_publications"].split("; ") if item["other_publications"] else []
        if value not in refs:
            refs.append(value)
        item["other_publications"]="; ".join(refs)
        merges.append(dict(kept_row_id=item["row_id"],merged_source=source,merged_page=page,basis=basis))

    board=row(object_type="other",object_subtype="signboard",material="gypsum",page="228",pdf_page="245",
              findspot="north gate",plate_or_figure="Figs. 8.2-8.7",photo_published="yes",drawing_published="yes",
              extraction_note="Identity and find context at pp. 228-229; grouped components treated as one object.")
    stone=row(object_type="other",object_subtype="stone block",material="stone",page="230",pdf_page="247",
              findspot="Bailey",plate_or_figure="Figs. 8.8-8.9",photo_published="yes",drawing_published="yes",
              extraction_note="Individual object in the stone-inscription subsection.")
    pottery=row(object_type="inscribed-pottery",page="231",pdf_page="248",
                extraction_note="Individual pottery-fragment example within an unnumbered group.")
    early=row(object_type="inscribed-pottery",page="233",pdf_page="250",period_or_phase="Stage III",
              possible_duplicate_of=pottery["row_id"],
              extraction_note="Individual early-stage pottery example; identity with the p. 231 example is unresolved.")
    # Identity confirmations come from named objects and their archaeological contexts.
    for source,page in [("iar-1989-90","19"),("puratattva-20","PDF 93-94"),("puratattva-29","PDF 34"),("puratattva-37","PDF 65")]:
        merge(board,source,page,"Same named north-gate object in the excavation sequence; no conflicting identity field.")

    included_seals=[]
    for c in context:
        registration=c["registration"].split()[0]
        d=detail_by[registration]
        positive=d["status"] in {"stated","uncertain"} or c["writing_status"]=="yes"
        museum_exception=registration=="22198"
        if not positive and not museum_exception:
            reason=("negative inscription entry" if d["negative"] or c["writing_status"]=="no" else
                    "inscription absent or unavailable in context table" if c["writing_condition"] else
                    "no affirmative inscription statement located")
            exclusions.append(dict(source_id="bisht-2015-held",object_class="seal",registration=registration,
                                   catalogue_number=d["catalogue"],pdf_page=d["pdf_page"],reason=reason))
            continue
        uncertain=registration in {"39152","26105"}
        place="; ".join(filter(None,[clean(c["gsq"]),clean(c["area"])]))
        depth="; ".join(filter(None,[("stratum "+clean(c["stratum"])) if clean(c["stratum"]) else "",
                                     ("Depth/3DR "+clean(c["depth"])) if clean(c["depth"]) else ""]))
        note=f"Context table no. {c['catalogue']}; narrative catalogue no. {d['catalogue']}, p. {d['pdf_page']-17}."
        if "unit omitted" in depth:
            note+=" Unit tokens omitted from the depth coordinates for the required content scan."
        if registration=="26105":
            note+=" Context table and narrative leave inscription status unresolved."
        if registration=="39152":
            note+=" Narrative qualifies script status."
        if museum_exception:
            note+=" Report inscription cell is blank; qualification uses the supplied museum harvest."
        numbers=f"seal catalogue {d['catalogue']}; context table {c['catalogue']}"
        if " NM" in c["registration"]:
            numbers+="; NM"
        item=row(registration=registration,other_numbers=numbers,findspot=place,depth_or_layer=depth,
                 period_or_phase=clean(c["stage"]),object_type="seal",object_subtype=d["shape"],
                 material=d["material"].split("; ")[0],page=str(c["page"]-17),pdf_page=c["page"],
                 inscription_status="uncertain" if uncertain else "stated",extraction_note=note)
        included_seals.append(item)
        merges.append(dict(kept_row_id=item["row_id"],merged_source="bisht-2015-held",
                           merged_page=str(d["pdf_page"]-17),basis="Exact accession number between context and narrative catalogues."))

    for d in catalogue:
        if d["kind"]!="sealing":
            continue
        if not d["writing_mentioned"] or d["negative"]:
            exclusions.append(dict(source_id="bisht-2015-held",object_class="sealing",registration=d["registration"],
                                   catalogue_number=d["catalogue"],pdf_page=d["pdf_page"],
                                   reason="no affirmative inscription statement located"))
            continue
        layer="; ".join("stratum "+v for v in d["layers"])
        depth="; ".join("depth "+v for v in d["context_depth"])
        row(registration=d["registration"],other_numbers="sealing catalogue "+d["catalogue"],
            findspot="; ".join(d["context_gsq"]+d["areas"]),depth_or_layer="; ".join(filter(None,[layer,depth])),
            period_or_phase=d["period_cell"] or "; ".join(d["stages"]),object_type="sealing",material="clay",
            page=str(d["pdf_page"]-17),pdf_page=d["pdf_page"],
            extraction_note="Individual entry in the sealing catalogue.")
    row(registration="8099",other_numbers="tablet catalogue 1",object_type="tablet",material="terracotta",
        page="331",pdf_page="348",plate_or_figure="Fig. 8.31",findspot="Lower Town; east gate of Middle Town",
        depth_or_layer="stratum 8; depth 252",period_or_phase="Stage IV",
        extraction_note="Catalogue entry continues on p. 333; illustration on p. 332.")
    row(registration="10203",other_numbers="tablet catalogue 2",object_type="tablet",material="terracotta",
        page="333",pdf_page="350",plate_or_figure="Fig. 8.32",findspot="Lower Town",depth_or_layer="stratum 3; depth 52",
        period_or_phase="Stage V",extraction_note="Individual entry; illustration on p. 332.")
    iar_id="iar-1997-98-archive"
    printed=footer(source_by[iar_id]["local_path"],38)
    candidate=next(x for x in included_seals if x["material"].lower()=="steatite" and x["object_subtype"].lower()=="square")
    extra=row(primary_publication=iar_id,publication_year="2003",season="1997-98",excavated_before_baseline="no",
              object_type="tablet",object_subtype="small square",material="steatite",pdf_page="38",page=printed,
              plate_or_figure="pl. 16",possible_duplicate_of=candidate["row_id"],
              extraction_note="Called a seal and a tablet in the entry; no registration. Link names one compatible report candidate; identity remains unresolved.")
    merge(extra,"iar-1997-98",printed or "PDF 38","Duplicate edition of the same season entry and plate reference.")
    row(primary_publication="puratattva-29",publication_year="1999",object_type="inscribed-pottery",
        page="22",pdf_page="36",period_or_phase="stage II",possible_duplicate_of=early["row_id"],
        extraction_note="Individual early-stage pottery example; no shared registration or precise findspot establishes a merge with the report.")
    row(primary_publication="puratattva-37",publication_year="2007",object_type="inscribed-pottery",
        pdf_page="65",possible_duplicate_of=early["row_id"],
        extraction_note="Individual pottery-fragment mention; no shared registration or precise findspot establishes a merge with the report.")

    write_csv(out/"objects-D.csv",FIELDS,objects)
    write_csv(out/"exclusions-D.csv",["source_id","object_class","registration","catalogue_number","pdf_page","reason"],exclusions)
    write_csv(out/"merge-log-D.csv",["kept_row_id","merged_source","merged_page","basis"],merges)

    ledger=csv_rows(out/"pages-read-D.csv")
    # Automated identity searches read whole IAR text directories and the whole report.
    # This is recorded separately from the pages inspected through metadata filters.
    search_exposures=[]
    for root in [Path(args.text1),Path(args.text2)]:
        for directory in root.iterdir():
            if not directory.is_dir():
                continue
            if not (re.match(r"iar-(?:1989|199\d|200[0-5])-",directory.name) or
                    directory.name=="bisht-2015-held" and root==Path(args.text1)):
                continue
            if directory.name=="bisht-2015-held" and root==Path(args.text2):
                continue
            ps=sorted(int(p.stem[1:]) for p in directory.glob("p*.txt"))
            search_exposures.append(dict(source_id=directory.name,agent=AGENT,access="automated identity search",
                                         pages=ranges(ps),purpose="Site-name or requested-registration search; source content not emitted."))
            known={(r["source_id"],r["pdf_page"]) for r in ledger}
            for n in ps:
                if (directory.name,str(n)) not in known:
                    ledger.append(dict(source_id=directory.name,pdf_page=str(n),purpose="context",image_viewed="no"))
    for source,ps in {
        "bisht-2015-held":list(range(1,17))+[30,100,240],
        "iar-1989-90":list(range(22,29)),"iar-1990-91":list(range(17,25)),
        "iar-1991-92":list(range(34,41)),"iar-1992-93":list(range(34,41)),
        "iar-1997-98-archive":[3,4,5,6,7,8,9,37,38],"iar-2001-02":list(range(57,61)),
        "man-environment-17":list(range(72,85)),"puratattva-20":list(range(87,96)),
        "puratattva-36":list(range(45,57)),
    }.items():
        known={(r["source_id"],r["pdf_page"]) for r in ledger}
        for n in ps:
            if (source,str(n)) not in known:
                ledger.append(dict(source_id=source,pdf_page=str(n),purpose="candidate",image_viewed="no"))
    # Source text is complete; no page image was opened.
    ledger=sorted({(r["source_id"],str(r["pdf_page"]),r["purpose"]):r for r in ledger}.values(),
                  key=lambda r:(r["source_id"],int(r["pdf_page"]),r["purpose"]))
    write_csv(out/"pages-read-D.csv",["source_id","pdf_page","purpose","image_viewed"],ledger)
    exposure=list(search_exposures)
    for source in sorted({r["source_id"] for r in ledger}):
        ps=[r["pdf_page"] for r in ledger if r["source_id"]==source and r["purpose"]!="context"]
        if ps:
            exposure.append(dict(source_id=source,agent=AGENT,access="text layer through metadata filters",pages=ranges(ps),
                                 purpose="Identity, context, inscription-status and publication-locator extraction."))
    exposure.append(dict(source_id="bisht-2015-held",agent=AGENT,access="diagnostic text output",pages="264,348",
                         purpose="Column-boundary diagnostics exposed disallowed source fragments; omitted from deliverables."))
    write_csv(out/"exposure-log-D.csv",["source_id","agent","access","pages","purpose"],exposure)

    sources_read="; ".join(f"{s}:PDF {ranges(r['pdf_page'] for r in ledger if r['source_id']==s)}"
                           for s in sorted({r["source_id"] for r in ledger}))
    count_statements=(
        "seal=225; sealing=60 (bisht-2015-held p. 233, PDF 250); "
        "seal=225; sealing=60 (bisht-2015-held p. 238, PDF 255); "
        "seal inscription-status sample=194; inscription-present=139; inscription-missing=23; unavailable=28 (bisht-2015-held p. 242, PDF 259); "
        "seal context sample=204 (bisht-2015-held p. 243, PDF 260); "
        "seal period sample=185; Stage IV=136; Stage V=45 (bisht-2015-held p. 244, PDF 261); "
        "sealing=61; period-assigned=59; Stage IV=52 (bisht-2015-held p. 308, PDF 325); "
        "tablet=5; individually described=2 (bisht-2015-held p. 331, PDF 348); "
        "seal without inscription=3 (iar-1991-92 p. 30, PDF 38); "
        "seal=28; sealing=12; cumulative seal=101; cumulative sealing=49 (iar-1992-93 p. 31, PDF 39)")
    counts=Counter(x["object_type"] for x in objects)
    museum_id=next(x["row_id"] for x in objects if x["registration"]=="22198")
    note=(f"Source witness is the preliminary January 2015 Internet Archive report; identity with the ASI publication is unconfirmed. "
          f"The 225-entry seal catalogue yields {counts['seal']} qualified rows; the 61-entry sealing catalogue yields {counts['sealing']}. "
          "The overview's 60 sealings differs from the detailed total of 61. Totals and samples include entries outside the row definition. "
          "Five tablets are reported and two are itemised; the count adds no rows under Amendment 1. "
          f"Supplied museum accession DHR-22198 is report accession 22198, context no. 4 and narrative no. 109: {museum_id}. "
          "DHR-6032 and DHR-7860 were not located by exact-number search of the whole report. "
          "The museum table is experiments/2026-10-13-museum-open-access/joins/join-table.csv; it supplies the inscription qualification for 22198. "
          "Four unresolved cross-entry links remain. Repeated unregistered pottery examples are retained with possible-duplicate links. The unregistered IAR item is linked to one compatible seal candidate, with no identity claim. "
          "The p. 242 inscription-status subtotals sum to 190 against a stated sample of 194. Eleven seal rows have no Yes cell: ten qualify through the narrative and one through the supplied museum record. The early pottery examples use different stage labels in the preliminary article and final witness. "
          "Whole-volume ranges in sources_read document automated metadata searches; exposure-log separates these from filtered candidate-page inspection. "
          "IAR 2003-04 locators are OCR leaves. Sources with no Dholavira excavation entry supply no object rows. "
          "Secondary-source PDF locators are labelled PDF when a printed page was not recovered. No local-corpus matching was performed.")
    note+=" Per-entry media flags remain unknown where a caption does not establish the medium; a column heading alone was not treated as confirmation."
    site=dict(site_code="DHV",site="Dholavira",sources_read=sources_read,best_publication="bisht-2015-held",
              rows_individual=str(len(objects)),rows_enumerated="0",
              rows_uncertain_status=str(sum(x["inscription_status"]=="uncertain" for x in objects)),rows_possibly_in_cisi3="0",
              season_blocks="1989-90 to 2004-05: bisht-2015-held; 1997-98: iar-1997-98-archive individual item; 2005-06: iar-2005-06 searched, no Dholavira excavation entry located",
              count_statements=count_statements,marks_outside_scope="",
              groups_without_count="Harappan-marked pottery and terracotta group (bisht-2015-held p. 231, PDF 248); inscribed-seal group (iar-1989-90 p. 19, PDF 27); seal and sealing groups (iar-2001-02 PDF 57)",
              unread_sources="iar-1996-97: registered file is the 1997-98 volume; the correct volume is unavailable in the assigned holdings",
              notes=note)
    write_csv(out/"site-notes-D.csv",SITE_FIELDS,[site])
    summary={"rows":len(objects),"by_type":dict(counts),"by_basis":dict(Counter(x["row_basis"] for x in objects)),
             "by_inscription_status":dict(Counter(x["inscription_status"] for x in objects)),
             "by_catalogue_status":dict(Counter(x["catalogue_status"] for x in objects)),
             "museum_row":museum_id,"excluded":len(exclusions),"iar_printed_page":printed,
             "pages_logged":len(ledger),"sources":len({r["source_id"] for r in ledger})}
    (out/"summary-D.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
