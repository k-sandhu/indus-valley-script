"""Build the research report from saved evidence and numerical results."""
from __future__ import annotations
import argparse,json,html,re
from datetime import datetime,timezone
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
START=datetime(2026,10,1,23,7,54,tzinfo=timezone.utc)
INK=colors.HexColor('#263744');BLUE=colors.HexColor('#24486c');TEAL=colors.HexColor('#2b847a')
LIGHT=colors.HexColor('#eef3f5');ORANGE=colors.HexColor('#9e542f')


def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def pct(x):return f'{100*x:.1f}%'
def ci(xs,scale=1,decimals=3):return f'{xs[0]*scale:.{decimals}f} to {xs[1]*scale:.{decimals}f}'

def tidy(s):
    """Space prose joins without altering links, catalogue IDs or executable code."""
    parts=re.split(r'(<[^>]+>|&(?:#\d+|#x[\da-fA-F]+|\w+);|(?<![A-Za-z0-9])[a-f0-9]{32,64}(?![A-Za-z0-9])|(?:[\w.-]+[/\\])+[\w.-]+\.(?:py|md|json|jsonl|csv|pdf|html))',str(s))
    for i in range(0,len(parts),2):
        t=parts[i]
        t=re.sub(r'([a-z])(?=\d)',r'\1 ',t)
        t=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',t)
        t=re.sub(r'(?<=%)(?=[A-Za-z])',' ',t)
        t=re.sub(r';(?=\S)','; ',t)
        t=re.sub(r',(?=[A-Za-z])',', ',t)
        parts[i]=t
    return ''.join(parts)


def build(final=False):
    generated=datetime.now(timezone.utc)
    elapsed=(generated-START).total_seconds()
    if final and elapsed<4*3600:raise ValueError('Final edition cannot precede four hours of elapsed research time')
    fontdir=Path('C:/Windows/Fonts')
    for name,file in [('Report','segoeui.ttf'),('ReportBold','segoeuib.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
    pdfmetrics.registerFontFamily('Report',normal='Report',bold='ReportBold',italic='Report',boldItalic='ReportBold')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyR',fontName='Report',fontSize=10.2,leading=14.6,textColor=INK,spaceAfter=8))
    styles.add(ParagraphStyle(name='SmallR',fontName='Report',fontSize=8.4,leading=11.5,textColor=INK,spaceAfter=7))
    styles.add(ParagraphStyle(name='TitleR',fontName='ReportBold',fontSize=28,leading=32,textColor=BLUE,spaceAfter=16))
    styles.add(ParagraphStyle(name='HeadingR',fontName='ReportBold',fontSize=17,leading=21,textColor=BLUE,spaceAfter=12))
    styles.add(ParagraphStyle(name='SubR',fontName='ReportBold',fontSize=11.5,leading=15,textColor=TEAL,spaceBefore=7,spaceAfter=6))
    styles.add(ParagraphStyle(name='CellR',fontName='Report',fontSize=8.5,leading=11.5,textColor=INK))
    styles.add(ParagraphStyle(name='CodeR',fontName='Courier',fontSize=8,leading=11,textColor=INK,spaceAfter=8))
    story=[]
    def p(s,small=False):story.append(Paragraph(tidy(s),styles['SmallR' if small else 'BodyR']))
    def h(s):story.append(Paragraph(s,styles['HeadingR']))
    def sub(s):story.append(Paragraph(s,styles['SubR']))
    def page(s):story.append(PageBreak());h(s)
    def table(rows,widths=None):
        cells=[[Paragraph(tidy(x),styles['CellR']) for x in row] for row in rows]
        t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),
             ('LINEBELOW',(0,0),(-1,0),.7,BLUE),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d9e1e5')),
             ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
             ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        story.extend([t,Spacer(1,10)])
    def figure(name,caption,width=500):
        path=ROOT/'output/figures'/f'{name}.png';iw,ih=ImageReader(str(path)).getSize()
        story.append(Image(str(path),width=width,height=width*ih/iw));p(caption,True)
    def code(s):story.append(Paragraph(html.escape(s).replace('\n','<br/>'),styles['CodeR']))
    def source(title,url):return f'<link href="{html.escape(url,quote=True)}" color="#24486c">{html.escape(title)}</link>'

    nested=load('research/methods/results/nested_primary/nested_results.json')
    unique=load('research/methods/results/nested_unique_preserved_aliases/nested_results.json')
    collapsed=load('research/methods/results/nested_collapsed/nested_results.json')
    templates=load('research/methods/results/templates_extended/template_results.json')
    office=load('research/methods/results/workflow_templates/template_results.json')
    restore=load('results/restoration/benchmark.json');rc=load('results/restoration_collapsed/benchmark.json')
    site_restore=load('results/restoration_crosssite/crosssite.json')
    independent=load('results/independent_annotator/candidate_event_test.json')
    quality=load('results/independent_annotator/photo_quality_sensitivity.json')
    gap=load('results/gap_restoration/gap_benchmark.json')
    gap_design=load('research/methods/results/gap_design_matched/gap_design_matched.json')
    font_fresh=load('research/visual_digitization/font_fresh20/evaluation_frozen_endpoint.json')
    chart=load('research/chart_reference/manual_numeric_reference.json')
    seal=load('results/context/independent_text/seal_tablet.json');bull=load('results/context/independent_text/bull1_other.json')
    pairs=load('results/paired/summary.json')
    joint=load('research/methods/results/joint_nested_primary/joint_nested_results.json')
    extended_path=ROOT/'research/methods/results/joint_nested_primary_1000/joint_nested_results.json'
    extended=load(str(extended_path.relative_to(ROOT))) if extended_path.exists() else None
    # Select the extension only when its declared reference is complete.
    if extended:
        candidates=[(k,v) for k,v in extended.items() if isinstance(v,dict) and v.get('permutations',0)>=1000 and
                    not v.get('in_progress',False) and 'p_one_sided' in v and 'metadata' in k]
        if candidates:joint=extended
    nulls=[(k,v) for k,v in joint.items() if isinstance(v,dict) and 'metadata' in k and 'p_one_sided' in v]
    metadata_null=nulls[0][1] if nulls else None
    unique_joint_path=ROOT/'research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json'
    unique_joint=load(str(unique_joint_path.relative_to(ROOT))) if unique_joint_path.exists() else None
    unique_null=unique_joint.get('null_position_metadata') if unique_joint else None
    if final and (not metadata_null or metadata_null.get('permutations',0)<1000):
        raise ValueError('Final report requires the complete stronger1,000-shuffle metadata reference')
    if final and (not unique_null or unique_null.get('in_progress',True) or unique_null.get('permutations',0)<1000):
        raise ValueError('Final report requires the complete unique-conditioned1,000-shuffle reference')

    p('INDUS SCRIPT RESEARCH / 1-2 OCTOBER 2026',True)
    story.append(Paragraph('Structural constraints<br/>and the limits of decipherment',styles['TitleR']))
    p('<b>No accepted reading is proposed.</b> This investigation did not establish a phonetic value, identify a word, choose a language, or translate an inscription. The contribution is a reproducible set of structural tests, prediction benchmarks, photographic checks and failed-hypothesis audits.')
    p(f"Edition: {'Final research report' if final else 'WORKING DRAFT - investigation ongoing'}. Generated {generated:%Y-%m-%d %H:%M:%S UTC}. Research began {START:%Y-%m-%d %H:%M:%S UTC}. Elapsed research time: {elapsed/3600:.2f} hours.")
    sub('The strongest reproducible results')
    table([['Finding','Evidence','What it establishes'],
       ['Sign-order dependence',f"{nested['observed']['gain_bits_per_noninitial_sign']:.3f}bits per noninitial sign; grouped95% interval {ci(nested['observed']['gain_95pct_group_bootstrap_ci'])}.",'Transferable graphic sequencing beyond independent position and known metadata.'],
       ['Second manual annotator',f"74faces; +{independent['all_clear_weighting']['gain_bits_per_noninitial_candidate_event']:.3f}bits per candidate event.",'The order result survives a different transcription, with shared catalogue/source limits.'],
       ['One known missing slot',f"Exact top-one {pct(restore['models']['local']['top1'])}, versus {pct(restore['models']['baseline']['top1'])}baseline.",'Ranked common-glyph suggestions under a verified one-slot assumption.'],
       ['Unknown gap length',f"Count accuracy {pct(gap['models']['local']['exact_count_accuracy'])}; one-sign control {pct(gap['models']['local']['constant_one_glyph_design_control_accuracy'])}.",'Context alone is unreliable for deciding how many signs were lost.'],
       ['Semantic identification','No secure sound/meaning bridge established.','Useful structural advance; no substantive semantic decipherment breakthrough.']], [120,172,208])
    p('Three parallel research agents handled corpus/provenance, primary literature/novelty, and independent statistical methods. Root integrated the work and produced separate archaeological-context, paired-surface, restoration, independent-annotator and digitization experiments. Model size or confidence was never treated as evidence of a decoded language.',True)

    page('1. Evidence, units and source identity')
    table([['Material','Scope','Status'],
       ['Lipi observational export','5,680 face records;4,695 object-family IDs. Clean RTL single-line subset2,930; main length>=3 subset2,107.','Derivative export associated with a disputed Sanskrit decipherment. Translations, Sanskrit, notes and text-derived class labels excluded.'],
       ['Mayig photo digitization','179 Mohenjo-daro seal faces;186 original lines;94 explicitly clear faces.86 clear single-line faces length>=3.','Independent Michael Carlson manual annotation of CISI photographs; MIT2024. P IDs are local class IDs.'],
       ['CISI1 scan','Government-hosted Joshi/Parpola1987.862PDF pages comprise two identical431-page copies.','Offset431 duplication verified for every page image. Count one book, not twice the artifacts.'],
       ['Finnish1979/1980/1982 editions','Institutional primary corpus, documentation and concordance acquired separately.','1979 and1982 explicitly CC BY4.0.1980 license not inferred from the other editions.'],
       ['Photographic audits','Initial25-object audit;13 selected fish/stroke cases; copper, duplicate, restoration and paired-face extensions.','Nonrandom audit samples. Compatibility counts are not population error rates.']], [125,185,190])
    p('Codes identify graphics. Wells002 denotes two SHORT bars,032 two TALL bars;700 a simple U,740 a handled-jar graphic. A visual count of two strokes does not establish the semantic numeral two. Mayig P IDs, Mahadevan numbers, Wells numbers and Finnish stable codes cannot be equated by their digits.')
    p('The observational code000 denotes an eroded/illegible unit; a Mayig P000 can denote a lost section of unknown extent.999 denotes a physical blank between signs. Neither is a word delimiter or proof of one missing glyph. Complete-observed flags describe a recorded inscription, not proof that every inscription on the physical object has been inventoried.')
    p('Encoded Lipi strings are visual left-to-right lists in a presentation arranged for reading from the right. We reverse within the retained normalized single line for computational reading. Dir is preserved as a catalogue field; primary conventions use impressions for seal texts, so it does not by itself describe every physical incision\'s direction. Mayig likewise records impression layouts. Multiline records require separate treatment. Source definitions and exclusions are preserved in data/normalized/.')
    p('Lipi has no explicit repository license in the pinned source. Its bulk extraction remains local research material; this report and code do not license redistribution of that corpus. Pinned commits: Lipi fc8813a52e183d19c441631dc26c33a4dccbea39; Mayig ad2f1e218a34b8c33c57de0d6cb8d99272765bbb.',True)

    page('2. How the structural test works')
    p('The main population has2,107 complete explicit-RTL, single-line records with at least three signs,1,596 distinct whole strings and1,526 transitive components. A component joins all records linked by physical artifact aliases or an identical whole string. No component crosses an outer validation fold. The largest contains36 records.')
    p('Five outer folds evaluate prediction. Three inner grouped folds select an independent baseline among global unigram, length/position and length/position/site/object-type distributions, and select smoothing for the dependent model. Selection uses training records only. Candidate smoothing values are5,20,100,500 and2,000. The observed selections are PM500 and PMB100 in all outer folds.')
    code('PMB(c | previous, length, slot, metadata)\n  proportional to PM(c | length, slot, metadata) * BG(c | previous) / U(c)\nNormalize across the TRAINING alphabet plus UNKNOWN.')
    p('The test measures a reduction in held-out noninitial cross-entropy, in bits per sign. Unknown test glyphs share one descriptive UNKNOWN bucket in the likelihood calculation. Exact restoration counts such fine-code predictions as failures. Cluster-bootstrap intervals condition on the fitted cross-validation models; they do not incorporate all transcription or model-selection uncertainty.')
    table([['Weighting/inventory','Predictive gain(bits/sign)','Conditional grouped95% interval'],
       ['All clean records',f"{nested['observed']['gain_bits_per_noninitial_sign']:.3f}",ci(nested['observed']['gain_95pct_group_bootstrap_ci'])],
       ['Unique whole strings, all physical aliases retained',f"{unique['observed']['gain_bits_per_noninitial_sign']:.3f}",ci(unique['observed']['gain_95pct_group_bootstrap_ci'])],
       ['Only861->817,405->390,706->705 merged',f"{collapsed['observed']['gain_bits_per_noninitial_sign']:.3f}",ci(collapsed['observed']['gain_95pct_group_bootstrap_ci'])]], [250,110,140])
    p('The three merges are compatibility sensitivities based on shared historical catalogue classes. They are not photographic proof of allography. Including length-two strings creates an804-record transitive component,27.4% of the2,930-record population; that broader design has substantially weaker effective independence.')
    if metadata_null:
        p(f"The stronger shuffled reference rebuilds grouping/folds, selects smoothing and fits models on each full shuffled corpus while preserving exact length/position/site/type marginals. It has{metadata_null['permutations']:,}completed metadata shuffles and a one-sided Monte Carlo reference p={metadata_null['p_one_sided']:.6f}. Its p-value is a comparison to that declared null, not a probability that the script is linguistic.")
    if unique_null and not unique_null.get('in_progress',True):
        p(f"The unique-string reference additionally rejects shuffles that create duplicate whole strings. It completes{unique_null['permutations']:,} accepted draws from{unique_null['attempts']:,} proposals, rebuilding grouping/folds, tuning and prediction. Observed gain0.848 bits/sign has zero exceedances, reference p={unique_null['p_one_sided']:.6f}; null mean0.007 bits. The accepted reference preserves the unique sampling rule and all physical aliases.",True)
    p('Earlier fixed-fold nulls and foldwise fixed-discovery tests remain archived and labelled as conditional diagnostics. Their apparent precision must not replace the full-procedure references. A loader defect that discarded physical aliases after uniqueness filtering was repaired before the headline unique-string and restoration results; unsafe outputs remain explicitly superseded.',True)

    page('3. Order is not a diagnosis of language')
    figure('structural_specificity','Both datasets are fit using the same normalized prediction protocol. Lower cross-entropy is better within a dataset; comparing absolute values between them does not classify language.')
    p(f"A finite mixture of independent-slot templates, allowing up to64 components selected on training data, improves the independent Indus baseline by{templates['contrasts']['TEMPLATE_minus_BASELINE']['gain_bits_per_noninitial_sign']:.3f}bits. Previous-sign information still improves that mixture by{templates['contrasts']['PMB_minus_TEMPLATE']['gain_bits_per_noninitial_sign']:.3f}bits, interval{ci(templates['contrasts']['PMB_minus_TEMPLATE']['95pct_group_bootstrap_ci'])}.")
    p(f"A constructive nonphonetic control contains3,000 office-routing records. Its symbols identify office entities and legal handoffs; they encode no speech. Under the same protocol its Markov model improves the selected template family by{office['contrasts']['PMB_minus_TEMPLATE']['gain_bits_per_noninitial_sign']:.3f}bits, interval{ci(office['contrasts']['PMB_minus_TEMPLATE']['95pct_group_bootstrap_ci'])}. Thus residual adjacency dependence is not specific to phonetic writing.")
    p('This control is a counterexample to a diagnostic inference, not a historical model of Indus administration. Published critiques already make the broader point. We also acquired author-preserved real nonlinguistic data: the totem encoding has43.7% held-out OOV tokens and very sparse observations, so its small gains are not a comparable threshold. The weather archive forms one station/text component under conservative alias closure; independent grouped cross-validation is infeasible.')
    p('Administrative templates and Sproat comparator data also appear in '+source('Nair2026, arXiv2604.17828v1','https://arxiv.org/abs/2604.17828v1')+'. This unreviewed prior limits any claim to have introduced such controls. Our contribution is the particular normalized predictive assay and artifact/text grouping protocol.',True)
    p('The label-symmetry demonstration renames every fine-code state and model parameter consistently. Likelihood differences remain below2e-15bits and restoration-mass differences below6e-18. Such an objective cannot choose among arbitrary unanchored sound/meaning labels. An independently fixed linguistic model, physical anchor or risky semantic prediction can break that symmetry; this does not make historical decipherment impossible.')

    page('4. A second manual transcription')
    figure('independent_annotator','Intervals condition on fitted models. Each event is a set of possible fine Wells codes; it does not identify a single token-level graphic variant.')
    p('This test uses all86 eligible Mayig clear single-line faces of length>=3, without selecting by agreement with Lipi. Five contain unmapped P classes; seven more have a slot with no training-supported fine candidate.74 faces are scored, with73 distinct P strings.20 scored faces include some unsupported alternative fine candidates; the fully supported54-face sensitivity is reported separately.')
    p('Training excludes every component touched by any CISI M1..M199 source family in the full observational register, including damaged/short/multiline records. It also excludes any complete fine-code string compatible at every position with an eligible Mayig candidate-set text. This removes170 of1,596 training strings, leaving1,426 strings in1,362 components.195 source objects are identified;155 occur in eligible training material.')
    p('The forward recursion sums over compatible fine-code paths and normalizes after each observed candidate event. It has been checked against exhaustive path enumeration and singleton Model.score. Unseen fine candidates are not credited through UNKNOWN. Candidate sets can overlap across P labels, so this is an event likelihood, not a normalized prediction distribution over Mayig labels.')
    p('The primary stratum assumes Mohenjo-daro/SEAL:S. Replacing its seal subtype with an unseen unspecified subtype gives a similar positive gain. The annotation and crosswalk are independently supplied by Michael Carlson, but the photographs and historical catalogues are shared. This is useful replication across annotation, not an independent archaeological corpus or a new sign inventory.')
    p(f"A post-photo-audit sensitivity excludes the three scored faces with independently flagged segmentation/height/decorated-variant discrepancies (M81,M140,M181; a fourth flag,M62, was not scored). The remaining71 faces give +{quality['all_remaining']['gain_bits_per_noninitial_candidate_event']:.3f} bits per event, conditional interval{ci(quality['all_remaining']['conditional_cluster_bootstrap_95_ci'])}. This check uses already observed outcomes and unchanged fitted models; it is exploratory source-quality sensitivity, not a new preregistered confirmation.")

    page('5. Restoration with a known one-sign slot')
    table([['Metric','Position/site/type baseline','Local context'],
       ['Exact top-one',pct(restore['models']['baseline']['top1']),pct(restore['models']['local']['top1'])],
       ['True code among top five',pct(restore['models']['baseline']['top5']),pct(restore['models']['local']['top5'])],
       ['True code among top ten',pct(restore['models']['baseline']['top10']),pct(restore['models']['local']['top10'])],
       ['Each whole text equally weighted',pct(restore['models']['baseline']['equal_text_weight']['top1']),pct(restore['models']['local']['equal_text_weight']['top1'])]], [240,130,130])
    p(f"The benchmark masks every glyph in1,596 unique texts, totaling8,009 slots, in1,526 artifact/text components. Exact gain is{restore['paired_gain']['gain_accuracy']*100:.2f}percentage points, conditional cluster interval{ci(restore['paired_gain']['cluster_bootstrap_95_ci'],100,2)}. All outer folds select alpha20 using grouped inner training accuracy. A separate reviewer checked a wider U/P/PM baseline family and still selected PM20.")
    p(f"The compatible-merge sensitivity yields{pct(rc['models']['local']['top1'])}exact local accuracy versus{pct(rc['models']['baseline']['top1'])}baseline on7,917 slots in1,575 unique texts. This is graphic prediction; no sound or meaning is assigned. Across all548 observed fine-code types, macro-average exact accuracy is only5.13%local versus0.63%baseline. The205 singleton types cannot be recovered when unseen in training.")
    table([['Entire held-out site','Unique test texts','Exact local gain(points)','Conditional95% interval'],
       *[[z['site'],z['test_texts'],f"{z['paired_gain']['gain_accuracy']*100:.2f}",ci(z['paired_gain']['cluster_bootstrap_95_ci'],100,2)] for z in site_restore['results']]], [140,95,120,145])
    p('Site exclusion is defined using every raw clean record at the held-out site, rather than only the retained unique representative. Entire touched training components are removed. Representative metadata may still discard copies at other sites, so this is a conservative transfer sensitivity, not proof of a universally accurate decoder.')
    p('The nonrandom photographic compatibility check holds out16 fine-coded derivative texts and every linked artifact/string. Local exact accuracy is33/79 slots, baseline15/79. Those cases were selected for source audit, and catalogue-family compatibility is weaker than fine-glyph identity;41.8%is not an independent population accuracy estimate.',True)

    page('6. Damage extent and calibrated uncertainty')
    figure('restoration_limits','Initial/internal/final position here means reading order. The artificial gap-count task has a different truth distribution from the single-slot graphic task.')
    p(f"The unknown-length gap experiment removes one internal span of1..3 signs from each held-out text, giving the predictor only survivors and site/type. Exact marginalization sums every hidden-code path. Local count accuracy is{pct(gap['models']['local']['exact_count_accuracy'])}, versus{pct(gap['models']['baseline']['exact_count_accuracy'])}factored baseline; paired gain{gap['paired_gain']['gain_accuracy']*100:.2f}points, interval{ci(gap['paired_gain']['cluster_bootstrap_95_ci'],100,2)}. Always guessing one sign scores{pct(gap['models']['local']['constant_one_glyph_design_control_accuracy'])}under this artificial erasure law.")
    p('The gap model is therefore unsuccessful as a dependable count estimator. Its strong-looking masses are especially misleading: the highest bin averages0.936model mass but49.4%exact correctness. The one-slot predictor is also overconfident. No model mass is presented as an archaeological confidence probability.')
    p('A reviewer identified a mismatch between the historical length prior and the artificial sampling law: the latter samples the erased count uniformly from 1 through min(3,L-2). A separate post-audit sensitivity reweights each saved count posterior by 1/min(3,L-2), leaving models, folds and survivors fixed. Independent accuracy becomes 45.61%, local accuracy 46.30%, and local gain 0.689 percentage points (conditional grouped interval -0.569 to 1.940). Local accuracy remains 4.762 points below the constant-one control (interval -7.775 to -1.726). This strengthens the negative conclusion and is not an archaeological gap prior.')
    p('A blind review of17 Mayig faces containing one P000 found no secure new single-sign restoration. M169 initially looked promising, but its interval is wider than neighbouring signs and contains separate remnants; the historical fine-code export contains two000units there. That catalogue count is not ground truth, but it corroborates rejection of the one-slot premise.')
    p('A second frame of seven Lipi internal-single000cases yielded five acquired primary plates. M61 has a bounded partial graphic already annotated uncertain W081 by Mayig, so suggesting it would be postdiction. M62 has a visible U-like graphic already annotated W700, and a tall/short coding disagreement. These are recoding/audit cases, not newly recovered historical text.')

    page('7. Model mass and actual correctness')
    figure('calibration','Each plotted point is a held-out bin mean; the diagonal is the calibration reference. These curves demonstrate empirical overconfidence in this corpus and benchmark design.')
    p('For a known one-sign slot, the0.4..0.6mass bin averages0.492model mass and0.384exact accuracy. The0.8..1.0bin averages0.896and0.838. A high rank is useful for narrowing alternatives, but it must be combined with surviving carving, correct sign height, orientation, line boundaries and independently assessed slot extent.')
    p('The predictor reports alternatives rather than modifying inscriptions. It rejects000and999as proof of an exact missing slot, accepts explicit artifact exclusions, and removes every connected training component touching those artifact IDs. Source cases with an unknown number of lost signs must not be passed to the one-slot interface.')
    code('python src/restoration.py predict --sequence "817,002,?,740"')
    p('The example is an exploratory graphic query. For a source case, provide --site, --type, --alpha 20 and --exclude-artifact with the actual observational object-family ID. All-local training can contain matching texts on different objects; the output explicitly warns that exploratory suggestions may overlap known material. Accepted epigraphic restoration remains a separate human/source judgment.')

    page('8. Archaeological context: what survives')
    p('Context prediction uses observation fields only. A principal inscription per physical object is selected deterministically by greatest retained length, then record ID. Models compare sign presence/boundaries/bigrams against a site-by-length baseline. All preprocessing is fit inside grouped training folds. Text-derived structural class labels and decipherer translations are excluded.')
    table([['Question','Robust result','Interpretation'],
       ['Seal versus tablet, one representative per whole text','1,679representatives; sign features improve log loss by0.0482nats/object;95%interval0.0271..0.0688;1,999site/length permutations p=.0005.','Some textual distribution tracks artifact function beyond these baseline covariates. It does not identify a commodity or title.'],
       ['Bull1 versus other field motifs','1,020representatives; gain -0.0568nats; interval -0.0792..-0.0346; p=.556.','This model fails to improve motif prediction. Absence of predictive gain is not proof of no semantic relation.'],
       ['Mohenjo-daro excavation blocks','Known-period subset316objects; block-similarity p=.056. Unique and compatible-merge sensitivities p=.0634.. .0864.','Weak/nonrobust local association. Blocks can be trenches/streets; they are not asserted households.']], [125,235,140])
    p('Repeated whole texts can have different archaeological labels. Rowwise label permutations on the original duplicate-weighted population are difficult to interpret because duplicated-text cohorts are not independently exchangeable. The headline context sensitivity retains a deterministic source-ID representative of each whole text, records disagreements and does not choose a majority label after observing outcomes.')
    p('Artifact-type site-transfer results are mixed and sometimes lose predictive performance. Thus the in-corpus context gain cannot be promoted into a universal artifact classifier. Missing excavation periods are excluded in the stronger microcontext sensitivity; a dash is not a known shared archaeological date.')

    page('9. Paired faces and stroke modules')
    p('The query distinguishes adjacent two/three/four TALL strokes plus simple U700, in either order, from short bars and handled jar740. It finds316 objects with a qualifying face and a complete other inscription:83two-stroke,123three-stroke and110four-stroke.371objects qualify overall;55lack a retained complete other face.')
    p('A tempting observation - no object has two unequal qualifying module counts - has almost no exposure to test that proposition.370objects have one qualifying face; only one has two, both three-stroke. The source H355 prism has distinct B/C faces; it is not two photographs of one face. The absence of unequal counts is therefore not strong semantic exclusion evidence.')
    table([['Other-face string','Objects','Opposite tall-stroke counts','Limit'],
       ['176,740,400','29','Two:2;three:18;four:9','A repeated label occurs opposite varying modules; the broader family relation is published prior.'],
       ['003,861','22','Three:1;four:21 in derivative codes','H2238 middle-face short bars are verified; its reverse tally is unresolved in the individual drawing.'],
       ['Within-label geometry','60objects in four site/type/text strata','Width coefficient p=.299; Holm-adjusted .598. Height p=.603.','Dimensions are not mass or contents. Sparse negative results cannot rule out numerical readings.']], [115,60,150,175])
    p('Primary HARP cohort photographs support a three-versus-four long-bar contrast between manufacture groups, but lack individual excavation IDs needed to assign the photographed representative to H2238. Cohort-level corroboration must not be converted into an individually verified exception. Mould/manufacture dependence remains incompletely documented.')
    p('The paired relation challenges a deterministic mapping from the other-face label to one stroke count. An unchanged name or category could accompany varying quantities. Ration, fee, offering, entitlement, quantity and nonnumeric categories remain alternatives. No referent has been selected.')

    page('10. Substitutions, graphic classes and priority')
    p('Many attractive pairs share a coarse external catalogue class:817/861,390/405 and705/706. These can reflect fine inventory splitting. The strongest raw pair mapped to disjoint Mayig P classes,817/820, shares eight exact whole frames; its opener environment is already published. Disjoint catalogue coding is not independent token-level photographic certification. We count distinct frames, discover on training frames, and validate in a wholly new held-out frame.')
    table([['Full-procedure transfer','Observed disjoint P-class pair-frames','Metadata-null mean','1,000-shuffle p'],
       ['All complete records','5','5.005','.541'],
       ['Unique strings, physical aliases preserved','3','.096','.001'],
       ['Three compatible-class merges','5','5.658','.639']], [205,110,95,90])
    p('A uniqueness-conditioned sensitivity rejects shuffled corpora that create duplicate whole strings: three transfers versus mean0.116, p=.003in1,000accepted draws from6,569attempts. This supports the unique-weighted aggregate constraint, while the primary and merged references remain unremarkable. It does not establish a new semantic substitution family.')
    p('The three unique disjoint P-class confirmations are176/904,220/231 and233/235, each in one new frame. An aggregate p-value is not an individual p-value. A post-pilot frequency-adjusted maximum test is globally positive, largely driven by known opener/fish correspondences;176/904 has primary familywise p=.130at10,000shuffles, and220/231 p=.863.')
    p('One exact176/904contrast, Ad3/H2139 in frame235,705,033,*,740, is already diagrammed in RMRL bulletin6(June2025), printedp17/PDF23Fig6. No earlier explicit statistical pair-class test was found in that passage, but the juxtaposed examples are prior. Fine photographic verification of all six distinct strings remains incomplete.')
    p('The initial25-object photographic audit found catalogue compatibility in17of24eligible complete single-line comparisons. Seven differences include compound-versus-two-grid segmentation, height-category disagreement and decorated variants. These observations prevent treating a broad crosswalk as fine-glyph ground truth. The sample is not a random error audit.',True)

    page('11. Semantic and external-anchor audits')
    sub('Fish, strokes and copper devices')
    p('Short versus tall bars are visibly distinct in the13selected source cases. Source checks identify opposite coding errors: Mayig assigns tall bars in M140 where the photo supports short ones; Lipi assigns tall bars in M62 where the photo supports short ones. Their glyph-height classes must be retained before testing any numerical or rebus proposal.')
    p('Published fish/star interpretations concern six/seven short-bar configurations and specific modified-fish constructions. A two-long-bar+fish Venus proposal uses a space/white rebus rather than cardinal two. A test that pools all bars as numerals would attack a different hypothesis.')
    p('Copper reverse-device families are already described in Parpola2005/2008. Literal animal-name readings depend on fine ligature identity and on the device/label referent relation. Broad P124 merges include disputed outer leaf/person and inner feet distinctions; partial/corroded source photographs do not securely resolve C5/C6fine identity. The observed relation does not uniquely select animal names, deities, institutions, clans or offices.')
    sub('The familiar Gulf objects do not supply aligned readings')
    p('Shu-ilishu names a Meluhhan interpreter in cuneiform and depicts a scene, but the inspected object supplies no Indus sign sequence to align with that name. Gadd no1(BM120573/U7683) has bison imagery and cuneiform alone. No6is a different cylinder; a later source appears to cite it in place of no1. Gulf-style or pseudo-Indus signs without a paired known text do not establish phonetic values.')
    p('The inspected references therefore provide historical contact and language-context evidence, but no secure sign-to-sound bridge. This audit does not claim that every unexamined collection lacks an anchor, nor that a bilingual is logically required for every possible decipherment. New claims need inventory numbers, accessible originals and an explicit alignment.')
    page('12. Numerical scale and independent tests')
    p('Fuls2020 derives a proposed4.04 L unit from Wells\'s40.4 L per-long-stroke estimate by assuming one long stroke equals ten. V=40.4*n and V=4.04*(10*n) are identical predictions for every long-stroke vessel. Those capacities alone cannot select the value ten, a decimal base or a spoken numeral. The value ten requires independently grounded mixed-sign/count evidence.')
    p('The primary original three pots are fitting cases, not external validation. H370shows seven long bars without U; H371six plus U; H372three plus U. Published volume estimates depend on geometric reconstruction and direct dimensions rather than measured ancient contents. Funerary or secondary use does not establish what the earlier marks quantified. Later pots differ in marking inventory, units and reconstruction uncertainty; none is silently forced into the same frozen unit model.')
    table([['Source fit case','Long strokes','Indexed profile volume','Eligibility limit'],
       ['H372','3','About121 litres','Profile-to-object table alignment remains provisional.'],
       ['H371','6','About241 litres','Part of original scale fitting.'],
       ['H370','7','About284 litres','No U; not an unqualified test of a U-conditioned proposal.']], [80,75,110,235])
    p('The indexed estimates closely reproduce40.4 litres per long stroke, but original Table1 PDF layout was inaccessible and excavation-number links disagree: CISI assigns12908 to H370, whereas the indexed Fuls table associates it with H372. H95-2661 has four rim strokes in the inspected cluster, yet its excavation report describes four inscriptions and later reuse as a sump. K90 has uncertain profile units. No independently eligible held-out vessel test was established. Complete source fields, geometric alternatives and unresolved mappings are retained in research/literature/metrology/.')

    page('13. Numerical constraints: exact conditional result')
    p('A proposed reading is stronger when its assumptions imply a finite set of checkable values. We independently solved the two equalities used in Fuls\'s numerical argument, without a bounded search or an assumed decimal base. Let L and S be the multipliers assigned to selected long/short stroke positions and v the proposed crescent value. These are hypothetical quantities, not unconditional decoded values for every stroke.')
    code('v = 2*S - L\nv*L + 1 = 7*S + 5\nEliminate v: (2*L - 7)*S = L*L + 4\nLet d = 2*L - 7: d must divide 65.')
    table([['All positive integer solutions','L','S','v'],
       ['Solution1','4','20','36'],['Solution2','6','8','10'],
       ['Solution3','10','8','6'],['Solution4','36','20','4']], [260,80,80,80])
    p('Conditional on either cited range8<=L<=13 or the broader8<=L<=18, only(L,S,v)=(10,8,6) survives. The range and equalities carry the identifying information. Excluding primes or assuming S even is unnecessary; the first equality by itself only constrains the parity of v+L. Without the upper bound, L>=10 still permits(36,20,4). The exact proof is executable in src/methods/audit_numerical_equalities.py; hypothetical two/three/four-stroke inputs are compared separately in numerical_count_delta.py.')
    p('The bangle range is not independently authenticated for the object captioned M-1383 in the author\'s Fig15. The original Vidale1987 chapter (printed105-111/PDF108-114) describes a fused DK-B,C block whose identity with that object has not been established. Its ten-bangle reconstruction is conjectural and supplies no82-fragment/15-20 total here. The current M-1383 export has clay-tag metadata but compatible seven-short/one-long signs; the author figure/catalogue must resolve this context conflict. The range is unverified, rather than disproved.',True)
    sub('An original object check, with the identifier gap preserved')
    p('The author\'s historical ICIT3786 number points to a different object in the pinned current export. Searching complete opposing sign patterns instead identifies a unique candidate, current family1786/CISI H904. Vats1940 Plate XCVI no477 (PDF 200 of the plates scan) shows three long strokes between U and crescent on one face, and two long strokes between jar and overlapping circles on the other. The original table, printed page349/PDF 378 of the text scan, gives find J213, mound D, and0.65 by0.28 inches, matching H904\'s J213(D)477 and16.5 by7.1mm.')
    p('This establishes the H904-to-Vats object join and supports the candidate\'s coarse three/two stroke counts. The historical3786-to-H904 join remains provisional because the author\'s Figure16 image was not independently retrieved. The prose\'s W032/three-stroke discrepancy may be a code typo, rather than evidence for changing the coefficient to two. Extra signs and equality/addition/unit assumptions remain unresolved; source-count agreement alone does not validate the numerical semantics.',True)
    p('Source pagination: the2020 proceedings chapter is pp57-90; the inspected2023 author reprint is pp15-48. The first equality is on reprintp30/PDF16, and the M331 equality on reprintp32/PDF18. The M331 photograph supports coarse stroke configurations, but positional multiplication and equal total quantity across faces are interpretive premises.',True)

    page('14. A primary chart and its transcription limits')
    p(f"A local searchable atlas now provides all687 chart cells from the independently acquired1979 corpus, with original context crops, ranks, stable Finnish numeric codes and explicit alternatives. {chart['numeric_ambiguous_cells']} cells retain ambiguous numeric readings. Source underlines and damage markers are modern editorial conventions. AI visual inspection is not expert certification, and no chart-derived inscription was added to the analytical corpus.")
    p('The initial blind numeric audit found only14/28 clear labels correct by OCR and15/28 by a source-font recognizer. Manual reinspection subsequently corrected digit readings; those later corrections do not revise the earlier score. Duplicate-code alerts were used to find source crops, never to force uniqueness. Historical inputs and candidate unions remain archived.')
    p('A ten-row image development pilot tested four predeclared segmentation penalties. A source-observed crop defect included neighbouring number ink and was repaired; one row was partially disclosed during that repair. At penalties0.5 and1, all ten drawn-unit counts matched, but first-choice candidates matched only two whole rows. This was development evidence, with the partial disclosure recorded.')
    sub('Fresh twenty-row validation: reference withheld until freeze')
    ff=font_fresh['summary']['all20_prespecified']
    table([['Frozen endpoint','Result','Meaning'],
       ['Modern source drawn units',f"{ff['true_drawn_units']} total: {ff['charted_glyph_drawn_units']} charted, {ff['editorial_auxiliary_drawn_units']} editorial",'No inference of ancient text length.'],
       ['Predicted units / matching counts',f"{ff['predicted_units']} / {ff['correct_drawn_unit_count_rows']} of20 rows",'Counts do not certify boundaries.'],
       ['First image-template candidate',f"{ff['strict_top1']['summed_edit_distance']} summed edits; {ff['strict_top1']['candidate_compatible_whole_rows']} whole rows compatible",'Numeric alternatives can widen one candidate.'],
       ['First five image templates',f"{ff['strict_top5']['summed_edit_distance']} summed edits; {ff['strict_top5']['candidate_compatible_whole_rows']} whole rows compatible",'Mean candidate-code set width5.04, maximum8.']], [180,170,150])
    p('Twenty randomly selected printed rows used the fixed penalty1 chosen from development. All selected rows were retained, including two auxiliary-only rectangles and four rows with loss or inaccessibility marks. The manual reference was withheld until a complete prediction file existed. These scores use the chart snapshot frozen at prediction time, with14 numeric ambiguities; the later16-ambiguity atlas is not retroactive validation. Strict scores use set intersection in Levenshtein alignment; zero edits mean candidate compatibility, not a uniquely certified fine-code transcription.')
    p('A subsequent source-only crop audit found18 of20 crops entered the target row\'s upper ink, and14 included following-row ink. The scores therefore assess the failed frozen acquisition pipeline, rather than uncontaminated shape recognition alone. The deliverable is a verifiable chart reference and documented acquisition limits, not a completed independent sign corpus. Original physical side/line boundaries remain unknown.',True)
    p('A separate post-reference geometry diagnostic retains the identical frozen chart, matcher, penalty1 and horizontal bounds. Clean source-only vertical crops yield96 predicted units and18/20 matching row counts. Strict first-template candidates give24 summed edits and6 compatible whole rows; five templates give6 edits and16 rows (maximum9 code candidates per slot). This isolates a substantial geometry defect, but is development after reference release and needs fresh validation.',True)

    page('15. What advances and what does not')
    table([['Contribution','Status'],
       ['Artifact/text alias preservation, stronger full-procedure nulls, second-annotator event replication','A reproducible methodological robustness contribution. Not first discovery of Indus order.'],
       ['Known-slot restoration with train-only tuning, site exclusion, rarity and calibration audits','A useful benchmark/tool. Markov restoration itself is published prior(Rao2009).'],
       ['Unknown gap-length estimator','Failed exploratory extension. It must not be promoted to accepted restoration.'],
       ['Photographic coding/extent discrepancies, scan duplication and corrigenda','Concrete source corrections/flags; sampled scope is explicit.'],
       ['Opening/terminal/fish substitution categories and paired count modules','Largely replicate published findings; no priority claim.'],
       ['Language identification, phonetic assignments, lexical meanings or authenticated translation','Not achieved. No substantive semantic decipherment breakthrough is claimed.'],
       ['Conditional numerical proof and original H904/Vats source join','All integer solutions derived; key stroke counts corroborated. Semantics and historical index join remain conditional.'],
       ['Independent1979digitized sign corpus','Not completed. Manual chart delivered; frozen acquisition failed. Geometry repair improves development scores and needs fresh validation.']], [285,215])
    p('Shared-context and substitution discovery itself is established prior, including Khanna and Merriam2025. The contribution here is the specific alias-preserving evaluation, held-out annotation test, stronger null protocol and source-level failure accounting. No published proposed functional or semantic reading is adopted merely because it uses similar statistical methods.')
    p('The project preserves unsuccessful tests and superseded defects rather than combining their best numbers. The evidentiary hierarchy is physical carving/source identity, observational transcription, tested distributional constraint, then a separately falsifiable semantic or phonetic hypothesis. Passing the first three stages does not automatically pass the fourth.')
    sub('What would make the next claim substantive')
    p('A decoder should commit in advance to exact graphic values, segmentation and an external referent/phonological model, then predict an independently acquired inscription or archaeological measurement that competing readings cannot match by freely changing units or dictionaries. Full artifact/mould aliases and every inscription on a multi-marked object must be inventoried before scoring. A new reading should also explain its failed cases.')

    page('16. Reproduce and inspect')
    p('The workspace contains original acquisitions/provenance, normalized observational files, preregistrations, exploratory plans, code, held-out audits, machine-readable result JSON and agent reviews. No cloud publication or external message was sent. Bulk derivative data remain local.')
    table([['Purpose','Entry point'],
       ['Integrity checks','python src/verify_root.py<br/>python src/methods/verify_methods.py'],
       ['Known-slot benchmark','python src/restoration.py benchmark'],
       ['Site-held-out restoration','python src/restoration.py crosssite --out results/restoration_crosssite'],
       ['Independent manual annotation','python src/independent_annotator.py'],
       ['Unknown-length negative benchmark','python src/gap_restoration.py benchmark'],
       ['Unanchored label symmetry','python src/identifiability_demo.py'],
       ['Frozen image-test evaluation','python src/evaluate_font_fresh20.py'],
       ['Conditional numerical constraints','python src/methods/audit_numerical_equalities.py'],
       ['Scientific figures / report','python src/research_figures.py<br/>python src/research_report.py --final'],
       ['Long structural/null procedures','research/methods/REPRODUCING.md; source seeds, hashes and completion states in RESULT_INDEX.json.']], [180,320])
    p('Commands run from the workspace root. Python numerical, statistical, image, PDF and plotting dependencies are recorded in the final environment manifest. Some long null procedures take around an hour on this host; exact runtime is saved, and resumed seeds are preserved. The final flag refuses to generate a final edition before four elapsed hours or before the stronger1,000metadata reference is complete.')
    p('Important review files: research/methods/FINDINGS.md; root_restoration_audit.json; independent_annotator_audit.json; research/literature/evidence_and_novelty_matrix.md; external_phonetic_anchor_audit.md; restoration_review.md; research/corpus/primary/1979_extraction_assessment.md; plate_audit/restoration_slots/; and the final output/evidence_manifest.json.',True)
    p('The expanded literature matrix records exact source locations, retrieval failures,2026 preprint status and corrected source identities. Speculative projects are novelty comparators, not accepted decipherments. Acquiring a source does not endorse its reading.',True)

    page('Selected primary references')
    refs=[
      ('Koskenniemi & Parpola1979, Corpus of texts in the Indus script','https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/','Stable-code/rank, uncertainty and printing conventions. Official CC BY4.0entry; later documentation revisions audited separately.'),
      ('Joshi & Parpola1987, CISI1','https://ignca.gov.in/Asi_data/76884.pdf','Primary photographs; duplicate scan and corrigenda audit. Printed page numbers differ from PDFindices.'),
      ('Rao et al.2009, A Markov model of the Indus script','https://doi.org/10.1073/pnas.0906237106','Prior sequence prediction and damaged-text restoration. Present results add scope-specific robustness safeguards.'),
      ('Sproat2010, Last Words','https://aclanthology.org/J10-3012/','Critique of structural evidence as a linguistic diagnostic. Corrected source identity; J10-4009was unrelated.'),
      ('Yadav2013, Sensitivity of Indus Script to Site and Type of Object','https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf','Paired labels/modules and archaeological context.'),
      ('Yadav2019, statistical/structural overview','https://insa.nic.in/writereaddata/UpLoadedFiles/IJHS/Vol54_2_2019__Art01.pdf','p127Table1quantifies prior opening pairs.'),
      ('Mahadevan1982, Terminal ideograms','https://rmrl.in/en/dl/research-papers/mahadevan/ebook?id=Terminal+ideograms+in+the+Indus+script_1982a','pp313-314published terminal correspondence; proposed meanings remain hypotheses.'),
      ('Mahadevan1986, Towards a grammar of the Indus texts','https://rmrl.in/en/dl/research-papers/mahadevan/ebook?id=Towards+a+grammar+of+the+Indus+texts_1986b','Short markers, modified fish and grammatical proposals.'),
      ('Parpola2005, Study of the Indus script','https://www.harappa.com/sites/default/files/pdf/indusscript%282%29.pdf','pp55-59fine copper-related ligature variants.'),
      ('Parpola2008, Copper tablets from Mohenjo-daro','https://tuhat.helsinki.fi/ws/portalfiles/portal/127257447/Parpola_A_2008._Copper_tablets_from_Mohenjo_daro._ECL_During_Caspers_Vol.pdf','Device/label group relations; fine photographic limits remain.'),
      ('Wells2008, Airavati contribution','http://www.varalaaru.com/airavati/airavati_final_high.pdf','pp285-286published U/stroke group and mould-duplication cautions.'),
      ('RMRL bulletin6, June2025','https://rmrl-site-files.s3.us-east-1.amazonaws.com/PDFFIles/bulletin/bulletin-No-6-June-2025.pdf','p17Fig6already juxtaposes Ad3/H2139candidate frame; commodity interpretation not adopted.'),
      ('Gadd1932, Seals of Ancient Indian style found at Ur','https://ignca.gov.in/Asi_data/33779.pdf','Primary Gulf objects and cuneiform-only/Indus-object distinctions.'),
      ('Possehl2006, Shu-ilishu\'s cylinder seal','https://www.harappa.com/sites/default/files/201402/Shu-ilishus-Cylinder-Seal.pdf','Named interpreter; no aligned Indus written sequence on inspected object.'),
      ('Fuls2020 chapter,2023 author reprint, Structural Analysis of Numerical Indus Inscriptions','https://www.researchgate.net/publication/373522958_Ancient_Writing_and_Modern_Technologies_-_Structural_Analysis_of_Numerical_Indus_Inscriptions','Inspected author posting pagination15-48;2020 proceedings chapter57-90. Numerical semantics remain assumptions.'),
      ('Vats1940, Excavations at Harappa, plates','https://ignca.gov.in/Asi_data/9842.pdf','PlateXCVI no477: original H904 candidate. Text table and dimensions independently joined; government catalogue title roles were checked against the scans.'),
      ('Vidale, More Evidence on a Protohistoric Ceramic Puzzle, InterimReportsVol2','https://ignca.gov.in/Asi_data/77275.pdf','Original pp105-111: conjectural saggar arrangement for a fused block, not an independent M1383 total.'),
      ('Khanna & Merriam2025, A Computational Analysis of the Indus Script: Identifying Sign Functions in Logo-Syllabic Writing Systems','https://www.ijcaonline.org/archives/volume187/number64/khanna-2025-ijca-926075.pdf','Prior shared-context and substitution clustering. Proposed meanings are not accepted anchors.'),
      ('Fuls2012, Volumenmaße von Tongefäßen der Induskultur','https://www.academia.edu/8808307/VOLUMENMA%C3%9FE_VON_TONGEF%C3%84%C3%9FEN_DER_INDUSKULTUR','Author-posted indexed text locates measurements and modelling. Original PDFlayout unavailable; table alignment flagged provisional.'),
      ('Mayig observational source, pinned2024annotation','https://github.com/mayig/indus-valley-script-corpus/tree/ad2f1e218a34b8c33c57de0d6cb8d99272765bbb','Independent manual photo annotation; local P code/schema conventions, MIT.'),
      ('Lipi observational export, pinned revision','https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39','Only observational fields used. Disputed translations excluded; bulk license absent.')]
    for title,url,note in refs:p(source(title,url)+'<br/>'+html.escape(note),True)

    out=ROOT/'output/pdf';out.mkdir(parents=True,exist_ok=True)
    target=out/'indus_script_research_report.pdf'
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Report',8);canvas.setFillColor(INK)
        canvas.drawString(48,26,'Indus script research | Graphic constraints, no phonetic reading')
        canvas.drawRightString(564,26,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(target),pagesize=(612,792),leftMargin=50,rightMargin=50,topMargin=44,bottomMargin=43,
        title='Indus script: structural constraints and limits of decipherment',author='Codex research investigation')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (ROOT/'output/report_build.json').write_text(json.dumps({'path':str(target.relative_to(ROOT)),
       'edition':'final' if final else 'draft','generated_utc':generated.isoformat(),'research_started_utc':START.isoformat(),
       'elapsed_hours':elapsed/3600,'stronger_metadata_null_permutations':metadata_null.get('permutations') if metadata_null else None,
       'unique_conditioned_metadata_null_permutations':unique_null.get('permutations') if unique_null else None},indent=2),encoding='utf-8')
    print(str(target))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');args=ap.parse_args();build(args.final)
