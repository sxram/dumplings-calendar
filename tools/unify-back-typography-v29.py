"""Unify visible text using native PDF type. Originals remain unmodified."""
import json,io,math,struct,hashlib,re,calendar
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color,HexColor
ROOT=Path(__file__).resolve().parents[1];COMP=ROOT/'production/typography/v29';PW,PH=1492,1054;INK='#173e59'
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v28.pdf'
reg=json.loads((ROOT/'production/assets.json').read_text());assert hashlib.sha256((ROOT/BASE).read_bytes()).hexdigest()==reg['assets'][BASE]['sha256']
font=TTFont('Unified','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0);pdfmetrics.registerFont(font);face=font.face;glyf=face.get_table('glyf');em=face.unitsPerEm

def metrics(s):
 pos=0;bounds=[]
 for ch in s:
  g=face.charToGlyph.get(ord(ch),0);off=face.glyphPos[g];end=face.glyphPos[g+1]
  if end>off:
   n,x0,y0,x1,y1=struct.unpack('>hhhhh',glyf[off:off+10]);bounds.append((pos+x0,y0,pos+x1,y1))
  pos+=face.charWidths.get(ord(ch),face.defaultWidth)*em/1000
 if not bounds:return [0,0,pos,em*.7]
 return [min(x[0] for x in bounds),min(x[1] for x in bounds),max(x[2] for x in bounds),max(x[3] for x in bounds)]

def type_line(c,s,b):
 x0,y0,x1,y1=b;m=metrics(s);size=(y1-y0)*em/max(1,m[3]-m[1]);scale=(x1-x0)*em/max(1,m[2]-m[0])/size
 c.saveState();c.setFillColor(HexColor(INK));c.translate(x0-m[0]*size/em*scale,PH-y1-m[1]*size/em);c.scale(scale,1);c.setFont('Unified',size);c.drawString(0,0,s);c.restoreState()

def erase_ink(c,pix,b,sx,sy):
 x0=max(0,int(b[0]/sx)-2);y0=max(0,int(b[1]/sy)-2);x1=min(pix.shape[1],int(math.ceil(b[2]/sx))+2);y1=min(pix.shape[0],int(math.ceil(b[3]/sy))+2)
 a=pix[y0:y1,x0:x1,:3].astype(float);lum=a.mean(2);bright=a[lum>=np.percentile(lum,70)]
 if not len(bright):return
 bg=np.median(bright,axis=0);threshold=bg.mean()-42;mask=lum<threshold
 # Expand only glyph-shaped regions, never a rectangular panel.
 mm=mask.copy()
 for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:mm|=np.roll(mask,(dy,dx),(0,1))
 c.setFillColor(Color(*(bg/255)));p=c.beginPath();runs=0
 for row in range(mm.shape[0]):
  changes=np.diff(np.pad(mm[row].astype(int),(1,1)));starts=np.flatnonzero(changes==1);ends=np.flatnonzero(changes==-1)
  for st,en in zip(starts,ends):p.rect((x0+st)*sx,PH-(y0+row+1)*sy,(en-st)*sx,sy);runs+=1
 c.drawPath(p,fill=1,stroke=0)
 return runs

def recolor_wordmark(c,pix,b,sx,sy):
 x0=max(0,int(b[0]/sx)-5);y0=max(0,int(b[1]/sy)-5);x1=min(pix.shape[1],int(b[2]/sx)+6);y1=min(pix.shape[0],int(b[3]/sy)+6)
 a=pix[y0:y1,x0:x1,:3].astype(float);lum=a.mean(2);mask=lum<215
 todo=set(map(tuple,np.argwhere(mask)));kept=np.zeros_like(mask)
 while todo:
  seed=todo.pop();queue=[seed];comp=[seed];touch=False
  while queue:
   yy,xx=queue.pop();touch|=yy in [0,mask.shape[0]-1] or xx in [0,mask.shape[1]-1]
   for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
    q=(yy+dy,xx+dx)
    if q in todo:todo.remove(q);queue.append(q);comp.append(q)
  if not touch and len(comp)>35 and max(q[0] for q in comp)-min(q[0] for q in comp)>(y1-y0)*.4:
   for yy,xx in comp:kept[yy,xx]=True
 edges={}
 def edge(a,b):edges.setdefault(a,[]).append(b)
 for yy,xx in np.argwhere(kept):
  if yy==0 or not kept[yy-1,xx]:edge((xx,yy),(xx+1,yy))
  if xx==kept.shape[1]-1 or not kept[yy,xx+1]:edge((xx+1,yy),(xx+1,yy+1))
  if yy==kept.shape[0]-1 or not kept[yy+1,xx]:edge((xx+1,yy+1),(xx,yy+1))
  if xx==0 or not kept[yy,xx-1]:edge((xx,yy+1),(xx,yy))
 p=c.beginPath()
 while edges:
  start=next(iter(edges));q=start;pts=[q]
  while True:
   nxt=edges[q].pop()
   if not edges[q]:del edges[q]
   q=nxt
   if q==start:break
   pts.append(q)
   if q not in edges:break
  if len(pts)<4:continue
  simplified=[]
  for i,q in enumerate(pts):
   a=pts[i-1];z=pts[(i+1)%len(pts)]
   if (q[0]-a[0])*(z[1]-q[1])!=(q[1]-a[1])*(z[0]-q[0]):simplified.append(q)
  if len(simplified)<3:continue
  q=simplified[0];p.moveTo((x0+q[0])*sx,PH-(y0+q[1])*sy)
  for q in simplified[1:]:p.lineTo((x0+q[0])*sx,PH-(y0+q[1])*sy)
  p.close()
 c.setFillColor(HexColor(INK));c.drawPath(p,fill=1,stroke=0,fillMode=0)
 return int(kept.sum())

# Explicitly bounded patches for the six main June Dumplings, as clarified by user.
PATCHES=[[(208,61),(346,60),(381,117),(387,192),(356,230),(302,247),(185,237),(175,166),(187,112)],[(59,747),(196,728),(231,786),(226,871),(184,909),(77,905),(38,848),(48,784)],[(799,456),(875,440),(918,480),(946,552),(932,596),(880,615),(821,616),(775,572),(774,521)],[(940,435),(1002,433),(1061,452),(1091,521),(1071,570),(1025,585),(960,579),(921,527),(920,478)],[(1093,438),(1164,430),(1211,476),(1216,536),(1192,570),(1131,575),(1072,554),(1057,511),(1067,463)],[(1240,480),(1311,462),(1362,497),(1368,554),(1322,587),(1255,587),(1220,552),(1211,515)]]

def june_patches(c):
 for pts in PATCHES:
  c.saveState();p=c.beginPath();p.moveTo(pts[0][0],PH-pts[0][1])
  for x,y in pts[1:]:p.lineTo(x,PH-y)
  p.close();c.clipPath(p,stroke=0);c.drawImage(str(COMP/'june-six-smooth-source.png'),0,0,PW,PH);c.restoreState()

raw=json.loads(Path('/tmp/calendar-all-ocr.json').read_text());(COMP/'ocr-input.json').write_text(json.dumps(raw,indent=2)+'\n')
b=PdfReader(ROOT/BASE);pdf=pdfplumber.open(ROOT/BASE);w=PdfWriter();records=[]
for month,r in enumerate(raw,1):
 page=b.pages[2*month];pl=pdf.pages[2*month];im=Image.open(ROOT/r['path']).convert('RGB');pix=np.asarray(im);sx=PW/im.width;sy=PH/im.height
 ocr=[{'text':v['text'],'box':[v['box'][0]*sx,v['box'][1]*sy,v['box'][2]*sx,v['box'][3]*sy]} for v in r['lines']]
 native=[{'text':v['text'],'box':[v['x0']*PW/float(page.mediabox.width),v['top']*PH/float(page.mediabox.height),v['x1']*PW/float(page.mediabox.width),v['bottom']*PH/float(page.mediabox.height)]} for v in pl.extract_words()]
 # Remove actual native BT/ET objects before their unified replacements.
 stream=ContentStream(page.get_contents(),b);ops=[];inside=False
 for args,op in stream.operations:
  if op==b'BT':inside=True
  if not inside:ops.append((args,op))
  if op==b'ET':inside=False
 stream.operations=ops;page.replace_contents(stream)
 nums=[v for v in ocr if v['text'].isdigit() and 1<=int(v['text'])<=31 and v['box'][0]<820 and 245<v['box'][1]<615]
 first=calendar.weekday(2027,month,1);samples=[]
 for v in nums:
  day=int(v['text']);row,col=divmod(first+day-1,7);samples.append((row,col,v['box'][0],v['box'][1],v['box'][3]-v['box'][1]))
 xs=np.linalg.lstsq(np.array([[1,v[1]] for v in samples]),np.array([v[2] for v in samples]),rcond=None)[0];ys=np.linalg.lstsq(np.array([[1,v[0]] for v in samples]),np.array([v[3] for v in samples]),rcond=None)[0];nh=float(np.median([v[4] for v in samples]))
 lines=[]
 tracker_boxes={1:(850,115,1440,180),2:(850,155,1440,210),3:(884,175,1372,216),4:(837,166,1222,208),5:(816,132,1227,179),6:(839,75,1421,118),7:(826,75,1419,117),8:(888,79,1416,123),9:(862,72,1420,114),10:(857,71,1424,114),11:(871,73,1423,115),12:(918,56,1442,99)}
 for v in ocr:
  bb=v['box'];s=v['text']
  tr=tracker_boxes[month]
  if tr[0]<(bb[0]+bb[2])/2<tr[2] and tr[1]<(bb[1]+bb[3])/2<tr[3]:continue
  if v in nums:continue
  if month==10 and s=='ENE':continue
  if any(ch in s for ch in ['≤','ư','«']):
   if month==2 and bb[1]>550:s='A';bb=[918,572,941,600]
   else:continue
  if month==2 and bb[0]>1350 and 550<bb[1]<930:continue
  if month==3 and bb[0]>920 and 518<bb[1]<830:continue
  if any(bb[0]-3<=sum(n['box'][::2])/2<=bb[2]+3 and bb[1]-3<=(n['box'][1]+n['box'][3])/2<=bb[3]+3 for n in native):continue
  s=re.sub(r'Gi[qg]{1,3}le','Giggle',s).replace('uin the past','in the past').replace('canbe','can be')
  if s=='O Did you know?':s='Did you know?'
  if s=='butteet':continue
  kind='wordmark' if bb[1]<310 and bb[3]-bb[1]>40 and ('2027' in s or calendar.month_name[month] in s) else 'source_raster'
  original_box=list(bb)
  if 'Did you know?' in s:bb[2]=min(bb[2],290)
  lines.append({'text':s,'box':bb,'kind':kind,'source_erase_box':original_box})
 if month in [2,4,5]:
  fb={2:[524,278,579,306],4:[496,278,546,304],5:[489,278,540,304]}[month]
  lines.append({'text':'Friday','box':fb,'kind':'source_raster'})
 if month==2:
  lines.extend([{'text':'Sunday','box':[760,279,820,305],'kind':'source_raster'},{'text':'Stronger','box':[1372,176,1464,197],'kind':'source_raster'},{'text':'Friends','box':[1382,198,1456,220],'kind':'source_raster'}])
  lines.append({'text':'C','box':[920,733,943,760],'kind':'source_raster','source_erase_box':[914,724,952,765]})
  for k,yy in enumerate([569,647,725,803]):lines.append({'text':str(k+1),'box':[1414,yy,1439,yy+31],'kind':'source_raster'})
 if month==11:lines.append({'text':'Put the Storm Story in Order!','box':[832,649,1214,684],'kind':'source_raster','source_erase_box':[829,644,1217,693]})
 for n in native:
  if month==2 and n['text'].isdigit() and n['box'][0]>1350 and 550<n['box'][1]<930:continue
  if n['text'].isdigit() and n['box'][0]<820 and 245<n['box'][1]<615:continue
  lines.append(dict(n,kind='native'))
 for day in range(1,calendar.monthrange(2027,month)[1]+1):
  row,col=divmod(first+day-1,7);x=xs[0]+xs[1]*col;y=ys[0]+ys[1]*row;s=str(day);m=metrics(s);width=nh*(m[2]-m[0])/(m[3]-m[1]);lines.append({'text':s,'box':[float(x),float(y),float(x+width),float(y+nh)],'kind':'calendar','erase_box':[float(x-6),float(y-5),float(x+width+13),float(y+nh+6)]})
 # OCR boxes for slanted lettering can include several baselines; fit native type to actual line spacing.
 for v in lines:
  if v['kind'] in ['calendar','wordmark']:continue
  bb=v['box'];v['erase_box']=v.get('source_erase_box',list(bb));h=bb[3]-bb[1]
  overlaps=[q['box'][1]-bb[1] for q in lines if q is not v and q['box'][1]>bb[1]+7 and min(bb[2],q['box'][2])-max(bb[0],q['box'][0])>min(bb[2]-bb[0],q['box'][2]-q['box'][0])*.55]
  cap=min(overlaps)-3 if overlaps else h
  if bb[1]>780 and len(v['text'])>7:cap=min(cap,22)
  if cap<h:bb[3]=bb[1]+max(13,cap)
 mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH))
 if month==6:june_patches(c)
 for v in nums:erase_ink(c,pix,[v['box'][0]-3,v['box'][1]-3,v['box'][2]+3,v['box'][3]+3],sx,sy)
 for v in lines:
  if v['kind']!='wordmark':erase_ink(c,pix,v.get('erase_box',v['box']),sx,sy)
 for v in lines:
  if v['kind']=='wordmark':recolor_wordmark(c,pix,v['box'],sx,sy)
  else:type_line(c,v['text'],v['box'])
 if month==4:
  c.setFillColor(HexColor(INK));c.circle(361,PH-196,9.5,fill=1,stroke=0)
 c.save();mem.seek(0);over=PdfReader(mem).pages[0];over.scale_to(float(page.mediabox.width),float(page.mediabox.height));page.merge_page(over);w.add_page(page)
 records.append({'month':month,'ink':INK,'font':'ChalkboardSE regular, embedded native PDF','lines':lines,'calendar_fit':[xs.tolist(),ys.tolist()],'calendar_day_count':calendar.monthrange(2027,month)[1],'visual_review':'pending','user_review':'pending'})
w.add_metadata({'/Title':'Giggle Dumplings - unified native back typography REVIEW v29','/Subject':'Working candidate. All back text one ink and embedded vector type. Six main June dumplings locally smoothed.'})
with (ROOT/'tmp/pdfs/typography-v29/candidate.pdf').open('wb') as f:w.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'months':records,'june_character_clip_polygons':PATCHES,'image_generation_calls':1,'visual_review':'pending','user_review':'pending','print_status':'not_released'},indent=2)+'\n')
print('12 candidate backs staged; OCR/native wording and calendar placement require visual review.')
