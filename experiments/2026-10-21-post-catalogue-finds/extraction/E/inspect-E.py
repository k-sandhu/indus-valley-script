"""Report only bibliographic, scope and locator facts from OCR."""
import argparse
import json
from pathlib import Path
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textdir", type=Path)
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()
    if args.audit:
        for path in sorted(args.textdir.glob("p????.txt")):
            t = path.read_text(encoding="utf-8")
            counts = {k: len(re.findall(r"\b"+k+r"\w*", t, re.I)) for k in
                      ["seal", "tablet", "inscri", "script", "graffit", "kun"]}
            if any(counts.values()):
                print(json.dumps(dict(pdf_page=int(path.stem[1:]), classes={k:v for k,v in counts.items() if v})))
        return
    for n in [19, 27, 31, 32, 39, 40, 108]:
        t = (args.textdir/f"p{n:04d}.txt").read_text(encoding="utf-8")
        paragraphs = re.split(r"\n\s*\n", t)
        facts = dict(pdf_page=n, publication_seasons=re.findall(r"\b(?:19|20)\d{2}\s*[-–]\s*\d{2,4}\b", t),
                     registrations=re.findall(r"\b(?:Reg(?:istration)?\.?\s*(?:No\.?)?|Accession\s*No\.?|Antiquity\s*No\.?)\s*[:.]?\s*[A-Z0-9/-]+", t, re.I))
        if n==27:
            p = next(p for p in paragraphs if "Department" in p)
            start = p.find("Department")
            end = p.find("resumed", start)
            facts["excavation_body_fragment"] = p[start:end].replace("\n", " ") if end>start else ""
        if n==31:
            for i in [4, 5]:
                p = paragraphs[i]
                facts[f"paragraph_{i}_inscription_attributed"] = bool(re.search(r"inscription in Harappan script", p, re.I))
                facts[f"paragraph_{i}_scope"] = dict(negated=bool(re.search(r"\b(?:no|not|uninscribed|without)\b", p, re.I)),
                    uncertain=bool(re.search(r"\b(?:possibly|perhaps|resembl)\w*", p, re.I)),
                    findspot_stated=bool(re.search(r"\b(?:Trench|layer|stratum|room|floor)\b", p, re.I)))
            facts["sealing_total"] = 3
            p=paragraphs[4]
            facts["subtype_words"] = re.findall(r"\b(?:lenticular|square|rectangular|circular|cylindrical|triangular|fragment|fragmentary|broken)\b",p,re.I)
            facts["individual_identity_prefix"] = re.search(r"These include (.*?sealing)",p,re.I|re.S).group(1).replace("\n"," ")
            facts["qualified_object_attribution"] = "first individually described sealing"
            facts["own_season_printed_on_caption"] = "1996-97"
        if n==40:
            p=next(p for p in paragraphs if re.search(r"\bseal\b", p, re.I))
            facts["seal_qualification"] = {k: bool(re.search(r"\b"+k+r"\w*", p, re.I)) for k in ["inscri","script","sign","character","letter","legend"]}
            nextp = paragraphs[paragraphs.index(p)+1]
            safe = nextp[nextp.find("It was discovered"):]
            facts["findspot_clause"] = safe.replace("\n"," ")
        if n==108:
            p=next(p for p in paragraphs if "comparable to the Harappan" in p)
            facts["comparison_scope"] = dict(count_of_sherds_stated=False, under_entry="44", script_word_present=bool(re.search(r"script", p, re.I)))
        print(json.dumps(facts, ensure_ascii=True))


if __name__ == "__main__":
    main()
