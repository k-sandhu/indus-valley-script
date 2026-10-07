"""Write review-2/row-checks.csv and review-2/caption-check.csv.

The results and notes are typed from the reviewer's reading of each cited passage.
The script joins them to the package's own row metadata and prints the tallies; it
does not recompute any judgement. Read-only on the package.
"""
import collections
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent

S, P = 'supported', 'partly supported'

CHECKS = {
 'F01': (S, 'Captions 30:08-30:30: earlier efforts were by single scholars; he proposes team work across kinds of expertise. The window matches the package window within 5 s.'),
 'F02': (S, 'Captions 24:36-25:12: regional corpora not yet attempted but feasible; so far one undifferentiated corpus. An explicit suggestion; the coordinator note only describes it.'),
 'F03': (P, 'Core request at 29:00-29:15: look further at how sign inventories vary with site size, in the context of use. The assemblage-size control is the coordinator rarefaction gloss, and sign 740 at 10% (29:20-29:50) is a finding. The limitation field credits sample-size questions to the talk; the captions have none.'),
 'F04': (P, 'Captions 51:00-52:50 describe non-canonical sequences outside the valley and two readings of two frequent signs, introduced as an interesting closing point. No request to study them; the imperative is the package wording.'),
 'F05': (S, 'p. viii: next research should define regional differences in how texts are structured.'),
 'F06': (S, 'p. viii: the development of the script cannot be understood without chronological control (a precondition). The comparison entry cites Wells himself at the same pages.'),
 'F07': (S, 'p. ix: progress depends on international, interdisciplinary cooperation.'),
 'F08': (S, 'p. x: linguists should use the Chapter 3 structural detail to identify or exclude candidate languages.'),
 'F09': (S, 'p. 45: the aim of the author own database is worldwide access and updates after new publications. An author plan worded as advice.'),
 'F10': (S, 'p. 45: inscribed artefacts served varied purposes and should not be pooled as one set. The locator names a paragraph that does not exist; the sentence ends the paragraph beginning A special issue.'),
 'F11': (S, 'p. 223: producer marks and user marks on pottery need to be separated in future work.'),
 'F12': (S, 'p. 230: urges wider excavation of Early Harappan sites to enlarge the sample of early writing.'),
 'F13': (S, 'p. 230: asks for finer recording and counting of marks made before and after firing, on pottery and other objects, by region. The row narrows this to pottery marks.'),
 'F14': (S, 'p. 231: progress needs continued collaboration and data published in accessible form.'),
 'F15': (S, 'Scan p. 21, read as an image: earlier-excavated seals and inscribed objects should be re-examined and sorted chronologically.'),
 'F16': (S, 'p. 13690: names a fuller analysis using all known texts and new sign lists as a future objective.'),
 'F17': (S, 'p. 13690: a site-by-site analysis could show regional differences in sign order; a possibility. The Yadav 2013 comparison involves a coauthor of this paper.'),
 'F18': (S, 'p. 13690: names grammar inference by statistical and machine-learning methods as the future challenge.'),
 'F19': (S, 'p. 98: concludes that interpretive models must treat site and object type as sources of variation.'),
 'F20': (S, 'p. 98: says a detailed study of stylistic variants by object type and site would help; modal wording, then a call for site- and type-sensitive analysis.'),
 'F21': (S, 'Section 8, reader p. 6: the authors state a goal of determining the language from text segments. A goal rather than advice; the limitation field holds a maintenance note about the first pass.'),
 'F22': (S, 'p. 127: iconic meaning has to be settled before rebus readings are considered. A premise argued in a rebuttal of Farmer, Sproat and Witzel; restated faithfully.'),
 'F23': (S, 'p. 37 n. 23: future Indus work depends on rare-symbol studies, which bear on how the system worked and was controlled. The Parpola (pp. 113-115) and Vidale (conclusion) comparison entries also match.'),
 'F24': (P, 'p. 43 n. 28: the Near Eastern second-hand seal problem has to be weighed before drawing conclusions about links between symbols on Indus seals and their users. The row says Near Eastern seal symbols.'),
 'F25': (S, 'p. 44: the authors expect sign-frequency changes in nonlinguistic systems to track historical developments and say such studies are starting. Their own programme under their nonlinguistic thesis, as the row states.'),
 'F26': (S, 'p. 46: names the role of the symbols in cultural cohesion and its decline as a main future challenge.'),
 'F27': (S, 'p. 592: sets the evidence standard for a classifier: it must separate a large set of known linguistic and nonlinguistic systems with high accuracy. A condition rather than advice; restated faithfully.'),
 'F28': (S, 'p. 593: suggests that general journals add computational linguists as reviewers.'),
 'F29': (S, 'p. 86: future work should widen the taxonomy and corpora of nonlinguistic systems.'),
 'F30': (S, 'pp. 85-86: future work may find features independent of text length; grammar induction is called one avenue. Hedged.'),
 'F31': (S, 'p. 803: the stated goal is better statistical tests, used as a set within an inductive framework.'),
 'F32': (S, 'Appendix proposal 1, p. 363: a small committee of experts to settle the sign inventory and variants.'),
 'F33': (S, 'Appendix proposal 2, p. 363: a shared font, rules for adding signs and a central archive.'),
 'F34': (S, 'Appendix proposal 3, p. 363: coordinated student theses on palaeography, made from the objects themselves.'),
 'F35': (S, 'Appendix proposal 4, pp. 363-364: study variation by material, function and location, keep pre- and post-firing pottery apart and examine objects directly.'),
 'F36': (S, 'p. 2: the semantic scope of inscriptions should be narrowed before values are inferred for single signs.'),
 'F37': (S, 'p. 29: leaves to future studies whether stamped pointed-base goblets were standardized administrative vessels.'),
 'F38': (S, 'p. 525: the economic functions ascribed to text components need further analysis and archaeological evidence.'),
 'F39': (S, 'Printed p. 186 n. 11: Wengrow branding assumptions need more testing and a stronger theoretical frame before use here.'),
 'F40': (S, 'p. 371: calls for detailed studies of particular material classes, architecture included. The Wells and Yadav comparison entries concern texts and site and type, a looser match.'),
 'F41': (S, 'Accepted manuscript lines 656-658: sees much to learn about how settlers lived from local subsistence, geomorphology and hydrology. The locator is the accepted manuscript, not the published pages.'),
 'F42': (S, 'Accepted manuscript lines 675-678: suggests further models of mobility and of sedentary and pastoral relations in Cholistan. Theme is coded computational method though the models describe behaviour.'),
 'F43': (S, 'pp. 500-501: Law plans wider steatite sampling in the northwest frontier region and Jammu. The author own plan.'),
 'F44': (S, 'p. 503: studying the northern borderlands needs new data from question-led excavation or re-excavation, naming Ropar, Manda, Musa Khel and Hisham Dheri.'),
 'F45': (S, 'p. 503: Law plan for a long-term sourcing program with scholars in India, Pakistan and elsewhere. An own plan, worded in the row as an instruction.'),
 'F46': (S, 'Biography page: Miller personally aims to use technological data to find possible bureaucracies or record-keeping centres. A project aim on an undated page; the limitation field holds a maintenance note about the first pass.'),
 'F47': (S, 'Slides 35 and 47: sign modifications and animal motifs have to be understood in context. The Wells and Yadav comparison entries are a loose match.'),
 'F48': (S, 'Slide 43: composite signs and add-on elements need to be isolated and studied.'),
 'F49': (S, 'Principle 1 of three on a Penn page describing a 1996 book; read live, identical to the proxy text. An undated description without page numbers.'),
 'F50': (S, 'Principle 2 on the same page: many small-scale studies of the script.'),
 'F51': (S, 'Principle 3 on the same page: test decipherment claims through independent lines of inference.'),
 'F52': (S, 'p. 8: wants more material evidence, documentation of graffiti-marked potsherds, and further exploration, excavation and analysis.'),
 'F53': (P, 'Rao is quoted that the number system might be partly reconstructed; the method with tally marks and weight ratios is the reporter hedged gloss. A prediction recast as an instruction.'),
 'F54': (S, 'Rao hopes future excavations yield longer texts or texts beside a known language.'),
 'F55': (P, 'Interview: relays a colleague remark that specialist studies of plant and animal remains have become repetitive and says archaeology should take it seriously. About excavation sampling, remote from the script.'),
 'F56': (S, 'p. 50: seal chronology has to be considered in discussing the script.'),
 'F57': (S, 'p. 182: further research is warranted on other possible inequalities (age, gender, material variety, urban infrastructure).'),
 'F58': (S, 'p. 183: proposes asking whether the Indus had more heterarchical corporate groups than early societies with exclusionary elites, and why.'),
 'F59': (S, 'p. 184: suggests exploring specialization and egalitarian growth; attachments among corporate groups are called an important future topic.'),
}

CAPTIONS = [
 ('F01', '30:05-30:25', '30:08-30:30', 'Earlier attempts were efforts of single scholars; a team effort with different expertise is proposed.', 'supported'),
 ('F02', '24:45-25:40', '24:36-25:12', 'Regional corpora not yet attempted but feasible, giving statistics a sounder footing; so far the corpus has been treated as one block with no chronological or geographical split.', 'supported'),
 ('F03', '28:45-30:40', '28:40-30:10', 'Inventory by site size (over 500, 100-200, 20-50 signs) could be investigated further in the context of use at 29:00-29:15; sign 740 at 10% of occurrences, top three 20%, top six 30%, top twenty half at 29:20-29:50, reported as a finding; much work could be done on the system at 30:00.', 'partly supported'),
 ('F04', '51:00-53:00', '51:00-52:50', 'Inscriptions outside the valley were analysed from Parpola in the 1980s and found to convey non-canonical sequences; one example seal; frequent man and twins signs read by some as patronymics and by others as another language. No request to study.', 'partly supported'),
 ('P03', '41:30-43:30', '41:10-43:50', 'Unbalanced oligopoly defined; unicorn, and the Indus bison outside the valley, as the majority component; same iconographies at the same frequencies for almost a millennium; seals compared with corporate ID badges and guild symbols.', 'matches position'),
 ('P04', '16:20-17:05, 48:25, 53:05', '53:25-53:45 only', 'Probably rejected any influence from other scripts and did not need other uses of writing such as longer texts or narratives. The other cited windows were not re-read.', 'matches position at 53:25-53:45'),
 ('P05', '17:05-24:00, 53:05', '53:00-53:20 only', 'Script called an original invention rooted around the turn from the fourth to the third millennium (the caption wording is garbled). The 17:05-24:00 window was not re-read.', 'matches position at 53:00-53:20'),
]


def main():
    rows = json.loads((PACKAGE / 'recommendations.json').read_text(encoding='utf-8'))
    sources = {s['id']: s for s in json.loads((PACKAGE / 'sources.json').read_text(encoding='utf-8'))}
    sample = set(json.loads((HERE / 'sample.json').read_text(encoding='utf-8'))['sample_sorted'])
    assert [r['id'] for r in rows] == sorted(CHECKS), 'every package row needs exactly one check'
    out = []
    for r in rows:
        i = r['id']
        group = ('random sample' if i in sample else 'lecture' if i in ('F01', 'F02', 'F03', 'F04')
                 else 'Frenez 2018 footnote' if i == 'F39' else 'other row, one-pass reading')
        if i in ('F01', 'F02', 'F03', 'F04'):
            route = 'English auto-captions read in browser pane, 7 Oct 2026; coordinator note'
        elif i in ('F49', 'F50', 'F51'):
            route = 'live page read in browser pane; package proxy text'
        else:
            route = sources[r['source_id']]['witness_path']
        result, note = CHECKS[i]
        out.append(dict(id=i, researcher=r['researcher'], source_id=r['source_id'], package_locator=r['source_locator'],
                        group=group, result=result, route=route, note=note))
    with open(HERE / 'row-checks.csv', 'w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(out)
    with open(HERE / 'caption-check.csv', 'w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['item', 'package_window', 'caption_window_read', 'caption_content_paraphrase', 'result'])
        writer.writerows(CAPTIONS)
    tally = collections.Counter(o['result'] for o in out)
    by_group = collections.Counter((o['group'], o['result']) for o in out)
    print(dict(tally))
    for key, count in sorted(by_group.items()):
        print(key, count)


if __name__ == '__main__':
    main()
