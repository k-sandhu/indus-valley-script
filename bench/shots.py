"""Create closure-preserving splits, freeze a shared round and audit confirmation reads."""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from .common import (ROOT, SHOT_SOURCE, digest, envelope, legacy, read_json,
                     read_rows, sha256, strict_json, write_json)

LEDGER = ROOT / "bench/spent.json"
DEFAULT_SEED = "2026-10-13-bench-round-1"


def family_name(name):
    name = name.strip().lower().replace("-", "_").replace(" ", "_")
    return {"size": "seal_size", "seal_area": "seal_size", "animal": "motif",
            "findspot": "site", "sites": "site"}.get(name, name)


@contextmanager
def locked(path):
    lock = Path(str(path) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def update_json(path, value):
    """Atomic state update under the caller's ledger lock."""
    path = Path(path)
    tmp = Path(str(path) + ".pending")
    with tmp.open("x", encoding="utf-8") as f:
        json.dump(strict_json(value), f, indent=2, allow_nan=False)
        f.write("\n")
    os.replace(tmp, path)


def assignment(rows, seed):
    source = legacy(SHOT_SOURCE + "/shots_common.py")
    old = source.SEED
    try:
        source.SEED = seed
        return source.components(rows)
    finally:
        source.SEED = old


def summary(rows, comp):
    sizes = Counter(v["component"] for v in comp.values())
    return {"faces": len(rows), "families_by_half": dict(Counter(v["half"] for v in comp.values())),
            "components": len(sizes), "largest_components_families": sorted(sizes.values(), reverse=True)[:10]}


def create(input_path, split_path, seed=DEFAULT_SEED, ledger_path=LEDGER, synthetic=False):
    rows = read_rows(input_path)
    comp = assignment(rows, seed)
    if len(set(v["half"] for v in comp.values())) != 2:
        raise ValueError("Split needs both nonempty halves")
    identifier = digest([seed, sha256(input_path)])
    ledger_path, split_path = Path(ledger_path), Path(split_path)
    with locked(ledger_path):
        ledger = read_json(ledger_path) if ledger_path.exists() else {"schema_version": "1.0", "splits": {}}
        if identifier in ledger["splits"]:
            raise ValueError("This seed/input split already exists in the spending ledger")
        inherited = set()
        for prior in ledger["splits"].values():
            if prior["input_sha256"] == sha256(input_path):
                inherited.update(prior["spent_families"])
        state = {"schema_version": "1.0", "split_id": identifier, "seed": seed,
                 "input_path": str(Path(input_path).resolve()), "input_sha256": sha256(input_path),
                 "assignment_sha256": digest(comp), "summary": summary(rows, comp),
                 "synthetic": synthetic, "shots": {}, "opened": False,
                 "inherited_spent_families": sorted(inherited),
                 "freshness": "generated independent population" if synthetic else "requires independent population/source review"}
        write_json(split_path, state)
        ledger["splits"][identifier] = {"seed": seed, "input_sha256": state["input_sha256"],
                                         "assignment_sha256": state["assignment_sha256"],
                                         "spent_families": sorted(inherited), "reads": [], "synthetic": synthetic}
        update_json(ledger_path, ledger)
    return state


def register(split_path, shot, predictions_path, ledger_path=LEDGER):
    with locked(ledger_path):
        state = read_json(split_path)
        if state["opened"] or shot in state["shots"]:
            raise ValueError("Register every shot once, before any confirmation read")
        state["shots"][shot] = {"predictions_path": str(Path(predictions_path).resolve()), "frozen": None}
        update_json(split_path, state)
    return {"shot": shot, "registered": True}


def freeze(split_path, shot, artifacts=(), ledger_path=LEDGER):
    with locked(ledger_path):
        state = read_json(split_path)
        item = state["shots"][shot]
        if state["opened"] or item["frozen"]:
            raise ValueError("Frozen predictions cannot be replaced")
        path = Path(item["predictions_path"])
        obj = read_json(path)
        families = sorted(set(family_name(f) for f in obj["statistic_families"]))
        if not families or not obj["predictions"]:
            raise ValueError("Declare statistic families and predictions before freezing")
        for p in obj["predictions"]:
            if not all(p.get(k) for k in ("statistic", "null", "pass_rule")):
                raise ValueError("Every frozen prediction requires statistic, null and pass_rule")
        item["frozen"] = {"predictions_sha256": sha256(path), "statistic_families": families,
                          "joint_credence_rule": obj.get("joint_credence_rule"),
                          "withhold_site": bool(obj.get("withhold_site")),
                          "artifacts": {str(Path(p).resolve()): sha256(p) for p in artifacts},
                          "utc": datetime.now(timezone.utc).isoformat()}
        update_json(split_path, state)
    return {"shot": shot, "frozen": item["frozen"]}


def audit(split_path, entry):
    path = Path(split_path).with_suffix(".access.jsonl")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(strict_json(entry), allow_nan=False) + "\n")


def load_half(split_path, half, shot=None, ledger_path=LEDGER, allow_spent=False):
    """Return rows in memory. CLI emits only counts. Every successful or denied read is logged."""
    with locked(ledger_path):
        state = read_json(split_path)
        entry = {"utc": datetime.now(timezone.utc).isoformat(), "split_id": state["split_id"],
                 "half": half, "shot": shot, "allowed": False}
        try:
            if half not in ("discovery", "confirmation"):
                raise ValueError("half must be discovery or confirmation")
            if sha256(state["input_path"]) != state["input_sha256"]:
                raise ValueError("Input changed after the split was recorded")
            if half == "confirmation":
                if shot not in state["shots"]:
                    raise ValueError("Confirmation requires a registered shot")
                if not all(s["frozen"] for s in state["shots"].values()):
                    raise ValueError("Every shot sharing this round must freeze before any reads confirmation")
                for item in state["shots"].values():
                    f = item["frozen"]
                    if sha256(item["predictions_path"]) != f["predictions_sha256"]:
                        raise ValueError("Predictions changed after freezing")
                    if any(sha256(p) != h for p, h in f["artifacts"].items()):
                        raise ValueError("A frozen map, model or scoring artifact changed")
                if len(state["shots"]) > 1:
                    rules = [s["frozen"]["joint_credence_rule"] for s in state["shots"].values()]
                    if not all(rules) or len(set(rules)) != 1:
                        raise ValueError("Shared objects require the same nonempty joint credence rule")
                families = sorted({f for s in state["shots"].values() for f in s["frozen"]["statistic_families"]})
                reused = sorted(set(families) & set(state["inherited_spent_families"]))
                if reused and not allow_spent:
                    raise ValueError("Statistic families already spent on this input: " + ", ".join(reused))
                entry.update({"predictions_sha256": state["shots"][shot]["frozen"]["predictions_sha256"],
                              "statistic_families": families, "reused_families": reused,
                              "fresh_claim_allowed": state["synthetic"] and not reused})
            rows = read_rows(state["input_path"])
            comp = assignment(rows, state["seed"])
            if digest(comp) != state["assignment_sha256"]:
                raise ValueError("Closure or assignment changed")
            out = [dict(r, half=half, component=comp[r["object_family_id"]]["component"])
                   for r in rows if comp[r["object_family_id"]]["half"] == half]
            withheld = state["shots"].get(shot, {}).get("frozen") or {}
            # During exploration use the declaration too, before its freeze.
            if shot in state["shots"] and not withheld:
                withheld = read_json(state["shots"][shot]["predictions_path"])
            if withheld.get("withhold_site"):
                for i, r in enumerate(out):
                    blocked = {"region", "source_cisi", "cisi", "record_id", "object_family_id", "record_order",
                               "source_row", "source_index", "excavation-idno", "area-section", "block-house", "room-grid"}
                    if half == "discovery":
                        blocked.add("site")
                    r["metadata"] = {k: v for k, v in r.get("metadata", {}).items() if k not in blocked}
                    for k in blocked:
                        r.pop(k, None)
                    r["component"] = digest([state["split_id"], r["component"]])
                    r["id"] = digest([state["split_id"], half, i])
            if half == "confirmation":
                ledger = read_json(ledger_path)
                record = ledger["splits"][state["split_id"]]
                record["spent_families"] = sorted(set(record["spent_families"]) | set(entry["statistic_families"]))
                record["reads"].append(dict(entry, rows=len(out), allowed=True))
                update_json(ledger_path, ledger)
                state["opened"] = True
                update_json(split_path, state)
            entry.update(allowed=True, rows=len(out))
            audit(split_path, entry)
            return out, entry
        except (ValueError, KeyError, FileNotFoundError) as error:
            entry["reason"] = str(error)
            audit(split_path, entry)
            raise


def synthetic_rows():
    rows = []
    for i in range(60):
        signs = [f"S{i % 12}", f"S{(i * 7 + 2) % 31}", f"S{(i * 11 + 1) % 37}"]
        rows.append({"object_family_id": f"F{i}", "source_cisi": f"M-{i}", "record_id": str(i),
                     "complete_observed": True, "has_unknown_sign": False, "length": 3,
                     "signs_reading_rtl": signs, "object_type": "SEAL:S", "site": "Synthetic",
                     "metadata": {"site": "Synthetic", "record_order": i}})
    rows.append(dict(rows[0], object_family_id="AliasF0", record_id="alias"))
    rows.append(dict(rows[1], object_family_id="CopyF1", record_id="copy", source_cisi="Other"))
    return rows


def synthetic_check(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    inp, split, ledger = directory / "objects.json", directory / "split.json", directory / "spent.json"
    write_json(inp, synthetic_rows())
    state = create(inp, split, ledger_path=ledger, synthetic=True)
    prediction = {"statistic_families": ["size"], "joint_credence_rule": "One joint update for the round",
                  "withhold_site": True, "predictions": [{"statistic": "rank difference", "null": "within-band permutations", "pass_rule": "p <= .05"}]}
    paths = [directory / "shot-a.json", directory / "shot-b.json"]
    for shot, path in zip(("a", "b"), paths):
        write_json(path, prediction)
        register(split, shot, path, ledger)
    freeze(split, "a", ledger_path=ledger)
    denied = False
    try:
        load_half(split, "confirmation", "a", ledger)
    except ValueError:
        denied = True
    freeze(split, "b", ledger_path=ledger)
    discovery, _ = load_half(split, "discovery", "a", ledger)
    rows, access = load_half(split, "confirmation", "a", ledger)
    original = paths[0].read_text(encoding="utf-8")
    paths[0].write_text(original + " ", encoding="utf-8")
    tamper_denied = False
    try:
        load_half(split, "confirmation", "a", ledger)
    except ValueError:
        tamper_denied = True
    paths[0].write_text(original, encoding="utf-8")
    comps = assignment(synthetic_rows(), DEFAULT_SEED)
    closure = comps["F0"] == comps["AliasF0"] and comps["F1"] == comps["CopyF1"]
    disjoint = not ({r["component"] for r in discovery} & {r["component"] for r in rows})
    stripped = (all("source_cisi" not in r and "record_id" not in r for r in discovery + rows)
                and all("site" not in r for r in discovery) and all("site" in r for r in rows))
    spent = read_json(ledger)["splits"][state["split_id"]]["spent_families"] == ["seal_size"]
    new_split = directory / "second-seed-split.json"
    create(inp, new_split, DEFAULT_SEED + "-second", ledger, synthetic=True)
    register(new_split, "a", paths[0], ledger)
    freeze(new_split, "a", ledger_path=ledger)
    reuse_denied = False
    try:
        load_half(new_split, "confirmation", "a", ledger)
    except ValueError:
        reuse_denied = True
    _, reuse = load_half(new_split, "confirmation", "a", ledger, allow_spent=True)
    template = synthetic_rows()[0]
    closure_rows = [dict(template, object_family_id="T1", source_cisi="t1", length=2, object_type="TAB:I", signs_reading_rtl=["a", "b"]),
                    dict(template, object_family_id="T2", source_cisi="t2", length=2, object_type="TAB:I", signs_reading_rtl=["a", "b"]),
                    dict(template, object_family_id="S1", source_cisi="s1", length=2, signs_reading_rtl=["a", "b"]),
                    dict(template, object_family_id="S2", source_cisi="s2", length=2, signs_reading_rtl=["a", "b"])]
    special = assignment(closure_rows, DEFAULT_SEED)
    short_rule = special["T1"]["component"] != special["T2"]["component"] and special["S1"] == special["S2"]
    return {"summary": state["summary"], "all_shots_freeze_guard": denied, "tamper_guard": tamper_denied,
            "closure": closure, "halves_disjoint": disjoint, "site_proxies_stripped_and_confirmation_site_available": stripped,
            "spending_recorded": spent, "spent_input_rejected_after_new_seed": reuse_denied,
            "explicit_reuse_is_exploratory": not reuse["fresh_claim_allowed"], "short_tablet_exception": short_rule, "read": access,
            "pass": all((denied, tamper_denied, closure, disjoint, stripped, spent, reuse_denied, not reuse["fresh_claim_allowed"], short_rule))}


def configure(ap):
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--action", choices=("create", "register", "freeze", "load", "inspect"), default="create")
    ap.add_argument("--input", type=Path, default=ROOT / "data/normalized/lipi_observed_faces.jsonl")
    ap.add_argument("--split", type=Path)
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    ap.add_argument("--seed", default=DEFAULT_SEED)
    ap.add_argument("--shot")
    ap.add_argument("--predictions", type=Path)
    ap.add_argument("--artifact", action="append", type=Path, default=[])
    ap.add_argument("--half", choices=("discovery", "confirmation"), default="discovery")
    ap.add_argument("--allow-spent", action="store_true", help="Explicit exploratory/reproduction access; freshness remains false")
    ap.add_argument("--directory", type=Path, help="New directory for synthetic loader fixtures")


def run(args):
    if args.synthetic:
        if args.directory:
            result = synthetic_check(args.directory)
        else:
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                result = synthetic_check(Path(tmp) / "shots")
        return envelope("shots", result, True, [SHOT_SOURCE + "/shots_common.py", SHOT_SOURCE + "/REVIEW-RESPONSE.md"])
    if not args.split:
        raise ValueError("Supply --split")
    if args.action == "create":
        result = create(args.input, args.split, args.seed, args.ledger)
    elif args.action == "register":
        if not args.shot or not args.predictions:
            raise ValueError("Registration requires --shot and --predictions")
        result = register(args.split, args.shot, args.predictions, args.ledger)
    elif args.action == "freeze":
        result = freeze(args.split, args.shot, args.artifact, args.ledger)
    elif args.action == "load":
        rows, event = load_half(args.split, args.half, args.shot, args.ledger, args.allow_spent)
        result = {"rows": len(rows), "access": event}
    else:
        result = read_json(args.split)
    return envelope("shots", result, paths=[SHOT_SOURCE + "/shots_common.py", SHOT_SOURCE + "/REVIEW-RESPONSE.md"])
