"""Split construction and cross-fold leakage diagnostics for the leak-free refit.

Builds three progressively stricter 5-fold component-held-out partitions of the
Paper 001 restoration population (1,596 unique strings, 8,009 slot queries):
  1. split1_baseline: exact Paper 001 benchmark-only components (1,526 components).
  2. split2_alias_clean: full-corpus transitive closure across all 5,680 observed
     faces (object_family_id, CISI base key, site + normalized excavation-idno,
     and identical nonempty reading-order strings of any length, including 1-2 signs).
  3. split3_near_variant_clean: split2 components further merged across benchmark
     strings within Levenshtein distance 1 or identical under F-0010 base shapes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from methods.conditional_structure import group_records, load_records, make_folds

SEED = 20261006
CLEAN_PATH = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
OBSERVED_PATH = ROOT / "data/normalized/lipi_observed_faces.jsonl"
BASE_FAMILY_PATH = ROOT / "experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def load_base_family_map(path: Path = BASE_FAMILY_PATH) -> dict[str, str]:
    mapping: dict[str, str] = {}
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].strip():
            mapping[parts[0].strip()] = parts[1].strip()
    return mapping


def normalize_cisi_base(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"-", "--", "?", "??"} or "?" in text:
        return None
    match = re.match(r"^([A-Za-z]+-\d+)", text)
    return match.group(1).upper() if match else text.upper()


def normalize_excavation_idno(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"-", "--", "- -", "?", "??", "Unknown"} or "?" in text:
        return None
    norm = re.sub(r"[\s\-_./,]+", "", text).upper()
    if not any(ch.isdigit() for ch in norm):
        return None
    return norm


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, i: int, j: int) -> bool:
        a, b = self.find(i), self.find(j)
        if a == b:
            return False
        self.parent[max(a, b)] = min(a, b)
        return True


def _groups_from_uf(uf: UnionFind, n_bench: int) -> list[list[int]]:
    buckets: dict[int, list[int]] = defaultdict(list)
    for i in range(n_bench):
        buckets[uf.find(i)].append(i)
    return [members for _, members in sorted(buckets.items())]


def make_component_folds(rows: list[dict], comp_ids: list[int], n_folds: int, seed: int) -> tuple[dict[int, int], list[int]]:
    """Assign rows to balanced folds without splitting any precomputed component id."""
    by_comp: dict[int, list[int]] = defaultdict(list)
    for idx, cid in enumerate(comp_ids):
        by_comp[cid].append(idx)
    groups = [by_comp[cid] for cid in sorted(by_comp)]
    return make_folds(rows, groups, n_folds, seed)


def build_split2_uf(rows: list[dict], raw_faces: list[dict]) -> tuple[UnionFind, dict]:
    n_bench = len(rows)
    n_raw = len(raw_faces)
    uf = UnionFind(n_bench + n_raw)
    fam_tbl: dict[str, int] = {}
    cisi_tbl: dict[str, int] = {}
    exc_tbl: dict[tuple[str, str], int] = {}
    seq_tbl: dict[tuple[str, ...], int] = {}
    merges = Counter()

    def attach(idx: int, key, table: dict, label: str):
        if key is None:
            return
        if key in table:
            if uf.union(idx, table[key]):
                merges[label] += 1
        else:
            table[key] = idx

    for i, r in enumerate(rows):
        for alias in r["artifact_aliases"]:
            attach(i, str(alias), fam_tbl, "object_family")
        attach(i, r["seq"], seq_tbl, "sequence")

    for j, r in enumerate(raw_faces):
        idx = n_bench + j
        fam = str(r.get("object_family_id", r.get("artifact_id", r["record_id"])))
        attach(idx, fam, fam_tbl, "object_family")
        attach(idx, normalize_cisi_base(r.get("source_cisi")), cisi_tbl, "cisi_base")
        ne = normalize_excavation_idno((r.get("metadata") or {}).get("excavation-idno"))
        site = str(r.get("site") or "").strip().upper()
        if ne is not None:
            attach(idx, (site, ne), exc_tbl, "site_excavation_idno")
        seq = tuple(map(str, r.get("signs_reading_rtl", [])))
        if seq:
            attach(idx, seq, seq_tbl, "sequence")

    return uf, dict(merges)


def find_near_variant_edges(rows: list[dict], base_map: dict[str, str]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Return exact pairs of benchmark row indices with Levenshtein=1 or F-0010 base-shape match."""
    lev_edges: set[tuple[int, int]] = set()
    base_edges: set[tuple[int, int]] = set()

    # Exact F-0010 base-shape equivalence classes
    by_base: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        bseq = tuple(base_map.get(s, s) for s in r["seq"])
        by_base[bseq].append(i)
    for members in by_base.values():
        if len(members) > 1:
            for a_idx in range(len(members)):
                for b_idx in range(a_idx + 1, len(members)):
                    base_edges.add((members[a_idx], members[b_idx]))

    # Exact Levenshtein = 1 via substitution wildcards and single-sign deletion index
    by_wc: dict[tuple[int, int, tuple[str, ...]], list[int]] = defaultdict(list)
    by_del: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        seq = r["seq"]
        length = len(seq)
        for k in range(length):
            reduced = seq[:k] + seq[k + 1:]
            by_wc[(length, k, reduced)].append(i)
            by_del[reduced].append(i)
    for members in by_wc.values():
        if len(members) > 1:
            for a_idx in range(len(members)):
                for b_idx in range(a_idx + 1, len(members)):
                    lev_edges.add((members[a_idx], members[b_idx]))
    for i, r in enumerate(rows):
        for j in by_del.get(r["seq"], []):
            if i != j:
                lev_edges.add((min(i, j), max(i, j)))

    return sorted(lev_edges), sorted(base_edges)


def build_all_splits():
    rows, exclusions = load_records(CLEAN_PATH, min_length=3, unique=True)
    raw_faces = read_jsonl(OBSERVED_PATH)
    base_map = load_base_family_map(BASE_FAMILY_PATH)
    n_bench = len(rows)

    # Split 1: exact Paper 001 benchmark-only components
    groups1 = group_records(rows)
    assign1, loads1 = make_folds(rows, groups1, 5, SEED)
    comp1_of = {i: g for g, mem in enumerate(groups1) for i in mem}

    # Split 2: full-corpus transitive alias closure
    uf2, merges2 = build_split2_uf(rows, raw_faces)
    groups2 = _groups_from_uf(uf2, n_bench)
    assign2, loads2 = make_folds(rows, groups2, 5, SEED)
    comp2_of = {i: g for g, mem in enumerate(groups2) for i in mem}

    # Split 3: Split 2 + Levenshtein=1 + F-0010 base-shape identity
    lev_edges, base_edges = find_near_variant_edges(rows, base_map)
    uf3 = UnionFind(n_bench)
    for mem in groups2:
        for idx in mem[1:]:
            uf3.union(mem[0], idx)
    merges3 = Counter()
    for a, b in base_edges:
        if uf3.union(a, b):
            merges3["base_family"] += 1
    for a, b in lev_edges:
        if uf3.union(a, b):
            merges3["levenshtein_1"] += 1
    groups3 = _groups_from_uf(uf3, n_bench)
    assign3, loads3 = make_folds(rows, groups3, 5, SEED)
    comp3_of = {i: g for g, mem in enumerate(groups3) for i in mem}

    splits = {
        "split1_baseline": {
            "name": "split1_baseline",
            "label": "Split 1 (Baseline Paper 001)",
            "groups": groups1,
            "comp_of": comp1_of,
            "assignment": assign1,
            "fold_token_loads": loads1,
            "preserve_components_in_inner": False,
        },
        "split2_alias_clean": {
            "name": "split2_alias_clean",
            "label": "Split 2 (Full-corpus alias-clean, Q-0010)",
            "groups": groups2,
            "comp_of": comp2_of,
            "assignment": assign2,
            "fold_token_loads": loads2,
            "preserve_components_in_inner": True,
            "closure_merges": merges2,
        },
        "split3_near_variant_clean": {
            "name": "split3_near_variant_clean",
            "label": "Split 3 (Near-variant-clean sensitivity)",
            "groups": groups3,
            "comp_of": comp3_of,
            "assignment": assign3,
            "fold_token_loads": loads3,
            "preserve_components_in_inner": True,
            "closure_merges": dict(merges3),
        },
    }

    # Precompute leakage adjacency sets for diagnostics on every split
    lev_adj: dict[int, set[int]] = defaultdict(set)
    for a, b in lev_edges:
        lev_adj[a].add(b)
        lev_adj[b].add(a)
    base_adj: dict[int, set[int]] = defaultdict(set)
    for a, b in base_edges:
        base_adj[a].add(b)
        base_adj[b].add(a)

    for sname, sp in splits.items():
        sp["diagnostics"] = compute_split_diagnostics(
            rows, sp, comp1_of, comp2_of, comp3_of, lev_adj, base_adj
        )

    meta = {
        "clean_path": str(CLEAN_PATH.relative_to(ROOT).as_posix()),
        "clean_sha256": sha256_file(CLEAN_PATH),
        "observed_path": str(OBSERVED_PATH.relative_to(ROOT).as_posix()),
        "observed_sha256": sha256_file(OBSERVED_PATH),
        "base_family_path": str(BASE_FAMILY_PATH.relative_to(ROOT).as_posix()),
        "base_family_sha256": sha256_file(BASE_FAMILY_PATH),
        "benchmark_strings": n_bench,
        "benchmark_slots": sum(len(r["seq"]) for r in rows),
        "observed_faces": len(raw_faces),
        "exclusions": exclusions,
        "levenshtein_1_pairs": len(lev_edges),
        "base_family_pairs": len(base_edges),
        "seed": SEED,
    }
    return rows, raw_faces, base_map, splits, meta


def compute_split_diagnostics(
    rows: list[dict],
    split: dict,
    comp1_of: dict[int, int],
    comp2_of: dict[int, int],
    comp3_of: dict[int, int],
    lev_adj: dict[int, set[int]],
    base_adj: dict[int, set[int]],
) -> dict:
    n = len(rows)
    assign = split["assignment"]
    groups = split["groups"]
    total_slots = sum(len(r["seq"]) for r in rows)

    def crossing_by_comp(comp_map: dict[int, int]) -> dict:
        by_c: dict[int, list[int]] = defaultdict(list)
        for i in range(n):
            by_c[comp_map[i]].append(i)
        touched_rows = set()
        cross_components = 0
        per_fold = []
        for f in range(5):
            f_touched = set()
            f_linked_train = set()
            for mem in by_c.values():
                tests = [i for i in mem if assign[i] == f]
                trains = [i for i in mem if assign[i] != f]
                if tests and trains:
                    f_touched.update(tests)
                    f_linked_train.update(trains)
            touched_rows.update(f_touched)
            per_fold.append({
                "fold": f,
                "touched_test_strings": len(f_touched),
                "touched_test_queries": sum(len(rows[i]["seq"]) for i in f_touched),
                "linked_train_strings": len(f_linked_train),
            })
        for mem in by_c.values():
            if len({assign[i] for i in mem}) > 1:
                cross_components += 1
        q_count = sum(len(rows[i]["seq"]) for i in touched_rows)
        return {
            "crossing_components": cross_components,
            "touched_strings": len(touched_rows),
            "touched_queries": q_count,
            "touched_query_share": q_count / total_slots,
            "per_fold": per_fold,
        }

    def crossing_by_adj(adj: dict[int, set[int]]) -> dict:
        touched_rows = set()
        cross_edges = 0
        for i in range(n):
            f = assign[i]
            for j in adj.get(i, ()):
                if assign[j] != f:
                    touched_rows.add(i)
                    if i < j:
                        cross_edges += 1
        q_count = sum(len(rows[i]["seq"]) for i in touched_rows)
        return {
            "crossing_pairs": cross_edges,
            "touched_strings": len(touched_rows),
            "touched_queries": q_count,
            "touched_query_share": q_count / total_slots,
        }

    union_adj: dict[int, set[int]] = defaultdict(set)
    for i in range(n):
        union_adj[i] = lev_adj.get(i, set()) | base_adj.get(i, set())

    sizes_rows = sorted((len(g) for g in groups), reverse=True)
    sizes_slots = sorted((sum(len(rows[i]["seq"]) for i in g) for g in groups), reverse=True)
    return {
        "components": len(groups),
        "largest_component_strings": sizes_rows[0],
        "largest_component_slots": sizes_slots[0],
        "top5_component_strings": sizes_rows[:5],
        "top5_component_slots": sizes_slots[:5],
        "fold_token_loads": split["fold_token_loads"],
        "fold_string_counts": [sum(1 for i in range(n) if assign[i] == f) for f in range(5)],
        "cross_fold_benchmark_alias_leakage": crossing_by_comp(comp1_of),
        "cross_fold_full_corpus_alias_leakage": crossing_by_comp(comp2_of),
        "cross_fold_levenshtein_1_overlap": crossing_by_adj(lev_adj),
        "cross_fold_base_family_overlap": crossing_by_adj(base_adj),
        "cross_fold_direct_near_variant_overlap": crossing_by_adj(union_adj),
        "cross_fold_split3_closure_overlap": crossing_by_comp(comp3_of),
    }


def iter_inner_folds(rows: list[dict], split: dict, outer_fold: int):
    """Yield (inner_fold_id, fit_rows, val_rows) respecting the split's component rule."""
    assign = split["assignment"]
    train_indices = [i for i in range(len(rows)) if assign[i] != outer_fold]
    train_rows = [rows[i] for i in train_indices]
    if split["preserve_components_in_inner"]:
        comp_ids = [split["comp_of"][i] for i in train_indices]
        inner_assign, _ = make_component_folds(train_rows, comp_ids, 3, SEED + outer_fold)
    else:
        inner_groups = group_records(train_rows)
        inner_assign, _ = make_folds(train_rows, inner_groups, 3, SEED + outer_fold)
    for k in range(3):
        fit = [train_rows[idx] for idx in range(len(train_rows)) if inner_assign[idx] != k]
        val = [train_rows[idx] for idx in range(len(train_rows)) if inner_assign[idx] == k]
        yield k, fit, val
