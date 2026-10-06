"""Correct egg clipping with native PDF contours and derange August home categories."""
import ast,io,json,hashlib
from collections import defaultdict,deque
from pathlib import Path
from PIL import Image
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
ROOT=Path(__file__).resolve().parents[1]
# Reuse v25 helpers and verified layout without running its export or modifying it.
exec(compile((ROOT/'tools/refine-three-backs-v25.py').read_text().split('\nw=PdfWriter();b=')[0],'tools/refine-three-backs-v25.py','exec'),globals())
COMP=ROOT/'production/month-backs/refinements-v26';BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v25.pdf'
for rel in [BASE,'production/month-backs/refinements-v25/april-recolored-source.png','production/month-backs/refinements-v25/august-illustrated-source.png','tools/refine-three-backs-v25.py']:
 assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256'],rel
sheet='production/month-backs/refinements-v25/april-recolored-source.png'
im=Image.open(ROOT/sheet).convert('RGB');pixels=im.load()

def egg_contour(cx,top):
 # Read existing pixels only; do not edit/recolor/erase any source raster.
 roi=(cx-57,top,cx+57,top+137)
 dark={(x,y) for y in range(roi[1],roi[3]) for x in range(roi[0],roi[2]) if max(pixels[x,y])<115};components=[]
 while dark:
  seed=dark.pop();queue=deque([seed]);component=[seed]
  while queue:
   x,y=queue.popleft()
   for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
    n=x+dx,y+dy
    if n in dark:dark.remove(n);queue.append(n);component.append(n)
  components.append(component)
 component=max(components,key=len);rows=defaultdict(list)
 for x,y in component:rows[y].append(x)
 ys=sorted(rows);assert len(ys)>110
 # Subpixel allowance preserves antialiasing around the existing dark outline.
 left=[(min(rows[y])-.8,y-.4) for y in ys]
 right=[(max(rows[y])+.8,y+.4) for y in reversed(ys)]
 pts=left+right;xs,yy=zip(*pts)
 return {'polygon':pts,'bounds':[min(xs),min(yy),max(xs),max(yy)]}

cols=[867,973,1080,1188,1294,1401]
centers={'pink':(cols[0],550),'blue':(cols[1],550),'gold':(cols[2],550),'green':(cols[3],550),'zigzag':(cols[4],550),'hearts':(cols[5],550),'red':(cols[0],722),'stars':(cols[1],722),'confetti':(cols[3],722)}
contours={key:egg_contour(*center) for key,center in centers.items()}

def clipped_egg(c,shape,x,y):
 sx,sy,ex,ey=shape['bounds'];ax=100/(ex-sx);ay=122/(ey-sy)
 c.saveState();p=c.beginPath();pts=shape['polygon'];p.moveTo(x+(pts[0][0]-sx)*ax,PH-y-(pts[0][1]-sy)*ay)
 for xx,yy in pts[1:]:p.lineTo(x+(xx-sx)*ax,PH-y-(yy-sy)*ay)
 p.close();c.clipPath(p,stroke=0)
 c.drawImage(str(ROOT/sheet),x-sx*ax,PH-y-(1054-sy)*ay,1492*ax,1054*ay)
 c.restoreState()

def april_clean(c,src):
 ids=['pink','blue','gold','green','zigzag','hearts','red','stars','confetti','gold']
 box(c,814,515,658,344,'#fffdf0',r=15)
 for i,key in enumerate(ids):
  x=827+i%5*127;y=548+i//5*167
  clipped_egg(c,contours[key],x+11,y)
  if i==8:
   for dx,dy in [(48,31),(31,83)]:poly(c,star_points(x+11+dx,y+dy,6),'#fffdf0','#fffdf0',.2)
  text(c,x+61,y-9,'ABCDEFGHIJ'[i],21,'#44523a',center=True)
 assert ids[2]==ids[9] and len(set(ids))==9
 return {'answer':['C','J'],'motifs':ids,'contours':contours,'mask':'native PDF per-egg outline clipping; full tips, no rectangular background pieces','pair':'C/J use identical source, contour and scale'}

# Swap tree-related and ground-related home cards as well as exact matches.
code=ast.get_source_segment((ROOT/'tools/refine-three-backs-v25.py').read_text(),next(n for n in ast.parse((ROOT/'tools/refine-three-backs-v25.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='august_new'))
code=code.replace("names=['Owl','Rabbit','Squirrel','Fox','nest','den','tree hollow','burrow']","crops=crops[:4]+[crops[7],crops[6],crops[5],crops[4]]\n names=['Owl','Rabbit','Squirrel','Fox','burrow','tree hollow','den','nest']")
code=code.replace("{'Owl':3,'Rabbit':4,'Squirrel':1,'Fox':2}","{'Owl':2,'Rabbit':1,'Squirrel':4,'Fox':3}")
exec(code,globals())
records=[];w=PdfWriter();b=PdfReader(ROOT/BASE)
for month,builder in [(4,april_clean),(8,august_new)]:
 mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH));src=f'back-images-with-puzzles-v1/{month:02}.png';c.drawImage(str(ROOT/src),0,0,PW,PH)
 tr=tracker(c,month)
 if month==4:task(c,month)
 proof=builder(c,src)
 if month==8:
  assert list(proof['answer'].values())==[2,1,4,3]
  assert all(i+1!=j for i,j in enumerate(proof['answer'].values()))
  proof['category_check']='Owl over burrow, Rabbit over tree hollow, Squirrel over den, Fox over nest; no matching habitat category directly beneath.'
 c.save();mem.seek(0);page=PdfReader(mem).pages[0];page.scale_to(float(b.pages[month*2].mediabox.width),float(b.pages[month*2].mediabox.height));w.add_page(page)
 records.append({'month':month,'puzzle':proof,'tracker':tr,'visual_review':'pending','user_review':'pending'})
w.add_metadata({'/Title':'Giggle Dumplings - April and August corrections REVIEW v26','/Subject':'Working review, no print release.'})
with (ROOT/'tmp/pdfs/v26/candidate.pdf').open('wb') as f:w.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'months':records,'image_generation_calls':0,'source_images':'Unmodified v25 component sources; native contour clipping only.','user_review':'pending','print_status':'not_released'},indent=2)+'\n')
print('Two targeted pages staged; April pair C/J; August 2,1,4,3; no new image generation.')
