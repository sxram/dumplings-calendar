"""Shift only native date text January-May; no raster edits or re-generation."""
import json,hashlib,calendar
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,FloatObject
ROOT=Path(__file__).resolve().parents[1]
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v29.pdf'
OUT='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v30.pdf'
registry=json.loads((ROOT/'production/assets.json').read_text())
assert hashlib.sha256((ROOT/BASE).read_bytes()).hexdigest()==registry['assets'][BASE]['sha256']
assert not (ROOT/OUT).exists()
r=PdfReader(ROOT/BASE);w=PdfWriter(clone_from=r);changes=[]
for month in range(1,6):
 page=w.pages[month*2];cs=ContentStream(page.get_contents(),w);changed=[]
 for i,(args,op) in enumerate(cs.operations):
  if op!=b'Tj' or not str(args[0]).isdigit():continue
  day=int(str(args[0]));ci=i-5
  if ci<0:continue
  mat,oper=cs.operations[ci]
  if oper!=b'cm' or len(mat)!=6 or list(mat[:4])!=[1,0,0,1]:continue
  if not (0<float(mat[4])<820 and 400<float(mat[5])<800):continue
  before=float(mat[4]);mat[4]=FloatObject(before+22)
  changed.append({'day':day,'operation':ci,'x_before':before,'x_after':before+22})
 assert [v['day'] for v in changed]==list(range(1,calendar.monthrange(2027,month)[1]+1)),(month,changed)
 page.replace_contents(cs);changes.append({'month':month,'dates':changed})
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v30','/Subject':'Only January-May date numbers moved 22 design units right; review pending, not print released.'})
with (ROOT/OUT).open('wb') as f:w.write(f)
new=PdfReader(ROOT/OUT)
for i in range(26):
 oldcs=ContentStream(r.pages[i].get_contents(),r);newcs=ContentStream(new.pages[i].get_contents(),new)
 if i not in range(2,11,2):assert oldcs.get_data()==newcs.get_data(),i
 else:
  assert len(oldcs.operations)==len(newcs.operations)
  expected={v['operation'] for v in changes[i//2-1]['dates']}
  for k,((a,op),(b,bop)) in enumerate(zip(oldcs.operations,newcs.operations)):
   assert op==bop
   if k in expected:assert a[:4]==b[:4] and a[5]==b[5] and abs(float(b[4])-float(a[4])-22)<.001
   else:assert a==b,(i,k)
 for key,value in r.pages[i]['/Resources'].get('/XObject',{}).items():
  assert value.get_object().get_data()==new.pages[i]['/Resources']['/XObject'][key].get_object().get_data()
comp=ROOT/'production/calendar-dates/v30';comp.mkdir(parents=True,exist_ok=True)
(comp/'manifest.json').write_text(json.dumps({'base':BASE,'output':OUT,'offset_design_units':22,'offset_mm':22*841.89/1492*25.4/72,'changed_pages':[3,5,7,9,11],'unchanged_pages':21,'change_count':sum(len(m['dates']) for m in changes),'months':changes,'visual_review':'pending','user_review':'pending','print_status':'not_released'},indent=2)+'\n')
print('151 date placements shifted; other content and all image data unchanged.')
