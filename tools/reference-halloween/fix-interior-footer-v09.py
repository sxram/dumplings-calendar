"""Remove old PDF footer objects, then typeset within KDP safe margins."""
from pathlib import Path
import io,json,hashlib
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1]
src=R/'05-kdp/upload/de-2026-09-30-v08/Giggle-Dumplings-Halloween-DE-Innenbuch.pdf'
O=R/'05-kdp/upload/interior-de-v09';O.mkdir(exist_ok=False)
pdfmetrics.registerFont(TTFont('Footer',str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype/DejaVuSans.ttf')))
r=PdfReader(src);w=PdfWriter();changed=[]
for number,p in enumerate(r.pages,1):
 cs=p.get_contents()
 if cs is None:w.add_page(p);continue
 ops=cs.operations;out=[];i=0;texts=0;lines=0
 while i<len(ops):
  a,op=ops[i]
  if op==b'BT':
   j=i+1
   while ops[j][1]!=b'ET':j+=1
   block=ops[i:j+1];matrices=[a for a,o in block if o==b'Tm']
   if matrices and all(abs(float(a[5])-16.5)<.01 for a in matrices):
    texts+=1;i=j+1;continue
  if op==b'm' and len(a)==2 and abs(float(a[0])-783)<.01 and abs(float(a[1])-297)<.01:
   b,bo=ops[i+1];_,co=ops[i+2]
   assert bo==b'l' and list(map(float,b))==[5436.,297.] and co==b'S'
   lines+=1;i+=3;continue
  out.append((a,op));i+=1
 if texts or lines:
  assert texts and lines,(number,texts,lines)
  cs.operations=out;p[NameObject('/Contents')]=cs
  buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(612,792))
  c.setStrokeGray(0);c.setLineWidth(.715);c.line(78.3,49.2,543.6,49.2)
  c.setFillGray(0);c.setFont('Footer',8.8)
  c.drawString(78.3,36,'Giggle Dumplings');c.drawRightString(543.6,36,str(number));c.save()
  buf.seek(0);p.merge_page(PdfReader(buf).pages[0])
  changed.append({'page':number,'removed_text_blocks':texts,'removed_lines':lines})
 w.add_page(p)
out=O/'Giggle-Dumplings-Halloween-DE-Innenbuch-v09.pdf';w.write(out)
check=PdfReader(out);assert len(check.pages)==128
assert all(tuple(map(float,p.mediabox))==(0.,0.,612.,792.) for p in check.pages)
for p in check.pages:
 if p.get_contents():
  assert not any(op==b'Tm' and abs(float(a[5])-16.5)<.01 for a,op in p.get_contents().operations)
manifest={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pages':128,'changed':changed,'footer_baseline_pt':36,'rule_y_pt':49.2,'kdp_minimum_bottom_pt':18,'cover_unchanged':'cover-de-v11','user_review':'pending','kdp_preview':'pending'}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
rp=R/'production/assets.json';reg=json.loads(rp.read_text())
for f in [out,O/'manifest.json']:
 k='interior.footer.v09.'+f.suffix[1:]
 reg['assets'][k]={'path':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'role':'export','usage':'Korrigierter unterer Satzbereich für KDP','design_status':'review_pending','print_status':'not_released','issues':['KDP-Druckvorschau erneut prüfen'],'origin':{'project':'dumplings-halloween','source':manifest['source'],'note':'Alte Fußzeilenobjekte entfernt, neue Fußzeile höher gesetzt; Bildmaß und Seitenzahl erhalten.'}}
reg['selection']['current_kdp_interior_de']='interior.footer.v09.pdf'
rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pages':128,'footers_fixed':len(changed),'output':str(out)}))
