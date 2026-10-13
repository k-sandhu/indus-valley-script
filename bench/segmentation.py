"""Score complete word boundaries and partially observed catalogue line divisions."""
from collections import Counter
from pathlib import Path
import random

from .common import ROOT, STRUCTURE_SOURCE, envelope, legacy, read_json, read_rows


def segmenters():
    return legacy(STRUCTURE_SOURCE + "/segmenters.py")


def validate_boundaries(boundaries, lengths):
    if len(boundaries) != len(lengths):
        raise ValueError("Boundary count differs from text count")
    for cuts, length in zip(boundaries, lengths):
        if not isinstance(cuts, list) or any(isinstance(c, bool) or not isinstance(c, int) or not 1 <= c < length for c in cuts):
            raise ValueError("Boundaries must be internal integer positions")
        if cuts != sorted(set(cuts)):
            raise ValueError("Boundaries must be sorted and unique")


def score(gold, predictions, texts, complete=True):
    if not texts or any(len(t) < 1 for t in texts):
        raise ValueError("Score nonempty texts")
    validate_boundaries(gold, list(map(len, texts)))
    validate_boundaries(predictions, list(map(len, texts)))
    if complete:
        return {"reference": "complete word boundaries", **segmenters().boundary_scores(gold, predictions, texts)}
    hits = sum(len(set(g) & set(p)) for g, p in zip(gold, predictions))
    required = sum(map(len, gold))
    other = sum(len(set(p) - set(g)) for g, p in zip(gold, predictions))
    other_slots = sum(len(t) - 1 - len(g) for t, g in zip(texts, gold))
    return {"reference": "required line divisions; other positions unlabelled", "required_boundaries": required,
            "hits": hits, "boundary_recall": hits / required if required else None,
            "boundary_precision": None, "boundary_f1": None,
            "boundary_rate_elsewhere": other / other_slots if other_slots else None,
            "reason": "Catalogue line breaks supply positive boundary evidence; no negative labels"}


def predict(texts, method, sweeps=2000):
    if method == "all_boundaries":
        return [list(range(1, len(t))) for t in texts]
    if method == "no_boundaries":
        return [[] for _ in texts]
    if method == "dp_unigram":
        return segmenters().dp_unigram(texts, sweeps=sweeps)
    return getattr(segmenters(), method)(texts)


def cohorts():
    common = legacy(STRUCTURE_SOURCE + "/common.py")
    rehearsal = legacy(STRUCTURE_SOURCE + "/step5-rehearsal/rehearse_segmentation.py",
                       {"common": common, "segmenters": segmenters()})
    records = read_rows(common.BRONZE)
    lengths = [len(r["text"]) for r in common.load_clean()]
    rng = random.Random(common.SEED + 5)
    def pool(corpus, kind):
        seen, items = set(), []
        for r in records:
            if r["corpus"] != corpus or r["kind"] != kind:
                continue
            g = rehearsal.gold_from(r)
            if g and len(g[0]) >= 2 and g[0] not in seen:
                seen.add(g[0])
                items.append(g)
        return items
    return {"sumerian_seals_all": pool("sumerian", "seal"),
            "sumerian_lines_matched": rehearsal.matched_sample(pool("sumerian", "natural_line"), lengths, rng),
            "egyptian_glyph_sentences_matched": rehearsal.matched_sample(pool("egyptian", "glyph_sentence"), lengths, rng),
            "akkadian_letter_lines_matched": rehearsal.matched_sample(pool("akkadian", "natural_line"), lengths, rng)}


def local_rehearsal(methods, sweeps=2000):
    result = {}
    for name, items in cohorts().items():
        texts, gold = [t for t, b in items], [b for t, b in items]
        result[name] = {"texts": len(texts), "units": sum(map(len, texts)),
                        "scores": {m: score(gold, predict(texts, m, sweeps), texts) for m in methods}}
    return result


def local_lines(methods, sweeps=2000):
    common = legacy(STRUCTURE_SOURCE + "/common.py")
    lines = legacy(STRUCTURE_SOURCE + "/step3-segmentation/linebreaks.py", {"common": common})
    clean = [r["text"] for r in common.load_clean()]
    frozen = read_json(common.RAW / "step3-linebreak-faces.json")
    faces = {r["record_id"]: r for r in read_rows(common.FACES)}
    joined, gold, orders = [], [], []
    for r in frozen:
        ls = lines.lines_of(faces[r["face"]])
        if ls is None:
            raise ValueError("Frozen line face no longer parses")
        for order, seq in (("forward", ls), ("reverse", ls[::-1])):
            text, cuts = [], []
            for line in seq:
                text.extend(line)
                cuts.append(len(text))
            joined.append(tuple(text))
            gold.append(cuts[:-1])
            orders.append(order)
    result = {"clean_texts": len(clean), "joined_faces_per_order": len(frozen), "scores": {}}
    for method in methods:
        pred = predict(clean + joined, method, sweeps)[len(clean):]
        result["scores"][method] = {}
        for order in ("forward", "reverse"):
            idx = [i for i, o in enumerate(orders) if o == order]
            result["scores"][method][order] = score([gold[i] for i in idx], [pred[i] for i in idx],
                                                     [joined[i] for i in idx], complete=False)
    return result


def synthetic():
    texts = [tuple("abcde"), tuple("xyz")]
    gold, proposed = [[2, 4], [1]], [[2, 3], [1, 2]]
    actual = score(gold, proposed, texts)
    baselines = {m: score(gold, predict(texts, m), texts) for m in ("all_boundaries", "no_boundaries")}
    lines = score(gold, proposed, texts, complete=False)
    expected = {"precision": 2 / 4, "recall": 2 / 3, "f1": 4 / 7}
    passed = (actual["boundary_precision"] == expected["precision"]
              and actual["boundary_recall"] == expected["recall"]
              and abs(actual["boundary_f1"] - expected["f1"]) < 1e-12
              and lines["boundary_precision"] is None and lines["boundary_f1"] is None
              and lines["boundary_recall"] == 2 / 3)
    return {"scores": actual, "baselines": baselines, "line_divisions": lines, "hand_computed": expected, "pass": passed}


def configure(ap):
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--local-rehearsal", action="store_true")
    ap.add_argument("--local-lines", action="store_true")
    ap.add_argument("--references", type=Path, help="Rows: id, length, boundaries, complete")
    ap.add_argument("--predictions", type=Path, help="Rows: id, boundaries")
    ap.add_argument("--methods", default="branching_entropy,greedy_ngram,all_boundaries,no_boundaries")
    ap.add_argument("--sweeps", type=int, default=2000)


def run(args):
    sources = [STRUCTURE_SOURCE + "/segmenters.py", STRUCTURE_SOURCE + "/step5-rehearsal/rehearse_segmentation.py",
               STRUCTURE_SOURCE + "/review/review_step3_segmenter_breaks.py"]
    if args.synthetic:
        return envelope("segmentation", synthetic(), True, sources)
    methods = args.methods.split(",")
    if not set(methods) <= {"branching_entropy", "greedy_ngram", "dp_unigram", "all_boundaries", "no_boundaries"}:
        raise ValueError("Unknown segmentation method")
    if args.local_rehearsal:
        result = {"cohorts": local_rehearsal(methods, args.sweeps)}
        sources += ["data/normalized/lipi_clean_rtl_singleline.jsonl", "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl"]
    elif args.local_lines:
        result = {"line_divisions": local_lines(methods, args.sweeps)}
        sources += ["data/normalized/lipi_clean_rtl_singleline.jsonl", "data/normalized/lipi_observed_faces.jsonl",
                    "data/raw/2026-10-12-structure-first/step3-linebreak-faces.json"]
    else:
        if not args.references or not args.predictions:
            raise ValueError("Supply --references and --predictions")
        refs, preds = read_rows(args.references), read_rows(args.predictions)
        ids = [r["id"] for r in refs]
        pmap = {p["id"]: p for p in preds}
        if not refs or len(set(ids)) != len(refs) or len(pmap) != len(preds) or set(pmap) != set(ids):
            raise ValueError("Supply exactly one prediction for every reference id")
        complete = {r.get("complete", True) for r in refs}
        if len(complete) != 1 or not all(isinstance(v, bool) for v in complete):
            raise ValueError("Score complete references and line-only references in separate runs")
        if any(isinstance(r["length"], bool) or not isinstance(r["length"], int) or r["length"] < 1 for r in refs):
            raise ValueError("Reference lengths must be positive integers")
        texts = [tuple(range(r["length"])) for r in refs]
        gold = [r["boundaries"] for r in refs]
        result = {"scores": score(gold, [pmap[i]["boundaries"] for i in ids], texts, complete.pop()),
                  "baselines": {m: score(gold, predict(texts, m), texts, refs[0].get("complete", True))
                                for m in ("all_boundaries", "no_boundaries")}}
        sources += [args.references, args.predictions]
    result["pass_rule"] = "Frozen complete-boundary F1 improves the everywhere baseline on the declared readable cohorts; line-only evidence reports recall and cannot grant an F1 pass"
    return envelope("segmentation", result, paths=sources)
