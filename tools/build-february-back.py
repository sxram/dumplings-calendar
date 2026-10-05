"""Illustrated February template + verified native text/calendar/vector puzzle."""
import calendar, hashlib, importlib.util, io, json, textwrap
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'production/month-backs/february-v01'
base=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v13.pdf'
single=ROOT/'output/pdf/giggle-dumplings-february-back-MUSTER-v02.pdf'
full=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v15.pdf'
assert not single.exists() and not full.exists()
reg=json.loads((ROOT/'production/assets.json').read_text())
assert hashlib.sha256(base.read_bytes()).hexdigest()==reg['assets'][str(base.relative_to(ROOT))]['sha256']
spec=importlib.util.spec_from_file_location('puzzles',ROOT/'tools/build-calendar-puzzles.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pdfmetrics.registerFont(TTFont('Chalk', '/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
W,H=841.8898,595.2756
c=canvas.Canvas(str(single),pagesize=(W,H));c.setTitle('Giggle Dumplings February - Musterseite v02')
c.drawImage(str(out/'winter-template.png'),0,0,W,H)
INK='#14395e';BLUE='#d19bb5'
def text(x,top,t,size=10,col=INK,center=False,font='Chalk'):
 c.setFillColor(HexColor(col));c.setFont(font,size)
 (c.drawCentredString if center else c.drawString)(x,H-top,t)
def wrap(x,top,t,width,size=10,leading=14):
 words=t.split();line='';lines=[]
 for word in words:
  test=(line+' '+word).strip()
  if pdfmetrics.stringWidth(test,'Chalk',size)>width and line:lines.append(line);line=word
  else:line=test
 if line:lines.append(line)
 for n,line in enumerate(lines):text(x,top+n*leading,line,size)
 return lines
text(60,45,'Giggle',8,center=True);text(60,57,'Dumplings',8,center=True)
c.setFillColor(HexColor('#fffaf2'));c.setFillAlpha(.93);c.roundRect(111,H-105,360,47,13,fill=1,stroke=0);c.setFillAlpha(1)
text(120,94,'February',36)
for n,(digit,col) in enumerate(zip('2027',['#f18535','#ef629a','#4fb7df','#48b9bf'])):text(340+n*28,94,digit,40,col)
# Monday-first calendar; all day placements derive from Python's calendar.
x,top,width=18,131,461;column=width/7;header=18;row=29
c.setStrokeColor(HexColor(BLUE));c.setLineWidth(.5)
for j in range(8):c.line(x+j*column,H-top,x+j*column,H-(top+header+6*row))
for t in [top,top+header]+[top+header+j*row for j in range(1,7)]:c.line(x,H-t,x+width,H-t)
for j,name in enumerate(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']):text(x+(j+.5)*column,top+14,name,8.7,center=True)
placements=[]
for week,days in enumerate(calendar.Calendar(0).monthdayscalendar(2027,2)):
 for weekday,day in enumerate(days):
  if day:
   assert calendar.weekday(2027,2,day)==weekday
   text(x+weekday*column+5,top+header+week*row+13,str(day),9)
   placements.append({'day':day,'weekday':weekday,'row':week})
assert len(placements)==28
text(510,68,'The Secret Valentine',20)
for j in range(12):
 pts=[(515+j*16+6*(1 if k%2==0 else .45)*__import__('math').cos(-__import__('math').pi/2+k*__import__('math').pi/5),98+6*(1 if k%2==0 else .45)*__import__('math').sin(-__import__('math').pi/2+k*__import__('math').pi/5)) for k in range(10)]
 c.setStrokeColor(HexColor('#a67d32' if j<2 else '#8c9da9'));c.setFillColor(HexColor('#efbc40' if j<2 else '#fffaf0'));p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
 for px,py in pts[1:]:p.lineTo(px,H-py)
 p.close();c.drawPath(p,fill=1,stroke=1)
story='Friendly letters lead the Dumplings through the snowy village. At the old bridge they discover the second golden star.'
wrap(511,125,story,251,11,16)
text(50,373,"Bao's Job This Month",12)
text(139,398,'Mail Carrier Bao',10)
for j,t in enumerate(['Carries letters','Finds addresses','Delivers kind notes']):
 text(164,424+j*26,'•',9)
 wrap(174,424+j*26,t,90,9,12)
text(297,373,'Giggle Challenge',14,col='#aa4c68')
wrap(296,404,'Leave someone a kind little note.',151,12,17)
c.setFillColor(HexColor('#fffaf2'));c.setFillAlpha(.94);c.roundRect(23,H-562,792,34,10,fill=1,stroke=0);c.setFillAlpha(1)
text(29,546,'Did you know?',13)
wrap(140,546,'Handwritten notes can make people feel remembered.',560,10.3,14)
scene=m.Scene();scene.ops=json.loads((ROOT/'production/puzzles/v07/02-drawing.json').read_text())
# Remove only the two flat background rectangles; the new raster template provides these.
scene.ops=[(k,a) for k,a in scene.ops if not (k=='poly' and a[0] in [[[0,0],[320,0],[320,290],[0,290]],[[5,57],[315,57],[315,284],[5,284]]])]
scene.ops=[(k, [*a[:3],a[3]*1.15,*a[4:]] if k=='text' and a[1]<50 else a) for k,a in scene.ops]
scene.ops=[(k,[a[0],a[1]+21.25,*a[2:]] if k=='text' and a[1]<50 else a) for k,a in scene.ops]
scene.render(c,550,160,.80)
c.save()
r=PdfReader(base);page=PdfReader(single).pages[0];writer=PdfWriter()
for i,p in enumerate(r.pages):writer.add_page(page if i==4 else p)
writer.add_metadata({'/Title':'Giggle Dumplings 2027 - Arbeitsmaster v15'});writer.write(full)
f=PdfReader(full);assert len(f.pages)==26
for i in range(26):
 if i!=4:assert f.pages[i].get_contents().get_data()==r.pages[i].get_contents().get_data()
text_out=' '.join(page.extract_text().split())
for t in [story,"Bao's Job This Month",'Mail Carrier Bao','Carries letters','Finds addresses','Delivers kind notes','Leave someone a kind little note.','Handwritten notes can make people feel remembered.',m.TITLES[1],m.TASKS[1]]:assert t in text_out,t
with Image.open(out/'winter-template.png') as im:pixels=list(im.size)
manifest={'date':'2026-10-04','base':str(base.relative_to(ROOT)),'full_master':str(full.relative_to(ROOT)),'sample':str(single.relative_to(ROOT)),'template':'winter-template.png','template_sha256':hashlib.sha256((out/'winter-template.png').read_bytes()).hexdigest(),'template_pixels':pixels,'native_ppi_at_A4':round(pixels[0]/(W/72),1),'image_generation':'one built-in call; prompt.txt','calendar_placements':placements,'tracker':'2 filled of 12','puzzle':'production/puzzles/v07/02-drawing.json','solution':{'A':3,'B':1,'C':4,'D':2},'retained_content':'story, concrete Bao jobs, challenge, fact, puzzle title and instruction verified','other_25_content_streams':'identical','visual_review':'pending','user_review':'pending','print_release':False}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(single);print(full)
