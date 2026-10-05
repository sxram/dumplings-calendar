"""Illustrated January template + verified native text/calendar/vector puzzle."""
import calendar, hashlib, importlib.util, io, json, textwrap
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'production/month-backs/january-rich-v01'
base=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v15.pdf'
single=ROOT/'output/pdf/giggle-dumplings-january-back-ILLUSTRIERT-v02.pdf'
full=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v17.pdf'
assert not single.exists() and not full.exists()
reg=json.loads((ROOT/'production/assets.json').read_text())
assert hashlib.sha256(base.read_bytes()).hexdigest()==reg['assets'][str(base.relative_to(ROOT))]['sha256']
spec=importlib.util.spec_from_file_location('puzzles',ROOT/'tools/build-calendar-puzzles.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pdfmetrics.registerFont(TTFont('Chalk', '/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Rounded', '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'))
W,H=841.8898,595.2756
c=canvas.Canvas(str(single),pagesize=(W,H));c.setTitle('Giggle Dumplings January - Illustrierte Musterseite v02')
c.drawImage(str(out/'winter-template-v02.png'),0,0,W,H)
INK='#14395e';BLUE='#78bade'
def text(x,top,t,size=10,col=INK,center=False,font='Chalk'):
 c.setFillColor(HexColor(col));c.setFont(font,size)
 if center:x-=pdfmetrics.stringWidth(t,font,size)/2
 c.saveState();c.setLineWidth(.9);c.setStrokeColor(HexColor('#fffaf0'));obj=c.beginText(x,H-top);obj.setFont(font,size);obj.setTextRenderMode(2);obj.textOut(t);c.drawText(obj);c.restoreState();c.setFillColor(HexColor(col));c.setFont(font,size);c.drawString(x,H-top,t)
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
def headline(x,top,t,size,col):
 c.saveState();c.setLineWidth(3.2);c.setStrokeColor(HexColor('#ffffff'));c.setFillColor(HexColor(col));obj=c.beginText(x,H-top);obj.setFont('Rounded',size);obj.setTextRenderMode(2);obj.textOut(t);c.drawText(obj);obj=c.beginText(x,H-top);obj.setFont('Rounded',size);obj.setTextRenderMode(0);obj.textOut(t);c.drawText(obj);c.restoreState()
headline(112,100,'January',46,INK)
for n,(digit,col) in enumerate(zip('2027',['#f18535','#ef629a','#4fb7df','#48b9bf'])):headline(325+n*31,100,digit,46,col)
# Monday-first calendar; all day placements derive from Python's calendar.
x,top,width=18,142,461;column=width/7;header=18;row=28
c.setStrokeColor(HexColor(BLUE));c.setLineWidth(.5)
for j in range(8):c.line(x+j*column,H-top,x+j*column,H-(top+header+6*row))
for t in [top,top+header]+[top+header+j*row for j in range(1,7)]:c.line(x,H-t,x+width,H-t)
for j,name in enumerate(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']):text(x+(j+.5)*column,top+14,name,8.7,center=True)
placements=[]
for week,days in enumerate(calendar.Calendar(0).monthdayscalendar(2027,1)):
 for weekday,day in enumerate(days):
  if day:
   assert calendar.weekday(2027,1,day)==weekday
   text(x+weekday*column+5,top+header+week*row+13,str(day),9)
   placements.append({'day':day,'weekday':weekday,'row':week})
assert len(placements)==31
text(510,68,'The First Star',22,font='Rounded')
for j in range(12):
 pts=[(515+j*16+6*(1 if k%2==0 else .45)*__import__('math').cos(-__import__('math').pi/2+k*__import__('math').pi/5),98+6*(1 if k%2==0 else .45)*__import__('math').sin(-__import__('math').pi/2+k*__import__('math').pi/5)) for k in range(10)]
 c.setStrokeColor(HexColor('#a67d32' if j==0 else '#8c9da9'));c.setFillColor(HexColor('#efbc40' if j==0 else '#fffaf0'));p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
 for px,py in pts[1:]:p.lineTo(px,H-py)
 p.close();c.drawPath(p,fill=1,stroke=1)
story='The Dumplings discover mysterious footprints in the snow. The trail leads them through the winter forest to the first golden star.'
wrap(511,125,story,251,11,16)
text(114,371,"Bao's Job",13,font='Rounded');text(114,387,'This Month',13,font='Rounded')
text(139,408,'Winter Ranger Bao',10)
for j,t in enumerate(['Tracks footprints','Guides the team','Knows winter safety']):
 text(151,424+j*26,'•',9)
 wrap(161,424+j*26,t,102,9,12)
text(297,373,'Giggle Challenge',13,col='#aa4c68',font='Rounded')
wrap(308,404,'Make someone smile on a cold day.',137,12,17)
text(29,546,'Did you know?',13)
wrap(140,546,'Fresh snow can preserve animal tracks for hours.',560,10.3,14)
# Production scene: native footprints follow manually fitted snow corridors.
import math
scene=m.Scene()
paths_px=[[(985,575),(1010,608),(1060,634),(1120,635),(1190,624),(1240,635),(1310,655),(1360,665),(1380,655)],
          [(995,645),(1030,620),(1090,643),(1150,695),(1200,732),(1260,772),(1320,770),(1368,745),(1400,745)],
          [(995,735),(1030,723),(1080,714),(1120,700),(1150,669),(1190,647),(1240,644),(1290,615),(1330,595),(1380,560),(1400,555)],
          [(1020,805),(1070,842),(1130,836),(1180,821),(1240,826),(1290,817),(1340,833),(1365,853)]]
with Image.open(out/'winter-template-v02.png') as im:iw,ih=im.size
# Pixel coordinates refer to the inspected 1492 x 1054 illustration layout.
paths=[[(px*W/1492-503,py*H/1054-227.2756) for px,py in points] for points in paths_px]
colors=['#346c99','#6c6391','#377b78','#9b733e']
def mark(kind,x,y,theta):
 color=colors[kind]
 def p(dx,dy):return(x+dx*math.cos(theta)-dy*math.sin(theta),y+dx*math.sin(theta)+dy*math.cos(theta))
 if kind==0:
  for dy in [-2,0,2]:scene.line(*p(-2,0),*p(2,dy),color,.8)
 elif kind==1:
  for dy in [-1.9,1.9]:scene.poly([p(-2,dy-1),p(2,dy-1),p(3,dy),p(2,dy+1),p(-2,dy+1)],color,color,.3)
 elif kind==2:
  scene.poly([p(-2,-1.3),p(1.7,-1.3),p(3,0),p(1.7,1.3),p(-2,1.3)],color,color,.3);scene.line(*p(-3,-1),*p(-3,1),color,.8)
 else:
  scene.circle(x,y,1.7,color,color,.3)
  for dx,dy in [(2.8,-1.8),(3.3,0),(2.8,1.8)]:scene.circle(*p(dx,dy),.6,color,color,.2)
for kind,points in enumerate(paths):
 x0,y0=points[0];scene.circle(x0-11,y0,6,'#fff9e7','#ac9778',.6);scene.text(x0-11,y0+3,'ABCD'[kind],8,colors[kind])
 dense=[];extended=[points[0]]+points+[points[-1]]
 for j in range(len(points)-1):
  p0,p1,p2,p3=extended[j:j+4]
  for k in range(30):
   t=k/30
   dense.append(tuple(.5*((2*p1[d])+(-p0[d]+p2[d])*t+(2*p0[d]-5*p1[d]+4*p2[d]-p3[d])*t*t+(-p0[d]+3*p1[d]-3*p2[d]+p3[d])*t*t*t) for d in range(2)))
 dense.append(points[-1]);accum=0
 for a,b in zip(dense,dense[1:]):
  accum+=math.dist(a,b)
  if accum>=7:
   mark(kind,*b,math.atan2(b[1]-a[1],b[0]-a[0]));accum=0
# Do not draw the old geometric endpoint symbols: these are illustrated in the background.
text(591,242,m.TITLES[0],12,center=True,font='Rounded')
wrap(694,238,m.TASKS[0],125,8.1,11)
scene.render(c,503,78,1)
(out/'footprints-v02.svg').write_text(scene.svg())
(out/'footprints-drawing-v02.json').write_text(json.dumps(scene.ops,indent=2)+'\n')
c.save()
r=PdfReader(base);page=PdfReader(single).pages[0];writer=PdfWriter()
for i,p in enumerate(r.pages):writer.add_page(page if i==2 else p)
writer.add_metadata({'/Title':'Giggle Dumplings 2027 - Arbeitsmaster v17'});writer.write(full)
f=PdfReader(full);assert len(f.pages)==26
for i in range(26):
 if i!=2:assert f.pages[i].get_contents().get_data()==r.pages[i].get_contents().get_data()
text_out=' '.join(page.extract_text().split())
for t in [story,"Bao's Job This Month",'Winter Ranger Bao','Tracks footprints','Guides the team','Knows winter safety','Make someone smile on a cold day.','Fresh snow can preserve animal tracks for hours.',m.TITLES[0],m.TASKS[0]]:assert t in text_out,t
with Image.open(out/'winter-template-v02.png') as im:pixels=list(im.size)
manifest={'date':'2026-10-04','base':str(base.relative_to(ROOT)),'full_master':str(full.relative_to(ROOT)),'sample':str(single.relative_to(ROOT)),'template':'winter-template-v02.png','template_sha256':hashlib.sha256((out/'winter-template-v02.png').read_bytes()).hexdigest(),'template_pixels':pixels,'native_ppi_at_A4':round(pixels[0]/(W/72),1),'image_generation':'two built-in calls: initial scene + targeted terrain correction; prompt.txt and terrain-correction-prompt.txt','calendar_placements':placements,'tracker':'1 filled of 12','puzzle':'production/month-backs/january-rich-v01/footprints-drawing-v02.json','paths_px':paths_px,'construction':'4 separate smooth trails with distinct footprint shapes; C ends at illustrated star; no geometric endpoint icons','solution':'C','retained_content':'story, concrete Bao jobs, challenge, fact, puzzle title and instruction verified','other_25_content_streams':'identical','visual_review':'pending','user_review':'pending','print_release':False}
(out/'manifest-v02.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(single);print(full)
