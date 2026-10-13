"""Build a bounded Sanskrit comparison ledger from fixed exact MW records.

The full dictionary and selected source bodies remain in ignored data/raw.
Public outputs contain authored sense paraphrases and exact source locators.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-12-anchor-expansion/anchors'
MW = ROOT / 'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt'
INDEX = ROOT / 'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json'
PRIOR = ROOT / 'experiments/2026-10-11-bonta-adversarial/run-v6/sanskrit-senses.json'
PIN = '55e8addbd96e8d9001b8789026b026763f4049c1'
SOURCE_URL = f'https://github.com/sanskrit-lexicon/csl-orig/blob/{PIN}/v02/mw/mw.txt'
SOURCE = f'Monier-Williams 1899, Cologne digital edition, pinned csl-orig {PIN}'
EXPECTED_MW_SHA = '555ecf5aadaaf21e5965d6b3b419f428fc9ab9237f563627001ceca468d0cff8'

# word, comparison headword, SLP1 key, exact sense, page/column, selected
# meaning, cited source scope, use in the proposed semantic family.
ADDITIONS = [
 ('śikya','śikya','Sikya','216503','1069,3','rope loop or carrying sling suspended from a pole or yoke to receive a load','Atharvaveda cited; this record also permits the load so carried','Suspension and cargo component; equipment rather than a specified worker'),
 ('śikyapāśa','śikyapāśa','SikyapASa','216506','1069,3','cord by which a vessel is suspended','Śatapatha Brāhmaṇa cited','Suspended vessel alternative to an unspecified pair of burdens'),
 ('bandha','bandha','banDa','142631','720,3','binding or tying; bond or tie','Rigveda cited for this selected binding sense','Binding operation or tied bundle; later deposit and account senses excluded'),
 ('pāśa','pāśa','pASa','123319','623,3','noose, tie, bond or cord','Rigveda cited','Loop or fastening component; snare is a literal rival'),
 ('sūtra','sūtra','sUtra','251185','1241,3','thread, yarn, string or cord','Atharvaveda cited','Cord/textile component; rule-book and measuring-line senses are separate'),
 ('danta','danta','danta','90025','468,2','tooth, by the selected record’s cross-reference to dat','Rigveda 6.75.11 and Atharvaveda cited; dat 89783 explicitly gives tooth','Individual tooth component; does not identify a complete comb or harrow'),
 ('kaṇṭaka','kaṇṭaka','kaRwaka','42385','245,2','thorn','Śatapatha Brāhmaṇa V, Mahābhārata and Yājñavalkya cited','Pointed projections as a thorn motif, rival to tool teeth'),
 ('yugma','yugma','yugma','171923','854,2','pair or couple','Śāṅkhāyana Gṛhya, Yājñavalkya and Rāmāyaṇa cited','Pair of objects or units; does not assign a value to each pictured component'),
 ('yuga (pair)','yuga','yuga','171839','854,1','pair or couple','Gṛhya/Śrauta Sūtra abbreviation GṛŚrS. and Mahābhārata cited','Paired equipment/loads, separately from the existing yoke sense'),
 ('saṃpuṭa','sampuṭa','sampuwa','236160','1173,1','round covered case, box or casket','Nīlakaṇṭha cited; chronology of this selected citation unresolved','Closed portable-container rival to enclosure, vessel or room'),
 ('droṇa','droṇa','droRa','98002','502,3','wooden vessel, bucket or trough','Rigveda and Mahābhārata cited','Open receptacle rather than the separate capacity-measure sense'),
 ('kalaśa','kalaśa','kalaSa','45762','260,3','water-pot, pitcher or jar','Rigveda cited','Jar/vessel comparison; contents and exact capacity remain unspecified'),
 ('sthālī','sthālī','sTAlI','255299','1262,2','earthen dish, pan or cooking-vessel','Atharvaveda, Brāhmaṇa and Śrauta Sūtra cited','Cooking-container alternative to storage jar or generic receptacle'),
 ('pātra','pātra','pAtra','120799','612,3','vessel or receptacle, including bowl, cup or dish','Rigveda cited','Generic container; meal, competent person and capacity senses have separate records'),
 ('kusūla','kusūla','kusUla','53680','298,3','granary or grain store-room; kuśūla is a recorded variant','Bhāgavata Purāṇa cited for the granary; AV goblin is a separate record','Grain-storage competitor for bounded frames, with later citation visible'),
 ('gṛha','gṛha','gfha','66501','361,3','house, habitation or home','Rigveda and Atharvaveda cited','Built enclosure rather than portable container or plot'),
 ('kakṣā','kakṣā','kakzA','41532','241,3','surrounding wall, courtyard or secluded room','Mahābhārata, Bhāgavata Purāṇa and Manu cited','Enclosed area/room rival; kakṣa hiding-place has a different record'),
 ('vṛti','vṛti','vfti','203992','1007,2','hedge, fence or enclosed cultivated ground','Manu and Mahābhārata cited','Fence or plot boundary alternative to room, crate and internal tally frame'),
 ('sasya','sasya','sasya','239928','1192,3','grain, produce or crop of grain','Atharvaveda cited; śasya is a recorded spelling','Generic crop category rather than a specifically identified species'),
 ('aṅkura','aṅkura','aNkura','1469','7,2','sprout, shoot or blade; same record also includes swelling','Suśruta cited; separate dates for each listed sense are not established','Growing plant alternative to seed, fruit, bud or rounded implement'),
 ('śūka','śūka','SUka','220136','1085,2','awn of grain','Rāmāyaṇa, Sarvadarśanasaṃgraha and a Kātyāyana Śrauta commentary cited','Fine pointed grain component; does not identify barley or an entire ear'),
 ('puṣpa','puṣpa','puzpa','126969','639,2','flower or blossom','Atharvaveda cited','Blossom/rosette component rather than grain or a specific plant taxon'),
 ('pattra (leaf)','pattra','pattra','114852','581,2','leaf or petal; patra is a recorded spelling','Kātyāyana Śrauta, Manu and Mahābhārata cited','Leaf/petal comparison; wing and written-document senses have separate records'),
 ('matsya','matsya','matsya','155087','776,3','fish','Rigveda cited','Direct fish shape, retaining name, commodity and phonetic rivals at inscription level'),
 ('śakuni','śakuni','Sakuni','211354','1046,2','bird','Rigveda cited; proposed species identifications are lexicographic alternatives','Generic bird comparison; no messenger occupation follows from the picture'),
 ('mṛga','mṛga','mfga','166792','828,2','wild animal or game, especially deer or antelope','Rigveda cited','Animal-class rival to domestic livestock, horn or hide'),
 ('śṛṅga','śṛṅga','SfNga','220523','1087,1','animal horn or horn used as an object','Rigveda cited','Horn component; mountain peak, building pinnacle and other projections have separate records'),
 ('vṛścika','vṛścika','vfScika','204836','1011,3','scorpion','No literary citation supplied by this selected record; first textual date unresolved','Segmented small-animal rival where legs and a curved tail compete with the bird interpretation'),
 ('makṣikā','makṣikā','makzikA','154017','771,3','fly or bee','Rigveda cited; the selected record includes both fly and bee','Insect/winged-small-animal rival; neither species nor honey production selected'),
 ('nau','nau','nO','112618','571,2','boat or ship','Rigveda cited','Boat-shaped object; homonymous first-person pronoun record is excluded'),
 ('dhvaja','dhvaja','Dvaja','102417','522,1','banner, flag or standard','Rigveda cited','Mounted emblem/standard alternative to plant, spear, staff or human carrier'),
 ('śaṅku','śaṅku','SaNku','211471','1047,2','peg, nail or spike','Rigveda cited','Pointed implement; stake, weapon, dial-gnomon and fixed length are separate senses'),
 ('dhanus','dhanus','Danus','99627','509,2','bow','Rigveda cited; dhanuṣ is its separately indexed compound form','Bow-shaped tool rather than a measure, a curved border or an astral sign'),
 ('dhanvin','dhanvin','Danvin','99684','509,3','armed with a bow; bowman','Mahābhārata cited; Vāmana grammatical citation also present','Person with bow, separating equipment from bearer and occupation'),
 ('puruṣa','puruṣa','puruza','126438','637,1','human being or person','Rigveda cited','Visible human component; role, gender and rank remain independently unresolved'),
 ('niśrayaṇī','niśrayaṇī','niSrayaRI','110641','561,2','ladder or staircase','Śatapatha Brāhmaṇa and Kātyāyana Śrauta cited','Access/ladder rival to barred panel, tally enclosure or storage compartments'),
 ('stamba','stamba','stamba','254432','1257,3','clump or tuft of grass; bunch or cluster','Atharvaveda cited; explicit sheaf-of-grain sense is separate 254433 marked L.','Bundled vegetation; tied harvested grain remains a more specific rival'),
 ('kāṇḍa','kāṇḍa','kARqa','47500','269,2','jointed part of a reed, cane or plant stalk; section','Atharvaveda, Taittirīya Saṃhitā and Vājasaneyi Saṃhitā cited','Stalk component; arrow, bundle and general full-stem senses are separately indexed'),
 ('pallava','pallava','pallava','120296','610,2','sprout, shoot, twig or bud','Mahābhārata and classical poetry cited','Plant growth component; scarf, dynasty and fish senses excluded'),
 ('go','go','go','66884','363,3','ox, cow or cattle','Rigveda cited','Domestic bovine rival to wild game or unspecified horned animal'),
]

FAMILIES = {
 'quantity_strokes': (['saṃkhyā','gaṇanā','śreṇi','yugma'], 'Repeated strokes motivate number/series or paired-unit tests.', ['phonetic marks','field separators','engraving variants']),
 'bounded_tallies': (['varga','koṣṭha (enclosure)','gṛha','vṛti'], 'Marks within a frame permit bounded set, enclosure and plot comparisons.', ['crate','room','purely geometric sign']),
 'carrier_yoke': (['vivadha','yuga','śikya','śikyapāśa','bhārin','bhāra'], 'Separate bearer, carrying pole, sling and suspended contents.', ['consignment','carrying equipment','balance','offering bearer']),
 'toothed_tool_bearer': (['matya','kaṅkata','danta','kaṇṭaka','puruṣa'], 'A person carries a toothed component; harrow, comb and thorn tests stay separate.', ['comb bearer','weapon bearer','named emblem','other craft tool']),
 'staff_bearer': (['daṇḍin','śaṅku','adhikārin'], 'Staff and human components motivate a bearer; occupation requires context.', ['guard','ritual attendant','implement user','personal name']),
 'bow_bearer': (['dhanus','dhanvin','pāśa','puruṣa'], 'Bow-like curve and person permit an equipped-person comparison.', ['loop or carrying apparatus','curved staff','issuer name']),
 'animal_or_hide_bearer': (['carman','paśu','go','mṛga','gopāla'], 'Distinguish carried skin/animal part from a keeper or living animal.', ['butcher','hide worker','animal-themed personal name','nonanimal burden']),
 'fish_bearer': (['matsya','puruṣa'], 'Fish and human components permit fish handling without fixing a trade.', ['fish offering','fish-named person','nonfish carried object']),
 'paired_suspended_ovals': (['śikya','śikyapāśa','yuga (pair)','yugma','dvaya'], 'Two suspended bodies motivate sling, paired containers or loads.', ['balance pans','detached fish','independent repeated signs']),
 'enclosed_human': (['puruṣa','pāśa','bandha','gṛha'], 'Human plus curved flanks permits a bounded person or worn/carried apparatus.', ['clothing','open container','paired emblems','pure graphic qualification']),
 'fish_shapes': (['matsya'], 'Generic fish precedes any species, commodity or word-value assignment.', ['name or phonetic sign','asset/grade symbol','different oval-bodied object']),
 'bird_shapes': (['śakuni','pakṣin'], 'Bird is the graphic comparison; species and messenger roles require other evidence.', ['personal name','issuer emblem','nonavian object']),
 'toothed_closer': (['kaṅkata','śreṇi','varga','gaṇa','danta'], 'Separate comb/teeth appearance from an ordered-series or closing-class function.', ['harrow','personal-name element','grammatical suffix']),
 'toothed_implements': (['matya','kaṅkata','śaṅku','kaṇṭaka'], 'Parallel projections can be working teeth, points or thorns.', ['plant branches','weapon','stand-alone emblem']),
 'plant_branch': (['sasya','aṅkura','pallava','śūka','dhānya'], 'Distinguish crop, growth, blossom and awn rather than selecting a species.', ['tool','tally','issuer emblem']),
 'leaf_cluster': (['pattra (leaf)','puṣpa','pallava'], 'Leaf, petal and bud offer component-level vocabulary.', ['animal parts','textile','pure geometry']),
 'bound_stalks': (['stamba','kāṇḍa','bandha','sūtra','sasya'], 'Parallel plant-like stems and basal fastening motivate bunch or tied-stalk tests.', ['reeds','container of implements','unharvested plants','row/category sign']),
 'compartmented_frame': (['koṣṭha (enclosure)','koṣṭha','kośa','kusūla','gṛha','kakṣā','niśrayaṇī','dvāra'], 'Room, enclosure, portable box, ladder and barred access predict different uses.', ['tally frame','capacity marker','graphic qualifier']),
 'horned_animal': (['go','paśu','mṛga','śṛṅga'], 'Domestic animal, game and detached horn are different object hypotheses.', ['nonanimal design','named issuer','symbolic emblem']),
 'circled_stem': (['bīja','aṅkura','pallava','phala'], 'Seed, shoot, bud and fruit are alternatives for a stalk joined to a round body.', ['rounded tool','container on a handle','issuer name']),
 'loop_chain': (['pāśa','bandha','sūtra'], 'Loops or linked marks permit fastening, cord and binding comparisons.', ['independent repeated units','name element','ornament']),
 'bent_parallel_rows': (['śreṇi','varga','bandha','kāṇḍa'], 'Ordered parallel components motivate row, section or joined-set comparisons.', ['numerals','bent implements','engraving variation']),
 'wave_zigzag': (['udaka','jala'], 'Wave or zigzag permits water as one literal picture.', ['bent implement','path','phonetic sign']),
 'vessel_shapes': (['kumbha','kalaśa','droṇa','sthālī','pātra','kośa','saṃpuṭa'], 'Separate open vessels, cooking pots, jars and covered boxes.', ['body or plant motif','commodity name','capacity class']),
 'bounded_space': (['koṣṭha (enclosure)','gṛha','kakṣā','vṛti','kṣetra'], 'Closed borders permit room, building, fenced ground and plot comparisons.', ['portable container','geometric classifier','phonetic sign']),
 'ladder_access': (['niśrayaṇī','sopāna','dvāra'], 'Parallel sides and connecting rungs permit ladder/access tests.', ['barred frame','storage compartments','tally structure']),
 'wheel_forms': (['cakra'], 'A hub/spoke structure permits wheel without choosing vehicle or workshop.', ['sun emblem','rosette','generic circle']),
 'boat_forms': (['nau','droṇa','pātra'], 'Curved hull-like borders permit boat alongside trough or vessel.', ['crescent','open container','curved implement']),
 'mounted_standard': (['dhvaja','śaṅku','puruṣa'], 'An emblem on an upright permits standard alongside implement or carried object.', ['plant','spear','staff','issuer symbol']),
 'insect_or_scorpion': (['vṛścika','makṣikā','śakuni','pakṣin'], 'Count leg-like projections, distinguish wings from arms and inspect the terminal tail before choosing small-animal class.', ['bird','scorpion','fly or bee','human or geometric design']),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    if path.exists():
        raise RuntimeError('Refusing to overwrite ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert sha(MW) == EXPECTED_MW_SHA
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    prior = json.loads(PRIOR.read_text(encoding='utf-8'))['rows']
    source_text = MW.read_text(encoding='utf-8')
    records = {}
    line = 1
    previous_end = 0
    for match in re.finditer(r'<L>(.*?)<LEND>', source_text, re.S):
        line += source_text.count('\n', previous_end, match.start())
        body = '<L>' + match.group(1)
        head = re.match(r'<L>(.*?)<pc>(.*?)<k1>(.*?)<k2>', body)
        assert head
        records[head[1]] = dict(entry_id=head[1], page_column=head[2], slp1=head[3],
                               start_line=line,
                               source_record=body)
        line += source_text.count('\n', match.start(), match.end())
        previous_end = match.end()
    rows = []
    for original in prior:
        r = dict(original)
        r['role'] = 'Reused selected comparison; its catalogue assignment is reviewed separately.'
        r['addition_status'] = 'reused-run-v6'
        r['source_run'] = PRIOR.relative_to(ROOT).as_posix()
        rows.append(r)
    for word, head, slp1, identity, page, meaning, period, role in ADDITIONS:
        rows.append(dict(word=word, slp1=slp1, comparison_headword=head,
                         entry_id=identity, page_column=page, meaning=meaning,
                         period=period, source=SOURCE, url=SOURCE_URL,
                         role=role, addition_status='new-selected-sense-2026-10-12'))
    checks = []
    selected_records = []
    for r in rows:
        record = records.get(r['entry_id'])
        assert record, r
        assert record['slp1'] == r['slp1'], (r,record)
        assert record['page_column'] == r['page_column'], (r,record)
        idx = [x for x in index[r['slp1']] if x['entry_id'] == r['entry_id']]
        assert len(idx) == 1 and idx[0]['page_column'] == r['page_column'], (r,idx)
        checks.append(dict(word=r['word'], entry_id=r['entry_id'], headword_match=True,
                           page_column_match=True, existing_index_match=True,
                           source_record_sha256=hashlib.sha256(record['source_record'].encode()).hexdigest()))
        r['source_record_url'] = SOURCE_URL + '#L' + str(record['start_line'])
        r['dictionary_citations'] = re.findall(r'<ls(?: [^>]*)?>(.*?)</ls>', record['source_record'])
        r['sense_id'] = 'MW-' + r['entry_id']
        if r['word'] == 'danta':
            r['supporting_records'] = [{'entry_id':'89783','slp1':'dat','page_column':'467,2','relation':'cross-reference target explicitly gives tooth'}]
        if r['word'] == 'saṃpuṭa':
            r['spelling_note'] = 'Canonical digitized lookup sampuṭa; saṃpuṭa records the nasalized display spelling.'
        if r['word'] == 'dhanus':
            r['spelling_note'] = 'MW indexes dhanus; dhanuṣ (99604) is its compound form, while dhanuḥ is a declined form.'
        selected_records.append({'word':r['word'],**record})
    assert len(rows) == 96 and len(ADDITIONS) == 40
    assert len({r['word'] for r in rows}) == len(rows)
    by = {r['word']:r for r in rows}
    families = {}
    for key,(words,argument,rivals) in FAMILIES.items():
        assert all(w in by for w in words), (key, words)
        families[key] = dict(words=words, sense_ids=[by[w]['sense_id'] for w in words],
                             basis=argument, rivals=rivals,
                             scope='Graphic/semantic comparison; contributor reviewed no new complete-context result tables.')
    write(HERE/'senses.json',dict(scope='Authored selected semantic comparisons. Dictionary literary citations date cited uses, not an Indus reading or first attestation.',
                                 previous_senses=56, additional_senses=40, rows=rows))
    write(HERE/'family-links.json',dict(scope='Candidate graphic/semantic family keys before inspection of new complete-context outcomes. Root integrates these with the final visual family map.', families=families))
    write(RAW/'selected-dictionary-records.json',dict(source_path=MW.relative_to(ROOT).as_posix(), rows=selected_records))
    write(HERE/'verification.json',dict(status='pass', selected_records=96, new_senses=40,
                                       reused_senses=56, family_keys=len(families),
                                       headword_page_index_checks=checks,
                                       inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [MW,INDEX,PRIOR]],
                                       source_body_treatment='Full selected records remain in ignored data/raw.',
                                       limitations=['Gloss and chronology selection manually checked against exact record bodies.',
                                                    'No independent first-attestation research or Bronze Age word dating.',
                                                    'No full new-context statistical tables were inspected by this contributor.']))
    print(json.dumps({'status':'pass','senses':len(rows),'additional':40,'families':len(families)},ensure_ascii=False))


if __name__ == '__main__':
    main()
