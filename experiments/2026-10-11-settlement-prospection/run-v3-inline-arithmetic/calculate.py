"""Preserved inline unit/calendar arithmetic and source-register comparison.

Replay into a new directory; source values remain attributed observations.
This script does not import or rerun the main settlement analysis.
"""
from __future__ import annotations
import argparse, ast, hashlib, json, math, re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def file_record(path):
    data=path.read_bytes()
    return {"path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
def write(path, obj):
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(obj,f,ensure_ascii=False,indent=2); f.write("\n")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(); out=args.output.resolve()
    names=["arithmetic.json","source-register-comparison.json","verification.json","manifest.json"]
    if out.exists():
        if out!=Path(__file__).resolve().parent or any((out/n).exists() for n in names):
            parser.error("Output directory already exists; use a new directory.")
    else: out.mkdir(parents=True,exist_ok=False)
    v2_path=BASE/"sources-v2.json"; v4_path=BASE/"sources-v4.json"
    v2={s["id"]:s for s in load(v2_path)["sources"]}; v4={s["id"]:s for s in load(v4_path)["sources"]}
    cross=load(BASE/"run-v3/source-id-crosswalk.json")
    code=BASE/"analysis.py"; code_text=code.read_text(encoding="utf-8"); tree=ast.parse(code_text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="source_crosswalk")
    consumed=["id","title","url","observation_id"]
    comparisons=[]
    for rid in cross:
        for field in consumed:
            comparisons.append({"source_id":rid,"field":field,"v2":v2[rid].get(field),"v4":v4[rid].get(field),"identical":v2[rid].get(field)==v4[rid].get(field)})
    changed=[]
    for rid in cross:
        for field in sorted(set(v2[rid])|set(v4[rid])):
            if v2[rid].get(field)!=v4[rid].get(field):
                changed.append({"source_id":rid,"field":field,"consumed_by_analysis":field in consumed,"v2":v2[rid].get(field),"v4":v4[rid].get(field)})
    manifest_main=load(BASE/"run-v3/manifest.json"); actual_code=file_record(code)
    r38_present="R38" in v2 and all(re.search(r"(?<!\d)"+str(n)+r"(?!\d)",v2["R38"]["observation"]) for n in [1056,96])
    comparison={"status":"source metadata comparison with code-consumption audit","source_registers":[file_record(v2_path),file_record(v4_path)],"run_v3_script":actual_code,"source_crosswalk_function_lines":[fn.lineno,fn.end_lineno],"consumed_register_fields":consumed,"numeric_register_fields_consumed":[],"comparison_count":len(comparisons),"comparisons":comparisons,"nonconsumed_metadata_changes":changed,"R38_exists_in_sources_v2":r38_present,"R38_v2_observation":v2["R38"]["observation"],"R38_v4_observation":v4["R38"]["observation"],"numerical_provenance":"The register supplies source IDs, titles, URLs and observation IDs to the crosswalk. Published numerical inputs are curated constants in analysis.py functions green_table, published_arithmetic and resurvey_descriptives; the script does not extract numbers from register prose. That code still matches run-v3's declared code hash. R38 and its 1056/96 count already occur in sources-v2. The final register refines wording and locators, including R08's six-mound observation, while these consumed crosswalk fields remain identical.","scope":"This checks register consumption and preserved code, not automatic extraction or independent authentication of every source number."}
    def row(rid,cid,description,inputs,formula,result,display,limits):
        return {"id":cid,"description":description,"source_id":rid,"source_observation_id":v4[rid]["observation_id"],"source_url":v4[rid]["url"],"source_locator":v4[rid]["locator"],"inputs":inputs,"formula":formula,"result":result,"manuscript_display":display,"limits":limits}
    rows=[]
    rows.append(row("R61","IA01","Depth below the contemporary plain in Dales's historical boring account",{"feet":39,"metres_per_international_foot":"0.3048"},"39 × 0.3048",{"metres":float(Decimal(39)*Decimal("0.3048"))},"approximately 11.9 metres","Exact unit conversion of a source-reported historical depth; not a present water depth, dated occupation boundary or continuous deposit thickness."))
    rows.append(row("R41","IA02","Ghazi Shah inventory rectangular dimensions",{"length_m":160,"width_m":130,"square_metres_per_hectare":10000},"160 × 130 / 10000",{"hectares":160*130/10000},"approximately 2.08 hectares","Rectangular equivalent of inventory dimensions; not a phase-specific occupied or excavated area."))
    rows.append(row("R19","IA03","Kotada fort enclosure dimensions",{"length_m":100,"width_m":60,"square_metres_per_hectare":10000},"100 × 60 / 10000",{"hectares":100*60/10000},"0.6 hectares","Enclosure area derived from reported dimensions; not the whole settlement."))
    for rid,cid,description,bp,display,limits in [
        ("R32","IA04","Lothal IUACD#20C3314 calibrated calendar interval",[4385,3918],"approximately 2435–1968 BCE","Source calibration is retained. No new calibration or second reservoir adjustment is made; ΔR −106 ± 51 years belongs to the source's marine calibration."),
        ("R32","IA05","Lothal D-AMS 042905 calibrated calendar interval",[3825,3424],"approximately 1875–1474 BCE","Source calibration is retained. The source's reported rounded summary is not substituted for its interval endpoints."),
        ("R15","IA06","Approximate Sutlej avulsion age orientation",[8000],"roughly 6050 BCE","The source says shortly after about 8 ka. This is rough calendar orientation using 1950, not a new event date. An OSL study's age reference year can differ from 1950 by decades."),
        ("R16","IA07","Approximate Markanda/foothill palaeoflood age orientation",[3900,3800],"roughly 1950–1850 BCE","Approximate orientation of 3.9–3.8 ka using 1950. The age reference year and dating method remain source-specific; a different OSL reference year can shift this orientation by decades.")]:
        rows.append(row(rid,cid,description,{"BP_or_approximate_age_years_oldest_first":bp,"orientation_reference_year_CE":1950},"calendar-year orientation = 1950 − age; approximate BCE magnitude = age − 1950",{"calendar_year_CE_orientation":[1950-a for a in bp],"approximate_BCE_oldest_first":[a-1950 for a in bp]},display,limits))
    arithmetic={"status":"attributed inline arithmetic, no new archaeological measurements","rows":rows,"calendar_convention":"Calendar BP has origin 1950 CE. Approximate BCE magnitudes here use age minus 1950, following the manuscript's orientation convention; exact historical calendar boundary conventions do not alter its intended rounded scale. Conventional uncalibrated radiocarbon BP is not converted.","unit_constants":{"international_foot_metres":"0.3048","hectare_square_metres":10000},"provenance_limits":"Inputs come from the named source observations, which retain their original measurement precision, dating method and access scope. This endpoint records conversions omitted from the main numerical run. It does not measure new sites, assign archaeological periods or estimate discovery yields."}
    checks=[]
    def check(name,passed,evidence): checks.append({"name":name,"passed":bool(passed),"evidence":evidence})
    check("32_consumed_source_fields_identical",len(comparisons)==32 and all(c["identical"] for c in comparisons),{"field_count":len(comparisons),"source_count":len(cross)})
    check("R38_1056_and_96_already_in_v2",r38_present,{"source_id":"R38","observation_id":v2["R38"]["observation_id"]})
    check("main_code_witness_unchanged",actual_code["sha256"]==manifest_main["script"]["sha256"],{"expected_sha256":manifest_main["script"]["sha256"],"observed_sha256":actual_code["sha256"]})
    for r in rows: check(r["id"]+"_source_observation_resolves",r["source_observation_id"]==v4[r["source_id"]]["observation_id"],{"source_observation_id":r["source_observation_id"]})
    expected=[{"metres":11.8872},{"hectares":2.08},{"hectares":0.6},{"calendar_year_CE_orientation":[-2435,-1968],"approximate_BCE_oldest_first":[2435,1968]},{"calendar_year_CE_orientation":[-1875,-1474],"approximate_BCE_oldest_first":[1875,1474]},{"calendar_year_CE_orientation":[-6050],"approximate_BCE_oldest_first":[6050]},{"calendar_year_CE_orientation":[-1950,-1850],"approximate_BCE_oldest_first":[1950,1850]}]
    for r,e in zip(rows,expected,strict=True): check(r["id"]+"_arithmetic_matches",r["result"]==e,{"actual":r["result"],"expected":e})
    verification={"method":"Independent inline calculations using exact Decimal foot conversion, metric-area identities and integer calendar orientation; no import of analysis.py.","checks":checks,"passed_count":sum(c["passed"] for c in checks),"failed_count":sum(not c["passed"] for c in checks),"interpretation":"Implementation checks are bookkeeping, not archaeological evidence."}
    if verification["failed_count"]: raise AssertionError(verification)
    write(out/"arithmetic.json",arithmetic); write(out/"source-register-comparison.json",comparison); write(out/"verification.json",verification)
    inputs=[file_record(x) for x in [v2_path,v4_path,code,BASE/"run-v3/manifest.json",BASE/"run-v3/source-id-crosswalk.json"]]
    write(out/"manifest.json",{"generated_utc":datetime.now(timezone.utc).isoformat(),"status":"verified inline arithmetic","code":file_record(Path(__file__).resolve()),"inputs":inputs,"outputs":[file_record(out/n) for n in names[:-1]],"row_count":len(rows),"verification_check_count":len(checks),"reproduction":"Run the preserved calculate.py with --output pointing to a fresh directory. Existing numerical endpoints are not changed."})
    print(json.dumps({"output":out.relative_to(ROOT).as_posix(),"rows":len(rows),"passed":verification["passed_count"],"failed":verification["failed_count"]}))
if __name__=="__main__": main()
