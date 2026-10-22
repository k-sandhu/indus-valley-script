"""Read assigned source text and retain only locations and permitted metadata."""
import argparse
import csv
import json
import re
from pathlib import Path


def rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path,fields,items):
    with Path(path).open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)


NUMBERS={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,
         "ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,
         "sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,"thirty":30,
         "forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,"ninety":90}


def numeric(value):
    if value.isdigit():
        return int(value)
    total=0
    for word in re.split(r"[ -]+",value.lower()):
        if word=="hundred":
            total*=100
        else:
            total+=NUMBERS.get(word,0)
    return total


def metadata(text):
    compact=re.sub(r"\s+"," ",text)
    np=r"(?:\d+|"+"|".join(NUMBERS)+r")(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?"
    cp=r"seals?|sealings?|tablets?|tags?|inscribed\s+(?:potsherds?|pottery|objects?|stones?)|graffiti|marks"
    counts=[]
    for m in re.finditer(r"\b("+np+r")\s+(?:(inscribed|uninscribed|clay|terracotta|steatite)\s+)?("+cp+r")\b",compact,re.I):
        counts.append({"count":numeric(m.group(1)),"class":m.group(3).lower(),
                       "qualifier":(m.group(2) or "").lower(),"offset":m.start()})
    return {
        "site_mentioned":bool(re.search(r"Dholavira|Kotada",compact,re.I)),
        "counts":counts,
        "registrations":list(dict.fromkeys(re.findall(r"\bDHR[- .:/]*\d+\b|\b(?:Acc\.?|Reg(?:n|d|istration)?\.?)\s*(?:No\.?|number)?\s*[:.-]?\s*\d+",compact,re.I))),
        "gsq":list(dict.fromkeys(re.findall(r"(?:square|GSQ|trench)\s*[:.-]?\s*([A-Z]{0,3}\s*\d+(?:[xX.]\d+){1,2}(?:[+&,]\d+)?)",compact,re.I))),
        "seasons":list(dict.fromkeys(re.findall(r"\b(?:19|20)\d{2}\s*[-–]\s*\d{2,4}\b",compact))),
        "figures":list(dict.fromkeys(re.findall(r"\b(?:Pl\.?|Plate|Figs?\.?|Figures?)\s*[IVXLC\d]+(?:[.:/-]\d+)*(?:[A-Za-z])?",compact,re.I))),
        "classes":list(dict.fromkeys(m.group().lower() for m in re.finditer(r"\b(?:sealings?|seals?|tablets?|tags?|potsherds?|signboard|inscribed stone|inscription|script|graffiti)\b",compact,re.I))),
        "printed_page":next((line.strip() for line in reversed(text.splitlines())
                             if re.fullmatch(r"\(?\d{1,4}\)?",line.strip())),""),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidates",required=True)
    ap.add_argument("--text1",required=True)
    ap.add_argument("--text2",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out)
    assigned={}
    for row in rows(args.candidates):
        source=row["source_id"]
        if row["site_code"]=="DHV" and source.startswith(("puratattva-","man-environment-")):
            assigned.setdefault(source,set()).add(int(row["pdf_page"]))
    for root in [Path(args.text1),Path(args.text2)]:
        for directory in root.glob("iar-*"):
            if not re.match(r"iar-(?:1989|199\d|200[0-5])-",directory.name):
                continue
            selected=set()
            texts={int(p.stem[1:]):p.read_text(encoding="utf-8-sig",errors="replace") for p in directory.glob("p*.txt")}
            for n,text in texts.items():
                if re.search(r"Dholavira|Kotada",text,re.I):
                    selected.update(x for x in range(max(1,n-1),n+2) if (directory/f"p{x:04d}.txt").exists())
                if re.search(r"EXCAVATIONS?\s+AT\s+DHOLAVIRA",text,re.I):
                    # Read the whole entry, including continuation pages without the site name.
                    started=False
                    for m in range(n,min(n+16,max(texts)+1)):
                        if m not in texts:
                            break
                        selected.add(m)
                        candidate=texts[m]
                        if m==n:
                            candidate=candidate[re.search(r"EXCAVATIONS?\s+AT\s+DHOLAVIRA",candidate,re.I).end():]
                        if re.search(r"(?:^|\n)\s*\d+\.?\s*[.—-]?\s*(?:EXCAVATIONS?|EXPLORATIONS?)\s+(?:AT|IN)",candidate):
                            break
            assigned.setdefault(directory.name,set()).update(selected)
    assigned["bisht-2015-held"]=set(range(245,351))|{1,6,13,14,241,242,243,244}
    ledger=rows(out/"pages-read-D.csv") if (out/"pages-read-D.csv").exists() else []
    result=[]
    for source,numbers in sorted(assigned.items()):
        for number in sorted(numbers):
            paths=[Path(root)/source/f"p{number:04d}.txt" for root in [args.text1,args.text2]]
            path=next((p for p in paths if p.exists()),None)
            if not path:
                result.append({"source_id":source,"pdf_page":number,"unread":True})
                continue
            text=path.read_text(encoding="utf-8-sig",errors="replace")
            entry={"source_id":source,"pdf_page":number,**metadata(text)}
            result.append(entry)
            purpose="context" if source=="bisht-2015-held" and number<245 else "candidate"
            key=(source,str(number),purpose)
            if not any((r["source_id"],r["pdf_page"],r["purpose"])==key for r in ledger):
                ledger.append(dict(source_id=source,pdf_page=number,purpose=purpose,image_viewed="no"))
    write_csv(out/"pages-read-D.csv",["source_id","pdf_page","purpose","image_viewed"],ledger)
    (out/"source-scan-D.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"sources":len(assigned),"pages":len(result)}))


if __name__=="__main__":
    main()
