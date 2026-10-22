"""Third pass: combine markings A and B into the resolved donor list (PROTOCOL.md, Part 1).

Every decision below was taken after both markings were complete and is listed with its reason.
Agreeing rows keep the shared mark. Rows marked "not a personal name" by marker B leave the
denominator. Duplicate rows, one inscription read once by each scan without alignment, keep
the scan-A row.
"""
import argparse
import csv
from pathlib import Path

# Marker disagreements, resolved under MARKING-RULE.md.
DISAGREEMENTS = {
    "D0280": ("pushya", "strict", "Tisa = Tiṣya; scan A's Sanskrit is garbled ('Tiohya'), which defeated marker A"),
    "D0359": ("svati", "ambiguous", "Lüders gives Śaktigupta or Svātigupta; two equivalents are treated as ambiguous, as in D0118 and D0266"),
    "D0432": ("", "", "Lüders gives Aśvadeva; the Sanskrit equivalent decides, so Asa- is Aśva-"),
    "D0442": ("", "", "same name and equivalent as D0432"),
    "D0451": ("bharani", "ambiguous", "Bharaṇa- is not a listed form of Bharaṇī and bharaṇa 'support' is a common word"),
}

# Scan-B-only row -> scan-A-only row recording the same clause (name and following text agree).
DUPLICATES = {
    "D0812": "D0589", "D0793": "D0520", "D0782": "D0310", "D0796": "D0527", "D0799": "D0534",
    "D0774": "D0108", "D0800": "D0535", "D0788": "D0418", "D0798": "D0533", "D0804": "D0551",
    "D0776": "D0146", "D0775": "D0126", "D0797": "D0531", "D0805": "D0553", "D0790": "D0466",
    "D0807": "D0556", "D0781": "D0280", "D0789": "D0459", "D0810": "D0570", "D0809": "D0569",
    "D0787": "D0417", "D0778": "D0169", "D0806": "D0554", "D0785": "D0400", "D0808": "D0560",
    "D0783": "D0350",
}

# Donors the extractor missed and a marker found in a clause.
ADDED = [
    {"row_id": "D0378-co", "asterism": "pushya", "strength": "strict",
     "note": "co-donor Pusi (Puṣyā) in the clause of D0378, noted by marker B; the extractor took only the first donor"},
]


def read(path):
    with Path(path).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--marking-a", required=True)
    ap.add_argument("--marking-b", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = read(args.rows)
    ma = {r["row_id"]: r for r in read(args.marking_a)}
    mb = {r["row_id"]: r for r in read(args.marking_b)}
    out = []
    for r in rows:
        i = r["row_id"]
        a, b = ma[i], mb[i]
        personal = "no" if b["note"].lower().startswith("not a personal name") else "yes"
        if (a["asterism"], a["strength"]) == (b["asterism"], b["strength"]):
            ast, strength, source, note = a["asterism"], a["strength"], "agree", ""
        else:
            ast, strength, note = DISAGREEMENTS[i]
            source = "resolved"
        dup = DUPLICATES.get(i, "")
        out.append({"row_id": i, "asterism": ast, "strength": strength, "personal_name": personal if not dup else "duplicate",
                    "duplicate_of": dup, "source": source, "note": note or b["note"]})
    for add in ADDED:
        out.append(dict(add, personal_name="yes", duplicate_of="", source="added"))
    with Path(args.out).open("x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["row_id", "asterism", "strength", "personal_name", "duplicate_of", "source", "note"])
        w.writeheader()
        w.writerows(out)
    kept = [o for o in out if o["personal_name"] == "yes"]
    print(len(out), "rows;", len(kept), "personal donor occurrences;",
          sum(bool(o["asterism"]) for o in kept), "asterism-marked;",
          sum(o["strength"] == "strict" for o in kept), "strict")


if __name__ == "__main__":
    main()
