"""Integrity tests for structural inference machinery, independent of Indus outcomes."""
import random
import unittest
from unittest.mock import patch
import json
from collections import Counter
import numpy as np

from conditional_structure import Model, evaluate, frames, group_records, load_records, make_folds, pair_frames, shuffle_positions


def record(i, seq, artifact=None, site="A", object_type="seal"):
    return {"record_id": str(i), "artifact": str(artifact if artifact is not None else i), "seq": tuple(seq), "site": site, "object_type": object_type, "stratum": (site, object_type)}


class IntegrityTests(unittest.TestCase):
    def test_site_transfer_excludes_transitive_component_relatives(self):
        from nested_conditional import leave_site_out
        held = [record(i, "abc", artifact="held", site="held_site") for i in range(60)]
        relatives = [record(60, "abc", artifact="x", site="other_site"),
                     record(61, "xyz", artifact="x", site="other_site"),
                     record(62, "xyz", artifact="y", site="other_site"),
                     record(63, "qrs", artifact="y", site="other_site")]
        safe = record(64, "def", artifact="safe", site="other_site")
        selected = []
        def mocked_tune(train, seed):
            selected.extend(train)
            return ("U", 20), ("PMB", 20), {}
        with patch("nested_conditional.tune", side_effect=mocked_tune):
            result = leave_site_out(held + relatives + [safe])
        self.assertEqual([r["artifact"] for r in selected], ["safe"])
        self.assertEqual(result[0]["removed_additional_transitive_component_relatives"], 3)

    def test_site_transfer_excludes_any_physical_alias(self):
        from nested_conditional import leave_site_out
        rows = [record(i, "abc", artifact="held", site="held_site") for i in range(60)]
        for row in rows:
            row["artifact_aliases"] = ["held", "hidden_alias"]
        unsafe = record(60, "xyz", artifact="foreign_representative", site="other_site")
        unsafe["artifact_aliases"] = ["foreign_representative", "hidden_alias"]
        safe = record(61, "def", artifact="safe", site="other_site")
        selected = []
        def mocked_tune(train, seed):
            selected.extend(train)
            return ("U", 20), ("PMB", 20), {}
        with patch("nested_conditional.tune", side_effect=mocked_tune):
            result = leave_site_out(rows + [unsafe, safe])
        self.assertEqual([r["artifact"] for r in selected], ["safe"])
        self.assertEqual(result[0]["removed_exact_sequence_or_artifact_overlap"], 1)

    def test_unique_representative_preserves_every_artifact_alias(self):
        raw = [
            {"record_id": "1", "object_family_id": "x", "sequence": list("abc")},
            {"record_id": "2", "object_family_id": "y", "sequence": list("abc")},
            {"record_id": "3", "object_family_id": "y", "sequence": list("abd")},
        ]
        with patch("pathlib.Path.read_text", return_value="\n".join(json.dumps(r) for r in raw)):
            rows, excluded = load_records("mock", unique=True)
        self.assertEqual(len(rows), 2)
        self.assertEqual(excluded["duplicate_sequence"], 1)
        self.assertEqual(set(rows[0]["artifact_aliases"]), {"x", "y"})
        self.assertEqual(len(group_records(rows)), 1)

    def test_transitive_group_protects_artifact_and_duplicate(self):
        rows = [record(0, "abc", "x"), record(1, "abd", "x"), record(2, "abd", "y"), record(3, "xyz", "z")]
        groups = group_records(rows)
        self.assertEqual(sorted(map(len, groups)), [1, 3])
        assignment, _ = make_folds(rows, groups, 2, 17)
        self.assertEqual(assignment[0], assignment[1])
        self.assertEqual(assignment[1], assignment[2])
        self.assertNotEqual(assignment[0], assignment[3])

    def test_probabilities_are_normalized_and_unseen_sign_is_finite(self):
        rows = [record(0, "abc"), record(1, "abd"), record(2, "bac", site="B")]
        model = Model(rows, 20)
        for length, i, stratum, prev in [(3, 1, ("A", "seal"), "a"), (12, 11, ("Unknown", "pot"), "not_in_training")]:
            for distribution in model.distributions(length, i, stratum, prev):
                self.assertAlmostEqual(float(distribution.sum()), 1.0, places=12)
                self.assertTrue(np.all(distribution > 0))
        scores, oov = model.score(record(3, ["a", "never_seen", "d"]))
        self.assertEqual(oov, 1)
        self.assertTrue(all(np.isfinite(score).all() for score in scores.values()))

    def test_shuffle_preserves_declared_margins(self):
        rows = [record(i, [str(i % 3), str(i % 5), str(i % 7)], site="A" if i % 2 else "B") for i in range(30)]
        shuffled, mobility = shuffle_positions(rows, 15, True)
        def margins(data):
            counts = Counter()
            for row in data:
                for i, s in enumerate(row["seq"]):
                    counts[(len(row["seq"]), i, row["stratum"], s)] += 1
            return counts
        self.assertEqual(margins(rows), margins(shuffled))
        self.assertEqual(mobility["total_tokens"], 90)
        self.assertNotEqual([r["seq"] for r in rows], [r["seq"] for r in shuffled])

    def test_duplicate_inscriptions_do_not_inflate_substitution_support(self):
        rows = [record(0, "abc"), record(1, "abd"), record(2, "abc"), record(3, "zbc"), record(4, "zbd")]
        candidates = pair_frames(frames(rows))
        self.assertEqual(len(candidates[("c", "d")]), 2)
        self.assertEqual(len(candidates[("a", "z")]), 2)

    def test_latent_templates_capture_distant_slot_correlation_without_sounds(self):
        from template_comparison import Templates
        # Two nonphonetic templates link first and last slots; the middle varies.
        rows = [record(i, ["A" if i % 2 else "B", str(i % 7), "A" if i % 2 else "B"]) for i in range(140)]
        model = Templates(rows, 2, 5, 17)
        linked = model.score(record("test", ["A", "2", "A"]))
        mismatched = model.score(record("test", ["A", "2", "B"]))
        self.assertGreater(linked[-1], mismatched[-1] + 2)
        fitted = model.components[3]
        self.assertTrue(np.allclose(fitted["theta"].sum(axis=2), 1))
        self.assertTrue(np.allclose(fitted["pi"].sum(), 1))
        self.assertTrue(all(np.allclose(p.sum(), 1) for p in fitted["piz"].values()))


def calibration():
    # Synthetic data have known generative provenance; neither is ancient writing.
    rng = random.Random(20261001)
    independent, dependent = [], []
    for i in range(3000):
        independent.append(record(i, [str(rng.randrange(20)) for _ in range(6)], site="A" if i % 2 else "B"))
        latent = [rng.randrange(20) for _ in range(3)]
        dependent.append(record(i, [str(latent[0]), str(latent[0]), str(latent[1]), str(latent[1]), str(latent[2]), str(latent[2])], site="A" if i % 2 else "B"))
    output = {}
    for name, rows in [("independent", independent), ("dependent_paired_symbols", dependent)]:
        groups = group_records(rows)
        assignment, _ = make_folds(rows, groups, 5, 20261001)
        result, _ = evaluate(rows, groups, assignment, 5, 20, 0)
        output[name] = result["gain_bits_per_noninitial_sign"]
    assert output["independent"] < 0.05, output
    assert output["dependent_paired_symbols"] > 0.5, output
    return output


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IntegrityTests)
    passed = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    if not passed:
        raise SystemExit(1)
    print("Synthetic calibration:", calibration())
