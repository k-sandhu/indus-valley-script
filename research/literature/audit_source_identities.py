"""Display downloaded document headers and flag transport/identity mismatches."""
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root=Path(__file__).parent
records=json.loads((root/"source_retrieval_log.json").read_text(encoding="utf-8"))
result=[]
for item in records:
    if "raw_file" not in item:
        continue
    raw=root/item["raw_file"]
    head=raw.read_bytes()[:8]
    magic="PDF" if head.startswith(b"%PDF") else "ZIP" if head.startswith(b"PK") else "other"
    txt=root/item.get("text_file", "__no_text__")
    snippet=txt.read_text(encoding="utf-8")[:350].replace("\n", " ") if txt.is_file() else ""
    row={"id":item["id"],"magic":magic,"requested_url":item["url"],"header":snippet}
    if item["url"].split("?")[0].endswith(".pdf") and magic!="PDF":
        row["warning"]="URL names PDF but bytes are not PDF; HTTP200 does not verify source identity."
    result.append(row)
    if magic=="PDF":
        print(item["id"], "|", snippet[:210])
    elif "warning" in row:
        print("WARNING", item["id"], "|",snippet[:100])
(root/"source_identity_index.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
