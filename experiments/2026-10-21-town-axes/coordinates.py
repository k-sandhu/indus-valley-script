"""Observer coordinates for the horizon profiles (PROTOCOL.md, Horizon): the mean of the imagery measurers'
site coordinates where they report them, otherwise the plan measurers'. Reads only the location fields."""
import argparse, glob, json
from pathlib import Path
from common import BASE, write_new

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    locs = {}
    for role in ("measure-img-A", "measure-img-B", "measure-plan-A", "measure-plan-B"):
        for f in sorted(glob.glob(str(BASE / role / "towns" / "*.json"))):
            j = json.loads(Path(f).read_text(encoding="utf-8"))
            l = j.get("location") or {}
            if l.get("lat") is not None and l.get("lon") is not None:
                locs.setdefault(j.get("town") or Path(f).stem, {})[role] = (float(l["lat"]), float(l["lon"]), l.get("basis"))
    out = []
    for town, d in sorted(locs.items()):
        img = [v for k, v in d.items() if "img" in k]
        use = img or list(d.values())
        out.append({"slug": town, "lat": round(sum(v[0] for v in use) / len(use), 6), "lon": round(sum(v[1] for v in use) / len(use), 6),
                    "basis": "mean of " + ", ".join(k.replace("measure-", "") for k in d if (("img" in k) if img else True)) + " site coordinates",
                    "spread_m": round(max((((v[0] - use[0][0]) * 111000) ** 2 + ((v[1] - use[0][1]) * 100000) ** 2) ** 0.5 for v in use), 0)})
    print(write_new(a.out, out))

if __name__ == "__main__":
    main()
