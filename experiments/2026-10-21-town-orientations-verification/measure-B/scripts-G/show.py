"""Print a compact table of a measure_lines.py result."""
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
a = d.get("arrow")
if a:
    print("arrow dir_px", round(a["direction_px_deg"], 3), "sigma", round(a["sigma_deg"], 3), "m/px", d.get("metres_per_render_pixel"))
for r in d["lines"]:
    rms = r.get("residual_rms_px")
    print(f"{r['id']:28s} brg {r['bearing_deg']:8.3f} th {r['theta_deg']:7.3f} sig {r['sigma_deg']:.3f} L {r['length_m']:7.1f} inl {r['inlier_count']}/{r['profile_count']} rms {rms if rms is None else round(rms,3)} {r.get('warnings', [])}")
