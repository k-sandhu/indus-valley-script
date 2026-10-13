"""Independent closed forms and primitive-event enumeration for the root model."""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
TARGET = PACKAGE / "coordinator/run-v1/retention.json"
STATES = tuple(product((False, True), repeat=2))
CHECKS = []


def check(name, passed, **detail):
    CHECKS.append({"id": name, "pass": bool(passed), **detail})


def independent_marginals(e, r, d, n):
    # Solve p[n+1] = b + lambda*p[n], starting at p[0]=1.
    b = e + (1-e)*r
    lam = (1-r)*(1-2*e)
    pc = F(1) if lam == 1 else b/(1-lam) + (1-b/(1-lam))*lam**n
    ac = (1 + (1-2*d)**n)/2
    return pc, ac


def independent_event_row(previous, e, r, d):
    # Enumerate coins rather than constructing the author's marginal matrix.
    # The repair coin is drawn even if unused; only an incorrect procedure
    # receives repair. Attribution has a separate flip coin and no repair.
    result = {s: F(0) for s in STATES}
    for pflip, repair, aflip in product((False, True), repeat=3):
        weight = (e if pflip else 1-e) * (r if repair else 1-r) * (d if aflip else 1-d)
        proc = previous[0] ^ pflip
        if not proc and repair:
            proc = True
        attr = previous[1] ^ aflip
        result[(proc, attr)] += weight
    return tuple(result[s] for s in STATES)


def enumerate_paths(e, r, d, n, initial=(True, True)):
    law = {s: independent_event_row(s, e, r, d) for s in STATES}
    result = {s: F(0) for s in STATES}
    # All complete hidden-state paths for short n, including zero-weight paths.
    for path in product(STATES, repeat=n):
        prob, previous = F(1), initial
        for state in path:
            prob *= law[previous][STATES.index(state)]
            previous = state
        result[previous] += prob
    return tuple(result[s] for s in STATES)


def main():
    output = HERE / "retention-checks-v1.json"
    if output.exists():
        raise FileExistsError(output)
    saved = json.loads(TARGET.read_text(encoding="utf-8"))
    check("saved-state-order", saved["states_order"] == [list(s) for s in STATES])
    expected_grid = set(product(("1/100", "1/10", "3/10"), ("0", "1/2", "9/10"),
                                ("0", "1/100", "1/10", "3/10"), (0, 1, 5, 20, 100)))
    actual_grid = [(s["parameters"]["error"], s["parameters"]["repair"],
                    s["parameters"]["drift"], s["parameters"]["steps"]) for s in saved["grid"]]
    check("grid-180-unique-predeclared", len(actual_grid) == len(set(actual_grid)) == 180 and set(actual_grid) == expected_grid)
    for i, scenario in enumerate([saved["primary"], saved["unprotected_reference"], *saved["grid"]]):
        params = scenario["parameters"]
        e, r, d = (F(params[k]) for k in ("error", "repair", "drift"))
        n = params["steps"]
        pc, ac = independent_marginals(e, r, d, n)
        expected = {"procedure_correct": pc, "attribution_correct": ac,
                    "both_correct": pc*ac, "procedure_correct_attribution_wrong": pc*(1-ac),
                    "procedure_origin_tv": F(0), "attribution_origin_tv": abs((1-2*d)**n)}
        for endpoint, value in expected.items():
            actual = scenario[endpoint]
            check(f"scenario-{i}-{endpoint}-exact", F(actual["rational"]) == value)
            check(f"scenario-{i}-{endpoint}-float", actual["decimal"] == float(value))
        expected_states = [(pc if p else 1-pc) * (ac if a else 1-ac) for p, a in STATES]
        actual_states = [F(s["probability"]["rational"]) for s in scenario["states"]]
        check(f"scenario-{i}-state-joint-law", actual_states == expected_states)
        check(f"scenario-{i}-probability-normalization", sum(actual_states) == 1 and all(0 <= x <= 1 for x in actual_states))
    # The author's callable matrix is the comparison target. Expected entries
    # come entirely from the primitive-event enumeration above.
    path = PACKAGE / "coordinator/retention_model.py"
    spec = importlib.util.spec_from_file_location("reviewed_retention", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for i, (e, r, d) in enumerate(product((F(0), F(1, 10), F(1)), repeat=3)):
        matrix = mod.transition(e, r, d)
        for j, state in enumerate(STATES):
            check(f"event-matrix-{i}-{j}", matrix[j] == independent_event_row(state, e, r, d))
        for n in (0, 1, 2, 3):
            check(f"path-enumeration-{i}-{n}", mod.evolve(e, r, d, n) == enumerate_paths(e, r, d, n))
            pc, ac = independent_marginals(e, r, d, n)
            expected = tuple((pc if p else 1-pc)*(ac if a else 1-ac) for p, a in STATES)
            check(f"closed-form-boundary-{i}-{n}", expected == enumerate_paths(e, r, d, n))
    check("source-code-hash", saved["source_code_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest())
    protocol = PACKAGE / "coordinator/MODEL-PROTOCOL.md"
    check("protocol-hash", saved["protocol_sha256"] == hashlib.sha256(protocol.read_bytes()).hexdigest())
    result = {"target": TARGET.relative_to(PACKAGE).as_posix(),
              "target_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
              "method": "closed-form affine recurrence, independent eight-coin-event row enumeration, and complete four-state paths through n=3",
              "scope": "arithmetic correctness under the declared synthetic law; no historical parameter calibration",
              "passed": sum(c["pass"] for c in CHECKS), "failed": sum(not c["pass"] for c in CHECKS),
              "checks": CHECKS}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("passed", "failed", "method")}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
