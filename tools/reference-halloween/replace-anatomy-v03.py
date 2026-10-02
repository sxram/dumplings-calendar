"""Replace only registered illustration XObjects; preserve page streams and text."""
import sys
sys.dont_write_bytecode=True
import json,io,hashlib,importlib.util
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,NameObject
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v03'
spec=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py');ch=importlib.util.module_from_spec(spec);spec.loader.exec_module(ch)
r=json.loads((ROOT/'production/assets.json').read_text());errors=ch.check(r)
if errors:raise RuntimeError('\n'.join(errors))
assert not OUT.exists();OUT.mkdir(parents=True)
source_ids={};readers=[]
def asset(aid):
 a=r['assets'][aid];assert a['design_status'] not in ('rejected','reference_only');source_ids[aid]=a;return ROOT/a['path']
base_manifest=json.loads(asset('book.review.v02.manifest').read_text());plan=base_manifest['page_plan']
corrections={rec['id'].split('-')[0]:rec for rec in json.loads(asset('anatomy.prompts.v01').read_text())}
images={}
for sid,rec in corrections.items():
 aid='anatomy.v02.'+sid;p=asset(aid)
 with Image.open(p) as im:iw,ih=im.size
 b=io.BytesIO();c=canvas.Canvas(b,pagesize=(iw,ih));c.drawImage(str(p),0,0,iw,ih);c.showPage();c.save();b.seek(0)
 reader=PdfReader(b);readers.append(reader);images[sid]=next(iter(reader.pages[0]['/Resources']['/XObject'].values())).get_object()
outputs=[]
for lang in ('de','en','es'):
 src=PdfReader(asset('book.review.v02.'+lang));w=PdfWriter();changed=[]
 for entry,source in zip(plan,src.pages):
  page=w.add_page(source);sid=entry['id']
  if sid in corrections and entry['kind'] in ('coloring','jokes'):
   resources=DictionaryObject(page['/Resources']);xobjs=DictionaryObject(resources['/XObject'])
   keys=[key for key,obj in xobjs.items() if obj.get_object().get('/Subtype')=='/Image'];assert len(keys)==1
   old=xobjs[keys[0]].get_object();new=images[sid]
   assert abs(float(old['/Width'])/float(old['/Height'])-float(new['/Width'])/float(new['/Height']))<.002
   xobjs[keys[0]]=new.clone(w).indirect_reference;resources[NameObject('/XObject')]=xobjs;page[NameObject('/Resources')]=resources
   changed.append(entry['pdf_page'])
 w.add_metadata({'/Title':f'Giggle Dumplings Halloween {lang.upper()} - Anatomiekorrekturen v03','/Author':'Stefan Marx','/Subject':'Sichtfassung, keine Druckfreigabe; 110 Innenseiten plus Covervorschau'})
 p=OUT/f'giggle-dumplings-halloween-{lang}-review-v03.pdf'
 with p.open('xb') as f:w.write(f)
 result=PdfReader(p);assert len(result.pages)==111 and len(changed)==12
 for i,(old,new) in enumerate(zip(src.pages,result.pages),1):
  assert tuple(old.mediabox)==tuple(new.mediabox)
  oc,nc=old.get_contents(),new.get_contents();assert (oc.operations if oc else [])==(nc.operations if nc else [])
  assert old.extract_text()==new.extract_text(),(lang,i)
  ox=old.get('/Resources',{}).get('/XObject',{});nx=new.get('/Resources',{}).get('/XObject',{});assert set(ox)==set(nx)
  for key,obj in ox.items():
   target=images[plan[i-1]['id']] if i in changed else obj.get_object()
   assert target.get_data()==nx[key].get_object().get_data(),(lang,i,'image mismatch')
 outputs.append({'language':lang,'path':p.relative_to(ROOT).as_posix(),'sha256':ch.digest(p),'changed_pdf_pages':changed})
 print(lang,'12 images replaced; 111 page streams/text and all image bytes verified',flush=True)
m={'status':'review_draft','upload_ready':False,'interior_pages':110,'review_pages':111,'page_plan':plan,'sources':source_ids,'editions':outputs,'checks':{'only_12_image_resources_replaced':True,'all_text_and_layout_operators_unchanged':True,'page_count_and_boxes_unchanged':True},'visual_review':'pending','print_release':False}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
