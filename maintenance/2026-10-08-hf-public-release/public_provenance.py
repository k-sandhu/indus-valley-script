"""Publish self-contained chart provenance while retaining private source pins."""
from build_release import ROOT,read,dump

def write_public_provenance(release,builder):
    doc=release/'docs/CHART-REVIEW.md'
    doc.write_text('''# Chart review priorities

The chart numeric reference uses the printed inventory in Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979), PDF pages 20–21. The chart table and provenance/chart-changes.json contain the reviewed values and all 36 numeric-record deltas. The unchanged PNG crops preserve the printed witness. The card describes the scope of the AI readings and pixel checks.

Expert inspection should prioritize these drawings:

| Cell or group | Observation to check |
|---|---|
| p20_c4_r13, code 360 | Medium-confidence digits; the earlier reading dispute involved 350 versus 360. |
| p21_c7_r21, code 734 | Worn printed digits. |
| p21_c4_r21, class 300 | Faint class digits. |
| p21_c5_r32, p21_c5_r34, p21_c6_r1 | The one-, two- and three-tick U variants: retain 205, correct 205 to 206, and correct 206 to 208, respectively. |
| p20_c3_r33 and p20_c4_r1, class 86 | Check the class-86 reading and the adjacent branched-stem code corrected from 506 to 508. |
| p20_c4_r21, p21_c0_r21, p21_c0_r29, p21_c6_r9, p21_c6_r31 | Other corrected primary labels: 465 to 486, 360 to 380, 579 to 679, 385 to 386 and 285 to 286. |

Find each cell by pdf_page, column and row in chart_reference; image shows its original crop. Class means the printed upper inventory number (rank in the table), and code means the lower number. Previous-value columns retain the earlier reading where a field changed. These are graphic inventory labels.

## Public provenance pointers

The packaging code retains exact original witness paths and hashes outside the public dataset. Here, public pointers name this note, chart_reference, benchmark/reader-metadata.json and benchmark/expected-metrics.json. Opaque source labels identify excluded parent witnesses; they are provenance labels rather than downloadable files. Reader metadata preserves returned observations about process exposure and identifies their local witness by such labels.
''',encoding='utf8')
    path=release/'provenance/chart-changes.json';changes=read(path)
    def portable_notes(value):
        if isinstance(value,list):return [portable_notes(v) for v in value]
        if isinstance(value,dict):
            return {k:('docs/CHART-REVIEW.md' if k=='evidence_file' else portable_notes(v)) for k,v in value.items()}
        if isinstance(value,str):
            for old in ['cell-observations-v2.1.json','REVIEW.md','RECOMMENDED-USE.md']:
                value=value.replace(old,'docs/CHART-REVIEW.md')
            value=value.replace('Package P','chart audit').replace('Package M','benchmark pipeline').replace('coordinator-task-ledger.jsonl','benchmark/reader-metadata.json')
        return value
    dump(path,portable_notes(changes))

if __name__=='__main__':raise SystemExit('Called by the documentation builder.')
