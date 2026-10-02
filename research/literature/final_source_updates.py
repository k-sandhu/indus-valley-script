from pathlib import Path
import json,fitz,hashlib
B=Path(__file__).parent
q=B/'metrology/numerical_source_premises.json';j=json.loads(q.read_text(encoding='utf-8'))
e=next(x for x in j['premises'] if x['id']=='E1_bangle_range')
e['unresolved']='The82 fragment count and15–20 reconstructable bangle total remain unverified historical interpretations cited throughWells2015. The inscription reportedly begins with three reconstructed eroded signs. OriginalVidale1987 chapter now inspected does not identifyM1383 or provide those numbers.'
e['original_vidale_check']={
 'title':'More Evidence on a Protohistoric Ceramic Puzzle',
 'author':'MassimoVidale',
 'book':'Reports on Field Work Carried out at Mohenjo-Daro, InterimReportsVol2, Pakistan1983–84, editedM.Jansen/G.Urban',
 'publication_year':'1987 in primary-author bibliographies; actual title differs from frequently cited MoreInformation',
 'url':'https://ignca.gov.in/Asi_data/77275.pdf',
 'sha256':'e488536488de84426de6391764a8364275aa557613bc0efb82ff385e561e8c6f',
 'coordinates':'Printed105–111/PDF108–114; original titlePDF6, contentsPDF8',
 'object':'FusedDK-B,C kiln-slag block, found in excavation dump endApril1984, documentedFeb–March1985;23×19×13.5cm',
 'directly_attested':'Printed106–107/PDF109–110:two superposed stonewarebanglessurvive in one innerCoatedSubcylindricalBowl; this is a firingmodule observation.',
 'reconstruction':'Printed107/PDF110 describes apparently at least7innerbowls across block, uncertain whetheroneoutercontainer orcontiguousseries. Printed108/PDF111 uses hypothetical5bowls×2bangles=10 in a15cmdiameter×30cmhigh outercontainer and explicitly calls totalconjectural; apparent7bowlsanomaly retained.',
 'negative_search_scope':'Allseven chapter pages visually inspected; no82fragments,15–20reconstructabletotal,IndusinscriptionorM1383inventory observed. No physicalidentity join toM1383 established.',
 'scope_limit':'General firing reconstruction can constrain a technological model, not an inscription-specific count without artifactjoin.',
 'duplicate_scan':'384PDFpages repeat192pages atoffset192; all192renderedimagepairs checked with zero mismatches. Repeatedpages are not independent evidence.'}
j['conditional_algebra_result']['range8to13']='Only10,8,6 if both assumed equalities and the unverified inscription-specific historical range are imposed'
j['conditional_algebra_result']['range8to18']='Same conditional unique solution; generic firing reconstruction alone does not establish M1383identity orcount'
q.write_text(json.dumps(j,indent=2,ensure_ascii=False),encoding='utf-8')
q=B/'metrology/numerical_source_audit.md';s=q.read_text(encoding='utf-8')
s+='\nThe originalVidale1987 chapter has now been inspected: actual title **More Evidence on a Protohistoric Ceramic Puzzle**, printed105–111/PDF108–114 of [government-hosted InterimReportsVol2](https://ignca.gov.in/Asi_data/77275.pdf). It describes a fusedDK-B,C slag block foundApril1984 and documented1985. Two stoneware bangles survive in one inner bowl, while the overall assembly is reconstructed. Printed108 explicitly calls five bowls/two bangles each/ten per outercontainer conjectural and notes an apparent seven-bowl anomaly. The chapter supplies neither82fragments nor15–20completebangles nor anM1383inventory/inscription join. Those inscription-specific figures remain an unverified historical reconstruction throughWells2015. This strengthens the source audit, not the numeralvalue inference. All192pages are duplicated atoffset192; repetitions are not separate witnesses.\n'
q.write_text(s,encoding='utf-8')
q=B/'source_retrieval_log.json';a=json.loads(q.read_text(encoding='utf-8'))
for x in a:
 if x.get('id')=='jansen_urban1987_interim2':
  x.update({'identity_verified':True,'actual_title':'Reports on Field Work Carried out at Mohenjo-Daro, InterimReportsVol2, Pakistan1983–84','title_inspection':'OriginalPDF6 title,PDF8 contents; Vidaleactualchaptertitle MoreEvidenceon aProtohistoricCeramicPuzzle,printed105–111/PDF108–114','duplicate_pages':'192pairedpages,offset192,renderedpixelsmatchallpairs','chapter_identity_limit':'Not identified as M1383; no82fragments or15–20total in chapter.'})
p=B/'sources/khanna_merriam2025_functions.pdf';d=fitz.open(p)
(B/'sources/khanna_merriam2025_functions.txt').write_text('\n'.join(f'[PDFPAGE{i+1}]\n'+x.get_text() for i,x in enumerate(d)),encoding='utf-8')
if not any(x.get('id')=='khanna_merriam2025_functions' for x in a):
 a.append({'id':'khanna_merriam2025_functions','url':'https://www.ijcaonline.org/archives/volume187/number64/khanna-2025-ijca-926075.pdf','source_type':'OfficialjournalPDF','actual_title':'A Computational Analysis of the Indus Script: Identifying Sign Functions in Logo-Syllabic Writing Systems','authors':['RuhanKhanna','LouieMerriam'],'publication':'InternationalJournalofComputerApplications187(64),December2025,19–22','doi':'10.5120/ijca2025926075','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(d),'bytes':p.stat().st_size,'identity_verified':True,'local_file':str(p)})
q.write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
q=B/'chart_complete/duplicate_labels/adjudication.json';a=json.loads(q.read_text(encoding='utf-8'))
for x in a['rows']:
 if (x['pdf_page'],x['column_0based'],x['row_0based'])==(20,4,21):
  x['lower_confidence']='medium';x['lower_alternatives']=[485,486];x['candidate_union']=[465,485,486]
  x['note']='Literature reader best465; independentcorpusreader source16x still sees486 or485. Preserve three-code union, not resolved by uniqueness. Initialparent reference retained separately.'
q.write_text(json.dumps(a,indent=2),encoding='utf-8')
q=B/'evidence_and_novelty_matrix.md';s=q.read_text(encoding='utf-8')
row='| Singleton/context expansion and substitution resistance | [Khanna andMerriam2025](https://www.ijcaonline.org/archives/volume187/number64/khanna-2025-ijca-926075.pdf), IJCA187(64):19–22, §§2–5 | Expands singleton seeds by shared contexts, clusters signs/pairs and proposes substitution-resistant phonetic units; lists002-817/820/861. | Singleton=>logogram andboundpair=>syllabic are assumptions, not decoded facts. Shared-context discovery is prior; stronger alias-safe holdouts/nulls remain distinct evaluations. |\n'
s=s.replace('| Formal grammar and segmentation |',row+'| Formal grammar and segmentation |')
row='| [Glossa-Lab2026project](https://github.com/BitConcepts/glossa-lab), first-partyREADME/CITATIONS | Unreviewedpubliccode/projectclaims, mutablemain | Corpusacquisition,crosswalks,artifactanchors,matching/readingpipeline; claims extensiveProtoDravidianreadings. | No reading accepted here. Broadpipeline/corpus-reconciliation novelty must not be claimed; exactassaycomparison needs versionedreproduction. |\n'
s=s.replace('| [Indusvalleyscript2026]',row+'| [Indusvalleyscript2026]')
s=s.replace('preserves thirteen lower-code ambiguities','preserves fourteen lower-code ambiguities onPDF21 afterlaterduplicate-label reinspection')
s+='\nThe primaryVidale1987 chapter is now available through government77275. Its actualtitle is *MoreEvidenceon aProtohistoricCeramicPuzzle*, not the bibliographicvariant *MoreInformation*. Printed105–111/PDF108–114 concerns a fusedslagblock, not an identifiedinscribedM1383pot. Its overallbangleassemblycount is explicitly conjectural. It supplies no independent82-fragment or15–20complete-bangle count. The originalrange remains conditional; see updated`metrology/numerical_source_premises.json`.\n'
q.write_text(s,encoding='utf-8')
q=B/'chart_complete/README.md';s=q.read_text(encoding='utf-8')
s+='\n## Later duplicate-label source adjudication\n\n`duplicate_labels/adjudication.json` preserves16originalcells checkedafterparent flaggedduplicatebestcodes. This is post-comparison source reinspection, not a freshblindscore; allprior337and175tables remain in`*_before_duplicate_adjudication`files. PDF21c8r16 hasbest63/alternative53; fourteenPDF21lowercodesremainambiguous. PDF20c7r25was corrected363=>383 andc9r19 576=>676. Two originalnumeric506labelsremainduplicated; no uniquenessconstraintisused. PDF20c4r21 has readerdisagreement465/485/486 and remainsuncertain in the cross-readeradjudicationfile, rather than being forced to agree. Initialfresh20scoresremainunchanged.\n'
q.write_text(s,encoding='utf-8')
print('Updated original Vidale premises, exact2025 title/priority, duplicate uncertainty and provenance.')
