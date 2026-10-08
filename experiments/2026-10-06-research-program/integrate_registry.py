"""Add the October 6 program's reviewed package entries to the shared registry.

Each package proposed a registry entry in its own directory. This script copies
those entries into knowledge/experiments/registry.json under normalized IDs,
adds the package review files to each entry's evidence and records the
proposed ID. A rerun adds only the entries that are not yet present, except
that entries named in REFRESH are rebuilt from their package's current
proposal (keeping their ID and status) because the package recorded new
endpoints after integration. Other existing entries stay unchanged.
Run from the repository root:

    python experiments/2026-10-06-research-program/integrate_registry.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "knowledge/experiments/registry.json"

# Normalized ID, package directory, status assigned at integration.
PACKAGES = [
    ("MODERN-RESTORATION-01", "experiments/2026-10-06-modern-restoration", "exploratory-reused-masks-reviewed"),
    ("EVIDENCE-CENSUS-SITES-01", "experiments/2026-10-06-evidence-census/sites-and-publications", "superseded-by-regional-batches"),
    ("EVIDENCE-CENSUS-SITES-PAK-AFG-01", "experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan", "exploratory-source-census"),
    ("EVIDENCE-CENSUS-SITES-GUJARAT-01", "experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra", "exploratory-source-census"),
    ("EVIDENCE-CENSUS-SITES-NORTH-INDIA-01", "experiments/2026-10-06-evidence-census/sites-deep/c-north-india", "exploratory-source-census"),
    ("EVIDENCE-CENSUS-SITES-ABROAD-01", "experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad", "exploratory-source-census"),
    ("EVIDENCE-CENSUS-COLLECTIONS-01", "experiments/2026-10-06-evidence-census/collections-and-datasets", "exploratory-source-census"),
    ("EVIDENCE-CENSUS-SYNTHESIS-01", "experiments/2026-10-06-evidence-census/synthesis", "exploratory-synthesis-reviewed"),
    ("BYPRODUCT-INVENTORY-01", "experiments/2026-10-06-byproduct-inventory", "exploratory-assessment-reviewed"),
    ("CHRONOLOGY-REGION-01", "experiments/2026-10-06-chronology-region", "exploratory-reviewed-with-amendments"),
    ("SIGN-CONTEXT-SEALS-01", "experiments/2026-10-06-sign-context-and-seals", "exploratory-reviewed-with-amendments"),
    ("BACKWARD-CHRONOLOGY-01", "experiments/2026-10-06-backward-chronology", "exploratory-source-assembly-reviewed"),
    ("FIELD-RECOMMENDATIONS-01", "experiments/2026-10-06-field-recommendations", "exploratory-survey-reviewed"),
    ("WEIGHT-METROLOGY-01", "experiments/2026-10-06-weight-metrology", "exploratory-reviewed-with-amendments"),
    ("RESEMBLANCE-BASELINE-01", "experiments/2026-10-06-resemblance-baseline", "exploratory-pilot-reviewed"),
    ("OBJECT-LEDGER-PILOT-01", "experiments/2026-10-07-object-ledger", "exploratory-pilot-reviewed-with-amendments"),
    ("HELSINKI1979-DIGITIZATION-01", "experiments/2026-10-07-helsinki1979-digitization", "failed-frozen-evaluations-quarantined"),
    ("HELSINKI1979-ROW-VERIFICATION-01", "experiments/2026-10-08-helsinki1979-row-verification", "two-pilots-run-screen-failed-awaiting-owner-decision"),
    ("HELSINKI1979-CHART-REFERENCE-AUDIT-01", "experiments/2026-10-08-chart-reference-audit", "exploratory-reviewed-chart-v2.1"),
    ("HF-PUBLIC-RELEASE-01", "experiments/2026-10-08-hf-public-release", "private-preview-awaiting-owner-decisions"),
]

# Entries already integrated whose package has since recorded new endpoints. A rerun copies the
# package's current proposed fields over the integrated entry, keeping its ID and adding the reviews.
REFRESH = {
    "HELSINKI1979-DIGITIZATION-01": "experiments/2026-10-07-helsinki1979-digitization",
}

# Coordinator results recorded after a package's own entry was written.
COORDINATOR_NOTES = {
    "HELSINKI1979-ROW-VERIFICATION-01": (
        " Pilot 2 (coordinator record, experiments/2026-10-08-helsinki1979-row-verification/pilot-2/2026-10-08-v1/PILOT-2-RESULTS.md):"
        " two blind readers with clarified conventions, chart v2.1 labels and v3 geometry agreed on 132 of 144 rows;"
        " 12 (8.3%) went to adjudication. First-pass controls 10/12 all fields per role with one number misread;"
        " after adjudication 12/12 on number, classification, count and crop and 11/12 on the strict sequence."
        " 4,224,785 combined tokens; full-run projection about 340 million tokens."
    ),
}


def load_entry(directory):
    data = json.loads((ROOT / directory / "registry-entry.json").read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        if len(data) != 1:
            raise SystemExit(f"{directory}: expected one proposed entry, found {len(data)}")
        data = data[0]
    return data


def main():
    raw = REGISTRY.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    registry = json.loads(raw)
    existing = {entry["id"] for entry in registry["experiments"]}
    added = 0
    def build(pid, directory, status):
        proposed = load_entry(directory)
        evidence = list(proposed.get("evidence", []))
        for review in ("REVIEW.md", "REVIEW-2.md", "REVIEW-V3.md", "REVIEW-0.3.0.md"):
            path = f"{directory}/{review}"
            if (ROOT / path).exists() and path not in evidence:
                evidence.append(path)
        return {
            "id": pid,
            "theme": proposed["theme"],
            "status": status,
            "question": proposed["question"],
            "outcome": proposed["outcome"] + COORDINATOR_NOTES.get(pid, ""),
            "challenge": proposed["challenge"],
            "remedy": proposed["remedy"],
            "evidence": evidence,
            "retry_when": proposed["retry_when"],
            "proposed_id": proposed.get("id"),
            "package": directory,
        }

    refreshed = 0
    for i, entry in enumerate(registry["experiments"]):
        if entry["id"] in REFRESH:
            new = build(entry["id"], REFRESH[entry["id"]], entry["status"])
            if new != entry:
                registry["experiments"][i] = new
                refreshed += 1
    for pid, directory, status in PACKAGES:
        if pid in existing:
            continue
        added += 1
        registry["experiments"].append(build(pid, directory, status))
    program_entry = {
        "id": "RESEARCH-PROGRAM-2026-10-06",
        "theme": "multi-model research program, lecture check and integration",
        "status": "completed-coordination-record",
        "question": "Which further analyses, censuses and literature checks can extend the project beyond decipherment, and do Dennys Frenez's lecture statements hold against the captions and the local corpus?",
        "outcome": "Ran fifteen work packages through the Codex CLI (GPT-6.1-Sol for analysis, GPT-6-Luna for long reading); Claude Sonnet 5.5 reviewed each finished package or group, and required fixes were applied in the same Codex session. Checked the user's summary of Frenez's 3 October 2026 lecture against its English captions at every timestamp and turned its further statements into tests for packages D1, D2 and E.",
        "challenge": "GPT-6-Luna outputs were thin or misattributed; the YouTube transcript endpoint failed; the system disk filled and crashed five runs; editing a running shell script broke its final lines; packages read each other's unfinished outputs; some census files copied search snippets into title fields.",
        "remedy": "Moved source-citing work to GPT-6.1-Sol and reran with review-driven fixes; read the caption track loaded by the player without saving the transcript; purged caches, compressed logs and resumed interrupted sessions; kept running scripts unchanged; removed borrowed figures; trimmed 17 copied titles and kept originals locally.",
        "evidence": [
            "experiments/2026-10-06-research-program/README.md",
            "experiments/2026-10-06-research-program/REPORT.md",
            "experiments/2026-10-06-research-program/frenez-talk-check.md",
            "experiments/2026-10-06-research-program/COMMON.md",
            "knowledge/retrospectives/2026-10-06-research-program.md",
        ],
        "retry_when": "A new package needs the same multi-model pattern; reuse COMMON.md and the review template, keep source-citing work on the stronger model, check free disk space before parallel runs, and never edit a script that is running.",
    }
    if program_entry["id"] not in existing:
        registry["experiments"].append(program_entry)
        added += 1
    text = json.dumps(registry, indent=2, ensure_ascii=True) + "\n"
    REGISTRY.write_bytes(text.replace("\n", newline).encode("utf-8"))
    print(f"added {added} entries, refreshed {refreshed}; registry now has {len(registry['experiments'])}")


if __name__ == "__main__":
    main()
