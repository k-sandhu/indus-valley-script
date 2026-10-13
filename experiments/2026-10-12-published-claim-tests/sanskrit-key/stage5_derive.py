"""Derived Stage 5 tables: true-key separation, transfer z by plaintext and model, key recovery."""
import json
import os

import numpy as np

from common import HERE

NAMES = ["sanskrit", "latin", "tamil", "sumerian"]


def main():
    with open(os.path.join(HERE, "stage5", "summary.json")) as f:
        s = json.load(f)
    out = {"true_key_separation_sd": {}, "transfer_z": {}, "recovery": {}}
    for p in NAMES:
        d = s["plaintexts"][p]
        out["true_key_separation_sd"][p] = (d["true_key_G"] - d["permuted_true_key"]["mean"]) / d["permuted_true_key"]["sd"]
        row = {}
        for m in NAMES:
            rs = [r for r in s["runs"] if r["plaintext"] == p and r["model"] == m and r["label"] == "fitA"]
            nb = s["nulls"][f"{p}|{m}"]
            b = float(np.mean([r["eval_B"] for r in rs]))
            row[m] = {"fitA_on_B_mean": b, "null_B_mean": nb["mean_B"], "null_B_sd": nb["sd_B"],
                      "z": (b - nb["mean_B"]) / nb["sd_B"],
                      "per_run_z": [(r["eval_B"] - nb["mean_B"]) / nb["sd_B"] for r in rs]}
        out["transfer_z"][p] = row
        out["recovery"][p] = [{"G_fit": r["G_fit"], "token_recovery": r["token_recovery"],
                               "type_recovery": r["type_recovery"]}
                              for r in s["runs"] if r["plaintext"] == p and r["label"] == "fit_all_recovery"]
    with open(os.path.join(HERE, "stage3g", "derived.json")) as f:
        g = json.load(f)
    out["real_ivs_transfer_z"] = {m: g[m]["transfer_z"] for m in NAMES}
    with open(os.path.join(HERE, "stage5", "derived.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"sep": out["true_key_separation_sd"],
                      "z": {p: {m: round(v["z"], 1) for m, v in row.items()} for p, row in out["transfer_z"].items()},
                      "real": out["real_ivs_transfer_z"]}, indent=1))


if __name__ == "__main__":
    main()
