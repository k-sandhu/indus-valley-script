"""Checks for unsupported promotion of review evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import integrate


class ReviewBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.face = {'accepted_for_physical_layout': True, 'accepted_for_segment_order': True}
        self.decision = dict(self.face)

    def test_source_order_requires_both_readers_and_layout(self):
        self.decision['accepted_for_segment_order'] = False
        self.assertFalse(integrate.order_accepted(self.face, self.decision))
        self.decision['accepted_for_segment_order'] = True
        self.face['accepted_for_physical_layout'] = False
        self.assertFalse(integrate.order_accepted(self.face, self.decision))

    def test_duplicate_rows_do_not_satisfy_population(self):
        with self.assertRaises(ValueError):
            integrate.unique([{'id': 'a'}, {'id': 'a'}], 'id', 2)

    def fixture(self, eligible=False, missing_event=False):
        events = [{'event_id': 'e1', 'content_type': 'image_display'}]
        candidates = []
        for i in range(358):
            candidates.append({
                'source_row_id': f'c{i}', 'confirmation_eligible': eligible,
                'exposure_events': [{'event_id': 'missing' if missing_event else 'e1'}],
                'source_level_event_ids_without_page_overlap': [],
                'supported_candidate_family_ids': ['LIPI:1'] if i == 0 else [],
                'unresolved_candidate_family_ids': ['LIPI:2'] if i == 0 else [],
                'identity_status': 'identifier_supported_provisional_family',
                'reviewed_exposure_status': 'source_page_image_display_recorded_object_scope_unresolved',
                'page_mapping_status': 'explicit_pdf_page_event_match', 'participant_scope': ['historical reader'],
            })
        obj = integrate.Integration.__new__(integrate.Integration)
        obj.objects = {k: {'object_id': k, 'exposure_status': 'unreviewed'} for k in ['LIPI:1', 'LIPI:2']}
        obj.data = {'relationships': []}
        obj.events, obj.inputs = [], {}
        obj.source = lambda *args: 'source'
        captured = []
        def assertion(*args, **kwargs):
            captured.append((args, kwargs))
            return f'a{len(captured)}'
        obj.assertion = assertion
        return obj, candidates, events, captured

    def execute(self, obj, candidates, events):
        with patch.object(integrate, 'rows', side_effect=[candidates, events]), \
             patch.object(integrate, 'rel', side_effect=str), patch.object(integrate, 'sha', return_value='digest'):
            return obj.candidate_reviews(Path('candidate'), Path('events'))

    def test_page_image_event_never_becomes_exact_object_exposure(self):
        obj, candidates, events, captured = self.fixture()
        self.execute(obj, candidates, events)
        self.assertTrue(all(r['exposure_status'] == 'unreviewed' for r in obj.objects.values()))
        self.assertTrue(all(a[0][2]['object_specific_content_verified'] is False for a in captured))

    def test_candidate_relation_keeps_weak_confidence(self):
        obj, candidates, events, captured = self.fixture()
        self.execute(obj, candidates, events)
        self.assertEqual([r['status'] for r in obj.data['relationships']], ['confirmed', 'candidate'])
        self.assertEqual([a[1]['confidence'] for a in captured], ['identifier-supported', 'candidate'])

    def test_unlinked_rows_remain_in_review_population(self):
        obj, candidates, events, _ = self.fixture()
        result = self.execute(obj, candidates, events)
        self.assertEqual(len(result), 358)
        self.assertEqual(len(obj.objects), 2)

    def test_freshness_from_audit_is_rejected(self):
        obj, candidates, events, _ = self.fixture(eligible=True)
        with self.assertRaisesRegex(ValueError, 'eligibility'):
            self.execute(obj, candidates, events)

    def test_unrecorded_event_is_rejected(self):
        obj, candidates, events, _ = self.fixture(missing_event=True)
        with self.assertRaisesRegex(ValueError, 'missing exposure'):
            self.execute(obj, candidates, events)

    def test_face_review_pointer_survives_image_and_font_source_checks(self):
        obj = integrate.Integration.__new__(integrate.Integration)
        obj.objects = {'LIPI:1': {'exposure_status': 'unreviewed'}}
        obj.faces, obj.inputs, obj.events = {}, {}, []
        obj.source = lambda *args: 'source'
        obj.assertion = lambda *args, **kwargs: 'assertion'
        reviews, decisions = [], []
        for i in range(29):
            fid = f'LIPI:1.{i+1}'
            obj.faces[fid] = {'face_id': fid, 'object_id': 'LIPI:1'}
            reviews.append({'face_id': fid, 'accepted_for_physical_layout': False,
                            'accepted_for_segment_order': False,
                            'image_witnesses': [{'path': 'image.jpg', 'sha256': 'digest'}],
                            'observations': {'arrangement': 'unresolved'},
                            'source_alignment': {'source_path': 'export.jsonl', 'source_sha256': 'digest',
                                                 'source_font_path': 'font.ttf', 'source_font_sha256': 'digest'}})
            decisions.append({'face_id': fid, 'first_pass_records': [{'path': 'sealed.json', 'sha256': 'digest'}],
                              'inspected_code_sheet': 'sheet.png', 'accepted_for_physical_layout': False,
                              'accepted_for_segment_order': False, 'unresolved_reasons': ['low contrast']})
        with patch.object(integrate, 'rows', side_effect=[reviews, decisions]), \
             patch.object(integrate, 'rel', side_effect=str), patch.object(integrate, 'sha', return_value='digest'):
            obj.face_reviews(Path('face-reviews.jsonl'), Path('adjudications.jsonl'))
        self.assertEqual({r['layout_review']['review_path'] for r in obj.faces.values()}, {'face-reviews.jsonl'})


if __name__ == '__main__':
    unittest.main()
