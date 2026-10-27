"""Meaningful source identity, ambiguity and parser-guard checks."""
import copy
import hashlib
import json
import unittest

from prepare import ROOT, OUT, PKG, read, sha, entry_id
from review import select
from source_blocks import exact_winslow_blocks
from source_guard import grammatical, guard_entry, parse_page_reviewed
from prepare import stratum, SEED


def rows(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


class SourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets={p["sample_id"]:p for p in read(OUT / "compound-packets-v2.json")}

    def test_frozen_protocol_selector_selection_and_input_unchanged(self):
        freeze=read(PKG / "FREEZE.json")
        self.assertEqual(sha(PKG / "PROTOCOL.md"),freeze["protocol_sha256"])
        self.assertEqual(sha(PKG / "code/prepare.py"),freeze["selector_sha256"])
        for key in ("source","local_selection"):
            self.assertEqual(sha(ROOT / freeze[key]["path"]),freeze[key]["sha256"])

    def test_frozen_sample_ids_and_regressions_disjoint(self):
        freeze=read(PKG / "FREEZE.json")
        ids=[r["entry_id"] for r in freeze["selected_row_ids"]]
        self.assertEqual(len(ids),40)
        self.assertEqual(len(set(ids)),40)
        self.assertTrue(set(ids).isdisjoint(p["entry_id"] for p in self.packets.values() if p["sample_id"].startswith("R")))

    def test_deterministic_ranking_reproduces_frozen_sample(self):
        freeze=read(PKG / "FREEZE.json")
        pools={key:[] for key in freeze["stratum_selected"]}
        for record in rows(ROOT / freeze["source"]["path"]):
            if record["translit_plain"] in {"murukkampū","murukkañcettal","jamīṉ"}: continue
            group=stratum(record)
            if group:
                identifier=entry_id(record,"winslow")
                rank=hashlib.sha256((SEED+"|"+identifier).encode()).hexdigest()
                pools[group].append((rank,identifier))
        for group,count in freeze["stratum_selected"].items():
            observed=[item[1] for item in sorted(pools[group])[:count]]
            frozen=[item["entry_id"] for item in freeze["selected_row_ids"] if item["stratum"]==group]
            self.assertEqual(observed,frozen)
            self.assertEqual(len(pools[group]),freeze["stratum_population"][group])

    def test_all_original_blocks_match_exact_row_identity(self):
        for packet in self.packets.values():
            original=ROOT / packet["witnesses"][0]["source_path"]
            blocks=exact_winslow_blocks(original.read_text(encoding="utf-8"),packet["entry"])
            self.assertEqual(len(blocks),1,packet["sample_id"])
            self.assertEqual(blocks[0]["character_span"],packet["witnesses"][0]["character_span"])

    def test_same_head_wrong_gloss_does_not_bind(self):
        packet=self.packets["R02"]
        changed=dict(packet["entry"],gloss="fabricated different sense")
        path=ROOT / packet["witnesses"][0]["source_path"]
        self.assertEqual(exact_winslow_blocks(path.read_text(encoding="utf-8"),changed),[])

    def test_homograph_selection_requires_exactly_one_candidate(self):
        packet=next(p for p in read(OUT / "sense-packets.json") if p["word"]=="kā")
        spec=("kā",840,"⁴","picture","carrying pole")
        chosen=select(packet["candidates"],spec)
        self.assertEqual(chosen["homograph"],"⁴")
        with self.assertRaises(ValueError): select(packet["candidates"]*2,spec)
        with self.assertRaises(ValueError): select(packet["candidates"],("kā",840,"⁷","picture","missing"))

    def test_is_letter_header_general_rule_and_false_positive(self):
        self.assertTrue(grammatical("is a letter of the Sanscrit alphabet. composed of",None))
        self.assertTrue(grammatical("A letter of the Greek alphabet",None))
        self.assertFalse(grammatical("A letter sent to a friend","s."))
        self.assertFalse(grammatical("A tree whose name is a letter of the alphabet","s."))

    def test_attested_letter_root_suppresses_false_split(self):
        packet=self.packets["R02"]
        result=guard_entry(packet["entry"],packet["witnesses"][0]["raw_html"])
        self.assertEqual(result["original_members"],["ja","mīṉ"])
        self.assertEqual(result["guarded_members"],[])
        self.assertTrue(result["split_suppressed"])

    def test_parent_origin_mark_is_preserved_without_declaring_whole_word_loan(self):
        packet=self.packets["W24"]
        p,s=parse_page_reviewed("<div>"+packet["witnesses"][0]["raw_html"]+"</div>",packet["entry"]["page"])
        self.assertTrue(s[0]["parent_origin_mark_present"])
        self.assertFalse(s[0]["star"])
        self.assertEqual(s[0]["whole_entry_loan_status"],"not_determined_by_parent_mark")

    def test_guard_does_not_create_missing_compounds(self):
        for key in ("R01","R03","W21","W24"):
            packet=self.packets[key]
            result=guard_entry(packet["entry"],packet["witnesses"][0]["raw_html"])
            self.assertEqual(result["guarded_members"],[])

    def test_scoped_relations_do_not_change_frequency_spelling(self):
        relations=read(OUT / "accepted-relations.json")
        self.assertEqual(len(relations),4)
        self.assertTrue(all(not r["universal_alias"] and not r["frequency_alias"] for r in relations))
        self.assertEqual(next(r for r in relations if r["surface_form"]=="aṟu")["lemma_form"],"āṟu")

    def test_review_coverage_and_language_exclusions(self):
        senses=rows(OUT / "sense-review.jsonl")
        compounds=rows(OUT / "compound-review.jsonl")
        self.assertEqual(len(senses),24)
        self.assertEqual(len({r["form"] for r in senses}),24)
        self.assertEqual(len({r["entry_id"] for r in compounds}),43)
        self.assertEqual({r["form"] for r in senses if not r["accepted_for_tamil_picture_alternative"]},{"āvu","tōḷ"})
        self.assertTrue(all(s["earliest_attestation"] is None for r in senses for s in r["selected_senses"]))

    def test_all_source_hashes_and_output_hashes_match(self):
        manifest=read(PKG / "source-manifest-v1.json")
        for item in manifest["sources"]+manifest["local_outputs"]:
            self.assertEqual(sha(ROOT / item["path"]),item["sha256"],item["path"])


if __name__=="__main__":
    unittest.main()
