import io,json,importlib.util
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'05-kdp/specials/drafts/pumpkin-card-v01'
OUT.mkdir(parents=True,exist_ok=True)
texts={
 'de':('Meine Kürbis-Überraschungskarte',['Male das Kürbisgesicht aus.','Schneide die Karte an der Außenlinie aus.','Falte einmal an der gestrichelten Linie.','Zeichne innen deine Überraschung: Kekse, Sterne oder ein Gespenst.'],'Hier deine Überraschung zeichnen!'),
 'en':('My Pumpkin Surprise Card',['Colour in the pumpkin face.','Cut out the card along the outer line.','Fold once along the dashed line.','Draw your surprise inside: cookies, stars or a ghost.'],'Draw your surprise here!'),
 'es':('Mi tarjeta sorpresa de calabaza',['Colorea la cara de la calabaza.','Recorta la tarjeta por la línea exterior.','Dóblala una vez por la línea discontinua.','Dibuja dentro tu sorpresa: galletas, estrellas o un fantasma.'],'¡Dibuja aquí tu sorpresa!')}
try: pdfmetrics.registerFont(TTFont('Body','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc'))
except Exception: pass
font='Body' if 'Body' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
def pumpkin(c,cx,cy):
 c.saveState();c.setLineWidth(2)
 c.ellipse(cx-75,cy-58,cx-5,cy+58,stroke=1,fill=0);c.ellipse(cx+5,cy-58,cx+75,cy+58,stroke=1,fill=0);c.ellipse(cx-40,cy-64,cx+40,cy+64,stroke=1,fill=0)
 c.line(cx-8,cy+60,cx-2,cy+82);c.line(cx+3,cy+60,cx+9,cy+82);c.arc(cx-5,cy+72,cx+35,cy+92,20,100)
 c.circle(cx-27,cy+15,5,stroke=1,fill=0);c.circle(cx+27,cy+15,5,stroke=1,fill=0)
 c.arc(cx-20,cy-25,cx+20,cy+8,200,140);c.restoreState()
def make(lang):
 title,lines,inside=texts[lang];b=io.BytesIO();c=canvas.Canvas(b,pagesize=(504,720));c.setFillColor(black);c.setFont(font,22 if lang!='es' else 20);c.drawString(42,665,title);c.setFont(font,10)
 for i,line in enumerate(lines): c.drawString(42,632-i*15,line)
 x,y,w,h=72,125,360,360
 c.setLineWidth(1.4);c.rect(x,y,w,h,stroke=1,fill=0);c.setDash(5,3);c.line(x,y+h/2,x+w,y+h/2);c.setDash([])
 c.setFont(font,9);c.drawCentredString(252,y+h/2+8,'Faltlinie / Fold / Doblar')
 pumpkin(c,252,y+92);c.setFont(font,10);c.drawCentredString(252,y+h-32,inside)
 c.setFont(font,9);c.drawString(42,72,'Durchgezogen / Solid: schneiden / cut');c.drawRightString(462,72,'Gestrichelt / Dashed: falten / fold')
 c.setFont(font,8);c.drawString(42,34,'B06 · Papierprobe vor Druckfreigabe')
 c.showPage();c.save();b.seek(0);return PdfReader(b).pages[0]
w=PdfWriter()
for lang in ('de','en','es'): w.add_page(make(lang))
path=OUT/'kuerbis-ueberraschungskarte-de-en-es-v01.pdf'
with path.open('wb') as f:w.write(f)
manifest={'status':'review_draft','mechanism':'one horizontal center fold; blank interior; no glue tab; no mouth flap','languages':['de','en','es'],'output':str(path.relative_to(ROOT)),'visual_review':'pending','physical_test':'open','print_release':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(path)
