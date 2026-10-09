"""Preserve the current package and register the PDF-review corrections before outcomes."""
import shutil
from pdf_followup import ROOT, OWN, RAW, read, write, sha

OUT = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / OUT.name
HISTORY = OWN / 'history/2026-10-09-before-pdf-review'

AMENDMENT = '''
## PDF-extension review response amendment, 9 October 2026

REVIEW-PDF.md and review-pdf/ are read-only evidence. Their independent reruns reproduce the earlier numbers and identify source and interpretation defects. Every earlier output, mapping, packet, return and reviewer file stays frozen. Current summaries and the ledger are copied to history/2026-10-09-before-pdf-review/ before editing. New aggregate outputs use pdf-review-response-2026-10-09-v1/; source text, revised inventory rows, renders and per-assignment predictions use its matching local raw directory. These refinements follow observed outcomes and remain Exploratory.

| ID | Inputs and statistic | Null/comparison | Decision and negative result |
|---|---|---|---|
| PR-D | Correct the 58-entry value-derivation inventory against the second-edition manuscript and reviewer derivation-recheck.json. Distinguish pala from dictionary-derived pāla and fitted bala; mark ASHVA/GO as pictorial readings supported by those same readings. Reclassify mIn(a), cAru and AS/ISH/ASTI, and correct DAna/ASHVA/GO locators. | Source classification, with exact manuscript pages and value-level provenance; no statistical null. | Non-lexical proposal origins describe Bonta's argument, not independent authentication. Unknown later extension histories stay unknown. |
| PR-L | Audit the frozen five-type clear-origin panel's attainable score and its 120-permutation histogram. Reuse the review's six source-classification sensitivities and class-restricted null, identifying their original paths. Additionally score a stricter non-lexical-anchor panel from explicit captions: roles 6, 12, 15, 17, 18, 19, 29, 31, 36, 50, 51, 52; role 6 only ma/mā, 17 only pala, 29 only mīna, 31 only caru, with other Table 18 bundles unchanged. Exclude ASHVA/GO, PU/PATI, fitted maha/bala and unknown later extensions. | Same pinned MW dictionary and whole-headword matching; exact primary and the frozen normalization secondary. Permute the involved bundles exhaustively through 40,320 assignments, otherwise 1,999 draws (seed 1). Report possible own-bundle combinations separately from donor-permutation scores. | A tail <= .05 is conditional lexical excess. A panel whose own bundles cannot reach the rejection score is uninformative for that claim. Report sample size, attainable hits and remaining source-selection dependence; do not infer true language from a tail. |
| PR-H | Reproduce the review's partial split: labels from manuscript pp. 39–77 (derivation narrative and Tables 7–17) define the 129-label derivation set. Early roles are 5, 47, 6, 17, 18, 19, 36, 29, 50, 51, 52. Score explicit-caption multi-role types before and after excluding those labels, then the review's no-PU/PATI/maha/bala variant and the stricter PR-L anchor panel with the same split. Record hit dependence on dictionary-derived variants. | Same bundle-permutation null and seed/draw rule as PR-L. Membership uses primary labels exactly as the review; a separately reported object-identity closure sensitivity also excludes later rows sharing a joined CISI family with a derivation label. | This separates named derivation examples from other examples, without sealing later examples or proving historical holdout. Exact tail <= .05 is conditional only. If no source permits a larger independently reserved sample, say why. |
| PR-F | Preserve final-only canonical counts. Admit one jar/arrow in final or penultimate position, following manuscript p. 15, retaining other rules; record T as the suffix from that terminal onward. Run under first, second and agreed-only mappings on the fixed 2,469-object population. Count clean/conflict/indeterminate, reasons and transitions; decompose the frozen clean count by M/P presence. | Within-text sign shuffles, 1,999 draws, seed 20261009, preserving token counts/length; clean count, null mean, central 95% reference range and add-one tail. | Tail <= .05 describes positional/grammar compatibility. Report how much of the canonical clean count lacks M. Wider boundaries and repeated-oval assumptions remain unresolved. The final-only result must reproduce; no old output is replaced. |
| PR-O | Separately count O–F–MS order among texts with at least two tokenized M units under each mapping, regardless of canonical clean classification. Keep recognized fish compounds and MA+numeral pairs whole. | Shuffle tokenized units within each text, 1,999 draws, seed 4242 as in field_decomposition.py. Denominator is fixed within each mapping. Report ordered/eligible texts, null fraction mean/range and add-one tail. | Tail <= .05 supports this necessary order tendency within the operational units. It does not identify the boundary or physical quantity. Report all three mappings. |
| PR-R | Correct the four catalogue-code transcriptions and twelve empty bracket-caption transcriptions against PDF layout/figures, preserving row IDs and the 859-attempt denominator. Widen the unclear flag to doubtful, questionable and question marks in row-local source text, keeping alias uncertainty distinguishable from reading uncertainty. Count changes, corrected transcription coverage and selected-row effects. | Source correction and descriptive census, no statistical null. | A keyword flag records explicit uncertainty, not reading failure. Source text and corrected rows remain raw; tracked deltas carry identifiers, counts and short paraphrases. Uncertain attachments are explicit. |
| PR-J | Flag R0374, R0633, R0860, R0873, R0917 and R0951 as probable mistyped-CISI joins using the review's source identifiers and glyph-length evidence. Count joined attempts/families with and without these four objects. Preserve original alias matches; do not substitute same-number ICIT joins. | Printed CISI/ICIT disagreement and figure-length comparison are descriptive evidence. No null or threshold establishes identity. | Report both denominators and the unresolved identity; retain the other conflicting identifiers and source-qualified joins separately. |
| PR-C | Update source records, ledger test annotations, readable report and file inventories. Correct Language Log attribution to the 7 March 2025 reader comment, distinguish the manuscript from the separate letter, and record Table 18 exposure for the first coder's 17 caption forms. | Exact comparison with preserved source and editorial snapshots. Preservation/replay checks require equality. | Source wording and frozen evidence remain unchanged unless a documented extraction/source correction requires a successor annotation. Existing conclusions are superseded in the current summaries, with their old files preserved. |

The lexical scoring code does not read external reference mappings. The first/second equality therefore follows by construction; agreed-only changes target eligibility alone. Remove lexical mapping-survival claims. State the two-AI-coder/specialist-review qualifier once in each summary, keep the blind second packet's status, and distinguish it from the informed first coding of caption forms. No new physical metrology fit is registered because independently joined quantity observations remain absent.
'''


def main():
    if HISTORY.exists() or OUT.exists() or LOCAL.exists():
        raise SystemExit('Registration exists; refusing overwrite')
    HISTORY.mkdir(parents=True)
    names = ['README.md', 'REPORT.md', 'RETROSPECTIVE.md', 'PROTOCOL.md', 'sources.json',
             'registry-entry.json', 'claims.jsonl', 'claims.md', 'ledger-coverage.json',
             'COMPLETION.md', 'FILES.json', 'SECOND-CODER-FILES.json', 'concordance.json']
    for name in names:
        if (OWN / name).exists():
            shutil.copyfile(OWN / name, HISTORY / name)
    baseline = []
    for base in (OWN, RAW):
        for path in sorted(base.rglob('*')):
            if path.is_file() and '.git' not in path.parts and '__pycache__' not in path.parts:
                if path.is_relative_to(HISTORY):
                    continue
                baseline.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
    write(HISTORY / 'baseline-files.json', baseline)
    with (OWN / 'PROTOCOL.md').open('a', encoding='utf-8') as stream:
        stream.write(AMENDMENT)
    OUT.mkdir(); LOCAL.mkdir()
    shutil.copyfile(OWN / 'PROTOCOL.md', OUT / 'PROTOCOL-registered.md')
    inputs = [OWN / 'REVIEW-PDF.md', OWN / 'review-pdf/derivation-recheck.json',
              OWN / 'review-pdf/lexical-recheck.json', OWN / 'review-pdf/heldout-sensitivity.json',
              OWN / 'review-pdf/field-decomposition.json', OWN / 'review-pdf/field-penultimate.json',
              OWN / 'review-pdf/join-audit.json', OWN / 'review-pdf/sample-readings.json',
              OWN / 'pdf-2026-10-09-v1/value-derivations-v2.json',
              RAW / 'pdf-2026-10-09-v1/reading-inventory-v4.json',
              RAW / 'pdf-2026-10-09-v1/lexical-selection-v2.json']
    write(OUT / 'registration.json', {'date': '2026-10-09', 'status': 'Exploratory',
          'protocol_sha256': sha(OUT / 'PROTOCOL-registered.md'),
          'inputs': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)} for path in inputs]})
    print('Registered PDF-review response; earlier files preserved.')


if __name__ == '__main__':
    main()
