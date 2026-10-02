"""Centre six existing figures with PDF transforms, preserving every source raster."""
import sys
sys.dont_write_bytecode=True
import io,json,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject,ArrayObject,FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v06'
spec=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py');ch=importlib.util.module_from_spec(spec);spec.loader.exec_module(ch)
r=json.loads((ROOT/'production/assets.json').read_text());errors=ch.check(r)
if errors:raise RuntimeError('\n'.join(errors))
assert not OUT.exists();OUT.mkdir(parents=True)
used={}
def asset(aid):
 a=r['assets'][aid];assert a['design_status'] not in ('rejected','reference_only');used[aid]=a;return ROOT/a['path']
base=json.loads(asset('book.review.v05.manifest').read_text());plan=base['page_plan'];pages={100:'B03',102:'B04',104:'B05'}
boxes={};names={'B03':['Sunny','Mochi'],'B04':['Bao','Nibbles'],'B05':['Dreamy','Pips']};placements=[]
for sid in pages.values():
 a=np.array(Image.open(asset('05-kdp.specials.v01.'+sid)).convert('RGB'));ih,iw,_=a.shape;assert (iw,ih)==(1774,887)
 boxes[sid]=[]
 for j,(left,right) in enumerate(((0,iw//2),(iw//2,iw))):
  yy,xx=np.where(a[:,left:right].min(axis=2)<100);box=[int(xx.min()+left),int(yy.min()),int(xx.max()+left+1),int(yy.max()+1)];boxes[sid].append(box)
  l,t,rr,b=box;bh=b-t;bw=rr-l;h=140.;w=h*bw/bh;cx=154.5+j*204;cy=172.
  assert w<=164,(sid,w)
  placements.append({'id':sid,'figure':names[sid][j],'source_bbox_px':box,'visible_box_pt':[cx-w/2,cy-h/2,w,h],'card_front_pt':[60.5+j*204,80,188,184],'top_bottom_gap_pt':22.,'side_gap_pt':(188-w)/2,'effective_dpi':bh/h*72})
def form(w,data,resources,bbox=(0,0,1,1)):
 f=DecodedStreamObject();f.set_data(data.encode());f.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Form'),NameObject('/BBox'):ArrayObject([FloatObject(x) for x in bbox]),NameObject('/Resources'):DictionaryObject({NameObject('/XObject'):DictionaryObject({NameObject(k):v for k,v in resources.items()})})});return w._add_object(f)
def figures(w,source,sid):
 out=[];ref=source.clone(w).indirect_reference
 for box in boxes[sid]:
  l,t,rr,b=box;bw,bh=rr-l,b-t
  data=f'q {1774/bw:.12f} 0 0 {887/bh:.12f} {-l/bw:.12f} {-(887-b)/bh:.12f} cm /Base Do Q\n'
  out.append(form(w,data,{'/Base':ref},(-3/bw,-3/bh,1+3/bw,1+3/bh)))
 return out
outputs=[]
for lang in ('de','en','es'):
 src=PdfReader(asset('book.review.v05.'+lang));w=PdfWriter()
 for n,old in enumerate(src.pages,1):
  p=w.add_page(old)
  if n in pages:
   sid=pages[n];res=DictionaryObject(p['/Resources']);xo=DictionaryObject(res['/XObject']);assert len(xo)==1;key=next(iter(xo));original=xo[key].get_object();fs=figures(w,original,sid);ops=''
   for j,rec in enumerate(z for z in placements if z['id']==sid):
    x,y,ww,hh=rec['visible_box_pt'];ops+=f'q {ww/368:.12f} 0 0 {hh/184:.12f} {(x-72.5)/368:.12f} {(y-80)/184:.12f} cm /F{j} Do Q\n'
   xo[key]=form(w,ops,{'/F0':fs[0],'/F1':fs[1]});res[NameObject('/XObject')]=xo;p[NameObject('/Resources')]=res
 p=OUT/f'giggle-dumplings-halloween-{lang}-review-v06.pdf';w.add_metadata({'/Title':f'Giggle Dumplings Halloween {lang.upper()} - Aufsteller v06','/Subject':'Sichtfassung, keine Druckfreigabe','/Author':'Stefan Marx'})
 with p.open('xb') as f:w.write(f)
 result=PdfReader(p);assert len(result.pages)==len(src.pages)==111
 for n,(old,new) in enumerate(zip(src.pages,result.pages),1):
  assert tuple(old.mediabox)==tuple(new.mediabox)
  oc,nc=old.get_contents(),new.get_contents();assert (oc.operations if oc else [])==(nc.operations if nc else [])
  assert old.extract_text()==new.extract_text()
  ox=old.get('/Resources',{}).get('/XObject',{});nx=new.get('/Resources',{}).get('/XObject',{});assert set(ox)==set(nx)
  for k,v in ox.items():
   if n not in pages:assert v.get_object().get_data()==nx[k].get_object().get_data()
   else:
    for f in nx[k].get_object()['/Resources']['/XObject'].values():
     original=f.get_object()['/Resources']['/XObject']['/Base'].get_object();assert original.get_data()==v.get_object().get_data()
 outputs.append({'language':lang,'path':str(p.relative_to(ROOT)),'sha256':ch.digest(p),'changed_pdf_pages':list(pages)})
 print(lang,'3 standee pages aligned; all texts, page operators and source bytes retained',flush=True)
# Diagram of the folded tents, built from the same individual PDF figures.
pdfmetrics.registerFont(TTFont('Body','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc'))
b=io.BytesIO();c=canvas.Canvas(b,pagesize=(504,720));c.setFont('Body',21);c.drawString(32,681,'Unsere Freunde auf dem Partytisch');c.setFont('Body',10);c.drawString(32,658,'Faltvorschau · sechs Figuren · Entwurf v01')
preview_ops=[]
for i,rec in enumerate(placements):
 col=i%2;row=i//2;x=35+col*239;y=474-row*176;s=.70
 c.setFont('Body',13);c.drawString(x,y+147,rec['figure'])
 c.saveState();c.translate(x,y);c.scale(s,s)
 # Triangular end showing the folded blank rear face.
 p=c.beginPath();p.moveTo(188,0);p.lineTo(217.44,184);p.lineTo(251,0);p.close();c.setFillGray(.94);c.drawPath(p,fill=1,stroke=1)
 c.transform(1,0,.16,1,0,0);c.setFillGray(1);c.rect(0,0,188,184,stroke=1,fill=1);c.restoreState()
 bx,by,ww,hh=rec['visible_box_pt'];localx=(188-ww)/2;localy=22
 preview_ops.append(f'q {s} 0 {s*.16} {s} {x} {y} cm {ww} 0 0 {hh} {localx} {localy} cm /Figure{i} Do Q\n')
c.setFont('Body',10);c.drawString(32,79,'Die bedruckte Hälfte zeigt nach vorn. Die obere Hälfte wird zur Rückseite.');c.drawString(32,62,'Schematische Vorschau: Faltwinkel und Stand müssen am Papier geprüft werden.');c.setFont('Body',9);c.drawString(32,35,'Keine neue Illustration: vorhandene Figuren einzeln ausgerichtet.');c.showPage();c.save();b.seek(0)
pr=PdfReader(b);pw=PdfWriter();pg=pw.add_page(pr.pages[0]);res=DictionaryObject(pg['/Resources']);xo=DictionaryObject();src=PdfReader(asset('book.review.v05.de'))
for i,(n,sid) in enumerate(pages.items()):
 original=next(iter(src.pages[n-1]['/Resources']['/XObject'].values())).get_object();ff=figures(pw,original,sid)
 for j,f in enumerate(ff):xo[NameObject('/Figure'+str(i*2+j))]=f
res[NameObject('/XObject')]=xo;pg[NameObject('/Resources')]=res;stream=DecodedStreamObject();stream.set_data(pg.get_contents().get_data()+''.join(preview_ops).encode());pg[NameObject('/Contents')]=pw._add_object(stream)
p=OUT/'aufsteller-faltvorschau-v01.pdf'
with p.open('xb') as f:pw.write(f)
assert len(PdfReader(p).pages)==1
m={'status':'review_draft','upload_ready':False,'interior_pages':110,'review_pages':111,'page_plan':plan,'sources':used,'editions':outputs,'preview':{'path':str(p.relative_to(ROOT)),'sha256':ch.digest(p)},'placements':placements,'method':'Clipped PDF Form XObjects, individual visible-contour centering and equal height; no bitmap edits or image generation','checks':{'all_text_and_page_layout_operators_unchanged':True,'source_image_bytes_preserved':True,'page_count_and_boxes_unchanged':True,'physical_paper_test':'open','visible_height_pt':140,'top_bottom_gap_pt':22},'visual_review':'pending','print_release':False}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
