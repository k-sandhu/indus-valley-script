"""Inspect text using a restricted vocabulary; never emit protected content."""
import argparse
import csv
import json
import re
from pathlib import Path

KEEP=set("a an the of on in at with without from to by and or but which that these those this they their its it were was are is have has had be been bears bear bearing carry carries carrying only all total out remains remaining other both some few most many found recovered excavated during before after above below period phase stage lower middle upper town castle bailey reservoir north south east west surface square layer stratum depth inscription inscriptions inscribed uninscribed script signs sign character characters letter letters seals seal sealing sealings tablet tablets potsherd potsherds pottery stone stones steatite sandstone clay terracotta gypsum faience copper button circular rectangular round prismatic site dholavira kotada excavation excavations no not nil unavailable available broken missing lost defaced damaged clear uncertain illegible include includes including number numbers field registration accession printed same different fragments fragment thereof except two-dimensional three-dimensional corpus catalogue report study article survey reviewed illustrated photograph photographs drawing drawings figure figures table tables pl fig acc gsq identification identification indicated stated confirmed ancient harappan indus early mature late until each together description details small part portions partly can could may might possibly probably perhaps resemble resembling relevant sealings-signatures".split())
KEEP.update("rock boulder slab block wall sherd sherds gate passage chamber chambers locus debris underground corner".split())

ap=argparse.ArgumentParser()
ap.add_argument("--text",required=True)
ap.add_argument("--source",required=True)
ap.add_argument("--pages",required=True)
ap.add_argument("--filter",default="")
args=ap.parse_args()
ledger_path=Path(__file__).parent/"pages-read-D.csv"
with ledger_path.open(encoding="utf-8-sig",newline="") as stream:
    ledger=list(csv.DictReader(stream))
numbers=[]
for part in args.pages.split(","):
    ends=[int(x) for x in part.split("-")]
    numbers.extend(range(ends[0],ends[-1]+1))
for number in numbers:
    text=(Path(args.text)/args.source/f"p{number:04d}.txt").read_text(encoding="utf-8-sig",errors="replace")
    if not any(r["source_id"]==args.source and r["pdf_page"]==str(number) for r in ledger):
        ledger.append(dict(source_id=args.source,pdf_page=number,purpose="candidate",image_viewed="no"))
    text=re.sub(r"\s+"," ",text)
    sentences=re.split(r"(?<=[.!?])\s+",text)
    result=[]
    for sentence in sentences:
        if args.filter and not re.search(args.filter,sentence,re.I):
            continue
        output=[]
        omitted=False
        for token in re.findall(r"[A-Za-z]+|\d+",sentence):
            if token.lower() in KEEP:
                output.append(token)
                omitted=False
            else:
                if not omitted:
                    output.append("...")
                omitted=True
        result.append(" ".join(output))
    print(json.dumps({"source_id":args.source,"pdf_page":number,"filtered_text":result}))
with ledger_path.open("w",encoding="utf-8",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=["source_id","pdf_page","purpose","image_viewed"])
    writer.writeheader()
    writer.writerows(ledger)
