"""Integrity checks for consequential research assumptions, using small independent cases."""
import json
import itertools
import math
from pathlib import Path
import unittest

import numpy as np

import context_study as context
import microcontext
import paired_surfaces as paired
from restoration import Restorer
from methods.conditional_structure import group_records
from methods.conditional_structure import Model
from independent_annotator import event_scores,conservative_training
from gap_restoration import GapModel
from identifiability_demo import witness


def row(ident, artifact, seq, site="A", typ="SEAL:S"):
    return {"record_id":ident,"object_family_id":artifact,
            "signs_reading_rtl":list(seq),"site":site,"length":len(seq),
            "object_type":typ,"metadata":{"area-section":"X", "block-house":"B",
            "period":"Late"}}


class Integrity(unittest.TestCase):
    def test_gap_marginal_equals_exhaustive_hidden_path_sum(self):
        rows=[{'seq':('a','b','c'),'stratum':('A','S')},
              {'seq':('a','d','c'),'stratum':('A','S')}]
        model=GapModel(rows,20)
        for k in [1,2]:
            for bi,kind in [(False,'PM'),(True,'PMB')]:
                exhaustive=0.
                for hidden in itertools.product(model.model.signs,repeat=k):
                    seq=('a',)+hidden+('c',)
                    scores,_=model.model.score({'seq':seq,'stratum':('A','S')})
                    exhaustive+=2.**sum(scores[kind])
                forward=math.exp(model.log_surviving_probability(('a',),('c',),k,('A','S'),bi))
                self.assertAlmostEqual(forward,exhaustive,places=12)

    def test_candidate_event_forward_matches_enumerated_paths(self):
        rows=[{'seq':('a','b','c'),'stratum':('A','S')},
              {'seq':('d','a','c'),'stratum':('A','S')}]
        m=Model(rows,20);sets=[{'a','d'},{'a','b'},{'c'}]
        for kind in ['U','P','PM','PMB']:
            exhaustive=0.
            for seq in itertools.product(*sets):
                scores,_=m.score({'seq':seq,'stratum':('A','S')})
                exhaustive+=2.**sum(scores[kind])
            actual=2.**sum(event_scores(m,sets,kind,('A','S')))
            self.assertAlmostEqual(actual,exhaustive,places=12)

    def test_candidate_singletons_equal_original_code_likelihood(self):
        rows=[{'seq':('a','b','c'),'stratum':('A','S')},
              {'seq':('a','d','c'),'stratum':('A','S')}]
        m=Model(rows,20)
        expected,_=m.score(rows[0])
        for kind in expected:
            actual=event_scores(m,[{s} for s in rows[0]['seq']],kind,('A','S'))
            self.assertTrue(np.allclose(actual,expected[kind]))

    def test_source_removal_propagates_along_artifact_text_chain(self):
        rows=[{'artifact':'A','artifact_aliases':['A','B'],'seq':('a','b','c')},
              {'artifact':'B','artifact_aliases':['B'],'seq':('d','e','f')},
              {'artifact':'C','artifact_aliases':['C'],'seq':('g','h','i')}]
        allrows=[dict(rows[0],source_cisi='M-140')]
        train,audit=conservative_training(rows,allrows,[])
        self.assertEqual([r['artifact'] for r in train],['C'])
        self.assertEqual(audit['excluded_component_texts'],2)

    def test_label_renaming_preserves_unanchored_objective(self):
        rows=[{'seq':('a','b','c'),'stratum':('A','S')},
              {'seq':('a','d','c'),'stratum':('A','S')}]
        result=witness(rows)
        self.assertLess(result['maximum_likelihood_difference_bits'],1e-12)
        self.assertLess(result['maximum_restoration_mass_difference'],1e-12)

    def test_unique_glyph_texts_preserve_physical_alias_links(self):
        rows=[{"artifact":"A","artifact_aliases":["A","B"],"seq":("x","y")},
              {"artifact":"B","artifact_aliases":["B"],"seq":("y","z")}]
        self.assertEqual(group_records(rows),[[0,1]])

    def test_restoration_never_inspects_masked_truth(self):
        rows=[{"seq":("a","b","c"),"stratum":("A","S")},
              {"seq":("a","d","c"),"stratum":("A","S")}]
        model=Restorer(rows,20)
        a={"seq":("a","?","c"),"stratum":("A","S")}
        b={"seq":("a","UNSEEN","c"),"stratum":("A","S")}
        for bi in [False,True]:
            self.assertTrue(np.allclose(model.distribution(a,1,bi),model.distribution(b,1,bi)))

    def test_local_restoration_equals_joint_model_conditional(self):
        rows=[{"seq":("a","b","c"),"stratum":("A","S")},
              {"seq":("a","d","d"),"stratum":("A","S")}]
        model=Restorer(rows,20)
        query={"seq":("a","?","c"),"stratum":("A","S")}
        joint=[]
        for code in model.model.signs:
            r=dict(query,seq=("a",code,"c"))
            scores,_=model.model.score(r)
            joint.append(2.**sum(scores["PMB"]))
        joint=np.asarray(joint);joint/=joint.sum()
        self.assertTrue(np.allclose(model.distribution(query,1,True),joint))

    def test_transitive_artifact_and_sequence_grouping(self):
        rows = [row("1.1","1","AB"),row("1.2","1","CD"),
                row("2.1","2","CD"),row("3.1","3","EF")]
        g=context.groups_for(rows)
        self.assertEqual(len(set(g[:3])),1)
        self.assertNotEqual(g[2],g[3])

    def test_principal_surface_deterministic(self):
        a=row("1.2","1","AB"); b=row("1.1","1","CD")
        c=row("2.1","2","ABC")
        self.assertEqual([r["record_id"] for r in context.principal_rows([a,c,b])],
                         ["1.1","2.1"])

    def test_fold_has_no_artifact_or_whole_sequence_overlap(self):
        rows = [row(str(i),str(i),[str(i),"X"]) for i in range(20)]
        rows.extend([row("dup", "dup", ["1","X"])])
        cache=context.make_cache(rows,context.groups_for(rows),["full"])
        for train,test,_,_ in cache["full"]:
            for field in ["object_family_id","signs_reading_rtl"]:
                self.assertFalse({str(rows[i][field]) for i in train} &
                                 {str(rows[i][field]) for i in test})

    def test_translation_and_derived_class_cannot_enter_features(self):
        a=row("1","1",["817","002","740"])
        b=dict(a,translation="king",sanskrit="invented",notes="private",**{"class":"SS"})
        self.assertEqual(context.feature_dicts([a],"full"),context.feature_dicts([b],"full"))

    def test_independent_text_representative_not_majority_label(self):
        rows=[row("2","2","AB"),row("1","1","AB"),row("3","3","CD")]
        rr,y,audit=context.independent_text_rows(rows,np.asarray([1,0,1]))
        self.assertEqual([r["record_id"] for r in rr],["1","3"])
        self.assertEqual(y.tolist(),[0,1])
        self.assertEqual(audit[0]["labels"],{1:1,0:1})

    def test_collapse_before_global_dedup(self):
        rows=[row("2","2",["861","002"]),row("1","1",["817","002"])]
        rr,_,_=context.independent_text_rows(rows,np.asarray([0,1]),collapse=True)
        self.assertEqual(len(rr),1)
        self.assertEqual(rr[0]["record_id"],"1")

    def test_permutations_preserve_stratum_label_histograms(self):
        y=np.asarray([0,0,1,1,0,1]); strata=[np.asarray([0,1,2]),np.asarray([3,4,5])]
        yp=context.permute_within(y,strata,np.random.default_rng(9))
        for ix in strata:
            self.assertEqual(sorted(y[ix]),sorted(yp[ix]))

    def test_graphic_count_keeps_stroke_height_and_jar_distinct(self):
        self.assertEqual(paired.numeric(["032","700"]),(2,"stroke_U"))
        self.assertEqual(paired.numeric(["700","034"]),(4,"U_stroke"))
        for seq in [["002","700"],["032","740"],["032","700","740"],["700"]]:
            self.assertIsNone(paired.numeric(seq))

    def test_geometry_uses_only_within_template_variation(self):
        x=np.asarray([2,3,4,2,3,4]); y=7.*x+np.asarray([0,0,0,100,100,100])
        self.assertAlmostEqual(paired.coefficient(y,x,[np.arange(3),np.arange(3,6)]),7.)

    def test_missing_dimensions_not_zero_measurements(self):
        for value in [None,"-","nan",0,-5,"inf"]:
            self.assertIsNone(paired.number(value))
        self.assertEqual(paired.number("3.5"),3.5)

    def test_holm_is_monotone_and_preserves_original_order(self):
        self.assertTrue(np.allclose(paired.holm([.2,.01,.04]),[.2,.03,.08]))

    def test_microcontext_handles_no_comparable_pairs(self):
        with self.assertRaises(ValueError): microcontext.score([])

    def test_microcontext_unique_discards_all_duplicates(self):
        rows=[row("1","1","ABC",site="Mohenjo-daro"),
              row("2","2","ABC",site="Mohenjo-daro"),
              row("3","3","ABD",site="Mohenjo-daro")]
        rr,_=microcontext.prepare(rows,unique=True)
        self.assertEqual([r["record_id"] for r in rr],["3"])

    def test_known_period_excludes_missing(self):
        a=row("1","1","ABC",site="Mohenjo-daro")
        b=row("2","2","ABD",site="Mohenjo-daro");b["metadata"]["period"]="-"
        rr,_=microcontext.prepare([a,b],known_period=True)
        self.assertEqual([r["record_id"] for r in rr],["1"])

    def test_clean_population_excludes_unknowns_and_spaces(self):
        root=Path(__file__).resolve().parents[1]
        rows=context.load_rows(root/"data/normalized/lipi_clean_rtl_singleline.jsonl")
        self.assertEqual(len(rows),2930)
        self.assertTrue(all(not ({"000","999"}&set(r["signs_reading_rtl"])) for r in rows))
        self.assertTrue(all(r["single_line"] and r["complete_observed"] for r in rows))


if __name__=="__main__": unittest.main(verbosity=2)
