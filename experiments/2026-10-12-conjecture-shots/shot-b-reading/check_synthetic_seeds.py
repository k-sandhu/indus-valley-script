"""Calibration check of confirm.py on synthetic withheld fields with no planted effect.

Runs the full confirmation procedure (300 rearrangements each, for speed) on the
discovery half with random site, animal, size, period and material values drawn with
eight different seeds, and records the distance of the primary score S = z1 + z2 and the S3 correlation.
Writes discovery/synthetic_seed_check.json. No real withheld value is read.
"""
import contextlib
import io
import json

import numpy as np

import confirm

orig = np.random.default_rng
rows_out = []
for sd in range(11, 19):
    def fake(seed=None, _sd=sd):
        return orig(_sd if seed == 7 else seed)
    confirm.np.random.default_rng = fake
    rows = confirm.synthetic_rows()
    confirm.np.random.default_rng = orig
    confirm.N_PERM = 300
    tmp = confirm.SHOT / "discovery" / "_tmp_seedcheck.json"
    with contextlib.redirect_stdout(io.StringIO()):
        r = confirm.run(rows, tmp, f"seed {sd}")
    tmp.unlink()
    s3 = r["secondary"].get("S3_grade_numeral_size", {})
    rows_out.append({"synthetic_seed": sd, "primary_distance_sd": r["primary"]["distance_sd"],
                     "primary_pass": r["primary"]["pass"], "primary_percentile": r["primary"]["percentile_of_S"],
                     "component_z": {k: v.get("z") for k, v in r["components"].items()},
                     "S3_rho": s3.get("rho"), "S3_p_two_sided": s3.get("p_two_sided")})
(confirm.SHOT / "discovery" / "synthetic_seed_check.json").write_text(json.dumps(rows_out, indent=1), encoding="utf-8")
print(json.dumps([(x["synthetic_seed"], round(x["primary_distance_sd"], 2), round(x["S3_rho"] or 0, 2)) for x in rows_out]))
