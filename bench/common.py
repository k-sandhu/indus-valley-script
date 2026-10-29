"""Inputs, finite permutation inference and source-pinned legacy imports."""
from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np

from . import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/2026-10-13-bench"
KEY_SOURCE = "experiments/2026-10-12-published-claim-tests/sanskrit-key"
SHOT_SOURCE = "experiments/2026-10-12-conjecture-shots"
STRUCTURE_SOURCE = "experiments/2026-10-12-structure-first"
RELEASE_SOURCE = "maintenance/2026-10-08-hf-public-release/release"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def read_rows(path):
    path = Path(path)
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    obj = read_json(path)
    rows = obj.get("rows", obj.get("records")) if isinstance(obj, dict) else obj
    if not isinstance(rows, list):
        raise ValueError("Expected a JSON list, {rows: [...]}, {records: [...]}, or JSONL")
    return rows


def strict_json(value):
    if isinstance(value, dict):
        return {str(k): strict_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [strict_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return strict_json(value.tolist())
    if isinstance(value, np.generic):
        return strict_json(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(strict_json(value), f, indent=2, allow_nan=False)
        f.write("\n")


def provenance(paths):
    out = []
    for p in paths:
        p = Path(p)
        p = p if p.is_absolute() else ROOT / p
        try:
            label = p.relative_to(ROOT).as_posix()
        except ValueError:
            label = str(p)
        out.append({"path": label, "sha256": sha256(p)})
    return out


def envelope(task, result, synthetic=False, paths=()):
    own = [ROOT / "bench/common.py", ROOT / "bench/__main__.py"]
    module_path = ROOT / "bench" / (task.replace("-", "_") + ".py")
    if module_path.exists():
        own.append(module_path)
    if task == "selftest":
        own.extend(ROOT / "bench" / (name + ".py") for name in ("key_calibration", "meaning_map", "shots", "restoration", "segmentation"))
    return strict_json({"schema_version": SCHEMA_VERSION, "task": task,
                        "synthetic": synthetic, "provenance": provenance([*own, *paths]), **result})


@contextmanager
def aliases(modules):
    saved = {k: sys.modules.get(k) for k in modules}
    sys.modules.update(modules)
    try:
        yield
    finally:
        for k, old in saved.items():
            if old is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = old


def legacy(relative, dependencies=None):
    path = ROOT / relative
    name = "bench._legacy_" + hashlib.sha256(relative.encode()).hexdigest()[:16]
    if name in sys.modules:
        if sys.modules[name].__bench_source_sha256__ != sha256(path):
            raise ValueError("Imported source changed during this process: " + relative)
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    module.__bench_source_sha256__ = sha256(path)
    old_path = sys.path[:]
    try:
        with aliases(dependencies or {}):
            spec.loader.exec_module(module)
    finally:
        sys.path[:] = old_path
    sys.modules[name] = module
    return module


def key_common():
    return legacy(KEY_SOURCE + "/common.py")


def permutation_indices(bands, draws, seed):
    groups = defaultdict(list)
    for i, b in enumerate(bands):
        groups[json.dumps(b, sort_keys=True)].append(i)
    rng = np.random.default_rng(seed)
    for _ in range(draws):
        perm = np.arange(len(bands))
        for members in groups.values():
            perm[members] = rng.permutation(members)
        yield perm


def null_summary(actual, draws, alpha=0.05):
    a = np.asarray(draws, dtype=float)
    finite = np.isfinite(a)
    # An undefined rearrangement cannot be discarded to improve significance.
    if not np.isfinite(actual) or not len(a) or not finite.all() or np.std(a) == 0:
        return {"computable": False, "score": actual, "draws": len(a),
                "undefined_draws": int((~finite).sum()), "pass": False}
    mean, sd = float(a.mean()), float(a.std())
    p = float((1 + np.sum(a >= actual)) / (len(a) + 1))
    return {"computable": True, "score": float(actual), "null_mean": mean,
            "null_sd": sd, "distance_sd": (actual - mean) / sd,
            "p_one_sided": p, "draws": len(a), "alpha": alpha,
            "null_quantiles": dict(zip(("q025", "q50", "q95", "q975"),
                                        map(float, np.quantile(a, [.025, .5, .95, .975])))),
            "null_min": float(a.min()), "null_max": float(a.max()), "pass": p <= alpha}


def positive_int(value):
    n = int(value)
    if n < 1:
        raise ValueError("Expected a positive integer")
    return n
