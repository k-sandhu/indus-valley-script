"""Plot reported phase composition. This figure makes no production estimate."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument("--summary", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    raise SystemExit("Refusing to overwrite figure")
data = json.loads(args.summary.read_text(encoding="utf-8"))
rows = [r for r in data["cohorts"] if r["site"] in ("Masudpur VII", "Bahola")]
labels = [r["site"] + ": " + r["phase"].replace("Harappan", "H.") for r in rows]
fig, ax = plt.subplots(figsize=(9.2, 4.8))
left = [0.] * len(rows)
for key, label, color in [("winter_pct", "Winter", "#305f72"), ("summer_pct", "Summer", "#c99443"),
                          ("fruit_pct", "Tree/orchard", "#829d76"), ("unknown_pct", "Unassigned", "#d2d6d5")]:
    values = [r[key] for r in rows]
    ax.barh(labels, values, left=left, color=color, label=label, height=.65)
    left = [a+b for a,b in zip(left, values)]
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("Reported percentage of recovered crop assemblage")
ax.set_title("Both seasons persist while their proportions change", loc="left", pad=18)
ax.legend(loc="upper left", bbox_to_anchor=(0, -.19), ncol=4, frameon=False)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.text(.02, .025, "Source: Petrie & Bates (2017), Tables S12 and S23, CC BY 4.0.\n"
         "Our replot of published rounded proportions; no error bars or acreage inference.", fontsize=8, color="#4b555a")
fig.subplots_adjust(left=.36, bottom=.29, right=.97, top=.85)
metadata = {"Creator": "Indus research project"}
if args.out.suffix.lower() == ".svg":
    metadata["Date"] = None
fig.savefig(args.out, metadata=metadata)
plt.close(fig)
