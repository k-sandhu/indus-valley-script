"""Score artificial known-slot masks and the release's candidate-set visual rows."""
from collections import defaultdict
import math
from pathlib import Path

import numpy as np

from .common import RELEASE_SOURCE, ROOT, envelope, legacy, read_json, read_rows


def core():
    return legacy(RELEASE_SOURCE + "/code/score_core.py")


def wilson(success, total):
    return core().wilson(success, total)


def known_slots(rows):
    if not rows:
        raise ValueError("Known-slot predictions are empty")
    seen, top, by_text, by_code, items = set(), {k: [] for k in (1, 5, 10)}, defaultdict(list), defaultdict(list), []
    losses = []
    for r in rows:
        target = r.get("actual", r.get("target"))
        if not isinstance(target, str) or target == "UNKNOWN":
            raise ValueError("Known-slot target must be an observed graphic string")
        rid = r.get("record_id", r.get("id"))
        slot = r["slot"]
        if isinstance(slot, bool) or not isinstance(slot, int) or slot < 0 or not rid:
            raise ValueError("Each prediction requires an id and nonnegative integer slot")
        query = (rid, slot)
        if query in seen:
            raise ValueError("Duplicate known-slot query")
        seen.add(query)
        guesses = r.get("suggestions", r.get("predictions"))
        if not guesses or not all(isinstance(g.get("code"), str) for g in guesses):
            raise ValueError("Supply ranked suggestions with graphic code strings")
        codes = [g["code"] for g in guesses]
        if len(set(codes)) != len(codes):
            raise ValueError("Repeated graphic in ranked suggestions")
        masses = [g.get("model_mass", g.get("probability")) for g in guesses]
        if any(isinstance(p, bool) or not isinstance(p, (float, int)) or not math.isfinite(p) or not 0 <= p <= 1 for p in masses):
            raise ValueError("Suggestion probabilities must be finite in [0, 1]")
        if any(a + 1e-12 < b for a, b in zip(masses, masses[1:])) or sum(masses) > 1 + 1e-9:
            raise ValueError("Suggestions must be ranked by nonincreasing probability with total mass <= 1")
        for k in top:
            top[k].append(target in codes[:k])
        correct = top[1][-1]
        by_text[rid].append(correct)
        by_code[target].append(correct)
        items.append([masses[0], int(correct)])
        if "bucket_loss_bits" in r:
            losses.append(r["bucket_loss_bits"])
    return {"queries": len(rows), "texts": len(by_text),
            "top_k": {str(k): wilson(sum(v), len(v)) for k, v in top.items()},
            "equal_text_top1": float(np.mean([np.mean(v) for v in by_text.values()])),
            "equal_code_top1": float(np.mean([np.mean(v) for v in by_code.values()])),
            "mean_bucket_loss_bits": float(np.mean(losses)) if losses else None,
            "calibration": core().calibration(items),
            "scope": "Artificial known-slot recovery; exact fine-code targets, including OOV failures"}


def paired_comparison(rows, baseline, draws=2000, seed=20261013):
    known_slots(baseline)
    def identity(r):
        return r.get("record_id", r.get("id")), r["slot"]
    ref = {identity(r): r for r in baseline}
    if len(ref) != len(baseline) or set(ref) != {identity(r) for r in rows}:
        raise ValueError("Baseline and proposed model must score exactly the same masked queries")
    grouped = defaultdict(list)
    for r in rows:
        b = ref[identity(r)]
        target = r.get("actual", r.get("target"))
        if target != b.get("actual", b.get("target")):
            raise ValueError("Baseline target differs")
        component = r.get("component", r.get("group", r.get("artifact", identity(r)[0])))
        bcomponent = b.get("component", b.get("group", b.get("artifact", identity(b)[0])))
        if component != bcomponent:
            raise ValueError("Baseline closure component differs")
        a = r.get("suggestions", r.get("predictions"))[0]["code"] == target
        c = b.get("suggestions", b.get("predictions"))[0]["code"] == target
        grouped[str(component)].append(int(a) - int(c))
    numerators = np.array([sum(v) for v in grouped.values()])
    denominators = np.array([len(v) for v in grouped.values()])
    rng = np.random.default_rng(seed)
    samples = rng.integers(0, len(grouped), size=(draws, len(grouped)))
    values = numerators[samples].sum(axis=1) / denominators[samples].sum(axis=1)
    ci = np.quantile(values, [.025, .975]).tolist()
    return {"top1_difference": float(numerators.sum() / denominators.sum()), "component_bootstrap_ci95": ci,
            "components": len(grouped), "draws": draws, "seed": seed, "pass_statistical": ci[0] > 0,
            "pass_rule": "Positive lower 95% paired component-bootstrap endpoint on a separately frozen held-out population"}


def validate_visual(predictions, version):
    # Input checks adapted from release/code/score_benchmark.py without its parquet dependency.
    for row in predictions:
        for canonical, alias in (("printed_inscription_id", "inscription_number"), ("classification_literal", "classification_code")):
            if canonical not in row and alias not in row:
                raise ValueError("Visual predictions require " + canonical)
            if canonical in row and alias in row and row[canonical] != row[alias]:
                raise ValueError("Conflicting canonical and alias values")
            value = row.get(canonical, row.get(alias))
            if value is not None and not isinstance(value, str):
                raise ValueError("Inscription and classification identifiers must be strings or null")
            row[alias] = value
        if version in ("v2", "v3") and row.get("section") not in ("number_order", "end_sorted", "beginning_sorted"):
            raise ValueError("v2/v3 visual predictions require a valid section")
        if not isinstance(row.get("units"), list):
            raise ValueError("Visual predictions require units")
        for unit in row["units"]:
            c = unit.get("confidence")
            if isinstance(c, bool) or not isinstance(c, (int, float)) or not math.isfinite(c) or not 0 <= c <= 1:
                raise ValueError("Every visual unit requires finite confidence in [0, 1]")
            if not unit.get("alternatives"):
                raise ValueError("Every predicted unit requires ranked alternatives")


def visual_rows(predictions, references, version="v1"):
    validate_visual(predictions, version)
    pmap, rmap = {p["sample_index"]: p for p in predictions}, {r["sample_index"]: r for r in references}
    if len(pmap) != len(predictions) or len(rmap) != len(references) or set(pmap) != set(rmap):
        raise ValueError("Supply one prediction and one reference for every sample")
    scores = []
    for i in sorted(pmap):
        ref = rmap[i]
        r = core().score_row(pmap[i], ref)
        if version in ("v2", "v3") and ref.get("valid_printed_target") is False:
            r.update(crop_correct=False, count_agrees=False, number_correct=False,
                     classification_correct=False, uniquely_resolved_exact_sequence=False)
            for k in ("strict_top1", "strict_top5", "shape_only_top1", "shape_only_top5"):
                r[k]["whole_row_compatible"] = False
        scores.append(r)
    return core().aggregate(scores)


def release_inputs(version):
    base = ROOT / "experiments/2026-10-07-helsinki1979-digitization"
    if version == "v1":
        pred = base / "portable-inputs/data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json"
        refs = [base / f"blind/reference-{c}.json" for c in "abc"]
    else:
        folder = base / "repair" / ("2026-10-07-v2" if version == "v2" else "2026-10-08-v3")
        pred, refs = folder / "predictions.json", [folder / "blind/adjudicated-reference.json"]
    return pred, refs


def release_pages(version):
    if version == "v1":
        return {}, []
    folder = ROOT / "experiments/2026-10-07-helsinki1979-digitization/repair" / ("2026-10-07-v2" if version == "v2" else "2026-10-08-v3")
    refpath, predpath, selection = folder / "blind/adjudicated-counts.json", folder / "count-page-detections.json", folder / "blind/selection.json"
    refs, preds = read_json(refpath)["pages"], read_json(predpath)["pages"]
    pmap = {p["pdf_page"]: p["rows"] for p in preds}
    recall = legacy(RELEASE_SOURCE + "/code/score_recall.py", {"score_core": core()})
    rv3 = legacy(RELEASE_SOURCE + "/code/score_recall_v3.py") if version == "v3" else recall
    random_pages = set(read_json(selection)["random_count_pages"])
    results = {}
    for physical in ([False, True] if version == "v3" else [False]):
        pages = [rv3.recall_page(pmap[r["pdf_page"]], r, physical) if version == "v3" else recall.recall_page(pmap[r["pdf_page"]], r) for r in refs]
        results["physical_line_recall" if physical else "source_row_recall"] = {
            "random": recall.page_summary([p for p in pages if p["pdf_page"] in random_pages]),
            "stress": recall.page_summary([p for p in pages if p["pdf_page"] not in random_pages]),
            "matching_tolerance_pdf_points": 9}
    return results, [refpath, predpath, selection, RELEASE_SOURCE + "/code/score_recall.py", RELEASE_SOURCE + "/code/score_recall_v3.py"]


def pipeline_criteria(summary, version, pages):
    criteria = {name: summary[key]["rate"] is not None and summary[key]["rate"] >= threshold
                for name, key, threshold in (("crop_90", "row_crop_correctness", .90),
                                             ("number_90", "inscription_number_accuracy", .90),
                                             ("count_95", "drawn_unit_count_agreement", .95))}
    criteria["top5_rows_80"] = summary["strict_top5"]["whole_rows_all_sample"]["rate"] >= .8
    if version != "v1":
        rate = pages["source_row_recall"]["random"]["recall"]["rate"]
        criteria["random_page_recall_95"] = rate is not None and rate >= .95
    return {"negative_result_criteria": criteria, "pipeline_pass": all(criteria.values())}


def synthetic():
    rows = [
        {"id": "A", "slot": 0, "target": "s1", "predictions": [{"code": "s1", "probability": .8}, {"code": "s2", "probability": .2}]},
        {"id": "A", "slot": 1, "target": "s2", "predictions": [{"code": "s1", "probability": .6}, {"code": "s2", "probability": .4}]},
        {"id": "B", "slot": 0, "target": "unseen", "predictions": [{"code": "UNKNOWN", "probability": 1.}]}]
    k = known_slots(rows)
    pred = {"sample_index": 0, "occurrence_key": "synthetic", "pdf_page": 1,
            "inscription_number": "1", "classification_code": "A", "units": [
                {"confidence": .9, "alternatives": [{"codes": [1]}, {"codes": [2]}]},
                {"confidence": .8, "alternatives": [{"codes": [9]}, {"codes": [3]}]}]}
    ref = {"sample_index": 0, "drawn_unit_count": 2, "printed_inscription_id": "1", "classification_literal": "A",
           "crop_correct": True, "units": [{"strict_candidate_codes": [1, 2]}, {"strict_candidate_codes": [3]}]}
    v = visual_rows([pred], [ref])
    recall = legacy(RELEASE_SOURCE + "/code/score_recall.py", {"score_core": core()})
    page = recall.recall_page([{"row_anchor_y_2x": y, "margin_xyxy_2x": [0, 0, 20, 10]} for y in (20, 40, 100)],
                             {"pdf_page": 1, "columns": [{"x_extent_pdf": [0, 100], "row_centers_pdf": [10, 20], "row_count": 2}]})
    page_scores = recall.page_summary([page])
    expected = {"known_top1": 1 / 3, "known_top5": 2 / 3, "equal_text_top1": .25,
                "brier": (.04 + .36 + 1) / 3, "visual_top1": .5, "visual_top5": 1.}
    passed = (math.isclose(k["top_k"]["1"]["rate"], expected["known_top1"])
              and math.isclose(k["top_k"]["5"]["rate"], expected["known_top5"])
              and math.isclose(k["equal_text_top1"], .25)
              and math.isclose(k["calibration"]["brier"], expected["brier"])
              and v["strict_top1"]["aligned_recall"]["rate"] == .5
              and v["strict_top5"]["aligned_recall"]["rate"] == 1.
              and page_scores["recall"]["rate"] == 1. and page_scores["precision"]["rate"] == 2 / 3)
    return {"known_slot": k, "visual_row": v, "source_row_recall": page_scores, "hand_computed": expected, "pass": passed}


def configure(ap):
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--mode", choices=("known-slot", "visual-row"), default="known-slot")
    ap.add_argument("--predictions", type=Path)
    ap.add_argument("--references", type=Path)
    ap.add_argument("--baseline", type=Path, help="Matched known-slot predictions for paired component comparison")
    ap.add_argument("--local-paper", choices=("order2", "pm", "pmb", "order1"))
    ap.add_argument("--local-release", choices=("v1", "v2", "v3"))
    ap.add_argument("--version", choices=("v1", "v2", "v3"), default="v1")


def run(args):
    sources = [RELEASE_SOURCE + "/code/score_core.py", RELEASE_SOURCE + "/code/score_benchmark.py",
               "papers/001-artifact-aware-prediction/methods.md"]
    if args.synthetic:
        return envelope("restoration", synthetic(), True, sources)
    if args.local_paper:
        paths = {"order2": "experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl",
                 "order1": "experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl",
                 "pm": "results/restoration/baseline_slot_audit.jsonl", "pmb": "results/restoration/local_slot_audit.jsonl"}
        pred = ROOT / paths[args.local_paper]
        result = {"known_slot": known_slots(read_rows(pred))}
        sources.append(pred)
    elif args.local_release:
        pred, refs = release_inputs(args.local_release)
        result = {"visual_row": visual_rows(read_rows(args.predictions or pred),
                                           [r for path in refs for r in read_rows(path)], args.local_release)}
        sources += [args.predictions or pred, *refs]
        pages, paths = release_pages(args.local_release)
        result.update(pages)
        result.update(pipeline_criteria(result["visual_row"], args.local_release, pages))
        result["page_predictions_scope"] = "Frozen source pipeline geometric predictions"
        sources += paths
    elif args.predictions:
        if args.mode == "visual-row":
            if not args.references:
                raise ValueError("Visual-row scoring requires --references")
            result = {"visual_row": visual_rows(read_rows(args.predictions), read_rows(args.references), args.version)}
            sources.append(args.references)
        else:
            rows = read_rows(args.predictions)
            result = {"known_slot": known_slots(rows)}
            if args.baseline:
                result["comparison"] = paired_comparison(rows, read_rows(args.baseline))
                sources.append(args.baseline)
        sources.append(args.predictions)
    else:
        raise ValueError("Supply --predictions, --local-paper or --local-release")
    result["pass_rule"] = "A proposed model needs a frozen held-out comparator and paired component uncertainty; scoring alone grants no claim pass"
    return envelope("restoration", result, paths=sources)
