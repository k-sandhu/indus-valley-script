"""Independent finite-count/type/pin checks of the frozen documentary construction."""
from pathlib import Path
from itertools import permutations, product
from math import factorial
import hashlib
import json
import argparse

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="run-v1")
    parser.add_argument("--out", default="verification.json")
    args = parser.parse_args()
    if Path(args.run).name != args.run or Path(args.out).name != args.out:
        raise ValueError("Use local run/output names")
    out = OWN / args.out
    if out.exists():
        raise FileExistsError("Preserve frozen verification; choose another output")
    summary = json.loads((OWN / args.run / "summary.json").read_text(encoding="utf-8"))
    demo = json.loads((OWN / args.run / "compression-demo.json").read_text(encoding="utf-8"))
    audit = json.loads((OWN / args.run / "graph-audit.json").read_text(encoding="utf-8"))
    sources = json.loads((OWN / "sources.json").read_text(encoding="utf-8"))
    obs = json.loads((OWN / "observations.json").read_text(encoding="utf-8"))
    checks = []

    def test(name, actual, expected):
        checks.append({"name": name, "actual": actual, "expected": expected, "passed": actual == expected})

    for name, value in summary["input_sha256"].items():
        test("frozen input hash " + name, sha(OWN / name), value)
    for s in sources["sources"]:
        test("raw witness hash " + s["id"], sha(ROOT / s["witness_path"]), s["sha256"])
    ids = {s["id"] for s in sources["sources"]}
    test("unique source ids", len(ids), len(sources["sources"]))
    test("unique observation ids", len({o["id"] for o in obs["observations"]}), len(obs["observations"]))
    test("all observation sources exist", all(set(o["source_ids"]) <= ids for o in obs["observations"]), True)
    sourcechecks = json.loads((OWN / "source-checks.json").read_text(encoding="utf-8"))
    for c in sourcechecks["checks"]:
        path = ROOT / c["witness"]
        test("checked derivative hash " + c["observation"] + " " + path.name, sha(path), c["sha256"])
        if c["kind"].startswith("JSON segment"):
            content = json.loads(path.read_text(encoding="utf-8")); actual = [t in content for t in c["required_tokens"]]
        else:
            if "pdf_page" in c:
                content = json.loads(path.read_text(encoding="utf-8"))[c["pdf_page"]-1]["text"]
            else:
                content = path.read_text(encoding="utf-8")
            actual = [t.casefold() in content.casefold() for t in c["required_tokens"]]
        test("required tokens " + c["observation"] + " " + path.name, actual, [True] * len(c["required_tokens"]))
    graph = json.loads((OWN / "claim-graph.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = {(e["from"], e["to"]): e for e in graph["edges"]}
    test("reported graph nodes", audit["node_count"], len(nodes))
    test("reported graph edges", audit["edge_count"], len(edges))
    for row in audit["routes"]:
        edge_rows = [edges[(a, b)] for a, b in zip(row["route"][:-1], row["route"][1:])]
        valid = len(edge_rows) == 1 and all(e["status"] == "supported" and e.get("same_text") is True
                and e["kind"] == "attests_own_text_by_witness_date" for e in edge_rows)
        valid = valid and nodes[row["route"][-1]]["kind"] == "text_presence_bound"
        test("independent route " + ">".join(row["route"]), row["calendar_bound_allowed"], valid)
    test("no composition bound propagated", all(nodes[r["route"][-1]]["kind"] != "text_composition" for r in audit["routes"] if r["calendar_bound_allowed"]), True)
    test("10 unsupported routes blocked", audit["blocked_challenged_routes"], 10)
    test("2 genuine presence controls allowed", audit["accepted_presence_controls"], 2)
    expected_size = 4 * 4 * factorial(4) * 3 ** 3
    test("analytic invented input-space size", demo["history_count"], expected_size)
    # Independent enumeration of annotation partitions, without importing the rewrite implementation.
    worlds = list(product(range(4), range(4), permutations(range(4)), product(range(3), repeat=3)))
    test("independently enumerated invented input-space size", len(worlds), expected_size)
    partitions = {"operation_only": lambda w: (), "route_retained": lambda w: (w[0],),
                  "time_retained": lambda w: (w[1], w[3]), "agents_retained": lambda w: (w[2],),
                  "all_annotations_retained": lambda w: w}
    for name, key in partitions.items():
        sizes = {}
        for world in worlds:
            k = key(world); sizes[k] = sizes.get(k, 0) + 1
        actual = demo["retention_variants"][name]
        test("distinct outputs " + name, actual["distinct_outputs"], len(sizes))
        expected = {}
        for n in sizes.values():
            expected[str(n)] = expected.get(str(n), 0) + 1
        test("preimage distribution " + name, actual["preimage_sizes"], expected)
    examples = demo["examples"]
    test("long-local and recent-invention constructive equivalence", len({json.dumps(e["account"], sort_keys=True) for e in examples}), 1)
    test("all declared route labels represented", len({e["history"]["route"] for e in examples}), 4)
    test("constructive depths differ", sorted({e["history"]["depth"] for e in examples}), [1, 100])
    test("retained structural change distinguished", demo["structural_positive_control"]["base_account"] != demo["structural_positive_control"]["revised_account"], True)
    payload = {"status": "pass" if all(c["passed"] for c in checks) else "fail", "check_count": len(checks), "checks": checks,
               "scope": "Pin/locus/finite-count/type checks; semantic interpretation remains subject to source and adversarial review",
               "run": args.run, "summary_sha256": sha(OWN / args.run / "summary.json"), "verify_code_sha256": sha(Path(__file__))}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "failed": [c["name"] for c in checks if not c["passed"]]}))
    if payload["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
