"""Append externally observable PDF work to the editable retrospective."""
from pdf_followup import OWN

INTRO = '''The 9 October PDF follow-up resolves the missing-glyph limit recorded in the earlier phases below. It adds a frozen 96-target first coding and blind packet, a 1,200-row source inventory with 859 reading attempts, canonical field tests and expanded lexical comparisons. All first-coder outcomes remain Exploratory. The source-explicit clear-origin lexical subset has five types and an exact tail of 0.20; historical validation and physical metrology remain unresolved. [PDF report](REPORT.md).
'''

TEXT = '''
## PDF follow-up, 9 October 2026

The owner supplied the 259-page second edition. Registration and pre-PDF hashes preceded witness extraction and all calculations. The source inventory and chart reference contributors supplied starting annotations and references. Their files and the first pass were read and reused without edits. No new third-party source was downloaded. The PDF hash and Ghostscript metadata match the supplied witness; all 259 page pairs have the same alphanumeric character multiset. Layout differences prevent ordered equality on 173 pages, so the section/table sequence and sample renders were also checked. The PDF is unfoliated; page-map.json records one-based PDF pages and null printed folios.

Image extraction initially failed while building a contact sheet because inline images lacked file paths. An inline recovery attempt also needed correction before the successor completed. The retained partial extraction and successor preserve those stages. The PDF has 2,650 image resource entries, 223 unique referenced image objects and 8,402 displayed placements, including 3,544 inline placements. Repeated placements and allographs differ from sign counts. Local clip renders recover inline drawings; images and crops remain raw-only.

Table 18 supplies 58 assignment labels and 65 drawings, explaining the stated 55 plus three terminal/logographic entries. Seventeen additional caption-associated forms and fourteen field targets give 96 coding targets. The 79-target mapping and its 17-form successor were each frozen before their packet stages and lexical scoring. The successor has 85 singleton Mayig assignments, three ambiguous and eight unmapped. Wells/Helsinki candidates cover 88. The blind packet retains neutral IDs, 96 crops, 687 chart cells, Mayig metadata/contact sheets and a blank 96-row return template. No second coding has arrived.

The PDF changes the provisional juncture inventory: bent pair 060 replaces full-height pair 032, which belongs to a fish compound. It distinguishes fish plus comb and fish plus full-height pair, and exposes pooled included/excluded oval forms under Wells 832. The source also reverses DAna1/DAna2 graphic labels between Table 18 and the individual sections. Two SAVA captions print a triangular form associated visually with KARA; U149 was excluded before scoring. Candidate mappings were preserved after outcomes rather than adjusted to improve fits.

The first 955-entry parser sometimes attached a caption that lay slightly above its label to the preceding entry. Renders exposed this error. A five-point baseline allowance corrected source attachments; prior outputs remained frozen. Supplemental continuations, parenthetical figures and Table 21 extend the final inventory to 1,200 source rows, 859 attempts and 341 structural examples. Repeated and deferred entries remain separate. Explicit manuscript CISI aliases join 713 attempts to 338 object families; 146 remain unjoined. A final descriptive successor recomputes lists and flags 33 joined entries with source qualifiers. Equal ICIT numbers across editions were never used as a join.

The narrow canonical field test gives 942 clean, 349 conflicting and 1,178 indeterminate texts, against a shuffle mean of 419.87. Mayig gives 42/12/46 on 100 overlapping clear lines. Fish adjacency with the PDF compounds gives 142 versus 55.72. Lexical fish uses, pooled oval classes, missing boundaries and the 19 extended Table 19 templates limit interpretation of canonical conflicts. The older fish maximum/repeat claim stays withdrawn; prior numerical files remain unchanged.

The expanded lexical selection was frozen before scoring: 640 identifiable occurrences, with 219 exclusions in the final 859-attempt inventory. Full selection gives 84/228 exact type matches versus mean 27.83, tail .0005. After seeing that output, a registered source-explicit sensitivity removed complete-drawing fallbacks, including repeated-pala quantity figures. It gives 83/206 versus 28.75, tail .0005. Removing explicit dictionary-context origins, unknown later-extension provenance and fitted maha/bala alternatives leaves five types: 2/5 exact, tail 24/120=.20; normalized 3/5, tail 70/120=.5833. A small source-selected anchor set remains, and the paper supplies zero individually identifiable historical held-out entries. The broad-set excess cannot resolve lexical construction dependence.

The object audit preserves all six earlier corrections. Its 68 ICIT-first labels include 48 corpus joins. Seven unqualified same-entry MH aliases and ICIT3656's repeated MH object give eight confirmed links. The PDF page 92 question mark beside ICIT3355/MH2280 is separated as one questioned link in a v4 audit. An ICIT-first label can be a corrected transcription of MH material. The historical check batch, fixed pre-check values and attempted/failure denominator remain unidentified.

The ledger now has 1,021 source-linked records: 130 retained, 32 PDF source additions and 859 reading annotations. Ninety retained records acquire page or glyph corrections. Generic semantic categories attached to reading glosses remain extraction annotations needing source sampling. Some unlabelled/damaged figures and caption attachments need manual adjudication, wider field rules and phonological/multiword acceptance remain unfinished, and no physical quantity join is available. The work completed a bounded inventory and conditional tests; completion scope and verification are recorded separately. FILES.json and PDF-FILES.json identify the created and changed paths.
'''

if __name__=='__main__':
    p=OWN/'RETROSPECTIVE.md';text=p.read_text(encoding='utf-8-sig')
    if '## PDF follow-up, 9 October 2026' in text:raise SystemExit('Retrospective already updated')
    header,body=text.split('\n',1)
    p.write_text(header+'\n\n'+INTRO+body+'\n'+TEXT,encoding='utf-8')
