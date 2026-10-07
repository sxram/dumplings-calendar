import io,json,copy,calendar
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image
import numpy as np
root=Path('/Users/stefan.marx/Documents/privat/dumplings-calendar');tmp=root/'tmp/pdfs/v32'
r=PdfReader(tmp/'candidate.pdf');w=PdfWriter(clone_from=r);review=PdfWriter();j=json.loads((root/'production/typography/v29/manifest.json').read_text());report=[]
pdfmetrics.registerFont(TTFont('DateFixed','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
for m in range(1,13):
 p=w.pages[2*m];cs=ContentStream(p.get_contents(),w);drop=set();found=[]
 for i,(a,o) in enumerate(cs.operations):
  if o!=b'BT':continue
  k=i+1
  while k<len(cs.operations) and cs.operations[k][1]!=b'ET':k+=1
  ts=[str(a[0]) for a,o in cs.operations[i:k] if o==b'Tj']
  if len(ts)!=1 or not ts[0].isdigit():continue
  mat=None
  for q in range(i-1,max(-1,i-5),-1):
   if cs.operations[q][1]==b'cm':mat=cs.operations[q][0];break
  if mat is None or not(0<float(mat[4])<840 and 400<float(mat[5])<800):continue
  found.append(int(ts[0]));drop.update(range(i,k+1))
 assert sorted(found)==list(range(1,calendar.monthrange(2027,m)[1]+1)),(m,found)
 cs.operations=[v for i,v in enumerate(cs.operations) if i not in drop];p.replace_contents(cs)
 mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(1492,1054));dates=[v for v in j['months'][m-1]['lines'] if v['kind']=='calendar']
 source=np.asarray(Image.open(root/f'tmp/pdfs/typography-v29/before-{m:02d}.png').convert('RGB'))
 grid={};first=calendar.monthrange(2027,m)[0]
 for d in dates:
  col=(first+int(d['text'])-1)%7
  if col in grid:continue
  gx,gy,_,_=d['box'];candidates=list(range(max(0,int(gx)-16),int(gx)+1));scores=[]
  for cx in candidates:
   strip=source[int(gy)+27:int(gy)+40,cx].astype(float)
   contrast=2*strip[:,0]-strip[:,1]-strip[:,2] if m==2 else (2*strip[:,1]-strip[:,0]-strip[:,2] if m in [3,4,5] else strip[:,1]+strip[:,2]-2*strip[:,0])
   scores.append(np.maximum(0,contrast).sum())
  cx=candidates[int(np.argmax(scores))];grid[col]=(cx,np.median(source[int(gy)+27:int(gy)+40,cx],axis=0)/255)
 size=29 if m<=5 else 25
 for d in dates:
  x,y,x1,y1=d['box'];day=d['text'];shift=12 if m<=5 else 10
  # Restore paper tone inside the former numeral area, away from the grid edge.
  sample=source[int(y+3):int(y1),int(x1+5):int(x1+15)]
  bright=sample.reshape(-1,3);bright=bright[np.min(bright,axis=1)>225]
  color=np.median(bright,axis=0)/255 if len(bright) else np.array([.97,.974,.974])
  c.setFillColorRGB(*color);c.rect(x-1,1054-y1-2,max(x1-x+2,20),y1-y+4,fill=1,stroke=0)
  col=(first+int(day)-1)%7;gx,gcolor=grid[col]
  c.setStrokeColorRGB(*gcolor);c.setLineWidth(.8);c.line(gx,1054-y1-7,gx,1054-y+7)
  c.setFillColor(HexColor('#173e59'));c.setFont('DateFixed',size)
  # Fixed font metrics give all digits the same height and natural spacing.
  c.drawString(x+shift,1054-y-size*.73,day)
 c.save();mem.seek(0);overlay=PdfReader(mem).pages[0];overlay.scale_to(float(p.mediabox.width),float(p.mediabox.height));p.merge_page(overlay);review.add_page(copy.deepcopy(p));report.append({'month':m,'count':len(found),'font_size':size,'horizontal_offset':12 if m<=5 else 10})
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v32','/Subject':'Consistent native body text and calendar numerals; user review and print checks pending.'})
with (tmp/'candidate-dates.pdf').open('wb') as f:w.write(f)
with (tmp/'backs.pdf').open('wb') as f:review.write(f)
manifest=json.loads((root/'production/typography/v32/manifest.json').read_text());manifest['calendar']=report;(root/'production/typography/v32/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('365 uniform numerals rebuilt from checked 2027 geometry')
