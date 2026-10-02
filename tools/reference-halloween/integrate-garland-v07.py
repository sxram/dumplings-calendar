"""Replace B08 with the approved language page; preserve all other pages."""
import sys
sys.dont_write_bytecode=True
import io,json,importlib.util,hashlib
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v07'
s=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py');ch=importlib.util.module_from_spec(s);s.loader.exec_module(ch)
r=json.loads((ROOT/'production/assets.json').read_text());err=ch.check(r)
if err:raise ValueError(err)
used={}
def asset(key):
 a=r['assets'][key];used[key]=a;return ROOT/a['path']
assert r['assets']['garland.sample.v01']['design_status']=='approved'
m=json.loads(asset('book.review.v06.manifest').read_text());plan=m['page_plan'];gi=next(i for i,p in enumerate(plan) if p['id']=='B08');assert plan[gi+1]['kind']=='blank'
assert len({p['id'] for p in plan if p['kind']=='coloring'})==sum(p['kind']=='coloring' for p in plan)==30
sample=PdfReader(asset('garland.sample.v01'));assert len(sample.pages)==3
assert not OUT.exists();OUT.mkdir(parents=True)
paint={b'Do',b'Tj',b'TJ',b"'",b'"',b'S',b's',b'f',b'F',b'f*',b'B',b'B*',b'b',b'b*',b'sh'}
def ops(p):
 c=p.get_contents();return c.operations if c else []
def streams(obj,path=''):
 obj=obj.get_object();out={}
 if hasattr(obj,'get_data'):out[path]=hashlib.sha256(obj.get_data()).hexdigest()
 for k,v in obj.get('/Resources',{}).get('/XObject',{}).items():out.update(streams(v,path+str(k)))
 return out
ed=[]
for li,lang in enumerate(('de','en','es')):
 src=PdfReader(asset('book.review.v06.'+lang));w=PdfWriter()
 for i,p in enumerate(src.pages):
  new=w.add_page(sample.pages[li] if i==gi else p)
  if i==gi:
   b=io.BytesIO();c=canvas.Canvas(b,pagesize=(504,720));c.setFont('Helvetica',8);c.drawRightString(462,15,str(plan[gi]['interior_page']));c.showPage();c.save();b.seek(0);new.merge_page(PdfReader(b).pages[0])
 w.add_metadata({'/Title':f'Giggle Dumplings Halloween {lang.upper()} - Sichtfassung v07','/Subject':'Freigegebene Girlande eingebaut; keine Druckfreigabe','/Author':'Stefan Marx'})
 dest=OUT/f'giggle-dumplings-halloween-{lang}-review-v07.pdf'
 with dest.open('xb') as f:w.write(f)
 out=PdfReader(dest);assert len(out.pages)==len(plan)==111
 for i,(a,b) in enumerate(zip(src.pages,out.pages)):
  assert tuple(a.mediabox)==tuple(b.mediabox)
  if i!=gi:
   assert ops(a)==ops(b);assert a.extract_text()==b.extract_text();assert streams(a)==streams(b)
  else:
   assert sample.pages[li].extract_text().strip() in b.extract_text();assert streams(sample.pages[li])==streams(b)
  if plan[i]['kind']=='blank':assert not any(op in paint for _,op in ops(b))
 ed.append({'language':lang,'path':str(dest.relative_to(ROOT)),'sha256':ch.digest(dest),'changed_pdf_pages':[gi+1]})
 print(lang,'all 110 other pages unchanged; blank backs, sources and page plan checked')
m={'status':'review_draft','upload_ready':False,'interior_pages':len(plan)-1,'review_pages':len(plan),'page_plan':plan,'sources':used,'editions':ed,'checks':{'coloring_unique':30,'blank_backs':'passed','unaffected_page_content_text_and_nested_images':'identical','garland_sources':'identical to approved sample','physical_paper_test':'open'},'visual_review':'pending','print_release':False}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
