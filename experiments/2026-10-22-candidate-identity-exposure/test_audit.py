"""Synthetic checks for identity and exposure decisions; no source assets read."""
import collections
import unittest

import audit


class MetadataRules(unittest.TestCase):
    def test_numeric_identifier_boundaries(self):
        self.assertNotEqual(audit.normalize_registration("218"), audit.normalize_registration("DHR21897"))
        self.assertNotEqual(audit.normalize_registration("09-899"), audit.normalize_registration("09899"))
        self.assertEqual(audit.normalize_registration("BSR-0055"), audit.normalize_registration("BSR 55"))
        self.assertIsNone(audit.normalize_registration("55?"))

    def test_documented_namespaces_preserve_complete_numeric_components(self):
        self.assertEqual(audit.site_registration("Kanmer", "RIHN-Indus project06-1054"), audit.site_registration("Kanmer", "06-1054"))
        self.assertNotEqual(audit.site_registration("Kanmer", "RIHN-Indus project06-1054"), audit.site_registration("Kanmer", "061054"))
        self.assertEqual(audit.site_registration("Dholavira", "DHR-21897"), audit.site_registration("Dholavira", "21897"))
        self.assertNotEqual(audit.site_registration("Dholavira", "DHR-21897"), audit.site_registration("Dholavira", "218"))
        self.assertNotEqual(audit.site_registration("Other", "DHR-21897"), audit.site_registration("Other", "21897"))

    def test_pages(self):
        self.assertEqual(audit.parse_pages("PDF 2-4;6,8")["pages"], [2, 3, 4, 6, 8])
        self.assertEqual(audit.parse_pages("4-2")["status"], "invalid_range")
        self.assertEqual(audit.parse_pages("printed page 4")["status"], "unparsed")
        self.assertEqual(audit.parse_pages("")["status"], "missing")

    def test_access_methods(self):
        self.assertEqual(audit.access_class("Automated word-window hashing; no source words emitted")[1], "script_only_recorded")
        self.assertEqual(audit.access_class("cropped image viewed")[0], "image_display")
        self.assertIn("exposed_subset_unknown", audit.access_class("automated complete-page screening; incidental restricted-content exposure in previews")[2])
        self.assertEqual(audit.access_class("unexplained access")[1], "display_status_unknown")

    def fixture(self):
        obj = audit.Audit.__new__(audit.Audit)
        obj.sources = {"a": {"sha256": "v1", "local_path": "a.pdf"}, "b": {"sha256": "v2", "local_path": "b.pdf"}, "c": {"sha256": "v1", "local_path": "c.pdf"}}
        obj.event_by_source = collections.defaultdict(list)
        obj.register = {"LIPI:1": {}, "LIPI:2": {}}
        obj.regindex = collections.defaultdict(set)
        obj.reg_evidence = collections.defaultdict(list)
        obj.hashes = {audit.PATHS["inventory"]: "inventory-hash", audit.PATHS["register"]: "register-hash"}
        obj.decisions = {}
        return obj

    def row(self):
        return {"row_id": "test", "primary_publication": "a", "pdf_page": "12", "page": "8", "registration": "100", "site": "Site", "local_site_label": "Site", "local_match": "candidate", "local_family_ids": "1|2", "match_basis": "type-only", "context_join_family": ""}

    def event(self, sid):
        return {"event_id": sid, "pdf_pages": [12], "page_coordinate_basis": "explicit_pdf_incident", "display_status": "model_display_recorded", "content_type": "image_display", "display_extent": "page_specific; crop_object_identity_unresolved", "participant_scope": {"reported_label": "example"}, "evidence": {"path": "synthetic"}}

    def test_versions_do_not_share_page_coordinates(self):
        obj = self.fixture(); obj.event_by_source["b"].append(self.event("b"))
        self.assertEqual(obj.match_events(self.row())["exposure_events"], [])
        obj.event_by_source["c"].append(self.event("c"))
        result = obj.match_events(self.row())
        self.assertEqual(result["exposure_events"][0]["source_relation"], "same_declared_sha256")
        self.assertFalse(result["confirmation_eligible"])

    def test_one_to_many_stays_unresolved(self):
        obj = self.fixture(); obj.regindex[("site", ("100",))] = {"LIPI:1", "LIPI:2"}
        result = obj.identity(self.row())
        self.assertEqual(result["identity_status"], "identifier_supported_one_to_many_unresolved")
        self.assertEqual(len(result["supported_candidate_family_ids"]), 2)
        self.assertIn("no families merged", result["physical_identity_status"])

    def test_conflict_is_not_overridden(self):
        obj = self.fixture(); obj.regindex[("site", ("100",))] = {"LIPI:1"}
        row = self.row(); row["match_basis"] = "conflict"
        self.assertEqual(obj.identity(row)["supported_candidate_family_ids"], [])

    def test_contained_match_needs_whole_identifier_support(self):
        obj = self.fixture(); row = self.row()
        row.update(local_match="matched", local_family_ids="1", match_basis="registration-contained")
        self.assertEqual(obj.identity(row)["supported_candidate_family_ids"], [])
        obj.regindex[("site", ("100",))] = {"LIPI:1"}
        self.assertEqual(obj.identity(row)["supported_candidate_family_ids"], ["LIPI:1"])

    def test_missing_history_does_not_establish_freshness(self):
        result = self.fixture().match_events(self.row())
        self.assertEqual(result["reviewed_exposure_status"], "exposure_history_unknown")
        self.assertFalse(result["confirmation_eligible"])


if __name__ == "__main__": unittest.main()
