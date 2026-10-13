"""Exact synthetic retention scenarios; no parameters are historical estimates."""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATES = tuple(product((False, True), repeat=2))

def next_correct(previous: bool, error: F, repair: F) -> F:
    """Flip, then repair an incorrect value. Repair has an external procedure check."""
    uncorrected = 1 - error if previous else error
    return uncorrected + (1 - uncorrected) * repair

def transition(error: F, repair: F, drift: F) -> tuple[tuple[F, ...], ...]:
    if any(x < 0 or x > 1 for x in (error, repair, drift)):
        raise ValueError("Probabilities must lie in [0,1].")
    rows = []
    for p, a in STATES:
        pc, ac = next_correct(p, error, repair), next_correct(a, drift, F(0))
        row = tuple((pc if np else 1 - pc) * (ac if na else 1 - ac)
                    for np, na in STATES)
        assert sum(row) == 1
        rows.append(row)
    return tuple(rows)

def evolve(error: F, repair: F, drift: F, steps: int,
           initial_attribution_correct: bool = True) -> tuple[F, ...]:
    if steps < 0:
        raise ValueError("Transmission steps must be nonnegative.")
    law = transition(error, repair, drift)
    prob = tuple(F(int(s == (True, initial_attribution_correct))) for s in STATES)
    for _ in range(steps):
        prob = tuple(sum(prob[i] * law[i][j] for i in range(4)) for j in range(4))
    return prob

def exact(x: F) -> dict:
    return {"rational": str(x), "decimal": float(x)}

def scenario(error: F, repair: F, drift: F, steps: int) -> dict:
    p = evolve(error, repair, drift, steps)
    q = evolve(error, repair, drift, steps, False)
    pc = sum(w for (s, _), w in zip(STATES, p) if s)
    ac = sum(w for (_, s), w in zip(STATES, p) if s)
    qc = sum(w for (s, _), w in zip(STATES, q) if s)
    # q uses the same reference origin: its initial label is the other origin.
    qa = sum(w for (_, s), w in zip(STATES, q) if s)
    procedure_tv = abs(pc - qc)
    attribution_tv = abs(ac - qa)
    assert attribution_tv == abs((1 - 2 * drift) ** steps)
    assert procedure_tv == 0
    assert p[3] == pc * ac  # independent channels in this synthetic law
    return {"parameters": {"error": str(error), "repair": str(repair),
                            "drift": str(drift), "steps": steps},
            "procedure_correct": exact(pc), "attribution_correct": exact(ac),
            "both_correct": exact(p[3]), "procedure_correct_attribution_wrong": exact(p[2]),
            "procedure_origin_tv": exact(procedure_tv),
            "attribution_origin_tv": exact(attribution_tv),
            "states": [{"procedure_correct": s[0], "attribution_correct": s[1],
                        "probability": exact(w)} for s, w in zip(STATES, p)]}

def run() -> dict:
    grid = [scenario(e, r, d, n) for e, r, d, n in product(
        (F(1, 100), F(1, 10), F(3, 10)), (F(0), F(1, 2), F(9, 10)),
        (F(0), F(1, 100), F(1, 10), F(3, 10)), (0, 1, 5, 20, 100))]
    primary = scenario(F(1, 10), F(9, 10), F(1, 10), 20)
    reference = scenario(F(1, 10), F(0), F(1, 10), 20)
    assert len(grid) == 180
    return {"status": "synthetic mathematical counterexample; no historical calibration",
            "source_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol_sha256": hashlib.sha256((HERE / "MODEL-PROTOCOL.md").read_bytes()).hexdigest(),
            "steps_are": "invented transmission steps, not generations or years",
            "states_order": [list(s) for s in STATES],
            "primary": primary, "unprotected_reference": reference, "grid": grid,
            "interpretation": "Procedure-only observations cannot distinguish the two initial origins under the declared law. Attribution labels may distinguish them to the specified total variation distance if the law is known. Neither calculation dates or identifies an ancient tradition."}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Output exists; preserve the endpoint and use a fresh path.")
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scenarios": len(result["grid"]),
                      "primary": {k: v for k, v in result["primary"].items()
                                  if k not in ("states", "parameters")}}))

if __name__ == "__main__":
    main()
