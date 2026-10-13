"""Restore targets affected by a draft number-spacing edit; retain readable prose."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKAGE = HERE.parent
OUT = ROOT / "data/raw/2026-10-11-societal-persistence/coordinator/editorial-v1"

def restore(text):
    return re.sub(r"(?<=\d) (?=[A-Z])", "", re.sub(r"(?<=[A-Za-z]) (?=\d)", "", text))

def main():
    if OUT.exists():
        raise SystemExit("Editorial snapshot exists; do not overwrite.")
    OUT.mkdir(parents=True)
    files = sorted(PACKAGE.glob("*.md")) + [ROOT / "knowledge/retrospectives/2026-10-11-societal-persistence.md"]
    records = []
    for path in files:
        before = path.read_bytes()
        snapshot = OUT / path.name
        snapshot.write_bytes(before)
        lines = []
        fenced = False
        for line in before.decode("utf-8").splitlines(keepends=True):
            if line.startswith("```"):
                fenced = not fenced
            if fenced:
                line = restore(line)
            else:
                line = re.sub(r"(\]\()([^\n)]+)(\))", lambda m: m[1] + restore(m[2]) + m[3], line)
                line = re.sub(r"`[^`]+`", lambda m: restore(m[0]), line)
                line = line.replace("Period 3 C", "Period 3C").replace("StageVI", "Stage VI")
            lines.append(line)
        after = "".join(lines).encode("utf-8")
        if after != before:
            path.write_bytes(after)
        records.append({"path":path.relative_to(ROOT).as_posix(), "snapshot":snapshot.relative_to(ROOT).as_posix(),
                        "before_sha256":hashlib.sha256(before).hexdigest(), "after_sha256":hashlib.sha256(after).hexdigest()})
    with (HERE / "editorial-fix-v1.json").open("x",encoding="utf-8") as stream:
        json.dump({"scope":"Draft edit only; unintended spacing in link targets and code restored before final checks", "files":records},stream,indent=2); stream.write("\n")
    print(json.dumps({"files":len(records),"changed":sum(r["before_sha256"] != r["after_sha256"] for r in records)}))

if __name__ == "__main__":
    main()
