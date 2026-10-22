"""Check that run_winslow.evaluate() reproduces REBUS-BASE-RATE-2026-10-21 on the Tamil Lexicon.

The wrapper calls run_interlocks.run() in its synthetic mode. Given the Madras
Tamil Lexicon table, the DEDR table, the Sangam tokens and the concept pools of
the 2026-10-21 study, it must return the numbers of that study's
results-v2/interlocks.json exactly (same code, same seed).

    python experiments/2026-10-22-rebus-winslow/code/check_reuse.py OUT.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_winslow  # noqa: E402
from run_winslow import rebus, run_interlocks  # noqa: E402

V2 = run_winslow.ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "results-v2" / "interlocks.json"


def main(out_path):
    out_path = Path(out_path)
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    lex_path = rebus.DER / "tamil-lex-entries.jsonl"
    entries = [json.loads(l) for l in lex_path.open(encoding="utf-8")]
    dedr = rebus.load_dedr()
    tokens, hashes = run_interlocks.sangam_tokens()
    pools = json.loads(run_winslow.POOLS.read_text(encoding="utf-8"))
    got = run_winslow.evaluate(entries, dedr, tokens, hashes, pools, run_winslow.RAW / "check-reuse-v1")
    got = json.loads(json.dumps(got, ensure_ascii=False))
    ref = json.loads(V2.read_text(encoding="utf-8"))
    compare = {
        "lexicon": (got["lexicon"], ref["lexicon"]),
        "real_features": (got["real_features"], ref["real_features"]),
        "replacement_pools": (got["replacement_pools"], ref["replacement_pools"]),
        "real": (got["real"], ref["real"]),
        "null": (got["null"], ref["null"]),
    }
    same = {k: a == b for k, (a, b) in compare.items()}
    out = {"schema_version": "1.0", "task": "rebus-winslow/check-reuse", "synthetic": False,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "reference": {"path": run_winslow.rel(V2), "sha256": run_winslow.sha(V2)},
           "inputs": {run_winslow.rel(lex_path): run_winslow.sha(lex_path)},
           "code": {p.name: run_winslow.sha(p) for p in sorted(Path(__file__).resolve().parent.glob("*.py"))},
           "identical_sections": same, "I1_T0s_K50_rate": [got["null"]["I1_T0s"]["K50"]["rate"], ref["null"]["I1_T0s"]["K50"]["rate"]],
           "network_T0s_rate": [got["null"]["network_T0s"]["rate"], ref["null"]["network_T0s"]["rate"]],
           "pass": all(same.values())}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("identical_sections", "I1_T0s_K50_rate", "network_T0s_rate", "pass")}))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
