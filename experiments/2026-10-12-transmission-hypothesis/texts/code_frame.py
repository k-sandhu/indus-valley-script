"""Write declared human readings of every selected stanza, with source joins.

This script serializes documentary judgments; it does not derive interpretations
or origin probabilities automatically from word matching.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/texts'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


RV=[
('RV9.112.1','Different workers seek corresponding clients: repair for the woodworker, illness for the healer and a Soma-presser for the ritual specialist.',['work-role','client-relation'],'Occupational comparison embedded in Soma refrain.','The portrayal does not count practitioners, establish a market organization or identify a hereditary caste.'),
('RV9.112.2','An artisan seeks a wealthy person while plant material, bird feathers, stones and fire/light appear in the work imagery.',['work-role','materials','client-relation'],'Griffith calls the worker a smith; the object and precise production sequence remain qualified.','No bead-drilling, polishing or furnace layout is specified.'),
('RV9.112.3','The speaker portrays a bard, a healer father and a mother working with grinding stones, sharing desires for resources.',['household-roles','grain-processing','resources'],'First-person poetic portrayal; Soma refrain continues.','It is not a demographic household sample or an apprenticeship account.'),
('RV9.112.4','Desires of a horse, entertainers, a male and a frog complete the comparison, with the Soma refrain.',['analogy','ritual-frame'],'Humorous/body/animal comparisons extend the occupational examples.','The entire hymn is broader than a classification of social professions.'),
('RV10.71.1','Naming and the first emergence of speech are described in an address to Bṛhaspati.',['speech','naming'],'Mythic/metapoetic beginning.','Narrated first emergence does not date language or a civilization.'),
('RV10.71.2','Fashioning speech is compared with sifting meal; companions recognize affiliation through their speech.',['practical-metaphor','speech','affiliation'],'An explicit comparison carries a sorting operation into a speech domain.','It does not identify the origin or specific tools of grain processing.'),
('RV10.71.3','Speech is located in seers through sacrifice, distributed in many places and sounded together by seven singers.',['ritual','speech','distribution','collective-performance'],'Poetic representation of speech in a ritual repertoire.','The locations and singers are not an excavated teaching network.'),
('RV10.71.4','Seeing and hearing can occur without grasping speech; disclosure is compared with a wife revealing herself.',['competence','understanding','analogy'],'A distinction between access to words and comprehension.','No formal educational assessment is named.'),
('RV10.71.5','A person is depicted as unproductive in companionship and unable to obtain fruit or flower from speech.',['competence','affiliation','evaluation'],'Evaluative poetic imagery; Griffith renders māyā as illusion.','That English choice is not taken as a later philosophical doctrine.'),
('RV10.71.6','Abandoning a knowledgeable companion is linked to loss of a share in speech and ineffective hearing.',['affiliation','access','competence'],'The poem makes a normative connection between association and successful speech.','An admission rule or sanctioning organization is a further institutional hypothesis.'),
('RV10.71.7','Companions with eyes and ears can differ in mental capacities, illustrated through waters of different depths.',['competence','comparison'],'Differences in capacity are portrayed through an analogy.','No population distribution or test score is recoverable.'),
('RV10.71.8','Companion brahmans perform together; some are left behind amid differences in attainments.',['ritual','peer-comparison','competence'],'The passage represents differentiated performance among ritual peers.','The exact comparison procedure and a formal school remain unobserved.'),
('RV10.71.9','Persons classed as neither brahmans nor Soma-preparers are disparaged through speech and weaving imagery.',['boundary','ritual-role','practical-metaphor'],'Polemical role boundary and metaphor.','The difficult weaving term does not establish a textile production lineage.'),
('RV10.71.10','Companions welcome a successful participant in an assembly, associated with food and support for the group.',['assembly','peer-recognition','resources'],'Success, group recognition and support occur together in the poem.','This is not an independently documented council constitution or examination.'),
('RV10.71.11','Recitation, melodic performance, speaking knowledge and measuring the sacrifice are differentiated among participants.',['division-of-work','ritual-role','knowledge'],'An explicit ritual role/action distinction.','Griffith’s rules of sacrificing and lore of being are translation choices; a written rulebook or metaphysical school is not inferred.'),
('RV10.101.1','Companions sharing a dwelling and purpose are urged to awaken and kindle fire while gods are invoked.',['collective-action','ritual','co-residence'],'Ritual exhortation addressed to companions.','It does not determine settlement size or a political organization.'),
('RV10.101.2','Hymns, a boat, implements and the advancement of sacrifice appear in coordinated imperatives.',['collective-action','equipment','ritual'],'Practical imagery participates in an exhortation to sacrifice.','The passage supplies no ship construction specifications.'),
('RV10.101.3','Plows/yokes, prepared ground, sowing seed, ripeness and a sickle are connected with hoped-for yield through song.',['plow','sowing','harvest','collective-action'],'Agricultural operations are invoked within the hymn’s ritual purpose.','The poem does not name a crop species, material design or complete work calendar.'),
('RV10.101.4','Wise performers yoke plows and spread yokes with a desire for favor from gods.',['plow','coordination','ritual'],'Skill and divine favor accompany the equipment imagery.','The verse does not independently confirm literal operation at a named site.'),
('RV10.101.5','Receptacles and straps are arranged for pouring from a water-bearing well described as unfailing.',['well','receptacles','straps'],'Imperatives and first-person plural action in the ritual hymn.','A connection to irrigating a particular field is not explicit.'),
('RV10.101.6','The speaker pours from a well with prepared receptacles, straps and abundant flow.',['well','receptacles','straps'],'First-person well imagery.','Water-lifting throughput or annual reliability is not measured.'),
('RV10.101.7','Horses/chariot and a well with wooden receptacle and stone-wheel terminology occur together.',['chariot','well','stone-wheel','receptacles'],'Dense equipment imagery with a difficult container compound.','The arrangement is not a uniquely reconstructible pulley or mechanism.'),
('RV10.101.8','Enclosure, protective covering, metallic strongholds and a secure nonleaking cup are urged.',['protection','container','metal-image'],'Protective/container images in the same exhortation.','The metal adjective does not justify Griffith’s iron as an authenticated material identification.'),
('RV10.101.9','A divine sacrificial intention is invoked and compared with a milk-giving cow returning from pasture.',['ritual','pastoral-metaphor'],'The word with yavasa concerns grass/fodder in this context.','It is not a selected occurrence of the grain lemma yava.'),
('RV10.101.10','Liquid, a wooden vessel, stone implements, bindings and vehicle imagery are connected.',['vessel','fashioning','bindings','ritual'],'Equipment and Soma-related liquid imagery remain jointly qualified.','No hard-stone drilling or ceramic firing operation is specified.'),
('RV10.101.11','Two poles, a forest/wood relation and sinking a well without digging continue the imagery.',['wood','well','nonliteral-cue'],'The well without digging makes a wholly literal manual interpretation problematic.','No actual excavation operation or well construction event is identified.'),
('RV10.101.12','Men and ritual participants summon Indra for aid and Soma drinking.',['ritual','collective-action'],'The conclusion states the Soma/Indra purpose.','It supplies no independent date or ancestry of the practical images.')
]


CONTROL=[
('TX-Y9-PRESS','T-YASNA',['Y9.1','Y9.2','Y9.3','Y9.4'],'Yasna9.1–4','Haoma preparation, praise, a ritual performer and a reward account are depicted.','Ritual frame and terminology can have an Indo-Iranian explanation; these selected verses do not match an agricultural/well operation sequence.'),
('TX-Y9-MYTH','T-YASNA',['Y9.5','Y9.6','Y9.7','Y9.8'],'Yasna9.5–8','The preparation/reward account continues with ideal rule and heroic genealogies.','Narrated prosperity and ancestors do not date farming institutions or establish a local occupational route.'),
('TX-V3-CULTIVATION','T-VENDIDAD',[f'V3.{x}' for x in range(23,30)],'Vendidad3.23–29','Sowing, watering dry ground, draining wet ground, sustained cultivation and access to food are morally valued.','The Younger Avestan genre supplies an agricultural/ethical comparator, not the rare well fittings or their origin.'),
('TX-V3-REGISTER','T-VENDIDAD',[f'V3.{x}' for x in range(30,34)],'Vendidad3.30–33','Cultivation is mapped onto religious righteousness; grain development is linked to demons and food to strength for work, ritual and reproduction.','This directly observes literary association and practical reasoning at this textual endpoint, not redaction of a surviving Rigvedic source.'),
('TX-OD17-ROLES','T-ODYSSEY',['Od17.382-386'],'Odyssey17.382–386','A speaker lists seer, healer, woodworker and singer among invited specialists.','The literary cluster provides a Greek comparison; resemblance alone does not prove common ancestry of the entire role bundle.'),
('TX-DN1-NORM','T-DN1',[f'DN1.1.{x}' for x in range(21,28)],'DN1.1.21–27','A repertoire of divination, prediction, ritual, calculation and treatment is classified as livelihood from which Gotama abstains while living on donated food.','This is a normative literary classification, not an occupational census or demonstrated rewrite of an earlier surviving text.'),
('TX-DN1-MARKS','T-DN1',['DN1.1.22'],'DN1.1.22','Interpretation of marks on gems, equipment, people and animals belongs to the disallowed repertoire.','Gem-mark interpretation provides no bead-manufacturing operation.'),
('TX-DN1-CALC','T-DN1',['DN1.1.25'],'DN1.1.25','Prediction of food, rain and harvest occurs alongside calculation/accounting and poetic/cosmological activities in the translated list.','The list attests a classification at its own stage; it does not date any listed skill to a Harappan city.'),
('TX-DN1-TREAT','T-DN1',['DN1.1.27'],'DN1.1.27','Medicinal applications and procedures share a normative list with rites and property/house-site activities.','The grouping demonstrates literary organization; provider counts, actual procedures and a direct Rigvedic inheritance remain further claims.')
]


def main():
    target=HERE/'OBSERVATIONS.json'
    if target.exists():raise FileExistsError(target)
    paired=RAW/'paired-passages-v2.json';d=json.loads(paired.read_text('utf8'))
    index={x['pair_id']:x for x in d['main_pairs']}
    if {x[0] for x in RV}!=set(index):raise ValueError('Main frame mismatch')
    rows=[]
    for pair_id,statement,features,context,limit in RV:
        rows.append(dict(observation_id='TX-'+pair_id,pair_ids=[pair_id],source_ids=['T-RVSANS','T-GRIFFITH'],locus=pair_id,statement=statement,
            features=features,context=context,inference_limit=limit,kind='authored reading of textual depiction, with qualified interpretation',
            paired_witness_path=paired.relative_to(ROOT).as_posix(),paired_witness_sha256=sha(paired)))
    for ident,source,pairs,locus,statement,limit in CONTROL:
        rows.append(dict(observation_id=ident,pair_ids=pairs,source_ids=[source],locus=locus,statement=statement,inference_limit=limit,
            kind='authored control reading',paired_witness_path=paired.relative_to(ROOT).as_posix(),paired_witness_sha256=sha(paired)))
    lex={
        'kṛṣ':r'kṛṣ','yava':r'\byav(?:a(?:ṃ|ḥ|m)?|ā(?:ḥ|n|nām)?)\b','sīra':r'\bsīr','lāṅgala':r'\blāṅgal','takṣ':r'takṣ|taṣṭ','bhiṣaj':r'bhiṣa','brahman':r'brahm|brāhmaṇ','vāc':r'vāc|vāk|vāg'
    }
    matches={}
    for lemma,pattern in lex.items():
        matches[lemma]=[x['pair_id'] for x in d['main_pairs'] if re.search(pattern,' '.join(y['text'] for y in x['sanskrit_padas']))]
    matches['bīja-postselection']=[x['pair_id'] for x in d['main_pairs'] if re.search(r'\bbīja',' '.join(y['text'] for y in x['sanskrit_padas']))]
    lexical=dict(scope='Stanza-presence checks over the fixed frame; declared stem/inflection patterns are not a general Sanskrit lemmatizer. Dictionary and historical attribution remain separate.',
        original_lemmas=list(lex),patterns=lex,matches=matches,
        excluded_false_positive=dict(locus='RV10.101.9',form='yavaseva',reason='Pasture/fodder word yavasa with iva; not counted as grain lemma yava'),
        postselection_amendment='AMENDMENT-lexical-bija.md',paired_witness_sha256=sha(paired))
    target.write_text(json.dumps(dict(scope='Full new27-stanza frame and selected controls; source-language/translation text stays in local paired witnesses; origin decisions are separate',script_sha256=sha(Path(__file__)),frozen_selection_sha256=sha(HERE/'selection-v1.json'),observations=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (HERE/'LEXICAL-RESULTS.json').write_text(json.dumps(lexical,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(main=27,controls=len(CONTROL),total=len(rows),lexical_matches=matches),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
