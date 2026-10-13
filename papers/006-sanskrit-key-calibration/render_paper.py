"""Render Paper 006 as a printable, linked PDF.

Adapted from the settlement paper renderer (experiments/2026-10-11-settlement-prospection/render_paper.py).
SVG figures are replaced by PNG rasters of the same name from --figure-cache, produced by
make_figures.py with PREVIEW set to that directory.
"""
from pathlib import Path
import argparse, re, html, json, hashlib
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT

INK=colors.HexColor('#243237');TEAL=colors.HexColor('#086b66');GRAY=colors.HexColor('#657478')

def fonts():
    for label,file in [('Georgia','georgia.ttf'),('Georgia-Bold','georgiab.ttf'),('Georgia-Italic','georgiai.ttf'),('Georgia-BoldItalic','georgiaz.ttf')]:
        path=Path('C:/Windows/Fonts')/file
        if not path.exists():raise FileNotFoundError('Required printable font: '+str(path))
        pdfmetrics.registerFont(TTFont(label,str(path)))
    pdfmetrics.registerFontFamily('Georgia',normal='Georgia',bold='Georgia-Bold',italic='Georgia-Italic',boldItalic='Georgia-BoldItalic')

def rich(s):
    # ASCII hyphens in print; source titles remain exact in Markdown/registers.
    s=s.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    parts=[];cursor=0
    # DOI targets may contain a balanced parenthesized year. Consume that group
    # inside the target rather than displaying its suffix as manuscript text.
    for m in re.finditer(r'\[([^\]]+)\]\(((?:[^()]|\([^()]*\))*)\)',s):
        parts.append(html.escape(s[cursor:m.start()]))
        label,url=m.groups()
        if url.startswith('http'):
            parts.append('<a href="'+html.escape(url,quote=True)+'" color="#086b66">'+html.escape(label)+'</a>')
        else:parts.append(html.escape(label))
        cursor=m.end()
    parts.append(html.escape(s[cursor:]));s=''.join(parts)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'<font size="8.5">\1</font>',s)
    return s

class PaperDoc(BaseDocTemplate):
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and getattr(flowable,'toc_level',None) is not None:
            level=flowable.toc_level;text=flowable.getPlainText();key='s'+hashlib.sha256(text.encode('utf-8')).hexdigest()[:18]
            self.canv.bookmarkPage(key)
            self.notify('TOCEntry',(level,text,self.page,key))

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--figure-cache',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('PDF exists; use a new versioned output path.')
    fonts();a.output.parent.mkdir(parents=True,exist_ok=True)
    width,height=letter;left=54;right=54;top=50;bottom=50;usable=width-left-right
    styles={
      'body':ParagraphStyle('body',fontName='Georgia',fontSize=10.4,leading=14.7,textColor=INK,spaceAfter=8,allowWidows=0,allowOrphans=0),
      'title':ParagraphStyle('title',fontName='Georgia-Bold',fontSize=22,leading=28,textColor=TEAL,spaceAfter=18),
      'h1':ParagraphStyle('h1',fontName='Georgia-Bold',fontSize=15,leading=19,textColor=TEAL,spaceBefore=15,spaceAfter=9,keepWithNext=True),
      'h2':ParagraphStyle('h2',fontName='Georgia-Bold',fontSize=11.6,leading=15,textColor=INK,spaceBefore=10,spaceAfter=7,keepWithNext=True),
      'small':ParagraphStyle('small',fontName='Georgia',fontSize=8.6,leading=11.8,textColor=GRAY,spaceAfter=9),
      'table':ParagraphStyle('table',fontName='Georgia',fontSize=8.5,leading=11.4,textColor=INK,spaceAfter=0),
      'tablehead':ParagraphStyle('tablehead',fontName='Georgia-Bold',fontSize=8.5,leading=11.4,textColor=colors.white),
    }
    page_meta=[]
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#cfdbd8'));canvas.line(left,35,width-right,35)
        canvas.setFillColor(GRAY);canvas.setFont('Georgia',8)
        canvas.drawString(left,23,'Indus script research | reviewed working paper | 12 October 2026')
        canvas.drawRightString(width-right,23,str(doc.page))
        if doc.page>1:
            canvas.setFont('Georgia',7.7);canvas.drawString(left,height-25,'Testing a published Sanskrit key against its own rearrangements')
        page_meta.append(doc.page);canvas.restoreState()
    doc=PaperDoc(str(a.output),pagesize=letter,leftMargin=left,rightMargin=right,topMargin=top,bottomMargin=bottom,
                 title='Testing a published Sanskrit key for the Indus script against its own rearrangements',author='Indus research project; AI-assisted working paper')
    doc.addPageTemplates(PageTemplate(id='paper',frames=[Frame(left,bottom,usable,height-top-bottom,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer))
    lines=a.input.read_text(encoding='utf-8').splitlines();story=[];i=0;first_h1=True
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('# '):
            story.append(Paragraph(rich(line[2:]),styles['title']));i+=1;continue
        if line.startswith('## '):
            text=line[3:]
            if first_h1:
                # Put abstract on first page, contents immediately afterwards.
                first_h1=False
            if text.startswith('1.'):
                story.append(PageBreak());story.append(Paragraph('Contents',styles['h1']))
                toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Georgia',fontSize=9.5,leading=14.3,textColor=INK,leftIndent=0,firstLineIndent=0,spaceBefore=4)]
                story.append(toc);story.append(PageBreak())
            if text.startswith('Appendix') or text.startswith('References'):story.append(PageBreak())
            para=Paragraph(rich(text),styles['h1'])
            if text!='Abstract':para.toc_level=0
            story.append(para);i+=1;continue
        if line.startswith('### '):
            story.append(Paragraph(rich(line[4:]),styles['h2']));i+=1;continue
        if line.startswith('!['):
            m=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
            if not m:raise ValueError('Bad image syntax '+line)
            caption,rel=m.groups();path=(a.input.parent/rel).resolve()
            if path.suffix=='.svg':path=a.figure_cache/(path.stem+'.png')
            if not path.exists():raise FileNotFoundError(path)
            im=Image(str(path));aspect=im.imageHeight/im.imageWidth
            image_width=usable;image_height=usable*aspect
            max_height=330
            if image_height>max_height:image_height=max_height;image_width=image_height/aspect
            im.drawWidth=image_width;im.drawHeight=image_height
            story.append(KeepTogether([Spacer(1,8),im,Spacer(1,6),Paragraph(rich(caption),styles['small'])]));i+=1;continue
        if line.startswith('|'):
            table_lines=[]
            while i<len(lines) and lines[i].strip().startswith('|'):table_lines.append(lines[i].strip());i+=1
            rows=[[v.strip() for v in x.strip('|').split('|')] for x in table_lines]
            rows=[r for r in rows if not all(re.fullmatch(r':?-+:?',c) for c in r)]
            n=len(rows[0]);lengths=[max(6,len(rows[0][j]),min(52,max(len(r[j]) for r in rows))) for j in range(n)]
            weights=[max(0.14,v/sum(lengths)) for v in lengths];weights=[v/sum(weights) for v in weights]
            cells=[[Paragraph(rich(v),styles['tablehead'] if k==0 else styles['table']) for v in row] for k,row in enumerate(rows)]
            table=Table(cells,colWidths=[usable*w for w in weights],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),TEAL),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f0f4f3')]),('LINEBELOW',(0,-1),(-1,-1),0.5,colors.HexColor('#cfdbd8'))]))
            story.extend([table,Spacer(1,10)]);continue
        paragraph=[]
        while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#','|','![')):
            paragraph.append(lines[i].strip());i+=1
        if not paragraph:raise ValueError('Unexpected line '+line)
        text=' '.join(paragraph)
        style=styles['small'] if text.startswith('Complete working') or text.startswith('**[R') else styles['body']
        story.append(Paragraph(rich(text),style))
    doc.multiBuild(story)
    import fitz
    rendered=fitz.open(a.output);issues=[]
    for n,page in enumerate(rendered):
        for block in page.get_text('dict')['blocks']:
            if block.get('type')!=0:continue
            for line in block.get('lines',[]):
                for span in line.get('spans',[]):
                    x0,y0,x1,y1=span['bbox']
                    if x0<left-1 or x1>width-right+1 or y0<10 or y1>height-10:
                        issues.append({'page':n+1,'bbox':span['bbox'],'text':span['text']})
    diag={'pages':len(rendered),'text_characters':sum(len(p.get_text()) for p in rendered),'out_of_margin_text':issues,'fonts':'Georgia embedded regular,bold,italic,bolditalic','source':str(a.input)}
    a.output.with_suffix('.layout.json').write_text(json.dumps(diag,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pages':len(rendered),'margin_issues':len(issues)}))

if __name__=='__main__':main()
