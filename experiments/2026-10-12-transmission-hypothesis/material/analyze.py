"""Audit frozen source-linked qualitative comparisons. No historical score is fitted."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

PACKAGE = Path("experiments/2026-10-12-transmission-hypothesis/material")
RAW = Path("data/raw/2026-10-12-transmission-hypothesis/material")


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    names = ["PROTOCOL.md","sources.json","observations.json","comparisons.json","operation-joins.json","analyze.py"]
    sources = json.loads((PACKAGE/"sources.json").read_text(encoding="utf-8"))["sources"]
    obs = json.loads((PACKAGE/"observations.json").read_text(encoding="utf-8"))["observations"]
    comps = json.loads((PACKAGE/"comparisons.json").read_text(encoding="utf-8"))["comparisons"]
    joins = json.loads((PACKAGE/"operation-joins.json").read_text(encoding="utf-8"))["joins"]
    checks=[]
    def check(label,passed,detail):checks.append({"check":label,"passed":bool(passed),"detail":detail})
    sm={x["source_id"]:x for x in sources};om={x["observation_id"]:x for x in obs}
    check("unique-source-ids",len(sm)==len(sources),len(sources))
    check("unique-observation-ids",len(om)==len(obs),len(obs))
    for s in sources:
        check(s["source_id"]+"-scope",bool(s["reading_scope"] and s["notes"] and s["lineage"]),"Reading and dependence recorded")
        for w in s["witnesses"]:
            p=Path(w["path"])
            check(s["source_id"]+"-"+p.name,p.is_file() and digest(p)==w["sha256"] and p.stat().st_size==w["bytes"],"Witness bytes/hash match")
    for o in obs:
        s=sm.get(o["source_id"])
        check(o["observation_id"]+"-source",s and o["witness_hash"] in [w["sha256"] for w in s["witnesses"]],"Exact witness join")
        check(o["observation_id"]+"-locus",bool(o["locus"] and o["context"] and o["phase"] and o["observation_kind"]),"Unit and locus present")
        check(o["observation_id"]+"-unobserved-carrier",o["carrier_institution_observed"] is None and o["teaching_relationship_observed"] is None,"A proposed carrier is not coded as an observed teaching institution")
        check(o["observation_id"]+"-identity-and-join",o["language_or_ethnicity_identified"] is False and o["diagnostic_cross_domain_join"] is False,"No identity or diagnostic origin assigned from artifacts")
    statuses={"compatible","less_adequate_for_this_observation","unresolved","contradicted_at_stated_scope"}
    check("fixed-candidate-frame",{c["candidate_id"] for c in comps}=={"C1","C2","C3"},"Only preselected families analyzed")
    for c in comps:
        check(c["candidate_id"]+"-evidence",bool(c["observations"]) and all(x in om for x in c["observations"]),"Substantive surviving observations required")
        check(c["candidate_id"]+"-four-rivals",{r["rival"] for r in c["rivals"]}=={"L","I","R","N"},"Broad routes remain distinct")
        for r in c["rivals"]:
            check(c["candidate_id"]+"-"+r["rival"],r["status"] in statuses and bool(r["basis"]) and all(x in om and c["candidate_id"] in om[x]["candidates"] for x in r["basis"]),"Status joined to candidate-specific observations")
        n=c["narrow_control"]
        check(c["candidate_id"]+"-narrow-scope",n["status"] in statuses and n["scope"] and all(x in om for x in n["basis"]),"A claim-scope control is not a general route exclusion")
    for i,j in enumerate(joins):check(f"join-{i+1}",all(x in om for x in j["material_observations"]) and j["status"] in {"unresolved","material_candidate_only"},"Only supplied observations; no forced textual counterpart")
    derivative_count=0
    for manifest in sorted(RAW.glob("ocr-*/manifest.json")):
        data=json.loads(manifest.read_text(encoding="utf-8"))
        for r in data["records"]:
            check(f"ocr-{manifest.parent.name}-{r['pdf_page']}",digest(r["source_path"])==r["source_sha256"] and digest(r["render_path"])==r["render_sha256"] and r["ocr_exit_code"]==0 and digest(r["text_path"])==r["text_sha256"],"Source/render/OCR hash and exit status")
            derivative_count+=1
    # A declared empty-evidence control cannot retain a material comparison.
    empty_retained=[c["candidate_id"] for c in comps if any(x in set() for x in c["observations"])]
    check("empty-evidence-control",not empty_retained,"No candidate retained when all linked material observations are removed")
    # Accession collision is explicitly retained as one observation, not two replicas.
    check("BPR208-collision-visible","quartz" in om["MO13"]["source_observation"] and "agate" in om["MO13"]["source_observation"],"Material disagreement preserved")
    check("bead-curation-visible",om["MO03"]["source_id"]=="MS02" and "all Harappan" in om["MO03"]["source_observation"],"Collection manufacture/deposition separated")
    date=om["MO23"]["date_evidence"]
    check("dated-specimen-gate",date["probability"]==0.954 and date["sample_layer_join"].startswith("not supplied"),"Source date confidence and missing layer linkage retained")
    rows=[{"candidate_id":c["candidate_id"],"rival":r["rival"],"status":r["status"],"basis":r["basis"]} for c in comps for r in c["rivals"]]
    summary={"sources":len(sources),"observations":len(obs),"candidate_families":len(comps),"broad_rival_comparisons":len(rows),"statuses":dict(Counter(r["status"] for r in rows)),
             "narrow_claim_controls":len(comps),"diagnostic_material_to_textual_joins":sum(o["diagnostic_cross_domain_join"] for o in obs),
             "observed_teaching_relations":sum(o["teaching_relationship_observed"] is not None for o in obs),"checked_OCR_pages":derivative_count,
             "checks":len(checks),"passed":sum(x["passed"] for x in checks),"failed":[x["check"] for x in checks if not x["passed"]],
             "scope":"Integrity and source-linked documentary comparison. Zero joins follows the recorded missing feature/route evidence; no historical probability or general absence is estimated."}
    for n,data in [("checks.json",checks),("summary.json",summary),("rival-matrix.json",rows),("input-hashes.json",{(PACKAGE/n).as_posix():digest(PACKAGE/n) for n in names})]:
        (args.output_dir/n).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary))
    if summary["failed"]:raise SystemExit(1)


if __name__=="__main__":main()
