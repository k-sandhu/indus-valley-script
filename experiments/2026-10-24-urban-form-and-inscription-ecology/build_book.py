"""Create the local study book from authored prose and validated source-linked figures."""
from pathlib import Path
from datetime import date
from html import escape
import argparse
import hashlib
import json
import re
import shutil

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                               PageBreak, NextPageTemplate, Image, LongTable, TableStyle,
                               KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

P=Path(__file__).resolve().parent
LOCAL=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology')
FONT=Path('C:/Users/sandh/AppData/Roaming/Python/Python313/site-packages/matplotlib/mpl-data/fonts/ttf')
INK=colors.HexColor('#182C30'); TEAL=colors.HexColor('#207D80'); MUTED=colors.HexColor('#56676A')
CREAM=colors.HexColor('#F7F4ED'); LINE=colors.HexColor('#D9DCD5')
STYLES={}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def actual(value): return Path(value.replace('\\\\','\\'))

def setup_fonts():
    for alias,file in [('Body','DejaVuSans.ttf'),('BodyBold','DejaVuSans-Bold.ttf'),('BodyItalic','DejaVuSans-Oblique.ttf'),('Mono','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(alias,str(FONT/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    STYLES.update({
      'body':ParagraphStyle('body',fontName='Body',fontSize=9.2,leading=14,spaceAfter=6,textColor=INK,splitLongWords=True),
      'bullet':ParagraphStyle('bullet',fontName='Body',fontSize=9.0,leading=13.3,leftIndent=11,firstLineIndent=-8,spaceAfter=4,textColor=INK,splitLongWords=True),
      'subbullet':ParagraphStyle('subbullet',fontName='Body',fontSize=8.3,leading=12,leftIndent=18,spaceAfter=4,textColor=MUTED,splitLongWords=True),
      'h1':ParagraphStyle('h1',fontName='BodyBold',fontSize=22,leading=28,spaceBefore=6,spaceAfter=18,textColor=INK,keepWithNext=True),
      'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=13,leading=18,spaceBefore=14,spaceAfter=8,textColor=TEAL,keepWithNext=True),
      'h3':ParagraphStyle('h3',fontName='BodyBold',fontSize=10.2,leading=15,spaceBefore=10,spaceAfter=5,textColor=INK,keepWithNext=True),
      'small':ParagraphStyle('small',fontName='Body',fontSize=7.5,leading=10.5,spaceAfter=5,textColor=MUTED,splitLongWords=True),
      'caption':ParagraphStyle('caption',fontName='Body',fontSize=8.4,leading=11.8,spaceAfter=5,textColor=INK,splitLongWords=True),
      'table':ParagraphStyle('table',fontName='Body',fontSize=8,leading=11.5,spaceAfter=0,textColor=INK,splitLongWords=True),
      'tablehead':ParagraphStyle('tablehead',fontName='BodyBold',fontSize=8,leading=11.5,spaceAfter=0,textColor=colors.white,splitLongWords=True),
      'cover':ParagraphStyle('cover',fontName='BodyBold',fontSize=35,leading=43,spaceAfter=20,textColor=INK),
      'subtitle':ParagraphStyle('subtitle',fontName='Body',fontSize=15,leading=23,spaceAfter=20,textColor=TEAL),
    })

def markup(text):
    links=[]
    def hide(m):
        token=f'LINKTOKEN{len(links)}END'
        url=m.group(2)
        if url.startswith('http'):
            links.append('<link href="'+escape(url,quote=True)+'" color="#207D80">'+escape(re.sub(r'[*`]','',m.group(1)))+'</link>')
        else:
            links.append(escape(m.group(1))+' <font color="#56676A">('+escape(url)+')</font>')
        return token
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',hide,text)
    text=escape(text)
    text=re.sub(r'`([^`]+)`',lambda m:'<font name="Mono" size="7.6">'+m.group(1)+'</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',text)
    for i,link in enumerate(links):text=text.replace(f'LINKTOKEN{i}END',link)
    return text

class Book(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=46,bottomMargin=42,
                         title='Indus towns: construction histories and documentary practice',author='Indus research project; AI-assisted source review',
                         pageCompression=1,allowSplitting=1)
        portrait=Frame(44,42,A4[0]-88,A4[1]-88,id='portrait-frame')
        ls=landscape(A4)
        wide=Frame(36,32,ls[0]-72,ls[1]-64,id='wide-frame')
        self.addPageTemplates([PageTemplate(id='portrait',frames=[portrait],pagesize=A4,onPage=self.page),
                               PageTemplate(id='wide',frames=[wide],pagesize=ls,onPage=self.page)])
        self.heading_counter=0
    def page(self,canvas,doc):
        w,h=doc.pageTemplate.pagesize or doc.pagesize
        canvas.saveState();canvas.setStrokeColor(LINE);canvas.setLineWidth(.5)
        canvas.line(36,h-27,w-36,h-27)
        canvas.setFont('Body',7);canvas.setFillColor(MUTED)
        canvas.drawString(38,h-20,'INDUS TOWNS / SOURCE REVIEW / 24 OCTOBER 2026')
        canvas.drawRightString(w-38,17,str(doc.page))
        canvas.restoreState()
    def beforeDocument(self):
        self.heading_counter=0
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and hasattr(flowable,'book_heading'):
            level,label,toc=flowable.book_heading
            self.heading_counter+=1
            key='heading-'+str(self.heading_counter)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(label,key,level=level,closed=True)
            if toc:self.notify('TOCEntry',(level,label,self.page,key))

def heading(text,level=0,toc=True):
    obj=Paragraph(markup(text),STYLES[['h1','h2','h3'][min(level,2)]])
    obj.book_heading=(level,re.sub(r'[*`]','',text),toc)
    return obj

def markdown(path,chapter_title=None,town_breaks=False,bibliography=False):
    lines=path.read_text(encoding='utf-8').splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('# '):
            story.append(heading(chapter_title or line[2:],0,True));i+=1;continue
        if line.startswith('## '):
            if town_breaks:story.append(PageBreak())
            story.append(heading(line[3:],1,town_breaks));i+=1;continue
        if line.startswith('### '):
            story.append(heading(line[4:],2,False));i+=1;continue
        if line.startswith('|'):
            table=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c.replace(' ','')) for c in cells):table.append(cells)
                i+=1
            width=A4[0]-100
            cols=len(table[0]); colwidths=[width/cols]*cols
            if cols==3:colwidths=[width*.28,width*.35,width*.37]
            content=[[Paragraph(markup(c),STYLES['tablehead' if r==0 else 'table']) for c in row] for r,row in enumerate(table)]
            t=LongTable(content,colWidths=colwidths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),
                                   ('GRID',(0,0),(-1,-1),.4,LINE),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                                   ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.extend([t,Spacer(1,9)]);continue
        if line.startswith('- '):
            story.append(Paragraph('&#8226; '+markup(line[2:]),STYLES['bullet']));i+=1;continue
        if line.startswith('  '):
            story.append(Paragraph(markup(line.strip()),STYLES['subbullet']));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ','  ')):
            paragraph.append(lines[i]);i+=1
        text=' '.join(paragraph)
        style='small' if bibliography and (text.startswith('SHA-256') or text.startswith('Rights:') or text.startswith('Read scope:')) else 'body'
        story.append(Paragraph(markup(text),STYLES[style]))
    return story

def main(out,fig_manifest,tag):
    if out.exists():raise FileExistsError(out)
    if not out.resolve().is_relative_to(LOCAL):raise ValueError('Output must stay in local D: package')
    out.parent.mkdir(parents=True,exist_ok=True)
    setup_fonts()
    figures=json.loads(fig_manifest.read_text(encoding='utf-8'))
    assert figures['figure_count']==23
    inputs=[P/f for f in ['REPORT.md','METHODS.md','COMPARISON.md','TEST-DESIGN.md','SOURCES.md']]+[fig_manifest]
    archived=out.parent/'authored-inputs'
    archived.mkdir()
    for source in inputs:
        shutil.copyfile(source,archived/source.name)
    shutil.copyfile(Path(__file__),archived/'build_book.py')
    story=[Spacer(1,65),Paragraph('Indus towns',STYLES['cover']),
           Paragraph('Construction histories<br/>and documentary practice',STYLES['subtitle']),Spacer(1,15),
           Paragraph('Twelve towns. 287 source-qualified assertions.<br/>Twenty-three source-linked graphics.',STYLES['subtitle']),
           Spacer(1,40),Paragraph('A comparative source review and exploratory research programme',STYLES['body']),
           Paragraph('24 October 2026<br/>Indus research knowledge base',STYLES['body']),Spacer(1,22),
           Paragraph('The study compares reported architecture and building episodes. Counts retain their excavation scope. Proposed institutional readings have explicit credences and deciding tests. Raw sources and all large products remain local on D:.',STYLES['body']),PageBreak(),
           heading('Contents',0,False)]
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('toc0',fontName='BodyBold',fontSize=10.5,leading=17,leftIndent=0,firstLineIndent=0,spaceBefore=8,textColor=INK),
                     ParagraphStyle('toc1',fontName='Body',fontSize=9,leading=14,leftIndent=14,firstLineIndent=0,spaceBefore=3,textColor=MUTED)]
    story += [toc,PageBreak()]
    chapters=[('REPORT.md','Findings and interpretation',False,False),('METHODS.md','Methods and competing explanations',False,False),
              ('COMPARISON.md','Twelve source-backed town profiles',True,False),('TEST-DESIGN.md','The deciding study',False,False),
              ('SOURCES.md','Source-use bibliography',False,True)]
    for index,(filename,title,town_breaks,bibliography) in enumerate(chapters):
        if index:story.append(PageBreak())
        story.extend(markdown(P/filename,chapter_title=title,town_breaks=town_breaks,bibliography=bibliography))
    story += [PageBreak(),heading('Graphic atlas',0,True),Paragraph('Each figure preserves its source IDs and exact locators in the companion manifest. Source-backed graphics, conceptual diagrams and synthetic demonstrations carry their scope in their captions. The PNG and SVG originals remain available separately at full resolution.',STYLES['body']),
              Paragraph('Core data: run-v3. The source index records evidence and limits together; it does not score completeness or planning. No acquired plan or photograph is reproduced.',STYLES['body'])]
    for figure in figures['figures']:
        story += [NextPageTemplate('wide'),PageBreak()]
        asset=next(a for a in figure['assets'] if a['format']=='png')
        path=actual(asset['physical_path'])
        assert sha(path)==asset['sha256']
        inputs.append(path)
        caption=Paragraph(f"<b>Figure {figure['figure']}. {escape(figure['title'])}.</b> "+markup(figure['caption']),STYLES['caption'])
        source_text='; '.join(str(s.get('source_id',''))+': '+str(s.get('locator','')) for s in figure.get('sources',[]))
        if figure.get('observation_ids'):source_text+=' | Assertions: '+', '.join(figure['observation_ids'])
        source_note=Paragraph(escape(source_text),STYLES['small'])
        width=landscape(A4)[0]-84
        caph=caption.wrap(width,1000)[1]; noteh=source_note.wrap(width,1000)[1]
        available=landscape(A4)[1]-82-caph-noteh-10
        with PILImage.open(path) as image:w,h=image.size
        scale=min(width/w,available/h)
        image=Image(str(path),width=w*scale,height=h*scale,hAlign='CENTER')
        story += [image,Spacer(1,6),caption,source_note]
    story += [NextPageTemplate('portrait'),PageBreak(),heading('The reading and the deciding test',0,True),
              Paragraph('<b>Indus urbanism preserved shared frameworks while repeatedly changing the buildings and activities connected to them.</b> Earlier occupation could precede enclosure or clearance, and established layouts could accommodate later additions. These ordered relations are the strongest common result across the source histories.',STYLES['body']),
              Paragraph('The deciding test surveys the same named routes, entrances and adjacent structures through independently dated building episodes, then joins primary documentary contexts to those episodes. Architectural coding remains blind to inscriptions and sealing occurrence. Object and manufacturing groups remain separate from context labels.',STYLES['body']),
              Paragraph('A frozen comparison then asks whether access changes predict documentary operations beyond production, household activity, engineering and recovery effects. Preferential route continuity can support common rules. A claim about negotiation requires a contrast with supervision. A labour-obligation reading requires evidence that distinguishes it from ordinary goods allocation.',STYLES['body']),
              Paragraph('New primary contexts and adequate sensitivity can decide the proposed extension. A persistent absence of the predicted relation, or a complete explanation through secondary manufacture debris and recovery, defeats it.',STYLES['body'])]
    doc=Book(out);doc.multiBuild(story)
    reader=PdfReader(out)
    manifest=dict(output_physical_path=str(out),output_logical_path='data/raw/2026-10-24-urban-form-and-inscription-ecology/'+out.relative_to(LOCAL).as_posix(),
                  sha256=sha(out),bytes=out.stat().st_size,pages=len(reader.pages),figure_count=23,
                  word_counts={f:len((P/f).read_text(encoding='utf-8').split()) for f,_,_,_ in chapters},
                  input_manifest=[dict(path=str(p),sha256=sha(p)) for p in inputs],code_sha256=sha(Path(__file__)),
                  rights='Project-authored prose, source-linked summaries and charts. No acquired source image or plan embedded. Sources retain their own terms.',
                  archived_authored_inputs=str(archived),
                  source_data_endpoint='run-v3',scientific_confirmation=False)
    (P/f'book-manifest-{tag}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ['output_physical_path','sha256','bytes','pages','figure_count']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path);parser.add_argument('--figures',required=True,type=Path);parser.add_argument('--tag',required=True)
    args=parser.parse_args();main(args.out,args.figures,args.tag)
