"""Check safe reports and old-rank aggregates, without opening reserved payloads."""
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out):
    if out.exists():
        raise SystemExit("Preserve previous output; choose a new endpoint")
    farm = EXP / "2026-10-20-fresh-test-collection"
    foreign = EXP / "2026-10-20-foreign-script-audit"
    blind = EXP / "2026-10-20-foreign-script-blind-review"
    coverage = read(farm / "coverage-summary.json")
    reserve = read(farm / "reservation-manifest.json")
    custody_check = read(farm / "reservation-verification.json")
    checks = {
        "candidate_dispositions_reconcile": sum(coverage["dispositions"].values()) == coverage["candidate_identifier_rows"],
        "coverage_and_reserve_agree": coverage["candidate_identifier_rows"] == reserve["candidate_identifier_rows"],
        "reserve_approves_no_objects_for_scoring": reserve["test_eligible"] == 0,
        "no_universal_freshness_claim": reserve["universal_freshness_claim"] is False,
        "custodian_verification_count_matches_manifest": custody_check["payload_files_verified"] == reserve["payload_hash_manifest"]["entries"],
        "custodian_reports_all_frozen_hashes_match": custody_check["pass"] is True,
    }
    for name, expected in read(blind / "freeze.json")["files"].items():
        checks["blind_freeze:" + name.replace("\\", "/")] = sha(ROOT / name) == expected
    with (foreign / "legacy-ranks-and-eligibility.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    observed = {}
    scenarios = [("legacy_pooled", None), ("circular_only", "circular_eligible"),
                 ("circular_exclude_tablet", "tablet_excluded_eligible"),
                 ("circular_exclude_tablet_and_uncertain_composition", "text_conservative_eligible")]
    saved = read(foreign / "sensitivity.json")["variants"]
    for name, flag in scenarios:
        selected = [r for r in rows if flag is None or r[flag] == "1"]
        west = [r for r in selected if r["group"] == "west_asia"]
        south = [r for r in selected if r["group"] == "south_asia"]
        delta = sum(float(r["u_surprisal"]) for r in west) / len(west) - sum(float(r["u_surprisal"]) for r in south) / len(south)
        checks["difference:" + name] = abs(delta - saved[name]["difference"]) < 1e-12
        checks["counts:" + name] = len(west) == saved[name]["west_faces"] and len(south) == saved[name]["south_faces"]
        observed[name] = {"west_faces": len(west), "south_faces": len(south), "difference": delta}
    input_paths = [farm / "coverage-summary.json", farm / "reservation-manifest.json",
                   farm / "reservation-verification.json", foreign / "legacy-ranks-and-eligibility.csv",
                   foreign / "sensitivity.json", blind / "freeze.json"]
    result = {
        "utc": dt.datetime.now(dt.timezone.utc).isoformat(), "pass": all(checks.values()),
        "checks": checks, "recomputed": observed,
        "inputs": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in input_paths},
        "reserved_payload_files_opened": 0,
        "scope": "Aggregate accounting and old-rank arithmetic independently checked. Raw acquisition hashes are the custodian's reported verification, not a parent reread. Archaeological identity and script eligibility remain pending."
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"pass": result["pass"], "checks": len(checks), "reserved_payload_files_opened": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args().out)
