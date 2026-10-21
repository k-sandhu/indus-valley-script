"""Post-outcome support and source audit; no relaxed significance test."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import variation as V


def main():
    out = HERE / "audit-v1"
    local = V.LOCAL / "audit-v1"
    out.mkdir(exist_ok=False)
    local.mkdir(parents=True, exist_ok=False)
    source = {r["family"]: r for r in V.rows(V.LOCAL / "source-v1/objects.jsonl")}
    collision_map = json.loads((V.LOCAL / "source-v1/accession-collisions.json").read_text(encoding="utf-8"))
    raw_cisi = {}
    for label in ("cisi1", "cisi2"):
        for row in V.rows(V.INPUTS[label]):
            raw_cisi[(row["cisi"], row["volume"])] = row
    collision_audit = []
    for key, families in collision_map.items():
        evidence = []
        for fam in families:
            for src in source[fam]["cisi_sources"]:
                rr = raw_cisi[(src["cisi"], src["volume"])]
                evidence.append({"family": fam, "cisi": src["cisi"], "volume": src["volume"],
                                 "printed_page": src["printed_page"], "pdf_page": src["pdf_page"],
                                 "raw_museum_cell": rr["col4_museum"], "parsed_holdings": rr["parsed"].get("museum_holdings"),
                                 "uncertain_columns": rr.get("uncertain_columns", [])})
        # Two ASI source numbers contain punctuation that the source parser splits.
        # The raw value continues after the parsed numeric prefix in both records.
        code, number = key.split(":", 1)
        fragments = all(code == "ASI" and number.replace(".", "") in e["raw_museum_cell"].replace(".", "").replace(" ", "")
                        and "," in e["raw_museum_cell"] for e in evidence)
        collision_audit.append({"key": key, "families": families, "disposition": "parser-fragment" if fragments else "repeated-source-value-needs-plate",
                                "evidence": evidence})
    V.dump(local / "collision-audit.json", collision_audit)
    with (out / "candidate-source-identities.csv").open("x", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate", "cisi_identifiers", "source_locators", "disposition", "same_object_asserted"])
        for i, r in enumerate(collision_audit, 1):
            w.writerow([f"accession-candidate-{i:02}", ";".join(e["cisi"] for e in r["evidence"]),
                        ";".join(f"{e['volume']} printed {e['printed_page']} PDF {e['pdf_page']}" for e in r["evidence"]), r["disposition"], "false"])

    details = V.rows(V.LOCAL / "run-v1/primary-details.jsonl")
    family_summary = []
    for cl in sorted({r["class"] for r in details}):
        rr = [r for r in details if r["class"] == cl]
        family_summary.append({"class": cl, "components": len(rr), "mean_gain_bits": sum(r["gain"] for r in rr) / len(rr),
                               "site_count": len({r["site"] for r in rr}), "variant_count": len({r["code"] for r in rr}),
                               "site_counts": dict(Counter(r["site"] for r in rr))})
    V.dump(out / "family-summary.json", family_summary)
    codeclass, familycodes = V.mapping()
    observed = []
    for row in V.rows(V.INPUTS["faces"]):
        if not row.get("clean_rtl_singleline") or len(row["signs_reading_rtl"]) < 3:
            continue
        if not V.INV.usable("site", row.get("site")):
            continue
        seq = row["signs_reading_rtl"]
        src = source.get(row["object_family_id"], {})
        m = row["metadata"]
        for i, code in enumerate(seq):
            cl = codeclass.get(code)
            if code not in familycodes.get(cl, []):
                continue
            observed.append({"code": code, "class": cl, "family": row["object_family_id"], "record": row["record_id"],
                             "site": row["site"], "cisi": row["source_cisi"], "position": i,
                             "frame": seq[:i] + [cl] + seq[i + 1:], "carrier": row["object_type"],
                             "motif": V.norm("symbol", row["symbol"]), "preservation": V.norm("preservation", m.get("preservation")),
                             "volume": "+".join(src.get("volumes", [])) or "not-held",
                             "qualified": src.get("qualified_cisi", False)})
    support = []
    requirements = [[], ["carrier"], ["carrier", "motif"], ["carrier", "motif", "preservation"], ["carrier", "motif", "preservation", "volume"]]
    for qualifiers in requirements:
        buckets = defaultdict(list)
        for r in observed:
            key = tuple(r["frame"]) + (r["position"],) + tuple(r[k] for k in qualifiers)
            buckets[key].append(r)
        eligible = [v for v in buckets.values() if len({r["site"] for r in v}) > 1 and len({r["code"] for r in v}) > 1]
        supported_families = {r["family"] for v in eligible for r in v}
        support.append({"qualifiers": qualifiers, "cross_site_variable_frames": len(eligible),
                        "target_events": sum(len(v) for v in eligible), "physical_families": len(supported_families),
                        "source_qualified_families": len({r["family"] for v in eligible for r in v if r["qualified"]})})
        if qualifiers == requirements[-1]:
            V.dump(local / "strict-all-events-worklist.json", eligible)
    V.dump(out / "support.json", {"status_class": "exploratory", "endpoint": "post-outcome coverage only", "all_target_events": len(observed),
                                 "collision_dispositions": dict(Counter(r["disposition"] for r in collision_audit)), "frame_support": support,
                                 "provenance": V.provenance(), "audit_code_sha256": V.sha(__file__),
                                 "local_hashes": {p.name: V.sha(p) for p in local.iterdir()}})
    print(json.dumps({"collision_dispositions": dict(Counter(r["disposition"] for r in collision_audit)), "frame_support": support}, indent=2))


if __name__ == "__main__":
    main()
