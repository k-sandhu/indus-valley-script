"""Independently recount selected-ledger restrictions and a synthetic projection.

The author's algorithms are not imported. Manually inspected source-table
percentages are independent pins, and input hashes identify the frozen endpoints.
The checks validate those declared operations, not historical transmission.
"""
from collections import Counter
from decimal import Decimal as D
from itertools import permutations, product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
CHECKS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(name, passed, **detail):
    CHECKS.append({"id": name, "pass": bool(passed), **detail})


def institutions():
    base = PACKAGE / "institutions"
    saved = read(base / "run-v2/audit.json")
    sources = read(base / "sources.json")
    observations = read(base / "observations.json")
    claims = read(base / "claims.json")
    for name, expected in saved["input_hashes"].items():
        check("institution-input-" + name, digest(base / name) == expected)
    check("institution-source-count", len(sources) == saved["counts"]["sources"] == 14)
    check("institution-observation-count", len(observations) == saved["counts"]["observations"] == 30)
    check("institution-claim-count", len(claims) == saved["counts"]["claims"] == 7)
    witnesses = [w for s in sources for w in s["witnesses"]]
    check("institution-witness-count", len(witnesses) == saved["counts"]["witnesses_verified"] == 31)
    for index, witness in enumerate(witnesses):
        path = ROOT / witness["path"]
        check(f"institution-witness-{index}", path.exists() and path.stat().st_size == witness["bytes"]
              and digest(path) == witness["sha256"], path=witness["path"])
    O = {o["id"]: o for o in observations}
    H = [c for c in claims if c["kind"] == "transmission_hypothesis"]
    later = {"rv_family_late_addition", "rv_later_book", "brahmana", "buddhist"}
    text_types = {"rv_family_unflagged", "rv_family_late_addition", "rv_later_book", "brahmana", "buddhist"}
    policies = [
        (set(), False, False),
        (later, False, False),
        (later | {"rv_family_unflagged"}, False, False),
        (set(), True, False),
        (set(), True, True),
    ]
    recounted = []
    for index, (excluded, needs_intermediate, needs_diagnostic) in enumerate(policies):
        retained = {o["id"] for o in observations if o["evidence_type"] not in excluded}
        texts = {i for i in retained if O[i]["evidence_type"] in text_types}
        eligible = []
        for hypothesis in H:
            cited_text = any(i in texts for i in hypothesis["observation_ids"])
            intermediate = any(i in retained for i in hypothesis["intermediate_archaeological_ids"])
            diagnostic = hypothesis["diagnostic_feature_crosses_text_archaeology"]
            if cited_text and (not needs_intermediate or intermediate) and (not needs_diagnostic or diagnostic):
                eligible.append(hypothesis["id"])
        components = sorted({O[i]["component"] for i in texts})
        row = dict(observations_retained=len(retained), textual_observations_retained=len(texts),
                   represented_text_components=components,
                   candidate_hypotheses_passing_declared_requirements=eligible)
        recounted.append(row)
        for key, value in row.items():
            check(f"institution-policy-{index}-{key}", value == saved["sensitivity"][index][key], observed=value)
    check("institution-no-text-no-eligibility", recounted[2]["textual_observations_retained"] == 0
          and recounted[2]["candidate_hypotheses_passing_declared_requirements"] == [])
    check("institution-five-hypotheses-have-no-diagnostic", all(not h["diagnostic_feature_crosses_text_archaeology"] for h in H))
    # Manual pins from the accepted manuscript, PDF pp. 13–14, Tables 2–4.
    published = [
        ["75.84", "9.55", "14.61", "0.00"],
        ["0.00", "28.57", "42.86", "28.57"],
        ["39.46", "9.99", "4.51", "46.03"],
        ["6.92", "33.15", "0.00", "59.93"],
    ]
    cells = [
        [[135], [17], [26], [0]],
        [[0], [2], [3], [2]],
        [[.5, 0, 1, 29.5, 4, 118], [.75, 1.5, .5, 23.5, .5, 12],
         [0, .5, 0, 4.5, 0, 12.5], [1, 4, 0, 19.5, 2.5, 151.5]],
        [[0, 2.22, 0, 0, 0, 0], [1.33, 2.22, 0, 2.67, 2.4, 2],
         [0, 0, 0, 0, 0, 0], [1.33, 11.11, 3, 1.33, 2.4, 0]],
    ]
    bounds = []
    for index, (pinned, table) in enumerate(zip(published, cells)):
        row = saved["rice_classification_sensitivity"]["bounds"][index]
        values = list(map(D, pinned))
        lower, upper = values[1], values[1] + values[3]
        bounds.append((lower, upper))
        for key, value in zip(("wild", "domesticated", "immature", "uncertain"), values):
            check(f"rice-source-{index}-{key}", D(str(row[key])) == value)
        check(f"rice-lower-{index}", D(str(row["domesticated_lower"])) == lower)
        check(f"rice-upper-{index}", D(str(row["domesticated_upper"])) == upper)
        # The density cells are rounded too. Agreement is checked only to 0.1
        # percentage point, without replacing the frozen published percentages.
        totals = [sum(D(str(x)) for x in group) for group in table]
        density_percentages = [100 * x / sum(totals) for x in totals]
        check(f"rice-rounded-density-plausibility-{index}",
              all(abs(a - b) < D(".1") for a, b in zip(values, density_percentages)),
              displayed_density_percentage=[str(x) for x in density_percentages])
    rice = saved["rice_classification_sensitivity"]
    check("rice-within-site-direction", bounds[1][0] > bounds[0][1]
          and rice["masudpur_VII_late_exceeds_mature_for_all_uncertain_assignments"] is True)
    check("rice-between-sites-overlap", bounds[3][0] <= bounds[2][1]
          and rice["masudpur_I_vs_bahola_order_guaranteed"] is False)
    check("rice-within-site-two-contexts", [row["contexts"] for row in rice["bounds"][:2]] == [1, 1]
          and rice["within_site_comparison_survives_removal_of_either_Masudpur_VII_context"] is False)
    check("rice-pgw-exclusion", O["A06"]["values"]["pgw_spikelet_contexts_retained"] == 0
          and rice["pgw_domestication_endpoint_available"] is False)
    return dict(endpoint="institutions/run-v2/audit.json", endpoint_sha256=digest(base / "run-v2/audit.json"),
                recount=recounted, source_table_bounds=[[str(x) for x in pair] for pair in bounds],
                scope="Categorical restrictions on a selected ledger and classification bounds on published rounded percentages")


def memory():
    base = PACKAGE / "memory"
    saved = read(base / "run-v1/summary.json")
    graph = read(base / "claim-graph.json")
    audited = read(base / "run-v1/graph-audit.json")
    demo = read(base / "run-v1/compression-demo.json")
    for name, expected in saved["input_sha256"].items():
        check("memory-input-" + name, digest(base / name) == expected)
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = {(e["from"], e["to"]): e for e in graph["edges"]}
    check("memory-unique-nodes", len(nodes) == len(graph["nodes"]))
    check("memory-unique-edges", len(edges) == len(graph["edges"]))
    check("memory-endpoints-defined", all(a in nodes and b in nodes for a, b in edges))
    check("memory-node-count", len(nodes) == audited["node_count"] == 16)
    check("memory-edge-count", len(edges) == audited["edge_count"] == 11)
    observations = read(base / "observations.json")["observations"]
    obs_ids = {o["id"] for o in observations}
    for n in nodes.values():
        for candidate in [n.get("observation"), n.get("date", {}).get("observation")]:
            if candidate is not None:
                check("memory-node-observation-" + n["id"], candidate in obs_ids)
    def allowed(e):
        return (e["status"] == "supported" and e["kind"] == "attests_own_text_by_witness_date"
                and e.get("same_text") is True
                and nodes[e["from"]]["kind"] in {"manuscript_witness", "modern_digital_witness"}
                and nodes[e["to"]]["kind"] == "text_presence_bound")
    challenge_count = len(graph["routes_to_challenge"])
    rows = []
    for index, route in enumerate(graph["routes_to_challenge"] + graph["valid_controls"]):
        verdict = all(allowed(edges[pair]) for pair in zip(route[:-1], route[1:]))
        rows.append(verdict)
        check(f"memory-route-{index}", verdict == audited["routes"][index]["calendar_bound_allowed"], route=route)
    check("memory-challenged-routes-blocked", not any(rows[:challenge_count])
          and audited["blocked_challenged_routes"] == challenge_count == 10)
    check("memory-presence-controls", all(rows[challenge_count:]) and audited["accepted_presence_controls"] == 2)
    check("memory-composition-nodes-undated", all(n.get("absolute_date") is None
          for n in nodes.values() if n["kind"] == "text_composition"))
    # Enumerate from the saved declared finite space, projecting selected fields.
    # No author account/operation_order function is used.
    space = demo["input_space"]
    routes, depths, gaps = space["routes"], space["depths_in_invented_generations"], space["gap_units"]
    agent_ids = tuple(demo["examples"][0]["history"]["agents"])
    counters = {name: Counter() for name in demo["retention_variants"]}
    histories = []
    for route in routes:
        for depth in depths:
            for actors in permutations(agent_ids):
                for intervals in product(gaps, repeat=3):
                    histories.append((route, depth, actors, intervals))
                    counters["operation_only"][()] += 1
                    counters["route_retained"][(route,)] += 1
                    counters["time_retained"][(depth, intervals)] += 1
                    counters["agents_retained"][(actors,)] += 1
                    counters["all_annotations_retained"][(route, depth, actors, intervals)] += 1
    check("memory-finite-input-cardinality", len(histories) == demo["history_count"] == 10368
          and len(set(histories)) == len(histories))
    independent = {}
    for name, counts in counters.items():
        sizes = {str(k): v for k, v in sorted(Counter(counts.values()).items())}
        independent[name] = dict(distinct_outputs=len(counts), preimage_sizes=sizes)
        check("memory-projection-" + name, independent[name] == demo["retention_variants"][name])
        check("memory-projection-total-" + name, sum(int(k) * v for k, v in sizes.items()) == len(histories))
    check("memory-examples-identical-accounts", all(e["account"] == demo["examples"][0]["account"] for e in demo["examples"]))
    check("memory-examples-cover-four-routes", set(e["history"]["route"] for e in demo["examples"]) == set(routes))
    control = demo["structural_positive_control"]
    orders = list(permutations(control["base_account"][2]))
    valid_orders = []
    for edge_key in ["base_edges", "revised_edges"]:
        valid = [order for order in orders if all(order.index(a) < order.index(b) for a, b in control[edge_key])]
        valid_orders.append(valid)
        check("memory-unique-order-" + edge_key, len(valid) == 1)
    check("memory-structural-positive-control", list(valid_orders[0][0]) == control["base_account"][2]
          and list(valid_orders[1][0]) == control["revised_account"][2]
          and valid_orders[0] != valid_orders[1] and control["distinguished"] is True)
    return dict(endpoint="memory/run-v1/summary.json", endpoint_sha256=digest(base / "run-v1/summary.json"),
                independently_enumerated_inputs=len(histories), projections=independent,
                scope="Declared date-axis gate and stipulated finite erasure projection; no empirical transmission frequency")


def main():
    out = HERE / "package-checks-v1.json"
    if out.exists():
        raise FileExistsError(out)
    institution_result = institutions()
    memory_result = memory()
    derivatives = []
    for n in [13, 14]:
        path = ROOT / f"data/raw/2026-10-11-early-indian-continuity/review/bates2017-rice-page-{n}.png"
        derivatives.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path),
                                parent_path="data/raw/2026-10-11-early-indian-continuity/institutions/bates2017-rice.pdf",
                                parent_sha256=digest(ROOT / "data/raw/2026-10-11-early-indian-continuity/institutions/bates2017-rice.pdf"),
                                pdf_page=n, scale=1.5, disposition="local-only"))
    result = dict(checker_sha256=digest(Path(__file__)), checks=CHECKS,
                  passed=sum(c["pass"] for c in CHECKS), failed=sum(not c["pass"] for c in CHECKS),
                  institutions=institution_result, memory=memory_result, source_derivatives=derivatives)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"]}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
