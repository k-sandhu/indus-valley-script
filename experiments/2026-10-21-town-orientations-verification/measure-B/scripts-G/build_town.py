"""Assemble a town input for systems.py from a town config and measured line files.

The config (JSON) gives:
  slug, located_point, notes, unmeasurable_reason, registrations (optional),
  sources: list of source entries; a plan source may name its measured
           lines file in "lines_file" so that the arrow result is copied in,
  line_files: list of {"path": ..., "source_id": ..., "locator": ...,
                       "systems": {line_id: system}, "exclude": [line_id, ...]}

Every measured row keeps all refinement fields; source_id, a source locator and
the lines file path are added.  The output refuses to overwrite.

Usage: python -I build_town.py <config.json> <town-input.json>
"""
import json
import sys
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def main():
    cfg = load(sys.argv[1])
    out = Path(sys.argv[2])
    if out.exists():
        raise FileExistsError(out)
    sources = []
    manifest_path = "experiments/2026-10-21-town-orientations-verification/infra-v1/imagery-manifest-v1.json"
    for s in cfg["sources"]:
        s = dict(s)
        if s.get("kind") == "imagery" and s.get("manifest_slug"):
            man = load(manifest_path)
            t = next(t for t in man["towns"] if t["slug"] == s["manifest_slug"])
            ids = t["composite_scene_ids"]
            s["scene_ids"] = ids
            s["scene_datetimes"] = [sc["datetime"] for sc in t["scenes"] if sc["item_id"] in ids]
            s["manifest_path"] = manifest_path
            s["composite_path"] = t["composite"]["path"]
            s["composite_sha256"] = t["composite"]["sha256"]
            s["rights_notice"] = t["composite"]["rights_notice"]
        if s.get("lines_file"):
            m = load(s["lines_file"])
            s["north_record"] = m.get("north")
            s["arrow_result"] = m.get("arrow")
            s["metres_per_render_pixel"] = m.get("metres_per_render_pixel")
            s["source_sha256"] = m.get("source_sha256")
            s["measurement_provenance"] = m.get("provenance")
        sources.append(s)
    lines = []
    for lf in cfg.get("line_files", []):
        m = load(lf["path"])
        sid = lf["source_id"]
        if m["source_id"] != sid:
            raise ValueError(f"source id mismatch in {lf['path']}")
        excl = set(lf.get("exclude", []))
        for r in m["lines"]:
            if r["id"] in excl:
                continue
            row = dict(r)
            row["source_id"] = sid
            if r["id"] in lf.get("systems", {}):
                row["system_as_picked"] = r["system"]
                row["system"] = lf["systems"][r["id"]]
            row["lines_file"] = lf["path"]
            row["source_locator"] = lf["locator"]
            if "sigma_deg" not in row or row["sigma_deg"] is None:
                raise ValueError("line without error: " + r["id"])
            lines.append(row)
    town = dict(
        schema_version=1,
        slug=cfg["slug"],
        measurer="B",
        share="G",
        located_point=cfg["located_point"],
        sources=sources,
        lines=lines,
        registrations=cfg.get("registrations", []),
        notes=cfg.get("notes", ""),
        unmeasurable_reason=cfg.get("unmeasurable_reason"),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(town, indent=2, ensure_ascii=False) + "\n")
    print(out, len(lines), "lines")


if __name__ == "__main__":
    main()
