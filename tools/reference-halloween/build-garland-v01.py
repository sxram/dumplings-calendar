"""Registered existing PDF figures on native vector pennants; no raster edits."""
import io,json,hashlib,importlib.util
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'05-kdp/specials/drafts/garland-v01'
spec=importlib.util.spec_from_file_location('check',ROOT/'tools/check-production-assets.py');ch=importlib.util.module_from_spec(spec);spec.loader.exec_module(ch)
r=json.loads((ROOT/'production/assets.json').read_text());errors=ch.check(r)
if errors:raise RuntimeError(errors)
a=r['assets']['book.review.v06.de']; src=PdfReader(ROOT/a['path'])
ma=r['assets']['book.review.v06.manifest'];m=json.loads((ROOT/ma['path']).read_text())
texts={
'de':{'title':'Unsere Halloween-Girlande','lines':['1. Male die sechs Freunde bunt aus.','2. Schneide die Wimpel an der durchgezogenen Außenlinie aus.','3. Falte die Laschen an der gestrichelten Linie nach hinten.','4. Lege eine Schnur in die Falten und klebe die Laschen hinten fest.'],'tab':'Klebelasche','footer':'Durchgezogen: schneiden    Gestrichelt: falten'},
'en':{'title':'Our Halloween Garland','lines':['1. Colour in all six friends.','2. Cut out the pennants along the solid outer lines.','3. Fold the tabs backwards along the dashed lines.','4. Place string inside the folds and glue the tabs to the backs.'],'tab':'Glue tab','footer':'Solid line: cut    Dashed line: fold'},
'es':{'title':'Nuestra guirnalda de Halloween','lines':['1. Colorea a los seis amigos.','2. Recorta los banderines por la línea continua exterior.','3. Dobla las pestañas hacia atrás por la línea discontinua.','4. Pon un cordón en los pliegues y pega las pestañas por detrás.'],'tab':'Pestaña para pegar','footer':'Línea continua: cortar    Línea discontinua: doblar'}}
pdfmetrics.registerFont(TTFont('Body','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc'))
w=PdfWriter(); placements=[]
for lang,t in texts.items():
 b=io.BytesIO();c=canvas.Canvas(b,pagesize=(504,720));c.setFont('Body',22 if lang!='es' else 20);c.drawCentredString(252,679,t['title'])
 c.setFont('Body',10)
 for i,line in enumerate(t['lines']):
  assert pdfmetrics.stringWidth(line,'Body',10)<420
  c.drawString(42,652-i*16,line)
 ops=[]
 for i,rec in enumerate(m['placements']):
  x=54+(i%2)*222;y=394-(i//2)*166;ww=174;hh=134
  # Complete cut perimeter includes broad tab; fold goes across its base.
  p=c.beginPath();p.moveTo(x,y+20);p.lineTo(x+ww/2,y);p.lineTo(x+ww,y+20);p.lineTo(x+ww,y+hh+18);p.lineTo(x,y+hh+18);p.close()
  c.setLineWidth(1);c.drawPath(p);c.setDash(4,3);c.line(x,y+hh,x+ww,y+hh);c.setDash()
  c.setFont('Body',7);c.drawCentredString(x+ww/2,y+hh+6,t['tab'])
  bw,bh=rec['source_bbox_px'][2]-rec['source_bbox_px'][0],rec['source_bbox_px'][3]-rec['source_bbox_px'][1]
  h=98;fw=h*bw/bh;fx=x+(ww-fw)/2;fy=y+25
  assert fw<ww-24
  ops.append(f'q {fw} 0 0 {h} {fx} {fy} cm /Figure{i} Do Q\n')
  if lang=='de':placements.append({'figure':rec['figure'],'source_id':rec['id'],'visible_box_pt':[fx,fy,fw,h],'effective_dpi':bh/h*72,'tab_height_pt':18})
 c.setFont('Body',9);c.drawCentredString(252,38,t['footer']);c.showPage();c.save();b.seek(0)
 pg=w.add_page(PdfReader(b).pages[0]);res=DictionaryObject(pg['/Resources']);xo=DictionaryObject()
 for pair,n in enumerate((100,102,104)):
  container=next(iter(src.pages[n-1]['/Resources']['/XObject'].values())).get_object()
  fs=container['/Resources']['/XObject']
  for j in range(2):xo[NameObject('/Figure'+str(pair*2+j))]=fs['/F'+str(j)].clone(w).indirect_reference
 res[NameObject('/XObject')]=xo;pg[NameObject('/Resources')]=res;st=DecodedStreamObject();st.set_data(pg.get_contents().get_data()+''.join(ops).encode());pg[NameObject('/Contents')]=w._add_object(st)
w.add_metadata({'/Title':'Figuren-Girlande DE EN ES - Entwurf v01','/Subject':'B08 Einzelmuster; Papierprobe und Druckfreigabe offen'})
p=OUT/'figuren-girlande-de-en-es-v01.pdf'
with p.open('xb') as f:w.write(f)
out=PdfReader(p);assert len(out.pages)==3
for pg,t in zip(out.pages,texts.values()):
 assert tuple(pg.mediabox)==(0,0,504,720)
 for line in t['lines']:assert line in pg.extract_text()
manifest={'status':'review_draft','source':{'id':'book.review.v06.de','path':a['path'],'sha256':a['sha256']},'placements':placements,'texts':texts,'output':{'path':str(p.relative_to(ROOT)),'sha256':ch.digest(p)},'visual_review':'pending','physical_test':'open','print_release':False,'book_integration':'not yet integrated'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('3 language pages created; text and page sizes checked')
