"""Compare my_values.json (from recompute.py) with the run summaries and write verification.json.

Run after recompute.py: python -X utf8 compare.py
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = EXP.parents[1]
COUNT_TOL = 1e-6
RATIO_TOL = 1e-3


def load(p):
    return json.loads(Path(p).read_text(encoding="utf8"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


mine = load(HERE / "my_values.json")
s1 = load(EXP / "step1-signs/run-2026-10-12/summary.json")
s2 = load(EXP / "step2-image-text/run-2026-10-12-v2/summary.json")
s3 = load(EXP / "step3-segmentation/run-linebreaks-2026-10-12-v2/summary.json")
s4 = load(EXP / "step4-numerals/run-2026-10-12/summary.json")
s6 = load(EXP / "step6-language/run-2026-10-12/summary.json")

checks = []


def add(check, name, definition, my_value, run_value, run_key, kind):
    tol = COUNT_TOL if kind == "count" else RATIO_TOL
    agree = abs(float(my_value) - float(run_value)) <= tol
    checks.append({"check": check, "name": name, "definition": definition, "my_value": my_value,
                   "run_value": run_value, "run_key": run_key, "tolerance": tol, "agree": agree})


D1 = "Distinct clean reading-order texts (1,859 texts, 8,535 signs); W = font code, B = coder-1 base family."
p1 = mine["check1_profiles"]
for inv in ("W", "B"):
    add(1, f"profile {inv}: attested types", D1, p1[inv]["types"], s1["profiles"][inv]["types"],
        f"step1 summary profiles.{inv}.types", "count")
    add(1, f"profile {inv}: share of types occurring once", D1, p1[inv]["share_types_once"],
        s1["profiles"][inv]["once_share"], f"step1 summary profiles.{inv}.once_share", "ratio")
    add(1, f"profile {inv}: token share of 30 commonest types", D1, p1[inv]["top30_token_share"],
        s1["profiles"][inv]["top30_token_share"], f"step1 summary profiles.{inv}.top30_token_share", "ratio")

D2 = ("Adjusted Rand index between coder-1 and coder-2 base labels over the 577 attested codes; "
      "weighted version builds the contingency table with each code contributing its token count.")
p2 = mine["check2_coder_ari"]
add(2, "coder ARI, unweighted", D2, p2["ari_unweighted"], s1["coder_agreement"]["ari_unweighted"],
    "step1 summary coder_agreement.ari_unweighted", "ratio")
add(2, "coder ARI, token-weighted", D2, p2["ari_token_weighted"], s1["coder_agreement"]["ari_token_weighted"],
    "step1 summary coder_agreement.ari_token_weighted", "ratio")

D3 = ("TAB:C faces grouped by object_family_id; normalized symbol labels unioned per object; texts are complete, "
      "known-sign, nonempty faces. Among single-class objects with a text, distinct texts on 2+ objects, and those "
      "whose objects share one class.")
p3 = mine["check3_copper_2a"]
add(3, "2a copper: texts on 2+ single-class objects", D3, p3["shared_texts"], s2["copper"]["2a"]["texts_on_2plus_objects"],
    "step2 v2 summary copper.2a.texts_on_2plus_objects", "count")
add(3, "2a copper: of those, all objects one class", D3, p3["shared_texts_one_class"], s2["copper"]["2a"]["class_pure"],
    "step2 v2 summary copper.2a.class_pure", "count")
add(3, "2a copper: single-class objects with a text", D3, p3["single_class_objects_with_text"],
    s2["copper"]["2a"]["objects_with_one_class_and_text"], "step2 v2 summary copper.2a.objects_with_one_class_and_text", "count")

D4 = ("Copper-class-specific contiguous bigrams and trigrams (one-sign text contributes itself), specific against other "
      "labelled copper classes; distinct (text, class) pairs on single-class seal objects of types SEAL, SEAL:S, SEAL:R, "
      "SEAL:C, SEAL:CY; hits are pairs whose class matches and whose text contains a specific n-gram of that class.")
p4 = mine["check4_2d"]
d2d = s2["2d_copper_to_seals"]
add(4, "2d: matching hits summed over classes", D4, p4["hits_total"], d2d["matching_hits"],
    "step2 v2 summary 2d_copper_to_seals.matching_hits", "count")
add(4, "2d: seal (text, class) pairs", D4, p4["pairs"], d2d["seal_text_animal_pairs"],
    "step2 v2 summary 2d_copper_to_seals.seal_text_animal_pairs", "count")
for c, h in p4["hits_by_class"].items():
    add(4, f"2d: hits for {c} (supplementary)", D4, h, d2d["per_class"][c]["hits_matching"],
        f"step2 v2 summary 2d_copper_to_seals.per_class.{c}.hits_matching", "count")
    add(4, f"2d: specific n-grams for {c} (supplementary)", D4, p4["copper_classes"][c]["specific_ngrams"],
        d2d["per_class"][c]["specific_ngrams"], f"step2 v2 summary 2d_copper_to_seals.per_class.{c}.specific_ngrams", "count")

D5 = ("Faces with '/' and no '[', ']' or '000'; lines split on '/', signs on '-', reversed unless L/R. Found = contiguous "
      "in a distinct clean text whose family set is not exactly this face's family. Line windows: each line of length "
      ">= 2. Straddle windows: per adjacent pair and order, windows of length len(A) and len(B) (each >= 2) crossing the "
      "junction. Better order = higher of the per-face forward and reverse straddle rates.")
p5 = mine["check5_linebreaks"]
cb = s3["conservative_best_order"]
add(5, "line breaks: faces used", D5, p5["faces_used"], s3["faces_used"], "step3 v2 summary faces_used", "count")
add(5, "line breaks: faces line rate > better-order straddle", D5, p5["line_gt_better"], cb["faces_line_higher"],
    "step3 v2 summary conservative_best_order.faces_line_higher", "count")
add(5, "line breaks: faces better-order straddle > line rate", D5, p5["line_lt_better"], cb["faces_straddle_higher"],
    "step3 v2 summary conservative_best_order.faces_straddle_higher", "count")
add(5, "line breaks: two-sided exact sign-test p (better order)", D5, p5["sign_test_p_better"], cb["sign_test_two_sided_p"],
    "step3 v2 summary conservative_best_order.sign_test_two_sided_p", "ratio")
add(5, "line breaks: faces line rate > pooled straddle (supplementary)", D5, p5["line_gt_pooled"], s3["faces_line_higher"],
    "step3 v2 summary faces_line_higher", "count")
add(5, "line breaks: faces pooled straddle > line rate (supplementary)", D5, p5["line_lt_pooled"], s3["faces_straddle_higher"],
    "step3 v2 summary faces_straddle_higher", "count")
add(5, "line breaks: mean better-order straddle rate (supplementary)", D5, p5["mean_better_rate"],
    cb["mean_straddle_rate_best_order"], "step3 v2 summary conservative_best_order.mean_straddle_rate_best_order", "ratio")
add(5, "line breaks: mean pooled straddle rate (supplementary)", D5, p5["mean_pooled_rate"], s3["mean_straddle_rate"],
    "step3 v2 summary mean_straddle_rate", "ratio")
add(5, "line breaks: pooled straddle rate (supplementary)", D5, p5["pooled_straddle_rate"], s3["pooled_straddle_rate"],
    "step3 v2 summary pooled_straddle_rate", "ratio")
add(5, "line breaks: mean line rate (supplementary)", D5, p5["mean_line_rate"], s3["mean_line_rate"],
    "step3 v2 summary mean_line_rate", "ratio")
add(5, "line breaks: pooled line rate (supplementary)", D5, p5["pooled_line_rate"], s3["pooled_line_rate"],
    "step3 v2 summary pooled_line_rate", "ratio")

D6 = ("Numeral codes: coder-1 base B001 or B031 with nonempty count. Item = next sign or </s>; tokens followed by a numeral "
      "are skipped. Items with >= 5 tokens qualify; top share is token-weighted over qualifying items.")
p6 = mine["check6_numerals"]
iv = s4["ivs_clean"]
add(6, "numerals: tokens", D6, p6["tokens"], iv["tokens"], "step4 summary ivs_clean.tokens", "count")
add(6, "numerals: items with >= 5 tokens", D6, p6["items_ge5"], iv["qualifying_items"], "step4 summary ivs_clean.qualifying_items", "count")
add(6, "numerals: mean distinct values per item", D6, p6["mean_distinct_values"], iv["mean_distinct_values_per_item"],
    "step4 summary ivs_clean.mean_distinct_values_per_item", "ratio")
add(6, "numerals: token-weighted commonest-value share", D6, p6["token_weighted_top_share"], iv["token_weighted_top_value_share"],
    "step4 summary ivs_clean.token_weighted_top_value_share", "ratio")

D7 = ("Normalized entropy (bits / log2 of distinct signs in the set) of first sign minus that of last sign, over distinct "
      "texts of length >= 2. Sumerian: corpus sumerian, kind seal, concatenated word_units, records with an empty word "
      "unit skipped, deduplicated.")
p7 = mine["check7_edge_asymmetry"]
add(7, "edge asymmetry: IVS clean", D7, p7["ivs"]["asymmetry"],
    s6["profiles"]["ivs_all_clean"]["edge_asymmetry"]["asymmetry_initial_minus_final"],
    "step6 summary profiles.ivs_all_clean.edge_asymmetry.asymmetry_initial_minus_final", "ratio")
add(7, "edge asymmetry: Sumerian seal legends, sign level", D7, p7["sumerian_seal"]["asymmetry"],
    s6["profiles"]["sumerian_seals"]["sign_level"]["edge_asymmetry"]["asymmetry_initial_minus_final"],
    "step6 summary profiles.sumerian_seals.sign_level.edge_asymmetry.asymmetry_initial_minus_final", "ratio")
add(7, "edge asymmetry: Sumerian distinct texts (supplementary)", D7, p7["sumerian_seal"]["texts"],
    s6["profiles"]["sumerian_seals"]["sign_level"]["edge_asymmetry"]["texts"],
    "step6 summary profiles.sumerian_seals.sign_level.edge_asymmetry.texts", "count")

DIAG = {
    "line_rate_disagreement": (
        "The run's linebreaks.py appends line windows inside the loop over adjacent line pairs (for L in (A, B)), so a "
        "line between two others is counted twice. Four of the 72 faces have three or more lines. Counting each line once "
        "gives 133 line windows, mean line rate 0.22685 and pooled line rate 0.24060; the run reports 137, 0.22917 and "
        "0.24818. recompute.py reproduces the run's values exactly when interior lines are counted twice "
        "(check5_diagnostic_interior_lines_twice). The face-level sign counts (23 vs 4 and 25 vs 3) and p-values are the "
        "same under both countings."),
}

result = {
    "description": "Independent recomputation of structure-first headline numbers; code in recompute.py and compare.py.",
    "tolerances": {"count": COUNT_TOL, "ratio": RATIO_TOL},
    "inputs_sha256": {
        "data/normalized/lipi_clean_rtl_singleline.jsonl": sha(ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"),
        "data/normalized/lipi_observed_faces.jsonl": sha(ROOT / "data/normalized/lipi_observed_faces.jsonl"),
        "step1-signs/sign_components_v1.tsv": sha(EXP / "step1-signs/sign_components_v1.tsv"),
        "step1-signs/second-coder/components_coder2.tsv": sha(EXP / "step1-signs/second-coder/components_coder2.tsv"),
        "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl":
            sha(ROOT / "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl"),
    },
    "frame": mine["frame"],
    "assigned_checks_agree": all(c["agree"] for c in checks if "supplementary" not in c["name"]),
    "all_checks_agree": all(c["agree"] for c in checks),
    "checks": checks,
    "diagnosis": DIAG,
}
(HERE / "verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
for c in checks:
    print(f"{'OK ' if c['agree'] else 'DIFF'} {c['check']} {c['name']}: mine {c['my_value']} run {c['run_value']}")
print("assigned agree:", result["assigned_checks_agree"], "all agree:", result["all_checks_agree"])
