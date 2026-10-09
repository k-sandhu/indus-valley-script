"""PDF-qualified object overlap; historical validation membership stays unknown."""
from pathlib import Path
import argparse, collections, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, OUT, WORK, read, write, sha

def main(output_root=OUT):
    output_root=Path(output_root).resolve()
    if not output_root.is_relative_to(OWN):raise SystemExit('Output must remain in package tree')
    if (output_root/'validation-audit-v3.json').exists():raise SystemExit('Endpoint exists')
    rows=read(WORK/'reading-inventory-v3.json')
    mh_by_cisi=collections.defaultdict(set)
    for r in rows:
        if r['primary_label'].startswith('MH'):
            for c in r['cisi_aliases']:mh_by_cisi[c].add(r['primary_label'])
    icit=collections.defaultdict(list)
    for r in rows:
        if r['primary_label'].startswith('ICIT') and r['is_reading_attempt']:icit[r['primary_label']].append(r)
    cohort=[]
    for label,entries in sorted(icit.items()):
        cisi=sorted({c for r in entries for c in r['cisi_aliases']})
        explicit=sorted({m for r in entries for m in r['mh_aliases']})
        illustrated=sorted({m for c in cisi for m in mh_by_cisi[c]})
        overlap=bool(explicit or illustrated)
        cohort.append({'icit_label':label,'pages':sorted({r['source_page'] for r in entries}),
          'reading_ids':[r['reading_id'] for r in entries],'cisi_aliases':cisi,
          'explicit_same_entry_MH_aliases':explicit,'MH_first_same_object_entries':illustrated,
          'has_documented_MH_object_overlap':overlap,'CISI_joined':any(r['joined_record_ids'] for r in entries),
          'historical_post_fix_check_membership':'unresolved',
          'source_status':'ICIT-first reading entry; source order alone cannot establish a held-out check'})
    special=[
      {'icit':'ICIT3656','cisi':'M-1357','mh':'MH2356','pages':[193,213],
       'classification':'Confirmed repeated object; one ICIT-first reading entry',
       'figure_check':'Both entries print vAsu–PATI–nI, matching the same CISI alias; each contains B032/B051/B003 in RTL order.'},
      {'icit':'ICIT3084','cisi':'M-634','mh':'MH2069','pages':[87,95,148,217],
       'classification':'Confirmed repeated object; alias within MH-first readings',
       'figure_check':'MH2069 heads the reading entry; ICIT3084 remains the attached catalogue alias.'},
      {'icit':'ICIT2816','cisi':'M-296','mh':'MH1387','pages':[166,200],
       'classification':'Confirmed repeated object; ICIT mention is an iconography remark',
       'figure_check':'No ICIT2816 primary reading entry; the discussion describes the object iconography.'},
      {'icit':'ICIT2717','false_cisi':'M-1714','true_cisi':'M-192','pages':[142,159,186],
       'classification':'Parser false overlap',
       'figure_check':'The M-1714 entry consistently has ICIT2346; ICIT2717 is attached to M-192 on page 186.'},
      {'icit':'ICIT1802','false_cisi':'M-1687','true_cisi':'H-922','pages':[121],
       'classification':'Parser false overlap','figure_check':'H-922 is attached to ICIT1802/MH4474; the next M-1687 entry has ICIT2485.'},
      {'icit':'ICIT415','false_cisi':'H-642','true_cisi':'H-1832','pages':[139,152],
       'classification':'Parser false overlap','figure_check':'ICIT415/H-1832 and MH4266/H-642/ICIT1557 are separate entries.'}]
    x={'status':'Exploratory','source_pages':[5,84,85],
       'ICIT_first_distinct_reading_labels':len(cohort),'ICIT_first_attempt_rows':sum(len(v) for v in icit.values()),
       'ICIT_first_labels_with_explicit_CISI':sum(bool(r['cisi_aliases']) for r in cohort),
       'ICIT_first_labels_CISI_joined':sum(r['CISI_joined'] for r in cohort),
       'ICIT_first_labels_with_MH_first_same_object_entry':sum(bool(r['MH_first_same_object_entries']) for r in cohort),
       'ICIT_first_labels_with_explicit_same_entry_MH_alias':sum(bool(r['explicit_same_entry_MH_aliases']) for r in cohort),
       'ICIT_first_labels_with_either_MH_overlap_basis':sum(r['has_documented_MH_object_overlap'] for r in cohort),
       'historical_checks_individually_identified':0,'historical_attempted_denominator':None,'historical_failed_readings':None,
       'reported_withdrawn_sign_values_in_foreword':1,'reported_withdrawn_values_in_letter':'a couple',
       'review_candidate_repeated_objects':3,'review_candidate_ICIT_first_readings':1,
       'review_candidate_MH_first_aliases':1,'review_candidate_iconography_mentions':1,'review_candidate_parser_false_overlaps':3,
       'cohort':cohort,'review_candidate_figure_audit':special,
       'interpretation':'Documented object reuse supplies a lower bound. ICIT-first entries include corrected MH transcriptions by the author’s own formatting rule. Neither absent paper MH references nor absent CISI joins establishes a new object in the historical validation batch.'}
    write(output_root/'validation-audit-v3.json',x)
    print(json.dumps({k:v for k,v in x.items() if k not in ('cohort','review_candidate_figure_audit')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-root',default=str(OUT));a=p.parse_args();main(a.output_root)
