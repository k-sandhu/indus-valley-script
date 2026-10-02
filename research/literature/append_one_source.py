import sys, json
from fetch_sources import ROOT, retrieve
if __name__ == "__main__":
    item = tuple(sys.argv[1:])
    assert len(item)==4, "id publication status url"
    result=retrieve(item)
    path=ROOT/"source_retrieval_log.json"
    records=json.loads(path.read_text(encoding="utf-8"))
    records.append(result)
    path.write_text(json.dumps(records,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
