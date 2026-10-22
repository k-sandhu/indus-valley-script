"""Keep aligned clauses with a named donor in either scan and number them D0001 onward."""
import argparse
import csv

FIELDS = ["row_id", "entry", "entry_b", "name", "sanskrit", "name_b", "sanskrit_b", "status", "status_b",
          "site_heading", "context", "context_b"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aligned", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.aligned, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["status"] == "named" or r["status_b"] == "named"]
    for i, r in enumerate(rows, 1):
        r["row_id"] = f"D{i:04d}"
    with open(args.out, "x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(len(rows))


if __name__ == "__main__":
    main()
