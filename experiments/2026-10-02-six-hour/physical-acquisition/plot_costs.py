"""Plot identification counts from the saved paired acquisition summary."""

from hashlib import sha256
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    root = Path(__file__).resolve().parent
    target = root / "figures"
    target.mkdir(exist_ok=True)
    outputs = [target / "acquisition-cost-v2.svg", target / "acquisition-cost-v2.png"]
    if any(p.exists() for p in outputs):
        raise FileExistsError(outputs)
    source = root / "main-analysis/analysis.json"
    analysis = json.loads(source.read_text())
    labels = {"information_rank": "Information/rank", "random": "Random", "cost_availability": "Cheapest available"}
    colours = {"information_rank": "#206095", "random": "#e36b23", "cost_availability": "#777777"}
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for axis, condition, title in zip(axes, ("complete_exact", "incomplete"), ("Complete groups and exact counts", "Incomplete groups and exact counts")):
        for policy in labels:
            row = next(r for r in analysis["rows"] if r["condition"] == condition and r["policy"] == policy)
            curve = row["absolute_identification_by_paid_cost"]
            axis.step(range(25), [curve[str(cost)] for cost in range(25)], where="post",
                      label=labels[policy], color=colours[policy], linewidth=2)
        axis.set_title(title, fontsize=11)
        axis.set_xlabel("Paid observation cost")
        axis.set_xlim(0, 24); axis.set_ylim(-0.5, 24.5)
        axis.set_xticks(range(0, 25, 4)); axis.set_yticks(range(0, 25, 4))
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Worlds with correct absolute quantities (of 24)")
    axes[1].legend(loc="upper left", frameon=False, fontsize=9)
    fig.tight_layout()
    for path in outputs:
        fig.savefig(path, dpi=160)
    plt.close(fig)
    manifest = {"status": "own-scientific-figure", "analysis_sha256": sha256(source.read_bytes()).hexdigest(),
                "matplotlib_version": matplotlib.__version__, "numpy_version": np.__version__,
                "code_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                "figures": {p.name: sha256(p.read_bytes()).hexdigest() for p in outputs},
                "interpretation": "First correct absolute identification by paid cost; policies retain worlds lacking identification. Synthetic acquisition worlds."}
    (target / "acquisition-cost-v2-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
