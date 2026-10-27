"""Generated counterexamples for the lexical repair; no acquired text fixtures."""
import unittest
import unicodedata
from lexical_inputs import FormCounts, Lexicon, entry_id, form_key, tamil_tokens


def row(translit, head, hom="", page=1):
    return {"translit": translit, "head": head, "hom": hom, "page": page,
            "members": [translit]}


class ExactInputTests(unittest.TestCase):
    def test_vowel_mark_is_retained(self):
        counts = FormCounts(["கா", "கால்", "கடல்", "க", "கா"])
        self.assertEqual(counts.exact("கா"), 2)
        self.assertEqual(counts.exact("க"), 1)

    def test_token_boundaries(self):
        self.assertEqual(tamil_tokens("கா,கால். கா ௧ ஆ! ஆடு"),
                         ["கா", "கால்", "கா", "ஆ", "ஆடு"])

    def test_canonical_unicode(self):
        word = "கொ"
        counts = FormCounts([word, unicodedata.normalize("NFD", word)])
        self.assertEqual(counts.exact(word), 2)
        self.assertEqual(counts.reviewed_variants([word, unicodedata.normalize("NFD", word)]), 2)

    def test_gemination_and_length_not_collapsed(self):
        lex = Lexicon([row("aṟṟu", "அற்று"), row("āṟu", "ஆறு")])
        self.assertEqual(lex.resolve("aṟu")["status"], "missing")
        self.assertEqual(lex.resolve("āṟu")["status"], "exact")

    def test_missing_is_not_zero(self):
        lex = Lexicon([row("kā", "கா")])
        counts = FormCounts(["கால்"])
        self.assertEqual(lex.resolve("kā", counts)["frequency"], 0)
        self.assertIsNone(lex.resolve("ā", counts)["frequency"])

    def test_homographs_ambiguous_but_form_count_available(self):
        lex = Lexicon([row("kā", "கா", "1"), row("kā", "கா", "2")])
        answer = lex.resolve("kā", FormCounts(["கா", "கா"]))
        self.assertEqual(answer["status"], "ambiguous")
        self.assertIsNone(answer["frequency"])
        self.assertEqual(answer["form_counts"], {"கா": 2})
        self.assertEqual(len(answer["candidates"]), 2)

    def test_resolution_does_not_depend_on_row_order(self):
        rows = [row("kā", "கா", "1"), row("kā", "கா", "2")]
        self.assertEqual(Lexicon(rows).resolve("kā"), Lexicon(rows[::-1]).resolve("kā"))

    def test_explicit_alias_has_evidence(self):
        entry = row("āṟu", "ஆறு")
        lex = Lexicon([entry])
        decision = {"query": "aṟu", "entry_id": entry_id(entry),
                    "reviewer": "synthetic reviewer", "evidence": "generated fixture",
                    "relation": "attested-form-variant"}
        answer = lex.resolve("aṟu", FormCounts(["ஆறு"]), decision)
        self.assertEqual(answer["status"], "adjudicated")
        self.assertEqual(answer["frequency"], 1)
        self.assertEqual(answer["adjudication"], decision)
        with self.assertRaises(ValueError):
            lex.resolve("aṟu", adjudication=dict(decision, evidence=""))
        with self.assertRaises(ValueError):
            lex.resolve("aṟu", adjudication=dict(decision, relation="exact-sense"))
        with self.assertRaises(ValueError):
            lex.resolve("kā", adjudication=decision)
        with self.assertRaises(ValueError):
            lex.resolve("aṟu", adjudication=dict(decision, entry_id="absent"))

    def test_exact_homograph_selection(self):
        entries = [row("kā", "கா", "1"), row("kā", "கா", "2")]
        decision = {"query": "kā", "entry_id": entry_id(entries[1]),
                    "reviewer": "synthetic reviewer", "evidence": "generated fixture",
                    "relation": "exact-sense"}
        self.assertEqual(Lexicon(entries).resolve("kā", adjudication=decision)["entry_id"],
                         entry_id(entries[1]))

    def test_empty_form_rejected(self):
        for value in (None, "", "  "):
            with self.assertRaises(ValueError):
                form_key(value)


if __name__ == "__main__":
    unittest.main()
