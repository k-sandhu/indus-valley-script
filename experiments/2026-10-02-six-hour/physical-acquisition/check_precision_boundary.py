"""Test the new interval branch while changing only unopened hidden records."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import copy
import importlib.util
import inspect
import json
import random


def main():
    root = Path(__file__).resolve().parent
    output = root / "precision-boundary-review.json"
    if output.exists():
        raise FileExistsError(output)
    source = Path("src/six_hour/physical_acquisition.py")
    spec = importlib.util.spec_from_file_location("precision_boundary", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert not {"world", "oracle", "answer", "truth", "withheld"}.intersection(inspect.signature(module.select_action).parameters)
    # A current coordinate range of width 1 can be trimmed by an interval of width 2.
    action = {"code": 0, "declared_radius": 1}
    model = {"absolute": True}
    state = {"coordinate_ranges": [["4", "5"]] * 6}
    assert module.count_score(model, state, action) == 0
    assert module.count_score(model, state, action, overlap=True) == F(1, 3)
    records = []
    for seed in range(940000, 940004):
        world = module.make_world(seed, "valid_intervals")
        available_count = next((a for a in world["public_actions"] if a["kind"] == "count" and a["available"]), None)
        assert available_count is not None
        states = [(list(world["initial_observations"]), set(), 24, "initial")]
        states.append((list(world["initial_observations"]) + [world["oracle_responses"][available_count["id"]]],
                       {available_count["id"]}, 24 - available_count["cost"], "after_one_count"))
        altered = copy.deepcopy(world)
        altered["concealed_values"] = [101, 103, 107, 109, 113, 127]
        altered["oracle_responses"] = {key: {"poisoned_unopened_response": True} for key in world["oracle_responses"]}
        altered["withheld_relations"] = [{"poisoned_withheld_relation": True}]
        altered["withheld_counts"] = [{"poisoned_withheld_count": True}]
        for obj in altered["objects"]:
            obj["quantity"] = 99999
        for observations, acquired, remaining, stage in states:
            lp = module.CertifiedLP()
            state, model = module.analyze(lp, observations)
            decisions = []
            for candidate in (world, altered):
                decision = module.select_action("information_overlap", candidate["public_actions"], acquired,
                                                remaining, observations, state, model, lp, random.Random(811))
                decisions.append(decision)
            assert decisions[0] == decisions[1]
            records.append({"seed": seed, "stage": stage,
                            "action": decisions[0][0]["id"] if decisions[0][0] else None,
                            "choice_and_score_trace_unchanged": True})
    result = {"status": "passed", "metamorphic_cases": len(records), "records": records,
              "width_one_radius_one_scores": {"original": "0", "refined": "1/3"},
              "code_sha256": sha256(source.read_bytes()).hexdigest(),
              "scope": "Initial and already-counted states in four new audit worlds; hidden unopened quantities, responses and withheld answers replaced."}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
