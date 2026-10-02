"""Local searchable primary chart with preserved numeric ambiguity and source context."""
from pathlib import Path
import json,fitz,html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/chart_atlas'

def main():
    OUT.mkdir(exist_ok=True);(OUT/'cells').mkdir(exist_ok=True)
    labels=json.loads((ROOT/'research/chart_reference/manual_numeric_reference.json').read_text())
    a=json.loads((ROOT/'research/corpus/primary/chart_complete/column0_reinspection.json').read_text())
    b=json.loads((ROOT/'research/corpus/primary/chart_complete/manual_columns1_4.json').read_text())
    boxes={(20,0,r['row_0based']):r['source_cell_pdf_points'] for r in a['rows']}
    boxes.update({(20,c['col_0based'],r['row_0based']):r['source_cell_pdf_points'] for c in b['columns'] for r in c['rows']})
    for file in ['manual_numeric_labels.json','full21_audit.json']:
        for r in json.loads((ROOT/'research/literature/chart_complete'/file).read_text())['rows']:
            boxes[r['pdf_page'],r['column_0based'],r['row_0based']]=r['cell_clip_points']
    pdf=fitz.open(ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf')
    rows=[]
    for r in labels['rows']:
        p,c,i=r['pdf_page'],r['column'],r['row'];box=boxes[p,c,i]
        # Retain original context rather than pretending the crop adjudicates ink boundaries.
        clip=fitz.Rect(box[0]-2,box[1]-4,box[2]+2,box[3]+2)
        name=f'p{p}_c{c}_r{i}.png';pdf[p-1].get_pixmap(matrix=fitz.Matrix(4,4),clip=clip).save(OUT/'cells'/name)
        rows.append(dict(r,image=f'cells/{name}',source_crop_pdf_points=list(clip)))
    (OUT/'reference.json').write_text(json.dumps(dict(labels,rows=rows),indent=2),encoding='utf-8')
    data=json.dumps(rows,ensure_ascii=False).replace('</','<\\/')
    template='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>1979 Indus chart: numeric reference</title>
<style>body{margin:0;font:16px/1.5 system-ui;color:#263744;background:#f5f7f8}header,main{max-width:1240px;margin:auto;padding:24px}header{background:white}h1{font-size:30px;line-height:1.2;margin:0 0 14px;color:#24486c}p{max-width:950px}a{color:#24486c}.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:center}input,select{font:inherit;padding:8px;border:1px solid #a0afb8;border-radius:4px}#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}.card{background:white;border:1px solid #d8e1e6;border-radius:5px;padding:12px}.card.ambiguous{border-color:#be855c}.card img{display:block;width:100%;height:130px;object-fit:contain;background:white}.code{font-size:19px;font-weight:650}.meta{font-size:13px;color:#536675}.badge{color:#8b4b2d}footer{max-width:1240px;margin:20px auto;padding:24px;font-size:13px}</style>
<header><h1>1979 Indus chart: numeric reference</h1><p>687 source cells from Koskenniemi and Parpola's <em>Corpus of Texts in the Indus Script</em>. Upper numbers are ranks; lower numbers are stable Finnish codes. These identify drawings, not sounds or meanings. __AMBIGUOUS__ numeric readings retain alternatives.</p><p>AI visual readings and enlarged source checks; no expert certification. Context crops can contain neighbouring ink. Dashed glyph underlines and damage graphics are editorial annotations. A matching image or numeric code does not certify an original inscription's segmentation.</p><div class="controls"><label>Search code or rank <input id="query" placeholder="e.g. 436" aria-label="Search code or rank"></label><label><input type="checkbox" id="amb"> Ambiguous numeric readings only</label><label>Page <select id="page"><option value="">Both</option><option>20</option><option>21</option></select></label><span id="count"></span></div></header><main><div id="grid"></div></main>
<footer>Source: Kimmo Koskenniemi and Asko Parpola (1979), <a href="https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/">official University of Helsinki repository</a>, CC BY 4.0. Cropped source images, numeric readings and uncertainty metadata are attributed adaptations. Original PDF SHA-256: 7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27. <a href="reference.json">Machine-readable reference</a>. No entire inscription corpus or decipherment is supplied.</footer>
<script>
const rows=__DATA__;
const q=document.querySelector('#query'),a=document.querySelector('#amb'),p=document.querySelector('#page');
const uncertain=r=>r.alternatives.length||r.rank_alternatives.length;
function update(){
 const value=q.value.trim();
 const selected=rows.filter(r=>(!value||[r.rank,...r.rank_alternatives,r.code,...r.alternatives].some(x=>String(x).includes(value)))&&(!a.checked||uncertain(r))&&(!p.value||r.pdf_page===Number(p.value)));
 document.querySelector('#count').textContent=selected.length+' cells';
 document.querySelector('#grid').innerHTML=selected.map(r=>`<article class="card ${uncertain(r)?'ambiguous':''}"><div class="code">Code ${r.code}${r.alternatives.length?' / '+r.alternatives.join(' / '):''}</div><div class="meta">Rank ${r.rank}${r.rank_alternatives.length?' / '+r.rank_alternatives.join(' / '):''} · PDF ${r.pdf_page} · column ${r.column} · row ${r.row}</div><img loading="lazy" src="${r.image}" alt="Original chart context for rank ${r.rank}"><div class="meta ${uncertain(r)?'badge':''}">${uncertain(r)?'Numeric alternatives retained':'Qualitative numeric reading'} · ${r.numeric_confidence}</div></article>`).join('');
}
[q,a,p].forEach(x=>x.addEventListener('input',update));update();
</script></html>'''
    (OUT/'index.html').write_text(template.replace('__DATA__',data).replace('__AMBIGUOUS__',str(labels['numeric_ambiguous_cells'])),encoding='utf-8')
    print(json.dumps({'cells':len(rows),'path':'output/chart_atlas/index.html'}))
if __name__=='__main__':main()
