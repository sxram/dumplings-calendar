"""Deterministic calendar puzzle components and lower-page working master.
No image generation. SVG + PDF share a single drawing model.
"""
import argparse, calendar, hashlib, html, io, json, math, re, textwrap
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject
ROOT=Path(__file__).resolve().parents[1]
BLUE='#1e6ea1'; INK='#24465a'; GOLD='#efbc40'; GREEN='#79a984'; CREAM='#fff4d8'
W,H=320,290
TITLES=['Follow the Footprints!','Special Delivery','Seed Trail','Find the Matching Eggs!','Find the Butterflies!','Who Took the Strawberries?','Which Shadow Belongs to the Castle?','Who Lives Here?','Find the 6 Differences!','Pumpkin Pairs','Put the Storm Story in Order!','Complete the Last Star!']
TASKS=['Which footprints lead to the golden star? Follow the trail!','Follow each path. Which mailbox gets each letter?','What comes next? Complete the two patterns!','Two eggs are exactly the same. Can you find them?','Eight butterflies are hiding in the picture. Can you find them all?','The strawberries are gone! Read the clues and find out who took them.','Look carefully! Which shadow matches the sandcastle exactly?','Match each woodland animal to its home.','These two pictures look almost the same. Can you find all 6 differences?','Find the 5 matching pairs. Which 2 pumpkins are left without a partner?','What happened first? Put the 4 pictures in the correct order.','One piece is missing. Which piece completes the star exactly?']
class Scene:
 def __init__(self):self.ops=[]
 def add(self,k,*a):self.ops.append((k,a))
 def text(self,x,y,t,size=10,color=INK,anchor='middle'):self.add('text',x,y,t,size,color,anchor)
 def line(self,x,y,xx,yy,color=INK,width=1.2):self.add('line',x,y,xx,yy,color,width)
 def poly(self,pts,fill='none',stroke=INK,width=1):self.add('poly',pts,fill,stroke,width)
 def rect(self,x,y,w,h,fill='none',stroke=INK,width=1):self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,stroke,width)
 def ellipse(self,x,y,rx,ry,fill='none',stroke=INK,width=1):self.add('ellipse',x,y,rx,ry,fill,stroke,width)
 def circle(self,x,y,r,fill='none',stroke=INK,width=1):self.ellipse(x,y,r,r,fill,stroke,width)
 def bezier(self,pts,color=INK,width=1.4):self.add('bezier',pts,color,width)
 def image_crop(self,rel,box,x,y,w,h):self.add('image',rel,box,x,y,w,h)
 def render(self,c,ox=0,oy=0,scale=1):
  c.saveState();c.translate(ox,oy);c.scale(scale,scale)
  for k,a in self.ops:
   if k=='text':
    x,y,t,size,col,anchor=a;c.setFillColor(HexColor(col));c.setFont('Helvetica',size)
    getattr(c,{'middle':'drawCentredString','end':'drawRightString','start':'drawString'}[anchor])(x,H-y,t)
   elif k in ['poly','ellipse']:
    *vals,fill,stroke,width=a;c.setLineWidth(width);c.setStrokeColor(HexColor(stroke));c.setFillColor(HexColor(fill if fill!='none' else '#ffffff'))
    if k=='poly':
     p=c.beginPath();p.moveTo(vals[0][0][0],H-vals[0][0][1])
     for x,y in vals[0][1:]:p.lineTo(x,H-y)
     p.close();c.drawPath(p,stroke=1,fill=fill!='none')
    else:
     x,y,rx,ry=vals;c.ellipse(x-rx,H-y-ry,x+rx,H-y+ry,stroke=1,fill=fill!='none')
   elif k=='line':
    x,y,xx,yy,col,width=a;c.setStrokeColor(HexColor(col));c.setLineWidth(width);c.line(x,H-y,xx,H-yy)
   elif k=='bezier':
    pts,col,width=a;c.setStrokeColor(HexColor(col));c.setLineWidth(width);p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1]);p.curveTo(*[v for x,y in pts[1:] for v in (x,H-y)]);c.drawPath(p)
   elif k=='image':
    rel,(bx,by,bw,bh),x,y,w,h=a;from PIL import Image
    with Image.open(ROOT/rel) as im:iw,ih=im.size
    c.saveState();p=c.beginPath()
    if bx==1050:
     points=[(1050,330),(1344,330),(1344,565),(1318,600),(1318,695),(1050,695)]
     for j,(px,py) in enumerate(points):
      getattr(p,'moveTo' if j==0 else 'lineTo')(x+(px-bx)*w/bw,H-y-(py-by)*h/bh)
     p.close()
    else:p.rect(x,H-y-h,w,h)
    c.clipPath(p,stroke=0,fill=0)
    c.drawImage(str(ROOT/rel),x-bx*w/bw,H-y-h-(ih-by-bh)*h/bh,width=iw*w/bw,height=ih*h/bh);c.restoreState()
  c.restoreState()
 def svg(self):
  out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="320pt" height="290pt" viewBox="0 0 320 290">']
  for i,(k,a) in enumerate(self.ops):
   if k=='text':
    x,y,t,size,col,anchor=a;out.append(f'<text x="{x}" y="{y}" fill="{col}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" text-anchor="{anchor}">{html.escape(t)}</text>')
   elif k=='poly':
    pts,fill,stroke,width=a;out.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
   elif k=='ellipse':
    x,y,rx,ry,fill,stroke,width=a;out.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
   elif k=='line':
    x,y,xx,yy,col,width=a;out.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="{col}" stroke-width="{width}"/>')
   elif k=='bezier':
    pts,col,width=a;out.append(f'<path d="M{pts[0][0]} {pts[0][1]} C{" ".join(f"{x} {y}" for x,y in pts[1:])}" fill="none" stroke="{col}" stroke-width="{width}"/>')
   elif k=='image':
    rel,(bx,by,bw,bh),x,y,w,h=a;clip=(f'<defs><clipPath id="crop-{i}"><polygon points="1050,330 1344,330 1344,565 1318,600 1318,695 1050,695"/></clipPath></defs>' if bx==1050 else '');attr=(f' clip-path="url(#crop-{i})"' if clip else '');out.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{bx} {by} {bw} {bh}">{clip}<image{attr} href="../../../{html.escape(rel)}" width="1717" height="916"/></svg>')
  return '\n'.join(out+['</svg>'])

def star(s,x,y,r=12,n=5,fill=GOLD):
 pts=[(x+math.cos(-math.pi/2+i*math.pi/n)*(r if i%2==0 else r*.45),y+math.sin(-math.pi/2+i*math.pi/n)*(r if i%2==0 else r*.45)) for i in range(2*n)];s.poly(pts,fill,'#aa7b17');return pts

def flower(s,x,y,col='#e891a2'):
 for t in range(5):s.circle(x+math.cos(t*math.tau/5)*4,y+math.sin(t*math.tau/5)*4,3,col,col)
 s.circle(x,y,2,GOLD,GOLD)
def butterfly(s,x,y,size=1):
 for dx in [-1,1]:s.ellipse(x+dx*4*size,y-3*size,4*size,5*size,CREAM,GREEN);s.ellipse(x+dx*3*size,y+4*size,3*size,3*size,CREAM,GREEN)
 s.line(x,y-6*size,x,y+7*size,INK,1.2);s.line(x,y-5*size,x-3*size,y-9*size);s.line(x,y-5*size,x+3*size,y-9*size)
def animal(s,name,x,y,z=1):
 col={'Rabbit':'#ead8bd','Squirrel':'#d69964','Duck':'#f7d86a','Owl':'#bca18a','Fox':'#e49852'}.get(name,CREAM)
 if name=='Rabbit':
  for dx in [-6,6]:s.ellipse(x+dx*z,y-19*z,4*z,14*z,col)
 if name=='Squirrel':s.ellipse(x+17*z,y+12*z,10*z,17*z,col)
 if name in ['Fox','Owl']:
  for dx in [-8,8]:s.poly([(x+dx*z-5*z,y-8*z),(x+dx*z,y-21*z),(x+dx*z+5*z,y-8*z)],col)
 s.ellipse(x,y+10*z,14*z,18*z,col);s.circle(x,y,13*z,col)
 for dx in [-5,5]:s.circle(x+dx*z,y-2*z,1.5*z,INK,INK)
 if name=='Duck':s.poly([(x+8*z,y),(x+22*z,y+3*z),(x+8*z,y+7*z)],'#efad46')
 else:s.poly([(x-2*z,y+5*z),(x+2*z,y+5*z),(x,y+8*z)],INK)

def seed(s,name,x,y):
 if name=='acorn':s.ellipse(x,y,7,9,CREAM);s.rect(x-8,y-7,16,5,'#bca18a');s.line(x,y-7,x+2,y-12)
 elif name=='sunflower':s.ellipse(x,y,4,10,'#dbbd84');s.line(x,y-7,x,y+7)
 elif name=='pumpkin':s.ellipse(x,y,7,10,CREAM)
 elif name=='sprout':s.line(x,y+10,x,y-4,GREEN,2);s.ellipse(x-4,y-4,5,3,GREEN,GREEN);s.ellipse(x+4,y-8,5,3,GREEN,GREEN)
 elif name=='tulip':s.line(x,y+10,x,y-4,GREEN,2);s.poly([(x-8,y-12),(x-4,y-5),(x,y-12),(x+4,y-5),(x+8,y-12),(x+6,y+1),(x-6,y+1)],'#e891a2')

def egg(s,x,y,k):
 s.ellipse(x,y,17,24,CREAM)
 if k==2:
  for dx in [-7,7]:
   for dy in [-9,5]:s.circle(x+dx,y+dy,2.5,'#d28ab1')
 elif k%3==0:
  for j in range(k//3+1):
   dy=-9+j*9;s.line(x-12,y+dy,x+12,y+dy,'#77a8be',2)
 elif k%3==1:
  for j in range(k//3+1):flower(s,x,y-10+j*11)
 else:
  for j in range(k//3):
   dy=-9+j*12;s.poly([(x-11,y+dy),(x-6,y+dy-6),(x,y+dy),(x+6,y+dy-6),(x+11,y+dy)],'none',GREEN,2)
  s.circle(x,y+13,3,GOLD)

def castle(s,x,y,z=1,variant=0,shadow=False):
 pts=[(0,65),(0,20),(8,20),(8,10),(16,10),(16,20),(24,20),(24,10),(32,10),(32,20),(40,20),(40,35),(60,35),(60,20),(68,20),(68,10),(76,10),(76,20),(84,20),(84,10),(92,10),(92,20),(100,20),(100,65)]
 if variant==1:pts=[(xx,yy-8 if xx<40 and yy<=20 else yy) for xx,yy in pts]
 if variant==2:pts=[(xx,yy+12 if xx>=60 and yy<35 else yy) for xx,yy in pts]
 if variant==3:pts=[(xx,yy) for xx,yy in pts if xx<84 or yy==65];pts[-2:]=[(100,35),(100,65)]
 s.poly([(x+xx*z,y+yy*z) for xx,yy in pts],INK if shadow else '#e9c68b')
 # Flag belongs to the exact exterior in reference and C.
 s.rect(x+19*z,y-8*z,2*z,20*z,INK if shadow else INK)
 s.poly([(x+21*z,y-8*z),(x+36*z,y-4*z),(x+21*z,y+1*z)],INK if shadow else '#e891a2')
 if not shadow:s.rect(x+44*z,y+45*z,13*z,20*z,'#ba935f')
 return pts

def pumpkin(s,x,y,k):
 s.ellipse(x,y,20,19,'#f4c17d');s.line(x,y-19,x+2,y-26,GREEN,3)
 if k%2:s.circle(x-7,y-4,3,INK,INK);s.circle(x+7,y-4,3,INK,INK)
 else:
  for dx in [-7,7]:s.poly([(x+dx-4,y-1),(x+dx,y-7),(x+dx+4,y-1)],INK)
 # Seven intentionally distinct mouth patterns; duplicate IDs reuse all geometry.
 s.line(x-11,y+7,x+11,y+7,INK,2)
 for j in range(k+1):s.rect(x-10+j*20/max(k,1),y+7,2,3,INK,INK)
 if k>=5:s.poly([(x+3,y-20),(x+13,y-26),(x+10,y-18)],GREEN)

def header(n):
 s=Scene();s.rect(0,0,W,H,'#ffffff','#ffffff')
 title=TITLES[n-1];size=min(13,300/max(stringWidth(title,'Helvetica',1),1));s.text(160,18,title,size,BLUE)
 lines=textwrap.wrap(TASKS[n-1],width=65)
 for j,t in enumerate(lines):s.text(160,34+j*11,t,8.6)
 return s

def ruin(s,x,y,z=1,changed=False):
 s.rect(x,y,140*z,93*z,'#f3f7ec','#9ab7aa');s.line(x,y+77*z,x+140*z,y+77*z,GREEN)
 # Base arch, and exactly one removable upper stone.
 for i in range(4):s.rect(x+(32+i*17)*z,y+31*z,16*z,13*z,'#c2bcb0')
 for dx in [32,83]:s.rect(x+dx*z,y+44*z,16*z,33*z,'#c2bcb0')
 if changed:s.rect(x+49*z,y+31*z,16*z,13*z,'#f3f7ec','#f3f7ec')
 s.circle(x+67*z,y+59*z,15*z,'#ded9cd')
 for i in range(12):star(s,x+(67+11*math.cos(i*math.tau/12))*z,y+(59+11*math.sin(i*math.tau/12))*z,1.7*z)
 s.line(x+18*z,y+19*z,x+18*z,y+55*z)
 if not changed:s.poly([(x+18*z,y+19*z),(x+32*z,y+23*z),(x+18*z,y+29*z)],'#e891a2')
 flower(s,x+20*z,y+68*z,'#77a8be' if changed else '#e891a2')
 s.ellipse(x+119*z,y+67*z,12*z,8*z,GREEN,GREEN)
 for dx in ([115,122,126] if changed else [115,122]):s.circle(x+dx*z,y+65*z,1.5*z,'#bc5b5b')
 if not changed:
  for dx in [100,105,110]:s.circle(x+dx*z,y+15*z,4*z,'#ffffff','#ffffff')
 # Bao from existing reference, not a new illustration.
 s.image_crop('characters/reference-images/01-character-reference-v02-accessories.png',(655,212,393,468),x+2*z,y+34*z,18*z,28*z)
 if changed:s.circle(x+28*z,y+49*z,3*z,'none',BLUE);s.line(x+30*z,y+51*z,x+34*z,y+55*z,BLUE)

def build(n):
 s=header(n);answer=None;proof={}
 if n==1:
  colors=['#5793bb','#a889b0','#8faa68','#b79564'];ends=[(284,90),(284,135),(284,195),(284,245)]
  s.text(18,72,'START',8,BLUE,'start')
  for j,(ex,ey) in enumerate(ends):
   pts=[(30,95+j*46),(95,95+j*40),(170,95+j*48),(260,ey)]
   for a,b in zip(pts,pts[1:]):
    for t in [i/8 for i in range(8)]:
     x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;s.ellipse(x,y,2+j*.3,3.5,colors[j],colors[j]);s.circle(x,y-4,1,colors[j],colors[j])
   s.text(15,101+j*46,'ABCD'[j],10)
  animal(s,'Rabbit',284,88,.65);s.rect(274,123,20,25,CREAM);s.poly([(270,123),(284,112),(298,123)],'#a889b0');star(s,284,195,16)
  s.circle(284,245,11,'#ffffff');s.circle(284,229,7,'#ffffff');s.line(276,225,292,225,BLUE,2)
  answer='Trail C';proof={'trails':4,'star_trail':'C','branching':False}
 elif n==2:
  ys=[90,140,190,240];targets=[2,0,3,1]
  for i,y in enumerate(ys):
   s.rect(10,y-10,26,18,CREAM);s.line(10,y-10,23,y,INK);s.line(36,y-10,23,y,INK);s.text(23,y-17,'ABCD'[i],10)
   dest=ys[targets[i]];s.bezier([(42,y),(115,y+(-16 if i%2 else 16)),(205,dest+(16 if i%2 else -16)),(273,dest)],INK,1.7)
  # Clear overpass at each curve intersection avoids ambiguous junctions.
  curves=[]
  for i,y in enumerate(ys):
   dest=ys[targets[i]];curves.append([(42,y),(115,y+(-16 if i%2 else 16)),(205,dest+(16 if i%2 else -16)),(273,dest)])
  def point(ps,t):return tuple(sum(ps[k][d]*[ (1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3][k] for k in range(4)) for d in range(2))
  for i in range(4):
   for j in range(i):
    last=point(curves[i],0)[1]-point(curves[j],0)[1]
    for step in range(1,501):
     t=step/500;v=point(curves[i],t)[1]-point(curves[j],t)[1]
     if last*v<0:
      lo=(step-1)/500;hi=t
      for _ in range(20):
       mid=(lo+hi)/2;vv=point(curves[i],mid)[1]-point(curves[j],mid)[1]
       if vv*last>0:lo=mid
       else:hi=mid
      tt=(lo+hi)/2;a=point(curves[i],tt-.025);b=point(curves[i],tt+.025);s.line(*a,*b,'#ffffff',5);s.line(*a,*b,INK,1.7)
     last=v
  for i,y in enumerate(ys):s.rect(278,y-13,28,24,'#e4f1f8');s.line(283,y-4,301,y-4);s.line(292,y+11,292,y+25);s.text(292,y-19,str(i+1),10)
  answer={'A':3,'B':1,'C':4,'D':2};proof={'curves':4,'branches':0,'mapping':answer}
 elif n==3:
  rows=[['sunflower','acorn','pumpkin']*2+['sunflower',None],['sprout','sprout','tulip']*2+['sprout','sprout',None]]
  for j,row in enumerate(rows):
   y=96+j*83;s.text(11,y,str(j+1),10)
   for i,k in enumerate(row):
    x=33+i*32
    if k:seed(s,k,x,y)
    else:s.rect(x-11,y-15,22,30,'#eef6f9');s.text(x,y+4,'?',14)
   opts=['pumpkin','sunflower','acorn','sprout'] if j==0 else ['sprout','tulip','acorn','pumpkin']
   for i,k in enumerate(opts):seed(s,k,65+i*57,y+40);s.text(65+i*57,y+64,'ABCD'[i],9)
  answer={'row1':'C — acorn','row2':'B — tulip'};proof={'periods':[3,3],'answers':['acorn','tulip']}
 elif n==4:
  types=[0,1,2,3,4,5,6,2,7,8];assert len(set(types))==9
  for i,k in enumerate(types):x=35+(i%5)*62;y=105+(i//5)*108;egg(s,x,y,k);s.text(x,y+40,'ABCDEFGHIJ'[i],10)
  answer=['C','H'];proof={'pattern_ids':types,'duplicate_pair':[2,7]}
 elif n==5:
  s.rect(8,63,304,204,'#edf5e9',GREEN);s.rect(226,96,25,150,'#cfaf83');s.ellipse(237,96,62,30,'#bad3a7',GREEN);s.ellipse(235,176,7,12,'#987855');s.line(15,240,304,240,GREEN)
  for i in range(15):flower(s,23+i*19,216-(i%3)*18)
  s.rect(63,232,43,23,'#dcb47c');s.bezier([(67,232),(65,204),(100,204),(103,232)])
  positions=[(40,87),(126,114),(198,91),(238,151),(271,213),(74,235),(159,211),(302,128)]
  for x,y in positions:butterfly(s,x,y,.8)
  answer={'count':8,'positions':positions};proof={'butterflies':8,'positions':positions}
 elif n==6:
  for i,name in enumerate(['Rabbit','Squirrel','Duck','Nibbles']):
   x=42+i*78
   if name=='Nibbles':s.image_crop('characters/reference-images/01-character-reference-v02-accessories.png',(1050,330,295,360),x-24,63,48,59);s.circle(x-11,89,7,'none','#45adae',1.5);s.circle(x+9,89,7,'none','#45adae',1.5)
   else:animal(s,name,x,90,.8)
   s.text(x,137,name,9)
  clues=['Clue 1: Small footprints were found beside the basket.','Clue 2: Whoever took the strawberries did not have wings.','Clue 3: A turquoise circle was found beside the empty basket.']
  for i,t in enumerate(clues):s.text(10,167+i*27,t,8.6,INK,'start')
  s.rect(100,242,40,20,'#dcb47c');s.circle(174,252,9,'none','#45adae',2);s.text(118,275,'Empty basket',8);s.text(197,275,'A turquoise circle',8)
  for xx,yy in [(148,252),(153,247),(158,252)]:s.ellipse(xx,yy,1.5,2,INK,INK)
  answer='Nibbles';proof={'suspects':['Rabbit','Squirrel','Duck','Nibbles'],'wings':[False,False,True,False],'turquoise_glasses':[False,False,False,True]}
 elif n==7:
  castle(s,109,68,1);s.text(160,151,'The sandcastle',9)
  variants=[1,2,0,3];geometries=[]
  for i,k in enumerate(variants):x=17+(i%2)*158;y=171+(i//2)*57;geometries.append(castle(s,x,y,.72,k,True));s.text(x+38,y+55,'ABCD'[i],10)
  assert geometries[2]!=geometries[0] and geometries[2]!=geometries[1] and geometries[2]!=geometries[3]
  answer='C';proof={'reference_variant':0,'options':variants,'exact_option':'C'}
 elif n==8:
  homes=['nest','den','tree hollow','burrow'];animals=['Owl','Rabbit','Squirrel','Fox']
  for i,name in enumerate(animals):y=86+i*51;animal(s,name,34,y,.57);s.text(67,y+7,name,9,INK,'start');s.circle(126,y+5,2,BLUE,BLUE)
  for i,name in enumerate(homes):
   y=86+i*51;s.circle(170,y+5,2,BLUE,BLUE)
   if name=='nest':s.line(214,y+8,245,y+8,GREEN,2);s.ellipse(229,y+3,15,6,'#ba9769');s.circle(230,y,2,'#cfaf83');s.ellipse(249,y+11,2,3,'#ba9769');s.ellipse(254,y+11,2,3,'#ba9769')
   elif name=='tree hollow':s.rect(219,y-15,20,36,'#cfaf83');s.ellipse(229,y,6,9,'#705f4c');s.line(245,y+8,251,y+3,BLUE)
   elif name=='burrow':s.ellipse(230,y+9,19,12,'#d7c3a7');s.ellipse(230,y+12,7,9,'#705f4c');s.line(207,y+15,211,y+5,GREEN,2);s.line(254,y+15,249,y+5,GREEN,2)
   else:s.poly([(211,y+15),(218,y-8),(241,y-8),(249,y+15)],'#d7c3a7');s.ellipse(230,y+6,7,9,'#705f4c');s.circle(249,y+16,2,'#b18d67')
   s.text(280,y+27,name,8)
  answer={'Owl':'tree hollow (3)','Rabbit':'burrow (4)','Squirrel':'nest (1)','Fox':'den (2)'};proof={'homes':homes,'mapping':[3,4,1,2]}
 elif n==9:
  ruin(s,76,63,1.2,False);ruin(s,76,174,1.2,True)
  answer=['flag missing','flower color','one arch stone missing','one extra berry','cloud missing','extra magnifying glass by Bao']
  proof={'differences':answer,'count':6,'mechanism_spaces':12,'mechanism_identical':True}
 elif n==10:
  ids=[0,1,2,5,3,1,4,0,4,2,6,3];assert sorted(ids.count(i) for i in set(ids))==[1,1,2,2,2,2,2]
  for i,k in enumerate(ids):x=43+(i%4)*78;y=88+(i//4)*80;pumpkin(s,x,y,k);s.text(x,y+31,'ABCDEFGHIJKL'[i],10)
  answer={'pairs':['A-H','B-F','C-J','E-L','G-I'],'unpaired':['D','K']};proof={'pattern_ids':ids,'pair_count':5,'unpaired':2}
 elif n==11:
  order=[2,0,3,1]
  for i,state in enumerate(order):
   x=10+(i%2)*156;y=65+(i//2)*103;s.rect(x,y,144,81,'#eef5f7',BLUE)
   if state in [0,1]:
    for dx in [35,63,90]:s.ellipse(x+dx,y+22,24,9,'#9caeb9')
   if state==1:
    for dx in range(20,140,17):s.line(x+dx,y+39,x+dx-7,y+56,BLUE);s.line(x+12,y+64,x+118,y+60,BLUE)
   if state in [2,3]:
    s.line(x+17,y+68,x+96,y+51,'#947253',5);s.line(x+68,y+57,x+79,y+41,'#947253',3);s.poly([(x+62,y+76),(x+100,y+60),(x+130,y+76)],'#cfaf83')
   if state==3:star(s,x+91,y+67,9);s.image_crop('characters/reference-images/01-character-reference-v02-accessories.png',(655,212,393,468),x+13,y+32,25,33)
   s.circle(x+72,y+92,8,'#ffffff',BLUE)
  s.text(160,278,'Write 1, 2, 3 and 4.',9)
  answer={'displayed_states':['C','A','D','B'],'write':[3,1,4,2]};proof={'chronological_states':[0,1,2,3],'displayed_states':order}
 elif n==12:
  pts=[(160+math.cos(-math.pi/2+i*math.pi/12)*(65 if i%2==0 else 37),130+math.sin(-math.pi/2+i*math.pi/12)*(65 if i%2==0 else 37)) for i in range(24)]
  s.poly(pts,GOLD,'#aa7b17');piece=[(160,130),pts[3],pts[4],pts[5]];s.poly(piece,'#ffffff',BLUE,1.2)
  local=[(x-160,y-130) for x,y in piece];opts=[]
  for i in range(4):
   p=[list(v) for v in local]
   if i==0:p[1][0]-=9
   if i==1:p[2][1]+=10
   if i==3:p[3][0]+=11
   opts.append(p);x=20+i*78;y=220;s.poly([(x+xx*.75,y+yy*.75) for xx,yy in p],GOLD,'#aa7b17');s.text(x+27,274,'ABCD'[i],10)
  assert opts[2]==[list(v) for v in local] and all(opts[i]!=opts[2] for i in [0,1,3])
  answer='C';proof={'star_points':12,'missing_polygon':local,'options':opts,'exact_option':'C'}
 return s,answer,proof

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--source',default='giggle_dumplings_2027_lower_pages_master_v2_illustrated.pdf');args=p.parse_args();out=(ROOT/args.output).resolve()
 assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 reg=json.loads((ROOT/'production/assets.json').read_text());rel=args.source;src=ROOT/rel
 assert hashlib.sha256(src.read_bytes()).hexdigest()==reg['assets'][rel]['sha256']
 reference='characters/reference-images/01-character-reference-v02-accessories.png'
 assert hashlib.sha256((ROOT/reference).read_bytes()).hexdigest()==reg['assets'][reference]['sha256']
 reader=PdfReader(src);recovered=len(reader.pages)==26;assert len(reader.pages) in [12,26]
 source_pages=[reader.pages[2+i*2] for i in range(12)] if recovered else reader.pages
 writer=PdfWriter();records=[]
 for n,page in enumerate(source_pages,1):
  s,answer,proof=build(n)
  raw=page.get_contents().get_data()
  if recovered:
   year_pattern=rb'BT 1 0 0 1 (164|185|206|227) 557\.2756 Tm (/F2\+0 25 Tf 30 TL \([2027]\) Tj T\* ET)'
   raw,count=re.subn(year_pattern,lambda m:b'BT 1 0 0 1 '+str(int(m.group(1))+41).encode()+b' 557.2756 Tm '+m.group(2),raw)
   assert count==4,(n,'year header layout changed')
  if recovered:
   if n==12:
    assert raw.count(b'\nQ\n\nq\n')==1
    raw=raw.split(b'\nQ\n\nq\n')[0]+b'\nQ\n'
   begins=list(re.finditer(rb'1 1 1 rg\n([^\n]+) RG\n1 w\nn\n491 100 m\n',raw))
   ends=list(re.finditer(rb'[^\n]+ rg\n[^\n]+ RG\n1 w\nn\n25 14 m\n',raw))
  else:
   begins=list(re.finditer(rb'1 1 1 rg\n([^\n]+) RG\n\.8 w\nn\n502 88 m\n',raw))
   ends=list(re.finditer(rb'[^\n]+ rg\n[^\n]+ RG\n\.8 w\nn\n501 15 m\n',raw))
  assert len(begins)==1 and len(ends)==1,(n,'source layout changed')
  a=begins[0].start();b=ends[0].start();assert a<b;removed=raw[a:b]
  rgb=[float(v) for v in begins[0].group(1).split()];season='#'+''.join(f'{round(v*255):02x}' for v in rgb)
  season_ink='#'+''.join(f'{round(v*255*.60):02x}' for v in rgb)
  s.ops=[(k,tuple(season_ink if v==BLUE else v for v in args)) for k,args in s.ops]
  (out/f'{n:02}-puzzle.svg').write_text(s.svg());(out/f'{n:02}-drawing.json').write_text(json.dumps(s.ops,ensure_ascii=False,indent=2)+'\n')
  new=raw[:a]+raw[b:];new=new.replace(b'BT /F1 8.5 Tf 10.2 TL ET',b'.141176 .27451 .352941 rg\nBT /F1 8.5 Tf 10.2 TL ET');stream=DecodedStreamObject();stream.set_data(new);page[NameObject('/Contents')]=stream
  mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(float(page.mediabox.width),float(page.mediabox.height)))
  c.setFillColor(HexColor('#ffffff'));c.setStrokeColor(HexColor(season));c.setLineWidth(.8)
  if recovered:c.roundRect(479,100,348.89,315.2756,12,fill=1,stroke=1);s.render(c,493,110,1)
  else:c.roundRect(492,88,335.89,305.2756,10,fill=1,stroke=1);s.render(c,500,94,1)
  c.save();mem.seek(0);page.merge_page(PdfReader(mem).pages[0]);writer.add_page(page)
  records.append({'month':n,'title':TITLES[n-1],'instruction':TASKS[n-1],'answer':answer,'construction':proof,'removed_old_puzzle_sha256':hashlib.sha256(removed).hexdigest(),'retained_source_operations_sha256':hashlib.sha256(new).hexdigest()})
 writer.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER - lower pages '+out.name,'/Subject':'Working master. Gelato print checks and user review pending.'})
 target=out/f'giggle-dumplings-2027-lower-pages-ARBEITSMASTER-{out.name}.pdf'
 with target.open('wb') as f:writer.write(f)
 (out/'manifest.json').write_text(json.dumps({'source':rel,'source_sha256':reg['assets'][rel]['sha256'],'source_layout':'recovered_26_page' if recovered else 'illustrated_lower_12_page','status':'working_master','user_review':'pending','gelato_print_review':'pending','months':records},indent=2,ensure_ascii=False)+'\n')
 print('12 SVGs + shared drawing data + working master created; logical checks passed.')
if __name__=='__main__':main()
