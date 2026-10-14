"""Flag selected stock writing patterns for manual editing, not authorship detection."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "stock_word": r"\b(?:delve|delves|delving|leverage|leveraging|foster|fostering|seamless|tapestry|game[- ]changer|groundbreaking)\b",
    "stock_opening": r"\b(?:it['’]s worth noting|here['’]s the thing|in today['’]s|at the end of the day|in conclusion|in summary|bottom line|key takeaway)\b",
    "rhetorical_contrast": r"\b(?:not just|isn['’]t just|it['’]s not about|this isn['’]t about)\b",
    "self_applause": r"\b(?:and that matters|that['’]s the part everyone misses|cannot be overstated|paradigm shift)\b",
    "em_dash": "—",
    "third_person_voice": r"\b(?:the user|user['’]s|owner['’]s (?:priority|decision|request|approval)|owner decision|the coordinator)\b",
    "template_paragraph": r"\b(?:the present contribution|our contribution is|are established (?:methods|research approaches|precedents))\b",
    "generic_link_label": r"\[(?:primary|original|published|exact|source|article|paper|preprint|author manuscript|abstract)\b[^\]]{0,40}\]\(https?://",
    "inflating_ing_clause": r",\s(?:highlighting|underscoring|showcasing|emphasi[sz]ing|reflecting the)\b",
    "copula_avoidance": r"\b(?:serves as|stands as)\b",
    "formal_word": r"\b(?:utili[sz](?:e|es|ed|ing|ation)|subsequently|commenc\w+)\b",
}
# Applied after links, inline code and URLs are removed from the line.
PLAIN_PATTERNS = {
    "slash_compound": r"\b[A-Za-z]{3,}/[A-Za-z]{3,}\b",
}


def plain(line):
    line = re.sub(r"\]\([^)]*\)", "]", line)
    line = re.sub(r"`[^`]*`", "", line)
    return re.sub(r"https?://\S+", "", line)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", help="File or directory to scan; repeat for several owned paths")
    parser.add_argument("--output", default="knowledge/editorial/prose-review.json")
    parser.add_argument("--no-write", action="store_true", help="Print findings without changing a shared report")
    args = parser.parse_args()
    if args.path:
        files = []
        for value in args.path:
            target = ROOT/value
            files.extend(target.rglob("*.md") if target.is_dir() else [target])
    else:
        files = [ROOT/x for x in ("README.md", "REPRODUCING.md", "CONTRIBUTING.md", "REUSE.md")]
        files += list((ROOT/"papers").rglob("*.md")) + list((ROOT/"knowledge").rglob("*.md")) + list((ROOT/"experiments").rglob("*.md"))
    files = sorted(set(path for path in files if path.is_file() and "editorial" not in path.parts))
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
            for name, pattern in PLAIN_PATTERNS.items():
                if re.search(pattern,plain(line)):
                    flags.append({"file": path.relative_to(ROOT).as_posix(), "line": number, "pattern": name, "text": line})
    result = {"scope": "new repository prose; flags require human judgment and may be source titles/technical quotations", "files_scanned": len(files), "flags": flags}
    if not args.no_write:
        output = ROOT/args.output
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2) + "\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
