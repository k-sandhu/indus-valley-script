"""Grouped structural tests for normalized Indus transcriptions.

Uses observation columns only. Numeric sign IDs have no assigned meanings.
PMB is a normalized multiplicative model: PM(c|length,index,stratum) times
BG(c|previous)/U(c). This is a predictive comparison, not a linguistic test.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import time

import numpy as np

UNKNOWN = "__UNKNOWN__"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_records(path, min_length=3, unique=False, reverse=False, collapse=None):
    raw = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    result, excluded = [], Counter()
    seen = set()
    for row in sorted(raw, key=lambda r: str(r.get("record_id", r.get("id", "")))):
        seq = row.get("signs_reading_rtl", row.get("sequence", row.get("signs", [])))
        seq = tuple(map(str, seq))
        if len(seq) < min_length:
            excluded["too_short"] += 1
            continue
        if any(s in {"000", "999", "P000", "?", UNKNOWN} for s in seq):
            excluded["unknown_sign"] += 1
            continue
        if row.get("max_damage", 0) or row.get("max_uncertainty", 0):
            excluded["damaged_or_uncertain"] += 1
            continue
        if row.get("complete_observed") is False or row.get("single_line") is False:
            excluded["incomplete_or_multiline"] += 1
            continue
        if collapse:
            seq = tuple(collapse.get(sign, sign) for sign in seq)
        if unique and seq in seen:
            excluded["duplicate_sequence"] += 1
            continue
        seen.add(seq)
        row = dict(row)
        row["seq"] = tuple(reversed(seq)) if reverse else seq
        row["artifact"] = str(row.get("object_family_id", row.get("artifact_id", row.get("record_id", row.get("id")))))
        row["stratum"] = (row.get("site", "MISSING"), row.get("object_type", "MISSING"))
        result.append(row)
    return result, dict(excluded)


def group_records(rows):
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def join(i, j):
        x, y = find(i), find(j)
        if x != y:
            parent[max(x, y)] = min(x, y)

    artifacts, sequences = {}, {}
    for i, row in enumerate(rows):
        for value, table in [(row["artifact"], artifacts), (row["seq"], sequences)]:
            if value in table:
                join(i, table[value])
            else:
                table[value] = i
    result = defaultdict(list)
    for i in range(len(rows)):
        result[find(i)].append(i)
    return [indices for _, indices in sorted(result.items())]


def make_folds(rows, groups, folds, seed):
    # Greedy balance by token count, randomized ties; never split a component.
    rng = random.Random(seed)
    order = list(range(len(groups)))
    rng.shuffle(order)
    order.sort(key=lambda g: sum(len(rows[i]["seq"]) for i in groups[g]), reverse=True)
    loads, assigned = [0] * folds, {}
    for group in order:
        f = min(range(folds), key=lambda j: (loads[j], j))
        for i in groups[group]:
            assigned[i] = f
        loads[f] += sum(len(rows[i]["seq"]) for i in groups[group])
    return assigned, loads


class Model:
    def __init__(self, rows, alpha):
        self.alpha = float(alpha)
        signs = sorted({s for r in rows for s in r["seq"]})
        self.signs = signs + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        self.unigram = np.full(len(self.signs), 0.5)
        self.position = defaultdict(Counter)
        self.metadata = defaultdict(Counter)
        self.bigram = defaultdict(Counter)
        for row in rows:
            seq, stratum = row["seq"], row["stratum"]
            for i, sign in enumerate(seq):
                c = self.index[sign]
                self.unigram[c] += 1
                self.position[(len(seq), i)][c] += 1
                self.metadata[(len(seq), i, stratum)][c] += 1
                if i:
                    self.bigram[self.index[seq[i - 1]]][c] += 1
        self.unigram /= self.unigram.sum()
        self.pc, self.mc, self.bc, self.combo = {}, {}, {}, {}

    def smooth(self, counts, prior):
        n = sum(counts.values())
        result = self.alpha * prior.copy()
        for c, count in counts.items():
            result[c] += count
        return result / (n + self.alpha)

    def distributions(self, length, i, stratum, prev):
        pk = (length, i)
        if pk not in self.pc:
            self.pc[pk] = self.smooth(self.position.get(pk, {}), self.unigram)
        mk = (length, i, stratum)
        if mk not in self.mc:
            self.mc[mk] = self.smooth(self.metadata.get(mk, {}), self.pc[pk])
        if prev is None:
            return self.pc[pk], self.mc[mk], self.mc[mk]
        previous = self.index.get(prev, self.index[UNKNOWN])
        if previous not in self.bc:
            self.bc[previous] = self.smooth(self.bigram.get(previous, {}), self.unigram) / self.unigram
        ck = (mk, previous)
        if ck not in self.combo:
            combined = self.mc[mk] * self.bc[previous]
            self.combo[ck] = combined / combined.sum()
        return self.pc[pk], self.mc[mk], self.combo[ck]

    def score(self, row):
        scores = {name: [] for name in ("U", "P", "PM", "PMB")}
        seq = row["seq"]
        oov = 0
        for i, sign in enumerate(seq):
            c = self.index.get(sign, self.index[UNKNOWN])
            oov += sign not in self.index
            p, pm, pmb = self.distributions(len(seq), i, row["stratum"], seq[i - 1] if i else None)
            for name, prob in [("U", self.unigram[c]), ("P", p[c]), ("PM", pm[c]), ("PMB", pmb[c])]:
                scores[name].append(math.log2(float(prob)))
        return scores, oov


def evaluate(rows, groups, assignment, folds=5, alpha=20, bootstrap=2000, seed=20261001):
    group_lookup = {i: g for g, indices in enumerate(groups) for i in indices}
    totals, token_count, noninitial, oov = Counter(), 0, 0, 0
    group_deltas = defaultdict(lambda: [0.0, 0])
    record_scores, fold_results = [], []
    for fold in range(folds):
        train = [r for i, r in enumerate(rows) if assignment[i] != fold]
        test = [(i, r) for i, r in enumerate(rows) if assignment[i] == fold]
        model = Model(train, alpha)
        fold_delta, fold_count = 0.0, 0
        for index, row in test:
            scores, unknown = model.score(row)
            count = len(row["seq"]) - 1
            delta = sum(scores["PMB"][1:]) - sum(scores["PM"][1:])
            group = group_lookup[index]
            group_deltas[group][0] += delta
            group_deltas[group][1] += count
            record_scores.append({"record_id": row.get("record_id"), "group": group, "fold": fold, "noninitial_signs": count, "PMB_minus_PM_bits": delta, "oov_tokens": unknown})
            for name in scores:
                totals[name] += sum(scores[name])
            token_count += len(row["seq"])
            noninitial += count
            oov += unknown
            fold_delta += delta
            fold_count += count
        fold_results.append({"fold": fold, "train_records": len(train), "test_records": len(test), "noninitial_signs": fold_count, "gain_bits": fold_delta / fold_count if fold_count else None})
    paired = np.array(list(group_deltas.values()), dtype=float)
    point = paired[:, 0].sum() / paired[:, 1].sum()
    ci = None
    if bootstrap:
        rng = np.random.default_rng(seed)
        draws = np.empty(bootstrap)
        for i in range(bootstrap):
            sample = paired[rng.integers(0, len(paired), len(paired))]
            draws[i] = sample[:, 0].sum() / sample[:, 1].sum()
        ci = [float(x) for x in np.quantile(draws, [0.025, 0.975])]
    return {
        "records": len(rows), "groups": len(groups), "unique_sequences": len({r["seq"] for r in rows}),
        "tokens": token_count, "noninitial_tokens": noninitial, "oov_tokens": oov,
        "gain_bits_per_noninitial_sign": float(point), "gain_95pct_group_bootstrap_ci": ci,
        "PMB_vs_PM_noninitial_perplexity_ratio": float(2 ** (-point)),
        "all_token_cross_entropy_bits": {name: -value / token_count for name, value in totals.items()},
        "folds": fold_results,
    }, record_scores


def shuffle_positions(rows, seed, metadata=False):
    rng = random.Random(seed)
    result = [dict(row, seq=list(row["seq"])) for row in rows]
    cells = defaultdict(list)
    for n, row in enumerate(rows):
        for i in range(len(row["seq"])):
            key = (len(row["seq"]), i, row["stratum"] if metadata else ())
            cells[key].append(n)
    movable = 0
    for (_, i, _), indices in cells.items():
        values = [rows[n]["seq"][i] for n in indices]
        if len(set(values)) > 1:
            movable += len(indices)
        rng.shuffle(values)
        for n, value in zip(indices, values):
            result[n]["seq"][i] = value
    for row in result:
        row["seq"] = tuple(row["seq"])
    return result, {"cells": len(cells), "movable_tokens": movable, "total_tokens": sum(len(r["seq"]) for r in rows)}


def frames(rows):
    # Frame/sign keys deduplicate whole sequences while retaining every artifact
    # alias for independent metadata auditing. Lists do not enter edge counts.
    result = defaultdict(lambda: defaultdict(list))
    for row in rows:
        seq = row["seq"]
        for i, sign in enumerate(seq):
            key = (len(seq), i, seq[:i] + ("*",) + seq[i + 1:])
            result[key][sign].append(row)
    return result


def pair_frames(frame_map):
    result = defaultdict(list)
    for key, variants in frame_map.items():
        for pair in itertools.combinations(sorted(variants), 2):
            result[pair].append(key)
    return result


def substitution_summary(rows, assignment, folds=5, seed=20261001, permutations=200):
    all_frames = frames(rows)
    pairs = pair_frames(all_frames)
    candidates = []
    for pair, contexts in sorted(pairs.items(), key=lambda item: (-len(item[1]), item[0])):
        examples = []
        sites, artifacts = set(), set()
        for key in contexts:
            values = all_frames[key]
            records = {sign: [{"record_id": r.get("record_id"), "artifact": r["artifact"], "site": r.get("site"), "object_type": r.get("object_type")} for r in values[sign]] for sign in pair}
            for sign in pair:
                for r in values[sign]:
                    sites.add(r.get("site", "MISSING"))
                    artifacts.add(r["artifact"])
            examples.append({"length": key[0], "slot_zero_based_rtl": key[1], "frame_rtl": key[2], "records": records})
        candidates.append({"pair": pair, "distinct_frames": len(contexts), "sites": sorted(sites), "artifacts": len(artifacts), "examples": examples})
    transfer_observed, discoveries, tests = 0, [], []
    fold_transfers = []
    for fold in range(folds):
        train = [r for i, r in enumerate(rows) if assignment[i] != fold]
        test = [r for i, r in enumerate(rows) if assignment[i] == fold]
        train_frames = frames(train)
        discovered = {pair for pair, contexts in pair_frames(train_frames).items() if len(contexts) >= 2}
        test_pairs = pair_frames({key: value for key, value in frames(test).items() if key not in train_frames})
        transfer = sum(len(test_pairs.get(pair, [])) for pair in discovered)
        details = [{"pair": pair, "new_frame_count": len(test_pairs[pair]), "frames": test_pairs[pair]} for pair in sorted(discovered & test_pairs.keys())]
        fold_transfers.append({"fold": fold, "discovered_pairs_with_at_least_two_frames": len(discovered), "transfer_pair_frames": transfer, "confirmed_pairs": details})
        transfer_observed += transfer
        discoveries.append((discovered, set(train_frames)))
        tests.append(test)
    null_global, null_meta = [], []
    for metadata, results in [(False, null_global), (True, null_meta)]:
        for p in range(permutations):
            total = 0
            for fold, test in enumerate(tests):
                shuffled, _ = shuffle_positions(test, seed + 100000 * (1 + metadata) + p * folds + fold, metadata)
                discovered, training_frames = discoveries[fold]
                shuffled_pairs = pair_frames({key: value for key, value in frames(shuffled).items() if key not in training_frames})
                total += sum(len(shuffled_pairs.get(pair, [])) for pair in discovered)
            results.append(total)
    def null_stats(values):
        return {"permutations": len(values), "observed_transfer_pair_frames": transfer_observed, "mean": float(np.mean(values)) if values else None, "95pct_range": [float(x) for x in np.quantile(values, [0.025, 0.975])] if values else None, "p_one_sided": (1 + sum(v >= transfer_observed for v in values)) / (1 + len(values)) if values else None, "values": values}
    return {
        "unique_sequences": len({r["seq"] for r in rows}),
        "frames_with_variants": sum(len(value) > 1 for value in all_frames.values()),
        "distinct_substitution_pairs": len(pairs),
        "pairs_repeated_across_at_least_two_frames": sum(len(contexts) >= 2 for contexts in pairs.values()),
        "top_pairs": candidates[:50],
        "fold_transfer": fold_transfers,
        "transfer_null_position": null_stats(null_global),
        "transfer_null_position_metadata": null_stats(null_meta),
    }, candidates


def run(args):
    start = time.monotonic()
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, exclusions = load_records(args.input, args.min_length, args.unique, args.reverse, collapse)
    groups = group_records(rows)
    assignment, loads = make_folds(rows, groups, args.folds, args.seed)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    audit = {
        "input": str(Path(args.input).resolve()), "input_sha256": digest(args.input),
        "source_code_sha256": digest(__file__), "parameters": vars(args), "exclusions": exclusions,
        "group_sizes": sorted([len(g) for g in groups], reverse=True), "fold_token_loads": loads,
        "grouped_by": "transitive physical artifact OR identical full sequence",
        "null_caveat": "Position shuffles preserve marginal record counts but destroy repeated-sequence cohort identity; unique-sequence sensitivity is required.",
        "equation_PMB": "normalized PM(c|L,i,site,type) * BG(c|prev)/U(c)",
        "labels": "No phonetic or semantic assignments were used.",
    }
    primary, record_scores = evaluate(rows, groups, assignment, args.folds, 20, args.bootstrap, args.seed)
    primary["smoothing_alpha"] = 20
    audit["primary"] = primary
    print(json.dumps({"stage": "primary", "result": primary}, ensure_ascii=False), flush=True)
    audit["smoothing_sensitivity"] = {}
    for alpha in [5, 100]:
        score, _ = evaluate(rows, groups, assignment, args.folds, alpha, 0, args.seed)
        audit["smoothing_sensitivity"][str(alpha)] = score
    for metadata, label in [(False, "position"), (True, "position_metadata")]:
        values = []
        mobility = None
        for p in range(args.permutations):
            shuffled, mobility = shuffle_positions(rows, args.seed + p + (10000 if metadata else 0), metadata)
            score, _ = evaluate(shuffled, groups, assignment, args.folds, 20, 0, args.seed)
            values.append(score["gain_bits_per_noninitial_sign"])
            if (p + 1) % 25 == 0:
                print(json.dumps({"stage": "conditional_null", "null": label, "done": p + 1, "total": args.permutations}), flush=True)
        observed = primary["gain_bits_per_noninitial_sign"]
        audit["null_" + label] = {"permutations": len(values), "mobility": mobility, "mean": float(np.mean(values)) if values else None, "95pct_range": [float(x) for x in np.quantile(values, [0.025, 0.975])] if values else None, "p_one_sided": (1 + sum(v >= observed for v in values)) / (1 + len(values)) if values else None, "values": values}
    substitutions, all_candidates = substitution_summary(rows, assignment, args.folds, args.seed, args.substitution_permutations)
    audit["substitutions"] = substitutions
    audit["elapsed_seconds"] = time.monotonic() - start
    (output / "conditional_results.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "substitution_candidates.json").write_text(json.dumps(all_candidates, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "record_scores.jsonl").write_text("\n".join(json.dumps(row) for row in record_scores), encoding="utf-8")
    (output / "fold_assignment.jsonl").write_text("\n".join(json.dumps({"record_id": rows[i].get("record_id"), "artifact": rows[i]["artifact"], "group": g, "fold": assignment[i]}) for g, indices in enumerate(groups) for i in indices), encoding="utf-8")
    compact_transfer = {k: v for k, v in substitutions["transfer_null_position_metadata"].items() if k != "values"}
    print(json.dumps({"stage": "complete", "output": str(output), "seconds": audit["elapsed_seconds"], "primary_gain": primary["gain_bits_per_noninitial_sign"], "transfer": compact_transfer}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-length", type=int, default=3)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--permutations", type=int, default=200)
    parser.add_argument("--substitution-permutations", type=int, default=1000)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--collapse")
    run(parser.parse_args())
