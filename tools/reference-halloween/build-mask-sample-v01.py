"""Versioned visual mask prototype; no changes to full book or raster sources."""
from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
registry=json.loads((ROOT/'production/assets.json').read_text())
asset=registry['assets']['mask.sunny.v02']
source=ROOT/asset['path']
assert hashlib.sha256(source.read_bytes()).hexdigest()==asset['sha256'], 'Source checksum mismatch'
assert asset['design_status'] not in ('rejected','reference_only'), 'Blocked source'
out=ROOT/'05-kdp/review/mask-sunny-v01/sunny-vampir-maske-muster-v01.pdf'
pdfmetrics.registerFont(TTFont('Body','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc'))
c=canvas.Canvas(str(out),pagesize=(504,720));c.setTitle('Sunny als Vampir - Maskenmuster v01')
def text(x,y,t,size=11):
 c.setFont('Body',size);c.drawString(x,y,t)
text(36,682,'BASTELMUSTER · ENTWURF v01',10)
text(36,650,'Sunny als kleiner Vampir',23)
# Raster illustration, original bytes and colors preserved. White margin may extend off page.
x,y,w,h=-12,270,528,352
c.drawImage(str(source),x,y,width=w,height=h)
def xy(a,b):return x+a*w/1536,y+(1024-b)*h/1024
# Technical outer cut contour, deliberately outside the illustration.
p=c.beginPath();p.moveTo(*xy(676,47))
for coords in [(696,-20,813,-20,842,49),(1044,68,1176,185,1188,385),(1330,507,1330,747,1168,883),(985,1042,539,1038,344,877),(205,757,214,566,275,468),(239,470,239,406,311,358),(340,182,476,75,676,47)]:
 p.curveTo(*sum((xy(coords[k],coords[k+1]) for k in (0,2,4)),()))
p.close();c.setLineWidth(.55);c.drawPath(p)
# Eye opening paths sit inside the illustrated eye outlines.
for cx in (525,1005):
 a,b=xy(cx-87,550);d,e=xy(cx+87,642);c.ellipse(a,e,d,b)
# Glue locator is fully within the lower right cheek; dotted, never a cut.
a,b=xy(1020,740);c.setDash(1,2);c.rect(a,b-28,30,28);c.setDash()
text(36,241,'1  Male Sunny aus und klebe das Blatt auf dünnen Karton.',10.5)
text(36,224,'2  Schneide an der feinen äußeren Linie aus.',10.5)
text(36,207,'3  Lass die kleinen inneren Augenovale ausschneiden.',10.5)
text(36,190,'    Bitte eine erwachsene Person um Hilfe.',10.5)
text(36,173,'4  Schneide den Stiel aus. Klebe das markierte Ende hinten',10.5)
text(36,156,'    an die punktierte Stelle. Trocknen lassen - und Foto!',10.5)
# Separate reinforced paper handle, about 68 x 11 mm with 10 mm overlap.
c.setLineWidth(.65);c.roundRect(248,90,194,30,3);c.setDash(1,2);c.line(276,90,276,120);c.setDash()
text(248,131,'Stiel: linkes Ende hinten ankleben',9)
text(36,121,'Schnittlinie',9);c.line(36,109,111,109)
text(145,121,'Klebefläche',9);c.setDash(1,2);c.rect(145,100,62,12);c.setDash()
text(36,77,'Papierprobe: bei 100 % drucken, nicht anpassen.',9)
text(36,62,'Passform und Halt sind noch nicht praktisch geprüft.',9)
text(36,39,'Kontrollmaß: 5 cm',8);c.line(36,27,36+50/25.4*72,27)
c.line(36,24,36,30);c.line(36+50/25.4*72,24,36+50/25.4*72,30)
c.showPage();c.save()
r=PdfReader(str(out));assert len(r.pages)==1 and list(r.pages[0].mediabox)==[0,0,504,720]
assert 'Sunny als kleiner Vampir' in r.pages[0].extract_text()
manifest={'status':'review_draft','print_status':'not_released','whole_book_changed':False,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(out.relative_to(ROOT)),'page_pt':[504,720],'image_box_pt':[x,y,w,h],'image_px':[1536,1024],'effective_dpi':1536/(w/72),'eye_center_distance_mm':480*w/1536/72*25.4,'eye_opening_mm':[174*w/1536/72*25.4,92*h/1024/72*25.4],'layers':['unchanged generated illustration','outer cut path','eye opening paths','glue locator','handle','German text'],'physical_test':'open','visual_review':'pending','limitations':['Small stick-held photo mask, not a fitted costume mask','Native raster below 300 dpi at this size; print preparation open','No DE/EN/ES whole-book insertion']}
(out.parent/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(out)
