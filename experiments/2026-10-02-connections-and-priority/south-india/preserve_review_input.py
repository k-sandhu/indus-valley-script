"""Recover the reviewed prose version from its two documented wording edits.

The reconstruction must match the auditor's stored hash before it is saved.
Analysis endpoints and the independent review remain unchanged.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
current = (HERE / "REPORT.md").read_bytes()
old_paragraph = "The [compound membership endpoint](stroke-membership-v2/results.json) contains 209 queried compound keys. Explicit plain-stroke components occur in 194 of them; 15 have opaque component representations for this question. Among the 194, 142 have one contiguous stroke block and exactly one other component. Those forms account for 413 of the 491 reported occurrences in the resolved group. Thirteen forms contain separated stroke blocks, and 40 contain more than one other component. Their arrangement gives concrete cases for comparing a simple count-plus-category form with more complex structures."
new_paragraph = "The [compound membership endpoint](stroke-membership-v2/results.json) contains 209 queried compound keys. Explicit plain-stroke components occur in 194 of them; 15 have opaque component representations for this question. A stroke block is a run of consecutive stroke components in the normalized array. Form 39.13C illustrates this definition: two separately drawn three-stroke groups occupy one array run. Among the 194, 142 have one stroke block and exactly one other component. Those forms account for 413 of the 491 reported occurrences in the resolved group. Thirteen forms contain separated stroke blocks, and 40 contain more than one other component. Their arrangement gives concrete cases for comparing a simple count-plus-category form with more complex structures."
audit_link = "The [source audit](independent-review.md) independently checks the aggregate calculations, compound properties and printed comparisons. "
assert current.count(new_paragraph.encode()) == 1
assert current.count(audit_link.encode()) == 1
reviewed = current.replace(new_paragraph.encode(), old_paragraph.encode()).replace(audit_link.encode(), b"")
audit = json.loads((HERE / "independent-review.json").read_text(encoding="utf-8"))
expected = audit["reviewed_file_sha256"]["REPORT.md"]
assert hashlib.sha256(reviewed).hexdigest() == expected
dest = HERE / "REPORT-reviewed-v1.md"
if dest.exists():
    assert dest.read_bytes() == reviewed
else:
    dest.write_bytes(reviewed)
record = {"status": "pass", "review_input_snapshot": dest.name,
          "review_input_sha256": expected,
          "matches_independent_review_hash": True,
          "current_report_sha256": hashlib.sha256(current).hexdigest(),
          "changes_after_review": ["Define stroke block as adjacency in the normalized component array, with 39.13C as example", "Link the completed independent source audit"],
          "method": "Reverse only the two documented prose edits and require exact agreement with the audit's recorded SHA-256",
          "scope": "Prose revision provenance; calculations, source observations and independent audit unchanged"}
(HERE / "review-followup-v1.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record))
