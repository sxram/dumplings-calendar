"""Add ownership label above the existing name line on physical page 3."""
from pathlib import Path
import io,json,hashlib
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1]
src=R/'05-kdp/upload/interior-de-v10/Giggle-Dumplings-Halloween-DE-Innenbuch-v10.pdf'
O=R/'05-kdp/upload/interior-de-v11';O.mkdir(exist_ok=False)
pdfmetrics.registerFont(TTFont('Title','/System/Library/Fonts/Supplemental/Chalkboard.ttc',subfontIndex=0))
b=io.BytesIO();c=canvas.Canvas(b,pagesize=(612,792));c.setFillGray(0);c.setFont('Title',21)
c.drawString(89.3,525,'Dieses Buch gehört:');c.save();b.seek(0)
r=PdfReader(src);w=PdfWriter()
for i,p in enumerate(r.pages):
 if i==2:p.merge_page(PdfReader(b).pages[0])
 w.add_page(p)
out=O/'Giggle-Dumplings-Halloween-DE-Innenbuch-v11.pdf';w.write(out)
check=PdfReader(out);assert len(check.pages)==128
assert 'Dieses Buch gehört:' in check.pages[2].extract_text()
for i in range(128):
 if i!=2:
  before=PdfReader(src).pages[i] if False else r.pages[i]
  assert (before.get_contents().get_data() if before.get_contents() else b'')==(check.pages[i].get_contents().get_data() if check.pages[i].get_contents() else b'')
rp=R/'production/assets.json';reg=json.loads(rp.read_text());key='interior.owner.v11.pdf'
reg['assets'][key]={'path':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'role':'export','usage':'Seite 3: Dieses Buch gehört über vorhandener Namenszeile','design_status':'review_pending','print_status':'not_released','issues':['Nutzerreview und KDP-Vorschau offen'],'origin':{'project':'dumplings-halloween','source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()}}
reg['selection']['current_kdp_interior_de']=key;rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(out)
