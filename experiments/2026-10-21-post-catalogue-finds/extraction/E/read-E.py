"""Display a restricted vocabulary view of source paragraphs for metadata review."""
import argparse
import json
from pathlib import Path
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textdir", type=Path)
    ap.add_argument("pages", nargs="+")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    permitted = set("a an the of and or also as at in on from to for this these those it its their were was is are has had have been be found recovered yielded collected obtained noticed exposed inscribed inscription inscriptions inscribing script scripts Harappan Indus Brahmi Kharoshthi seal seals sealing sealings tablet tablets tag tags pottery potsherd potsherds sherd sherds pot pots vessel vessels jar jars rim rims base bases handle handles tool tools stone copper bronze terracotta clay steatite faience ivory bone shell silver gold lead metal square rectangular circular round oval triangular cylindrical fragment fragments fragmentary broken complete incomplete uninscribed graffiti mark marks pre early mature late historic historical period periods phase phases layer layers trench trenches pit pits room rooms floor floors surface debris stratum strata level levels type types all some several many few numerous various certain different one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty hundred thousand no not without only single double impression impressions legend legends character characters letter letters sign signs resembles resembling similarity similar comparable comparison possibly possible uncertain discovered located reported showing shown photograph photographs drawing drawings plate plates fig figs figure figures pl pls nos no registration antiquity accession number numbers total besides including include included comprises comprising consists consisting important antiquities finds objects object amongst among noteworthy small datable dated date attribution specimen specimens unidentifiable illegible unidentified".lower().split())
    sites = "Dholavira Kotada Bagasra Gola Dhoro Nagwada Kalibangan Kunal Rakhigarhi Banawali Balathal Rojdi Rupar Ropar Harappa Mohenjo-daro Lothal Alamgirpur Kuntasi Padri Chandigarh Haryana Gujarat Rajasthan Punjab Surkotada Rangpur Kanewal Pithad Prabhas Patan Nageshwar Pabumath".lower().split()
    permitted.update(sites)
    for spec in args.pages:
        a, sep, b = spec.partition("-")
        for n in range(int(a), int(b or a)+1):
            path = args.textdir / f"p{n:04d}.txt"
            t = path.read_text(encoding="utf-8")
            print("PDF", n)
            heading_lines = []
            for line in t.splitlines():
                if re.search(r"(?:EXCAVATION|EXPLORATION|DISTRICT)", line, re.I):
                    words = re.findall(r"[A-Za-z]+|\d{1,4}", line)
                    if words and sum(w.isupper() for w in words)/len(words) > .55:
                        heading_lines.append(" ".join(words))
            print("HEADINGS", json.dumps(heading_lines))
            paragraphs = re.split(r"\n\s*\n", t)
            for i, p in enumerate(paragraphs):
                if not args.all and not re.search(r"\b(?:seal\w*|tablet\w*|inscri\w*|script\w*|graffit\w*|signs?|characters?|letters?|legend\w*|impression\w*|tag\w*)", p, re.I):
                    continue
                q = re.sub(r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|single|double|several|many|few|numerous)\s*(?:[- ]\s*)?(?:sign\w*|character\w*|letter\w*|line\w*)", "[withheld]", p, flags=re.I)
                q = re.sub(r"\b\d+(?:\.\d+)?\s*(?:mm|cm|m|kg|gm|g)\b", "[withheld]", q, flags=re.I)
                q = re.sub(r"\([^)]*\)", "[parenthesis]", q)
                tokens = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)?|\d{1,4}|\[withheld\]|\[parenthesis\]", q)
                view = []
                for word in tokens:
                    if word.lower() in permitted or word in ["[withheld]", "[parenthesis]"]:
                        view.append(word)
                    elif view and view[-1] != "...":
                        view.append("...")
                refs = re.findall(r"\b(?:pl\.?|plate|fig\.?|figure)\s*[.:]?\s*[IVXLCDM\d]+(?:\s*[-–]\s*[IVXLCDM\d]+)?(?:\s*[A-Z])?", p, re.I)
                print(json.dumps(dict(paragraph=i, vocabulary_view=" ".join(view), references=refs), ensure_ascii=True))


if __name__ == "__main__":
    main()
