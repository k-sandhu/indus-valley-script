"""Record bounded source-census and missing-quantity endpoints from frozen ledgers."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "source-summary-v1.json"

def read(relative):
    path=PACKAGE/relative
    return json.loads(path.read_text(encoding="utf-8")),hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUTPUT.exists(): raise SystemExit("Census endpoint exists; do not overwrite.")
    sources, h1=read("literature/SOURCES.json")
    observations,h2=read("literature/OBSERVATIONS.json")
    fieldsources,h3=read("evidence/sources.json")
    fieldobs,h4=read("evidence/observations.json")
    copro,h5=read("review/co-production-v1/results.json")
    missing=("measured_service_delivery","task_duration_bounds","task_window","demand_lower_bound",
             "initial_delivery_upper_bound","imports_upper_bound")
    records=fieldobs["observations"]
    gains=[(w,m,w[m]) for w in copro["worlds"] for m in ("possible","robust") if w[m]["added_from_baseline"]]
    out={"scope":"Counts within separate purposive frames, not unique excavations or combined independent-work count",
         "input_sha256":{"literature/SOURCES.json":h1,"literature/OBSERVATIONS.json":h2,
                          "evidence/sources.json":h3,"evidence/observations.json":h4,"review/co-production-v1/results.json":h5},
         "literature":{"source_records":len(sources["sources"]),"scoped_primary_works":sum(r["selected_primary_work"] for r in sources["sources"]),
                       "observations":len(observations["observations"])},
         "archaeological_application":{"included_works":len(fieldsources["included_primary_works"]),"observations":len(records),
              "unresolved_count_by_field":{f:sum(r[f] is None for r in records) for f in missing},
              "fully_measured_bound_records":sum(all(r[f] is not None for f in missing) for r in records)},
         "shared_operation_variant":{"worlds":len(copro["worlds"]),"world_mode_infinite_sets_gaining":len(gains),
              "state_memberships_added":sum(len(r["added_from_baseline"]) for _,_,r in gains),
              "state_memberships_removed":sum(len(w[m]["removed_from_baseline"]) for w in copro["worlds"] for m in ("possible","robust"))}}
    with OUTPUT.open("x",encoding="utf-8") as stream: json.dump(out,stream,indent=2); stream.write("\n")
    print(json.dumps(out))

if __name__=="__main__": main()
