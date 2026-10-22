"""Check whether unresolved IAR heading locators are in front matter."""
import argparse
import json
import pathlib
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=pathlib.Path, required=True)
    parser.add_argument("--records", type=pathlib.Path, required=True)
    args = parser.parse_args()
    path = args.records / "sweep-summary-1a.json"
    sweep = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for row in sweep.get("unresolved_iar_heading_pages", []):
        page = args.raw / "text" / row["source_id"] / f"p{row['pdf_page']:04}.txt"
        lines = page.read_text(encoding="utf-8").splitlines()
        upper = "\n".join(lines[:18])
        front = bool(re.search(r'(?im)^\s*P\s*R\s*E\s*F\s*A\s*C\s*E\s*$', upper))
        results.append(dict(**row, front_matter_heading_detected=front,
            locator_status="no-excavation-heading-in-front-matter" if front else "unresolved",
            reason="Front-matter hit; no site/district entry heading applies." if front else "No site/district entry heading detected."))
    (args.records / "iar-heading-exceptions-1a.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(dict(pages=len(results), front_matter=sum(r["front_matter_heading_detected"] for r in results), unresolved=sum(not r["front_matter_heading_detected"] for r in results))))


if __name__ == "__main__":
    main()
