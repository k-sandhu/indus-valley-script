"""Source qualifications and counts from preserved PDF inventory; no score changes."""
import collections, re
from pdf_followup import OUT, WORK, read, write, sha

def main():
    for name in ['reading-coverage-v5.json','validation-audit-v4.json']:
        if (OUT/name).exists():raise SystemExit('Successor already exists: '+name)
    rows=read(WORK/'reading-inventory-v4.json')
    attempts=[r for r in rows if r['is_reading_attempt']]
    prior=read(OUT/'reading-coverage-v4.json')
    qualifiers=[]
    for r in rows:
        # A qualifier may concern a damaged image, an alias or its interpretation.
        # Preserve the full source excerpt locally; do not automatically reject.
        txt=r.get('source_text','')
        if r['cisi_aliases'] and re.search(r'possibly|perhaps|\(\?\)|uncertain',txt,re.I):
            qualifiers.append({'reading_id':r['reading_id'],'page':r['source_page'],
                'primary_label':r['primary_label'],'CISI_aliases':r['cisi_aliases'],
                'joined':bool(r['joined_record_ids']),
                'classification':'Source qualifier in same entry; manual object-alias review needed'})
    x={k:v for k,v in prior.items() if k not in ['unjoined_ids','Table21_rows']}
    x.update(inventory_sha256=sha(WORK/'reading-inventory-v4.json'),
        inventory_rows=len(rows),reading_attempt_rows=len(attempts),
        unique_primary_labels=len({r['primary_label'] for r in rows}),
        CISI_joined_rows=sum(bool(r['joined_record_ids']) for r in rows),
        CISI_joined_attempt_rows=sum(bool(r['joined_record_ids']) for r in attempts),
        unique_CISI_aliases=len({c for r in rows for c in r['cisi_aliases']}),
        unique_joined_object_families=len({c for r in rows for c in r['joined_object_family_ids']}),
        attempts_with_explicit_transcription=sum(bool(r.get('proposed_reading')) for r in attempts),
        unclear_or_unattested_attempt_rows=sum(r['unclear_or_unattested_flag'] for r in attempts),
        unjoined_attempt_rows=sum(not r['joined_record_ids'] for r in attempts),
        unjoined_reading_ids=[r['reading_id'] for r in attempts if not r['joined_record_ids']],
        structural_nonattempt_rows=len(rows)-len(attempts),
        source_kind_counts=dict(collections.Counter(r['source_kind'] for r in rows)),
        qualified_source_entries=len(qualifiers),
        qualified_source_joined_entries=sum(r['joined'] for r in qualifiers),
        source_qualified_aliases=qualifiers,
        Table21_rows=prior['Table21_rows'],
        scope='Source extraction inventory; repeated illustrations and partial attempts retained. Qualifier flags require manual adjudication.')
    # Earlier supplemental totals predate Table 21 additions and promotions.
    for k in ['supplemental_figures','supplemental_reading_figures','supplemental_structural_figures']:
        x.pop(k,None)
    write(OUT/'reading-coverage-v5.json',x)
    v=read(OUT/'validation-audit-v3.json')
    v['supersedes']='validation-audit-v3.json; source qualification only'
    v['ICIT_first_labels_with_confirmed_MH_overlap']=8
    v['ICIT_first_labels_with_questioned_MH_overlap']=1
    for r in v['cohort']:
        r['MH_overlap_source_qualification']=('Questioned MH2280 alias, PDF p. 92' if r['icit_label']=='ICIT3355'
            else 'Unqualified source link' if r['has_documented_MH_object_overlap'] else 'No documented paper link')
        r['has_confirmed_MH_overlap']=r['has_documented_MH_object_overlap'] and r['icit_label']!='ICIT3355'
    v['interpretation']='Eight ICIT-first labels have unqualified paper links to MH material; ICIT3355 has a questioned MH2280 alias. The historical post-fix check batch and success/failure denominator remain unidentified.'
    write(OUT/'validation-audit-v4.json',v)
    print({k:x[k] for k in ['inventory_rows','reading_attempt_rows','CISI_joined_attempt_rows',
        'unjoined_attempt_rows','unique_CISI_aliases','qualified_source_entries','qualified_source_joined_entries']})

if __name__=='__main__':main()
