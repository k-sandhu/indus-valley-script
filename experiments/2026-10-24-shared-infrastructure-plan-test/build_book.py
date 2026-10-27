"""Local illustrated study, reusing the earlier book's typography and Markdown reader."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
from html import escape

from PIL import Image as PILImage
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Paragraph, PageBreak, Spacer, NextPageTemplate, Image
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle

P=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')
PRIOR=P.parent/'2026-10-24-urban-form-and-inscription-ecology/build_book.py'
spec=importlib.util.spec_from_file_location('prior_book_typography',PRIOR)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class StudyBook(base.Book):
    def __init__(self,path):
        super().__init__(path)
        self.title='Shared infrastructure: excavation plans and dated contexts'
        self.author='Indus research project; AI-assisted exploratory source study'

    def page(self,canvas,doc):
        w,h=doc.pageTemplate.pagesize or doc.pagesize
        canvas.saveState()
        canvas.setStrokeColor(base.LINE);canvas.setLineWidth(.5)
        canvas.line(36,h-27,w-36,h-27)
        canvas.setFont('Body',7);canvas.setFillColor(base.MUTED)
        canvas.drawString(38,h-20,'SHARED INFRASTRUCTURE / EXCAVATION-PLAN TEST / 24 OCTOBER 2026')
        canvas.drawRightString(w-38,17,str(doc.page))
        canvas.restoreState()


def main(figures,out,tag):
    if out.exists() or (P/f'book-manifest-{tag}.json').exists():
        raise FileExistsError('Preserve each book endpoint.')
    assert out.resolve().is_relative_to(RAW.resolve())
    out.parent.mkdir(parents=True,exist_ok=False)
    base.setup_fonts()
    styles=base.STYLES
    for style in styles.values():
        style.allowWidows=0
        style.allowOrphans=0
    figure_data=json.loads(figures.read_text(encoding='utf-8'))
    records=figure_data['figures']
    chapters=[('REPORT.md','What the excavation evidence tests'),
              ('RESULTS.md','Measurements and context joins'),
              ('MEASUREMENT-RULES.md','How the measurements are read'),
              ('TEST-DESIGN.md','Deciding between explanations'),
              ('SOURCES.md','Sources and exact locators')]
    inputs=[P/name for name,_ in chapters]+[P/'DECISION.md',figures,Path(__file__),PRIOR]
    archive=out.parent/'authored-inputs';archive.mkdir()
    for path in inputs:
        shutil.copyfile(path,archive/('prior-'+path.name if path==PRIOR else path.name))
    story=[Spacer(1,60),Paragraph('Shared infrastructure',styles['cover']),
           Paragraph('Excavation plans, rebuilding<br/>and dated documentary contexts',styles['subtitle']),
           Spacer(1,15),Paragraph('An exploratory test of the common-rules idea<br/>24 October 2026',styles['body']),
           Spacer(1,26),Paragraph('We follow named streets, walls, drains and entrances through reported building episodes, then ask whether seals and tablets can be joined to the same activities and dates.',styles['body']),
           Paragraph('This local edition includes attributed excavation-plan crops and detailed source annotations. Acquired sources retain their own rights. Raw inputs and large products remain on D:.',styles['small']),
           PageBreak(),base.heading('Contents',0,False)]
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('study-toc',fontName='BodyBold',fontSize=10.5,leading=17,spaceBefore=9,textColor=base.INK)]
    story += [toc,PageBreak()]
    for index,(name,title) in enumerate(chapters):
        if index:story.append(PageBreak())
        source=P/name
        if re.search(r'^\d+\. ',source.read_text(encoding='utf8'),re.M):
            # The inherited Markdown reader treats separated numeric steps as
            # paragraphs. Add reading whitespace without changing the source.
            rendered_source=archive/(source.stem+'-reading-copy.md')
            rendered_source.write_text(re.sub(r'\n(?=\d+\. )','\n\n',source.read_text(encoding='utf8')),encoding='utf8')
            inputs.append(rendered_source)
            source=rendered_source
        story.extend(base.markdown(source,chapter_title=title,bibliography=(name=='SOURCES.md')))
    story += [PageBreak(),base.heading('Maps and evidence atlas',0,True),
              Paragraph(f"{len(records)} figures show the original plan evidence, measurements, context chains, dating problems and deciding contrasts. The companion manifest gives source IDs, exact locators and asset hashes.",styles['body']),
              Paragraph('Source geometry and our annotations remain distinguishable. Unknown areas stay unknown. A conceptual diagram has no archaeological scale; an attributed plan retains the north and scale information described in its caption.',styles['body'])]
    for f in records:
        path=Path(f['physical_path'])
        assert sha(path)==f['sha256']
        inputs.append(path)
        story += [NextPageTemplate('wide'),PageBreak()]
        caption=Paragraph('<b>Figure '+str(f['figure'])+'. '+escape(f['title'])+'.</b> '+base.markup(f['caption']),styles['caption'])
        note=Paragraph(escape(f.get('source_note','')),styles['small'])
        width=landscape(A4)[0]-84
        caph=caption.wrap(width,1000)[1];noteh=note.wrap(width,1000)[1]
        height=landscape(A4)[1]-84-caph-noteh-10
        with PILImage.open(path) as image:w,h=image.size
        scale=min(width/w,height/h)
        story += [Image(str(path),width=w*scale,height=h*scale,hAlign='CENTER'),Spacer(1,6),caption,note]
    story += [NextPageTemplate('portrait'),PageBreak()]
    story.extend(base.markdown(P/'DECISION.md',chapter_title='The strongest reading and the deciding test'))
    StudyBook(out).multiBuild(story)
    reader=PdfReader(out)
    manifest={'output_physical_path':str(out),'output_logical_path':'data/raw/2026-10-24-shared-infrastructure-plan-test/'+out.relative_to(RAW).as_posix(),
              'sha256':sha(out),'bytes':out.stat().st_size,'pages':len(reader.pages),'figure_count':len(records),
              'source_figures_included':True,'local_only':True,'scientific_confirmation':False,
              'input_manifest':[{'path':str(path),'sha256':sha(path)} for path in inputs],
              'archived_authored_inputs':str(archive),'typography_reuse':str(PRIOR),'code_sha256':sha(Path(__file__))}
    (P/f'book-manifest-{tag}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ['output_physical_path','pages','figure_count','sha256','bytes']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--figures',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--tag',required=True)
    args=parser.parse_args()
    main(args.figures,args.out,args.tag)
