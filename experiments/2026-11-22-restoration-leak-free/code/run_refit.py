"""Run the leak-free restoration refit across Splits 1, 2, and 3 for all 6 models.

Writes per-query predictions and fold registers to local storage under
data/raw/2026-11-22-restoration-leak-free/ (D: junction) and writes tracked
aggregates only to experiments/2026-11-22-restoration-leak-free/results-v1/summary.json.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parent.parent
RAW = ROOT / "data/raw/2026-11-22-restoration-leak-free"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/six_hour"))

from methods.conditional_structure import UNKNOWN
import markov_baseline as m1_module
import splits as sp_mod
import models as mdl

BOOTSTRAP_REPEATS = 10000
BOOTSTRAP_SEED = 20261122
MODEL_ORDER = ["PM", "M1", "M2", "MKN", "MKN-GF", "MKN-GF-SB"]
SPLIT_ORDER = ["split1_baseline", "split2_alias_clean", "split3_near_variant_clean"]


def score_predictions(rows: list[dict], probs: np.ndarray, signs: list[str], fold: int, comp_lookup: dict[str, int]) -> list[dict]:
    index = {s: i for i, s in enumerate(signs)}
    unk = index[UNKNOWN]
    out = []
    j = 0
    for r in rows:
        seq = r["seq"]
        length = len(seq)
        rid = r["record_id"]
        art = r["artifact"]
        grp = comp_lookup[rid]
        for slot, actual in enumerate(seq):
            p = probs[j]
            if not (np.all(np.isfinite(p)) and abs(float(p.sum()) - 1.0) < 1e-6):
                raise ValueError(f"Invalid probability vector for {rid} slot {slot}: sum={p.sum()}")
            rank = np.argsort(-p, kind="stable")
            top10_codes = [signs[t] for t in rank[:10]]
            actual_idx = index.get(actual, unk)
            out.append({
                "record_id": rid,
                "artifact": art,
                "slot": slot,
                "length": length,
                "actual": actual,
                "position": "initial" if slot == 0 else "final" if slot + 1 == length else "internal",
                "fold": fold,
                "group": grp,
                "known_in_training": actual in index,
                "top1": top10_codes[0] == actual,
                "top5": actual in top10_codes[:5],
                "top10": actual in top10_codes[:10],
                "model_top_mass": float(p[rank[0]]),
                "top_is_unknown": top10_codes[0] == UNKNOWN,
                "bucket_loss_bits": -math.log2(max(float(p[actual_idx]), 1e-300)),
                "suggestions": [{"code": signs[t], "model_mass": float(p[t])} for t in rank[:10]],
            })
            j += 1
    assert j == len(probs)
    return out


def paired_component_bootstrap(
    scores_a: list[dict],
    scores_b: list[dict],
    cluster_of_record: dict[str, int],
    repeats: int = BOOTSTRAP_REPEATS,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Compute B minus A paired differences and 95% cluster-bootstrap CIs."""
    metrics = ["top1", "top5", "top10", "bucket_loss_bits"]
    sums = defaultdict(lambda: np.zeros((len(metrics), 2), dtype=np.float64))
    for a, b in zip(scores_a, scores_b):
        if (a["record_id"], a["slot"], a["actual"]) != (b["record_id"], b["slot"], b["actual"]):
            raise ValueError("Misaligned query pair in bootstrap")
        cid = cluster_of_record[a["record_id"]]
        for m_idx, m in enumerate(metrics):
            delta = float(b[m]) - float(a[m])
            sums[cid][m_idx, 0] += delta
            sums[cid][m_idx, 1] += 1.0
    arr = np.asarray([sums[cid] for cid in sorted(sums)], dtype=np.float64)
    n_clusters = len(arr)
    point = arr.sum(axis=0)
    rng = np.random.default_rng(seed)
    draws = []
    batch = 250
    for offset in range(0, repeats, batch):
        cur = min(batch, repeats - offset)
        ix = rng.integers(0, n_clusters, size=(cur, n_clusters))
        totals = arr[ix].sum(axis=1)
        draws.append(totals[:, :, 0] / totals[:, :, 1])
    samples = np.concatenate(draws, axis=0)
    result = {
        "clusters": n_clusters,
        "bootstrap_repeats": repeats,
        "seed": seed,
        "metrics": {},
    }
    for m_idx, m in enumerate(metrics):
        diff = float(point[m_idx, 0] / point[m_idx, 1])
        ci = [float(x) for x in np.quantile(samples[:, m_idx], [0.025, 0.975])]
        result["metrics"][m] = {"difference": diff, "ci_95": ci}
    return result


def run_split(rows: list[dict], base_map: dict[str, str], split: dict, canonical_order: list[tuple[str, int]], started: float) -> tuple[dict, dict[str, list[dict]]]:
    sname = split["name"]
    assign = split["assignment"]
    comp_lookup = {rows[i]["record_id"]: split["comp_of"][i] for i in range(len(rows))}
    all_scores: dict[str, list[dict]] = {m: [] for m in MODEL_ORDER}
    fold_records: dict[str, list[dict]] = {m: [] for m in MODEL_ORDER}

    for fold in range(5):
        train = [rows[i] for i in range(len(rows)) if assign[i] != fold]
        test = [rows[i] for i in range(len(rows)) if assign[i] == fold]
        inner_splits = list(sp_mod.iter_inner_folds(rows, split, fold))
        total_inner_slots = sum(len(r["seq"]) for _, _, val in inner_splits for r in val)

        # --- 1. PM (inner top-1, ties favor larger alpha) ---
        pm_hits = Counter()
        for _, fit, val in inner_splits:
            for alpha in mdl.PM_GRID:
                m = mdl.PMRestorer(fit, alpha)
                probs = m.predict(val)
                st = mdl.probability_metrics(val, probs, m.signs)
                pm_hits[alpha] += round(st["top1"] * st["slots"])
        pm_alpha = max(mdl.PM_GRID, key=lambda a: (pm_hits[a], a))
        pm_model = mdl.PMRestorer(train, pm_alpha)
        all_scores["PM"].extend(score_predictions(test, pm_model.predict(test), pm_model.signs, fold, comp_lookup))
        fold_records["PM"].append({
            "fold": fold, "train_texts": len(train), "test_texts": len(test),
            "vocab_size": len(pm_model.signs), "selected": {"alpha": pm_alpha},
            "inner_top1": {str(a): pm_hits[a] / total_inner_slots for a in mdl.PM_GRID},
        })

        # --- 2. M1 (inner top-1, ties favor larger alpha) ---
        m1_hits = Counter()
        for _, fit, val in inner_splits:
            for alpha in mdl.M1_GRID:
                m = mdl.M1Restorer(fit, alpha)
                probs = m.predict(val)
                st = mdl.probability_metrics(val, probs, m.signs)
                m1_hits[alpha] += round(st["top1"] * st["slots"])
        m1_alpha = max(mdl.M1_GRID, key=lambda a: (m1_hits[a], a))
        m1_model = mdl.M1Restorer(train, m1_alpha)
        all_scores["M1"].extend(score_predictions(test, m1_model.predict(test), m1_model.signs, fold, comp_lookup))
        fold_records["M1"].append({
            "fold": fold, "train_texts": len(train), "test_texts": len(test),
            "vocab_size": len(m1_model.signs), "selected": {"alpha": m1_alpha},
            "inner_top1": {str(a): m1_hits[a] / total_inner_slots for a in mdl.M1_GRID},
        })

        # --- 3. M2 (inner top-1, ties favor later grid index matching MARKOV-03) ---
        m2_hits = Counter()
        for _, fit, val in inner_splits:
            for alpha in mdl.M2_GRID:
                m = mdl.M2Restorer(fit, alpha)
                probs = m.predict(val)
                st = mdl.probability_metrics(val, probs, m.signs)
                m2_hits[alpha] += round(st["top1"] * st["slots"])
        m2_alpha = max(mdl.M2_GRID, key=lambda a: (m2_hits[a], mdl.M2_GRID.index(a)))
        m2_model = mdl.M2Restorer(train, m2_alpha)
        all_scores["M2"].extend(score_predictions(test, m2_model.predict(test), m2_model.signs, fold, comp_lookup))
        fold_records["M2"].append({
            "fold": fold, "train_texts": len(train), "test_texts": len(test),
            "vocab_size": len(m2_model.signs), "selected": {"alpha": m2_alpha},
            "inner_top1": {("backoff_only" if a is None else str(a)): m2_hits[a] / total_inner_slots for a in mdl.M2_GRID},
        })

        # --- 4. MKN (inner bucket log loss) ---
        mkn_loss = Counter()
        mkn_inner_cache: dict[tuple[int, int, float], tuple[np.ndarray, list[str]]] = {}
        for k, fit, val in inner_splits:
            for cfg in mdl.MKN_GRID:
                m = mdl.MKNRestorer(fit, **cfg)
                probs = m.predict(val)
                st = mdl.probability_metrics(val, probs, m.signs)
                key = (cfg["order"], cfg["discount_scale"])
                mkn_loss[key] += st["bucket_loss_bits"] * st["slots"]
                mkn_inner_cache[(k, cfg["order"], cfg["discount_scale"])] = (probs, m.signs)
        mkn_best_key = min(
            [(c["order"], c["discount_scale"]) for c in mdl.MKN_GRID],
            key=lambda key: (mkn_loss[key], key[0], key[1]),
        )
        mkn_model = mdl.MKNRestorer(train, order=mkn_best_key[0], discount_scale=mkn_best_key[1])
        mkn_test_probs = mkn_model.predict(test)
        all_scores["MKN"].extend(score_predictions(test, mkn_test_probs, mkn_model.signs, fold, comp_lookup))
        fold_records["MKN"].append({
            "fold": fold, "train_texts": len(train), "test_texts": len(test),
            "vocab_size": len(mkn_model.signs),
            "selected": {"order": mkn_best_key[0], "discount_scale": mkn_best_key[1]},
            "inner_loss_bits": {f"k{k}_d{d}": mkn_loss[(k, d)] / total_inner_slots for k, d in sorted(mkn_loss)},
        })

        # --- 5. MKN-GF (inner bucket log loss over alpha_g and w_gf) ---
        gf_inner_cache: dict[tuple[int, float], np.ndarray] = {}
        sb_inner_cache: dict[int, np.ndarray] = {}
        inner_targets: dict[int, np.ndarray] = {}
        for k, fit, val in inner_splits:
            mkn_p, signs = mkn_inner_cache[(k, mkn_best_key[0], mkn_best_key[1])]
            idx_map = {s: i for i, s in enumerate(signs)}
            unk = idx_map[UNKNOWN]
            inner_targets[k] = np.array([idx_map.get(s, unk) for r in val for s in r["seq"]], dtype=np.int64)
            for ag in mdl.GF_ALPHA_GRID:
                gf_m = mdl.GraphicFamilyMarkov(fit, base_map, alpha=ag)
                assert gf_m.signs == signs
                gf_inner_cache[(k, ag)] = gf_m.predict(val)
            sb_m = mdl.SkipBigramPosModel(fit, alpha_pos=20.0, alpha_skip=20.0)
            assert sb_m.signs == signs
            sb_inner_cache[k] = sb_m.predict(val)

        gf_grid_loss = {}
        for ag in mdl.GF_ALPHA_GRID:
            for w_gf in mdl.GF_WEIGHT_GRID:
                tot = 0.0
                for k, _, _ in inner_splits:
                    mkn_p, _ = mkn_inner_cache[(k, mkn_best_key[0], mkn_best_key[1])]
                    pooled = mdl.log_linear_pool([mkn_p, gf_inner_cache[(k, ag)]], [1.0 - w_gf, w_gf])
                    t = inner_targets[k]
                    tot += float(-np.log2(np.clip(pooled[np.arange(len(t)), t], 1e-300, 1.0)).sum())
                gf_grid_loss[(ag, w_gf)] = tot / total_inner_slots
        best_ag, best_w_gf = min(gf_grid_loss, key=lambda key: (gf_grid_loss[key], key[1], key[0]))
        gf_outer_model = mdl.GraphicFamilyMarkov(train, base_map, alpha=best_ag)
        assert gf_outer_model.signs == mkn_model.signs
        gf_test_probs = gf_outer_model.predict(test)
        mkn_gf_test_probs = mdl.log_linear_pool([mkn_test_probs, gf_test_probs], [1.0 - best_w_gf, best_w_gf])
        all_scores["MKN-GF"].extend(score_predictions(test, mkn_gf_test_probs, mkn_model.signs, fold, comp_lookup))
        fold_records["MKN-GF"].append({
            "fold": fold, "train_texts": len(train), "test_texts": len(test),
            "vocab_size": len(mkn_model.signs),
            "selected": {"mkn_order": mkn_best_key[0], "mkn_discount_scale": mkn_best_key[1], "gf_alpha": best_ag, "w_gf": best_w_gf},
            "best_inner_loss_bits": gf_grid_loss[(best_ag, best_w_gf)],
            "zero_weight_inner_loss_bits": gf_grid_loss[(best_ag, 0.0)],
        })

        # --- 6. MKN-GF-SB (inner bucket log loss over w_gf and w_sb using selected best_ag) ---
        ens_grid_loss = {}
        for w_gf in mdl.ENS_GF_WEIGHT_GRID:
            for w_sb in mdl.ENS_SB_WEIGHT_GRID:
                w_mkn = 1.0 - w_gf - w_sb
                tot = 0.0
                for k, _, _ in inner_splits:
                    mkn_p, _ = mkn_inner_cache[(k, mkn_best_key[0], mkn_best_key[1])]
                    pooled = mdl.log_linear_pool(
                        [mkn_p, gf_inner_cache[(k, best_ag)], sb_inner_cache[k]],
                        [w_mkn, w_gf, w_sb],
                    )
                    t = inner_targets[k]
                    tot += float(-np.log2(np.clip(pooled[np.arange(len(t)), t], 1e-300, 1.0)).sum())
                ens_grid_loss[(w_gf, w_sb)] = tot / total_inner_slots
        ens_w_gf, ens_w_sb = min(ens_grid_loss, key=lambda key: (ens_grid_loss[key], key[0] + key[1], key[0]))
        sb_outer_model = mdl.SkipBigramPosModel(train, alpha_pos=20.0, alpha_skip=20.0)
        assert sb_outer_model.signs == mkn_model.signs
        sb_test_probs = sb_outer_model.predict(test)
        ens_test_probs = mdl.log_linear_pool(
            [mkn_test_probs, gf_test_probs, sb_test_probs],
            [1.0 - ens_w_gf - ens_w_sb, ens_w_gf, ens_w_sb],
        )
        all_scores["MKN-GF-SB"].extend(score_predictions(test, ens_test_probs, mkn_model.signs, fold, comp_lookup))
        fold_records["MKN-GF-SB"].append({
            "fold": fold, "train_texts": len(train), "test_texts": len(test),
            "vocab_size": len(mkn_model.signs),
            "selected": {
                "mkn_order": mkn_best_key[0], "mkn_discount_scale": mkn_best_key[1],
                "gf_alpha": best_ag, "w_mkn": round(1.0 - ens_w_gf - ens_w_sb, 6),
                "w_gf": ens_w_gf, "w_sb": ens_w_sb,
            },
            "best_inner_loss_bits": ens_grid_loss[(ens_w_gf, ens_w_sb)],
            "zero_weight_inner_loss_bits": ens_grid_loss[(0.0, 0.0)],
        })

        print(json.dumps({
            "stage": "fold_complete", "split": sname, "fold": fold,
            "pm": pm_alpha, "m1": m1_alpha, "m2": m2_alpha, "mkn": list(mkn_best_key),
            "mkn_gf": [best_ag, best_w_gf], "mkn_gf_sb": [ens_w_gf, ens_w_sb],
            "elapsed_s": round(time.perf_counter() - started, 2),
        }), flush=True)

    # Align every model's score list to canonical (record_id, slot) order and save local JSONLs
    pred_dir = RAW / "predictions" / sname
    pred_dir.mkdir(parents=True, exist_ok=True)
    aligned_scores: dict[str, list[dict]] = {}
    model_summaries = {}
    for mname in MODEL_ORDER:
        by_key = {(s["record_id"], s["slot"]): s for s in all_scores[mname]}
        assert len(by_key) == len(canonical_order)
        ordered = [by_key[k] for k in canonical_order]
        aligned_scores[mname] = ordered
        out_path = pred_dir / f"{mname}.jsonl"
        out_path.write_text("\n".join(json.dumps(s) for s in ordered) + "\n", encoding="utf-8")
        model_summaries[mname] = {
            "summary": m1_module.summarize(ordered),
            "folds": fold_records[mname],
            "local_predictions_path": str(out_path.relative_to(ROOT).as_posix()),
            "local_predictions_sha256": sp_mod.sha256_file(out_path),
        }

    # All 15 within-split pairwise model comparisons (B minus A)
    pairwise = {}
    for i in range(len(MODEL_ORDER)):
        for j in range(i + 1, len(MODEL_ORDER)):
            a, b = MODEL_ORDER[i], MODEL_ORDER[j]
            pairwise[f"{b}_minus_{a}"] = paired_component_bootstrap(
                aligned_scores[a], aligned_scores[b], comp_lookup
            )

    split_result = {
        "label": split["label"],
        "diagnostics": split["diagnostics"],
        "models": model_summaries,
        "pairwise_within_split": pairwise,
    }
    if "closure_merges" in split:
        split_result["closure_merges"] = split["closure_merges"]
    return split_result, aligned_scores


def main():
    started = time.perf_counter()
    out_dir = PKG / "results-v1"
    summary_path = out_dir / "summary.json"
    if summary_path.exists():
        raise FileExistsError(f"Frozen output already exists: {summary_path}")

    tests = mdl.self_test()
    print(json.dumps({"stage": "self_test_passed", "models": list(tests["checks"].keys())}), flush=True)

    rows, raw_faces, base_map, splits, meta = sp_mod.build_all_splits()

    # Use Paper 001 exact slot order as canonical alignment order across all splits & models
    pm_ref = sp_mod.read_jsonl(ROOT / "results/restoration/baseline_slot_audit.jsonl")
    canonical_order = [(x["record_id"], x["slot"]) for x in pm_ref]
    assert len(canonical_order) == meta["benchmark_slots"] == 8009

    # Save local fold/component registers
    folds_dir = RAW / "folds"
    folds_dir.mkdir(parents=True, exist_ok=True)
    fold_register_hashes = {}
    for sname in SPLIT_ORDER:
        sp = splits[sname]
        fpath = folds_dir / f"{sname}.jsonl"
        lines = []
        for i, r in enumerate(rows):
            lines.append(json.dumps({
                "record_id": r["record_id"],
                "artifact": r["artifact"],
                "length": len(r["seq"]),
                "component": sp["comp_of"][i],
                "fold": sp["assignment"][i],
            }))
        fpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
        fold_register_hashes[sname] = {
            "path": str(fpath.relative_to(ROOT).as_posix()),
            "sha256": sp_mod.sha256_file(fpath),
        }

    split_results = {}
    all_aligned: dict[str, dict[str, list[dict]]] = {}
    for sname in SPLIT_ORDER:
        res, aligned = run_split(rows, base_map, splits[sname], canonical_order, started)
        split_results[sname] = res
        all_aligned[sname] = aligned

    # Split 1 sensitivity: resample Split 1 model contrasts over Split 2's 1,361 components
    comp2_lookup = {rows[i]["record_id"]: splits["split2_alias_clean"]["comp_of"][i] for i in range(len(rows))}
    comp3_lookup = {rows[i]["record_id"]: splits["split3_near_variant_clean"]["comp_of"][i] for i in range(len(rows))}
    split1_s2_clusters = {}
    for i in range(len(MODEL_ORDER)):
        for j in range(i + 1, len(MODEL_ORDER)):
            a, b = MODEL_ORDER[i], MODEL_ORDER[j]
            split1_s2_clusters[f"{b}_minus_{a}"] = paired_component_bootstrap(
                all_aligned["split1_baseline"][a], all_aligned["split1_baseline"][b], comp2_lookup
            )

    # Cross-split paired comparisons for every model (using coarser component partition)
    cross_split = {
        "split2_minus_split1": {"cluster_basis": "split2_alias_clean (1361 components)", "models": {}},
        "split3_minus_split1": {"cluster_basis": "split3_near_variant_clean (964 components)", "models": {}},
        "split3_minus_split2": {"cluster_basis": "split3_near_variant_clean (964 components)", "models": {}},
    }
    for mname in MODEL_ORDER:
        cross_split["split2_minus_split1"]["models"][mname] = paired_component_bootstrap(
            all_aligned["split1_baseline"][mname], all_aligned["split2_alias_clean"][mname], comp2_lookup
        )
        cross_split["split3_minus_split1"]["models"][mname] = paired_component_bootstrap(
            all_aligned["split1_baseline"][mname], all_aligned["split3_near_variant_clean"][mname], comp3_lookup
        )
        cross_split["split3_minus_split2"]["models"][mname] = paired_component_bootstrap(
            all_aligned["split2_alias_clean"][mname], all_aligned["split3_near_variant_clean"][mname], comp3_lookup
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "experiment": "2026-11-22-restoration-leak-free",
        "issue": "GitHub #19 / Q-0010",
        "status": "Verified refit on pre-registered splits",
        "protocol_sha256": sp_mod.sha256_file(PKG / "PROTOCOL.md"),
        "code_sha256": {
            "splits.py": sp_mod.sha256_file(HERE / "splits.py"),
            "models.py": sp_mod.sha256_file(HERE / "models.py"),
            "run_refit.py": sp_mod.sha256_file(HERE / "run_refit.py"),
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch_installed": False,
        },
        "local_raw_logical": "data/raw/2026-11-22-restoration-leak-free",
        "local_raw_physical": str(RAW.resolve()),
        "fold_registers": fold_register_hashes,
        "corpus_meta": meta,
        "self_tests": tests,
        "model_order": MODEL_ORDER,
        "split_order": SPLIT_ORDER,
        "bootstrap": {"repeats": BOOTSTRAP_REPEATS, "seed": BOOTSTRAP_SEED},
        "splits": split_results,
        "split1_pairwise_under_split2_clusters": split1_s2_clusters,
        "cross_split_paired": cross_split,
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"stage": "complete", "summary_path": str(summary_path), "runtime_seconds": summary["runtime_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
