"""Check accounting and source identity without importing the result builder."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result_path = ROOT / args.out
    if result_path.exists():
        raise FileExistsError(result_path)
    checks = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "pass": bool(condition)})

    rows = list(csv.DictReader((OWN / "run-v1/target-dispositions.csv").open(encoding="utf-8")))
    summary = json.loads((OWN / "run-v1/summary.json").read_text(encoding="utf-8"))
    provenance = json.loads((OWN / "run-v1/provenance.json").read_text(encoding="utf-8"))
    obs = json.loads((OWN / "source-observations.json").read_text(encoding="utf-8"))
    targets = {f"H-{n}" for n in range(1719, 1767) if n != 1726}
    check("exact 47-target set", {r["target"] for r in rows} == targets and len(rows) == 47)
    check("38 export objects and nine absent", sum(r["export_status"] == "present" for r in rows) == 38 and sum(r["export_status"] == "absent" for r in rows) == 9)
    check("40 export faces", sum(int(r["export_faces"]) for r in rows) == 40)
    check("all operation assertions source-qualified", all(r["operation_source"] == "KM2010-P7" and r["operation_basis"] == "published-description" for r in rows))
    check("40 vessel operations", sum(r["source_operation"] == "impression in ceramic vessel wall before firing" for r in rows) == 40)
    check("six tags and one stopper", sum(r["source_operation"] == "separate clay sealing or tag" for r in rows) == 6 and sum(r["source_operation"] == "sub-conical jar stopper with impression" for r in rows) == 1)
    check("two identified primary target views", {r["target"] for r in rows if r["individual_caption"]} == {"H-1734", "H-1745"})
    check("no contents or reverse view coded", all(r["contents_observed"] == "False" and r["reverse_attachment_view"] == "False" for r in rows))
    check("two individual locus and unit-item additions", sum(bool(r["source_unit"]) and bool(r["source_item"]) for r in rows) == 2)
    check("no feasible classifier", summary["independent_group_feasibility"]["eligible_for_classifier"] is False)
    check("eligibility upper bound below threshold", summary["independent_group_feasibility"]["sealing_upper_bound_before_alias_text_closure"] < summary["independent_group_feasibility"]["required_per_class"])
    check("caption block has five objects", len(obs["caption_rows"]) == 5)
    check("three caption rows remain unjoined", sum(r["target"] is None for r in obs["caption_rows"]) == 3)
    check("sealing photos have no target assignment", all(r["target"] is None for r in obs["supplemental_witnesses"]))
    check("restored H1734 registration", next(r for r in rows if r["target"] == "H-1734")["source_registration"] == "H95-2526")
    check("H1745 sump-pit source locus", "sump pit" in next(r for r in rows if r["target"] == "H-1745")["deposition"])
    check("H1734 fill source locus", next(r for r in rows if r["target"] == "H-1734")["deposition"] == "Trench 10W, fill")
    for item in [provenance["corpus"], provenance["prior_frame"], *provenance["sources"]]:
        path = ROOT / item["path"]
        check("hash " + item["path"], path.exists() and digest(path) == item["sha256"])
    check("frozen protocol preserved", digest(OWN / "PROTOCOL.md") == provenance["protocol_sha256"] == (OWN / "PROTOCOL.sha256").read_text().split()[0])
    check("frozen observations preserved", digest(OWN / "source-observations.json") == provenance["annotations_sha256"])
    check("frozen builder preserved", digest(OWN / "build.py") == provenance["code_sha256"])
    corpus = [json.loads(x) for x in (ROOT / provenance["corpus"]["path"]).read_text(encoding="utf-8").splitlines()]
    registration_matches = {r["object_family_id"] for r in corpus if "H95-2407" in r["metadata"]["excavation-idno"]}
    unit_matches = {r["object_family_id"] for r in corpus if "H95-4450-31" in r["metadata"]["excavation-idno"]}
    check("registration unique and keyed to H1745", len(registration_matches) == 1 and all(r["source_cisi"] == "H-1745" for r in corpus if r["object_family_id"] in registration_matches))
    check("year-unit-item unique and keyed to H1734", len(unit_matches) == 1 and all(r["source_cisi"] == "H-1734" for r in corpus if r["object_family_id"] in unit_matches))
    unmatched = json.loads((OWN / "run-v1/unmatched-caption-checks.json").read_text())
    check("all unmatched searches returned zero", len(unmatched) == 3 and all(r["matches"] == 0 for r in unmatched))
    shot = json.loads((OWN / "shots-synthetic-v1.json").read_text())
    check("bench synthetic correctly identified", shot["task"] == "shots" and shot["synthetic"] is True and shot["pass"] is True)
    for name in ["all_shots_freeze_guard", "tamper_guard", "closure", "halves_disjoint", "site_proxies_stripped_and_confirmation_site_available", "spending_recorded", "spent_input_rejected_after_new_seed", "explicit_reuse_is_exploratory", "short_tablet_exception"]:
        check("bench " + name, shot[name] is True)
    if (OWN / "replay-v1").exists():
        for name in ["target-dispositions.csv", "summary.json", "unmatched-caption-checks.json", "provenance.json"]:
            check("byte-identical replay " + name, digest(OWN / "run-v1" / name) == digest(OWN / "replay-v1" / name))
    payload = {"verification_tier": "submitted; author integrity check", "checks": checks,
               "passed": sum(c["pass"] for c in checks), "failed": sum(not c["pass"] for c in checks)}
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: payload[k] for k in ["passed", "failed", "verification_tier"]}))
    raise SystemExit(bool(payload["failed"]))


if __name__ == "__main__":
    main()
