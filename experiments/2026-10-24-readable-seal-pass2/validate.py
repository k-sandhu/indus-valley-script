from pathlib import Path
import json,hashlib,collections
P=Path(__file__).resolve().parent
R=Path("D:/projects/indus_valley_script/data/raw/2026-10-24-readable-seal-pass2")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 errors=[]
 sources=json.loads((P/"source-manifest.json").read_text(encoding="utf-8"))
 for x in sources:
  if "physical_path" in x:
   f=Path(x["physical_path"])
   if not f.exists() or f.stat().st_size!=x["bytes"] or sha(f)!=x["sha256"]:errors.append(x["source_id"])
 rows=json.loads((R/"ledger-v1.json").read_text(encoding="utf-8"))
 assert len({x["id"] for x in rows})==len(rows)
 assert all(x["source_id"] in {s["source_id"] for s in sources} for x in rows)
 counts=collections.Counter(x["decision"] for x in rows)
 assert counts=={"defer":3,"exclude-incomplete":1,"defer-acquisition":2}
 assert sha(P/"PROTOCOL.md")==json.loads((P/"protocol-hash.json").read_text())["sha256"]
 result={"passed":not errors,"errors":errors,"sources_checked":len(sources),"rows":len(rows),"decisions":dict(counts),"admitted":0,"ledger_sha256":sha(R/"ledger-v1.json"),"scope":"author structural and source-byte validation"}
 (P/"validation-v1.json").write_text(json.dumps(result,indent=2))
 print(json.dumps(result))
 assert not errors
if __name__=="__main__":main()
