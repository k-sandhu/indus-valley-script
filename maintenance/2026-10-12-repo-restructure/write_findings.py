"""Create measured cards with source-field checks and a separate numeric audit."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'experiments/2026-10-12-repo-restructure'
AUDIT = []
CACHE = {}


def load(path):
    if path not in CACHE:
        CACHE[path] = json.loads((ROOT/path).read_text(encoding='utf-8'))
    return CACHE[path]


def check(path, pointer, expected, digits=None, scale=1):
    node = load(path)
    for key in pointer.split('/'):
        key = key.replace('~1','/').replace('~0','~')
        node = node[int(key)] if isinstance(node,list) else node[key]
    value = node*scale if scale != 1 else node
    compared = round(value,digits) if digits is not None else value
    assert compared == expected, (path,pointer,node,expected)
    AUDIT.append(dict(path=path, field=pointer, source_value=node, displayed_value=expected,
                      decimal_places=digits, scale=scale, pass_check=True,
                      source_sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
    return path+'#/'+pointer


CARDS = []


def card(title, status, area, day, ids, population, result, scope, evidence):
    CARDS.append((title,status,area,day,ids,population,result,scope,evidence))


def main():
    root_score='research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json'
    order='experiments/2026-10-02-six-hour/markov-order2/main/results.json'
    loss='experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json'
    gap='research/methods/results/gap_design_matched/gap_design_matched.json'
    num='research/methods/results/numerical_equalities/numerical_equalities_audit.json'
    census='experiments/2026-10-06-evidence-census/synthesis/coverage.json'
    joins='experiments/2026-10-06-evidence-census/synthesis/join-summary.json'
    base='experiments/2026-10-12-structure-first/'
    families=base+'step1-signs/run-2026-10-12/summary.json'
    images=base+'step2-image-text/run-2026-10-12-v3/summary.json'
    lines=base+'step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json'
    alternation=base+'step3-segmentation/run-alternation-2026-10-12/summary.json'
    rehearsal=base+'step5-rehearsal/run-segmentation-2026-10-12/summary.json'
    edge=base+'step6-language/run-2026-10-12/summary.json'
    strokes=base+'step4-numerals/run-2026-10-12/summary.json'
    seal='experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json'
    review='experiments/2026-10-12-seal-text-identity/run-2026-10-12/review-response.json'
    card('Sequential prediction on unique texts','verified-computation','structure','2026-10-02',['ROOT-02'],
         '1,596 distinct complete right-to-left single-line strings, 6,413 noninitial signs',
         'Previous-sign information improved held-out log score by 0.848 bits per noninitial sign on 1,596 distinct strings and 6,413 noninitial signs.',
         'The comparator is the selected independent position/site/type baseline, with physical aliases retained in grouping. The uniqueness-conditioned reference repeats nested fitting. This measures order in the selected transcriptions; the measurement date follows UTC in the original work log.',
         [check(root_score,'observed/gain_bits_per_noninitial_sign',.848,3),check(root_score,'observed/records',1596),check(root_score,'observed/noninitial_tokens',6413)])
    pop='8,009 artificial known-slot masks in 1,596 distinct strings'
    card('Second-order known-slot restoration','verified-computation','structure','2026-10-02',['MARKOV-03'],pop,
         'Second-order context reached 37.27% exact top-one recovery, against 34.59% for first order, on the same 8,009 masks.',
         'The benchmark hides one known position, holds physical aliases and repeated texts together and tunes on training folds. First order is the matched comparator. A known position and count are supplied; physical damage recovery requires additional observations.',
         [check(order,'models/Markov2/top1',37.27,2,100),check(order,'models/Markov1/top1',34.59,2,100),check(order,'correspondence/verified_queries_per_model',8009)])
    card('Second-order probability loss worsens','verified-computation','structure','2026-10-02',['MARKOV-03'],pop,
         'Bucket probability loss rose from 5.1194 bits per slot for first order to 5.2472 for second order.',
         'The models use the same held-out masks and the saved alphabet with an unknown-target bucket. This endpoint measures assigned probability, whereas the preceding card measures the highest-ranked graphic. It is conditional on the recorded masks and fitted models.',
         [check(order,'models/Markov1/bucket_cross_entropy_bits',5.1194,4),check(order,'models/Markov2/bucket_cross_entropy_bits',5.2472,4)])
    assert len(load(loss)['folds'])==5 and all(f['chosen_alpha'] is None for f in load(loss)['folds'])
    card('Loss selection returns first order','exploratory','structure','2026-10-02',['MARKOV-04'],pop,
         'All five folds selected backoff-only when second-order smoothing was chosen by inner probability loss. The outcome reproduced first-order top-one recovery of 34.5861%.',
         'This comparison was specified after the earlier second-order endpoint and reuses its queries. The candidate family includes pure first-order backoff. The result concerns that family and loss criterion.',
         [loss+'#/folds',check(loss,'models/Markov2/top1',34.5861,4,100)])
    card('Gap-count estimator loses to constant one','failed','structure','2026-10-02',['ROOT-08','METHODS-gap_design_matched'],
         '1,596 artificial missing-count queries, counts restricted to one through three',
         'The sampling-matched local estimator recovered the count in 46.30% of queries, below the constant-one control’s 51.07%.',
         'The adjustment matches the artificial sampling law while retaining models and queries. The comparator always predicts one erased sign. Physical gap geometry and surviving traces were absent, and the declared candidate counts exclude larger gaps.',
         [check(gap,'design_matched_models/local/exact_count_accuracy',46.30,2,100),check(gap,'design_matched_models/local/constant_one_glyph_design_control_accuracy',51.07,2,100)])
    assert len(load(num)['all_admissible_solutions'])==4
    card('Four conditional numeral solutions','verified-computation','numerals','2026-10-02',['ROOT-13','METHODS-numerical_equalities'],
         'Positive integer solutions of the published assumed equalities',
         'The exact audit retained four positive-integer solutions. Restricting L to 8–13 retained only (L, S, v) = (10, 8, 6).',
         'The audit enumerates solutions of the published equalities and applies the source’s additional range. It checks conditional arithmetic; object identity, equal-quantity premises and the physical range require their own source evidence.',
         [num+'#/all_admissible_solutions',num+'#/range_sensitivities/L_8_to_13'])
    card('Catalogue identifiers missing from export','source-review','data','2026-10-07',['EVIDENCE-CENSUS-SYNTHESIS-01'],
         '493 identifiers across 19 CISI volume 1 ranges in Gujarat and north India',
         'Of 493 catalogue identifiers, 327 matched local keys and 166 were absent. The absent keys comprised 75 in pottery/graffiti sections and 91 in other sections.',
         'The reviewed source census compares selected catalogue ranges with the pinned export and source-attested aliases. An absent key is an unresolved object join. This denominator covers those ranges and supplies no worldwide recall estimate.',
         [check(census,'summary/CISI1_BC_entries',493),check(census,'summary/CISI1_BC_matching_keys',327),check(census,'summary/CISI1_BC_absent_keys',166),check(census,'summary/CISI1_BC_absent_graffiti_or_pottery_sections',75),check(census,'summary/CISI1_BC_absent_seal_impression_tablet_other_sections',91)])
    card('Museum joins are a lower bound','source-review','data','2026-10-07',['EVIDENCE-CENSUS-SYNTHESIS-01'],
         '114 inspected inscription-confirmed original museum records',
         'The reviewed museum join count was 68 of 114 original records, leaving 46 unresolved records.',
         'The count follows the reviewed identifier and concordance joins in the census. The first comparison block had fewer joins; additional joins did not receive all paired-field comparisons. These are inspected-record minima and unresolved matches within the bounded collection frame.',
         [check(joins,'museum_original_records',114),check(joins,'confirmed_identifier_joins',68),check(joins,'unconfirmed_records',46)])
    card('Site frame coverage in the local export','source-review','data','2026-10-07',['EVIDENCE-CENSUS-SYNTHESIS-01'],
         '5,680 local face rows compared with the census site-label frame',
         'The census frame represented 5,652 of 5,680 local faces across 115 site/provenance entities assembled from 123 batch rows.',
         'Coverage refers to normalized export rows assigned to the source-label frame after overlap removal. Face rows and provisional object families have different denominators. Worldwide published-find coverage remains unknown.',
         [check(census,'summary/represented_local_faces',5652),check(census,'summary/local_all_faces',5680),check(census,'summary/site_or_provenance_entities_after_aliases',115),check(census,'summary/raw_batch_rows',123)])
    pop='1,859 distinct clean texts, 8,535 signs, held out by dependence component'
    card('Graphic base families improve prediction','frozen-evaluation','structure','2026-10-12',['SIGN-FAMILIES-2026-10-12'],pop,
         'Coder 1’s base families improved prediction by 0.0219 bits per sign beyond the ungrouped model, with p = 0.005 against size-matched random groupings.',
         'The endpoint predicts original Wells codes using a family backoff feature. Both coders used ordered glyph sheets and were instances of one model. A later contiguous-cut comparison found that Wells ordering carries much of the gain; it remains a separate exploratory check.',
         [check(families,'grouping_tests/B_coder1/gain_bits',.0219,4),check(families,'grouping_tests/B_coder1/p_value',.005,3)])
    card('Agreement between the two sign codings','verified-computation','images','2026-10-12',['SIGN-FAMILIES-2026-10-12'],
         '577 attested codes coded by two instances of one model',
         'The two codings had adjusted Rand agreement 0.884 unweighted and 0.975 token-weighted across 577 codes.',
         'The statistic compares assignments to graphic families, with token weighting favoring common codes. Both coders worked from code-ordered sheets, so a human coding from shuffled sheets is the proposed independent check.',
         [check(families,'coder_agreement/ari_unweighted',.884,3),check(families,'coder_agreement/ari_token_weighted',.975,3),check(families,'coder_agreement/codes_compared',577)])
    card('Modifier signatures fail the grouping test','failed','structure','2026-10-12',['SIGN-FAMILIES-2026-10-12'],pop,
         'Grouping by modifier signature failed the random-grouping test, with p = 0.11.',
         'The endpoint groups added elements across different graphic bases and predicts Wells codes. The comparator randomizes groups of the same sizes. Failure concerns the declared signature scheme and population.',
         [check(families,'grouping_tests/modifier_signature/p_value',.11,2),check(families,'grouping_tests/modifier_signature/passes',False)])
    card('Base families reduce unseen-code loss','frozen-evaluation','structure','2026-10-12',['SIGN-FAMILIES-2026-10-12'],
         '267 held-out signs with no training occurrence of their Wells code',
         'For unseen codes, base-family backoff lowered loss from 14.60 to 14.19 bits per sign.',
         'These are held-out tokens whose fine code is absent from the training fold. The comparator is the ungrouped Kneser–Ney baseline. Published Parpola and Mahadevan groupings are separate alternatives in the same output.',
         [check(families,'grouping_tests/B_coder1/by_training_frequency/seen0/tokens',267),check(families,'grouping_tests/B_coder1/by_training_frequency/seen0/baseline_bits',14.60,2),check(families,'grouping_tests/B_coder1/by_training_frequency/seen0/class_bits',14.19,2)])
    for genre,title,accuracy,majority,n in [('bas_relief','Bas-relief image prediction',24.8,21.5,149),('incised','Incised-tablet image prediction',57.4,48.1,54),('copper','Copper image prediction fails',19.2,26.9,26)]:
        card(title,'failed' if genre=='copper' else 'frozen-evaluation','tablets','2026-10-12',['IMAGE-TEXT-TABLETS-2026-10-12'],
             f'{n} text types in the {genre.replace("_"," ")} tablet cohort',
             f'Held-out image-class prediction reached {accuracy}% against a {majority}% majority comparator.',
             'The classifier predicts an image class from other text types in the same tablet genre. Class normalization and corrected populations follow the v3 endpoint. Recurrent-text purity is a separate measurement; this outcome is confined to the recorded genre.',
             [check(images,genre+'/2c/accuracy',accuracy,1,100),check(images,genre+'/2c/majority_rate',majority,1,100),check(images,genre+'/2c/text_types',n)])
    card('Copper groups do not transfer to seal animals','failed','seals','2026-10-12',['IMAGE-TEXT-TABLETS-2026-10-12'],
         '1,209 seal text/animal pairs in classes shared with copper tablets',
         'Copper class-specific sign groups occurred on matching-animal seals 3 times against 3.01 expected, with p = 0.62.',
         'The permutation comparator tests transfer of copper image-specific groups to matching field animals on seals. The recorded power is higher for fivefold than twofold enrichment. The result leaves smaller effects unresolved.',
         [check(images,'2d_copper_to_seals/matching_hits',3),check(images,'2d_copper_to_seals/null_mean',3.01,2),check(images,'2d_copper_to_seals/p_value',.62,2),check(images,'2d_copper_to_seals/seal_text_animal_pairs',1209)])
    card('Lines recur more than crossing windows','frozen-evaluation','structure','2026-10-12',['LINE-BREAKS-SEGMENTATION-2026-10-12'],
         '69 usable faces with catalogue line divisions',
         'Under the conservative line order, 23 faces had higher line recurrence, 4 had higher crossing-window recurrence and 42 tied; p = 0.0003.',
         'Lines are sought in clean single-line texts from another object. Crossing windows have matching lengths, and the better crossing order per face supplies the conservative comparator. The outcome uses the eligible catalogue-divided faces, mostly square seals.',
         [check(lines,'conservative_best_order/faces_line_higher',23),check(lines,'conservative_best_order/faces_straddle_higher',4),check(lines,'conservative_best_order/ties',42),check(lines,'conservative_best_order/sign_test_two_sided_p',.0003,4),check(lines,'faces_used',69)])
    card('Indus alternation has few stems','frozen-evaluation','structure','2026-10-12',['LINE-BREAKS-SEGMENTATION-2026-10-12'],
         '68 stems from Dirichlet-process segments of the distinct clean texts',
         'Only 2 of 68 segment-derived stems alternated, a rate of 0.029. The rate lay inside all four matched comparison ranges.',
         'The selected segmenter was chosen on the readable-corpus rehearsal. Comparison words are subsampled to the Indus unit-length profile. The protocol treats this rate as descriptive because alternation fails to separate known systems at this scale.',
         [check(alternation,'ivs_chosen_alternation/stems',68),check(alternation,'ivs_chosen_alternation/alternating_stems',2),check(alternation,'ivs_chosen_alternation/alternation_rate',.029,3),alternation+'#/comparisons'])
    all_boundary=sum(c['scores']['all_boundaries']['boundary_f1'] for c in load(rehearsal)['cohorts'].values())/4
    assert round(all_boundary,3)==.485
    card('Mean segmentation accuracy at Indus scale','frozen-evaluation','methods','2026-10-12',['REHEARSAL-SEGMENTATION-2026-10-12'],
         'Four readable cohorts with word boundaries hidden and lengths matched where feasible',
         'The best mean boundary F1 was 0.531 for the Dirichlet-process segmenter, against 0.485 for a boundary everywhere.',
         'F1 combines boundary precision and recall against edited word divisions. The mean weights the four cohorts equally; it does not estimate Indus word-boundary accuracy. The recorded cohorts omit the acquired Linear B sample.',
         [check(rehearsal,'mean_boundary_f1/dp_unigram',.531,3),rehearsal+'#/cohorts'])
    card('Seal-legend segmentation rehearsal','frozen-evaluation','methods','2026-10-12',['REHEARSAL-SEGMENTATION-2026-10-12'],
         '309 distinct Ur III seal legends with complete edited word units',
         'On Ur III seal legends, branching entropy reached boundary F1 0.692 against 0.557 for a boundary everywhere.',
         'The input conceals word boundaries and retains the seal-legend genre. The comparison scores predicted boundaries against the edition’s divisions. Transfer to Indus boundaries needs observed divisions or spacing evidence.',
         [check(rehearsal,'cohorts/sumerian_seals_all/scores/branching_entropy/boundary_f1',.692,3),check(rehearsal,'cohorts/sumerian_seals_all/scores/all_boundaries/boundary_f1',.557,3),check(rehearsal,'cohorts/sumerian_seals_all/texts',309)])
    card('Initial and final sign concentration differs','frozen-evaluation','structure','2026-10-12',['STRUCTURAL-TYPOLOGY-2026-10-12'],
         '1,859 distinct clean Indus texts',
         'Normalized initial-minus-final sign entropy was +0.260, against a shuffle range of −0.017 to +0.018.',
         'The statistic compares diversity at the two ends of complete texts with within-text shuffling. It describes concentration in the selected population. Genre and sign-versus-word units change the comparison statistic, so the frozen language rule leaves candidates tied.',
         [check(edge,'profiles/ivs_all_clean/edge_asymmetry/asymmetry_initial_minus_final',.260,3),check(edge,'profiles/ivs_all_clean/edge_asymmetry/shuffle_p2_5',-.017,3),check(edge,'profiles/ivs_all_clean/edge_asymmetry/shuffle_p97_5',.018,3)])
    card('Edge asymmetry changes with the unit','frozen-evaluation','comparative','2026-10-12',['STRUCTURAL-TYPOLOGY-2026-10-12'],
         'Edited Ur III seal legends at sign and word level',
         'Ur III seal-legend edge asymmetry was −0.204 by sign and +0.079 by word.',
         'The sign and complete-word cohorts differ by one eligible legend in the saved profile. Both compare normalized initial and final entropy. The reversal shows why the statistic requires matched unit and genre for language comparisons.',
         [check(edge,'profiles/sumerian_seals/sign_level/edge_asymmetry/asymmetry_initial_minus_final',-.204,3),check(edge,'profiles/sumerian_seals/word_level/edge_asymmetry/asymmetry_initial_minus_final',.079,3)])
    card('Stroke values are tied to following items','frozen-evaluation','numerals','2026-10-12',['NUMERAL-BEHAVIOUR-2026-10-12'],
         'Clean Indus stroke tokens with the next sign treated as item; size-matched Ur III counts',
         'Indus had 3.61 distinct values per qualifying item, against 4.53–5.15 in the size-matched Ur III interval.',
         'The endpoint treats the following sign as the item and compares observed stroke counts with edited Ur III quantities. Direction, units and selection have separate sensitivities. The result measures fixity of combinations under that representation.',
         [check(strokes,'ivs_clean/mean_distinct_values_per_item',3.61,2),check(strokes,'ur3_subsampled_to_ivs/mean_distinct_values_per_item/p2_5',4.53,2),check(strokes,'ur3_subsampled_to_ivs/mean_distinct_values_per_item/p97_5',5.15,2)])
    items={v['item']:v for v in load(strokes)['ivs_clean']['items']}
    assert round(items['520']['tokens']*items['520']['top_value_share'])==38
    assert round(items['585']['tokens']*items['585']['top_value_share'])==16
    card('Two near-fixed stroke combinations','exploratory','numerals','2026-10-12',['NUMERAL-BEHAVIOUR-2026-10-12'],
         'Clean stroke tokens followed by code 520 or code 585',
         'Code 520 followed three strokes in 38 of 41 cases, and code 585 followed seven in 16 of 17 cases.',
         'The counts summarize particular combinations selected in the post-outcome item inspection. The saved item table combines stroke families; the report identifies the dominant groups as tall strokes. These examples are within the broader fixed-value comparison and do not supply an independent quantity.',
         [strokes+'#/ivs_clean/items',base+'step4-numerals/REPORT.md'])
    card('Recurring seal texts span sites','frozen-evaluation','seals','2026-10-12',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],
         '1,430 complete single-line seals from named South Asian sites, one face per family',
         'There were 65 recurring texts on 174 of 1,430 eligible seals; 41 of the recurring texts spanned sites.',
         'Recurrence is exact text identity under the selected fine-code transcription, with at least two signs and one face per family. Site and motif labels come from catalogues. A second-face and merged-variant sensitivity are separate from this population.',
         [check(seal,'eligible_seal_objects',1430),check(seal,'shared_texts',65),check(seal,'seal_objects_in_shared_texts',174),check(seal,'shared_texts_spanning_sites/all',41)])
    by_length=load(seal)['S3_whole_text_reuse']['by_length']
    long_count=sum(v['seals'] for k,v in by_length.items() if int(k)>=6)
    long_pairs=sum(v['observed_identical_pairs'] for k,v in by_length.items() if int(k)>=6)
    assert (long_count,long_pairs)==(445,0)
    card('Long seal texts do not repeat','frozen-evaluation','seals','2026-10-12',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],
         '445 eligible seals with six or more signs',
         'No two of the 445 seals with six or more signs shared their complete text.',
         'The count uses exact complete text identity in the named-site, single-line, one-face seal population. It covers the recorded export and selected faces; it does not count damaged or unselected second faces.',
         [seal+'#/S3_whole_text_reuse/by_length'])
    card('Frozen duplicate-locality test does not pass','frozen-evaluation','seals','2026-10-12',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],
         '65 recurring texts among the 1,430 eligible seals',
         'The mean same-site share was 0.473 against 0.448 under shuffled site labels, with p = 0.31 and ratio to chance 1.06.',
         'The frozen statistic weights each recurring text equally and shuffles sites among all eligible seals. A later length-stratified null and site breakdown give different results and remain exploratory. This card records the original primary locality endpoint.',
         [check(seal,'S1_all/text_weighted/observed',.473,3),check(seal,'S1_all/text_weighted/null_mean',.448,3),check(seal,'S1_all/text_weighted/p_one_sided',.31,2),check(seal,'S1_all/text_weighted/ratio_to_null_mean',1.06,2)])
    card('Unicorn pairs account for motif matches','exploratory','seals','2026-10-12',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],
         '130 identical-text seal pairs with both field motifs recorded',
         'Of 89 matching-motif pairs, 88 were unicorn pairs. Only 1 of 42 pairs involving another animal shared its motif.',
         'This is the post-review breakdown of motif concordance within identical-text pairs. Catalogue motif classes and within-site shuffling define the comparison; the breakdown itself was selected after the pooled endpoint.',
         [check(review,'E_motif_pairs/pairs_with_both_motifs',130),check(review,'E_motif_pairs/same_motif',89),check(review,'E_motif_pairs/unicorn_unicorn',88),check(review,'E_motif_pairs/pairs_involving_non_unicorn',42),check(review,'E_motif_pairs/same_motif_among_non_unicorn',1)])
    card('Sealings match seals from other cities','verified-computation','seals','2026-10-12',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],
         '16 sealings or tags whose texts match an eligible seal, representing six texts',
         'Of 16 matching sealings or tags, 13 matched only seals found elsewhere. Those 13 carried 4 of the 6 distinct matching texts.',
         'The review recount corrects the original summary’s other-site count. Matching concerns catalogue text identity and recorded find sites. It leaves movement of the seal, sealed goods or formula unresolved.',
         [check(review,'G_S5_recount/rows',16),check(review,'G_S5_recount/rows_matching_only_other_site_seals',13),check(review,'G_S5_recount/distinct_texts',6),check(review,'G_S5_recount/texts_matching_only_other_site_seals',4)])
    copies='experiments/2026-10-02-six-hour/null-calibration/main/results.json'
    card('Literal-copy reference calibration','synthetic','methods','2026-10-02',['NULL-08'],
         '1,000 generated literal-copy populations under a known law',
         'At nominal 5%, matched object references rejected 5.4% of literal-copy populations, against 15.9% for record-wise references.',
         'The same nested prediction statistic is calibrated under an invented literal-copy process. The comparison changes the reference unit while retaining observations. It tests implementation under that law and supplies no archaeological estimate of copying.',
         [check(copies,'aggregate/physical_copies~1block_columns/rejections/0.05/rate',5.4,1,100),check(copies,'aggregate/physical_copies~1record_columns/rejections/0.05/rate',15.9,1,100)])
    noisy='experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json'
    card('Imperfect-face reference calibration','synthetic','methods','2026-10-02',['NULL-05'],
         '1,000 generated populations with two imperfect faces per object',
         'At nominal 5%, matched face-vector references rejected 5% of populations, against 11% for record-wise references.',
         'The generated observation law uses the specified paired-error mechanism. Whole vectors and individual-record columns are competing references for the saved statistic. The calibration is conditional on that known mechanism.',
         [check(noisy,'aggregate/noisy_faces~1face_vectors/rejections/0.05/rate',5,0,100),check(noisy,'aggregate/noisy_faces~1record_columns/rejections/0.05/rate',11,0,100)])
    selector='experiments/2026-10-02-six-hour/reference-selector/main/results.json'
    counts={}
    for row in load(selector)['rows']:
        counts[row['algorithm']]=counts.get(row['algorithm'],0)+int(row['exact_recovery'])
    assert sorted(counts.values())==[168,283,309,310],counts
    card('Reference-only symbol-map selection','synthetic','methods','2026-10-02',['CRYPTO-08'],
         '384 generated mapping conditions in 48 fresh systems',
         'The reference-only selector recovered 309 of 384 symbol maps, against 283 for fixed graph mapping and 168 for fixed slot mapping.',
         'The generated systems supply a known reference whose held-out score chooses the mapping objective. The source-family diagnostic is separate. Recovery measures the hidden generated bijection and depends on the supplied reference process.',
         [selector+'#/rows'])
    assert len(CARDS)==33
    records=[]
    for i,(title,status,area,day,ids,population,result,scope,evidence) in enumerate(CARDS,1):
        identifier=f'F-{i:04d}'
        slug=''.join(c.lower() if c.isalnum() else '-' for c in title)
        while '--' in slug:slug=slug.replace('--','-')
        path=ROOT/f'knowledge/findings/{identifier}-{slug.strip("-")}.md'
        path.parent.mkdir(parents=True,exist_ok=True)
        fields=dict(id=identifier,title=title,status_class=status,area=area,date=day,registry_ids=ids,
                    evidence=evidence,population=population,authors=['Codex (GPT-6; API harness)'])
        front='\n'.join(f'{k}: {json.dumps(v,ensure_ascii=False)}' for k,v in fields.items())
        links=[]
        for source in evidence:
            p,_,fragment=source.partition('#')
            target=os.path.relpath(ROOT/p,path.parent).replace('\\','/')
            links.append(f'- [{p}]({target})'+(f', JSON field `{fragment}`.' if fragment else '.'))
        text='---\n'+front+'\n---\n\n# Finding\n\n'+result+'\n\n# Evidence\n\n'+'\n'.join(links)+'\n\n# Scope\n\n'+scope+'\n'
        path.write_text(text,encoding='utf-8',newline='\n')
        records.append(dict(id=identifier,path=path.relative_to(ROOT).as_posix(),source_paths=evidence))
    # Derived-count checks are documented separately from rounded scalar displays.
    derived=dict(loss_selected_backoff_folds=5,conditional_positive_solutions=4,
                 mean_all_boundary_f1=all_boundary,near_fixed_counts={'520':[38,41],'585':[16,17]},
                 long_seals=long_count,long_identical_pairs=long_pairs,selector_counts=counts)
    (RUN/'finding-number-audit.json').write_text(json.dumps(dict(status='pass',cards=records,scalar_checks=AUDIT,derived_checks=derived),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Wrote',len(records),'findings;',len(AUDIT),'scalar source checks passed')


if __name__=='__main__':main()
