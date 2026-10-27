"""Create the nine editorial cards through kb.py; preserve package authors."""
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
specs = json.loads((PACKAGE / "card_specs.json").read_text(encoding="utf-8"))
created = []
for spec in specs:
    existing = [p for p in (ROOT / "knowledge/findings").glob("F-*.md")
                if 'title: ' + json.dumps(spec["title"], ensure_ascii=False) in p.read_text(encoding="utf-8-sig")]
    if existing:
        raise SystemExit("Card already exists: " + str(existing[0]))
    result = subprocess.run([sys.executable, "-B", "-X", "utf8", "tools/kb.py", "new", "finding",
                             "--title", spec["title"], "--area", spec["area"]], cwd=ROOT,
                            text=True, encoding="utf-8", capture_output=True, check=True)
    relative = result.stdout.strip()
    path = ROOT / relative
    identifier = path.name[:6]
    original = json.loads((ROOT / "knowledge/registry/attempts" / (spec["registry_ids"][0] + ".json")).read_text(encoding="utf-8-sig"))
    fields = {"id": identifier, **{k: spec[k] for k in ["title", "status_class", "area", "date", "registry_ids", "evidence", "population"]}, "authors": original["authors"]}
    front = "---\n" + "\n".join(k + ": " + json.dumps(v, ensure_ascii=False) for k, v in fields.items()) + "\n---\n"
    evidence = []
    for pointer in spec["evidence"]:
        file, _, fragment = pointer.partition("#")
        evidence.append("- [" + file + "](../../" + pointer + ")" + (", JSON Pointer `" + fragment + "`." if fragment.startswith("/") else "."))
    text = front + "\n# Finding\n\n" + spec["finding"] + "\n\n# Evidence\n\n" + "\n".join(evidence) + "\n\n# Scope\n\n" + spec["scope"] + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    created.append(relative)
    print(relative)
(PACKAGE / "new-cards.json").write_text(json.dumps(created, indent=2) + "\n", encoding="utf-8")
