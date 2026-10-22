"""Copy line candidates accepted by eye into a town configuration (role img-B).

Usage: python accept.py <slug> <spec.json>
spec.json is a list of {"cand": "P1-3", "system": "sys1", "kind": "...", "description": "...", "confidence": "..."}.
The endpoints and the candidate's statistics are copied from the candidate list
written by candidates.py, so the configuration holds every number needed to
rerun the measurement.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tiles  # noqa: E402
import cfgio  # noqa: E402

HERE = Path(__file__).resolve().parent


def main(slug, spec_path, replace=True):
    cfgp = HERE / "configs" / f"{slug}.json"
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    cands = json.loads((tiles.RAW / "views" / slug / "candidates.json").read_text())
    flat = {c["id"]: c for v in cands.values() for c in v}
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    sysparts = {s["id"]: s["part"] for s in cfg["systems"]}
    lines = [] if replace else cfg.get("check_lines", [])
    n0 = len(lines)
    for i, sp in enumerate(spec):
        c = flat[sp["cand"]]
        lines.append({
            "id": sp.get("id", f"S{n0 + i + 1}"), "system": sp["system"], "part": sp.get("part", sysparts[sp["system"]]),
            "kind": sp["kind"], "description": sp["description"],
            "p0": c["p0"], "p1": c["p1"], "no_refine": True,
            "endpoint_sigma_px": max(1.0, c["rms_px"]),
            "method": f"endpoints of a straight edge found by the OpenCV line-segment detector ({c['n_pieces']} piece(s), coverage {c['coverage']}, rms {c['rms_px']} px), accepted by eye as a wall or street edge (candidate {c['id']})",
            "confidence": sp.get("confidence", "medium"), "phase": sp.get("phase"),
        })
    cfg["check_lines"] = lines
    cfgio.save(cfg, cfgp)
    print(len(lines), "check lines")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], replace="--append" not in sys.argv)
