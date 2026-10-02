"""Pin source records and independently verify this descriptive audit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import itertools
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


extras = """README.md
knowledge/INDEX.md
knowledge/experiments/registry.json
knowledge/editorial/WRITING.md
knowledge/provenance/REDISTRIBUTION.md
knowledge/directions/archaeology-and-iconography.md
knowledge/directions/community-proposals.md
knowledge/retrospectives/literature.md
knowledge/retrospectives/methods.md
results/context/seal_tablet.json
results/context/bull1_other.json
results/microcontext/unique1_collapse1.json
results/paired/summary.json
results/paired/numeric_object_audit.json
research/corpus/FINAL_SOURCE_NOTES.md
research/literature/paired_surface_recommendations.md
research/literature/candidate_pair_novelty_audit.md
research/methods/results/numerical_equalities/numerical_equalities_audit.json
research/methods/results/numerical_equalities/numerical_count_delta_sensitivity.json
experiments/2026-10-02-six-hour/lothal-physical-use/source-provenance.json
experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json
experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/selected-trace-observations.json
experiments/2026-10-02-six-hour/harappa-object-frame/display-summary/results.json
experiments/2026-10-02-six-hour/harappa-object-frame/figure4-native-reinspection.json
experiments/2026-10-02-six-hour/harappa-object-frame/source-access-log.json
experiments/2026-10-02-six-hour/physical-information/ARCHAEOLOGICAL_TARGET.md
experiments/2026-10-02-six-hour/physical-acquisition/README.md
experiments/2026-10-02-six-hour/khipu-control/REPORT.md
experiments/2026-10-02-six-hour/khipu-control/robust-decoder/REPORT.md
experiments/2026-10-02-six-hour/khipu-control/conservation-check/REPORT.md
experiments/2026-10-02-six-hour/kanmer-physical-use/RETROSPECTIVE.md
experiments/2026-10-02-six-hour/kanmer-physical-use/source-continuation-2026-10-02/RETROSPECTIVE.md
experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/RETROSPECTIVE.md
experiments/2026-10-02-six-hour/stamp-geometry/RETROSPECTIVE.md""".splitlines()
paths = {ROOT / x for x in extras}
links = []
for p in OUT.glob("*.md"):
    for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
        if target.startswith(("https:", "http:")):
            continue
        q = (p.parent / target.split("#")[0]).resolve()
        links.append({"document": p.name, "target": target, "exists": q.exists()})
        if q.exists() and not q.is_relative_to(OUT):
            paths.add(q)
missing = [x for x in links if not x["exists"] and x["target"] not in ["source-pins.json", "freeze-manifest.json"]]
assert not missing, missing
pins = []
for p in sorted(paths):
    assert p.exists(), str(p)
    pins.append({"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)})
save("source-pins.json", {"created_utc": datetime.now(timezone.utc).isoformat(),
     "scope": "Project records reviewed for this audit. Linked raw source witnesses retain their existing local-only rights handling.", "files": pins})

groups = read(ROOT / "experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json")["groups"]
checks = read(OUT / "current-checks.json")
enumerated = {}
for view, excluded in [("diagnostic_categories", {"undiagnostic"}), ("all_recorded_categories", set())]:
    counts = [{k: v for k, v in g["physical_types"].items() if k not in excluded} for g in groups]
    scores = [sum(c[k] for c, k in zip(counts, assignment))
              for assignment in itertools.product(*[list(c) for c in counts])]
    maximum = max(scores)
    assert maximum == checks["lothal_single_category_per_complete_string"][view]["maximum_compatible_objects"]
    enumerated[view] = {"assignments_checked": len(scores), "best_compatible_objects": maximum,
                        "maximizing_assignments": scores.count(maximum)}
for x in checks["published_equality_solution_substitutions"]:
    L, S, v = x["L"], x["S"], x["v"]
    assert v + L == 2*S
    assert v*L + 1 == 7*S + 5
    assert x["bangle_expression_7_plus_L"] == 7 + L
for x in checks["susa_equal_mixture_witnesses"]:
    a, b, c, d = x["internal_and_external_class_values"]
    assert a+b == c+d
assert checks["metrology_eligibility"]["source_rows"] == len(checks["metrology_eligibility"]["rows"]) == 8
assert all(not x["eligible"] and not x["liquid_fill_measured"] for x in checks["metrology_eligibility"]["rows"])
assert checks["code_sha256"] == sha(OUT / "audit.py")
assert checks["protocol_sha256"] == sha(OUT / "PROTOCOL.md")
encoding_bad = {}
for p in OUT.glob("*.md"):
    txt = p.read_text(encoding="utf-8")
    terms = [t for t in ["\ufffd", "\u00e2\u20ac", "\u00c3\u00a9", "\u00c2\u00a0"] if t in txt]
    if terms:
        encoding_bad[p.name] = terms
assert not encoding_bad, encoding_bad
save("verification.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "status": "passed",
     "independent_category_enumeration": enumerated, "equality_candidates_checked": 4,
     "susa_witnesses_checked": 2, "ineligible_capacity_rows_checked": 8,
     "source_files_pinned": len(pins), "links_checked": len(links), "broken_links": missing,
     "code_and_protocol_hashes_match": True, "utf8_encoding_scan": encoding_bad,
     "scope": "Independent algebra/enumeration and link/encoding checks. Archaeological observations remain inherited source-reviewed records."})
print(json.dumps({"pins": len(pins), "links": len(links), "independent_enumeration": enumerated}, indent=2))
