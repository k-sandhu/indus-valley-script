"""Return site/keyword page co-occurrences only; never emit page text."""
import argparse
import json
import re
import subprocess
from pathlib import Path

SITES = {
"RGR":r"Rakhigarhi|Rakigarhi|Rakhi Garhi|Rakhi Shahpur|Rakhi Khas",
"FRM":r"Farmana","BHR":r"Bhirrana|Bhirdana","SNL":r"Sanauli|Sinauli",
"RPR":r"Rupar|Ropar","KRP":r"Karanpura","BJR":r"Binjor|4MSR",
"BRR":r"Baror","TKD":r"Tarkhanewala|Tarkhanwala","BNW":r"Banawali",
"KNL":r"Kunal","KLB":r"Kalibangan","DHV":r"Dholavira","KHR":r"Khirsara",
"KNM":r"Kanmer","SKP":r"Shikarpur","GDH":r"Gola Dhoro|Bagasra",
"NGW":r"Nagwada","PDR":r"Padri","BTD":r"Bet Dwarka","KNT":r"Kuntasi",
"JKR":r"Juni Kuran|Junikuran","KBD":r"Kotada Bhadli","NVN":r"Navinal",
"SKT":r"Surkotada","NHT":r"Nuhato|Gharo Bhiro|Garho Bhiro",
"LKD":r"Lakhan.?jo.?daro|Lakheen.?jo.?daro|Lakhueen.?jo.?daro",
"GNW":r"Ganweriwala|Ganweriwal","CHN":r"Chanhu.?daro|Chanhudaro",
"WTW":r"Wattoowala","CHL":r"Derawar Ther|Rappwala Ther|Guddal|Bakkar Buthi",
"RJP":r"Chak 585|Rajanpur","HRP":r"Harappa","MHJ":r"Mohenjo.?daro|Moenjodaro",
"HUL":r"Hulas","DHL":r"Dhalewan","MTL":r"Mitathal","MSD":r"Masudpur"}
ap=argparse.ArgumentParser()
ap.add_argument("root",type=Path)
ap.add_argument("out",type=Path)
ap.add_argument("ids",nargs="+")
args=ap.parse_args()
output=[]
for source_id in args.ids:
    path=args.root/"sources"/source_id/(source_id+".pdf")
    if not path.exists():
        continue
    proc=subprocess.run(["pdftotext","-enc","UTF-8",str(path),"-"],capture_output=True,timeout=120)
    pages=proc.stdout.decode("utf-8",errors="replace").split("\f")
    hits={}
    for code,pat in SITES.items():
        indices=[i+1 for i,page in enumerate(pages) if re.search(r"\b(?:"+pat+r")\b",page,re.I) and re.search(r"\bseal(?:ing)?s?\b|\btablets?\b|inscri|\bscript\b",page,re.I)]
        if indices:
            hits[code]=indices
    output.append({"source_id":source_id,"method":"same-page keyword co-occurrence; candidate locators only","pdf_pages":len(pages)-1,"site_candidate_pages":hits})
args.out.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
print(json.dumps(output))
