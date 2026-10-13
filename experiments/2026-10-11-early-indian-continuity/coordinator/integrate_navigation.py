"""Append this package to current navigation; preserve pre-edit bytes and prior entries."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/coordinator/before-integration-v1"
NAV = ("README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json", "knowledge/retrospectives/README.md")

def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> None:
    if RAW.exists() or (HERE / "navigation-integration-v1.json").exists():
        raise SystemExit("Integration already has a preservation record; inspect it instead of repeating.")
    old = {p: (ROOT / p).read_bytes() for p in NAV}
    additions = json.loads((HERE / "registry-additions.json").read_text(encoding="utf-8"))
    registry = json.loads(old[NAV[2]])
    previous = registry["experiments"]
    assert len({r["id"] for r in previous}) == len(previous)
    assert not ({r["id"] for r in previous} & {r["id"] for r in additions})
    assert len({r["id"] for r in additions}) == len(additions)
    for record in additions:
        for path in record["evidence"]:
            assert (ROOT / path).is_file(), path

    updated = {}
    readme = old[NAV[0]]
    newline = b"\r\n" if b"\r\n" in readme else b"\n"
    anchor = b"|---|---|" + newline
    assert readme.count(anchor) == 1
    row = b"| Early Indian institutions and deep cultural memory beyond decipherment | [Two developed mechanisms](experiments/2026-10-11-early-indian-continuity/REPORT.md), [manuscript](experiments/2026-10-11-early-indian-continuity/MANUSCRIPT.md), [review](experiments/2026-10-11-early-indian-continuity/review/REVIEW.md) |" + newline
    updated[NAV[0]] = readme.replace(anchor, anchor + row, 1)

    index_text = "\n## Early Indian institutions and cultural memory\n\nThe [October 11 continuity study](../experiments/2026-10-11-early-indian-continuity/REPORT.md) develops two problems beyond decipherment: survival of practical and institutional knowledge through settlement change, and preservation or reconstruction of origins in early Indian texts. Its [manuscript](../experiments/2026-10-11-early-indian-continuity/MANUSCRIPT.md) proposes selective inheritance combined with intellectual recombination. Farming and craft comparisons, ritual responsibilities, Buddhist institutional reasoning, Manu, river passages and DN27 supply source-qualified cases; no diagnostic Harappan-to-textual join was established.\n\nThe [institutional package](../experiments/2026-10-11-early-indian-continuity/institutions/README.md) retains its first filter defect and corrected endpoint. The [memory package](../experiments/2026-10-11-early-indian-continuity/memory/README.md) preserves a typed dating audit and explicitly synthetic history construction. A separate [textual control and retention model](../experiments/2026-10-11-early-indian-continuity/coordinator/CONTROL-AND-MODEL.md), [adversarial review](../experiments/2026-10-11-early-indian-continuity/review/REVIEW.md), [response](../experiments/2026-10-11-early-indian-continuity/REVIEW-RESPONSE.md) and [retrospective](retrospectives/2026-10-11-early-indian-continuity.md) record source scope and repairs. Prospective tests require unusual linked operations, independent branches, dated intermediates and matched alternatives; numerical checks do not authenticate a lineage.\n"
    index_newline = b"\r\n" if b"\r\n" in old[NAV[1]] else b"\n"
    updated[NAV[1]] = old[NAV[1]] + index_text.encode("utf-8").replace(b"\n", index_newline)

    registry_bytes = old[NAV[2]]
    registry_newline = b"\r\n" if b"\r\n" in registry_bytes else b"\n"
    tail = b"  ]" + registry_newline + b"}" + registry_newline
    assert registry_bytes.endswith(tail), "Unexpected registry formatting; do not rewrite prior bytes."
    body = registry_bytes[:-len(tail)]
    assert body.endswith(registry_newline)
    # Serialize new entries only; preserve every earlier byte and JSON object.
    entry_text = ",\n".join("\n".join("    " + line for line in json.dumps(record, ensure_ascii=False, indent=2).splitlines()) for record in additions)
    updated[NAV[2]] = body[:-len(registry_newline)] + b"," + registry_newline + entry_text.encode("utf-8").replace(b"\n", registry_newline) + registry_newline + tail
    parsed = json.loads(updated[NAV[2]])
    assert parsed["experiments"] == previous + additions

    retrospective_text = "\nThe [early Indian institutions and cultural-memory study](2026-10-11-early-indian-continuity.md) records selective practical transmission, changing origin explanations, a post-audit reset hypothesis, preserved filtering corrections, source-access repairs and independent chronology and arithmetic review. Its next tests compare unusual linked operations and independently dated carriers.\n"
    retrospective_newline = b"\r\n" if b"\r\n" in old[NAV[3]] else b"\n"
    updated[NAV[3]] = old[NAV[3]] + retrospective_text.encode("utf-8").replace(b"\n", retrospective_newline)

    # Detect concurrent changes before any write; snapshots cover the actual pre-edit bytes.
    assert all((ROOT / p).read_bytes() == old[p] for p in NAV), "Navigation changed during preparation."
    RAW.mkdir(parents=True)
    for path, content in old.items():
        snapshot = RAW / path
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(content)
    for path in NAV:
        assert (ROOT / path).read_bytes() == old[path], f"Concurrent change: {path}"
        (ROOT / path).write_bytes(updated[path])
    record = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Append-only navigation integration over current shared-workspace bytes; no prior registry entry changed.",
        "registry_before_count": len(previous), "registry_after_count": len(previous) + len(additions),
        "new_ids": [r["id"] for r in additions],
        "files": [{"path": p, "before_sha256": digest(old[p]), "after_sha256": digest(updated[p]),
                   "snapshot": (RAW / p).relative_to(ROOT).as_posix()} for p in NAV]
    }
    (HERE / "navigation-integration-v1.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"registry_before": len(previous), "registry_after": len(previous) + len(additions), "navigation_files": len(NAV)}))

if __name__ == "__main__":
    main()
