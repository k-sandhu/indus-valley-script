"""Export staged observations without condition names or concealed mappings."""

from collections import Counter
from pathlib import Path
import json
import random


def main():
    folder = Path("experiments/2026-10-02-six-hour/physical-information")
    output = folder / "blind-inputs"
    key_path = folder / "blind-export-key.json"
    if output.exists() or key_path.exists():
        raise FileExistsError("Preserve the existing blind export")
    output.mkdir()
    worlds = json.loads((folder / "main-corrected-anchor/worlds.json").read_text())
    training, withheld, keys = [], [], []
    scenarios = ("complete_membership", "scrambled_membership", "incomplete_recorded", "ownership_labels")
    for world in worlds:
        for condition_index, scenario in enumerate(scenarios):
            rng = random.Random(world["seed"] * 10 + condition_index)
            identifiers = [obj["id"] for obj in world["objects"]]
            rng.shuffle(identifiers)
            neutral_ids = {identifier: f"o{i:04d}" for i, identifier in enumerate(identifiers)}
            labels = world["ownership_label_by_object"] if scenario == "ownership_labels" else {
                obj["id"]: obj["code"] for obj in world["objects"]
            }
            observations = [{"object_id": neutral_ids[identifier], "label": f"g{labels[identifier]}"}
                            for identifier in identifiers]
            assert len(set(Counter(obj["label"] for obj in observations).values())) == 1
            relation_key = "incomplete_membership" if scenario == "incomplete_recorded" else scenario
            relations = [{"parent_object": neutral_ids[r["parent_object"]],
                          "child_objects": [neutral_ids[identifier] for identifier in r["child_objects"]],
                          "contents_complete": r["contents_complete"]}
                         for r in world[relation_key]]
            dataset_id = f"d{len(training) + 1:03d}"
            anchor = world["random_anchor_code"]
            measurement = world["independent_measurements"][scenario]
            training.append({
                "dataset_id": dataset_id,
                "stage_1_label_pool": observations,
                "stage_2_training_membership": relations[:12],
                "stage_3_independent_measurement": {
                    "object_id": neutral_ids[measurement["object_ids_by_code"][anchor]],
                    "observed_label": f"g{anchor}",
                    "physical_count": measurement["values_by_code"][anchor],
                },
            })
            withheld.append({"dataset_id": dataset_id, "membership": relations[12:]})
            keys.append({"dataset_id": dataset_id, "seed": world["seed"], "condition": scenario,
                         "concealed_quantity_values": world["concealed_values_by_code"],
                         "original_id_by_neutral_id": {v: k for k, v in neutral_ids.items()}})
    (output / "training.json").write_text(json.dumps(training, indent=2) + "\n")
    (output / "withheld.json").write_text(json.dumps(withheld, indent=2) + "\n")
    key_path.write_text(json.dumps(keys, indent=2) + "\n")
    print(json.dumps({"datasets": len(training), "training": str(output / "training.json"),
                      "withheld": str(output / "withheld.json"), "key": str(key_path)}, indent=2))


if __name__ == "__main__":
    main()
