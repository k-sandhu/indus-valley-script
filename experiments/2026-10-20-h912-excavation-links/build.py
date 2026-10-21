"""Build a source-qualified audit without reading inscription sequences."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-20-h912-excavation-links"
CORPUS = ROOT / "data/normalized/lipi_observed_faces.jsonl"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--local-out", required=True)
    args = parser.parse_args()
    out, local = ROOT / args.out, ROOT / args.local_out
    if out.exists() or local.exists():
        raise FileExistsError("Choose fresh outputs")
    obs = json.loads((OWN / "source-observations-v1.json").read_text(encoding="utf-8"))
    # Retain metadata only: sequence fields are never used by this audit.
    faces = []
    for line in CORPUS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        faces.append({k: r[k] for k in ["record_id", "object_family_id", "source_cisi", "site", "metadata"]})
    rows, private = [], []

    def add(kind, identifier, registration, source, relation, status, grade, cisi="", family="", detail=""):
        rows.append({"kind": kind, "identifier": identifier, "registration": registration,
                     "cisi": cisi, "family": family, "source": source, "context_relation": relation,
                     "join_status": status, "observational_grade": grade,
                     "direct_container_or_fish_lot_join": False, "detail": detail})

    for item in obs["h912_assertions"]:
        add("H912 field", item["field"], "8650c", item["source"] + " " + item["locator"],
            str(item["value"]), item["status"], item.get("basis", "documented missingness"), "H-912", "1793", item.get("scope", ""))
    for item in obs["series_8650"]:
        add("8650 suffix", item["registration"], item["registration"], "Vats1940 p." + str(item["source_page"]),
            "source collection frame; separate suffix retained", "source-registered",
            "published description", detail=json.dumps(item, ensure_ascii=False))
    for item in obs["broader_associations"]:
        add("broader association", item["registration"], item["registration"], item["source"],
            item["relation"], "source-registered-broader-setting", "published description",
            detail=json.dumps(item, ensure_ascii=False))
    plan_matches = []
    for item in obs["plan_objects"]:
        key = item["registration"]
        pattern = re.compile(re.escape(key) + r"(?:\D|$)")
        found = [r for r in faces if pattern.search(r["metadata"]["excavation-idno"])]
        fams = sorted({r["object_family_id"] for r in found})
        cisi = sorted({r["source_cisi"] for r in found})
        assert len(fams) == 1 and len(cisi) == 1, (key, fams, cisi)
        match = {**item, "family": fams[0], "cisi": cisi[0], "face_count": len(found),
                 "join_basis": "1990 plan caption and exact registration number; source year confirmed by export",
                 "fish_unit": None, "fish_association": "plan area only; no object-to-lot join"}
        plan_matches.append(match)
        add("Belcher plan object", key, key, "Belcher1991 p.109 Fig8.2", item["context_key"],
            "unique-registration", item["object_grade"] + "; " + item["location_grade"],
            cisi[0], fams[0], item["label_raw"])
    old = defaultdict(list)
    for face in faces:
        if face["site"] == "Harappa" and re.match(r"^8650[a-z]", face["metadata"]["excavation-idno"], re.I):
            old[face["object_family_id"]].append(face)
    source_refs = defaultdict(list)
    for fam, fs in old.items():
        meta = fs[0]["metadata"]
        raw = meta["excavation-idno"]
        source_refs[raw].append(fam)
        private.append({"family": fam, "cisi": fs[0]["source_cisi"], "excavation": raw,
                        "depth": meta["depth"], "stratum": meta["phase"], "faces": len(fs)})
        add("export prefix candidate", fam, raw, "Lipi export metadata", "candidate registration-series membership",
            "requires-source-qualification", "derivative metadata; no physical merge", fs[0]["source_cisi"], fam,
            "Depth and stratum retained locally; prefix alone does not establish closed-deposit identity.")
    for item in obs["catalogue_qualifiers"]:
        add("catalogue qualifier", item["target"], item.get("excavation", ""), item["source"],
            item["explanation"], item["status"], "primary catalogue or preserved derivative qualifier", item["target"])
    summary = {
        "h912_fields_audited": len(obs["h912_assertions"]),
        "primary_registration": "8650c",
        "primary_depth_ft_below_surface": [4,7],
        "export_depth_ft": -5.5,
        "depth_midpoint_compatibility": 5.5 == (4+7)/2,
        "point_measurement_source_found": False,
        "primary_square_frame": ["H12/21","I12/1"],
        "closed_deposit_documented": False,
        "recovery_period": "three months",
        "suffix_records": len(obs["series_8650"]),
        "stratum_conflict": {"overview": "IV", "8650q_specialist_chapter": "III"},
        "broader_registered_associations": len(obs["broader_associations"]),
        "export_prefix_families": len(old),
        "export_prefix_faces": sum(len(v) for v in old.values()),
        "shared_exact_source_references": {k:v for k,v in source_refs.items() if len(v)>1},
        "physical_merges_performed": 0,
        "belcher_plan_registered_objects": len(plan_matches),
        "belcher_plan_unique_export_joins": len(plan_matches),
        "belcher_plan_faces": sum(x["face_count"] for x in plan_matches),
        "belcher_plan_direct_fish_unit_joins": 0,
        "belcher_street_fish_lot_keys": len(obs["belcher_frame"]["street_lots_from_fig8_8"]),
        "h912_to_belcher_recovery_join": "excluded: different mound and excavation campaign",
        "h912_container_contents_or_allotment_joins": 0,
        "h302_cisi1": {"FC":"3864","excavation":"8650c","accession":"ASI63.11.94"},
        "empirical_bench_reads": 0,
        "disposition_rows": len(rows),
    }
    out.mkdir(parents=True)
    local.mkdir(parents=True)
    with (out / "dispositions.csv").open("x", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out / "summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out / "belcher-plan-joins.json").write_text(json.dumps(plan_matches,indent=2)+"\n",encoding="utf-8")
    (local / "prefix-metadata.json").write_text(json.dumps(private,indent=2)+"\n",encoding="utf-8")
    source_records=[]
    for source in obs["sources"]:
        p=ROOT/source["path"]
        source_records.append({"id":source["id"],"path":source["path"],"sha256":sha(p),"bytes":p.stat().st_size,"rights_status":source["rights_status"]})
        for page in source["pages_inspected"]:
            p=RAW/page["render"]
            assert p.exists(),p
            source_records.append({"source":source["id"],"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"printed_page":page["printed"],"pdf_page":page["pdf"],"rights_status":"rights-unverified"})
    provenance={"python":platform.python_version(),"corpus":{"path":CORPUS.relative_to(ROOT).as_posix(),"sha256":sha(CORPUS)},
                "code_sha256":sha(Path(__file__)),"protocol_sha256":sha(OWN/"PROTOCOL.md"),
                "observations_sha256":sha(OWN/"source-observations-v1.json"),"sources":source_records,
                "private_metadata_sha256":sha(local/"prefix-metadata.json"),"freshness":"source audit; no empirical confirmation read"}
    (out/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
