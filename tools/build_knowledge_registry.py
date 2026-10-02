"""Index saved investigations without rerunning expensive research analyses."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def entry(identifier, theme, status, question, outcome, challenge, remedy, evidence, retry_when):
    return dict(id=identifier, theme=theme, status=status, question=question, outcome=outcome,
                challenge=challenge, remedy=remedy, evidence=evidence, retry_when=retry_when)

def main():
    items = [
        entry("ROOT-01", "corpus", "completed-source-audit", "What observational corpus is usable?",
              "Pinned and normalized source records; RTL/single-line filters and inventory namespaces recorded.",
              "Variant codes, missing/damaged marks and interpretive source fields could contaminate observations.",
              "Excluded interpretation fields, retained raw observation provenance and separated inventories.",
              ["research/corpus/CORPUS_REPORT.md", "research/corpus/normalize_lipi.py"], "A new pinned corpus or corrected expert transcription is available."),
        entry("ROOT-02", "structural prediction", "verified-computation", "Does local order improve held-out score under artifact controls?",
              "Positive gain under the declared position/length/site/type reference; not language identification.",
              "Related artifacts, tuning and null fitting can create optimistic comparisons.",
              "Transitive alias/text groups, nested fitting and complete-procedure nulls.",
              ["research/methods/FINDINGS.md", "research/methods/results/joint_nested_unique_conditioned_1000"], "A new corpus, faithful prior baseline or independently frozen comparison changes the test."),
        entry("ROOT-03", "restoration", "superseded", "Can an early deduplicated restoration split generalize?",
              "Early endpoint is superseded; do not use its better numbers as the current benchmark.",
              "Choosing unique-string representatives discarded physical aliases.",
              "Preserved aliases before group closure and reran in separate output directories.",
              ["results/restoration_superseded_lost_aliases/SUPERSEDED.md"], "Do not rerun the defective design; inspect it only to understand leakage."),
        entry("ROOT-04", "restoration", "verified-computation", "Can one deliberately hidden known sign be ranked?",
              "33.8% exact top-one versus 17.0% position/metadata baseline on 8,009 slots.",
              "Slot micro accuracy conceals poor rare-code performance and confidence calibration.",
              "Added frequency, text-weighting, grouped uncertainty and site-transfer audits.",
              ["src/restoration.py", "results/restoration", "research/RESTORATION_SENSITIVITY.md"], "Fresh reviewed graphic cases or a new frozen restoration method are available."),
        entry("ROOT-05", "restoration site transfer", "completed-sensitivity", "Does restoration improve across held-out sites?",
              "Positive selected-site gains; no semantic or place-name reading follows.",
              "Aliases at other sites and excluded short faces can connect test artifacts to training.",
              "Excluded entire components with any held-out-site face in the full observational register.",
              ["results/restoration_crosssite", "src/methods/alias_safe_site_transfer.py"], "New sites/context or independent source-reviewed evaluation is available."),
        entry("ROOT-06", "independent annotation", "verified-computation", "Does structural gain survive another manual encoding?",
              "74 scored faces, approximately +0.725 bits/candidate event; shared archaeological sources.",
              "Crosswalk candidates overlap, source objects repeat, unseen candidates have no supported mass.",
              "Candidate-event recursion, family and compatible-text exclusions, retained unsupported events.",
              ["src/independent_annotator.py", "results/independent_annotator", "research/INDEPENDENT_ANNOTATOR_PLAN.md"], "A genuinely fresh expert-reviewed transcription block can be frozen."),
        entry("ROOT-07", "independent annotation", "exploratory-source-quality-sensitivity", "Do source-quality exclusions change the score?",
              "Post-outcome source exclusions retained gain; not independent confirmation.",
              "A source review after outcome creates selection sensitivity.",
              "Marked the quality sensitivity exploratory and kept the initial endpoint.",
              ["src/independent_quality_sensitivity.py", "research/INDEPENDENT_TEXT_SENSITIVITY.md"], "Quality rules can be fixed before new annotation outcomes."),
        entry("ROOT-08", "gap count", "failed-comparator", "Can the number of erased signs be inferred statistically?",
              "Matched estimator 46.3% versus 51.1% always-one; tested approach failed.",
              "The artificial masking law differs from the source-length distribution.",
              "Matched the prior to gap sampling and added the dominant constant-one baseline.",
              ["src/gap_restoration.py", "src/methods/gap_design_matched.py", "results/gap_restoration"], "Physical gap geometry or a genuinely new model with frozen masking controls is available."),
        entry("ROOT-09", "context", "exploratory-no-semantic-anchor", "Can site/type/motif predict a functional interpretation?",
              "Context diagnostics were generated; no authenticated function or lexical value.",
              "Broad metadata, object dependence and ambiguous source contexts limit interpretation.",
              "Compared metadata-conditioned alternatives and reviewed physical sources.",
              ["src/context_study.py", "results/context", "src/microcontext.py", "results/microcontext"], "Fine source-verified findspots, materials and independently observed functions become available."),
        entry("ROOT-10", "paired surfaces", "exploratory-no-semantic-anchor", "Do opposed faces create a decoding constraint?",
              "Paired-face relationships and source inconsistencies audited; no recovered meaning.",
              "Face relations and historical/current object IDs are not interchangeable.",
              "Preserved physical-family grouping and traced candidate catalogue joins.",
              ["src/paired_surfaces.py", "results/paired", "research/PAIRED_SURFACE_PLAN.md"], "Photographic identity and independent physical relation are authenticated."),
        entry("ROOT-11", "substitution families", "exploratory-inconclusive-individual", "Can shared frames establish a new semantic sign family?",
              "Aggregate weighting sensitivity; individual primary highlighted-pair support insufficient and important prior exists.",
              "Multiple testing, allographic compatibility and duplicated frames inflate discovery claims.",
              "Adjusted max and full-procedure transfer references; primary literature/graphic checks.",
              ["research/literature/candidate_pair_novelty_audit.md", "src/methods/substitution_validation.py"], "New independently verified graphic cases and a frozen family-specific prediction are available."),
        entry("ROOT-12", "nonphonetic control", "synthetic-counterexample", "Is sequential prediction diagnostic of language?",
              "Constructed office-routing data retains predictive gain; order alone is not diagnostic.",
              "An independent-slot finite template does not exhaust nonlinguistic generative alternatives.",
              "Ran a nonphonetic sequential workflow through the same assay.",
              ["src/methods/generate_workflow_control.py", "research/methods/FINDINGS.md"], "A broader known-system comparison with matched controls tests discrimination."),
        entry("ROOT-13", "numerical identifiability", "exact-conditional-audit", "Do published equalities uniquely identify numeral values?",
              "Four positive-integer solutions; 10/8/6 requires an additional range restriction.",
              "Unverified equality semantics, unsupported range and an invalid parity argument.",
              "Eliminated variables exactly, enumerated all divisors and reviewed cited archaeological sources.",
              ["src/methods/audit_numerical_equalities.py", "research/methods/NUMERICAL_CONSTRAINT_AUDIT.md"], "Independent count bounds, object identity and arithmetic premises are verified."),
        entry("ROOT-14", "metrology", "synthetic-identifiability-audit", "Can vessel capacities alone fix a stroke value/base?",
              "Rescaled unit/count interpretations fit the same capacities.",
              "Unit and count scale are confounded.",
              "Constructed explicit 10/12 alternative parameterizations with equal predictions.",
              ["src/identifiability_demo.py", "results/identifiability", "research/literature/metrology/README.md"], "An independent unit or count is physically grounded."),
        entry("ROOT-15", "chart transcription", "completed-uncertainty-preserving-resource", "Can the original sign chart be indexed transparently?",
              "687 source-linked cells with retained numeric ambiguities; no expert accuracy claim.",
              "Printed small digits, duplicates and inventory differences.",
              "Independent reference comparison, source crops and ambiguity-preserving atlas.",
              ["src/chart_reference.py", "src/chart_atlas.py", "output/chart_atlas/index.html", "research/chart_reference"], "Expert adjudication or a new source image corrects explicit uncertain fields."),
        entry("ROOT-16", "image recognition pilot", "exploratory-development", "Can original printed graphics be recognized from the chart?",
              "Small printed-row development pilot; not a full inscription corpus decoder.",
              "Segmentation, editorial signs, touching forms and clipped rows.",
              "Source crop review and explicit compatible-candidate scoring.",
              ["src/font_pilot.py", "research/visual_digitization/FRESH_FONT_PILOT_PLAN.md"], "New blind examples and source-only crop rules are frozen."),
        entry("ROOT-17", "fresh20 image test", "frozen-evaluation-failed-whole-row-recovery", "Does the frozen acquisition pipeline recover unseen-reference printed rows?",
              "14 matching row counts; two compatible first-candidate whole rows of 20.",
              "Acquisition/segmentation defects and chart mapping ambiguity.",
              "Preserved frozen predictions, independent numeric reference and explicit coverage.",
              ["research/visual_digitization/font_fresh20/evaluation_frozen_endpoint.json", "src/evaluate_font_fresh20.py"], "A repaired pipeline is frozen on genuinely new reference-withheld rows."),
        entry("ROOT-18", "image geometry repair", "post-reference-development", "Can source-only geometric repair reduce acquisition errors?",
              "Improved development row recovery; not a fresh blind accuracy result.",
              "Neighbor rows and top cuts contaminated drawn-unit acquisition.",
              "Used source-only revised vertical crops with the same frozen chart/matcher.",
              ["src/methods/font_geometry_sensitivity.py", "research/methods/results/font_geometry_sensitivity"], "Fresh withheld-source references can validate the revised crop protocol."),
        entry("ROOT-19", "source identity", "completed-with-unresolved-joins", "Which historical source joins are physically defensible?",
              "Several primary joins and scan duplicate checks resolved; other historical IDs/bangle context remain conditional.",
              "Misleading retrieval titles, reused inventory numbers, unavailable author figure and duplicated scan pages.",
              "Original plate/text review, dimensions, opposing strings and image hashing.",
              ["research/literature/audit_source_identities.py", "research/literature/cisi1_counting_and_errata.md", "research/corpus/FINAL_SOURCE_NOTES.md"], "The missing primary witness or authentic historical crosswalk is obtained."),
        entry("ROOT-20", "report and integrity", "completed-historical-verification", "Can the investigation be delivered with auditable evidence?",
              "18-page report; 1,568 selected evidence hashes verified; 23 root and eight methods historical checks.",
              "Quantitative/source scope and visual layout required independent review.",
              "Exact result audit, source corrections, render-and-inspect QA and manifest verification.",
              ["output/verification.json", "output/evidence_manifest.json", "output/report_visual_qa.json", "output/pdf/indus_script_research_report.pdf"], "A changed artifact or new manuscript requires the relevant new checks."),
        entry("CRYPTO-01", "cryptography framing", "verified-synthetic-demonstration", "Can an internally fitted structural score select semantic labels?",
              "All 720 six-symbol relabellings score identically; two fixed identities leave 24 maps.",
              "Permutation-equivariant structural statistics have no semantic anchor.",
              "Exact enumeration demonstrates the scope and external-anchor requirement.",
              ["experiments/2026-10-02-cryptography-framing/protocol.md", "experiments/2026-10-02-cryptography-framing/results.json", "src/exploratory/permutation_identifiability.py"], "A grounded known-system benchmark tests recovery under explicit anchors.")
    ]
    index = json.loads((ROOT / "research/methods/RESULT_INDEX.json").read_text(encoding="utf-8"))
    for name, outputs in sorted(index["results"].items()):
        evidence = [v["path"].replace("\\", "/") for v in outputs.values() if isinstance(v,dict) and "path" in v]
        designs = sorted({str(v.get("design") or "See exact source result") for v in outputs.values() if isinstance(v,dict)})
        parameters = [v["parameters"] for v in outputs.values() if isinstance(v,dict) and "parameters" in v]
        row = entry("METHODS-" + name, "original-methods-run", "completed-analysis-see-source-design",
                    "; ".join(designs), "Endpoint preserved; use methods FINDINGS and exact result, not the most favorable variant.",
                    "Population, selection and null-reference changes make endpoints noninterchangeable.",
                    "Run-specific parameters, design, seeds and hashes remain in the original result index.",
                    evidence or ["research/methods/results/" + name],
                    "A named new input or changed protocol justifies a new run; preserve this endpoint.")
        row["parameters"] = parameters
        row["source_index"] = "research/methods/RESULT_INDEX.json"
        items.append(row)
    target = ROOT / "knowledge/experiments/registry.json"
    # Keep future manual additions; rebuilding this initial index must not erase them.
    if target.exists():
        old = json.loads(target.read_text(encoding="utf-8"))
        generated = {row["id"] for row in items}
        items.extend(row for row in old.get("experiments", []) if row["id"] not in generated)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"schema_version": 1, "scope": "documented external work, not exhaustive unrecorded thoughts", "experiments": items}, indent=2) + "\n", encoding="utf-8")
    lines = ["# Experiment directory", "", "Generated from `registry.json`; the registry contains challenges, remedies and retry conditions.", "", "| ID | Status | Question |", "|---|---|---|"]
    lines += [f"| {r['id']} | {r['status']} | {r['question'].replace('|','/')} |" for r in items]
    (target.parent / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"experiments": len(items), "methods_runs": len(index["results"])}))

if __name__ == "__main__":
    main()
