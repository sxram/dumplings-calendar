"""Targeted native title repairs and deterministic curling February routes."""
import io,json,hashlib,math
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
R=Path(__file__).resolve().parents[1];PW,PH=1492,1054
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v33.pdf';OUT='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v34.pdf';C=R/'production/refinements/v34'
reg=json.loads((R/'production/assets.json').read_text());assert reg['selection']['current_working_master']==BASE
for rel in [BASE,'back-images-with-puzzles-v1/02.png','back-images-with-puzzles-v1/03.png','production/month-backs/february-paths-v23/manifest.json']:
 assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256'],rel
assert not (R/OUT).exists()
r=PdfReader(R/BASE);w=PdfWriter(clone_from=r)
pdfmetrics.registerFont(TTFont('Repair','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
records=[]
def remove(page,which):
 cs=ContentStream(page.get_contents(),w);drop=set();got=[]
 for i,(a,o) in enumerate(cs.operations):
  if o!=b'BT':continue
  j=i+1
  while cs.operations[j][1]!=b'ET':j+=1
  s=[str(aa[0]) for aa,oo in cs.operations[i:j] if oo==b'Tj']
  tm=[aa for aa,oo in cs.operations[i:j] if oo==b'Tm']
  mat=None
  for k in range(i-1,max(-1,i-5),-1):
   if cs.operations[k][1]==b'cm':mat=cs.operations[k][0];break
  x=float(mat[4]) if mat else (float(tm[0][4]) if tm else -1)
  y=PH-(float(mat[5]) if mat else (float(tm[0][5]) if tm else -1))
  if len(s)==1 and which(s[0],x,y):drop.update(range(i,j+1));got.append({'text':s[0],'x':x,'y':y})
 cs.operations=[v for i,v in enumerate(cs.operations) if i not in drop];page.replace_contents(cs);return got

def merge(page,draw):
 mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH));draw(c);c.save();mem.seek(0)
 p=PdfReader(mem).pages[0];p.scale_to(float(page.mediabox.width),float(page.mediabox.height));page.merge_page(p)

def text(c,s,x,baseline,size,center=False):
 c.setFillColor(HexColor('#173e59'));c.setFont('Repair',size)
 (c.drawCentredString if center else c.drawString)(x,baseline,s)

p=w.pages[6]
got=remove(p,lambda s,x,y:s=='The Missing Seeds' or (s in ['Small','Steps','Big Change'] and x>1300) or (s=='Seeds' and x>1350) or s in ['Seed','Trail'])
assert len(got)==7,got
# Restore only the original wooden puzzle sign. Its lettering is an illustrated source element.
def march(c):
 text(c,'The Missing Seeds',890,900,48)
 for s,b in [('Small',128),('Steps',106),('Big Change',84)]:text(c,s,1385,b,18,True)
 c.saveState();path=c.beginPath();path.rect(875,PH-513,235,67);c.clipPath(path,stroke=0)
 c.drawImage(str(R/'back-images-with-puzzles-v1/03.png'),0,0,PW,PH);c.restoreState()
merge(p,march);records.append({'page':7,'removed':got,'story_title_size':48,'small_sign_size':18,'puzzle_sign':'Original source clip restored; original illustrated title and wood retained. No opaque new title rectangle.','seed_bag':'Only native Seeds next to puzzle title removed; other bags retained.'})
p=w.pages[12];got=remove(p,lambda s,x,y:s in ['The','Picnic','Mystery'] and y<100)
assert len(got)==3,got
merge(p,lambda c:text(c,'The Picnic Mystery',1162,988,48,True));records.append({'page':13,'removed':got,'title':'One text object with uniform font size and baseline; no per-word fitting.'})
# February: four continuous cubic paths, endpoint mapping from the existing specification.
old=json.loads((R/'production/month-backs/february-paths-v23/manifest.json').read_text())
levels=[590,669,747,828];orders=old['column_orders'];curves={}
# Broader curves: keep every second column, retaining the exact end permutation.
idx=[0,2,4,6,8,10];xs=[971+(1382-971)*j/5 for j in range(6)]
for letter in 'ABCD':
 pts=[(xs[j],levels[orders[k].index(letter)]+([0,14,-18,15,-12,0][j])) for j,k in enumerate(idx)]
 segs=[]
 for j,(a,b) in enumerate(zip(pts,pts[1:])):
  dx=b[0]-a[0];bend=(18 if j%2==0 else -18)
  segs.append([a,(a[0]+dx*.90,a[1]+bend),(b[0]-dx*.90,b[1]-bend),b])
 curves[letter]=segs
assert {a:levels.index(v[-1][-1][1])+1 for a,v in curves.items()}=={'A':3,'B':1,'C':4,'D':2}
def piece(c,crop,target):
 sx,sy,ex,ey=crop;x,y,ww,hh=target;ax,ay=ww/(ex-sx),hh/(ey-sy)
 c.saveState();p=c.beginPath();p.roundRect(x,PH-y-hh,ww,hh,8);c.clipPath(p,stroke=0)
 c.drawImage(str(R/'back-images-with-puzzles-v1/02.png'),x-sx*ax,PH-y-(PH-sy)*ay,PW*ax,PH*ay);c.restoreState()
def feb(c):
 piece(c,(480,0,859,180),(867,539,608,383))
 crops=[((870,542,970,604),(869,556,104,65)),((870,616,970,681),(869,634,104,68)),((870,691,970,755),(869,713,104,67)),((870,768,971,834),(869,792,104,69)),((1383,566,1474,633),(1380,555,91,67)),((1383,645,1474,712),(1380,634,91,67)),((1383,722,1474,789),(1380,713,91,67)),((1383,799,1474,869),(1380,792,91,70))]
 for crop,target in crops:piece(c,crop,target)
 for a,segs in curves.items():
  for col,width in [('#ffffff',11),('#5593c7',6.5),('#a8daf1',3)]:
   c.setStrokeColor(HexColor(col));c.setLineWidth(width);c.setLineCap(1)
   p=c.beginPath();p.moveTo(segs[0][0][0],PH-segs[0][0][1])
   for seg in segs:p.curveTo(*[v for x,y in seg[1:] for v in (x,PH-y)])
   c.drawPath(p)
merge(w.pages[4],feb)
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v34','/Subject':'February curling paths, March local lettering corrections, June aligned story title. User review pending; not print released.'})
with (R/OUT).open('wb') as f:w.write(f)
q=PdfReader(R/OUT)
for n in range(26):
 if n in [4,6,12]:continue
 assert r.pages[n].get_contents().get_data()==q.pages[n].get_contents().get_data(),n
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="867 539 608 383">']
for a,segs in curves.items():
 d='M '+','.join(map(str,segs[0][0]))
 for seg in segs:d+=' C '+' '.join(f'{x:.4f},{y:.4f}' for x,y in seg[1:])
 for col,width in [('#ffffff',11),('#5593c7',6.5),('#a8daf1',3)]:svg.append(f'<path data-letter="{a}" d="{d}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round"/>')
svg.append('</svg>');(C/'february-paths.svg').write_text('\n'.join(svg)+'\n')
(C/'manifest.json').write_text(json.dumps({'base':BASE,'output':OUT,'changed_pages':[5,7,13],'unchanged_content_pages_verified':23,'local_text_changes':records,'february':{'paths':curves,'answer':{'A':3,'B':1,'C':4,'D':2},'construction':'Four separate continuous cubic paths, broad control handles and alternating bends; endpoint identities retained.','visual_review':'pending'},'image_generation_calls':0,'visual_review':'pending','user_review':'pending','print_status':'not_released'},ensure_ascii=False,indent=2)+'\n')
print('v34 created; 23 other page content streams unchanged.')
