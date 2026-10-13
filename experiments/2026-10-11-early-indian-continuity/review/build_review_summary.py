"""Freeze the independent review status, capsule hashes and changed paths."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/review"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    out = HERE / "review-checks.json"
    changed = HERE / "changed-paths.json"
    if out.exists() or changed.exists():
        raise FileExistsError("Review status and path list refuse overwrite")
    capsule_names = ["source-checks-v1.json", "retention-checks-v1.json", "package-checks-v1.json", "final-source-checks-v2.json"]
    capsules = []
    for name in capsule_names:
        payload = read(HERE / name)
        capsules.append(dict(file=(HERE / name).relative_to(ROOT).as_posix(), sha256=digest(HERE / name),
                             passed=payload["passed"], failed=payload["failed"]))
    reviewed = [
        "REPORT.md", "MANUSCRIPT.md", "CLAIM-EVIDENCE.json",
        "institutions/PROTOCOL.md", "institutions/METHODS.md", "institutions/REPORT.md", "institutions/TESTS.md",
        "institutions/sources.json", "institutions/observations.json", "institutions/claims.json",
        "institutions/audit.py", "institutions/audit-v2.py", "institutions/AMENDMENT-eligibility.md",
        "institutions/run-v1/audit.json", "institutions/run-v2/audit.json", "institutions/source-checks.json",
        "memory/PROTOCOL.md", "memory/METHODS.md", "memory/REPORT.md", "memory/TESTS.md",
        "memory/sources.json", "memory/observations.json", "memory/claim-graph.json", "memory/analyze.py",
        "memory/run-v1/summary.json", "memory/run-v1/graph-audit.json", "memory/run-v1/compression-demo.json",
        "memory/verification.json", "memory/source-checks.json",
        "coordinator/MODEL-PROTOCOL.md", "coordinator/CONTROL-AND-MODEL.md", "coordinator/DEVELOPED-PROPOSALS.md",
        "coordinator/sources.json", "coordinator/observations.json", "coordinator/retention_model.py",
        "coordinator/run-v1/retention.json",
    ]
    finding_data = [
        ("R01", "Author-discovered institutional filter defect", "closed_verified",
         "The corrected filter requires a surviving cited textual observation; original endpoint and script remain preserved.",
         ["institutions/AMENDMENT-eligibility.md", "institutions/audit-v2.py", "institutions/run-v2/audit.json"]),
        ("R02", "Intermediate-only candidates require a qualified label", "closed_verified",
         "The report identifies source-reported archaeological candidates and the preliminary Sanauli/local-manufacture gap.",
         ["institutions/REPORT.md", "REPORT.md", "MANUSCRIPT.md"]),
        ("R03", "Reference repair differs from practical success among variants", "closed_verified",
         "Coordinator prose distinguishes an exact reference check from several workable variants and defines replica fire production as the observable target.",
         ["coordinator/CONTROL-AND-MODEL.md"]),
        ("R04", "Synthetic coherence and erasure are premises", "closed_verified",
         "The memory and integrated reports limit the construction to non-identification under stipulated erasure; neither synthetic model generates literary sophistication.",
         ["memory/REPORT.md", "memory/METHODS.md", "MANUSCRIPT.md"]),
        ("R05", "Source identity, witness scope and transport", "closed_verified",
         "Allon is 2022; the Gāndhārī variant does not date DN27 or received Pali DN2. Indexed Witzel1997 access differs from full reading; Witzel1995 transport exception is disclosed.",
         ["memory/sources.json", "memory/REPORT.md", "institutions/sources.json"]),
        ("R06", "Graph scope and review dependencies", "closed_verified",
         "Root report attributes five date axes to chronology review and limits the graph to its actual routes. README names PyMuPDF for reviewer source work.",
         ["REPORT.md", "README.md"]),
        ("R07", "Narrative-reset refinement follows the audit", "closed_verified",
         "Memory and root prose label the reset proposal as post-audit and unmeasured; EI-C11 preserves the distinction between motivating cases and validation.",
         ["memory/REPORT.md", "memory/TESTS.md", "REPORT.md", "MANUSCRIPT.md", "CLAIM-EVIDENCE.json"]),
        ("R08", "Reviewer literal-probe false failure", "closed_verified",
         "The retained first attempt expected multiple workable variants; correct prose used several workable variants. The checker alone was revised and all 59 final source checks pass.",
         ["review/check_final_sources_attempt_v1.py", "review/final-source-checks-v1.json", "review/check_final_sources.py", "review/final-source-checks-v2.json"]),
    ]
    findings = [dict(id=i, title=t, status=s, outcome=o,
                     locators=[(PACKAGE / p).relative_to(ROOT).as_posix() for p in paths])
                for i, t, s, o, paths in finding_data]
    root_report = (PACKAGE / "REPORT.md").read_text(encoding="utf-8")
    root_readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    memory_test = (PACKAGE / "memory/TESTS.md").read_text(encoding="utf-8")
    final_manual_checks = [
        dict(id="root-date-axis-attribution-repair", passed="The chronology audit separates" in root_report),
        dict(id="root-graph-transfer-scope", passed="memory graph blocks the specified transfers" in root_report),
        dict(id="root-review-runtime", passed="PyMuPDF" in root_readme and "fitz" in root_readme),
        dict(id="memory-reset-post-audit", passed="formulated after the documentary audit" in memory_test),
        dict(id="review-prose-inspected", passed=True, method="Manual connected-prose/source-claim review and repository scan with zero flags"),
        dict(id="historical-claims-inspected", passed=True, method="Manual review of source meanings, alternative mechanisms, selection and declared output scope"),
    ]
    result = dict(
        schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
        status="complete_no_unresolved_blocker", reviewer_role="independent source and adversarial reviewer",
        reviewed_scope="Institutions, memory, coordinator control/model/proposals and integrated report/manuscript; README reviewed for dependency/rights scope before final manifest links",
        source_census=dict(records=len(read(HERE / "sources.json")["sources"]),
                           typed_chronology_records=len(read(HERE / "chronology.json")["records"]),
                           scope="Download, inspected reading depth and dependent editions are separately recorded"),
        independent_check_capsules=capsules,
        final_capsule_totals=dict(passed=sum(c["passed"] for c in capsules), failed=sum(c["failed"] for c in capsules),
                                 scope="Code identity, exact arithmetic, selected source locators and declared rules; not historical confidence"),
        preserved_failed_attempt=dict(file=(HERE / "final-source-checks-v1.json").relative_to(ROOT).as_posix(),
                                      sha256=digest(HERE / "final-source-checks-v1.json"), passed=58, failed=1,
                                      superseded_by=(HERE / "final-source-checks-v2.json").relative_to(ROOT).as_posix(),
                                      reason="Literal synonym mismatch in reviewer checker; author endpoints unchanged"),
        findings=findings, final_manual_checks=final_manual_checks,
        unresolved_blockers=[],
        unresolved_empirical_questions=[
            "No candidate has a diagnostic archaeology/intermediate/textual join.",
            "Joint rarity, recovery process and appropriate comparison denominator remain to measure.",
            "Actual practice must be separated from textual copying and finished-object circulation.",
            "No historical transmission rates or reference-repair fidelity are calibrated.",
            "Reset/explanation association requires genre/topic/length controls; actual acquisition erasure needs additional evidence.",
        ],
        reviewed_file_sha256={(PACKAGE / p).relative_to(ROOT).as_posix(): digest(PACKAGE / p) for p in reviewed},
        rights=dict(raw_disposition="local-only", raw_tracking="independently checked no tracked files in new raw package",
                    source_assets_redistributed=False, source_access_is_not_permission=True),
        reproduction=dict(commands=[
            "python -B experiments/2026-10-11-early-indian-continuity/review/check_retention.py",
            "python -B experiments/2026-10-11-early-indian-continuity/review/check_sources.py",
            "python -B experiments/2026-10-11-early-indian-continuity/review/check_packages.py",
            "python -B experiments/2026-10-11-early-indian-continuity/review/check_final_sources.py",
        ], output_policy="Existing frozen outputs refuse overwrite; use an isolated copy or change only the output target before reproducing.",
           dependencies="Python standard library for numeric recounts; PyMuPDF/fitz for PDF source checks; local-only source witnesses required.")
    )
    if any(not c["passed"] for c in final_manual_checks) or result["final_capsule_totals"]["failed"]:
        raise ValueError("Review cannot close with a failed current check")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tracked_candidates = [p.relative_to(ROOT).as_posix() for p in sorted(HERE.rglob("*")) if p.is_file()]
    tracked_candidates.append(changed.relative_to(ROOT).as_posix())
    raw_paths = [p.relative_to(ROOT).as_posix() for p in sorted(RAW.rglob("*")) if p.is_file()]
    changes = dict(ownership=[HERE.relative_to(ROOT).as_posix(), RAW.relative_to(ROOT).as_posix()],
                   authored_and_review_output_paths=sorted(tracked_candidates),
                   local_only_raw_paths=raw_paths,
                   other_contributor_files_edited=[], global_navigation_edited=[],
                   no_commit_push_publish_or_automation=True)
    changed.write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status=result["status"], **result["final_capsule_totals"],
                         owned_outputs=len(tracked_candidates), local_only_files=len(raw_paths))))


if __name__ == "__main__":
    main()
