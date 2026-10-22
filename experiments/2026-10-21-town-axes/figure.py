"""Figure for the report: town deviation against layout date, with the star and equinox models.

python figure.py --table exploratory-v1/table.json --out figures-v1/deviation-vs-date.svg
"""
import argparse
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import astro

INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
NAMES = {"mohenjo-daro": "Mohenjo-daro", "chanhu-daro": "Chanhu-daro"}
SERIES = {"alcyone": ("#2a78d6", "Pleiades (Alcyone) setting"), "aldebaran": ("#eb6834", "Aldebaran setting"),
          "sun-equinox-set": ("#1baf7a", "Equinoctial sunset")}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--table", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise FileExistsError(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    towns = [t for t in json.loads(Path(a.table).read_text(encoding="utf-8"))["towns"]
             if t.get("theta_deg") is not None and t.get("D_year") is not None]
    stars = astro.load_stars()
    years = np.arange(-3099, -1849, 25)
    flat = lambda az: 0.0
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=SURFACE)
    for ax, (ylo, yhi), title in ((axes[0], (-34, 44), "All towns with a layout date"),
                                  (axes[1], (-9, 6), "The four towns measured on imagery, with the models")):
        ax.set_facecolor(SURFACE)
        ax.axhline(0, color=MUTED, lw=1)
        for key, (col, label) in SERIES.items():
            for lat, ls in ((23.5, "-"), (30.5, ":")):
                th = [astro.predicted_deviation(key, y, lat, flat, stars) for y in years]
                ax.plot(1 - years, th, color=col, lw=2, ls=ls, label=f"{label}, lat {lat}°" if ax is axes[1] else None)
        for t in towns:
            img = str(t.get("theta_basis", "")).startswith("imagery")
            x, y = 1 - t["D_year"], t["theta_deg"]
            if not (ylo <= y <= yhi) or (ax is axes[1] and not img):
                continue
            ax.errorbar(x, y, yerr=t["sigma_theta_deg"], xerr=t["sigma_D"], fmt="o", ms=7, lw=1, capsize=0,
                        color=INK, mfc=INK if img else SURFACE, mec=INK, zorder=3)
            ax.annotate(NAMES.get(t["town"], t["town"].title()), (x, y), xytext=(5, 6), textcoords="offset points",
                        fontsize=8, color=INK2)
        ax.set_xlim(3150, 1850); ax.set_ylim(ylo, yhi)
        ax.set_xlabel("Layout date (years BCE)"); ax.set_ylabel("Deviation from cardinal (degrees, clockwise +)")
        ax.set_title(title, fontsize=10, color=INK, loc="left")
        ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].plot([], [], "o", color=INK, mfc=INK, label="Imagery, true north")
    axes[0].plot([], [], "o", color=INK, mfc=SURFACE, label="Plans, north not stated")
    axes[0].legend(loc="upper left", frameon=False, fontsize=8)
    axes[1].legend(loc="lower right", frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(out, facecolor=SURFACE)
    print(out)


if __name__ == "__main__":
    main()
