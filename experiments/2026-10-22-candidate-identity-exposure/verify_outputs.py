"""Check frozen output closure, evidence links, hashes and deterministic replay."""
import json
from pathlib import Path

from audit import HERE, PATHS, ROOT, normalize_site, read_csv, sha, site_registration, write_json


def lines(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]


def main():
    target = HERE / "source-and-replay-verification.json"
    if target.exists(): raise ValueError("Existing verification output refused")
    base = ROOT / "data/raw/2026-10-22-candidate-identity-exposure"
    run, replay = base / "run-v3", base / "replay-v3"
    reviews = lines(run / "candidate-reviews.jsonl")
    events = {r["event_id"]: r for r in lines(run / "exposure-events.jsonl")}
    patches = lines(run / "assertion-patches.jsonl")
    queue = {r["source_row_id"] for r in read_csv(PATHS["queue"])}
    inventory = {r["row_id"]: r for r in read_csv(PATHS["inventory"])}
    register = {r["object_id"]: r for r in lines(ROOT / PATHS["register"])}
    checked = []
    def check(name, condition, **detail):
        checked.append({"check": name, "passed": bool(condition), **detail})
        if not condition: raise AssertionError(name)
    check("fixed_selection_and_patch_closure", len(reviews) == len(patches) == 358 and {r["source_row_id"] for r in reviews} == queue == {p["source_row_id"] for p in patches})
    supported_checks = 0
    event_checks = 0
    for review in reviews:
        source = inventory[review["source_row_id"]]
        check("reviewed_no_confirmation_eligibility:" + review["source_row_id"], review["review_status"] == "metadata_review_completed" and review["confirmation_eligible"] is False)
        for oid in review["supported_candidate_family_ids"]:
            obj = register[oid]
            aliases = [a["value"] for a in obj["aliases"] if a["status"] == "confirmed" and (a["scheme"] == "export_registration_string" or a["scheme"].endswith(":field_number"))]
            same_site = normalize_site(obj["fields"]["context.site"]["value"]) in {normalize_site(source["site"]), normalize_site(source["local_site_label"])}
            check("whole_site_identifier:" + review["source_row_id"] + ":" + oid, same_site and any(site_registration(source["site"], a) == site_registration(source["site"], source["registration"]) for a in aliases))
            supported_checks += 1
        for event in review["exposure_events"]:
            raw = events[event["event_id"]]
            allowed_source = raw["source_id"] == review["primary_source_id"] or bool(raw["source_asset_sha256_declared"] and raw["source_asset_sha256_declared"] == review["source_version"]["sha256_declared"])
            check("source_and_page_event:" + review["source_row_id"] + ":" + event["event_id"], allowed_source and event["matched_pdf_pages"] == sorted(set(raw["pdf_pages"]) & set(review["candidate_pdf_pages"]["pages"])))
            event_checks += 1
    manifest = json.loads((HERE / "run-v3/source-manifest.json").read_text(encoding="utf-8"))
    check("input_bytes_unchanged", all(sha(ROOT / p["path"]) == p["sha256"] for p in manifest["inputs"]))
    check("final_builder_hash", sha(HERE / "audit.py") == manifest["code_sha256"])
    comparison = [{"file": p.name, "sha256": sha(p), "replay_sha256": sha(replay / p.name), "byte_equal": p.read_bytes() == (replay / p.name).read_bytes()} for p in sorted(run.iterdir())]
    check("all_local_outputs_byte_identical", all(c["byte_equal"] for c in comparison))
    relations = lines(run / "duplicate-relations.jsonl")
    check("duplicate_review_without_merges", len(relations) == 13 and all(r["merge_authorized"] is False and r["duplicate_cluster"] is None for r in relations))
    write_json(target, {"status": "passed", "checks_passed": len(checked), "errors": [], "supported_identifier_links_checked": supported_checks, "candidate_event_associations_checked": event_checks, "reviewed_candidates": len(reviews), "replay": comparison, "scope": "Metadata and output verification; does not reconstruct historical tool pixels or certify physical object identity."})
    print(json.dumps({"status": "passed", "checks": len(checked), "supported_links": supported_checks, "event_associations": event_checks, "replayed_files": len(comparison)}))


if __name__ == "__main__": main()
