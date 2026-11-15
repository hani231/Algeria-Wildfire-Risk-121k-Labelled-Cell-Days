"""Publication du rapport Markdown en PDF, sans écraser un livrable existant."""
import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from src.siad03_extensions.data import ROOT


def build_report(source, output):
    source, output = Path(source), Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    font_dir = Path(reportlab.__file__).parent/'fonts'
    pdfmetrics.registerFont(TTFont('Vera', str(font_dir/'Vera.ttf')))
    pdfmetrics.registerFont(TTFont('VeraBold', str(font_dir/'VeraBd.ttf')))
    styles = getSampleStyleSheet()
    for name in ['Title', 'Heading2']:
        styles[name].fontName = 'VeraBold'
    styles.add(ParagraphStyle(name='BodyFR', fontName='Vera', fontSize=10, leading=14, spaceAfter=9))
    styles.add(ParagraphStyle(name='CellFR', fontName='Vera', fontSize=7, leading=9))
    story, lines, i = [], source.read_text().splitlines(), 0
    def para(text, style='BodyFR'):
        return Paragraph(escape(text), styles[style])
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue
        if line.startswith('|'):
            rows=[]
            while i < len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+', c) for c in cells):
                    rows.append([para(c,'CellFR') for c in cells])
                i+=1
            table=Table(rows,colWidths=[480/len(rows[0])]*len(rows[0]),repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dbe8ef')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c1cbd1')),
                ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.extend([table,Spacer(1,12)]); continue
        image=re.match(r'!\[(.*?)\]\((.*?)\)',line)
        if image:
            picture=Image(str((source.parent/image[2]).resolve()))
            picture.drawHeight *= 475/picture.drawWidth; picture.drawWidth=475
            story.append(KeepTogether([picture,para(image[1],'Caption') if 'Caption' in styles else para(image[1])]))
        elif line.startswith('# '): story.append(para(line[2:],'Title'))
        elif line.startswith('## '): story.append(para(line[3:],'Heading2'))
        else:
            text=line
            while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|','![')):
                i+=1; text+=' '+lines[i].strip()
            story.append(para(text))
        i+=1
    def footer(canvas, doc):
        canvas.setFont('Vera',8)
        canvas.drawString(56,30,'SIAD03 | Annexe scientifique | Validation 2024, test 2025 réservé')
        canvas.drawRightString(A4[0]-56,30,str(doc.page))
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=56,leftMargin=56,topMargin=48,bottomMargin=50,
        title='Détections d’incendies en Algérie — annexe SIAD03',author='SIAD03')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'docs/siad03_extensions/RAPPORT.md')
    p.add_argument('--output',type=Path,default=ROOT/'docs/siad03_extensions/Rapport_SIAD03.pdf')
    a=p.parse_args(); build_report(a.source,a.output)
