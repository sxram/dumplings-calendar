"""Replace January only; deterministic winter footprints scene."""
import hashlib, importlib.util, io, json, math, re
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('puzzles',ROOT/'tools/build-calendar-puzzles.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=ROOT/'production/puzzles/january-v09';out.mkdir(exist_ok=False)
s=m.header(1)
s.rect(5,57,310,227,'#f2f9fc','#d4e8f2',.6)
# Quiet winter scenery stays behind the four trails.
for x,y,z in [(56,78,.75),(154,73,.65),(215,267,.65),(59,270,.55)]:
 s.rect(x-2,y,4,12*z,'#bca18a','#bca18a')
 for dy,ww in [(0,13),(-9,10),(-17,7)]:
  s.poly([(x-ww*z,y+dy*z),(x,y+(dy-17)*z),(x+ww*z,y+dy*z)],'#deeee7','#b6d2c6',.6)
 s.line(x-8*z,y-7*z,x+8*z,y-7*z,'#ffffff',2)
for x,y in [(105,68),(220,72),(52,130),(211,214),(102,267),(291,269)]:
 s.line(x-2,y,x+2,y,'#c4dce7',.7);s.line(x,y-2,x,y+2,'#c4dce7',.7)
paths=[[(34,109),(72,91),(117,152),(156,179),(211,167),(253,144)],
       [(34,155),(77,178),(115,111),(166,97),(205,146),(253,201)],
       [(34,201),(75,222),(124,216),(168,151),(206,111),(253,90)],
       [(34,246),(78,242),(126,166),(173,224),(217,248),(253,255)]]
colors=['#367b9f','#93609b','#39765b','#9b662a']
def footprint(kind,x,y,theta):
 color=colors[kind]
 def p(dx,dy):return(x+dx*math.cos(theta)-dy*math.sin(theta),y+dx*math.sin(theta)+dy*math.cos(theta))
 if kind==0:
  for dy in [-2,0,2]:s.line(*p(-2,0),*p(2,dy),color,.9)
 elif kind==1:
  for dy in [-1.9,1.9]:
   s.poly([p(-2,dy-1),p(2,dy-1),p(3,dy),p(2,dy+1),p(-2,dy+1)],color,color,.4)
 elif kind==2:
  s.poly([p(-2,-1.3),p(1.7,-1.3),p(3,0),p(1.7,1.3),p(-2,1.3)],color,color,.4)
  s.line(*p(-3,-1),*p(-3,1),color,1)
 else:
  s.circle(x,y,1.8,color,color,.4)
  for dx,dy in [(2.8,-1.8),(3.3,0),(2.8,1.8)]:s.circle(*p(dx,dy),.65,color,color,.3)
for j,pts in enumerate(paths):
 s.text(18,pts[0][1]+3,'ABCD'[j],10,colors[j])
 carry=0;count=0
 for a,b in zip(pts,pts[1:]):
  distance=math.dist(a,b);theta=math.atan2(b[1]-a[1],b[0]-a[0]);d=carry
  while d<distance:
   t=d/distance;footprint(j,a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,theta);count+=1;d+=9
  carry=d-distance
 assert count>28
s.text(29,72,'START',7,m.BLUE)
m.star(s,282,90,16)
m.animal(s,'Rabbit',282,139,.6)
s.rect(271,190,23,25,m.CREAM);s.poly([(267,190),(282,178),(298,190)],'#b3cde0');s.circle(282,201,4,'#ffffff');s.line(282,215,282,232,'#ac9475',2)
s.circle(282,257,11,'#ffffff');s.circle(282,241,7,'#ffffff');s.line(274,236,290,236,m.BLUE,2);s.circle(280,241,.7,m.INK,m.INK);s.circle(284,241,.7,m.INK,m.INK)
s.poly([(282,243),(289,244),(282,245)],'#e5a34e');s.line(270,252,264,246,'#ac9475');s.line(294,252,301,247,'#ac9475')
(out/'01-puzzle.svg').write_text(s.svg());(out/'01-drawing.json').write_text(json.dumps(s.ops,indent=2)+'\n')
reg=json.loads((ROOT/'production/assets.json').read_text())
base='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v08.pdf';source='update_26-10-02/giggle_dumplings_2027_current_master_v4.pdf'
for rel in [base,source]:assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256']
page=PdfReader(ROOT/source).pages[2];raw=page.get_contents().get_data()
pattern=rb'BT 1 0 0 1 (164|185|206|227) 557\.2756 Tm (/F2\+0 25 Tf 30 TL \([2027]\) Tj T\* ET)'
raw,count=re.subn(pattern,lambda q:b'BT 1 0 0 1 '+str(int(q.group(1))+41).encode()+b' 557.2756 Tm '+q.group(2),raw);assert count==4
a=list(re.finditer(rb'1 1 1 rg\n([^\n]+) RG\n1 w\nn\n491 100 m\n',raw));b=list(re.finditer(rb'[^\n]+ rg\n[^\n]+ RG\n1 w\nn\n25 14 m\n',raw));assert len(a)==len(b)==1
new=raw[:a[0].start()]+raw[b[0].start():];new=new.replace(b'BT /F1 8.5 Tf 10.2 TL ET',b'.141176 .27451 .352941 rg\nBT /F1 8.5 Tf 10.2 TL ET')
stream=DecodedStreamObject();stream.set_data(new);page[NameObject('/Contents')]=stream
mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(float(page.mediabox.width),float(page.mediabox.height)))
c.setFillColor(HexColor('#ffffff'));c.setStrokeColor(HexColor('#62b9f5'));c.setLineWidth(.8);c.roundRect(479,100,348.89,315.2756,12,fill=1,stroke=1);s.render(c,493,110);c.save();mem.seek(0);page.merge_page(PdfReader(mem).pages[0])
r=PdfReader(ROOT/base);writer=PdfWriter()
for i,p in enumerate(r.pages):writer.add_page(page if i==2 else p)
writer.add_metadata({'/Title':'Giggle Dumplings 2027 - Arbeitsmaster v09'})
target=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v09.pdf';assert not target.exists();writer.write(target)
final=PdfReader(target);assert len(final.pages)==26
for i in range(26):
 if i!=2:assert final.pages[i].get_contents().get_data()==r.pages[i].get_contents().get_data()
assert m.TITLES[0] in final.pages[2].extract_text() and m.TASKS[0] in final.pages[2].extract_text()
proof={'base':base,'output':str(target.relative_to(ROOT)),'answer':'Trail C','paths':paths,'trail_shapes':['bird toes','paired rabbit marks','boots','paw and toes'],'crossings':'different shapes and colors; no connecting lines or branches','changed_pages':[3],'other_25_content_streams':'identical','visual_review':'pending','print_release':False}
(out/'manifest.json').write_text(json.dumps(proof,indent=2)+'\n')
print(target)
