"""Page-specific draft-label masks and shorter lower joke bubbles."""
from pathlib import Path
import io,json,hashlib
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,FloatObject
from reportlab.pdfgen import canvas
R=Path(__file__).resolve().parents[1]
src=R/'05-kdp/upload/interior-de-v09/Giggle-Dumplings-Halloween-DE-Innenbuch-v09.pdf'
clean=R/'05-kdp/upload/de-2026-09-30-v05/Giggle-Dumplings-Halloween-DE-Innenbuch.pdf'
O=R/'05-kdp/upload/interior-de-v10';O.mkdir(exist_ok=True)
r=PdfReader(src);old=PdfReader(clean);w=PdfWriter()
puzzles=[13,29,41,53,65,81,97,105]
boxes={13:(503,87.5,24,8),41:(484,71,34,14),53:(484,71,34,14),65:(459,72,59,26),81:(491,62,34,11),97:(500,58,27,8.5),105:(496,61,29,12)}
def mask(p,rects):
 b=io.BytesIO();c=canvas.Canvas(b,pagesize=(612,792));c.setFillGray(1)
 for box in rects:c.rect(*box,fill=1,stroke=0)
 c.save();b.seek(0);p.merge_page(PdfReader(b).pages[0])
for num,p in enumerate(r.pages,1):
 if num in puzzles:
  cs=p.get_contents();ops=cs.operations;out=[];i=0;removed=0
  while i<len(ops):
   a,o=ops[i]
   if o==b're' and list(map(float,a))==[5050.,840.,550.,200.]:
    assert ops[i+1][1] in [b'f',b'f*'];i+=2;removed+=1;continue
   out.append((a,o));i+=1
  assert removed==1,(num,removed)
  cs.operations=out;p[NameObject('/Contents')]=cs
  if num in boxes:mask(p,[boxes[num]])
 if num in [23,45,67,87]:
  cs=p.get_contents();ops=cs.operations
  start=next(i for i,(a,o) in enumerate(ops) if o==b'm' and list(map(float,a))==[959.,495.])
  # Raise only bottom edge and bottom corner control points by 26.5 pt.
  for a,o in ops[start:start+9]:
   assert o in [b'm',b'l',b'c']
   for j in range(1,len(a),2):
    if float(a[j])<=671:a[j]=FloatObject(float(a[j])+265)
  cs.operations=ops;p[NameObject('/Contents')]=cs
 if num in [127,128]:
  p=old.pages[num-1];rects=[]
  for i in range(4):
   original=puzzles[(num-127)*4+i]
   if original not in boxes:continue
   x,y,ww,hh=boxes[original];tx=48+(i%2)*270;ty=414-(i//2)*354
   rects.append((tx+(x-28.8)/1.1*.48,ty+y/1.1*.48,ww/1.1*.48,hh/1.1*.48))
  mask(p,rects)
 w.add_page(p)
out=O/'Giggle-Dumplings-Halloween-DE-Innenbuch-v10.pdf';w.write(out)
assert len(PdfReader(out).pages)==128
manifest={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'clean_solution_source':str(clean.relative_to(R)),'clean_solution_sha256':hashlib.sha256(clean.read_bytes()).hexdigest(),'draft_masks_page_points':boxes,'bubble_pages':[23,45,67,87],'bubble_bottom_pt':76,'footer_rule_pt':49.2,'pages':128,'user_review':'pending','kdp_preview':'pending'}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
rp=R/'production/assets.json';reg=json.loads(rp.read_text())
for f in [out,O/'manifest.json']:
 k='interior.details.v10.'+f.suffix[1:]
 reg['assets'][k]={'path':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'role':'export','usage':'Kleinere untere Sprechblasen und individuelle Entwurfsvermerk-Korrektur','design_status':'review_pending','print_status':'not_released','issues':['Nutzerreview und KDP-Vorschau offen'],'origin':{'project':'dumplings-halloween','source':manifest['source']}}
reg['selection']['current_kdp_interior_de']='interior.details.v10.pdf';rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(out)
