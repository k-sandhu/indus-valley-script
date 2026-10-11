"""Post-outcome literal and finite-boundary Sanskrit lexical diagnostics.

The public endpoint is aggregate evidence. Detailed corpus windows and complete
rankings remain in the ignored local witness directory. No earlier run is edited.
"""
from pathlib import Path
from collections import Counter, defaultdict
from bisect import bisect_left, bisect_right
import hashlib
import itertools
import json
import random
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "lexical-diagnostics-v3"
RAW = ROOT / "data/raw/2026-10-11-bonta-adversarial/lexical-diagnostics-v3"
VOWELS = set("aAiIuUfFxXeEoO")
HETERO_I = VOWELS - set("iI")
CONSONANTS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh")
NASALS = {c: n for cs, n in [("kKgGN", "N"), ("cCjJY", "Y"),
                            ("wWqQR", "R"), ("tTdDn", "n"),
                            ("pPbBm", "m")] for c in cs}
SLP = {"ā": "A", "ī": "I", "ū": "U", "ṛ": "f", "ṝ": "F", "ḷ": "x",
       "ṅ": "N", "ñ": "Y", "ṭ": "w", "ḍ": "q", "ṇ": "R", "ś": "S",
       "ṣ": "z", "ṃ": "M", "ṁ": "M", "ḥ": "H"}
ASP = {"kh": "K", "gh": "G", "ch": "C", "jh": "J", "ṭh": "W", "ḍh": "Q",
       "th": "T", "dh": "D", "ph": "P", "bh": "B", "ai": "E", "au": "O"}
IAST = {v: k for k, v in SLP.items() if k != "ṁ"}
IAST.update({v: k for k, v in ASP.items()})
IAST["X"] = "ḹ"


def slp(word):
    for a, b in ASP.items():
        word = word.replace(a, b)
    return "".join(SLP.get(c, c) for c in word)


def iast(word):
    return "".join(IAST.get(c, c) for c in word)


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    if path.exists():
        raise RuntimeError("Refusing to overwrite " + str(path))
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def join(left, right, limited=True):
    """Keep concatenation and apply only the declared finite boundary rules."""
    ans = {left + right}
    if not limited or not left or not right:
        return ans
    a, b = left[-1], right[0]
    if a == "m" and b in CONSONANTS:
        ans.add(left[:-1] + "M" + right)
        if b in NASALS:
            ans.add(left[:-1] + NASALS[b] + right)
    if a in "aA" and b in "aA":
        ans.add(left[:-1] + "A" + right[1:])
    if a in "iI" and b in HETERO_I:
        ans.add(left[:-1] + "y" + right)
    if a in "iI" and b in "iI":
        ans.add(left[:-1] + "I" + right[1:])
    return ans


def join_parts(parts, limited):
    words = {""}
    for part in parts:
        words = {z for a in words for z in join(a, part, limited)}
    return words


def inverse_left(pre, word, limited):
    if not pre:
        return {word}
    result = set()
    if word.startswith(pre):
        result.add(word[len(pre):])
    if not limited:
        return result
    end = pre[-1]
    if end == "m":
        for n in "MNYRnm":
            prefix = pre[:-1] + n
            if word.startswith(prefix):
                rem = word[len(prefix):]
                if rem and rem[0] in CONSONANTS and (n == "M" or NASALS.get(rem[0]) == n):
                    result.add(rem)
    if end in "aA" and word.startswith(pre[:-1] + "A"):
        result.update(v + word[len(pre):] for v in "aA")
    if end in "iI":
        if word.startswith(pre[:-1] + "y"):
            rem = word[len(pre):]
            if rem and rem[0] in HETERO_I:
                result.add(rem)
        if word.startswith(pre[:-1] + "I"):
            result.update(v + word[len(pre):] for v in "iI")
    return result


def inverse_right(suf, word, limited):
    if not suf:
        return {word}
    result = set()
    if word.endswith(suf):
        rem = word[:-len(suf)]
        result.add(rem)
        if limited and rem and suf[0] in CONSONANTS:
            if rem[-1] == "M" or NASALS.get(suf[0]) == rem[-1]:
                result.add(rem[:-1] + "m")
    if not limited:
        return result
    start = suf[0]
    if start in "aA":
        tail = "A" + suf[1:]
        if word.endswith(tail):
            result.update(word[:-len(tail)] + v for v in "aA")
    if start in HETERO_I:
        tail = "y" + suf
        if word.endswith(tail):
            result.update(word[:-len(tail)] + v for v in "iI")
    if start in "iI":
        tail = "I" + suf[1:]
        if word.endswith(tail):
            result.update(word[:-len(tail)] + v for v in "iI")
    return result


def valid_residual(word):
    return 1 <= len(word) <= 6 and bool(set(word) & VOWELS) and bool(re.fullmatch("[a-zA-Z]+", word))


class Search:
    def __init__(self, entries):
        self.entries = entries
        self.words = sorted(entries)
        self.reversed = sorted(w[::-1] for w in entries)
        self.cache = {}

    def prefixed(self, pre):
        a = bisect_left(self.words, pre)
        b = bisect_right(self.words, pre + "\uffff")
        return self.words[a:b]

    def suffixed(self, suf):
        rev = suf[::-1]
        a = bisect_left(self.reversed, rev)
        b = bisect_right(self.reversed, rev + "\uffff")
        return [w[::-1] for w in self.reversed[a:b]]

    def candidates(self, pre, suf, limited):
        key = pre, suf, limited
        if key in self.cache:
            return self.cache[key]
        if pre:
            prefixes = {pre}
            if limited and pre[-1] == "m":
                prefixes.update(pre[:-1] + n for n in "MNYRnm")
            if limited and pre[-1] in "aA":
                prefixes.add(pre[:-1] + "A")
            if limited and pre[-1] in "iI":
                prefixes.update({pre[:-1] + "y", pre[:-1] + "I"})
            words = {w for p in prefixes for w in self.prefixed(p)}
        elif suf:
            suffixes = {suf}
            if limited and suf[0] in "aA":
                suffixes.add("A" + suf[1:])
            if limited and suf[0] in "iI":
                suffixes.add("I" + suf[1:])
            if limited and suf[0] in HETERO_I:
                suffixes.add("y" + suf)
            words = {w for s in suffixes for w in self.suffixed(s)}
        else:
            words = self.words
        hits = defaultdict(set)
        for word in words:
            for remainder in inverse_left(pre, word, limited):
                for residual in inverse_right(suf, remainder, limited):
                    if valid_residual(residual) and word in join_parts([pre, residual, suf], limited):
                        hits[residual].add(word)
        self.cache[key] = dict(hits)
        return self.cache[key]

    def pattern(self, pattern, values, limited):
        slot = pattern["slot"]
        choices = [[None] if i == slot else values[s] for i, s in enumerate(pattern["window"])]
        result = defaultdict(set)
        for parts in itertools.product(*choices):
            for pre in join_parts(parts[:slot], limited):
                for suf in join_parts(parts[slot + 1:], limited):
                    for residual, words in self.candidates(pre, suf, limited).items():
                        result[residual].update(words)
        return dict(result)


def entries_for(words, entries, limit=3):
    return [{"headword_iast": iast(w), "headword_slp1": w,
             "entries": [{"entry_id": e["entry_id"], "page_column": e["page_column"]}
                         for e in entries[w]]} for w in sorted(words)[:limit]]


def rank_frame(patterns, supports, selected, entries):
    counts = Counter(r for hit in supports for r in hit)
    n = len(supports)
    selected_support = counts[selected]
    higher = sum(v > selected_support for v in counts.values())
    ties = sum(v == selected_support for v in counts.values())
    ranked = sorted(counts, key=lambda r: (-counts[r], r))
    intersection = set.intersection(*(set(x) for x in supports)) if supports else None
    aggregate = {
        "searched_patterns": n,
        "patterns_with_any_match": sum(bool(x) for x in supports),
        "residual_candidates_scored": len(counts),
        "support_histogram": {str(k): v for k, v in sorted(Counter(counts.values()).items())},
        "selected_residual_iast": iast(selected),
        "selected_pattern_support": selected_support,
        "selected_support_fraction": selected_support / n if n else None,
        "selected_competition_rank": higher + 1 if selected in counts else None,
        "rivals_with_greater_support": higher,
        "residuals_tied_at_selected_support": ties if selected in counts else 0,
        "maximum_support": max(counts.values(), default=None),
        "full_intersection_count": len(intersection) if intersection is not None else None,
        "full_intersection_top": [iast(r) for r in sorted(intersection or set())[:20]],
        "intersection_defined": bool(supports),
        "top_rivals": []}
    full = []
    for residual in ranked:
        words = {w for hit in supports for w in hit.get(residual, set())}
        row = {"residual_iast": iast(residual), "residual_slp1": residual,
               "pattern_support": counts[residual],
               "competition_rank": 1 + sum(v > counts[residual] for v in counts.values()),
               "matched_headwords": len(words), "headwords": entries_for(words, entries)}
        full.append(row)
    aggregate["top_rivals"] = full[:20]
    return aggregate, {"ranking": full, "patterns": patterns,
                       "pattern_hits": [{r: sorted(w) for r, w in hit.items()} for hit in supports]}


def seed_values(row):
    if row["label"] == "AS":
        return ["as"]
    if row["label"] == "ISH":
        return ["IS", "Iz"]
    if row["label"] == "ASTI":
        return ["asti"]
    return sorted({slp(x.strip()) for x in re.split(r"[,/]", (row.get("proposed_variants") or "").split(";")[0])
                   if re.fullmatch(r"[a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]+", x.strip())})


def productivity(search, stem, limited, orientation):
    pre, suf = ("", stem) if orientation == "residual_then_anchor" else (stem, "")
    hits = search.candidates(pre, suf, limited)
    words = {w for ws in hits.values() for w in ws}
    return {"residual_candidates": len(hits), "headword_count": len(words)}, hits


def main():
    protocol_path = OUT / "PROTOCOL.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    for row in protocol["inputs"]:
        if digest(ROOT / row["path"]) != row["sha256"]:
            raise RuntimeError("Input changed after protocol: " + row["path"])
    if (OUT / "RESULTS.json").exists() or RAW.exists():
        raise RuntimeError("Preserve completed or partial lexical endpoints")
    RAW.mkdir(parents=True)
    dictionary_path = protocol["inputs"][0]["path"]
    entries = load(dictionary_path)
    search = Search(entries)
    witness = load(protocol["inputs"][1]["path"])
    catalogue = load("data/raw/2026-10-08-bonta-review/pdf-2026-10-09-v1/sign-catalogue-v2.json")
    original = {r["sign_id"]: r for r in load("experiments/2026-10-08-bonta-review/pdf-2026-10-09-v1/mapping-v1-frozen.json")["rows"]}
    first = {r["sign_id"]: r for r in load(protocol["inputs"][5]["path"])["rows"]}
    second = {r["sign_id"]: r for r in load(protocol["inputs"][6]["path"])["rows"]}
    values = defaultdict(set)
    disjoint = []
    imported_disputed = set()
    union_disputed = set()
    for row in catalogue:
        if row.get("table_entry") is None:
            continue
        sign = row["sign_id"]
        for code in original.get(sign, {}).get("wells_candidates", []):
            values[code].update(seed_values(row))
        a = set(first.get(sign, {}).get("wells_candidates", []))
        b = set(second.get(sign, {}).get("wells_candidates", []))
        if a and b and not a & b:
            original_codes = set(original.get(sign, {}).get("wells_candidates", []))
            imported_disputed.update(original_codes)
            union_disputed.update(a | b | original_codes)
            disjoint.append({"source_id": sign, "label": row["label"],
                             "first_codes": sorted(a), "second_codes": sorted(b),
                             "original_imported_codes": sorted(original_codes)})
    values = {c: sorted(v) for c, v in values.items() if v}
    for anchor in load(protocol["inputs"][4]["path"]):
        for code in anchor["codes"]:
            values[code] = [slp(anchor["preferred_probe"])]
    raw_text = (ROOT / protocol["inputs"][2]["path"]).read_text(encoding="utf-8")
    attestations = []
    for case in protocol["attestation_checks"]:
        word = slp(case["headword_iast"])
        matching = [e for e in entries.get(word, []) if e["entry_id"] == case["entry_id"]]
        assert matching, case
        line = re.search(r"<L>" + re.escape(case["entry_id"]) + r"<pc>([^<\n]+)<k1>([^<\n]+)", raw_text)
        assert line and line[2] == word, case
        attestations.append({**case, "headword_slp1": word, "page_column": line[1],
                             "verified_in_full_mw_text_and_index": True})
    print("Exact MW checks: " + json.dumps(attestations, ensure_ascii=False), flush=True)
    case_results = []
    private_cases = []
    earlier = {r["code"]: r for r in load(protocol["inputs"][9]["path"])["rows"]}
    for case in protocol["selected_cases"]:
        code, anchor, selected = case["code"], case["anchor_code"], case["residual_slp1"]
        patterns = witness[code]["patterns"]
        target_index = next(i for i, p in enumerate(patterns) if p["window"] == [code, anchor])
        row = {"code": code, "anchor_code": anchor, "selected_residual_slp1": selected,
               "original_searched_patterns": len(patterns), "models": {}, "selected_anchor_attestations": []}
        private = {"code": code, "models": {}}
        for limited in (False, True):
            model = "limited_join" if limited else "literal"
            supports = [search.pattern(p, values, limited) for p in patterns]
            target_hits = supports[target_index]
            row["models"][model] = {"motivating_window_residual_candidates": len(target_hits), "frames": {}}
            private["models"][model] = {}
            for name, excluded in [("all_original", set()), ("exclude_imported_disjoint", imported_disputed),
                                   ("exclude_either_coder_disjoint", union_disputed)]:
                keep = [i for i, p in enumerate(patterns) if not set(p["window"]) & excluded]
                agg, detail = rank_frame([patterns[i] for i in keep], [supports[i] for i in keep], selected, entries)
                agg["excluded_pattern_count"] = len(patterns) - len(keep)
                agg["excluded_object_family_count"] = len({f for i, p in enumerate(patterns) if i not in keep for f in p["object_families"]})
                agg["retained_object_family_count"] = len({f for i in keep for f in patterns[i]["object_families"]})
                agg["motivating_window_retained"] = target_index in keep
                row["models"][model]["frames"][name] = agg
                private["models"][model][name] = detail
            literal_aggregate = row["models"][model]["frames"]["all_original"]
            if not limited:
                assert len(target_hits) == earlier[code]["exact_target_candidate_classes"]
                assert literal_aggregate["selected_pattern_support"] == earlier[code]["selected_residual_exact_pattern_support"]
        for word_iast in case["alternative_anchor_iast"]:
            word = slp(word_iast)
            literal = selected + word
            forms = join(selected, word)
            matches = forms & entries.keys()
            row["selected_anchor_attestations"].append({"anchor_iast": word_iast,
                "literal_query_iast": iast(literal), "literal_query_slp1": literal,
                "literal_attested": literal in entries,
                "bounded_query_forms_iast": sorted(iast(w) for w in forms),
                "bounded_join_attested": bool(matches), "exact_attested_forms": entries_for(matches, entries, 10)})
        case_results.append(row)
        private_cases.append(private)
        print("Case " + code + ": " + json.dumps({m: {f: {k: v for k, v in a.items() if k in ("searched_patterns", "selected_pattern_support", "selected_competition_rank", "rivals_with_greater_support", "full_intersection_count")}
              for f, a in data["frames"].items()} for m, data in row["models"].items()}), flush=True)
    # The original draws were not saved. A named independent stream is fixed here.
    rng = random.Random(protocol["controls"]["seed"])
    all_stems = sorted({slp(w) for a in protocol["new_semantic_anchors"] for w in [a["anchor"]] + a["alternatives"]})
    lengths = sorted({len(s) for s in all_stems})
    samples = {}
    for length in lengths:
        pool = [w for w in search.words if len(w) == length]
        samples[length] = rng.sample(pool, min(1000, len(pool)))
    control_metrics = {}
    for length, sample in samples.items():
        print("Productivity controls, SLP1 length " + str(length) + ": " + str(len(sample)), flush=True)
        for limited in (False, True):
            for orientation in ("residual_then_anchor", "anchor_then_residual"):
                metrics = [productivity(search, stem, limited, orientation)[0] for stem in sample]
                control_metrics[length, limited, orientation] = metrics
    productivity_rows = []
    for anchor in protocol["new_semantic_anchors"]:
        row = {"anchor_iast": anchor["anchor"], "phonetic_windows_asserted": False,
               "scope": "Two-component dictionary-productivity stress test for semantic comparison words; no corpus sound assignment.", "comparisons": []}
        for name in [anchor["anchor"]] + anchor["alternatives"]:
            stem = slp(name)
            item = {"stem_iast": name, "stem_slp1": stem, "stem_length": len(stem),
                    "dictionary_attested": stem in entries, "stem_entries": entries_for({stem} & entries.keys(), entries), "models": {}}
            for limited in (False, True):
                model = "limited_join" if limited else "literal"
                item["models"][model] = {}
                for orientation in ("residual_then_anchor", "anchor_then_residual"):
                    actual, hits = productivity(search, stem, limited, orientation)
                    controls = control_metrics[len(stem), limited, orientation]
                    control_sizes = [x["residual_candidates"] for x in controls]
                    top = sorted(hits, key=lambda r: (-len(hits[r]), r))[:10]
                    item["models"][model][orientation] = {**actual,
                        "controls": len(controls), "control_median_residual_candidates": statistics.median(control_sizes),
                        "control_fraction_at_least_as_many_residuals": sum(n >= actual["residual_candidates"] for n in control_sizes) / len(control_sizes),
                        "top_residuals": [{"residual_iast": iast(r), "matched_headwords": len(hits[r]), "headwords": entries_for(hits[r], entries)} for r in top]}
            row["comparisons"].append(item)
        productivity_rows.append(row)
    # Meaningful exact checks of the finite parser and the known correction.
    assert "saMvAha" in join("sam", "vAha") and "saMvAha" not in join("sam", "vAha", False)
    assert "sAMSa" in join("sa", "aMSa") and "sAMSa" not in join("sa", "aMSa", False)
    assert "atyanta" in join("ati", "anta")
    assert "atIndriya" in join("ati", "indriya")
    assert "saNgama" in join("sam", "gama")
    assert "saYcaya" in join("sam", "caya")
    for left, right in [("sam", "vAha"), ("sam", "gama"), ("sa", "aMSa"), ("ati", "anta"), ("ati", "indriya")]:
        for word in join(left, right):
            assert right in inverse_left(left, word, True)
            assert left in inverse_right(right, word, True)
    results = {"status": "Exploratory post-outcome diagnostics", "dictionary_headwords": len(entries),
               "model_scope": protocol["models"], "crosswalk_disputes": disjoint,
               "original_imported_disputed_codes": sorted(imported_disputed), "either_coder_disputed_codes": sorted(union_disputed),
               "attestation_checks": attestations, "cases": case_results,
               "new_anchor_productivity": productivity_rows,
               "controls": {**protocol["controls"], "length_pool_counts": {str(n): sum(len(w) == n for w in search.words) for n in lengths}},
               "interpretation": "Exact dictionary support and rival ranks measure the declared search model. They are not probabilities of ancient readings. Limited joins repair named literal failures without supplying general Sanskrit morphology."}
    write(RAW / "pattern-rankings-and-witnesses.json", {"cases": private_cases})
    write(RAW / "control-headword-identities.json", {"seed": protocol["controls"]["seed"], "samples": {str(k): v for k, v in samples.items()}})
    write(OUT / "RESULTS.json", results)
    code_path = Path(__file__)
    write(OUT / "verification.json", {"status": "pass", "checks": ["Two asserted MW records match full text and pinned index",
        "Literal target candidate counts and selected pattern supports reproduce every run-v2 motivating case",
        "Finite join forward/inverse tests pass for anusvara, velar/palatal nasals and vowel joins",
        "Every recovered residual obeys length/vowel bounds and reproduces an exact headword by forward join"],
        "protocol_sha256": digest(protocol_path), "amendment_sha256": digest(OUT / "AMENDMENT-01.json"),
        "code_sha256": digest(code_path), "inputs": protocol["inputs"],
        "public_output": {"path": (OUT / "RESULTS.json").relative_to(ROOT).as_posix(), "sha256": digest(OUT / "RESULTS.json")},
        "local_outputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in RAW.iterdir() if p.is_file()],
        "scope": "Exact computations and source integrity in this finite post-outcome dictionary search; no semantic validation."})
    report = ["# Lexical repair and rival review", "",
              "The finite join model verifies saṃvāha (MW 226133) and sāṃśa (240923), while preserving the absence of their unjoined queries samvāha and saaṃśa. The full pinned text and the alphabetic dictionary index agree on these records. All literal counts reproduce the preceding run. The repaired model applies the same stated boundary rules to every candidate residual, and scores all recovered rivals across each sign's original searched patterns.", "",
              "| Code and selected comparison | Model | Patterns | Selected support | Rank with ties | Rivals with greater support | Full intersection |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for row in case_results:
        for model, data in row["models"].items():
            a = data["frames"]["all_original"]
            report.append(f"| W{row['code']} / {iast(row['selected_residual_slp1'])} | {model} | {a['searched_patterns']} | {a['selected_pattern_support']} | {a['selected_competition_rank']} | {a['rivals_with_greater_support']} | {a['full_intersection_count']} |")
    report.extend(["", "The rank is one plus the number of residuals with strictly greater pattern support. Multiple residuals can share it. A pattern contributes at most once to a residual, regardless of repeated objects or dictionary senses. The full search rankings and corpus windows are retained locally; the public [results](RESULTS.json) publish aggregate histograms and bounded leading rivals with exact dictionary entry/page identifiers.", "",
                   "Crosswalk sensitivities remove windows containing either original imported disputed codes or the union of both coders' disjoint Table 18 candidate sets. Both frames and their remaining pattern/family counts appear in the results. Removing every pattern leaves an undefined intersection, recorded as null. A disappeared frame supplies no positive lexical evidence.", "",
                   "The five new semantic anchors, bhārin, varga, dvāra, kṛṣi and lāṅgala, have no asserted phonetic windows in this iteration. Their stress tests enumerate two-component MW headwords with unknown components of one to six SLP1 letters containing a vowel, in both component orders. Fixed alternative stems and samples of up to 1,000 dictionary headwords of the same SLP1 length show how readily this construction produces alternatives. The independent control seed is 2026101103. The earlier control identities were not saved, so those draws cannot be replayed by identity.", "",
                   "The join rules cover final m before consonants, a/ā coalescence and i/ī vowel joins. Literal forms remain available. The inverse search forward-verifies each candidate against an exact indexed headword. General morphological parsing, arbitrary editing, voicing, retroflexion and the earlier broad normalization are excluded from this repair because they would enlarge the match space without a fixed linguistic model. Other Sanskrit joins remain outside its coverage.", "",
                   "The [protocol](PROTOCOL.json) and [pre-calculation amendment](AMENDMENT-01.json) were written before this computation. [Verification](verification.json) records input/code/output hashes and exact checks. These post-outcome counts describe dictionary-search flexibility and crosswalk sensitivity; they do not estimate historical reading probabilities."])
    report_path = OUT / "REPORT.md"
    if report_path.exists():
        raise RuntimeError("Refusing to overwrite report")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Completed " + str(OUT.relative_to(ROOT)), flush=True)


if __name__ == "__main__":
    main()
