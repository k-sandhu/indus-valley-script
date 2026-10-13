"""Recompute aggregate local endpoints without changing their source packages."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from bench import key_calibration as K, meaning_map as M, restoration as R, segmentation as S, shots
from bench.common import (KEY_SOURCE, RELEASE_SOURCE, RUN, SHOT_SOURCE, STRUCTURE_SOURCE,
                          envelope, legacy, provenance, read_json, read_rows, sha256, write_json)


def comparison(name, actual, original, source, tolerance=1e-12):
    return {"name": name, "recomputed": actual, "original": original, "source": source,
            "absolute_difference": abs(actual - original), "tolerance": tolerance,
            "match": abs(actual - original) <= tolerance}


def main():
    output = RUN / (sys.argv[1] if len(sys.argv) > 1 else "reproduction-v1")
    output.mkdir(parents=True, exist_ok=False)
    comparisons, sources = [], []
    kc = K.key_common()
    texts = kc.unique_texts()
    key = K.normalize_key({s: list(v) for s, v in kc.key_options().items()})
    model_path = ROOT / "data/raw/2026-10-12-decipherment-claim-tests/sanskrit-key/models/skeleton_kn5.npz"
    model = K.load_model(model_path, "kgcjtdnpbmyrlvs")
    key_result = K.evaluate(texts, key, model)
    refpath = KEY_SOURCE + "/stage3/summary.json"
    original = read_json(ROOT / refpath)["key"]["all"]
    comparisons.append(comparison("key-calibration: published key G", key_result["score"]["G"], original["G"], refpath))
    key_result["published_power_recalculation"] = {}
    power_source = KEY_SOURCE + "/stage5/summary.json"
    derived = read_json(ROOT / KEY_SOURCE / "stage5/derived.json")["true_key_separation_sd"]
    for name, result in read_json(ROOT / power_source)["plaintexts"].items():
        n = result["permuted_true_key"]
        z = (result["true_key_G"] - n["mean"]) / n["sd"]
        key_result["published_power_recalculation"][name] = z
        comparisons.append(comparison("key power arithmetic: " + name, z, derived[name], power_source))
    write_json(output / "key-calibration.json", envelope("key-calibration", key_result, paths=[kc.CLEAN_JSONL, kc.KEY_CSV, model_path, KEY_SOURCE + "/common.py", refpath, power_source]))
    print("Key score reproduced", flush=True)

    old_shots = legacy(SHOT_SOURCE + "/shots_common.py")
    old_summary = read_json(ROOT / SHOT_SOURCE / "split-summary.json")
    rows = read_rows(old_shots.FACES)
    old_split = old_shots.load_split()
    if sha256(old_shots.FACES) != old_summary["faces_sha256"]:
        raise ValueError("Historical face hash changed")
    computed = shots.assignment(rows, "2026-10-12-conjecture-shots")
    summary = shots.summary(rows, computed)
    for field in ("faces", "components"):
        comparisons.append(comparison("shots: " + field, summary[field], old_summary[field], SHOT_SOURCE + "/split-summary.json", 0))
    for half in ("discovery", "confirmation"):
        comparisons.append(comparison("shots: " + half + " families", summary["families_by_half"][half], old_summary["families_by_half"][half], SHOT_SOURCE + "/split-summary.json", 0))
    if computed != old_split:
        raise ValueError("Historical assignments differ")
    write_json(output / "shots.json", envelope("shots", {"historical": summary, "assignment_matches": True,
                              "source_reads": "Historical spent split, reproduction only; source loader logs untouched"}, paths=[old_shots.FACES, ROOT / SHOT_SOURCE / "shots_common.py", ROOT / SHOT_SOURCE / "split-summary.json"]))

    # General contrast/rearrangement code, supplied with the frozen Shot B measures.
    confirm = legacy(SHOT_SOURCE + "/shot-b-reading/confirm.py", {"shots_common": old_shots})
    confirmation = [dict(r, component=old_split[r["object_family_id"]]["component"])
                    for r in rows if old_split[r["object_family_id"]]["half"] == "confirmation"]
    gm = read_json(ROOT / SHOT_SOURCE / "shot-b-reading/GLOSS-MAP.json")["signs"]
    codes = [r["code"] for r in gm]
    mapping = {r["code"]: r for r in gm}
    bands = [[r["band"]["frequency"], r["band"]["position"]] for r in gm]
    families = [f for f in confirm.families(confirmation) if f["group"] == "SEAL"]
    e_site = confirm.concentration_effect(confirm.categorical_units(families, "site"), codes, confirm.MIN_SITE_UNITS, confirm.MIN_UNITS)[0]
    e_size = confirm.size_effect(confirm.size_units(families), codes, confirm.MIN_UNITS)[0]
    # Frozen records contain locality local/pan and official booleans.
    p = [{"id": "site", "positive": {"locality": "local"}, "negative": {"locality": "pan"}, "criterion": "none"},
         {"id": "size", "positive": {"official": True}, "negative": {"official": False}, "criterion": "none"}]
    result = M.rearrange_effects(codes, mapping, bands, [e_site, e_size], p, 10000, 20261012)
    refpath = SHOT_SOURCE + "/shot-b-reading/confirmation/results.json"
    original = read_json(ROOT / refpath)
    comparisons.append(comparison("meaning-map: Shot B primary S", result["primary"]["score"], original["primary"]["S"], refpath))
    comparisons.append(comparison("meaning-map: Shot B distance SD", result["primary"]["distance_sd"], original["primary"]["distance_sd"], refpath))
    comparisons.append(comparison("meaning-map: Shot B p", result["primary"]["p_one_sided"], original["primary"]["p_one_sided"], refpath))
    result["scope"] = "Frozen historical mean criterion and all-site measure; reproduction only. Current submissions require rank/influence and reviewed site policy."
    result["frozen_original_pass"] = result["primary"]["pass"]
    write_json(output / "meaning-map.json", envelope("meaning-map", result, paths=[ROOT / SHOT_SOURCE / "shot-b-reading/confirm.py", ROOT / SHOT_SOURCE / "shot-b-reading/GLOSS-MAP.json", ROOT / refpath]))
    print("Shot closure and meaning-map score reproduced", flush=True)

    paper_path = ROOT / "experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl"
    known = R.known_slots(read_rows(paper_path))
    refpath = "experiments/2026-10-02-six-hour/markov-order2/main/results.json"
    original = read_json(ROOT / refpath)["models"]["Markov2"]
    for k in (1, 5, 10):
        comparisons.append(comparison("restoration: Markov2 top" + str(k), known["top_k"][str(k)]["rate"], original["top" + str(k)], refpath))
    write_json(output / "restoration-known-slot.json", envelope("restoration", {"known_slot": known}, paths=[paper_path, refpath]))
    expected = read_json(ROOT / RELEASE_SOURCE / "benchmark/expected-metrics.json")
    for version in ("v1", "v2", "v3"):
        pred, refs = R.release_inputs(version)
        visual = R.visual_rows(read_rows(pred), [r for path in refs for r in read_rows(path)], version)
        original = expected[version]["summary"]
        for field in ("inscription_number_accuracy", "classification_exact_accuracy"):
            comparisons.append(comparison("restoration release " + version + ": " + field, visual[field]["success"], original[field]["success"], RELEASE_SOURCE + "/benchmark/expected-metrics.json", 0))
        for k in ("strict_top1", "strict_top5"):
            comparisons.append(comparison("restoration release " + version + ": " + k, visual[k]["aligned_recall"]["rate"], original[k]["aligned_recall"]["rate"], RELEASE_SOURCE + "/benchmark/expected-metrics.json"))
        pages, pagepaths = R.release_pages(version)
        for field, value in pages.items():
            comparisons.append(comparison("restoration release " + version + ": " + field + " random recall", value["random"]["recall"]["rate"], expected[version][field]["random"]["recall"]["rate"], RELEASE_SOURCE + "/benchmark/expected-metrics.json"))
        write_json(output / ("restoration-release-" + version + ".json"), envelope("restoration", {"visual_row": visual, **pages, **R.pipeline_criteria(visual, version, pages)}, paths=[pred, *refs, *pagepaths, RELEASE_SOURCE + "/code/score_core.py"]))
    print("Restoration scorer reproduced", flush=True)

    methods = ["branching_entropy", "greedy_ngram", "all_boundaries", "no_boundaries"]
    rehearsal = S.local_rehearsal(methods)
    refpath = STRUCTURE_SOURCE + "/step5-rehearsal/run-segmentation-2026-10-12/summary.json"
    original = read_json(ROOT / refpath)
    for cohort, value in rehearsal.items():
        comparisons.append(comparison("segmentation cohort count: " + cohort, value["texts"], original["cohorts"][cohort]["texts"], refpath, 0))
        for method in methods:
            comparisons.append(comparison("segmentation F1: " + cohort + "/" + method,
                                          value["scores"][method]["boundary_f1"], original["cohorts"][cohort]["scores"][method]["boundary_f1"], refpath))
    write_json(output / "segmentation.json", envelope("segmentation", {"cohorts": rehearsal}, paths=[STRUCTURE_SOURCE + "/segmenters.py", refpath, "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl"]))
    lines = S.local_lines(methods)
    write_json(output / "segmentation-lines.json", envelope("segmentation", {"line_divisions": lines}, paths=[STRUCTURE_SOURCE + "/review/review_step3_segmenter_breaks.py", "data/raw/2026-10-12-structure-first/step3-linebreak-faces.json"]))
    result = envelope("local-reproduction", {"comparisons": comparisons, "all_match": all(c["match"] for c in comparisons),
                                             "scope": "Recomputed source aggregates and rescored saved predictions; no model retraining or new conjecture test"})
    write_json(output / "comparisons.json", result)
    print(json.dumps({"comparisons": len(comparisons), "all_match": result["all_match"]}), flush=True)
    if not result["all_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
