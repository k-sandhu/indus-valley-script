"""Flag selected stock writing patterns for manual editing, not authorship detection."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "stock_word": r"\b(?:delve|delves|delving|leverage|leveraging|foster|fostering|seamless|tapestry|game[- ]changer|groundbreaking)\b",
    "stock_opening": r"\b(?:it['’]s worth noting|here['’]s the thing|in today['’]s|at the end of the day|in conclusion|in summary|bottom line|key takeaway)\b",
    "rhetorical_contrast": r"\b(?:not just|isn['’]t just|it['’]s not about|this isn['’]t about)\b",
    "self_applause": r"\b(?:and that matters|that['’]s the part everyone misses|cannot be overstated|paradigm shift)\b",
    "em_dash": "—",
}

def main():
    files = [ROOT/x for x in ("README.md", "REPRODUCING.md", "CONTRIBUTING.md", "REUSE.md")]
    files += list((ROOT/"papers").rglob("*.md")) + list((ROOT/"knowledge").rglob("*.md"))
    flags = []
    for path in files:
        if not path.exists() or "editorial" in path.parts:
            continue
        fenced = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            if line.startswith("```"):
                fenced = not fenced
            if fenced:
                continue
            for name, pattern in PATTERNS.items():
                if re.search(pattern,line,re.I):
                    flags.append({"file": path.relative_to(ROOT).as_posix(), "line": number, "pattern": name, "text": line})
    result = {"scope": "new repository prose; flags require human judgment and may be source titles/technical quotations", "files_scanned": len(files), "flags": flags}
    output = ROOT/"knowledge/editorial/prose-review.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2) + "\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
