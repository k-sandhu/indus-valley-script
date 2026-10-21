"""Expand local manual records into the fields of TRANSCRIPTION-BRIEF.md.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/records.py --input <local manual JSONL> --output <owned transcription JSONL> --source <source id> --scan <scan id>
Input values use the final field names. Legend text is supplied only in local data files.
"""
import argparse
import json
import unicodedata
from pathlib import Path

FIELDS = ("source entry sub_entry page_printed page_pdf plates object_text material dimensions object_kind device legend_as_printed legend_lines_as_printed line_division_evidence translation_as_printed doubtful restored illegible_part date_as_printed language_note findspot_as_printed depth_as_printed impressions duplicates cross_references museum uncertain_fields transcriber").split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--scan", required=True)
    args = ap.parse_args()
    records = []
    for line in args.input.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = {k: None for k in FIELDS}
        rec.update(source=args.source, scan=args.scan, sub_entry=None, material="clay",
                   object_kind="seal-die" if args.source.endswith("1903-04") else "clay-sealing",
                   doubtful=False, restored=False, illegible_part=False,
                   plates=[], duplicates=[], cross_references=[], uncertain_fields=[],
                   line_division_evidence="none given", transcriber="Codex (GPT-6), Codex Windows workspace harness; page-image")
        supplied = json.loads(line)
        aliases = {"e": "entry", "s": "sub_entry", "p": "page_printed", "P": "page_pdf",
                   "o": "object_text", "d": "dimensions", "v": "device", "l": "legend_as_printed",
                   "t": "translation_as_printed", "f": "findspot_as_printed", "z": "depth_as_printed",
                   "i": "impressions", "D": "duplicates", "x": "cross_references", "q": "doubtful",
                   "r": "restored", "b": "illegible_part", "a": "date_as_printed", "n": "remarks_as_printed",
                   "ld": "line_division_evidence", "lang": "language_note"}
        supplied = {aliases.get(k, k): v for k, v in supplied.items()}
        if "pl" in supplied:
            supplied["plates"] = [{"plate": p, "figure": f} for p, f in supplied.pop("pl")]
        rec.update(supplied)
        if rec.get("device") and len(rec["device"].split()) > 15:
            rec["device_full_local"] = rec["device"]
            rec["device"] = " ".join(rec["device"].split()[:15])
        if isinstance(rec["legend_as_printed"], list):
            rec["legend_lines_as_printed"] = rec["legend_as_printed"]
            rec["legend_as_printed"] = "\n".join(rec["legend_as_printed"])
            if rec["line_division_evidence"] == "none given":
                rec["line_division_evidence"] = "edition numbers or separately prints the legend lines"
        if rec["legend_as_printed"]:
            for field in ("legend_as_printed", "legend_lines_as_printed", "legend_nagari_as_printed"):
                if isinstance(rec.get(field), str):
                    rec[field] = unicodedata.normalize("NFC", rec[field])
            rec["restored"] = rec["restored"] or "[" in rec["legend_as_printed"]
        records.append(rec)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    print(json.dumps({"source": args.source, "rows": len(records), "entries": len({r["entry"] for r in records})}))


if __name__ == "__main__":
    main()
