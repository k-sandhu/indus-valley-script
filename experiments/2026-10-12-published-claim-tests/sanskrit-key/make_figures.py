"""Figures for Study A, drawn only from saved summaries (SVG, project-authored)."""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import HERE, RAW

GRAY = "#8a8985"
BLUE = "#2a78d6"     # the published key and readings
AQUA = "#1baf7a"     # optimized keys
ORANGE = "#eb6834"   # real Sanskrit text
INK = "#0b0b0b"
INK2 = "#52514e"


def load(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as f:
        return json.load(f)


def order_gain_figure():
    s3 = load("stage3/summary.json")
    n1 = np.load(os.path.join(RAW, "sanskrit-key", "stage3_null_arrays.npz"))["n1"][:, 0]
    ref = s3["sanskrit_word_span_reference"]
    ann = s3["anneal"]
    g3 = load("stage3g/summary.json")["key_multiset"]
    rows = [
        ("Random letter strings at Sanskrit frequencies", [ref["iid_unigram_strings_key_lengths"]["G"]], GRAY),
        ("Key values rearranged within frequency strata (1,000)", list(n1), GRAY),
        ("Yajnadevam's key", [s3["key"]["all"]["G"]], BLUE),
        ("His published readings (with inserted consonants)", [s3["published_reading_skeletons"]["G"]], BLUE),
        ("Rearranged to fit sign-shuffled texts, scored on real order",
         [r["eval_real"]["G"] for r in g3 if r["label"].startswith("scrambled")], AQUA),
        ("Rearranged to fit half A, scored on unseen half B", [r["eval_B"]["G"] for r in g3 if r["label"] == "fitA"], AQUA),
        ("Best rearrangements found (same values, same consonant count)",
         [r["G_fit"] for r in g3 if r["label"] == "real"], AQUA),
        ("Unconstrained swaps (turn 22-46% of signs into vowels)",
         [a["G_fit"] for a in ann if a["label"] == "real"], GRAY),
        ("Real Sanskrit: sentence-initial spans of 1-4 words",
         [v["G"] for v in ref["line_initial"].values()], ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    rng = np.random.default_rng(0)
    for i, (label, vals, color) in enumerate(rows):
        y = len(rows) - 1 - i
        vals = np.array(vals)
        if len(vals) > 50:
            lo, hi = np.percentile(vals, [2.5, 97.5])
            ax.plot([lo, hi], [y, y], color=color, lw=6, solid_capstyle="round", alpha=0.45)
            ax.plot([np.mean(vals)], [y], "o", color=color, ms=7, mec="white", mew=1.5)
        else:
            jitter = rng.uniform(-0.12, 0.12, size=len(vals)) if len(vals) > 1 else np.zeros(1)
            ax.plot(vals, y + jitter, "o", color=color, ms=8, mec="white", mew=1.5)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-0.75, 0.85)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_yticks([len(rows) - 1 - i for i in range(len(rows))])
    ax.set_yticklabels([r[0] for r in rows], fontsize=9, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#e4e3df", lw=0.6)
    ax.set_xticks([-0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8])
    ax.tick_params(axis="x", colors=INK2, labelsize=9)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.set_xlabel("Order gain under a Sanskrit 5-gram model (bits per consonant; 0 = no better than letter frequencies)",
                  fontsize=9, color=INK2)
    ax.set_title("The key sits near its own rearrangements and far below Sanskrit text",
                 fontsize=10.5, color=INK, loc="left")
    fig.tight_layout()
    out = os.path.join(HERE, "figures")
    os.makedirs(out, exist_ok=True)
    fig.savefig(os.path.join(out, "order-gain.svg"))
    if os.environ.get("PREVIEW"):
        fig.savefig(os.path.join(os.environ["PREVIEW"], "order-gain.png"), dpi=int(os.environ.get("PREVIEW_DPI", "110")))
    plt.close(fig)


def readability_figure():
    s2 = load("stage2/summary.json")
    by = s2["random_strings_by_length"]
    L = sorted(int(k) for k in by)
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    series = [("mw_m1", "Stems of one or more consonants (as in the published glossing)", BLUE),
              ("mw_m2", "Every stem at least two consonants", ORANGE)]
    for key, label, color in series:
        ys = [by[str(l)][key] * 100 for l in L]
        ax.plot(L, ys, "-o", color=color, lw=2, ms=5, mec="white", mew=1, label=label)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False, labelcolor=INK)
    ax.set_ylim(0, 104)
    ax.set_xlim(0.5, 16.5)
    ax.set_xlabel("Length of random consonant string", fontsize=9, color=INK2)
    ax.set_ylabel("Readable as Monier-Williams stems (%)", fontsize=9, color=INK2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e4e3df", lw=0.6)
    ax.set_title("Random strings at Sanskrit letter frequencies pass the readability criterion",
                 fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "figures", "readability.svg"))
    if os.environ.get("PREVIEW"):
        fig.savefig(os.path.join(os.environ["PREVIEW"], "readability.png"), dpi=int(os.environ.get("PREVIEW_DPI", "110")))
    plt.close(fig)


def separation_figure():
    """How far a key sits above within-stratum permutations of itself, in null standard deviations."""
    s3 = load("stage3/summary.json")
    sens = load("stage3/sensitivity_exhaustive.json")
    s5 = load("stage5/summary.json")
    rows = []
    for name, label in (("sumerian", "Sumerian (Ur III)"), ("tamil", "Old Tamil"), ("latin", "Latin"),
                        ("sanskrit", "Sanskrit")):
        p = s5["plaintexts"][name]
        z = (p["true_key_G"] - p["permuted_true_key"]["mean"]) / p["permuted_true_key"]["sd"]
        rows.append((f"True key, synthetic Indus-shaped {label} corpus", z, ORANGE))
    z_key = (s3["key"]["all"]["G"] - s3["N1_all"]["mean_G"]) / s3["N1_all"]["sd_G"]
    z_key_ex = (sens["key_G_exhaustive"] - sens["N1_300_exhaustive"]["mean"]) / sens["N1_300_exhaustive"]["sd"]
    tr = load("stage3/sensitivity_training.json")
    z_best = max(v["N1_G"]["z_key"] for v in tr.values())
    rows.append(("Yajnadevam's key, most favourable training text and projection", z_best, BLUE))
    rows.append(("Yajnadevam's key on the Indus corpus, main model", z_key, BLUE))
    fig, ax = plt.subplots(figsize=(10.5, 3.6))
    ys = np.arange(len(rows))[::-1]
    for y, (label, z, color) in zip(ys, rows):
        ax.barh(y, z, height=0.55, color=color)
        ax.text(z + 0.8, y, f"{z:.1f}", va="center", fontsize=9, color=INK)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=INK2, labelsize=9)
    ax.set_xlabel("Order gain above the mean of within-stratum rearrangements, in their standard deviations",
                  fontsize=9, color=INK2)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.grid(axis="x", color="#e4e3df", lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Distance of a key above rearrangements of its own values",
                 fontsize=10.5, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "figures", "key-separation.svg"))
    if os.environ.get("PREVIEW"):
        fig.savefig(os.path.join(os.environ["PREVIEW"], "key-separation.png"), dpi=int(os.environ.get("PREVIEW_DPI", "110")))
    plt.close(fig)


if __name__ == "__main__":
    order_gain_figure()
    readability_figure()
    if os.path.exists(os.path.join(HERE, "stage5", "summary.json")):
        separation_figure()
    print("figures written")
