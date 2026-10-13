"""Create the explicitly curated input ledger once; source text stays local-only."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / 'data/raw/2026-10-11-early-indian-continuity/institutions'

def witness(name, url=None):
    p = RAW / name
    a = p.with_name(p.name + '.acquisition.json')
    meta = json.loads(a.read_text(encoding='utf-8')) if a.exists() else {}
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                bytes=p.stat().st_size, url=url or meta.get('url'), acquisition=meta)

def source(i, title, authors, version, url, names, scope, rights='unverified; raw local-only'):
    return dict(id=i, title=title, authors=authors, edition_or_version=version, url=url,
                accessed='2026-10-11', inspected_scope=scope, rights=rights,
                witnesses=[witness(n) for n in names])

sources = [
source('S01','Approaching rice domestication in South Asia: New evidence from Indus settlements in northern India',
       'Jennifer Bates; Cameron A. Petrie; Ravindra N. Singh','JAS 78 (2017), 193–201; accepted manuscript',
       'https://doi.org/10.1016/j.jas.2016.04.018',['bates2017-rice.pdf'],
       'Accepted PDF pp. 9–18; Tables 2–4 on PDF pp. 13–14 visually checked; site dating on PDF p. 10.'),
source('S02','‘Multi-cropping’, Intercropping and Adaptation to Variable Environments in Indus South Asia',
       'Cameron A. Petrie; Jennifer Bates','JWorldPrehistory 30 (2017), 81–130; accepted manuscript with supplement',
       'https://doi.org/10.1007/s10963-017-9101-z',['petrie-bates2017.pdf'],
       'Accepted PDF pp. 1–7, 25–33; definitions, crop/weed inference and site sample limitations.'),
source('S03','Craft Traditions of the Indus Civilization and their Legacy in Modern Pakistan',
       'Jonathan Mark Kenoyer','Lahore Museum Bulletin IX(2), nominal July–December 1996; hosted filename Kenoyer1998',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer1998_Craft%20Traditions%20of%20the%20Indus%20Civilization%20and%20t.pdf',
       ['kenoyer1998-craft.pdf'],'Scan pp. 1–8 OCR; pp. 1, 5 visually checked; issue/date header p. 2 checked in OCR.'),
source('S04','Stone beads in Ancient South Asia—7000–600 BC: A comparative approach to technology, style, and ideology',
       'Jonathan Mark Kenoyer','International Bead Conference witness; header 23 November 2007',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer%202007%20Intl%20beads%20conf.pdf',
       ['kenoyer2007-beads.pdf'],'PDF pp. 1, 4–6 OCR; PDF p. 5 visually checked across four columns.'),
source('S05','Early Sanskritization: Origins and Development of the Kuru State',
       'Michael Witzel','Electronic Journal of Vedic Studies 1(4), 1995, 1–26; author copy',
       'https://www.michaelwitzel.org/wp-content/uploads/2014/06/ejvs0104article.pdf',
       ['witzel1995-kuru-author-tls-exception.pdf'],'PDF pp. 1, 7–11; institutional development thesis. Transport used disabled TLS verification, explicitly retained.'),
source('S06','Early Indian history: Linguistic and textual parameters; Ṛgvedic history: poets, chieftains and polities',
       'Michael Witzel','Two uncorrected author proofs for chapters in G. Erdosy (ed.), 1995; internal pagination differs from published chapter',
       'https://michaelwitzel.org/wp-content/uploads/2014/06/Erdosy1995.pdf',
       ['witzel1995-early-history-author-tls-exception.pdf'],'Second proof internal p. 197/PDF p. 113 lists RV 4.57.4–8 as a later addition. Transport used disabled TLS verification.'),
source('S07','Rigveda Translation Commentary (supplement to Jamison and Brereton 2014)',
       'Stephanie W. Jamison; with Joel P. Brereton translations','Official UCLA files dated 25 September 2026; selected books only',
       'https://rigvedacommentary.alc.ucla.edu/',
       ['jamison-book2.pdf','jamison-book4.pdf','jamison-book5.pdf','jamison-book6.pdf','jamison-book10.pdf'],
       'II.1.2/16 PDF pp. 1/4; IV.57 p. 142; V.29.15 p. 54; VI.28 pp. 116–118; X.34.13 p. 169. Commentary, not complete translations.'),
source('S08','The Rigveda: Metrically Restored Text',
       'Barend A. van Nooten; Gary B. Holland; revised electronic edition Karen Thomson and Jonathan Slocum',
       '1994 HOS 50 basis; University of Texas electronic revision, retrieved 2026',
       'https://lrc.la.utexas.edu/books/rigveda/',
       ['rv02-restored.html','rv04-restored.html','rv05-restored.html','rv06-restored.html','rv10-restored.html'],
       'Exact lines RV 2.001.02/16; 4.057.04–08; 5.029.15; 6.028.06; 10.034.13. A restored edition, not a manuscript facsimile.',
       'Site research/noncommercial permission observed; full HTML kept local-only'),
source('S09','Rig Veda: English translation',
       'H. H. Wilson','Wisdomlib transcription attributed to Wilson; site date 1866 not independently established for each original volume',
       'https://www.wisdomlib.org/hinduism/book/rig-veda-english-translation/d/doc833105.html',
       ['wilson-rv05029-15.html','wilson-rv06028-6.html'],'RV 5.29.15 and 6.28.6. Later commentary/glosses separated from verse.'),
source('S10','The Satapatha-Brahmana, Part III',
       'Julius Eggeling','Madhyandina translation; SBE 41 (1894); Wisdomlib umbrella date 1882 belongs to multivolume series',
       'https://www.wisdomlib.org/hinduism/book/satapatha-brahmana-english/d/doc63275.html',
       ['eggeling-sb531.html'],'ŚB 5.3.1.1–12 and translator notes 2, 4–6; courier verse 11 checked against online Sanskrit 5.3.1.11.'),
source('S11','ARYANS', 'Rüdiger Schmitt','Encyclopaedia Iranica II/7, 684–687 (1987), updated 8 March 2013',
       'https://www.iranicaonline.org/articles/aryans/',['iranica-aryans.html'],
       'Aryan culture and religion: cognate ritual/poetic terms and RV/Avestan phrase correspondences.'),
source('S12','Early Buddhist Texts: Their Composition and Transmission',
       'Mark Allon','Journal of Indian Philosophy 50 (2022), 523–556',
       'https://doi.org/10.1007/s10781-021-09499-6',['allon2022.html'],
       'Introduction; The Stylistic Features of Sutra Prose; discussion of intentional changes and bhāṇakas.'),
source('S13','Dīgha Nikāya DN 2, DN 5 and DN 16',
       'Pali edition: Mahāsaṅgīti root; English: Bhikkhu Sujato; SuttaCentral/Bilara',
       'published branch retrieved 2026-10-11; local hashes pin six files; branch head recorded separately',
       'https://github.com/suttacentral/bilara-data',
       ['dn2-pali.json','dn2-sujato.json','dn5-pali.json','dn5-sujato.json','dn16-pali.json','dn16-sujato.json','bilara-license.md','bilara-head.json'],
       'DN2:14.1–3; DN5:11.7–11; DN16:1.4.3–8 and 1.6.11–12; roots checked by segment ID; repeated passages count once.',
       'Bilara LICENSE.md explicitly CC0 for supported translations; root edition rights not independently resolved; all acquired text remains local-only'),
source('S14','The Rigveda: The Earliest Religious Poetry of India',
       'Stephanie W. Jamison; Joel P. Brereton','Oxford University Press 2014, Introduction; two overlapping excerpts count as one work',
       'https://vedisk.sites.ku.dk/files/2021/09/Jamison-Brereton-s.-2-15.pdf',
       ['jamison2014-2-15.pdf','jamison2014-13-22.pdf'],
       'Printed pp. 5, 9–10, 14–16 inspected; composition assessment, inherited patronage and staged collection. Copied from reviewer-acquired witness; no new edition independence.')
]

def axes(kind):
    if kind == 'archaeology':
        return dict(composition='Modern archaeological study, source-specific date.',
                    redaction='Not applicable to excavated remains.', manuscript='Not applicable; study witness is separately pinned.',
                    narrated_time='Not applicable.', archaeological_context='Source-assigned site/phase below; relative chronology retained.')
    if kind.startswith('rv'):
        return dict(composition='RV hymns: J&B 2014 p. 5 author estimate 1400–1000 BCE, explicitly contentious; no locus-specific absolute date.',
                    redaction='Family collections, staged consolidation and Śākala transmission distinct from hymn composition (J&B pp. 14–16).',
                    manuscript='No ancient manuscript inspected. Electronic editions/commentary are modern witnesses.',
                    narrated_time='Poetic address, prayer or advice; no dated event inferred.', archaeological_context='No excavated practice/context joined to this verse.')
    if kind == 'brahmana':
        return dict(composition='Post-Rigvedic prose ritual layer; no exact absolute date assigned in this study.',
                    redaction='Mādhyandina recension; text history not equated to original performance.',
                    manuscript='No manuscript inspected; nineteenth-century translation and modern transcription.',
                    narrated_time='Prescriptive royal consecration sequence, not a dated occurrence.', archaeological_context='No excavated royal household joined.')
    if kind == 'buddhist':
        return dict(composition='Early Buddhist canon with composition and transmission across generations; no whole-sutta date assigned (Allon 2022).',
                    redaction='Pali DN recension and bhāṇaka transmission; final surviving wording not assigned to Buddha’s lifetime.',
                    manuscript='No early manuscript inspected; modern Mahāsaṅgīti digital root and Sujato translation.',
                    narrated_time='Buddha-era frame; inner past story or transferred analogy specified below.', archaeological_context='Second urbanization is a comparison horizon, not a dated archaeological join to the speech.')
    return dict(composition='Modern scholarly argument, edition date in source ledger.', redaction='Source-specific editorial history.',
                manuscript='No ancient manuscript witness inspected.', narrated_time='Comparative reconstruction or source analysis, not a dated narrative.',
                archaeological_context='No new physical evidence acquired.')

def obs(i, kind, bundle, refs, locus, text, limit, layer=None, geography=None, values=None):
    return dict(id=i, evidence_type=kind, component=bundle, source_ids=refs, locus=locus,
                observation=text, permitted_inference_and_limit=limit, textual_layer=layer,
                geography=geography, date_axes=axes(kind), values=values)

observations = [
obs('A01','archaeology','agriculture',['S01'],'Accepted PDF p. 10, lines 246–260',
    'Winter and summer cereals/pulses occur at Masudpur I, VII and Bahola. Rice use spans source-assigned Early, Mature, Late Harappan and PGW deposits.',
    'Crop exploitation and regional persistence; grain presence does not identify domestication rate, same plot rotation or speakers.',geography='Haryana, northern India'),
obs('A02','archaeology','agriculture',['S01'],'Accepted PDF pp. 9–10, especially lines 243–260',
    'Direct rice-grain dates support Mature and Late use at Masudpur; earlier deposits have dates on other crops. Bahola had no radiocarbon dating in this paper.',
    'Date kind and context differ by site; Bahola phases are not direct AMS dates.',geography='Masudpur I/VII; Bahola'),
obs('A03','archaeology','agriculture',['S01'],'Accepted PDF p. 13, Table 2',
    'Masudpur VII context 514 and 515 supply one Mature and one Late spikelet assemblage.',
    'Within-site comparison of two assemblages; per-20-litre densities are not an independent-trial sample size.',geography='Masudpur VII',
    values={'unit':'reported percentage of classified spikelet assemblage','rows':[
        {'phase':'Mature','context':'514','wild':75.84,'domesticated':9.55,'immature':14.61,'uncertain':0.0,'contexts':1},
        {'phase':'Late','context':'515','wild':0.0,'domesticated':28.57,'immature':42.86,'uncertain':28.57,'contexts':1}]}),
obs('A04','archaeology','agriculture',['S01'],'Accepted PDF p. 13, Table 3 and lines 341–348',
    'Six Mature Harappan Masudpur I contexts enter the spikelet analysis after three single-spikelet contexts were excluded.',
    'Reported pooled/density-derived composition; nearly half uncertain; not a chronological series within this site.',geography='Masudpur I',
    values={'unit':'reported percentage','rows':[{'phase':'Mature','context':'six retained contexts','wild':39.46,'domesticated':9.99,'immature':4.51,'uncertain':46.03,'contexts':6}]}),
obs('A05','archaeology','agriculture',['S01'],'Accepted PDF p. 14, Table 4 and lines 358–374',
    'Six Late Harappan Bahola contexts enter the spikelet analysis; three single-spikelet Late contexts excluded.',
    'High uncertainty limits direction of site-pooled domestication comparison.',geography='Bahola',
    values={'unit':'reported percentage','rows':[{'phase':'Late','context':'six retained contexts','wild':6.92,'domesticated':33.15,'immature':0.0,'uncertain':59.93,'contexts':6}]}),
obs('A06','archaeology','agriculture',['S01'],'Accepted PDF p. 14, lines 358–367',
    'Of 30 Bahola macrobotanical contexts, 10 are Late and 20 PGW; rice grains occur in 50% and 60% respectively. Four PGW spikelet contexts are excluded for low recovery.',
    'A PGW rice-occurrence observation exists, but Tables 2–4 do not quantify a PGW domestication endpoint.',geography='Bahola',values={'late_contexts':10,'pgw_contexts':20,'late_rice_occurrence_percent':50,'pgw_rice_occurrence_percent':60,'pgw_spikelet_contexts_retained':0}),
obs('A07','archaeology','agriculture',['S02'],'Accepted PDF pp. 2–7, cropping definitions',
    'Multiple seasons, sequential cropping and intercropping require different land-use inferences.',
    'Winter/summer seeds together do not alone establish same-plot rotation or intercropping.',geography='Indus South Asia'),
obs('A08','archaeology','agriculture',['S02'],'Accepted PDF pp. 31–33, Masudpur Late contexts',
    'Low recovery, missing winter weeds and possible single-event gourd burning affect the Late comparison.',
    'Presence/absence and pooled proportions depend on taphonomy and sample type.',geography='Masudpur VII'),
obs('C01','archaeology','craft',['S03'],'Printed pp. 2–5',
    'Different craft organizations include dispersed kin networks and crafts requiring support for distant procurement.',
    'Archaeological organizational interpretation; dispersed specialization is compatible with complex skills outside cities.',geography='Harappa and Indus cities'),
obs('C02','archaeology','craft',['S03'],'Printed p. 5, Modern Craft Traditions',
    'Similar raw materials and efficient techniques can explain some ancient/modern pottery similarities.',
    'Modern analogy supplies a convergence control; modern kin arrangements do not date ancient organization.',geography='Pakistan'),
obs('C03','archaeology','craft',['S04'],'PDF p. 5, Localization Era, columns 1–2',
    'The author reports loss of ernestite drills and reduced access to distant bead raw materials after urban reorganization.',
    'Selective technological loss is relevant. Secret-source and elite-death explanations are explicitly author hypotheses.',geography='Greater Indus region'),
obs('C04','archaeology','craft',['S04'],'PDF p. 5, columns 2–3, Sanauli comparison',
    'Preliminary drill-hole comparisons distinguish Sanauli tapered stone drilling from tubular methods at Harappa; finished beads may include inherited/imported objects.',
    'Preliminary observations, partly personal communication; manufacture waste and excavated drills are needed to establish local production.',geography='Sanauli; Harappa'),
obs('C05','archaeology','craft',['S04'],'PDF p. 5, final column, PGW/Early Iron Age',
    'The 2007 comparison explicitly says comprehensive technological studies of PGW/early NBP beads had not yet been conducted.',
    'A documented coverage gap as of that source, not absence of craft continuity or a claim about all research through 2026.',geography='North India'),
obs('T01','rv_family_unflagged','priestly_specialization',['S08','S07'],'RV 2.1.2; UT 2.001.02a–d; Jamison II.1.2 PDF p. 1',
    'Agni is addressed through differentiated ritual duties/names including hotṛ, potṛ, neṣṭṛ, agnīdh, praśāstṛ, adhvaryu and brahman, alongside house-lord.',
    'The poetic enumeration presupposes intelligible differentiated duties; it does not prove the later human roster, staffing or a full four-Veda institution.',layer='Family book II; no locus-specific core date authenticated'),
obs('T02','rv_family_unflagged','patronage',['S08','S07','S14'],'RV 2.1.16; UT 2.001.16; J&B printed pp. 9–10',
    'The verse joins donors, cattle/horses and collective ritual speech; J&B describe a poet–patron compensation system.',
    'Representation of exchange and performance; Indo-Iranian/Indo-European inherited patronage is a positive alternative.',layer='Family book II; no locus-specific core date authenticated'),
obs('T03','rv_family_unflagged','craft',['S08','S09','S07'],'RV 5.29.15; Wilson exact verse; Jamison PDF p. 54',
    'The poet compares newly made praise with garments and an artisan-made chariot.',
    'Familiar crafted objects and making as a model for composition; no bead operation, workshop scale or Harappan genealogy.',layer='Family book V; no locus-specific core date authenticated'),
obs('T04','rv_family_unflagged','assemblies',['S08','S09','S07'],'RV 6.28.6; Jamison VI.28.6 PDF p. 118',
    'The praise of cattle places public speech in sabhā; Jamison compares it with the book-II vidatha refrain but distinguishes the settings/registers.',
    'An intelligible assembly/speech setting; no institutional identity with a Harappan council or Buddhist Vajji meetings.',layer='Family book VI; no locus-specific core date authenticated'),
obs('T05','rv_family_late_addition','agriculture',['S08','S07','S06'],'RV 4.57.4–8; Witzel proof PDF p. 113/internal p. 197',
    'Ploughing, draught animals and the personified furrow Sītā appear in the agricultural hymn.',
    'Witzel names these verses as a later addition within a family book; they cannot serve as an independently early core anchor.',layer='Family book IV, explicitly flagged later addition'),
obs('T06','rv_later_book','agriculture',['S08','S07'],'RV 10.34.13; Jamison X.34.13 PDF p. 169',
    'The gambler is advised to cultivate his field and attend to material livelihood.',
    'Later RV agricultural representation; crop species and cropping scheme are unspecified.',layer='Book X, later collection material'),
obs('B01','brahmana','priestly_specialization',['S10'],'ŚB Mādhyandina 5.3.1.1–12, especially 2 and 12',
    'Royal consecration visits specialist households and offers to the purohita; the ritual binds the ratnins to the consecrated ruler.',
    'Later coordinated ritual/political representation; translator notes show that some office glosses vary or remain unclear.',layer='Post-Rigvedic Brahmana prose'),
obs('B02','brahmana','patronage',['S10'],'ŚB 5.3.1.11; Sanskrit verse 5.3.1.11 online',
    'The courier pālāgala is dispatched along a road and included among the royal jewels; the offering has an assigned material fee.',
    'A prescribed communication/specialist tie; the ceremony supplies no archaeological dispatch network or performance date.',layer='Post-Rigvedic Brahmana prose'),
obs('N01','buddhist','craft',['S13'],'DN2:14.1–3; root and Sujato translation',
    'The dialogue enumerates crafts/services including potters, dyers, embroiderers, accountants and finger-talliers while contrasting visible occupational fruits with renunciation.',
    'Represented occupational differentiation in a didactic comparison; modern translation labels do not establish guilds or Harappan bookkeeping.'),
obs('N02','buddhist','agriculture',['S13'],'DN5:11.7–11; root and Sujato translation',
    'A priest advises seed/fodder for cultivation and cattle, funding for trade, and food/wages for royal service.',
    'The inner king Mahāvijita story is legendary past within a Buddha-era frame; normative policy reasoning is not an authenticated ancient policy event.'),
obs('N03','buddhist','assemblies',['S13'],'DN16:1.4.3–8; root and Sujato translation',
    'Frequent and harmonious Vajji meetings are presented as conditions of welfare/growth.',
    'An assembly ideal in the narrative; exact membership, voting and chronology need separate evidence.'),
obs('N04','buddhist','assemblies',['S13'],'DN16:1.6.11–12; root and Sujato translation',
    'Meeting principles are reused for mendicants after the Vajji passage.',
    'Explicit transfer of an institutional analogy within the text; repetition is not an independent archaeological confirmation.'),
obs('P01','scholarship','priestly_specialization',['S11'],'Aryan culture and religion, ritual terms and RV/Avestan phrase parallels',
    'Vedic hotṛ and Avestan zaotar, yajña/yasna, mantra/mąθra and cognate phrases support shared Indo-Iranian ritual/poetic inheritance.',
    'A specific alternative origin for terms and specialist tradition; no complete later institutional roster is reconstructed.'),
obs('P02','scholarship','priestly_specialization',['S05'],'PDF pp. 7–11, Strategies and institutional changes',
    'Witzel proposes post-Rigvedic Kuru consolidation of priestly corporations, rites and elite alliances.',
    'An explicit later-reorganization model. Author political causal interpretation is not a directly excavated formation event.'),
obs('P03','scholarship','agriculture',['S06'],'Second proof PDF p. 113/internal p. 197',
    'The addition list names RV 4.57.4–8 despite its family-book location.',
    'Book membership and verse stratum must be separate; published page numbering is not substituted for proof pagination.'),
obs('P04','scholarship','patronage',['S12'],'Introduction; prose style and intentional change discussion',
    'Formulaic memorization coexists with divergent recensions, intentional alteration and didactic narratives.',
    'Preserved precision and narrative historicity are different questions; no single composition date is assigned to the three suttas.'),
obs('P05','scholarship','patronage',['S14'],'Printed pp. 5, 9–10, 14–16',
    'J&B distinguish old poetic inheritance, hymn composition, family training collections and staged collection; patronage is inherited Indo-Iranian/Indo-European.',
    'Sophistication in earliest surviving textual representation does not measure the beginning of an institution.')
]

controls = ['selective_local_transmission','shared_indo_iranian_inheritance','convergence','genre_selection','later_reorganization_second_urbanization']
claims = [
dict(id='H01', kind='transmission_hypothesis', component='agriculture', observation_ids=['A01','A02','A06','A07','A08','T05','T06','N02'],
     claim='Some regional farming knowledge could have persisted through posturban communities and entered later agrarian settings.',
     intermediate_archaeological_ids=['A06'], diagnostic_feature_crosses_text_archaeology=False, controls=controls,
     missing='A dated joint operation/crop-management bundle connecting intermediate communities to the particular textual representation.'),
dict(id='H02', kind='transmission_hypothesis', component='craft', observation_ids=['C01','C02','C03','C04','C05','T03','N01'],
     claim='Domestic apprenticeship could carry some crafting operations across political change while distant procurement-dependent operations are lost or redesigned.',
     intermediate_archaeological_ids=['C04'], diagnostic_feature_crosses_text_archaeology=False, controls=controls,
     missing='Blindly matched manufacturing operations, locally produced intermediate waste and chronological/context joins; textual crafts remain nonspecific.'),
dict(id='H03', kind='transmission_hypothesis', component='priestly_specialization', observation_ids=['T01','B01','P01','P02','P05'],
     claim='Sophisticated priestly coordination could combine inherited Indo-Iranian specialists with later local recruitment and institutional consolidation.',
     intermediate_archaeological_ids=[], diagnostic_feature_crosses_text_archaeology=False, controls=controls,
     missing='A diagnostic Harappan ritual operation and dated intermediates; cognate role terms already support an inherited alternative.'),
dict(id='H04', kind='transmission_hypothesis', component='patronage', observation_ids=['T02','B02','P04','P05'],
     claim='Reciprocal patron–specialist relations can sustain complex knowledge in dispersed communities without continuous urban administration.',
     intermediate_archaeological_ids=[], diagnostic_feature_crosses_text_archaeology=False, controls=controls,
     missing='A local diagnostic exchange practice distinguished from inherited praise-poetry patronage and generic reciprocal support.'),
dict(id='H05', kind='transmission_hypothesis', component='assemblies', observation_ids=['T04','N03','N04'],
     claim='Gathered speech and coordinated meetings are compatible with several distinct institutions; continuity needs a rarer procedural bundle.',
     intermediate_archaeological_ids=[], diagnostic_feature_crosses_text_archaeology=False, controls=controls,
     missing='Membership, procedural rules and dated local antecedents independent of generic deliberation and textual analogy.'),
dict(id='M01',kind='mechanism',component='all', observation_ids=['A01','A07','C01','C02','C03','T01','T02','T03','P01','P02','P05'],
     claim='The carrier is a practice with learners, materials, repetition and sponsorship. Household transmission and inherited poetic specialists can coexist with lost urban coordination.',
     controls=controls, missing='Joint dated operation bundles needed to identify the actual carriers.'),
dict(id='R01',kind='numerical_sensitivity',component='agriculture',observation_ids=['A03','A04','A05','A06'],
     claim='Classifying all uncertain spikelets as wild or domesticated supplies bounded assemblage comparisons, not confidence intervals or a PGW domestication trajectory.',
     controls=['classification_uncertainty','context_and_site_selection'],missing='Independent context-level original counts and quantified PGW bases.')
]

for name, data in [('sources.json',sources),('observations.json',observations),('claims.json',claims)]:
    target = HERE / name
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite curated input: {target}')
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wrote {len(sources)} sources, {len(observations)} observations, {len(claims)} claims')
