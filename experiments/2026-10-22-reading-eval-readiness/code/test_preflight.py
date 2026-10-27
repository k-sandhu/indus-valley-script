"""Constructed declarations exercise fail-closed gates; review claims are fixtures."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from preflight import FREEDOMS, validate


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "fixture.json").write_text("{}", encoding="utf-8")
        artifact = {"path": "fixture.json", "sha256": hashlib.sha256(b"{}").hexdigest()}
        self.manifest = {
            "participant_id": "p", "role": "proposal", "family": "phonetic_key",
            "comparison_group": "synthetic fixture", "inputs": [artifact],
            "claim": {"title": "Generated claim", "edition": "fixture v1", "locator": "fixture 1",
                      "statement": "A generated test claim", "sources": [artifact]},
            "sign_namespace": {"name": "generated signs", "version": "1", "crosswalk": [artifact]},
            "mapping": [artifact],
            "construction_record": [artifact], "freedom": {key: 0 for key in FREEDOMS},
            "predictions": [{"id": "prediction", "statistic_family": "fixture_family",
                             "null": "generated null", "pass_rule": "generated criterion",
                             "min_units": 10, "missingness_rule": "exclude by fixed rule"}],
            "controls": {"known_correct": ["correct"], "wrong": ["wrong"]},
            "calibration": {"status": "accepted", "evidence": [artifact]},
            "source_review": {"status": "accepted", "evidence": [artifact]},
            "cohort": {"exposure_status": "reviewed-unexamined", "identity_review": [artifact],
                       "exposure_review": [artifact], "independent_units": 20},
            "scorer": {"task": "key-calibration", "artifacts": [artifact]},
            "freeze": {"registered_participants": ["p", "correct", "wrong"],
                       "frozen_participants": ["p", "correct", "wrong"],
                       "confirmation_reads": 0, "joint_credence_rule": "generated fixture rule",
                       "artifacts": [artifact]}}

    def test_complete_generated_contract(self):
        self.assertEqual(validate(self.manifest, self.root), [])

    def test_nonfinite_and_missing_freedom_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf"), None, "unknown", "", {}, []):
            item = copy.deepcopy(self.manifest)
            item["freedom"]["alternatives"] = value
            self.assertTrue(validate(item, self.root))
        del self.manifest["freedom"]["alternatives"]
        self.assertTrue(validate(self.manifest, self.root))

    def test_no_freshness_from_unreviewed_state(self):
        self.manifest["cohort"]["exposure_status"] = "unreviewed"
        self.assertTrue(validate(self.manifest, self.root))

    def test_unknown_scorer_blocked(self):
        self.manifest["family"] = "rebus"
        self.manifest["scorer"]["task"] = "rebus"
        self.assertTrue(validate(self.manifest, self.root))

    def test_artifact_change_rejected(self):
        (self.root / "fixture.json").write_text("changed", encoding="utf-8")
        self.assertTrue(validate(self.manifest, self.root))

    def test_missing_review_and_outside_root_rejected(self):
        self.manifest["source_review"]["evidence"] = []
        self.assertTrue(validate(self.manifest, self.root))
        self.manifest["inputs"] = [{"path": "../outside", "sha256": "0" * 64}]
        self.assertTrue(validate(self.manifest, self.root))

    def test_all_participants_frozen_and_no_reads(self):
        self.manifest["freeze"]["frozen_participants"].remove("wrong")
        self.assertTrue(validate(self.manifest, self.root))
        self.manifest["freeze"]["frozen_participants"].append("wrong")
        self.manifest["freeze"]["confirmation_reads"] = 1
        self.assertTrue(validate(self.manifest, self.root))

    def test_underpowered_population_and_empty_controls(self):
        self.manifest["cohort"]["independent_units"] = 3
        self.assertTrue(validate(self.manifest, self.root))
        self.manifest["cohort"]["independent_units"] = 20
        self.manifest["controls"]["wrong"] = []
        self.assertTrue(validate(self.manifest, self.root))

    def test_claim_namespace_and_mapping_required(self):
        for key in ("claim", "sign_namespace", "mapping"):
            item = copy.deepcopy(self.manifest)
            del item[key]
            self.assertTrue(validate(item, self.root))

    def test_duplicate_participants_and_overlapping_controls_rejected(self):
        for key in ("registered_participants", "frozen_participants"):
            item = copy.deepcopy(self.manifest)
            item["freeze"][key].append("p")
            self.assertTrue(validate(item, self.root))
        self.manifest["controls"]["wrong"] = ["correct"]
        self.assertTrue(validate(self.manifest, self.root))

    def test_malformed_family_and_role_return_errors(self):
        for value in ([], {}, 2):
            item = copy.deepcopy(self.manifest)
            item["family"] = value
            self.assertTrue(validate(item, self.root))
            item = copy.deepcopy(self.manifest)
            item["role"] = value
            self.assertTrue(validate(item, self.root))


if __name__ == "__main__":
    unittest.main()
