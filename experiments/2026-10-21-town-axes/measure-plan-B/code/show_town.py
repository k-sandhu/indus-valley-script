"""Print a compact summary of a built town JSON (for checking during measurement)."""
import json, sys
for slug in sys.argv[1:]:
    t = json.load(open("experiments/2026-10-21-town-axes/measure-plan-B/towns/%s.json" % slug, encoding="utf-8"))
    for s in t["sources"]:
        a = s.get("north_arrow_measurement", {})
        print(s["id"], "arrow az", a.get("page_azimuth_deg"), "render", s["rendering_check"])
    for s in t["structures"]:
        print("  ", s["id"], s["source"], s["bearing_deg"], s["deviation_deg"], "+-", s["sigma_deg"], s["length_m"], "m", s["confidence"])
    for s in t["systems"]:
        print(" SYS", s["id"], s["source"], s["deviation_deg"], "se", s["se_deg"], "sd", s["sd_deg"], s["total_length_m"], "m n", s["n_lines"])
