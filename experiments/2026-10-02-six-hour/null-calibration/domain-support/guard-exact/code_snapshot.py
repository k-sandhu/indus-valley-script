"""Exact finite-space calibration of an explicit zero guard and feasibility law."""
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
FOLDER = PARENT / "domain-support"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rows_for(table):
    return [{"record_id": str(index), "seq": tuple(map(str, row)), "artifact": str(index),
             "artifact_aliases": [str(index)], "stratum": ("s", "t")} for index, row in enumerate(table)]


def run():
    output = FOLDER / "guard-exact"
    if output.exists():
        raise FileExistsError("Refusing an existing guard endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    source = PARENT / "main/code_snapshot.py"
    old = load(source, "guard_original_null")
    helper, joint, hashes = old.freeze_sources()
    tables_file = PARENT / "exact/tables_and_sampler_counts.json"
    unique_file = PARENT / "exact/unique_nested_scores.json"
    tables = json.loads(tables_file.read_text())["tables"]
    reused = {record["table_index"]: record for record in json.loads(unique_file.read_text())}
    records = []
    started = time.monotonic()
    for index, table in enumerate(tables):
        rows = rows_for(table)
        components = len(helper.group_records(rows))
        if components < 5:
            record = {"table_index": index, "gain": 0., "components": components, "origin": "declared_guard"}
        elif index in reused:
            record = {"table_index": index, "gain": reused[index]["gain"], "components": components, "origin": "frozen_unique_score", "score": reused[index]}
        else:
            compact, _ = old.fit(rows, joint)
            record = {"table_index": index, "gain": compact["gain"], "components": components, "origin": "new_five_component_fit", "score": compact}
        records.append(record)
        if (index + 1) % 1000 == 0:
            print(json.dumps({"stage": "guard_exact", "tables": index + 1, "total": 8000, "elapsed_seconds": time.monotonic() - started}), flush=True)
    gains = np.array([record["gain"] for record in records])
    feasible = np.array([record["components"] >= 5 for record in records])
    assert feasible.sum() == 5760 and len(reused) == 2880
    full_sorted, feasible_sorted = np.sort(gains), np.sort(gains[feasible])
    full_counts = len(gains) - np.searchsorted(full_sorted, gains, side="left")
    conditional_counts = int(feasible.sum()) - np.searchsorted(feasible_sorted, gains, side="left")
    for index, record in enumerate(records):
        record["full_exceedances"] = int(full_counts[index])
        record["full_tail"] = float(full_counts[index] / 8000)
        record["observed_action"] = "test" if feasible[index] else "abstain"
        record["feasible_exceedances"] = int(conditional_counts[index]) if feasible[index] else None
        record["feasible_tail"] = float(conditional_counts[index] / 5760) if feasible[index] else None
    endpoint = {}
    for alpha in [Fraction(1, 100), Fraction(1, 20), Fraction(1, 10)]:
        full_reject = feasible & (full_counts * alpha.denominator <= 8000 * alpha.numerator)
        conditional_reject = feasible & (conditional_counts * alpha.denominator <= 5760 * alpha.numerator)
        endpoint[str(float(alpha))] = {
            "extended_law_full_population": {"rejections": int(full_reject.sum()), "denominator": 8000, "rate": float(full_reject.mean())},
            "extended_law_given_feasible_observation": {"rejections": int(full_reject.sum()), "denominator": 5760, "rate": float(full_reject.sum() / 5760)},
            "feasibility_conditioned_law": {"rejections": int(conditional_reject.sum()), "denominator": 5760, "rate": float(conditional_reject.sum() / 5760)},
            "conditioned_law_full_population_with_abstention": {"rejections": int(conditional_reject.sum()), "denominator": 8000, "rate": float(conditional_reject.mean())}}
    (output / "scores_and_tails.json").write_text(json.dumps(records, separators=(",", ":")) + "\n", encoding="utf-8")
    result = {"status": "complete", "simulation": True, "tables": 8000, "feasible_tables": 5760, "abstentions": 2240,
              "feasible_probability_exact": "18/25", "new_fits": 2880, "reused_fits": 2880,
              "guard_score": 0., "component_counts": dict(Counter(record["components"] for record in records)),
              "endpoints": endpoint, "source_sha256": digest(__file__), "protocol_sha256": digest(FOLDER / "GUARD_PROTOCOL.md"),
              "input_hashes": {str(tables_file.relative_to(PARENT)): digest(tables_file), str(unique_file.relative_to(PARENT)): digest(unique_file)},
              "preserved_source_sha256": digest(source), "preserved_method_hashes": hashes,
              "scores_sha256": digest(output / "scores_and_tails.json"), "elapsed_seconds": time.monotonic() - started}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    run()
