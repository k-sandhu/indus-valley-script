"""Audit typed chronology routes and enumerate an explicitly invented narrative rewrite."""
from pathlib import Path
from itertools import permutations, product
from collections import Counter
import argparse
import hashlib
import json

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]
OPERATIONS = ("store_grain", "define_shares", "censure_taking", "delegate_enforcement")
BASE_EDGES = tuple(zip(OPERATIONS[:-1], OPERATIONS[1:]))
REVISED_EDGES = (("store_grain", "define_shares"), ("define_shares", "delegate_enforcement"), ("delegate_enforcement", "censure_taking"))
ROUTES = ("local_transmission", "acquisition_from_neighbors", "reconstruction_from_current_practice", "recent_invention")
DEPTHS = (1, 5, 20, 100)  # invented generations, with no calendar calibration
GAPS = (1, 2, 9)  # invented time units between operations, with no historical frequency
AGENTS = ("invented_actor_A", "invented_actor_B", "invented_actor_C", "invented_actor_D")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def calendar_edge_allowed(edge, nodes):
    """A witness may attest its own text's presence; none of these records dates first composition."""
    return (edge["status"] == "supported"
            and edge["kind"] == "attests_own_text_by_witness_date"
            and edge.get("same_text") is True
            and nodes[edge["from"]]["kind"] in {"manuscript_witness", "modern_digital_witness"}
            and nodes[edge["to"]]["kind"] == "text_presence_bound")


def route_audit(graph):
    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = {(edge["from"], edge["to"]): edge for edge in graph["edges"]}
    rows = []
    for route in graph["routes_to_challenge"] + graph["valid_controls"]:
        traversed = [edges[(a, b)] for a, b in zip(route[:-1], route[1:])]
        rows.append({"route": route, "calendar_bound_allowed": all(calendar_edge_allowed(e, nodes) for e in traversed),
                     "edge_checks": [{"from": e["from"], "to": e["to"], "kind": e["kind"],
                                      "allowed": calendar_edge_allowed(e, nodes)} for e in traversed]})
    return {"node_count": len(nodes), "edge_count": len(edges), "challenged_routes": len(graph["routes_to_challenge"]),
            "blocked_challenged_routes": sum(not row["calendar_bound_allowed"] for row in rows[:len(graph["routes_to_challenge"])]),
            "accepted_presence_controls": sum(row["calendar_bound_allowed"] for row in rows[len(graph["routes_to_challenge"]):]),
            "composition_nodes_with_propagated_absolute_bounds": 0,
            "routes": rows,
            "scope": "A formal safeguard on our claim graph, not evidence that a particular story is young or old"}


def operation_order(edges):
    pending = set(OPERATIONS)
    result = []
    while pending:
        ready = sorted(n for n in pending if all(a not in pending for a, b in edges if b == n))
        if len(ready) != 1:
            raise ValueError("This invented example requires an acyclic chain with a unique operation order")
        result.extend(ready)
        pending.remove(ready[0])
    return tuple(result)


def account(history, keep=(), edges=BASE_EDGES):
    """Declared origin rewrite keeps the operation order and replaces historical attribution."""
    base = ("primordial_community", "grain", operation_order(edges))
    annotations = tuple((k, history[k]) for k in keep)
    return base + annotations


def compression_demo():
    counters = {name: Counter() for name in ("operation_only", "route_retained", "time_retained", "agents_retained", "all_annotations_retained")}
    keep = {"operation_only": (), "route_retained": ("route",), "time_retained": ("depth", "gaps"),
            "agents_retained": ("agents",), "all_annotations_retained": ("route", "depth", "gaps", "agents")}
    examples = {}
    n = 0
    for route, depth, agents, gaps in product(ROUTES, DEPTHS, permutations(AGENTS), product(GAPS, repeat=3)):
        history = {"route": route, "depth": depth, "agents": agents, "gaps": gaps}
        n += 1
        for name in counters:
            counters[name][account(history, keep[name])] += 1
        selected_depth = 100 if route == "local_transmission" else 1
        if route not in examples and depth == selected_depth:
            examples[route] = {"history": history, "account": account(history)}
    distributions = {name: {"distinct_outputs": len(counts), "preimage_sizes": dict(sorted(Counter(counts.values()).items()))}
                     for name, counts in counters.items()}
    control_history = {"route": ROUTES[-1], "depth": 1, "agents": AGENTS, "gaps": (1, 1, 1)}
    return {"status": "Explicitly synthetic logical construction; no historical frequency or probability",
            "input_space": {"routes": list(ROUTES), "depths_in_invented_generations": list(DEPTHS),
                            "distinct_agent_assignments": 24, "three_gap_assignments": 27, "gap_units": list(GAPS),
                            "historical_calibration": None},
            "history_count": n, "retention_variants": distributions,
            "account_description": "A primordial community stores grain, defines shares, censures taking and delegates enforcement, in the retained dependency order. Named actors, times and acquisition route are omitted by the declared rewrite.",
            "examples": list(examples.values()),
            "structural_positive_control": {"base_edges": BASE_EDGES, "revised_edges": REVISED_EDGES,
                                             "base_account": account(control_history), "revised_account": account(control_history, edges=REVISED_EDGES),
                                             "distinguished": account(control_history) != account(control_history, edges=REVISED_EDGES)},
            "interpretation": "A coherent operation account cannot identify its route or depth after those annotations are erased; retaining a genuine independent annotation or changing a retained relation can separate outputs. The erasure rule was stipulated, not inferred from ancient texts."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="run-v1")
    args = parser.parse_args()
    if Path(args.out).name != args.out:
        raise ValueError("Use one fresh output directory name")
    out = OWN / args.out
    out.mkdir(exist_ok=False)
    graph = json.loads((OWN / "claim-graph.json").read_text(encoding="utf-8"))
    ledger = json.loads((OWN / "sources.json").read_text(encoding="utf-8"))
    observations = json.loads((OWN / "observations.json").read_text(encoding="utf-8"))
    graph_result = route_audit(graph)
    demo = compression_demo()
    write(out / "graph-audit.json", graph_result)
    write(out / "compression-demo.json", demo)
    summary = {"sources": len(ledger["sources"]), "observations": len(observations["observations"]),
               "historical_routes_identified": [], "graph": {k: v for k, v in graph_result.items() if k != "routes"},
               "synthetic_histories": demo["history_count"], "synthetic_outputs": demo["retention_variants"],
               "input_sha256": {name: digest(OWN / name) for name in ("PROTOCOL.md", "sources.json", "observations.json", "claim-graph.json", "source-checks.json", "analyze.py")},
               "raw_witness_counts_are_not_independent_ancient_evidence": True}
    write(out / "summary.json", summary)
    print(json.dumps({"out": out.relative_to(ROOT).as_posix(), "nodes": graph_result["node_count"], "edges": graph_result["edge_count"],
                      "blocked_routes": graph_result["blocked_challenged_routes"], "valid_presence_controls": graph_result["accepted_presence_controls"],
                      "synthetic_histories": demo["history_count"], "synthetic_account_outputs": demo["retention_variants"]["operation_only"]["distinct_outputs"]}))


if __name__ == "__main__":
    main()
