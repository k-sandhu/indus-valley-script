"""Replace all unopened answers while preserving the planner's observations."""

from pathlib import Path
import copy
import importlib.util
import inspect
import json
import random


def main():
    root = Path("experiments/2026-10-02-six-hour/physical-acquisition")
    output = root / "selection-boundary-review.json"
    if output.exists(): raise FileExistsError(output)
    spec = importlib.util.spec_from_file_location("physical_acquisition_boundary", "src/six_hour/physical_acquisition.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert not {"world", "oracle", "answer", "truth", "withheld"}.intersection(inspect.signature(module.select_action).parameters)
    records = []
    for condition_index, condition in enumerate(module.CONDITIONS):
        world = module.make_world(930000 + condition_index, condition)
        altered = copy.deepcopy(world)
        altered["concealed_values"] = [101, 103, 107, 109, 113, 127]
        altered["oracle_responses"] = {key: {"poisoned_unopened_response": True} for key in world["oracle_responses"]}
        altered["withheld_relations"] = [{"poisoned_withheld_relation": True}]
        altered["withheld_counts"] = [{"poisoned_withheld_count": True}]
        for obj in altered["objects"]: obj["quantity"] = 99999
        assert world["public_actions"] == altered["public_actions"] and world["initial_observations"] == altered["initial_observations"]
        lp = module.CertifiedLP()
        state, model = module.analyze(lp, world["initial_observations"])
        for policy in module.POLICIES:
            choices = []
            for candidate in (world, altered):
                action, selection = module.select_action(policy, candidate["public_actions"], set(), 24,
                                                         candidate["initial_observations"], state, model, lp,
                                                         random.Random(811))
                choices.append((action["id"] if action else None, selection))
            assert choices[0] == choices[1]
            records.append({"condition": condition, "policy": policy, "choice": choices[0][0],
                            "choice_and_score_trace_unchanged": True, "unopened_oracle_and_answer_replaced": True})
    result = {"status": "passed", "metamorphic_cases": len(records), "records": records,
              "scope": "Planner boundary for five independent initial states and all three policies. Saved public-input hashes additionally cover every acquired action in the runs."}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "metamorphic_cases": len(records)}, indent=2))


if __name__ == "__main__": main()
