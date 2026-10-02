"""Patch registered illustrations through clipped PDF layers; preserve page layout."""
import sys
sys.dont_write_bytecode=True
import io,json,importlib.util
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject,ArrayObject,NumberObject
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v05'
spec=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py');ch=importlib.util.module_from_spec(spec);spec.loader.exec_module(ch)
r=json.loads((ROOT/'production/assets.json').read_text());errors=ch.check(r)
if errors:raise RuntimeError('\n'.join(errors))
assert not OUT.exists(), 'Do not overwrite an existing book version'
OUT.mkdir(parents=True)
used={};readers=[]
def asset(aid):
 a=r['assets'][aid];assert a['design_status'] not in ('rejected','reference_only');used[aid]=a;return ROOT/a['path']
base=json.loads(asset('book.review.v04.manifest').read_text());plan=base['page_plan']
# Boxes in original image pixels, top-left origin, explicitly bounded to repaired contours.
patches={'C05':[18,800,120,943],'C06':[12,250,185,322],'K02':[69,1080,300,1160],'B04':[185,501,335,580]}
by_page={4:'B04',38:'K02',92:'C05',94:'C06',102:'B04'}
edits={};sizes={}
for sid in patches:
 p=asset('figures.v02.'+sid);original=asset('05-kdp.specials.v01.'+sid)
 with Image.open(p) as im:sz=im.size
 with Image.open(original) as im:assert im.size==sz
 sizes[sid]=sz
 b=io.BytesIO();c=canvas.Canvas(b,pagesize=(1,1));c.drawImage(str(p),0,0,1,1);c.showPage();c.save();b.seek(0)
 rr=PdfReader(b);readers.append(rr);edits[sid]=next(iter(rr.pages[0]['/Resources']['/XObject'].values())).get_object()
def make_form(old,sid,w):
 iw,ih=sizes[sid];l,t,rr,bb=patches[sid];rect=[l/iw,1-bb/ih,(rr-l)/iw,(bb-t)/ih]
 f=DecodedStreamObject();f.set_data(('q /Original Do Q\nq '+' '.join(f'{v:.10f}' for v in rect)+' re W n /Edit Do Q\n').encode())
 f.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Form'),NameObject('/FormType'):NumberObject(1),NameObject('/BBox'):ArrayObject([NumberObject(v) for v in (0,0,1,1)]),NameObject('/Resources'):DictionaryObject({NameObject('/XObject'):DictionaryObject({NameObject('/Original'):old.clone(w).indirect_reference,NameObject('/Edit'):edits[sid].clone(w).indirect_reference})})})
 return w._add_object(f)
outputs=[]
for lang in ('de','en','es'):
 src=PdfReader(asset('book.review.v04.'+lang));w=PdfWriter();changed=[]
 for n,source in enumerate(src.pages,1):
  page=w.add_page(source)
  if n in by_page:
   sid=by_page[n];res=DictionaryObject(page['/Resources']);xo=DictionaryObject(res['/XObject']);keys=[k for k,v in xo.items() if v.get_object().get('/Subtype')=='/Image'];assert len(keys)==1
   key=keys[0];old=xo[key].get_object();assert (old['/Width'],old['/Height'])==sizes[sid]
   xo[key]=make_form(old,sid,w);res[NameObject('/XObject')]=xo;page[NameObject('/Resources')]=res;changed.append(n)
 w.add_metadata({'/Title':f'Giggle Dumplings Halloween {lang.upper()} - Figurenkorrekturen v05','/Author':'Stefan Marx','/Subject':'Sichtfassung; keine Druckfreigabe'})
 p=OUT/f'giggle-dumplings-halloween-{lang}-review-v05.pdf'
 with p.open('xb') as f:w.write(f)
 result=PdfReader(p);assert len(result.pages)==111 and changed==sorted(by_page)
 for n,(old,new) in enumerate(zip(src.pages,result.pages),1):
  assert tuple(old.mediabox)==tuple(new.mediabox)
  oc,nc=old.get_contents(),new.get_contents();assert (oc.operations if oc else [])==(nc.operations if nc else [])
  assert old.extract_text()==new.extract_text(),(lang,n,'text')
  ox=old.get('/Resources',{}).get('/XObject',{});nx=new.get('/Resources',{}).get('/XObject',{});assert set(ox)==set(nx)
  for key,obj in ox.items():
   target=nx[key].get_object()
   if n in by_page:
    assert target['/Subtype']=='/Form';xo=target['/Resources']['/XObject'];assert set(xo)=={'/Original','/Edit'}
    assert xo['/Original'].get_object().get_data()==obj.get_object().get_data()
    assert xo['/Edit'].get_object().get_data()==edits[by_page[n]].get_data()
   else:assert target.get_data()==obj.get_object().get_data(),(lang,n,'unchanged image')
 outputs.append({'language':lang,'path':str(p.relative_to(ROOT)),'sha256':ch.digest(p),'changed_pdf_pages':changed})
 print(lang,'5 page image resources patched; all 111 texts/layouts and originals verified',flush=True)
assert len([p for p in plan if p['kind']=='coloring'])==30
assert len({p['id'] for p in plan if p['kind']=='coloring'})==30
m={'status':'review_draft','upload_ready':False,'interior_pages':110,'review_pages':111,'page_plan':plan,'sources':used,'editions':outputs,'patch_boxes_top_left_pixels':patches,'image_sizes':sizes,'page_patch_sources':by_page,'method':'Original embedded image plus clipped edited image in a PDF Form XObject; no raster editing or replacement outside the clip','checks':{'all_text_and_page_layout_operators_unchanged':True,'original_raster_bytes_preserved':True,'all_unaffected_resources_unchanged':True,'page_count_and_boxes_unchanged':True,'30_unique_coloring_pages':True},'visual_review':'pending','print_release':False}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
