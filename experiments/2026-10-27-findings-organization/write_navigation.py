"""Write the findings guide and the permitted model appendix from card sources."""
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import kb

SUMMARIES = {
1: "Knowing the previous sign improves prediction by 0.848 bits per noninitial sign across 1,596 distinct texts.",
2: "Two-sign context ranks the hidden sign first in 37.27% of 8,009 artificial gaps, against 34.59% for one-sign context.",
3: "Probability loss worsens from 5.1194 to 5.2472 bits per hidden sign when the restoration model uses two signs of context.",
4: "All five validation folds choose the one-sign model when smoothing is selected by probability loss, retaining 34.5861% top-one accuracy.",
5: "The lost-sign count estimator scores 46.30%, below 51.07% for always guessing one.",
6: "Fuls's assumed numeral equations have four positive integer solutions; restricting the long-stroke multiplier to 8–13 leaves (10, 8, 6).",
7: "Of 493 checked CISI 1 identifiers, 166 have no corpus match, including 75 in pottery and graffiti sections.",
8: "At least 68 of 114 inspected museum records join corpus objects, with 46 unresolved in that census.",
9: "The census site list covers 5,652 of 5,680 corpus faces and reduces 123 entries to 115 site or provenance labels.",
10: "Base-shape families improve held-out prediction by 0.0219 bits per sign beyond the ungrouped model, exceeding random groupings (p = 0.005).",
11: "Two graphic-family codings of 577 sign codes agree at adjusted Rand indices 0.884 unweighted and 0.975 weighted by occurrences.",
12: "Grouping signs by their added marks performs no better than random groups of the same sizes (p = 0.11).",
13: "For 267 held-out signs whose code is absent from training, base families reduce loss from 14.60 to 14.19 bits per sign.",
14: "Bas-relief tablet texts predict image class in 24.8% of cases, against 21.5% for the majority guess.",
15: "Incised tablet texts predict image class in 57.4% of cases, against 48.1% for the majority guess.",
16: "Copper-tablet texts predict image class in 19.2% of cases, below the majority guess's 26.9%.",
17: "Copper-tablet sign groups occur with matching seal animals 3 times against 3.01 expected (p = 0.62).",
18: "Among 69 divided faces, 23 favour recurrence of whole lines, 4 favour stretches crossing a break and 42 tie (p = 0.0003).",
19: "Only 2 of 68 inferred stems occur with multiple final signs, a rate inside all four matched comparison ranges.",
20: "Across four readable corpora at Indus scale, the best segmenter reaches boundary F1 0.531 against 0.485 for cutting everywhere.",
21: "Branching entropy finds Ur III seal-legend word boundaries at F1 0.692 against 0.557 for cutting everywhere.",
22: "Initial-minus-final sign entropy is +0.260 across 1,859 distinct texts, against −0.017 to +0.018 under within-text shuffling.",
23: "Ur III seal-legend edge asymmetry changes from −0.204 by sign to +0.079 by word.",
24: "Indus stroke groups take 3.61 values per following sign on average, against 4.53–5.15 for matched Ur III counted items.",
25: "Sign 520 follows three strokes in 38 of 41 cases, and sign 585 follows seven in 16 of 17.",
26: "Among 1,430 eligible seals, 65 texts recur on 174 seals and 41 of those texts span sites.",
27: "None of 445 eligible seals with six or more signs shares its complete text with another.",
28: "The same-site share for recurring texts is 0.473 against a shuffled 0.448, leaving the planned concentration test unpassed (p = 0.31).",
29: "Of 89 identical-text seal pairs sharing an animal, 88 are unicorn pairs; only 1 of 42 pairs involving another animal matches.",
30: "Of 16 sealings or tags matching a seal text, 13 match only seals found elsewhere, carrying 4 of the 6 distinct texts.",
31: "In 1,000 simulated copied-record corpora, whole-object shuffling rejects a true null in 5.4% against 15.9% for record shuffling.",
32: "In 1,000 simulated imperfect-face corpora, keeping faces together rejects a true null in 5% against 11% for separate shuffling.",
33: "Reference-based method selection recovers 309 of 384 simulated symbol maps, against 283 for graph mapping and 168 for slot mapping.",
34: "The 118-sign class-and-gloss map fails to predict confirmation-half seal site and size, scoring at the 33.0th percentile of rearrangements.",
35: "Eleven confirmation seals ending in four specified signs show ×1.35 excess face area (p = 0.021), a result dependent on three 820 seals.",
36: "Parpola's 2010 Figure 6 matches H-912 B on CISI 2 p. 339, while its caption and prose name H-902.",
37: "The frozen fish order wins in 43 reserved dependency groups, loses in eight and ties in two (p = 0.0000003434).",
38: "H-912's primary source gives a 4–7-foot depth range; the export's 5.5 feet equals its midpoint.",
39: "The base register retains all 4,695 provisional objects and 5,680 faces with 225,223 attributed assertions and zero certified-fresh objects.",
40: "The reviewed H-1657 source chain places the seal on Room 591's floor in Trench 43, assigned to late Period 3C.",
41: "H-1688 joins H90-1600/3166-1 and lower street levels in Mound E area C, assigned to Period 3A.",
42: "Rao's jar-stopper interpretation of L-164 and the later tentative wooden-box interpretation share a cord-fastened flat underside in a twelve-object group.",
43: "Rao assigns Plate CLXI F to 1864 on p. 319 and 1830 on p. 325; CISI identifies them separately as L-164 and L-161.",
44: "Tell Brak REG257 joins Matthews catalogue 308 and TB1058, with a partly restored cup-bearer legend and zero corpus admissions.",
45: "The 22 H-2218–H-2239 tablets share a reported cutting direction and stroke order across at least three engravers, with sixteen recovered in a clump.",
46: "The 34-town register preserves 1,380 line and system records, 118 dated-part assertions and 620 radiocarbon assertions by architectural part.",
47: "Fourteen reviewed catalogue-view relations link thirteen held assets to twelve keys, adding zero newly available pilot photographs."
}

THEMES = [
("The corpus and its gaps", "These cards establish the population we can retrieve and the records still missing from it. Counts refer to the dated source frames on each card; the complete base register retains provisional identities and unresolved readings.", [7,8,9,39,47]),
("Sign order and prediction", "Preceding signs help predict a text, and closing positions draw from a smaller sign stock. Restoration accuracy and probability loss measure different properties, so both remain visible here.", [1,2,3,4,22]),
("Graphic families and added marks", "Shared base shapes carry predictive information, especially for rare signs. The separate tests of coder agreement and added marks show which grouping choices the evidence supports.", [10,11,12,13]),
("Lines, units and segmentation", "Catalogue line divisions provide observed boundaries to test inferred units against. Readable corpora show how much boundary recovery is possible at this scale and how the chosen unit changes a structural comparison.", [18,19,20,21,23]),
("Strokes and numbers", "Stroke groups are often fixed to their neighbouring signs. The numeral-equation result records exactly which arithmetic follows from its assumed equalities and physical range.", [6,24,25]),
("Seals, sealings and where texts travel", "Recurring seal texts connect sites, while long legends remain individually distinct in the selected corpus. Animal pairings, seal size and the source disputes over Lothal closures each constrain the proposed office interpretation.", [26,27,28,29,30,35,42,43]),
("Tablets, images and manufacture", "Text-to-image prediction differs among tablet genres. The Harappa clump adds a source-reported manufacturing relation and a recovery group whose physical use remains to be established.", [14,15,16,17,45]),
("Fish signs and H-912", "The fish cards separate a repeated graphic order from the identity and excavation context of the vessel-and-fish tablet. Functional readings of those constructions have their own conjecture cards.", [36,37,38]),
("Archaeological contexts of objects and towns", "Named excavation keys and architectural parts make published contexts traceable. Floor, street and building-phase assertions retain the dating basis supplied by each source.", [40,41,46]),
("Calibration and readable comparisons", "Failed predictions and known-system controls define what the methods can establish. Readable comparison objects enter a test population only after identity, completeness and language checks.", [5,31,32,33,34,44])]

def main():
    items = kb.index_items()
    cards = {int(x["id"][2:]): x for x in items if x["kind"] == "finding"}
    text = "# Findings\n\nA finding card records a result, its exact evidence, the population it covers and its status class. Start with a theme, then follow a card to the versioned output or primary-page source check. Counts and conclusions keep the date and scope of the original result.\n\nThe [status vocabulary](../registry/VOCABULARY.md) distinguishes verified computations, evaluations frozen before their reported outcome, exploratory refinements, failed tests, source reviews and synthetic controls; proposed, superseded and record classes preserve plans and research history. Verification tiers describe contributor review separately. The project's interpretations live in the [conjectures](../conjectures/README.md) and [working model](../WORKING-MODEL.md).\n"
    for title, intro, numbers in THEMES:
        text += "\n## " + title + "\n\n" + intro + "\n\n"
        for n in numbers:
            c = cards[n]
            text += f"- [{c['id']}]({Path(c['path']).name}) {SUMMARIES[n]} *{c['status']}*\n"
    inventory = json.loads((PACKAGE / "inventory.json").read_text(encoding="utf-8"))
    # Recompute citations now that the new cards exist.
    cited = {a for c in cards.values() for a in c["fields"]["registry_ids"]}
    text += "\n## Results recorded in packages but not yet carded\n\nThe remaining dated attempt records include measured outcomes, acquisition limits, reviews and preservation work. Their original status classes and recorded verification tiers appear below; an unspecified tier is labelled unrecorded. Related passes keep their own entries so that a later correction can be followed to its source.\n\n"
    uncarded = []
    summaries=json.loads((PACKAGE/'uncarded-summaries.json').read_text(encoding='utf-8'))
    for a in sorted(inventory["attempts"], key=lambda x:(x["date"],x["id"])):
        if a["id"] in cited:
            continue
        f = json.loads((ROOT / a["record"]).read_text(encoding="utf-8-sig"))
        package = ROOT / a["package"] if a["package"] else None
        if package:
            report = next((package/n for n in ["REPORT-v2.md", "REPORT.md", "README.md"] if (package/n).exists()), None)
            if report is None:
                report = next((ROOT/p.split('#')[0] for p in f['evidence'] if p.endswith('.md') and (ROOT/p).is_file()), None)
        else:
            report = None
        report = report or ROOT / a["record"]
        if a['id']=='DATA-ROUND-1-FOLLOW-UP-2026-10-13':report=ROOT/'experiments/2026-10-13-data-round-1-verification/README.md'
        outcome = summaries.get(a['id'],re.split(r'(?<=[.!?])\s+(?=[A-Z])', a["outcome"])[0].strip())
        # The inventory retains the verbatim outcome; the guide uses edited summaries.
        outcome = outcome.replace("\n", " ").replace("[", "\\[").replace("]", "\\]")
        if outcome and outcome[-1] not in '.!?': outcome += '.'
        text += f"- [{a['id']}](../../{report.relative_to(ROOT).as_posix()}) {outcome} *{a['status_class']}*, {a['verification_tier'] or 'unrecorded'}\n"
        reason='Retained in the package-results section after selecting nine cards for the source and register results named in this pass; no adverse evidence verdict is implied.'
        if a['status_class']=='record':reason='Coordination, presentation or preservation record; retained as research history.'
        elif 'IDENTITY' in a['id']:reason='Identity assertions or candidate bridges remain unresolved; no accepted physical-object merge is reported.'
        elif 'READABLE-SEAL' in a['id']:reason='No eligible legend admission; acquisition and exclusion decisions remain in the source package.'
        elif a['id'] in ['REBUS-BASE-RATE-2026-10-21','REBUS-BLIND-TEMPLATES-2026-10-22','REBUS-WINSLOW-2026-10-22']:reason='Later lexical reviews identify matching and extraction repairs; preserve the historical endpoint with its follow-ups before promoting a current reading result.'
        uncarded.append({"id":a["id"],"report":report.relative_to(ROOT).as_posix(),"summary":outcome,"reason":reason})
    (ROOT / "knowledge/findings/README.md").write_text(text, encoding="utf-8")
    (PACKAGE / "uncarded.json").write_text(json.dumps(uncarded,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    baseline = (PACKAGE / "baseline/WORKING-MODEL.md").read_bytes()
    claims = {
      'C-0002': 'Indus legends use seven classes arranged as household, name and office.',
      'C-0006': 'Mohenjo-daro seal legends kept their closing stock while their opening signs, variants and length drifted through the excavated sequence.',
      'C-0010': "Harappa seal legends kept their closing stock, opening signs, variants, length and inventory through Periods 3B and 3C.",
      'C-0011': 'Proto-Dravidian mīn meant both fish and star.',
      'C-0013': "Fish runs in a seal legend's name field give the holder's birth-star name from a closed class of about 30 to 40 forms.",
      'C-0014': "Parpola's interlocks arise from Tamil compound vocabulary and the choice of sign sequences examined.",
      'C-0015': "Harappan builders laid out town axes on a setting star, so deviation records layout date.",
      'C-0016': "The plains cities follow true north, while regional towns follow local landforms at deviations of 5 to 30 degrees anticlockwise.",
      'C-0017': 'Common rules preserved shared routes and services while neighbouring building groups changed their houses.',
      'C-0018': 'Sealings recorded responsibility at handovers between urban groups.',
      'C-0019': 'Harappa tablet series recorded obligations or entitlements for work on shared infrastructure.',
      'C-0020': 'Local farming households and specialist networks carried practical knowledge beyond Indus urban institutions.',
      'C-0021': 'Language contact carried regional farming knowledge and vocabulary into early Indo-Aryan-speaking communities.',
      'C-0022': 'A diagnostic operation in a Vedic farming rite descends through regional communities from an Indus-period practice.'
    }
    model = baseline.decode('utf-8-sig')
    if model.startswith('````markdown\n'):model=model[len('````markdown\n'):].removesuffix('\n````\n')
    appendix = "\n## Conjectures outside the integrated model\n\nThese cards hold claims outside the integrated account above. Each line gives the card's current status and credence; the card preserves its tests and revision history.\n\n"
    for item in items:
        if item['kind'] != 'conjecture' or item['id'] not in claims: continue
        f=item['fields'];appendix += f"- [{item['id']}](conjectures/{Path(item['path']).name}) {claims[item['id']]} Status {f['status']}; credence {f['credence']:.2f}.\n"
    # Insert only the allowed changelog line; append the one new section.
    model += "\n- 2026-10-27: added the list of conjectures outside the integrated model.\n" + appendix
    (ROOT/'knowledge/WORKING-MODEL.md').write_bytes(model.encode('utf-8'))
    print('47 cards in 10 themes;', len(uncarded), 'uncarded attempt entries; 14 model links added')

if __name__ == '__main__':
    main()
