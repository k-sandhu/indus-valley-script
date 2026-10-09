"""Integrate PDF source annotations and reading claims; retain historical endpoints."""
from pathlib import Path
import collections, json, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, RAW, OUT, WORK, read, write, sha

def main():
    original=[json.loads(l) for l in (OWN/'history/2026-10-09-before-pdf/claims.jsonl').read_text(encoding='utf-8').splitlines()]
    rows=json.loads(json.dumps(original));mapping=read(OUT/'mapping-v2-frozen.json');byid={r['sign_id']:r for r in mapping['rows']}
    catalog=read(WORK/'sign-catalogue-v2.json');table=collections.defaultdict(list)
    for r in catalog:
        if r['table_entry']:table[r['table_entry']].append(r['sign_id'])
    def pages(match):
        s=match[1];return 'PDF pp. '+re.sub(r'\d+',lambda x:str(int(x[0])+1),s).strip()
    changes=[]
    for old,r in zip(original,rows):
        if r['source_id']=='B24':
            loc=r['source_location'];new=re.sub(r'(?:text )?segments?\s+([\d\s,–-]+(?:and\s+\d+(?:[–-]\d+)?)?)',pages,loc)
            if new!=loc:r['page_text_location']=loc;r['source_location']=new
            r['page_locator_basis']='Unfoliated PDF; one-based physical leaf, verified against page-text segment index + 1.'
        number=int(r['id'][1:])
        if 55<=number<=112:
            entry=number-54;ids=table[entry]
            r['previous_graphic_identity']=r['graphic_identity']
            r['graphic_identity']={'catalogue_ids':ids,'mapping_file':'pdf-2026-10-09-v1/mapping-v2-frozen.json',
                 'candidate_Mayig_classes':sorted({c for s in ids for c in byid[s]['mayig_candidates']}),
                 'status':'Exploratory; first coder only'}
            r['test_ids']=sorted(set(r['test_ids'])|{'P-C','P-L'})
        if number==72:r['paraphrase']='Table 18 labels the bow-alone drawing DAna1, with proposed dhana/dhāna/dāna values; the section heading reverses the DAna1/DAna2 labels.'
        if number==73:r['paraphrase']='Table 18 labels the person-with-bow drawing DAna2, with the same proposed values; its section heading calls this DAna1.'
        if old!=r:changes.append({'id':r['id'],'changed_fields':[k for k in r if r.get(k)!=old.get(k)]})
    def add(location,kind,claim,evidence,tests,extra=None):
        r={'id':f'Q{len(rows)+1:03d}','source_id':'B24','source_location':location,'type':kind,
          'paraphrase':claim,'quotation':None,'offered_evidence':evidence,'testable_here':bool(tests),
          'test_ids':tests,'assessment_status':'Exploratory','graphic_identity':None,
          'note':'Proposed sounds, meanings and readings remain the author’s assignments. Mapping awaits second coding.'}
        if extra:r.update(extra)
        rows.append(r)
    newclaims=[
      ('PDF pp. 78–82','method','He counts 55 main assignments and places three additional logographic entries in Table 18.','The table has 58 labelled entries and 65 drawings; AS, ISH and ASTI are the three additional entries.',['P-S']),
      ('PDF pp. 20–21','segmentation or structure','The three junctures are a short single stroke, two short strokes and a bent pair.','B077/B078/B079; first-coder candidates Wells 002/060/001.',['P-C','P-F']),
      ('PDF p. 21','segmentation or structure','His F inventory includes basic fish combined with a comb or two full-height strokes.','B074/B075 have separately drawn components; RTL candidates 415–220 and 032–220.',['P-C','P-F']),
      ('PDF p. 21','segmentation or structure','He limits canonical O fields to two nonrepeating units and F fields to three.','Source inventory and paragraph on page 21; exceptions and lexical uses require field assignment.',['P-F']),
      ('PDF pp. 48, 80','segmentation or structure','He treats two forked-staff forms as allographs, although the reference classes distinguish their drawings.','B017/B018; source claims comparable distribution and no co-occurrence.',['P-C']),
      ('PDF pp. 80, 132, 134','sign value (phonetic or logographic)','The table and individual sections reverse the DAna1/DAna2 labels for bow and person-with-bow.','The proposed value bundles agree; the graphic labels differ.',['P-C']),
      ('PDF pp. 109–110','method','He adds initial maha/mahā to rescue readings that otherwise yield tentative ma compounds.','His discussion explicitly contrasts initial contexts with the original mātra anchor; sensitivity removes this extension.',['P-L']),
      ('PDF p. 76','method','He adds bala as a pala alternative when discussing the unattested pala-pati pairing.','The clear-origin sensitivity removes this dictionary-fitted variant.',['P-L']),
      ('PDF pp. 84–85','method','An ICIT-first heading can identify the more accurate transcription of an already known Mahadevan entry.','His formatting rule explains primary index use; ICIT-first alone has unresolved historical check membership.',['P-V']),
      ('PDF pp. 86, 229','sign value (phonetic or logographic)','He allows doubled DEVA to represent a feminine DEVI or a reduplicated divine epithet.','This contextual conversion exceeds literal concatenation of Table 18 deva bundles.',['P-L']),
      ('PDF pp. 159, 170; comparator p. 81','reading of a text','Two captions retain a sava label beside a triangular drawing that the first coder associates with kara.','U149 source-caption associations conflict with its visual Table 18 family; excluded pending second coding.',['P-C','P-L']),
      ('PDF pp. 234–240','segmentation or structure','He supplies 19 extended numerical or metrological templates, including mixed core and measure clusters.','These are wider than the canonical O–F–MS rule; the compatibility calculation has a narrower registered scope.',['P-F']),
      ('PDF pp. 249–251','reading of a text','He interprets seven full patterned examples as predicates, named participants and asset amounts.','Table 21; seven rows in reading-coverage-v4.json, Table21_rows.',['P-R','P-F']),
      ('PDF p. 24','historical, linguistic or archaeological','He links seven fish units and three oval units to two weight series described by Marshall.','This comparison supplies an inventory-size hypothesis; physical quantity joins remain zero.',['M1']),
      ('PDF pp. 5, 84–85','evaluation criterion','He reports a Mahadevan-first stage followed by an ICIT check and one withdrawn sign value.','The paper gives source history without the individual historical attempt list or pre-check assignment file.',['P-V'])]
    for args in newclaims:add(*args)
    for r in read(WORK/'additional-valued-catalogue.json'):
        add('PDF pp. '+', '.join(map(str,r['source_pages'])),'sign value (phonetic or logographic)',
            f'Caption-associated drawing {r["sign_id"]} is linked to Table 18 entry '+','.join(map(str,r['caption_proposed_role_candidates']))+'.',
            'Anchored caption alignment is recorded in local additional-valued-catalogue.json, witness_occurrences; its visual crosswalk is in mapping-v2-frozen.json.',
            ['P-C','P-L'],{'sign_catalogue_id':r['sign_id'],'source_value_consistency':r['source_value_consistent_with_visual_Table18_family']})
    readings=read(WORK/'reading-inventory-v4.json');countbefore=len(rows)
    for r in readings:
        if not r['is_reading_attempt']:continue
        text=(r.get('proposed_gloss') or '').lower()
        kinds=[]
        for pattern,description in [(r'king|queen|monarch|royal|prince|ruler','royal names or titles'),
          (r'wealth|treasur|money','wealth or treasury terms'),(r'god|divine|deit|brahma|shiva|vishnu','divine names or epithets'),
          (r'wife|husband|spouse|mistress|feminin','spouse or feminine titles'),(r'belong|property|owned|owns','ownership expressions'),
          (r'grain|palas|mina|amount|exactly','asset or measure notations'),(r'guard|protect','protection terms')]:
            if re.search(pattern,text):kinds.append(description)
        if kinds:claim=f'He relates the proposed interpretation under {r["primary_label"]} to '+', '.join(kinds[:3])+'.'
        elif r.get('proposed_reading'):claim=f'He supplies a whole or partial named-sign reading under {r["primary_label"]}.'
        else:claim=f'He includes {r["primary_label"]} as an example under a proposed value, with a deferred or absent individual transcription.'
        add(f'PDF p. {r["source_page"]}, entry {r["primary_label"]}', 'reading of a text',claim,
          f'Local reading-inventory-v4.json row {r["reading_id"]}: primary_glyphs, proposed_reading, proposed_gloss and caption_blocks.',
          ['P-R','P-L','P-V'],{'reading_inventory_id':r['reading_id'],'catalogue_label':r['primary_label'],
          'CISI_aliases':r['cisi_aliases'],'glyph_count':len(r['sign_sequence_visual_ltr']),
          'source_entry_kind':r['source_kind'],'unclear_or_unattested_source_flag':r['unclear_or_unattested_flag']})
    (OWN/'claims.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    lines=['# Claim ledger','',f'{len(rows)} records. The PDF is unfoliated; page numbers refer to physical PDF leaves. Proposed interpretations are indexed for review. Source reading rows stay local.', '',
           'The 130 pre-PDF records remain represented. Table 18 image identities and paper locators have dated successors. Reading claims link to the local inventory by ID; the source classification is retained beside the paraphrase.', '',
           '| ID | Source location | Type | Paraphrase | Evidence / test |','|---|---|---|---|---|']
    for r in rows:
        cells=[r['id'],r['source_id']+' '+r['source_location'],r['type'],r['paraphrase'],r['offered_evidence']+' Tests: '+','.join(r['test_ids'])]
        lines.append('| '+' | '.join(s.replace('|','/').replace('\n',' ') for s in cells)+' |')
    (OWN/'claims.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(OUT/'ledger-changes.json',{'status':'Exploratory','original_records':len(original),'original_records_changed':len(changes),
        'changed_records':changes,'new_source_claims':countbefore-len(original),'new_reading_claims':len(rows)-countbefore,
        'total_records':len(rows),'basis':'Every inventory reading-attempt row receives a source-linked claim; standalone structural examples remain indexed separately.'})
    write(OWN/'ledger-coverage.json',{'status':'Exploratory','records':len(rows),'original_checked_rows':126,
        'new_PDF_source_claims':countbefore-len(original),'new_PDF_reading_claims':len(rows)-countbefore,
        'inventory_rows':len(readings),'attempt_rows':859,'limitations':'Unlabelled figures and background propositions outside the scoped ledger still require manual review. The source extraction count is not a historical attempt denominator.'})
    write(OUT/'concordance-v2.json',{'status':'Exploratory','mapping_sha256':sha(OUT/'mapping-v2-frozen.json'),
       'rows':[{**r,'source_catalogue_record':next(({'pdf_page':s['pdf_page'],'table_entry':s['table_entry']} for s in catalog if s['sign_id']==r['sign_id']),
           {'additional_catalogue_id':r['sign_id']})} for r in mapping['rows']],
       'source_catalogue':'Local sign-catalogue-v2.json and additional-valued-catalogue.json; first coding only.'})
    sources=read(OWN/'sources.json');b=next(s for s in sources['sources'] if s['id']=='B24')
    b['access']='Opened supplied public-page text and owner-supplied complete second-edition PDF; extracted all page/image placements and visually inspected Table 18, field inventories and sampled reading pages.'
    b['pdf_location']=PDFpath='data/raw/2026-10-08-bonta-review/papers/A_Partial_Decipherment_of_the_Indus_Vall.pdf'
    b['pdf_sha256']=sha(ROOT/PDFpath);b['pdf_opened']=True;b['pdf_access_date_local']='2026-10-09';b['pdf_page_count']=259
    b['citation_basis']='One-based PDF leaves; no printed folios. Segment index + 1; acquisition header and appended website content excluded.'
    b['same_edition_evidence']='pdf-2026-10-09-v1/witness-v3.json';b['redistribution']='Unresolved rights; PDF/text/images/crops stay local-only.'
    sources['pdf_followup']={'date':'2026-10-09','reused':['research/literature/2026-10-08-bonta-sign-inventory/inventory.json',
       'research/literature/2026-10-08-bonta-coverage-and-next-steps/assessment.json',
       'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json'],
       'new_downloads':0,'witness_source':'Owner-provided PDF; no new third-party download during this follow-up.',
       'reference_attribution':'Mayig MIT, Michael Carlson 2024; Helsinki chart CC BY 4.0, Koskenniemi and Parpola 1979; existing source URLs and pins are reused.'}
    write(OWN/'sources.json',sources)
    print(json.dumps(read(OUT/'ledger-changes.json')|{'changed_records':'omitted'},indent=2))

if __name__=='__main__':main()
