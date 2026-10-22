"""Write plans-v1.json, the list of plans given to the registrars.

It copies from the plan-B town files of the town-axes package only what a
registrar needs to find a plan and its scale: render file, publication,
page, scale bar and approximate site coordinates. North arrows, line
bearings, deviations and systems are left out, so that the registrars
choose control points without seeing any orientation value.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TA = ROOT / "experiments" / "2026-10-21-town-axes"

ROLES = {
    # town: (role, group)
    "kalibangan": ("target", "G1"),
    "banawali": ("target", "G1"),
    "farmana": ("target", "G1"),
    "harappa": ("optional", "G1"),
    "surkotada": ("target", "G2"),
    "kanmer": ("target", "G2"),
    "dholavira": ("validation", "G2"),
    "chanhu-daro": ("target", "G3"),
    "lothal": ("validation", "G3"),
    "rangpur": ("optional", "G3"),
    "rojdi": ("optional", "G3"),
    "gola-dhoro": ("optional", "G3"),
}
SKIP = {"harappa:vats1940-pl3"}  # a granary-area plan; Wheeler's citadel plan covers the same mound


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists; write to a new path")
    plans = []
    for town, (role, group) in ROLES.items():
        f = TA / "measure-plan-B" / "towns" / f"{town}.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        for s in d["sources"]:
            pid = f"{town}:{s['id']}"
            if pid in SKIP or not s.get("render"):
                continue
            render = s["render"]
            alt = None
            if render.endswith("_wallmask.png"):
                alt, render = render, render.replace("_wallmask.png", ".png")
            elif render.endswith("_native_inverted.png"):
                alt = render.replace("_native_inverted.png", "_native.png")
            sb = s.get("scale_bar_measurement") or {}
            plans.append({
                "id": pid,
                "town": town,
                "source_id": s["id"],
                "role": role,
                "group": group,
                "citation": s.get("citation_or_service"),
                "locator": s.get("locator"),
                "publication_file": s.get("file"),
                "pdf_page_index": s.get("pdf_page_index"),
                "render": render,
                "render_sha256": sha256(ROOT / render),
                "render_alternative_same_pixels": alt,
                "scale_bar_m_per_px": sb.get("m_per_px"),
                "scale_bar_px": [sb.get("p1_px"), sb.get("p2_px")] if sb else None,
                "scale_bar_length_m": sb.get("length_m"),
                "site_lat_approx": d["location"]["lat"],
                "site_lon_approx": d["location"]["lon"],
            })
    rec = {
        "schema_version": "1.0",
        "created": "2026-10-21",
        "purpose": "Plans to be registered to imagery. Coordinates are published site coordinates, unchecked against imagery, and may be off by several hundred metres.",
        "source": "experiments/2026-10-21-town-axes/measure-plan-B/towns/*.json (render, publication, page and scale-bar fields only)",
        "plans": plans,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(plans), "plans written to", out)


if __name__ == "__main__":
    main()
