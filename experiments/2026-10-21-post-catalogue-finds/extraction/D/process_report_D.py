"""Derive permitted catalogue metadata without retaining descriptions."""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def words(path):
    root = ET.fromstring(path.read_bytes())
    return [{"t":w.text or "", "x":float(w.attrib["xMin"]), "y":float(w.attrib["yMin"])}
            for w in root.iter() if w.tag.endswith("word")]


def text_of(items):
    return " ".join(w["t"] for w in sorted(items,key=lambda w:(w["p"],round(w["y"],1),w["x"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--review", default="")
    args = ap.parse_args()
    cache = Path(args.cache)
    out = Path(args.out)
    all_words = []
    for p in range(277,347):
        for w in words(cache/f"p{p:04d}.xml"):
            w["p"]=p
            all_words.append(w)
    results = []
    for kind,lo,hi in [("seal",277,324),("sealing",326,346)]:
        group = [w for w in all_words if lo<=w["p"]<=hi and 50<=w["x"]<700 and 95<=w["y"]<705]
        anchors = sorted([w for w in group if w["x"]<95 and re.fullmatch(r"\d+\.",w["t"])],
                         key=lambda w:(w["p"],w["y"]))
        for i,anchor in enumerate(anchors):
            start=(anchor["p"],anchor["y"]-1)
            end=(anchors[i+1]["p"],anchors[i+1]["y"]-1) if i+1<len(anchors) else (hi+1,0)
            block=[w for w in group if start<=(w["p"],w["y"])<end]
            threshold=153 if kind=="sealing" or anchor["p"]%2==0 else 140
            id_words=sorted([w for w in block if 95<=w["x"]<threshold and re.fullmatch(r"\d+[a-z]?",w["t"])],
                            key=lambda w:(w["p"],w["y"]))
            registration=id_words[0]["t"] if id_words else ""
            body=text_of([w for w in block if w["x"]>=(153 if kind=="sealing" or w["p"]%2==0 else 140)])
            body=re.sub(r"(?<=\w)-\s+(?=\w)","",body)
            terms=bool(re.search(r"inscri|legend|script|\bsigns?\b|characters?|letters?",body,re.I))
            negative=bool(re.search(r"(?:no|without|devoid of|does not have|bears no|carries no)\s+(?:any\s+)?(?:an?\s+)?(?:inscription|legend|script|signs?|characters?)|uninscribed|no trace of (?:any )?(?:inscription|script|signs?)",body,re.I))
            uncertain=bool(re.search(r"(?:possibly|probably|perhaps|resembl\w*)[^.]{0,45}(?:inscri|script|sign|character)|(?:inscri|script|sign|character)[^.]{0,35}(?:possibly|probably|perhaps|resembl)",body,re.I))
            missing=bool(re.search(r"(?:inscription|legend)(?:\s+(?:is|are|completely|entirely|now|part|portion|section|has|been|all|mostly|fully))*\s+(?:missing|lost|obliterated)|(?:missing|lost)\s+(?:inscription|legend)",body,re.I))
            mats=[]
            for material in re.finditer(r"\b(?:steatite|terracotta|terra-cotta|faience|copper|sandstone|stone|clay|gypsum)\b",body,re.I):
                if material.group().lower() not in [x.lower() for x in mats]:
                    mats.append(material.group())
            shape=re.search(r"\b(?:square|rectangular|circular|cylindrical|round|button|prismatic)\b",body,re.I)
            classification="uncertain" if uncertain else "stated" if terms and not negative else "excluded" if negative else "review"
            # No source wording from the narrative is retained except short metadata values.
            entry={"kind":kind,"catalogue":anchor["t"].rstrip("."),"registration":registration,
                   "pdf_page":anchor["p"],"end_page":end[0] if end[1]>0 else end[0]-1,
                   "status":classification,"writing_mentioned":terms,"negative":negative,
                   "writing_missing":missing,
                   "material":"; ".join(mats),"shape":shape.group() if shape else "",
                   "stages":list(dict.fromkeys(re.findall(r"\bStage\s+[IVX]+(?:\s*[A-C])?\b",body,re.I))),
                   "seasons":list(dict.fromkeys(re.findall(r"\b(?:19|20)\d{2}\s*[-–]\s*\d{2,4}\b",body))),
                   "figures":list(dict.fromkeys(re.findall(r"\b(?:Pl\.?|Plate|Fig\.?|Figure)\s*\d+(?:\.\d+)?(?:[A-Za-z])?",body,re.I))),
                   "gsq":list(dict.fromkeys(re.findall(r"(?<=square )\d+[xX]\d+(?:[xX]\d+(?:\+\d+)?)?",body))),
                   "has_photo_column":kind=="sealing",
                   "tablet_mentioned":bool(re.search(r"\btablet\b",body,re.I)),
                   "transcription_reference":bool(re.search(r"Mahadevan|Parpola|sign[- ]list|sign numbers?|sign no",body,re.I))}
            entry["areas"]=list(dict.fromkeys(m.group() for m in re.finditer(
                r"\b(?:Lower Town|Middle Town|Bailey|Castle|(?:East|South|Eastern|Northern|Western)\s+[Rr]eservoir(?:[- ]\d+)?)\b",body)))
            entry["context_gsq"]=list(dict.fromkeys(re.findall(
                r"(?:square|G\.?\s*sq\.?|GSQ|Locus)\s*(?:no\.?)?\s*[:.-]?\s*(\d+[xX./×-]\d+(?:[xX./×-]\d+(?:[+&,]\d+)?)?)",body,re.I)))
            entry["join_assertion"]=bool(re.search(r"\bjoin(?:s|ed|ing)?\b|same physical object",body,re.I))
            entry["layers"]=list(dict.fromkeys(re.findall(
                r"\b(?:layer|stratum)\s*[:.-]?\s*\(?([\d]+\s*[A-Za-z]?)\)?",body,re.I)))
            entry["context_depth"]=list(dict.fromkeys(re.findall(
                r"\bdepth\s*(?:of\s*)?[:.]?\s*([-+]?\d+(?:\.\d+)?(?:\s*(?:to|[-–])\s*[-+]?\d+(?:\.\d+)?)?)",body,re.I)))
            if kind=="sealing":
                period=text_of([w for w in block if 500<=w["x"]<610])
                entry["period_cell"]=" ".join(re.findall(r"\b[IVX]+\b|\?",period))
            entry["stages"]=list(dict.fromkeys(re.findall(r"\b[Ss]tage\s*[-:.,]?\s*[IVX]+(?:\s*[A-C])?\b",body)))
            if args.review and (args.review=="uncertain" and uncertain or registration in args.review.split(",")):
                allowed=set("a an the of on in at with without from to by and or but which that these those this they their its it were was are is have has had be been bears bear bearing carry carries carrying only all total out remains remaining other both some few most many no not nil unavailable available broken missing lost defaced damaged clear uncertain illegible inscription inscriptions inscribed uninscribed script signs sign character characters letter letters seal seals part portion partly partially could may might possibly probably perhaps resemble resembling below above preserved visible obliterated completely entirely observed identification identified indistinct indistinctly trace traces incomplete intact said present is are have has do does number numbers be of this it its there can near without containing marked surface".split())
                clauses=[]
                for sentence in re.split(r"(?<=[.!?])\s+",body):
                    if not re.search(r"inscri|legend|script|\bsigns?\b|characters?|letters?",sentence,re.I):
                        continue
                    tokens=[]
                    for token in re.findall(r"[A-Za-z]+",sentence):
                        if token.lower() in allowed:
                            tokens.append(token)
                        elif not tokens or tokens[-1]!="...":
                            tokens.append("...")
                    clauses.append(" ".join(tokens))
                print(json.dumps({"registration":registration,"kind":kind,"pdf_page":anchor["p"],"writing_clauses":clauses}))
            results.append(entry)
    (out/"catalogue-metadata-D.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    from collections import Counter
    print(json.dumps({"counts":dict(Counter((r["kind"]+":"+r["status"]) for r in results)),
                      "missing_registration":[r for r in results if not r["registration"]]},indent=2))


if __name__=="__main__":
    main()
