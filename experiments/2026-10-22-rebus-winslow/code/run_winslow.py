"""Rerun the interlock searches of REBUS-BASE-RATE-2026-10-21 on Winslow's dictionary (1862).

The searches, pools, nulls, draw counts and seed are those of
experiments/2026-10-21-rebus-base-rate/code/run_interlocks.py, which this script
imports unchanged and calls with the Winslow compound table in place of the
Madras Tamil Lexicon. run_interlocks.run() is called in its synthetic mode,
which writes its full output (with compound lists) to the directory it is given
and adds no provenance block; we give it a local directory under
data/raw/2026-10-22-rebus-winslow/ and write the tracked result here, with this
package's provenance, the compound lists moved to a local detail file, and the
decision for prediction P2 of C-0014.

    python -I experiments/2026-10-22-rebus-winslow/code/run_winslow.py OUTDIR

OUTDIR receives interlocks.json. The script refuses to run when any file listed
in FREEZE.json has changed, and refuses to overwrite.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE_CODE = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "code"
sys.path.insert(0, str(BASE_CODE))
import rebus  # noqa: E402
import run_interlocks  # noqa: E402

PKG = ROOT / "experiments" / "2026-10-22-rebus-winslow"
RAW = ROOT / "data" / "raw" / "2026-10-22-rebus-winslow"
TABLE = RAW / "derived-v1" / "winslow-entries.jsonl"
POOLS = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "pools-v1.json"
P2_THRESHOLD = 0.20
DETAIL_KEYS = ("A_compounds", "B_compounds_sample", "A_restricted", "B_restricted")
FIELDS = ("page", "kind", "head", "translit", "members", "seg", "star", "pos", "verb", "gloss")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    p = Path(p).resolve()
    return (str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)).replace("\\", "/")


def load_entries(path=TABLE):
    out = []
    for line in Path(path).open(encoding="utf-8"):
        r = json.loads(line)
        out.append({k: r.get(k) for k in FIELDS})
    return out


def evaluate(entries, dedr, tokens, sangam_hashes, pools, local_dir):
    """Run the frozen searches on `entries` and return the result without the compound lists."""
    local_dir = Path(local_dir)
    full = local_dir / "interlocks-synthetic.json"
    if full.exists():
        raise SystemExit(f"refusing to overwrite {full}")
    local_dir.mkdir(parents=True, exist_ok=True)
    out = run_interlocks.run(local_dir, entries, dedr, tokens, sangam_hashes, pools, synthetic=True)
    detail = {k: out["real"].pop(k) for k in DETAIL_KEYS}
    detail_path = local_dir / "interlocks-detail.json"
    detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8")
    out["local_detail"] = {"path": rel(detail_path), "sha256": sha(detail_path),
                           "full_output": {"path": rel(full), "sha256": sha(full)}}
    rate = out["null"]["I1_T0s"]["K50"]["rate"]
    out["decision"]["P2_rule"] = ("C-0014 P2 passes if the share of random replacement pairs (both muruku and mīṉ "
                                  "replaced, pools of 50 matched on productivity and Sangam frequency, stated rule T0s) "
                                  "with a shared compound member is above 0.20")
    out["decision"]["P2_rate"] = rate
    out["decision"]["P2_pass"] = rate > P2_THRESHOLD
    return out


def check_freeze():
    freeze = json.loads((PKG / "FREEZE.json").read_text(encoding="utf-8"))
    changed = []
    for group in ("protocol", "code", "reused_code", "inputs"):
        items = freeze[group] if group != "protocol" else {freeze["protocol"]["path"]: freeze["protocol"]["sha256"]}
        for path, digest in items.items():
            if sha(ROOT / path) != digest:
                changed.append(path)
    return freeze, changed


def main(outdir):
    outdir = Path(outdir)
    target = outdir / "interlocks.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    freeze, changed = check_freeze()
    if changed:
        print("files changed since FREEZE.json:", changed)
        return 1
    entries = load_entries()
    dedr = rebus.load_dedr()
    tokens, sangam_hashes = run_interlocks.sangam_tokens()
    pools = json.loads(POOLS.read_text(encoding="utf-8"))
    out = evaluate(entries, dedr, tokens, sangam_hashes, pools, RAW / outdir.name)
    out["task"] = "rebus-winslow/interlocks"
    out["synthetic"] = False
    out["lexicon_source"] = "Winslow, A comprehensive Tamil and English dictionary of high and low Tamil (1862), DSAL edition"
    out["run_mode"] = ("run_interlocks.run() of REBUS-BASE-RATE-2026-10-21 called unchanged in its synthetic mode, "
                       "which suppresses its Tamil Lexicon provenance block and local path; the provenance below is this package's")
    out["created_utc"] = datetime.now(timezone.utc).isoformat()
    out["provenance"] = {
        "freeze": {"path": rel(PKG / "FREEZE.json"), "sha256": sha(PKG / "FREEZE.json")},
        "protocol": freeze["protocol"],
        "code": {rel(p): sha(p) for p in sorted((PKG / "code").glob("*.py"))},
        "reused_code": {rel(BASE_CODE / n): sha(BASE_CODE / n) for n in ("rebus.py", "run_interlocks.py", "parse_tamil_lex.py")},
        "inputs": {rel(p): sha(p) for p in (TABLE, rebus.DER / "dedr-entries.jsonl", POOLS)},
        "sangam_files": sangam_hashes, "sangam_tokens": len(tokens),
    }
    outdir.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["decision"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
