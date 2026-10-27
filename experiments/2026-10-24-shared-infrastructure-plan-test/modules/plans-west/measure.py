"""Measure the frozen western targets and fit only independent grid controls."""
import cmath
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sensitivity(d, b, s, e, eb):
    assert b > 2*eb
    return [s*max(0, d-2*e)/(b+2*eb), s*(d+2*e)/(b-2*eb)]


def parent_point(point, panel):
    """Invert the integer crop/rotation, without fitting archaeological features."""
    x, y = point
    left, top, right, bottom = panel["crop_pixels_actual"]
    rotation = panel["rotation_counterclockwise_degrees"]
    if rotation == 90:
        return [right-1-y, top+x]
    if rotation == -90:
        return [left+y, bottom-1-x]
    return [left+x, top+y]


def fit_similarity(controls):
    pixels = [complex(*[r["pixel"][0], -r["pixel"][1]]) for r in controls]
    targets = [complex(r["grid"][0]-2355, r["grid"][1]-1015) for r in controls]
    pm, qm = sum(pixels)/len(pixels), sum(targets)/len(targets)
    factor = sum((p-pm).conjugate()*(q-qm) for p,q in zip(pixels,targets))/sum(abs(p-pm)**2 for p in pixels)
    shift = qm-factor*pm
    residuals = [abs(factor*p+shift-q) for p,q in zip(pixels,targets)]
    return factor, shift, residuals


def main():
    run = LOCAL / "measurement-v1"
    run.mkdir()
    inv_path = HERE / "inventory-freeze.json"
    inv_hash = read(HERE / "inventory-freeze.sha256.json")["sha256"]
    assert sha(inv_path) == inv_hash
    inv = read(inv_path)
    assert sha(PACKAGE / "PROTOCOL.md") == inv["protocol_sha256"]
    trace_manifest = read(HERE / "trace-manifest-v1.json")
    trace_path = Path(trace_manifest["physical_path"])
    assert sha(trace_path) == trace_manifest["sha256"]
    traces = read(trace_path)
    assert traces["frozen_inventory_sha256"] == inv_hash
    assert traces["created_utc"] > inv["created_utc"]
    assert not traces["new_documentary_overlay_received"]
    panel_rows = read(LOCAL / "panel-crops-v1.json")
    panels = {r["id"]:r for r in panel_rows}
    refs_path = LOCAL / "panel-reference-points-v1.json"
    refs = read(refs_path)
    result_rows, detailed = [], []
    for r in traces["measurements"]:
        panel = panels[r["panel"]]
        assert sha(Path(panel["crop_physical_path"])) == panel["crop_sha256"]
        width, height = panel["crop_size"]
        for x,y in r["feature_endpoints"]+r["scale_endpoints"]:
            assert 0 <= x < width and 0 <= y < height, r["id"]
        d, b = math.dist(*r["feature_endpoints"]), math.dist(*r["scale_endpoints"])
        value = r["scale_metres"]*d/b
        bounds = sensitivity(d,b,r["scale_metres"],r["feature_endpoint_radius_px"],r["scale_endpoint_radius_px"])
        metric = dict(id=r["id"],panel=r["panel"],town=panel["town"],feature=r["feature"],source_id=panel["source_id"],
                      locator=panel["locator"],pdf_page_index=panel["pdf_page_index"],phase=panel["phase"],panel_class=panel["panel_class"],
                      metres=value,digitization_sensitivity_metres=bounds,
                      bound_type="conditional endpoint-reading sensitivity, not a confidence interval or source survey error",
                      unknown_source_error=r["source_error"],stated_scale_metres=r["scale_metres"],
                      feature_endpoint_reading_radius_px=r["feature_endpoint_radius_px"],scale_endpoint_reading_radius_px=r["scale_endpoint_radius_px"],
                      interpretation=r["interpretation"],north_reference=refs[r["panel"]]["north_reference"],
                      trace_physical_path=str(trace_path),trace_sha256=sha(trace_path),
                      dating_basis="Source relative sequence and figure attribution; this line has no independently dated repair sample.",
                      route_persistence_contrast_eligible=False,
                      ineligibility_reason="Single-panel geometry or published-dimension check; no complete matched internal-partition denominator.")
        if "published_check_metres" in r:
            check = r["published_check_metres"]
            metric.update(published_check_metres=check,published_check_inside_reading_bound=bounds[0]<=check<=bounds[1])
            assert metric["published_check_inside_reading_bound"]
        if "source_prose_dimensions_metres" in r:
            metric.update(source_prose_dimensions_metres=r["source_prose_dimensions_metres"],source_prose_locator=r["source_prose_locator"])
        result_rows.append(metric)
        detailed.append(dict(**metric,feature_pixels=d,scale_pixels=b,
                             crop_feature_endpoints=r["feature_endpoints"],crop_scale_endpoints=r["scale_endpoints"],
                             parent_feature_endpoints=[parent_point(point,panel) for point in r["feature_endpoints"]],
                             parent_scale_endpoints=[parent_point(point,panel) for point in r["scale_endpoints"]]))
    assert {r["id"] for r in result_rows} == {r["id"] for r in inv["numerical_targets"] if r["id"].startswith("PW-M")}
    registration = traces["registration"]
    detailed_registration, summaries = {}, []
    for pid, controls in registration["controls"].items():
        factor, shift, residuals = fit_similarity(controls)
        held_out = []
        for c in registration["held_out_controls"][pid]:
            predicted = factor*complex(c["pixel"][0],-c["pixel"][1])+shift
            target = complex(c["grid"][0]-2355,c["grid"][1]-1015)
            held_out.append(dict(**c,error_metres=abs(predicted-target),predicted_offsets_metres=[predicted.real,predicted.imag]))
        summary = dict(panel=pid,control_count=len(controls),held_out_control_count=len(held_out),
                       grid_fit_rmse_metres=math.sqrt(sum(v*v for v in residuals)/len(residuals)),
                       grid_fit_max_error_metres=max(residuals),held_out_max_error_metres=max(v["error_metres"] for v in held_out),
                       metres_per_pixel=abs(factor),control_reading_radius_metres=registration["control_reading_radius_px"]*abs(factor),
                       unknown_error="Original grid survey, scan distortion and plan compilation errors remain unquantified.")
        summaries.append(summary)
        detailed_registration[pid]=dict(**summary,pixel_to_grid_offset_matrix=[[factor.real,factor.imag,shift.real],[factor.imag,-factor.real,shift.imag],[0,0,1]],
                                        controls=controls,control_residuals_metres=residuals,held_out_controls=held_out)
    registration_summary = dict(id=registration["id"],panels=registration["panels"],model=registration["model"],
                                geometry_window=registration["declared_geometric_window"],window_scope=registration["window_scope"],
                                fits=summaries,feature_used_as_registration_control=False,flexible_warp_used=False,
                                eligible_for_persistence_difference=False,reason=registration["reason"],
                                local_detail_path=str(run/"registration-details.json"))
    data = dict(status_class="exploratory",created_utc=datetime.now(timezone.utc).isoformat(),frozen_inventory_sha256=inv_hash,
                trace_sha256=sha(trace_path),reading_rules_sha256=sha(PACKAGE/"MEASUREMENT-RULES.md"),
                measurements=result_rows,registration=registration_summary,
                decision=dict(C0017_P1_eligible_episodes=0,C0017_P1_effect=None,
                              effect_missing_reason="No complete source window supplies comparable shared-route and internal-partition persistence through independently joined episodes.",
                              genuinely_registered_descriptive_pair=1,primary_frame_towns_in_this_module=3,selected_panels=23),
                authors=[dict(model="GPT-6 family; exact serving variant unknown",harness="Codex desktop",agent="western_towns")])
    (run/"measurement-details.json").write_text(json.dumps(detailed,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (run/"registration-details.json").write_text(json.dumps(detailed_registration,indent=2)+"\n",encoding="utf-8")
    (HERE/"measurements.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # All coordinate arrays remain on D. The tracked panel manifest holds transformations and pointers.
    for panel in panel_rows:
        ref=refs[panel["id"]]
        panel.update(north_reference=ref["north_reference"],scale_bar_metres=ref["scale_bar_metres"],scale_note=ref["scale_note"],
                     reference_points_physical_path=str(refs_path),reference_points_sha256=sha(refs_path),
                     scale_endpoint_missing_reason=None if ref["scale_bar_crop_endpoints"] else ref["scale_note"],
                     feature_endpoint_trace_physical_path=str(trace_path),feature_endpoint_trace_sha256=sha(trace_path),
                     measured_feature_ids=[r["id"] for r in result_rows if r["panel"]==panel["id"]],
                     unmeasured_feature_reason="Only frozen named numerical targets are traced. Other visible linework supplies no complete survival inventory.",
                     independent_date_sample=None,independent_date_missing_reason="No repair sample tied to this represented feature is supplied by the selected panel.")
    (HERE/"plan-panels.json").write_text(json.dumps(dict(panels=panel_rows,coordinate_arrays_local_only=True),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(measurements=[dict(id=r["id"],m=round(r["metres"],3),bound=[round(x,3) for x in r["digitization_sensitivity_metres"]]) for r in result_rows],registration=summaries,eligible_episodes=0)))


if __name__ == "__main__":
    main()
