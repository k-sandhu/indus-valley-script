"""Assemble frozen-reference.json from the discovery inventories and the Brahmi calibration."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventories", default=str(HERE / "discovery-v1/inventories.json"))
    ap.add_argument("--calibration", default=str(HERE / "calibration-v1/calibration.json"))
    ap.add_argument("--brahmi-variant", choices=("strict", "broad"), required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    inv = json.loads(Path(args.inventories).read_text(encoding="utf-8"))
    cal = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
    t0 = inv["T0"]
    ref = {
        "discovery_T0_counts": t0,
        "discovery_T0_inventory": sorted(t0),
        "discovery_T0_top4": [k for k, _ in sorted(t0.items(), key=lambda kv: (-kv[1], kv[0]))[:4]],
        "brahmi_variant": args.brahmi_variant,
        "brahmi_asterism_counts": cal["variants"][args.brahmi_variant]["asterism_counts"],
        "brahmi_strict_counts": cal["variants"]["strict"]["asterism_counts"],
        "brahmi_broad_counts": cal["variants"]["broad"]["asterism_counts"],
        "sources": {"inventories": args.inventories, "inventories_sha256": sha(args.inventories),
                    "calibration": args.calibration, "calibration_sha256": sha(args.calibration)},
    }
    with open(args.out, "x", encoding="utf-8") as f:
        json.dump(ref, f, indent=2)
    print(json.dumps({k: ref[k] for k in ("discovery_T0_top4", "brahmi_variant", "brahmi_asterism_counts")}, indent=1))


if __name__ == "__main__":
    main()
