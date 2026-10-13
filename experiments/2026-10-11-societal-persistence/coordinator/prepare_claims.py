"""Record coordinator claims with source IDs and exact output pointers."""
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
PREFIX="experiments/2026-10-11-societal-persistence/"

def obs(file,*ids): return {"file":PREFIX+file,"ids":list(ids)}
def out(file,pointer,**assertion): return {"file":PREFIX+file,"pointer":pointer,**assertion}
def readable(statement):
    return re.sub(r"(?<=[A-Za-z])(?=\d)", " ", statement).replace("StageVI","Stage VI").replace("state(","state (")
def claim(id,statement,status,observations=(),outputs=(),discussion="THEORY.md",test="EMPIRICAL-PROTOCOL.md"):
    return {"id":id,"statement":readable(statement),"status":status,"observations":list(observations),"outputs":list(outputs),
            "discussion":PREFIX+discussion,"test":PREFIX+test}

def main():
    path=PACKAGE/"CLAIM-EVIDENCE.json"
    if path.exists(): raise SystemExit("Claim map exists; do not overwrite.")
    model="coordinator/run-v1/results.json"
    copro="review/co-production-v1/results.json"
    claims=[
      claim("P01","The minimum functions are conditional on the persistence outcome, horizon, boundary and bounded baseline supply; organizing institutions need distinct evidence.","conditional theory with established precedents",
            [obs("literature/OBSERVATIONS.json","O-L09-1","O-L09-2","O-L17-1","O-L24-3"),obs("coordinator/OBSERVATIONS.json","CO01","CO02")]),
      claim("P02","Under the separate-cost law, aging skill changes budget1/no-shock primary survival from indefinite to three safe transitions.","exact invented construction",
            outputs=[out(model,"/worlds/8/robust/primary/infinite_viable",equals=True),out(model,"/worlds/12/robust/infinite_count",equals=0),out(model,"/worlds/12/robust/primary/maximum_safe_transitions_if_finite",equals=3)],discussion="MODEL-RESULTS.md"),
      claim("P03","Budget2 exceeds mean work4/3 yet currently safe state(1,1,1) is outside its aging-skill/no-shock infinite set under separate costs.","exact invented construction plus ordinary work-window reasoning",
            [obs("literature/OBSERVATIONS.json","O-L27-1","O-L27-2")],
            [out(model,"/worlds/20/robust/infinite_count",equals=11),out(model,"/worlds/20/robust/infinite_kernel",excludes=[1,1,1])],discussion="MODEL-RESULTS.md"),
      claim("P04","Aging-skill/common-shock primary robustness lasts three transitions at budget2 and is indefinite at budget3 under the single-unit shock law.","exact invented construction",
            outputs=[out(model,"/worlds/22/robust/infinite_count",equals=0),out(model,"/worlds/22/robust/primary/maximum_safe_transitions_if_finite",equals=3),out(model,"/worlds/30/robust/infinite_count",equals=12),out(model,"/worlds/30/robust/primary/infinite_viable",equals=True)],discussion="MODEL-RESULTS.md"),
      claim("P05","In two stipulated provider graphs, a shared input gives minimum failure cardinality1; separate inputs give2.","exact structural construction without failure probabilities",
            outputs=[out(model,"/dependency_cases/0/minimum_failure_cardinality",equals=1),out(model,"/dependency_cases/1/minimum_failure_cardinality",equals=2)],discussion="MODEL-RESULTS.md"),
      claim("P06","A commensurable-output accounting residual lower-bounds additional delivery outside all bounded baseline routes; only one of seven invented controls is positive.","ordinary conditional accounting with exact controls",
            outputs=[out(model,"/inverse_bound_controls/1/additional_renewal_lower_bound",equals=5),out(model,"/inverse_bound_controls/3/additional_renewal_lower_bound",equals=0),out(model,"/inverse_bound_controls/3/finite_supply_bounds_available",equals=False)]),
      claim("P07","Technical feasibility alone does not guarantee voluntary enactment or minimum delivery to every resident.","exact counterexamples under invented payoffs and allocations; established social mechanisms",
            outputs=[out("review/counterexamples-v1/counterexamples.json","/results/implementation/safe_profiles",equals=[[1,0],[0,1]]),out("review/counterexamples-v1/counterexamples.json","/results/implementation/equilibrium_safe_profiles",equals=[]),out("review/counterexamples-v1/counterexamples.json","/results/distribution/resident_safe",equals=[[1,1]])]),
      claim("P08","Harappa's source-reported drain clogging is followed by a replacement culvert on a changed route; downtime, work and delivery remain unresolved.","field-source observation with exact context",
            [obs("evidence/observations.json","E07","E08")],discussion="evidence/APPLICATION.md",test="evidence/TESTS.md"),
      claim("P09","Dholavira's StageVI record includes a preceding desertion, retained reservoir-support walls, stone salvage and changed settlement layout.","field-source observation with occupation break",
            [obs("evidence/observations.json","E10","E11")],discussion="evidence/APPLICATION.md",test="evidence/TESTS.md"),
      claim("P10","A specified Dholavira eastern reservoir was repaired, later lost water function and hosted later activity; this does not identify every reservoir's outcome.","field-source sequence at its stated resolution",
            [obs("evidence/observations.json","E12","E13","E14","E15")],discussion="evidence/APPLICATION.md",test="evidence/TESTS.md"),
      claim("P11","The coded Harappan observations leave delivered quantities, work durations/windows and the demand/output/import bounds unresolved; no numerical minimum is estimated.","documentary endpoint within this sample",
            outputs=[out("coordinator/source-summary-v1.json","/archaeological_application/observations",equals=34),out("coordinator/source-summary-v1.json","/archaeological_application/fully_measured_bound_records",equals=0),out("coordinator/source-summary-v1.json","/archaeological_application/unresolved_count_by_field",equals={"measured_service_delivery":34,"task_duration_bounds":34,"task_window":34,"demand_lower_bound":34,"initial_delivery_upper_bound":34,"imports_upper_bound":34})],discussion="evidence/APPLICATION.md",test="evidence/TESTS.md"),
      claim("P12","Material reproduction, viable trajectories, joint repair and institutional pathways have direct predecessors; the contribution is a proposed archaeological measurement and inference procedure.","bounded predecessor assessment, no field-wide priority claim",
            [obs("literature/OBSERVATIONS.json","O-L17-1","O-L24-1","O-L24-2","O-L24-3","O-L27-1","O-L27-2","O-L11-1","O-L26-3","O-L28-1")],discussion="literature/GAP-ASSESSMENT.md"),
      claim("P13","The literature frame contains25 scoped primary works in28 records; the separate application frame contains14 works. Overlapping works and field lineages prevent interpreting their sum as independent evidence.","purposive source census",
            outputs=[out("coordinator/source-summary-v1.json","/literature/scoped_primary_works",equals=25),out("coordinator/source-summary-v1.json","/literature/source_records",equals=28),out("coordinator/source-summary-v1.json","/archaeological_application/included_works",equals=14)],discussion="literature/SURVEY.md"),
      claim("P14","Under the post-baseline shared-operation law, primary survival becomes indefinite at aging-skill budget1/no-shock and budget2/common-shock; separate-cost deficits are law-dependent.","exploratory exact invented alternative after baseline outcomes",
            outputs=[out(copro,"/worlds/4/robust/infinite_count",equals=9),out(copro,"/worlds/4/robust/primary/infinite_viable",equals=True),out(copro,"/worlds/10/robust/infinite_count",equals=12),out(copro,"/worlds/10/robust/primary/infinite_viable",equals=True),out("coordinator/source-summary-v1.json","/shared_operation_variant/state_memberships_added",equals=76),out("coordinator/source-summary-v1.json","/shared_operation_variant/state_memberships_removed",equals=0)],discussion="MODEL-RESULTS.md"),
      claim("P15","The baseline reconstruction and independent shared-operation reconstruction pass5218 and1968 checks respectively; these verify declared constructions rather than historical applicability.","independent numerical verification",
            outputs=[out("review/model-checks-v1/checks.json","/checks_passed",equals=5218),out("coordinator/co-production-checks-v1/checks.json","/checks_passed",equals=1968)],discussion="MODEL-RESULTS.md"),
    ]
    for c in claims:
        c["independent_check"]=PREFIX+"review/REVIEW.md"
    with path.open("x",encoding="utf-8") as stream:
        json.dump({"scope":"Coordinator synthesis. Status separates exact invented laws, source observations, conditional theory and future tests. Source branch IDs remain distinct.","claims":claims},stream,indent=2); stream.write("\n")
    print(json.dumps({"claims":len(claims)}))

if __name__=="__main__": main()
