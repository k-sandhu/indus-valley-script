"""Render bounded primary table/figure witnesses locally; no source image is tracked."""
from pathlib import Path
import hashlib,json
import fitz
HERE=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/contexts')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sources={r['source_id']:r for r in json.loads((HERE/'sources.json').read_text(encoding='utf8'))['sources']}
    specs=[
      ('FAR-TABLE','EAST-SHINDE2011',384,371,(.08,.06,.92,.93),'Farmana: seals and impressed clay objects',
       'Tables7.2–7.3 identify four steatite seals and two terracotta objects. Publication object types and phase assignments require separate formation assessments.','FAR-S1–S6'),
      ('FAR-PHASEMAP','EAST-SHINDE2011',397,384,(.04,.06,.96,.93),'Farmana: findspot figure',
       'Figure7.18 provides bounded trench/area anchors. Leader lines are not an exact object-to-operating-floor crosswalk.','FAR-S1–S6'),
      ('FAR-GUPTA-MATERIAL','EAST-SHINDE2011',845,832,None,'Farmana: sample08-001 / Structure3N',
       'Table13.1 gives PLD-12422 as carbonized wood from Tr.1E1/St.no.3N. The material/locus row must be read with its Gupta-age result on p.834.','FAR-ST3N-DATE'),
      ('FAR-GUPTA-RESULT','EAST-SHINDE2011',847,834,(.10,.07,.90,.57),'Farmana: later dates in the site table',
       'Table13.2 rows17–26. PLD-12422 is1390±20BP, AD616–666 at95.4%. A structure label does not date its Harappan construction.','FAR-ST3N-DATE'),
      ('HAR-WORKSHOP-PLAN','KENOYER2005',7,'Figure2',(0,.02,1,.98),'Harappa: Trench54 workshop area',
       'Figure2 labels workshop[601] within a surveyed area. The mapped manufacturing fill supports a bounded craft area; individual Fig.3 tablets have no plotted registration points.','HAR-TR54-MANUFACTURE'),
      ('HAR-WORKSHOP-TABLETS-A','KENOYER2005',8,'Figure3',(0,.02,1,.98),'Harappa: manufacturing-set registrations, part1',
       'Figure3 lists incised and moulded tablets and blanks from the workshop area. Manufacture, final use and deposition are separate stages in the assessment.','HAR-TR54-MANUFACTURE'),
      ('HAR-WORKSHOP-TABLETS-B','KENOYER2005',9,'Figure3 continuation / Figure4',(0,.01,1,.98),'Harappa: manufacturing-set boundary',
       'Figure3 continues through no.15. Figure4 is a separate list; its downslope tablet H2000-4483/2342-01 is excluded from the bounded15-unit illustration cohort.','HAR-TR54-MANUFACTURE;HAR-TR54-DOWNSLOPE'),
      ('HAR-FLOOR-SEALS','MK1997',15,154,(.10,.04,.94,.98),'Harappa: seal registrations and loci',
       'Figure7.4 H95-2598 is floor deposits;7.6 H95-2491 is floor/fill;7.5 H95-2419 is fill. The caption preserves the distinction needed to audit prose references to a courtyard floor.','HAR-TR10E-ROOM;HAR-TR10E-COURTYARD;HAR-TR10E-UPPERFILL'),
      ('HAR-SUMP-JAR','MK1997',22,161,(.10,.04,.92,.98),'Harappa: installed inscribed sump jar',
       'Figure12.2 and caption identify H95-2661/6640-501 as sunk into a Trench9 floor. This anchors final reuse, while earlier incisions can predate installation.','HAR-TR9-SUMP'),
      ('HAR-SECONDARY-CLUMP','MK2000',7,7,(.02,.02,.98,.98),'Harappa: Wall296 tablet-clump plan',
       'Figure2 plots the clump near Wall296 and other approximate finds. The source interprets a secondary dump deposited after wall construction.','HAR-W296-22'),
      ('LOT-ROW-TABLE-A','FT2005',30,93,(.08,.04,.94,.96),'Lothal: provenance rowsL124–L170',
       'Table1 first page. The local manual provenance transcription is retained for an independent recount; W1 is inferred from stamp identity.','LOT-WAREHOUSE-COHORT;LOT-W1-INFERRED'),
      ('LOT-ROW-TABLE-B','FT2005',31,94,(.08,.04,.94,.96),'Lothal: provenance rowsL171–L216',
       'Table1 second page. The two pages yield W35,W1=18,W2=11,O10,?19 in this transcription; prose gives O11/?17. No silent correction is made.','LOT-WAREHOUSE-COHORT'),
      ('LOT-PROSE-DENOMINATORS','FT2005',8,71,(.10,.50,.92,.83),'Lothal: stated precise-provenance denominator',
       'The bounded paragraph states35warehouse and11outside,46precise of93. Compare both original Table1 pages; this is an audit witness, not a settlement-frequency graphic.','LOT-WAREHOUSE-COHORT'),
      ('LOT-CLOSURE-RECONSTRUCTION','FT2005',35,98,(.05,.05,.96,.95),'Lothal: reverse-contact closure models',
       'Figure3 includes L206. Contact geometry can support a fastening model while leaving original application location and custody change unobserved.','LOT-L206'),
      ('LOT-DEPOSIT-PLAN','FT2005',34,97,(.04,.04,.97,.97),'Lothal: source site and warehouse-context figure',
       'Figure2 source panel; passage/block labels can anchor a bounded deposit area. It does not supply an original application point for every sealing.','LOT-WAREHOUSE-COHORT'),
      ('KAN-RICE-COUNTEREXAMPLE','POKHARIA2011',3,1836,None,'Kanmer: direct dates defeat grain phase labels',
       'The Oryza paragraph reports PLD-16351/16353 at fourth–fifth-century AD ages in Mature/Late assemblages and proposes reworking/percolation. The raw determinations are not supplied in this paragraph.','KAN-RICE-INTRUSION'),
      ('KAN-AMS-TABLE','POKHARIA2011',4,1837,(.04,.06,.97,.76),'Kanmer: sample-by-sample AMS table',
       'Table2 retains16lab IDs and grid/layer/depth. These provenance labels do not independently join a named seal to a construction episode.','KAN-3IMP'),
    ]
    assets=[]
    for id,sid,idx,printed,frac,title,caption,join in specs:
        source=sources[sid]
        with fitz.open(source['physical_path']) as doc:
            page=doc[idx];bounds=page.rect
            if id=='FAR-GUPTA-MATERIAL':
                nextrow=page.search_for('PLD-12423')[0]
                clip=fitz.Rect(.08*bounds.width,.04*bounds.height,.92*bounds.width,nextrow.y0)
            elif id=='KAN-RICE-COUNTEREXAMPLE':
                begin=page.search_for('Oryza sativa')[0]
                end=page.search_for('Measurements:')[0]
                # The paragraph is in the left column, above its measurements.
                clip=fitz.Rect(begin.x0-3,begin.y0-3,bounds.width*.51,end.y0+2)
            elif id=='LOT-PROSE-DENOMINATORS':
                begin=page.search_for('The sealings discovered')[0]
                ending=page.search_for('It is indeed possible')[0]
                clip=fitz.Rect(.10*bounds.width,begin.y0-3,.92*bounds.width,ending.y0-2)
            else:clip=fitz.Rect(frac[0]*bounds.width,frac[1]*bounds.height,frac[2]*bounds.width,frac[3]*bounds.height)
            out=RAW/(id.lower()+'.png')
            page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,alpha=False).save(out)
            assets.append({'id':id,'physical_path':str(out),'logical_path':'data/raw/2026-10-24-shared-infrastructure-plan-test/contexts/'+out.name,
              'sha256':sha(out),'title':title,'caption':caption,'context_assessment_ids':join,
              'source_id':sid,'source_title':source['title'],'source_url':source['url'],'source_sha256':source['sha256'],
              'locator':{'printed_page':printed,'pdf_index':idx,'pdf_page':idx+1,'crop_points':list(clip)},
              'local_only':True,'rights_status':source['rights_status'],'kind':'original-publication crop; no archaeological reconstruction',
              'visual_review':'pending'})
    write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    write(HERE/'visual-assets.json',{'assets':assets,'purpose':'Bounded source witnesses for auditing joins. All pixels stay onD; none is a decorative reconstruction.'})
    print(len(assets),'source witnesses rendered')
if __name__=='__main__':main()
