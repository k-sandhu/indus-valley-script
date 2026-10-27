import unittest
import extract as e

class ParserTests(unittest.TestCase):
    def row(self, head='சோதனை', form='aitaru'):
        return {'head':head,'translit_plain':form}

    def source(self, translit, members, head='சோதனை'):
        return dict(head=head,translit=translit,members=members,page=1,hom='')

    def test_unique_boundary(self):
        r=self.row(form='aintaru')
        status,pair,_=e.boundary_decision(r,e.source_boundaries([self.source('ai-n-taru',['ai','taru'])]))
        self.assertEqual((status,pair),('lexicon_assisted_boundary',['ai','taru']))

    def test_conflicting_homographs(self):
        i=e.source_boundaries([self.source('ai-taru',['ai','taru']),self.source('ait-aru',['ait','aru'])])
        self.assertEqual(e.boundary_decision(self.row(),i)[:2],('conflicting_cross_source_boundaries',None))

    def test_exact_script(self):
        self.assertIsNone(e.boundary_decision(self.row(head='வேறு'),e.source_boundaries([self.source('ai-taru',['ai','taru'])]))[1])

    def test_length_and_gemination(self):
        for form in ['āitaru','aittaru']:
            self.assertIsNone(e.boundary_decision(self.row(form=form),e.source_boundaries([self.source('ai-taru',['ai','taru'])]))[1])

    def test_e_length_alignment_requires_exact_tamil_head(self):
        i=e.source_boundaries([self.source('ce-marai',['ce','marai'])])
        self.assertEqual(e.boundary_decision(self.row(form='cēmarai'),i)[1],['ce','marai'])
        self.assertIsNone(e.boundary_decision(self.row(head='வேறு',form='cēmarai'),i)[1])

    def test_single_and_three_member_retained(self):
        for ms in [['aitaru'],['ai','ta','ru']]:
            i=e.source_boundaries([self.source('-'.join(ms),ms)])
            self.assertIsNone(e.boundary_decision(self.row(),i)[1])

    def test_increment_candidate_first(self):
        got=e.increment_candidates('murukkampū',['murukku'],{'murukku','pū'})
        self.assertEqual(got[0]['lemma_candidates'],['murukku','pū'])
        self.assertFalse(got[0]['scorer_eligible'])
        self.assertEqual(got[0]['status'],'unresolved_increment_morphology')

    def test_increment_candidate_second(self):
        got=e.increment_candidates('murukkañcettal',['cettal'],{'murukku','cettal'})
        self.assertEqual(got[0]['surface_members'],['murukkañ','cettal'])

    def test_increment_requires_exact_nouns_and_stop(self):
        self.assertEqual(e.increment_candidates('murukkampū',['murukku'],{'murukku'}),[])
        self.assertEqual(e.increment_candidates('murukkañpū',['murukku'],{'murukku','pū'}),[])

    def test_increment_preserves_ambiguous_lemmas(self):
        got=e.increment_candidates('mārampē',['māru'],{'māru','pe','pē'})
        self.assertEqual(len(got),2)
        self.assertTrue(all(not x['scorer_eligible'] for x in got))

    def test_grammatical_header(self):
        self.assertTrue(e.guard.grammatical('is a letter of the Tamil alphabet',None))
        self.assertFalse(e.guard.grammatical('s. A coral tree','s.'))

    def test_parent_origin(self):
        raw='<div>*<hw><tam><b>கா</b> <b>kā</b></tam></hw>, <i><pos>s.</pos></i> A tree. <p2><tam>காப்பூ</tam>, <i><pos>s.</pos></i> Flower.</p2></div>'
        p,s=e.reviewed_page(raw,1)
        self.assertTrue(s[0]['parent_origin_mark_present'])
        self.assertFalse(s[0]['star'])

if __name__=='__main__':unittest.main()
