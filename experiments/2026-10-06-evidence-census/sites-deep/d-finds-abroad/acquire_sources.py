"""Acquire or reuse a bounded source packet; all payloads stay in local raw storage."""
import argparse, hashlib, json, os, pathlib, datetime, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[4]
OWNED = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad"
SOURCES = {
 "laursen2010": "https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf",
 "parpola2018": "https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf",
 "nippur1993": "https://isac.uchicago.edu/sites/oi.uchicago.edu/files/uploads/shared/docs/oip111.pdf",
 "frankfort1933": "https://isac.uchicago.edu/sites/oi.uchicago.edu/files/uploads/shared/docs/oic16.pdf",
 "vidale_frenez2015": "https://www.harappa.com/sites/default/files/pdf/Vidale%20%26%20Frenez%20_%20Konar%20Sandal%20seal.pdf"
}
REUSE = {
 "gadd1932": "research/root_primary/gadd1932.pdf",
 "frenez2018": "research/literature/sources/frenez_2018_private_person.pdf",
 "salut2016": "research/literature/sources/frenez_2016_salut.pdf",
 "gonur2005": "data/raw/2026-10-02-source-recovery/oxus/sarianidi2005.pdf",
 "kircho2008": "data/raw/2026-10-02-source-recovery/oxus/kircho2008.pdf"
}
def main():
 global RAW
 parser=argparse.ArgumentParser()
 parser.add_argument('--verify',action='store_true',help='Verify successful saved PDF/text hashes without network access')
 parser.add_argument('--raw-subdir',help='Acquire into a new subdirectory within this package raw directory')
 args=parser.parse_args()
 if args.raw_subdir:
  base=RAW.resolve();dest=(base/args.raw_subdir).resolve()
  if dest==base or base not in dest.parents:raise ValueError('Use a new subdirectory within package raw storage')
  RAW=dest
 if args.verify:
  records=json.loads((RAW/'acquisition.json').read_text(encoding='utf-8'))
  for record in records:
   if record['status']=='acquired':
    for path_key,hash_key in [('path','sha256'),('text_path','text_sha256')]:
     assert hashlib.sha256((ROOT/record[path_key]).read_bytes()).hexdigest()==record[hash_key],record['id']
  print('Verified saved acquisition hashes; failed attempts retained:',sum(x['status']=='failed' for x in records))
  return
 if (RAW/'acquisition.json').exists():
  raise RuntimeError('Saved acquisition exists; use --verify or a new dated --raw-subdir')
 RAW.mkdir(parents=True, exist_ok=True)
 temp=RAW/"tmp";temp.mkdir(exist_ok=True)
 for key in ("TMP","TEMP","MPLCONFIGDIR"): os.environ[key]=str(temp)
 import fitz
 manifest=[]
 for sid in list(SOURCES)+list(REUSE):
  target=RAW/(sid+".pdf")
  rec={"id":sid,"retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"rights_status":"rights-unverified","handling":"local-only"}
  try:
   if sid in REUSE:
    parent=ROOT/REUSE[sid];rec["reused_from"]=REUSE[sid]
    payload=parent.read_bytes()
   else:
    rec["url"]=SOURCES[sid]
    req=urllib.request.Request(SOURCES[sid], headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=60) as resp:
     rec.update(http_status=resp.status, final_url=resp.url,content_type=resp.headers.get("Content-Type"))
     payload=resp.read()
   if not payload.startswith(b"%PDF"): raise ValueError("Payload is not a PDF")
   if target.exists() and target.read_bytes()!=payload: raise ValueError("Existing witness differs; choose a new filename")
   target.write_bytes(payload)
   doc=fitz.open(target);rec.update(path=str(target.relative_to(ROOT)).replace("\\","/"),bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest(),pages=len(doc))
   txt=RAW/(sid+".txt")
   txt.write_text("\n".join(f"[PDF PAGE {i+1}]\n"+p.get_text() for i,p in enumerate(doc)),encoding="utf-8")
   rec["text_path"]=str(txt.relative_to(ROOT)).replace("\\","/")
   rec["text_sha256"]=hashlib.sha256(txt.read_bytes()).hexdigest()
   rec["status"]="acquired"
  except Exception as exc: rec.update(status="failed",error=str(exc))
  manifest.append(rec);print(sid,rec["status"],rec.get("pages"),rec.get("error",""))
 (RAW/"acquisition.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
if __name__=="__main__":main()
