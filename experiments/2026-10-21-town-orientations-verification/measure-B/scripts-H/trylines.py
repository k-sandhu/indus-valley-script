"""Dry run of measure_lines on each pick separately; prints results, writes nothing.

Used to find which pick fails before the recorded run with tools/measure_lines.py.
Usage: trylines.py <picks.json> <render.png.json>
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
import warnings
warnings.filterwarnings("ignore")
import copy
from common import read_json
from measure_lines import measure


def main():
    picks = read_json(sys.argv[1])
    for line in picks["lines"]:
        one = copy.deepcopy(picks)
        one["lines"] = [line]
        try:
            r = measure(one, sys.argv[2])
            l = r["lines"][0]
            extra = ""
            if r.get("arrow"):
                extra = f" arrow_px={r['arrow']['direction_px_deg']:.2f}"
            print(f"{line['id']}: bearing {l['bearing_deg']:.2f} theta {l['theta_deg']:.2f} sigma {l['sigma_deg']:.2f} "
                  f"len {l['length_m']:.1f} m inl {l['inlier_count']}/{l['profile_count']} rms {l['residual_rms_px']} "
                  f"refined {[[round(v,1) for v in q] for q in l['refined_endpoints_px']]}{extra} {l.get('warnings','')}")
        except Exception as e:
            print(f"{line['id']}: FAILED {e}")


if __name__ == "__main__":
    main()
