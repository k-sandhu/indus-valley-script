"""Acquire observed public source links, retaining response and access metadata."""
from pathlib import Path
import datetime, hashlib, json, requests

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-02-source-recovery/oxus"
RAW.mkdir(parents=True, exist_ok=True)
SOURCES = [
    ("kircho2008.pdf", "https://www.old.archeo.ru/izdaniya-1/vagnejshije-izdanija/pdf/Altyn_technical_2008.pdf/at_download/file", "Official Institute for the History of Material Culture RAS publication landing page; download link 8"),
    ("sarianidi1998-cloud.html", "https://cloud.mail.ru/public/YRbv/maWz94TRz", "Official Margiana expedition publication list, page 3, 1998 book read link"),
    ("margiana-official-list.html", "https://margiana.su/publikaczii/rabotyi-v.i.-sarianidi/?page=3", "Official expedition bibliography"),
]
records=[]
for name,url,route in SOURCES:
    rec={"url":url,"route":route,"retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"rights_status":"rights-unverified","handling":"local-only"}
    try:
        if (RAW/name).exists():
            raise FileExistsError(f"Existing witness retained: {RAW/name}. Use a new filename for a new acquisition.")
        response=requests.get(url,timeout=150)
        path=RAW/name
        path.write_bytes(response.content)
        rec.update(http_status=response.status_code,final_url=response.url,content_type=response.headers.get("content-type"),bytes=len(response.content),sha256=hashlib.sha256(response.content).hexdigest(),path=path.relative_to(ROOT).as_posix(),pdf_header=response.content.startswith(b"%PDF"))
        print(name, response.status_code, len(response.content), response.headers.get("content-type"))
    except Exception as err:
        rec.update(error=str(err))
        print(name, str(err))
    records.append(rec)
manifest=OUT/"source-acquisition-initial.json"
if manifest.exists():
    raise FileExistsError("Existing acquisition manifest retained; use a new endpoint.")
manifest.write_text(json.dumps({"sources":records},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
