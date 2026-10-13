"""Pin the final substantive review and check its documentary/numerical joins.

Uses only the standard library; imports no coordinator or prior model functions.
This code verifies artifacts already independently reconstructed, not history.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
REPO = EXPERIMENT.parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def pointer(value, loc: str):
    if not loc:
        return value
    if not loc.startswith("/"):
        raise ValueError(f"Not an RFC 6901 pointer: {loc}")
    for part in loc[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "reviewer-final-v1")
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(HERE):
        raise SystemExit("Output must be within the owned review directory")
    if out.exists():
        raise SystemExit(f"Refusing existing output directory: {out}")
    out.mkdir()
    checks = []

    def check(label: str, condition: bool):
        checks.append({"check": label, "passed": bool(condition)})
        if not condition:
            raise AssertionError(label)

    try:
        root_markdown = [
            "README.md", "PROTOCOL.md", "THEORY.md", "MODEL-RESULTS.md",
            "EMPIRICAL-PROTOCOL.md", "MANUSCRIPT.md", "REPORT.md",
            "REVIEW-RESPONSE.md", "RETROSPECTIVE.md",
        ]
        reviewed = [EXPERIMENT / p for p in root_markdown]
        reviewed += [EXPERIMENT / "CLAIM-EVIDENCE.json",
                     EXPERIMENT / "coordinator/source-summary-v1.json"]
        for p in reviewed:
            check(f"reviewed file exists: {repo_relative(p)}", p.is_file())

        claim_map = read(EXPERIMENT / "CLAIM-EVIDENCE.json")
        claims = claim_map["claims"]
        check("all 15 distinct coordinator claims", len(claims) == 15 and
              {c["id"] for c in claims} == {f"P{i:02d}" for i in range(1, 16)})
        observation_joins = 0
        output_joins = 0
        source_files = set()
        output_files = set()
        for c in claims:
            for key in ("discussion", "test", "independent_check"):
                check(f"{c['id']} {key} exists", (REPO / c[key]).is_file())
            for ref in c["observations"]:
                path = REPO / ref["file"]
                source_files.add(path)
                obs = read(path)["observations"]
                ids = [r.get("observation_id", r.get("id")) for r in obs]
                check(f"distinct observation IDs in {ref['file']}",
                      len(ids) == len(set(ids)) and None not in ids)
                for oid in ref["ids"]:
                    check(f"{c['id']} source observation {oid}", oid in ids)
                    observation_joins += 1
            for ref in c["outputs"]:
                path = REPO / ref["file"]
                output_files.add(path)
                value = pointer(read(path), ref["pointer"])
                if "equals" in ref:
                    check(f"{c['id']} exact output {ref['pointer']}",
                          value == ref["equals"])
                elif "excludes" in ref:
                    check(f"{c['id']} output excludes {ref['excludes']}",
                          ref["excludes"] not in value)
                else:
                    raise AssertionError(f"Unspecified output claim: {c['id']}")
                output_joins += 1

        summary = read(EXPERIMENT / "coordinator/source-summary-v1.json")
        for name, digest in summary["input_sha256"].items():
            path = EXPERIMENT / name
            source_files.add(path)
            check(f"source summary input pin {name}", sha(path) == digest)
        literature_sources = read(EXPERIMENT / "literature/SOURCES.json")["sources"]
        literature_obs = read(EXPERIMENT / "literature/OBSERVATIONS.json")["observations"]
        evidence_sources = read(EXPERIMENT / "evidence/sources.json")["included_primary_works"]
        evidence_obs = read(EXPERIMENT / "evidence/observations.json")["observations"]
        calculated_literature = {
            "source_records": len(literature_sources),
            "scoped_primary_works": sum(s["selected_primary_work"] is True for s in literature_sources),
            "observations": len(literature_obs),
        }
        check("independent literature census", summary["literature"] == calculated_literature)
        fields = ["measured_service_delivery", "task_duration_bounds", "task_window",
                  "demand_lower_bound", "initial_delivery_upper_bound", "imports_upper_bound"]
        for row in evidence_obs:
            check(f"all quantity fields declared for {row['observation_id']}",
                  all(f in row for f in fields))
        calculated_application = {
            "included_works": len(evidence_sources),
            "observations": len(evidence_obs),
            "unresolved_count_by_field": {
                f: sum(row[f] is None for row in evidence_obs) for f in fields
            },
            "fully_measured_bound_records": sum(
                all(row[f] is not None for f in fields) for row in evidence_obs
            ),
        }
        check("independent archaeological census and missing-quantity counts",
              summary["archaeological_application"] == calculated_application)

        baseline_path = EXPERIMENT / "coordinator/run-v1/results.json"
        co_path = HERE / "co-production-v1/results.json"
        baseline = read(baseline_path)
        shared = read(co_path)
        source_files.add(baseline_path)
        check("shared-operation frozen baseline pin", sha(baseline_path) == shared["baseline_results_sha256"])
        baseline_worlds = {(w["budget"], w["shock_support"]): w
                           for w in baseline["worlds"] if w["skill_age"] == 1}
        check("all 16 aging-skill baseline worlds", len(baseline_worlds) == 16)
        gaining = added = removed = 0
        for world in shared["worlds"]:
            key = (world["budget"], world["shock_support"])
            for mode in ("possible", "robust"):
                old = {tuple(s) for s in baseline_worlds[key][mode]["infinite_kernel"]}
                new = {tuple(s) for s in world[mode]["infinite_kernel"]}
                extra, lost = new - old, old - new
                check(f"independent shared-operation inclusion {key}/{mode}", not lost)
                check(f"independent shared-operation added list {key}/{mode}",
                      extra == {tuple(s) for s in world[mode]["added_from_baseline"]})
                check(f"independent shared-operation removed list {key}/{mode}",
                      lost == {tuple(s) for s in world[mode]["removed_from_baseline"]})
                gaining += bool(extra)
                added += len(extra)
                removed += len(lost)
        calculated_shared = {"worlds": len(shared["worlds"]),
                             "world_mode_infinite_sets_gaining": gaining,
                             "state_memberships_added": added,
                             "state_memberships_removed": removed}
        check("independent shared-operation aggregate gains",
              summary["shared_operation_variant"] == calculated_shared)

        endpoint_totals = [
            (HERE / "model-checks-v1/checks.json", "checks_passed", 5218),
            (HERE / "source-checks-v3/checks.json", "checks_passed", 90),
            (HERE / "co-production-v1/results.json", "checks_passed", 1133),
            (EXPERIMENT / "coordinator/co-production-checks-v1/checks.json", "checks_passed", 1968),
            (HERE / "integrity-checks-v3/checks.json", "checks_passed", 50),
        ]
        for path, count_key, expected in endpoint_totals:
            doc = read(path)
            output_files.add(path)
            check(f"recorded total {repo_relative(path)}", doc[count_key] == expected)
            check(f"all recorded assertions pass {repo_relative(path)}",
                  len(doc["checks"]) == expected and all(r["passed"] for r in doc["checks"]))
        counter_path = HERE / "counterexamples-v1/counterexamples.json"
        counter = read(counter_path)
        check("all six declared counterexample assertions", len(counter["assertions"]) == 6 and
              all(v is True for v in counter["assertions"].values()))
        output_files.add(counter_path)

        evidence_audit_path = EXPERIMENT / "evidence/run-v2/summary.json"
        evidence_audit = read(evidence_audit_path)
        output_files.add(evidence_audit_path)
        check("evidence contributor documentary/source-scope audit", evidence_audit["checks"] == 275 and
              evidence_audit["passed"] == 275 and evidence_audit["failed"] == [])
        check("evidence audit agrees with census", evidence_audit["observations"] == 34 and
              evidence_audit["included_primary_works"] == 14)

        anchor_path = HERE / "final-source-controls.json"
        anchors = read(anchor_path)
        check("archaeological anchor ledger pin", anchors["sources_ledger_sha256"] ==
              sha(EXPERIMENT / "evidence/sources.json"))
        check("archaeological anchor observation pin", anchors["observations_ledger_sha256"] ==
              sha(EXPERIMENT / "evidence/observations.json"))
        check("three direct archaeological witness reviews", len(anchors["records"]) == 3)
        page_count = 0
        for record in anchors["records"]:
            check(f"direct archaeological witness pin {record['evidence_source_id']}",
                  sha(REPO / record["witness_path"]) == record["witness_sha256"])
            page_count += len(record["pdf_pages_one_based"])
        check("four directly inspected archaeological PDF pages", page_count == 4)
        output_files.add(anchor_path)

        # The following decision follows the documented substantive readings,
        # not the mechanical assertions above or an automated truth test.
        result = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "status": "passed final substantive and artifact-join review",
            "no_unresolved_blockers": True,
            "scope": "Exact pinned exploratory theory and manuscript; arithmetic/construction consistency and selected source scope. No historical calibration, completed causal comparison or exhaustive priority assessment.",
            "protocol_sha256": sha(HERE / "FINAL-REVIEW-PROTOCOL.md"),
            "checker_sha256": sha(Path(__file__)),
            "reviewed_file_sha256": {repo_relative(p): sha(p) for p in reviewed},
            "supporting_file_sha256": {repo_relative(p): sha(p) for p in sorted(source_files | output_files)},
            "checks_passed": len(checks),
            "checks": checks,
            "claim_join_summary": {"claims": len(claims), "observation_id_joins": observation_joins,
                                   "exact_output_joins": output_joins},
            "reconstructed_source_summary": {"literature": calculated_literature,
                                             "archaeological_application": calculated_application,
                                             "shared_operation_variant": calculated_shared},
            "verification_totals": {
                "independent_baseline_model_checks": 5218,
                "declared_counterexample_assertions": 6,
                "reviewer_precedent_source_integrity_checks": 90,
                "reviewer_precedent_works_at_recorded_scope": 7,
                "post_baseline_shared_operation_checks": 1133,
                "coordinator_independent_shared_operation_checks": 1968,
                "review_package_integrity_checks": 50,
                "evidence_contributor_documentary_and_source_scope_checks": 275,
                "additional_direct_archaeological_anchor_works": 3,
                "additional_direct_archaeological_anchor_pdf_pages": 4,
                "final_artifact_join_and_pin_checks": len(checks),
            },
            "manual_substantive_assessment": {
                "decision": "No unresolved blocker within the stated exploratory scope",
                "resolved_revisions": [
                    "Necessary condition tied to outcome, horizon, boundary and actual supply law",
                    "Finite initial stocks and demand contraction retained as countercases",
                    "Full state information, action-before-shock quantifiers and event order explicit",
                    "Joint schedule distinguished from separate feasibility and voluntary enactment",
                    "Delivered-output residual does not identify repairs or a particular institution",
                    "Unknown baseline bounds leave the conservation result uninformative",
                    "Work-window additivity accounts for shared outputs and carried inventory",
                    "Shared-operation variant labelled post-baseline and uncalibrated",
                    "Harappa replacement and Dholavira hiatus/selective reuse retain source resolution",
                    "Source lineages and missing quantities retained; no numerical Harappan budget",
                    "Outcome-exposed future comparisons remain exploratory",
                    "Close predecessors delimit the contribution as a proposed inference procedure",
                ],
                "supporting_review_documents": ["review/REVIEW.md", "review/MANUSCRIPT-REVIEW.md",
                                                "review/CO-PRODUCTION-RESULTS.md", "review/final-source-controls.json"],
                "nonblocking_unresolved_items": [
                    "The evidence sample has no measured quantities adequate for a numerical renewal bound",
                    "The evidence audit retains S12 Table 4 counts summing to 171 against its stated sample of 172; no fit uses it",
                    "The proposed archaeological discrimination tests have not been conducted",
                ],
            },
            "excluded_scope": ["coordinator finalizer and final repository verification",
                               "global navigation and final package manifest",
                               "whole-publication reading beyond each source's declared loci"],
            "prior_endpoints_preserved": True,
        }
        (out / "checks.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": result["status"], "checks_passed": len(checks),
                          "claims": len(claims), "output_joins": output_joins,
                          "observation_joins": observation_joins,
                          "endpoint": repo_relative(out / "checks.json")}, indent=2))
    except Exception as exc:
        failure = {"created_utc": datetime.now(timezone.utc).isoformat(),
                   "status": "failed; preserved attempt", "error": repr(exc), "checks": checks}
        (out / "failure.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
