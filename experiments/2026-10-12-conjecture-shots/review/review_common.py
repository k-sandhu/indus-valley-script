"""Shared loaders for the adversarial review of the October 12 conjecture shots.

Exploratory review analysis, 13 October 2026. Both halves are already open. The
discovery half is read with shots_common.load_half("discovery"), which does not log.
The confirmation half is read directly from the pinned faces file and the local split,
so the shots' confirmation-access logs are not touched. Hashes are checked against
split-summary.json before either half is returned.
"""
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True  # do not leave caches in the shots' directories

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG / "shot-a-rank"))

import shots_common as SC  # noqa: E402
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402

RAW_REVIEW = ROOT / "data/raw/2026-10-12-conjecture-shots/review"
STATUS = "Exploratory review analysis, 13 October 2026 (both halves open; not a frozen test)"


def check_hashes():
    s = json.loads((PKG / "split-summary.json").read_text(encoding="utf-8"))
    ok = SC.sha256(SC.FACES) == s["faces_sha256"] and SC.sha256(SC.RAW / "split.json") == s["split_sha256"]
    if not ok:
        raise SystemExit("faces or split hash differs from split-summary.json")
    return {"faces_sha256": s["faces_sha256"], "split_sha256": s["split_sha256"]}


def load_discovery():
    return SC.load_half("discovery")


def load_confirmation_direct():
    """Confirmation faces with half and component, read without the logged loader."""
    check_hashes()
    split = SC.load_split()
    out = []
    for r in SC.read_faces():
        c = split[r["object_family_id"]]
        if c["half"] != "confirmation":
            continue
        out.append(dict(r, half=c["half"], component=c["component"]))
    return out


def load_all():
    check_hashes()
    split = SC.load_split()
    return [dict(r, half=split[r["object_family_id"]]["half"], component=split[r["object_family_id"]]["component"])
            for r in SC.read_faces()]


def write_json(name, obj):
    p = HERE / name
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    return p


def write_raw(name, obj):
    RAW_REVIEW.mkdir(parents=True, exist_ok=True)
    p = RAW_REVIEW / name
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    return p
