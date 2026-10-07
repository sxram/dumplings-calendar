"""Repair legacy per-word fitted PDF text using consistent natural font sizes."""
import io,json,math,struct,statistics,hashlib,copy
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[1];PW,PH=1492,1054
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v31.pdf'
COMP=ROOT/'production/typography/v32';COMP.mkdir(parents=True,exist_ok=True)
TMP=ROOT/'tmp/pdfs/v32';TMP.mkdir(parents=True,exist_ok=True)
reg=json.loads((ROOT/'production/assets.json').read_text());assert hashlib.sha256((ROOT/BASE).read_bytes()).hexdigest()==reg['assets'][BASE]['sha256']
f=TTFont('BodyFixed','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0);pdfmetrics.registerFont(f);face=f.face;glyf=face.get_table('glyf');em=face.unitsPerEm

pdfmetrics.registerFont(TTFont('BodyNatural','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))

def bounds(s):
 pos=0;bs=[]
 for ch in s:
  g=face.charToGlyph.get(ord(ch),0);a=face.glyphPos[g];b=face.glyphPos[g+1]
  if b>a:
   _,x0,y0,x1,y1=struct.unpack('>hhhhh',glyf[a:a+10]);bs.append((pos+x0,y0,pos+x1,y1))
  pos+=face.charWidths.get(ord(ch),face.defaultWidth)*em/1000
 return [min(v[0] for v in bs),min(v[1] for v in bs),max(v[2] for v in bs),max(v[3] for v in bs)] if bs else [0,0,0,0]

def column(m,x,y):
 # Keep the distinct illustrated panels, date columns, footer facts and right-hand wooden signs separate.
 if y>926:
  if x>1300:return 'footer-sign'
  return 'footer-left' if x<760 else 'footer-right'
 if x<750:
  if y>620:return 'job' if x<(490 if m<=5 else 475) else 'challenge'
  return 'calendar'
 if x>1360 and y<640:return 'small-right-sign'
 return 'story' if y<(435 if m<=5 else 250) else 'puzzle'

r=PdfReader(ROOT/BASE);w=PdfWriter(clone_from=r);rv=PdfWriter();records=[]
for m in range(1,13):
 page=w.pages[2*m];cs=ContentStream(page.get_contents(),w);blocks=[]
 for i,(args,op) in enumerate(cs.operations):
  if op!=b'BT':continue
  j=i+1
  while j<len(cs.operations) and cs.operations[j][1]!=b'ET':j+=1
  ops=cs.operations[i:j];ts=[str(a[0]) for a,o in ops if o==b'Tj'];tm=[a for a,o in ops if o==b'Tm'];tf=[a for a,o in ops if o==b'Tf']
  if len(ts)!=1 or not tf or not tm or list(tm[0])!=[1,0,0,1,0,0]:continue
  mat=None
  for k in range(i-1,max(-1,i-5),-1):
   if cs.operations[k][1]==b'cm':mat=cs.operations[k][0];break
  if mat is None:continue
  text=ts[0];x=float(mat[4]);base=float(mat[5]);size=float(tf[-1][1]);scale=float(mat[0]);b=bounds(text)
  bb=[x+b[0]*size*scale/em,PH-base-b[3]*size/em,x+b[2]*size*scale/em,PH-base-b[1]*size/em]
  if text in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:continue
  if text.isdigit() and bb[0]<840 and 245<bb[1]<640:continue
  col=column(m,bb[0],bb[1])
  blocks.append({'text':text,'box':bb,'base':base,'font_size':size,'scale':scale,'range':list(range(i,j+1)),'column':col})
 # Form genuine text lines with a common baseline; never fit each word independently.
 groups=[]
 for b in sorted(blocks,key=lambda z:(z['column'],round(z['box'][1]/5)*5,z['box'][0])):
  possible=[g for g in groups if g['column']==b['column'] and abs(statistics.median(v['box'][1] for v in g['words'])-b['box'][1])<5 and abs(g['words'][-1]['box'][2]-b['box'][0])<45]
  if possible:possible[-1]['words'].append(b)
  else:groups.append({'column':b['column'],'words':[b]})
 drop=set();layouts=[];mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH))
 for g in groups:
  words=sorted(g['words'],key=lambda b:b['box'][0]);s=' '.join(v['text'] for v in words).replace('tind the tweltth','find the twelfth');x=min(v['box'][0] for v in words);right=max(v['box'][2] for v in words);h=statistics.median(v['box'][3]-v['box'][1] for v in words);base=statistics.median(v['base'] for v in words)
  # Single large display headings have no per-word size bug and retain their established artwork layout.
  if g['column']=='puzzle':continue
  if h>35 or "Job This Month" in s or s in ['Special Delivery','Seed Trail','Who Took the','Strawberries?','Find the Differences','Pumpkin Pairs','Storm Story','The Missing Piece','Sandcastle Shadows','Woodland Homes','Egg Hunt','Butterfly Search']:continue
  target=26
  width=pdfmetrics.stringWidth(s,'BodyNatural',target)
  # Preserve a line's available space; report exceptional lines for a deliberate paragraph repair.
  overshoot=width-(right-x)
  layouts.append({'text':s,'x':x,'baseline':base,'font_size':target,'column':g['column'],'old_width':right-x,'new_width':width,'overshoot':overshoot,'old_sizes':[v['font_size'] for v in words],'word_count':len(words)})
  for v in words:drop.update(v['range'])

 # One size for all body letters; preserve each original line's layout as a whole.
 for v in layouts:
  target=24 if v['column'] in ['story','job','challenge'] else (20 if v['column'] in ['footer-left','footer-right'] else 22)
  natural=pdfmetrics.stringWidth(v['text'],'BodyNatural',target)
  scale=v['old_width']/natural
  v['font_size']=target;v['horizontal_scale']=scale;v['new_width']=v['old_width']
  c.saveState();c.setFillColor(HexColor('#173e59'));c.translate(v['x'],v['baseline']);c.scale(scale,1);c.setFont('BodyNatural',target);c.drawString(0,0,v['text']);c.restoreState()
 cs.operations=[v for k,v in enumerate(cs.operations) if k not in drop];page.replace_contents(cs)
 c.save();mem.seek(0);o=PdfReader(mem).pages[0];o.scale_to(float(page.mediabox.width),float(page.mediabox.height));page.merge_page(o);rv.add_page(copy.deepcopy(page));records.append({'month':m,'lines':layouts,'visual_review':'pending'})
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v32 candidate','/Subject':'Working candidate: legacy per-word body text normalized; calendar correction pending.'})
with (TMP/'candidate.pdf').open('wb') as f:w.write(f)
with (TMP/'backs.pdf').open('wb') as f:rv.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'months':records,'visual_review':'pending','user_review':'pending','print_status':'not_released'},indent=2)+'\n')
print('Body-font candidate staged; layout review required.')
for v in records:
 bad=[q for q in v['lines'] if q['overshoot']>25];print(v['month'],[(q['text'],round(q['overshoot'])) for q in bad])
