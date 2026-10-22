"""Merge every source cited in dating-v1/towns/*.json into dating-v1/sources.json.

The Radiocarbon-journal lists come from code/radiocarbon_lists.json (with URL, DOI,
retrieval time and SHA-256). Other sources come from the towns' `sources` arrays;
when two towns give the same id with different citations, both citations are kept
under `variant_citations` so a reader can see the difference. Each entry lists the
towns that cite it. Lists that no town cites are kept and marked `cited_by: []`,
because we searched them for every town.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "sources.json"


def main():
    rc = json.loads((HERE / "radiocarbon_lists.json").read_text(encoding="utf-8"))
    by_id = {s["id"]: dict(s, cited_by=[], kind="radiocarbon date list") for s in rc}
    shared = json.loads((HERE / "shared_sources.json").read_text(encoding="utf-8"))
    for s in shared:
        by_id[s["id"]] = dict(s, cited_by=[], kind="radiocarbon compilation")
    for path in sorted((HERE.parent / "towns").glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        for s in d.get("sources", []):
            sid = s["id"]
            if sid not in by_id:
                by_id[sid] = {"id": sid, "citation": s.get("citation"), "url_or_path": s.get("url_or_path"),
                              "sha256": s.get("sha256"), "cited_by": [], "kind": "publication"}
            e = by_id[sid]
            if path.stem not in e["cited_by"]:
                e["cited_by"].append(path.stem)
            if e.get("kind") == "publication":
                if s.get("citation") and s["citation"] != e["citation"]:
                    v = e.setdefault("variant_citations", [])
                    if s["citation"] not in v:
                        v.append(s["citation"])
                for k in ("url_or_path", "sha256"):
                    if not e.get(k) and s.get(k):
                        e[k] = s[k]
    out = {"description": "Every source searched or cited by the dating-v1 compilation. Ids match the `source` fields in towns/*.json.",
           "n_sources": len(by_id),
           "sources": sorted(by_id.values(), key=lambda x: x["id"])}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(by_id), "sources written to", OUT)


if __name__ == "__main__":
    main()
