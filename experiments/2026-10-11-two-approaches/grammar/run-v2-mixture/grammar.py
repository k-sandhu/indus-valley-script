"""Finite-state sign-class grammar and matched fixed-length comparators.

Source-derived rows, predictions and fitted dictionaries are local-only.
Numeric codes identify transcribed graphics; states have no assigned meanings.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[_name] = "1"

from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

import numpy as np

UNKNOWN = "__UNKNOWN__"
POSITION_GRID = (5, 20, 100, 500, 2000)
MARKOV_GRID = tuple((order, alpha, weight) for order in (1, 2)
                    for alpha in (20, 100, 500) for weight in (0.0, 0.5, 1.0))
GRAMMAR_GRID = tuple((states, emission, contextual) for states in (4, 8, 12)
                     for emission in (5, 20) for contextual in (False, True))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def closure(raw, placeholder_edges=True):
    parent = list(range(len(raw)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[max(a, b)] = min(a, b)
    seen_artifact, seen_string = {}, {}
    for i, row in enumerate(raw):
        artifact = str(row.get("object_family_id", row.get("artifact_id", row["record_id"])))
        aliases = set(map(str, row.get("artifact_aliases", [artifact]))) | {artifact}
        for value in aliases:
            if value in seen_artifact:
                union(i, seen_artifact[value])
            else:
                seen_artifact[value] = i
        seq = tuple(map(str, row.get("signs_reading_rtl", row.get("seq", row.get("sequence", [])))))
        placeholder = row.get("has_unknown_sign", False) or row.get("has_blank_space", False) or any(x in {"000", "999", "?", UNKNOWN} for x in seq)
        if seq and (placeholder_edges or not placeholder):
            if seq in seen_string:
                union(i, seen_string[seq])
            else:
                seen_string[seq] = i
    components = defaultdict(list)
    for i in range(len(raw)):
        components[find(i)].append(i)
    components = [v for _, v in sorted(components.items())]
    return {i: g for g, members in enumerate(components) for i in members}, components


def load_corpus(path):
    raw = read_jsonl(path)
    full_groups, components = closure(raw)
    diagnostic_groups, diagnostic_components = closure(raw, placeholder_edges=False)
    ordered = sorted(range(len(raw)), key=lambda i: str(raw[i]["record_id"]))
    rows, seen, excluded = [], {}, Counter()
    eligible_count = 0
    for i in ordered:
        row = raw[i]
        seq = tuple(map(str, row["signs_reading_rtl"]))
        if not row.get("clean_rtl_singleline", False):
            excluded["not_clean_rtl_singleline"] += 1
            continue
        if (not row.get("complete_observed", False) or not row.get("single_line", False)
                or row.get("has_unknown_sign", False) or row.get("has_blank_space", False)
                or row.get("max_damage", 0) or row.get("max_uncertainty", 0)
                or any(x in {"000", "999", "?", UNKNOWN} for x in seq)):
            excluded["incomplete_unknown_or_uncertain"] += 1
            continue
        if len(seq) < 3:
            excluded["too_short"] += 1
            continue
        eligible_count += 1
        artifact = str(row["object_family_id"])
        if seq in seen:
            representative = rows[seen[seq]]
            assert representative["group"] == full_groups[i]
            representative["artifact_aliases"] = sorted(set(representative["artifact_aliases"]) | {artifact})
            excluded["duplicate_eligible_sequence"] += 1
        else:
            seen[seq] = len(rows)
            rows.append({"record_id": str(row["record_id"]), "seq": seq, "artifact_aliases": [artifact],
                         "group": full_groups[i], "site": row.get("site"),
                         "object_type": row.get("object_type"), "placeholder_edge_diagnostic_group": diagnostic_groups[i]})
    sizes = Counter(r["group"] for r in rows)
    return rows, {"raw_faces": len(raw), "raw_components": len(components),
                  "largest_raw_component_faces": max(map(len, components)),
                  "eligible_faces_before_uniqueness": eligible_count, "unique_texts": len(rows),
                  "analysis_components": len(sizes), "largest_analysis_component_texts": max(sizes.values()),
                  "raw_input_sha256": digest(path), "exclusions": dict(excluded),
                  "tokens": sum(len(r["seq"]) for r in rows),
                  "top_analysis_component_sizes": sorted(sizes.values(), reverse=True)[:10],
                  "placeholder_edge_graph_diagnostic": {
                      "raw_components_without_placeholder_string_edges": len(diagnostic_components),
                      "largest_raw_component_without_placeholder_string_edges": max(map(len, diagnostic_components)),
                      "analysis_components_without_placeholder_string_edges": len({r["placeholder_edge_diagnostic_group"] for r in rows}),
                      "largest_analysis_component_without_placeholder_string_edges": max(Counter(r["placeholder_edge_diagnostic_group"] for r in rows).values()),
                      "scope": "Graph census only. Primary folds and likelihoods retain all declared exact-string edges."},
                  "length_counts": dict(sorted(Counter(len(r["seq"]) for r in rows).items())),
                  "types": len({s for r in rows for s in r["seq"]})}


def folds(rows, nfold, seed):
    grouped = defaultdict(list)
    for i, row in enumerate(rows):
        grouped[row["group"]].append(i)
    ordered = list(grouped)
    rng = random.Random(seed)
    rng.shuffle(ordered)
    ordered.sort(key=lambda g: sum(len(rows[i]["seq"]) for i in grouped[g]), reverse=True)
    loads, assigned = [0] * nfold, {}
    for group in ordered:
        fold = min(range(nfold), key=lambda j: (loads[j], j))
        for i in grouped[group]:
            assigned[i] = fold
            loads[fold] += len(rows[i]["seq"])
    assert len(assigned) == len(rows)
    for members in grouped.values():
        assert len({assigned[i] for i in members}) == 1
    return assigned, loads


def audit_split(train, test):
    assert not ({r["group"] for r in train} & {r["group"] for r in test})
    assert not ({r["seq"] for r in train} & {r["seq"] for r in test})
    assert not ({a for r in train for a in r["artifact_aliases"]} &
                {a for r in test for a in r["artifact_aliases"]})
    return True


class Alphabet:
    def __init__(self, rows):
        self.signs = sorted({s for r in rows for s in r["seq"]}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        counts = np.full(len(self.signs), 0.5)
        for row in rows:
            for sign in row["seq"]:
                counts[self.index[sign]] += 1
        self.unigram = counts / counts.sum()

    def encode(self, seq):
        return np.array([self.index.get(s, len(self.signs) - 1) for s in seq], dtype=int)


class SignCounts:
    def __init__(self, rows):
        self.alphabet = Alphabet(rows)
        self.position, self.triples = defaultdict(Counter), defaultdict(Counter)
        v = len(self.alphabet.signs)
        self.bigram = np.zeros((v, v))
        self.bigram_seen = set()
        for row in rows:
            seq = self.alphabet.encode(row["seq"])
            for j, target in enumerate(seq):
                self.position[(len(seq), j)][int(target)] += 1
                if j:
                    self.bigram[seq[j - 1], target] += 1
                    self.bigram_seen.add((row["seq"][j - 1], row["seq"][j]))
                if j > 1:
                    self.triples[(int(seq[j - 2]), int(seq[j - 1]))][int(target)] += 1
        self.position_cache = {}

    def positional(self, length, slot, alpha):
        key = (length, slot, alpha)
        if key not in self.position_cache:
            counts = self.position.get((length, slot), {})
            prob = alpha * self.alphabet.unigram.copy()
            for target, count in counts.items():
                prob[target] += count
            self.position_cache[key] = prob / (sum(counts.values()) + alpha)
        return self.position_cache[key]


class Position:
    def __init__(self, counts, alpha):
        self.counts, self.alpha, self.alphabet = counts, alpha, counts.alphabet

    def distribution(self, prefix, length):
        return self.counts.positional(length, len(prefix), self.alpha)

    def score(self, row):
        seq = self.alphabet.encode(row["seq"])
        return np.array([math.log2(self.distribution(row["seq"][:j], len(seq))[c]) for j, c in enumerate(seq)])


class Markov:
    def __init__(self, counts, order, alpha, weight):
        self.counts, self.order, self.alpha, self.weight = counts, order, alpha, weight
        self.alphabet = counts.alphabet
        self.bg = (counts.bigram + alpha * self.alphabet.unigram[None, :]) / (counts.bigram.sum(axis=1)[:, None] + alpha)
        self.cache = {}

    def distribution(self, prefix, length):
        slot = len(prefix)
        if not slot:
            return self.counts.positional(length, slot, 100)
        last = int(self.alphabet.index.get(prefix[-1], len(self.alphabet.signs) - 1))
        second = int(self.alphabet.index.get(prefix[-2], len(self.alphabet.signs) - 1)) if slot > 1 and self.order == 2 else None
        key = (length, slot, second, last)
        if key not in self.cache:
            prob = self.bg[last].copy()
            if second is not None:
                counts = self.counts.triples.get((second, last), {})
                prob *= self.alpha
                for target, count in counts.items():
                    prob[target] += count
                prob /= self.alpha + sum(counts.values())
            if self.weight:
                prob *= (self.counts.positional(length, slot, 100) / self.alphabet.unigram) ** self.weight
            self.cache[key] = prob / prob.sum()
        return self.cache[key]

    def score(self, row):
        seq = self.alphabet.encode(row["seq"])
        return np.array([math.log2(self.distribution(row["seq"][:j], len(seq))[c]) for j, c in enumerate(seq)])


class Grammar:
    def __init__(self, rows, states, emission_strength, contextual, seed=20261011,
                 starts=2, iterations=60, context_strength=50, tolerance=1e-6):
        self.alphabet = Alphabet(rows)
        self.states, self.contextual = states, contextual
        self.emission_strength, self.context_strength = emission_strength, context_strength
        by_length = defaultdict(list)
        for row in rows:
            by_length[len(row["seq"])].append(self.alphabet.encode(row["seq"]))
        batches = {length: np.stack(items) for length, items in sorted(by_length.items())}
        best = None
        self.restart_summaries = []
        for restart in range(starts):
            rng = np.random.default_rng(seed + restart * 104729)
            counts = np.zeros((states, len(self.alphabet.signs)))
            if restart == 0:
                centers = (np.arange(states) + 0.5) / states
                for length, matrix in batches.items():
                    for j in range(length):
                        weights = np.exp(-((centers - (j + 0.5) / length) / 0.22) ** 2)
                        weights = 0.9 * weights / weights.sum() + 0.1 / states
                        for k in range(states):
                            counts[k] += weights[k] * np.bincount(matrix[:, j], minlength=counts.shape[1])
            else:
                all_tokens = np.concatenate([m.ravel() for m in batches.values()])
                membership = rng.dirichlet(np.ones(states) * 0.25, size=counts.shape[1]).T
                counts = membership * np.bincount(all_tokens, minlength=counts.shape[1])[None, :]
            counts *= rng.lognormal(0, 0.25, size=counts.shape)
            self.emission = (counts + emission_strength * self.alphabet.unigram) / (counts.sum(axis=1)[:, None] + emission_strength)
            self.initial = np.full(states, 1 / states)
            self.transition = rng.dirichlet(np.ones(states) * 5, size=states)
            self.context_initial = {length: self.initial.copy() for length in batches}
            self.context_transition = {(length, j): self.transition.copy() for length in batches for j in range(1, length)}
            trajectory = []
            for iteration in range(iterations):
                ec = np.zeros_like(self.emission)
                starts_count, transition_count = np.zeros(states), np.zeros((states, states))
                local_starts, local_transition = {}, {}
                ll = 0.0
                for length, matrix in batches.items():
                    forward, backward, scales, emissions = self._forward_backward(matrix)
                    gamma = forward * backward
                    gamma /= gamma.sum(axis=2, keepdims=True)
                    ll += float(np.log(scales).sum())
                    for k in range(states):
                        ec[k] += np.bincount(matrix.ravel(), weights=gamma[:, :, k].ravel(), minlength=ec.shape[1])
                    sc = gamma[:, 0].sum(axis=0)
                    starts_count += sc
                    local_starts[length] = sc
                    for j in range(1, length):
                        transition = self._transition(length, j)
                        xi = np.einsum("ni,ij,nj->ij", forward[:, j - 1], transition,
                                       emissions[:, j] * backward[:, j] / scales[:, j, None], optimize=True)
                        transition_count += xi
                        local_transition[(length, j)] = xi
                trajectory.append(ll)
                self.emission = (ec + emission_strength * self.alphabet.unigram) / (ec.sum(axis=1)[:, None] + emission_strength)
                self.initial = (starts_count + 0.5) / (starts_count.sum() + 0.5 * states)
                self.transition = (transition_count + 0.5) / (transition_count.sum(axis=1)[:, None] + 0.5 * states)
                if contextual:
                    self.context_initial = {length: (sc + context_strength * self.initial) / (sc.sum() + context_strength)
                                            for length, sc in local_starts.items()}
                    self.context_transition = {key: (tc + context_strength * self.transition) / (tc.sum(axis=1)[:, None] + context_strength)
                                               for key, tc in local_transition.items()}
                if iteration >= 14 and abs(trajectory[-1] - trajectory[-2]) < tolerance * (1 + abs(trajectory[-2])):
                    break
            final_ll = sum(float(np.log(self._forward_backward(matrix)[2]).sum()) for matrix in batches.values())
            state = {"emission": self.emission.copy(), "initial": self.initial.copy(), "transition": self.transition.copy(),
                     "context_initial": {key: val.copy() for key, val in self.context_initial.items()},
                     "context_transition": {key: val.copy() for key, val in self.context_transition.items()},
                     "training_ll_nats": final_ll, "iterations": len(trajectory), "restart": restart,
                     "likelihood_trajectory_nats": trajectory,
                     "likelihood_decreases": sum(b < a - 1e-8 for a, b in zip(trajectory[:-1], trajectory[1:]))}
            self.restart_summaries.append({key: state[key] for key in ("training_ll_nats", "iterations", "restart", "likelihood_decreases")})
            if best is None or final_ll > best["training_ll_nats"]:
                best = state
        for name, value in best.items():
            setattr(self, name, value)
        assert np.allclose(self.emission.sum(axis=1), 1)
        assert np.allclose(self.transition.sum(axis=1), 1)
        assert np.isclose(self.initial.sum(), 1)

    def _initial(self, length):
        return self.context_initial.get(length, self.initial) if self.contextual else self.initial

    def _transition(self, length, slot):
        return self.context_transition.get((length, slot), self.transition) if self.contextual else self.transition

    def _forward_backward(self, matrix):
        n, length = matrix.shape
        emissions = self.emission[:, matrix].transpose(1, 2, 0)
        forward = np.empty((n, length, self.states))
        scales = np.empty((n, length))
        forward[:, 0] = emissions[:, 0] * self._initial(length)
        scales[:, 0] = forward[:, 0].sum(axis=1)
        forward[:, 0] /= scales[:, 0, None]
        for j in range(1, length):
            forward[:, j] = (forward[:, j - 1] @ self._transition(length, j)) * emissions[:, j]
            scales[:, j] = forward[:, j].sum(axis=1)
            forward[:, j] /= scales[:, j, None]
        backward = np.ones_like(forward)
        for j in range(length - 2, -1, -1):
            backward[:, j] = (emissions[:, j + 1] * backward[:, j + 1]) @ self._transition(length, j + 1).T
            backward[:, j] /= scales[:, j + 1, None]
        return forward, backward, scales, emissions

    def distribution(self, prefix, length):
        states = self._initial(length).copy()
        for j, sign in enumerate(prefix):
            target = self.alphabet.index.get(sign, len(self.alphabet.signs) - 1)
            states *= self.emission[:, target]
            states /= states.sum()
            states = states @ self._transition(length, j + 1)
        return states @ self.emission

    def score(self, row):
        seq = self.alphabet.encode(row["seq"])
        states = self._initial(len(seq)).copy()
        scores = []
        for j, target in enumerate(seq):
            likelihood = self.emission[:, target]
            prob = float(states @ likelihood)
            scores.append(math.log2(prob))
            states *= likelihood
            states /= prob
            if j + 1 < len(seq):
                states = states @ self._transition(len(seq), j + 1)
        return np.array(scores)

    def posterior(self, row):
        matrix = self.alphabet.encode(row["seq"])[None, :]
        forward, backward, scales, _ = self._forward_backward(matrix)
        gamma = forward[0] * backward[0]
        gamma /= gamma.sum(axis=1, keepdims=True)
        assert np.allclose(gamma.sum(axis=1), 1)
        return gamma, float(np.log2(scales).sum())

    def viterbi(self, row):
        seq = self.alphabet.encode(row["seq"])
        value = np.log(self._initial(len(seq))) + np.log(self.emission[:, seq[0]])
        back = []
        for j, code in enumerate(seq[1:], start=1):
            table = value[:, None] + np.log(self._transition(len(seq), j))
            back.append(table.argmax(axis=0))
            value = table.max(axis=0) + np.log(self.emission[:, code])
        path = [int(value.argmax())]
        for pointers in reversed(back):
            path.append(int(pointers[path[-1]]))
        return tuple(reversed(path))


def self_tests():
    rows = [{"seq": seq} for seq in (("A", "B", "A"), ("B", "A", "B"), ("A", "A", "B"), ("A", "B", "B"))]
    counts = SignCounts(rows)
    models = {"position": Position(counts, 20), "markov1": Markov(counts, 1, 20, 1),
              "markov2": Markov(counts, 2, 20, 0.5),
              "grammar_global": Grammar(rows, 2, 5, False, starts=2, iterations=20),
              "grammar_contextual": Grammar(rows, 2, 5, True, starts=2, iterations=20)}
    sums = {}
    errors = {}
    for name, model in models.items():
        for length in (1, 2, 3, 4):
            total = sum(2 ** float(model.score({"seq": seq}).sum())
                        for seq in itertools.product(model.alphabet.signs, repeat=length))
            assert abs(total - 1) < 1e-10, (name, length, total)
            sums[f"{name}_L{length}"] = total
        first = model.score({"seq": ("A", "B", "A")})
        changed_suffix = model.score({"seq": ("A", "B", "B")})
        assert np.allclose(first[:2], changed_suffix[:2])
        assert np.allclose(model.distribution(("UNSEEN",), 3), model.distribution((UNKNOWN,), 3))
        if isinstance(model, Grammar):
            for seq in itertools.product(model.alphabet.signs, repeat=3):
                exact = 0.0
                for path in itertools.product(range(model.states), repeat=3):
                    prob = model._initial(3)[path[0]] * model.emission[path[0], model.alphabet.index[seq[0]]]
                    for j in range(1, 3):
                        prob *= model._transition(3, j)[path[j - 1], path[j]] * model.emission[path[j], model.alphabet.index[seq[j]]]
                    exact += prob
                forward = 2 ** float(model.score({"seq": seq}).sum())
                assert abs(forward - exact) < 1e-12
                posterior, sequence_score = model.posterior({"seq": seq})
                assert abs(sequence_score - model.score({"seq": seq}).sum()) < 1e-10
            errors[name] = "explicit state paths agree with normalized prefix likelihood"
    raw = [{"record_id": "a", "object_family_id": "one", "seq": ("short",)},
           {"record_id": "b", "object_family_id": "two", "seq": ("short",)},
           {"record_id": "c", "object_family_id": "one", "seq": ("A", "B", "C")},
           {"record_id": "d", "object_family_id": "two", "seq": ("B", "C", "A")}]
    mapping, groups = closure(raw)
    assert len(groups) == 1 and mapping[2] == mapping[3]
    return {"fixed_length_probability_sums": sums, "explicit_grammar_checks": errors,
            "oov_previous_code_matches_unknown": True, "short_excluded_face_retains_physical_bridge": True,
            "prefix_api_has_no_target_argument": True}
