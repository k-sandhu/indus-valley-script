"""New Sanskrit comparisons used as fixed assumptions in two lexical scenarios."""
from analyze import slp

def anchor(key, codes, meaning, words, alternate, role, rationale, context, references):
    return {'id':key, 'codes':codes, 'meaning':meaning, 'sanskrit_comparisons':words,
            'preferred_probe':words[0], 'alternative_probe':alternate, 'role':role,
            'shape_rationale':rationale, 'context_rationale':context,
            'sources':references, 'status':'new project hypothesis',
            'lexical_probe_assumption':'The comparison word is inserted as a full stem in an assumed word window.'}

MW='MW1899-Cologne'
ANCHORS=[
 anchor('N01',['151'],'porter service, carried load or transport obligation',
    ['bhāra','bhārika','vāha'],'vāha','labour',
    'The person visibly carries two loads. Bhāra supplies load/work; bhārika supplies a porter comparison.',
    'The code is final in 49 of 57 occurrences in distinct complete sequences; this permits a category after a named party.',[MW,'Rao2018','HARP-sealing']),
 anchor('N02',['411'],'barley/grain allotment', ['yava','dhānya','śasya'],'dhānya','commodity',
    'The class drawing has a cereal ear. Yava is a narrower alternative to grain; it is not Bonta’s separate looped DHANYA drawing.',
    'The few complete contexts include a numeral and the jar; the crop-specific choice has little contextual resolution.',[MW,'HARP-food']),
 anchor('N03',['450','452'],'water supply or water-related allotment', ['udaka','jala'],'jala','commodity',
    'Single zigzag/wave forms suggest a water comparison; the extra stroke may qualify it.',
    'Each graphic code has only one complete-sequence occurrence. Full-stem probes test the water idea without choosing a precise water institution.',[MW,'Dholavira-water']),
 anchor('N04',['600'],'bounded field or landed holding', ['kṣetra','koṣṭha'],'koṣṭha','institution',
    'A bounded rectangle can depict an allocated space. Kṣetra supplies a field; koṣṭha supplies a store-room alternative.',
    'Two complete contexts place it within or at the end of an account; field and storage remain competing uses.',[MW]),
 anchor('N05',['319'],'tiered access, store or stepped structure', ['sopāna','koṣṭha','setu'],'koṣṭha','institution',
    'The H-shaped framework contains small boxes. A stepped access/compartment comparison is an imaginative extension.',
    'Only two complete contexts occur; a architectural reading has a weak corpus basis.',[MW,'HARP-sealing']),
 anchor('N06',['825'],'woven cloth or textile allotment', ['vastra','paṭa'],'paṭa','commodity',
    'Cross hatching resembles a weave; this competes with a counted/registered leaf denomination.',
    'Four complete contexts include numeral-like neighbours; this permits a counted commodity reading.',[MW,'Kenoyer2004-textiles']),
 anchor('N07',['400'],'recorded batch, account total or counted class', ['gaṇa','gaṇanā','gaṇaka'],'gaṇanā','operation',
    'Repeated side strokes can function as an accounting/tally motif; gaṇa supplies a group or counted class.',
    '170 of 192 complete-sequence occurrences are final; 73 directly follow the AS jar. This favours a closing category over a free-standing pictorial noun.',[MW]),
 anchor('N08',['142'],'staff-holder or responsible official', ['daṇḍin','adhikārin'],'adhikārin','title',
    'A staff held by a person supplies daṇḍin; extending that to authority is a second assumption.',
    'Most contexts are initial or medial, with repeatable following signs; an occupational/name element fits that placement.',[MW]),
 anchor('N09',['130'],'cultivator or agricultural service', ['kṛṣaka','hala'],'hala','labour',
    'A person and fork/tool suggest a cultivator. Hala is a plough/tool alternative, without identifying the drawing as a plough.',
    'The sign recurs with person/tally-like neighbours and with Bonta’s deva and pati anchors.',[MW,'HARP-food']),
 anchor('N10',['121'],'livestock keeper or handler of animal products', ['gopāla','paśu','carma'],'paśu','labour',
    'A person plus an animal leg supplies a keeper or handler. The product/hide alternative is retained.',
    'The one complete sequence ends in the AS jar; it can fit a named keeper or an animal-related account.',[MW,'HARP-food']),
 anchor('N11',['272'],'messenger, bird-named person or mobile service', ['dūta','pakṣin'],'pakṣin','person',
    'Bird wings permit a messenger comparison; the shift from bird to messenger is speculative.',
    'All three complete-sequence occurrences are initial, two before Bonta’s tra sign; a name/service element is plausible.',[MW]),
 anchor('N12',['540'],'shared portion or distributed allotment', ['bhāga','saṃyoga'],'saṃyoga','measure',
    'The two opposed triangles make a paired/share motif. Bhāga supplies a portion, while saṃyoga supplies joining.',
    'Five of seven complete-sequence occurrences are medial and four precede the AS jar; the position can join an allotment to a party.',[MW]),
 anchor('N13',['645'],'together, partnership or joint contribution', ['saha','saṃyoga'],'saṃyoga','grammar',
    'Two crossed strokes supply a joining/together hypothesis.',
    'Eight of ten complete-sequence occurrences are medial; a connector is more plausible here than for the terminal comb.',[MW]),
 anchor('N14',['370'],'seed stock, seed-corn or bulb produce', ['bīja','phala'],'phala','commodity',
    'A stem interrupted by a round body and dot supplies a seed/bulb comparison.',
    'Four of five complete-sequence occurrences are initial; produce, a name or an issuer category remain alternatives.',[MW,'HARP-food']),
 anchor('N15',['818'],'wheel-related issuer, workshop or emblem', ['cakra'],'āditya','institution',
    'A four-spoke wheel supplies cakra. It is kept distinct from Bonta’s six-spoke DEVA mapping.',
    'Only one complete sequence, before a numeral-like sign, survives; a potter/cart office and a solar emblem compete.',[MW]),
 anchor('N16',['930'],'wheel-associated hall or institutional house', ['śālā','agāra'],'agāra','institution',
    'An arch encloses a wheel and two strokes; a house/hall with a qualifying emblem is the working composition.',
    'The sign is final in its sole complete-sequence occurrence; an institution after a name is possible.',[MW])
]

def seeds_for_scenario(inherited, alternative=False):
    result={k:list(v) for k,v in inherited.items()}
    for a in ANCHORS:
        word=a['alternative_probe'] if alternative else a['preferred_probe']
        for code in a['codes']:
            assert code not in result, (a['id'],code)
            result[code]=[{'source_id':a['id'],'label':word,'slp1':[slp(word)],
                'category':'new comparison-word probe','graphic_mapping_confidence':'project hypothesis'}]
    return result
