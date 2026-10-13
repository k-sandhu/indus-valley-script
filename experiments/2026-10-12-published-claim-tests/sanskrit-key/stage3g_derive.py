"""Derived Stage 3g comparisons: transfer to half B relative to each language's null and own text."""
import json
import os

import numpy as np

from common import HERE


def main():
    with open(os.path.join(HERE, "stage3g", "summary.json"), encoding="utf-8") as f:
        s = json.load(f)
    out = {}
    for name, d in s["languages"].items():
        refs = [d["references"][f"line_initial_{k}"]["G"] for k in (1, 2, 3)]
        ref = float(np.mean(refs))
        null = d["null_token_matched"]
        runs = [r for r in s["language_runs"] if r["language"] == name]
        fit_all = [r["G_fit"] for r in runs if r["label"] == "real"]
        b = [r["eval_B"]["G"] for r in runs if r["label"] == "fitA"]
        a = [r["eval_A"]["G"] for r in runs if r["label"] == "fitA"]
        scr_real = [r["eval_real"]["G"] for r in runs if r["label"] == "scrambled"]
        out[name] = {
            "own_text_reference_mean_1to3_words": ref,
            "null_mean_all": null["mean_all"], "null_sd_all": null["sd_all"],
            "null_mean_B": null["mean_B"], "null_sd_B": null["sd_B"],
            "fit_all_mean": float(np.mean(fit_all)),
            "fitA_in_sample_mean": float(np.mean(a)),
            "fitA_on_B_mean": float(np.mean(b)),
            "transfer_z": float((np.mean(b) - null["mean_B"]) / null["sd_B"]),
            "transfer_gap_closed": float((np.mean(b) - null["mean_B"]) / (ref - null["mean_B"])),
            "fit_all_gap_closed": float((np.mean(fit_all) - null["mean_all"]) / (ref - null["mean_all"])),
            "scrambled_fit_on_real_mean": float(np.mean(scr_real)),
        }
    km = s["key_multiset"]
    out["key_multiset_within_strata"] = {
        "real_fit": [r["G_fit"] for r in km if r["label"] == "real"],
        "scrambled_fit_on_scrambled": [r["eval_scrambled"]["G"] for r in km if r["label"].startswith("scrambled")],
        "scrambled_fit_on_real": [r["eval_real"]["G"] for r in km if r["label"].startswith("scrambled")],
        "fitA_in_sample": [r["eval_A"]["G"] for r in km if r["label"] == "fitA"],
        "fitA_on_B": [r["eval_B"]["G"] for r in km if r["label"] == "fitA"],
    }
    with open(os.path.join(HERE, "stage3g", "derived.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
