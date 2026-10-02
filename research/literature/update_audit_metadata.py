"""Retain historical retrieval identifiers and add corrective descriptive metadata."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
path=ROOT/'source_retrieval_log.json'
records=json.loads(path.read_text(encoding='utf-8'))
for row in records:
 if row.get('id')=='frenez_2018_identity':
  row['metadata_correction']='Mislabelled file identifier retained. Actual document: Rajesh P.N.Rao, The Indus Script and Economics, published2018 chapter pp518-525; not Frenez.'
  row['verified_author']='Rajesh P.N.Rao'
  row['verified_title']='The Indus Script and Economics'
  row['status']='published Rao chapter with cover and contents; initial Frenez identifier erroneous'
 if row.get('id')=='frenez_cv_official':
  row['publication']='2024-07-10 author CV'
  row['exact_location']='p7 lists expanded Hybrid identities manuscript in preparation; p6 lists2014 Stockholm presentation'
path.write_text(json.dumps(records,indent=2),encoding='utf-8')
path=ROOT/'evidence_and_novelty_matrix.md'
t=path.read_text(encoding='utf-8')
replacements={
 'Version 1, prepared 1 October 2026.':'Version 2, updated 2 October 2026.',
 'discussion of superior/inferior signs and ICIT mergers':'PDF p.18, section7',
 'functional-class analysis | Uses positions':'pp.6–16,20–24; p.7 Criterion2 | Uses positions',
 'They do not independently establish absence of phonetics.':'Criterion2 assumes other faces are semantically complete to infer a solitary lexeme. These criteria do not independently establish absence of phonetics.',
 'Results/Discussion | Sign networks':'preprint pp.3–11, p.10 Fig.13 and pp.11–12 discussion | Sign networks',
 'design classes; [Daggumati':'PDF pp.7–17 and34–36, design classes/conclusion; [Daggumati',
}
for old,new in replacements.items():
 if old in t:t=t.replace(old,new)
 elif new not in t:raise ValueError('Expected old or replacement string absent: '+old)
extra='''

The scan duplication is verified image by image: PDF1–431 and432–862 repeat at offset431 without exception. IntroductionXXIV–XXV explicitly defines additional photographs; Corrigenda p.375 additionally identifies duplicate catalogue numbers and mirrored illustrations. See `cisi1_counting_and_errata.md`. H355's B/C sides are separately captioned three-stroke modules; the H356=>H354bis correction does not affect H355. H2238 remains without a retrieved primary illustration.

The Gulf external-anchor audit is in `external_phonetic_anchor_audit.md`. The examined familiar objects do not provide aligned Indus/cuneiform texts. Shu-ilishu establishes a named interpreting role; Gadd's no.1 has cuneiform plus bison imagery; no.6 is a different cylinder. Their contents do not yield an Indus phonetic mapping.
'''
if 'The scan duplication is verified image by image:' not in t:t+=extra
path.write_text(t,encoding='utf-8')
print('Corrective metadata and matrix locations updated; original IDs and retrieval failures retained.')
