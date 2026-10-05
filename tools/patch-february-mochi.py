"""Clip a generated local repair over original February art; preserve outside."""
import hashlib,io,json
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v19.pdf'
patch=ROOT/'production/month-images/drafts/february-v02/02-mochi-no-pompoms-v01.png'
target=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v20.pdf'
assert not target.exists()
reg=json.loads((ROOT/'production/assets.json').read_text())
assert hashlib.sha256(base.read_bytes()).hexdigest()==reg['assets'][str(base.relative_to(ROOT))]['sha256']
r=PdfReader(base);page=r.pages[3];old=page.get_contents().get_data()
# The source image has this precise native placement in the existing PDF.
assert b'842.6482 0 0 595.2756 -0.379196 0 cm' in old
iw,ih=1492,1054;pw,ph=842.6482,595.2756;ox=-.379196
polygon=[(608,730),(609,720),(622,710),(631,708),(641,716),(646,708),(657,706),(669,712),(675,719),(670,730),(660,726),(651,728),(644,735),(636,733),(625,731),(613,730)]
buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(float(page.mediabox.width),float(page.mediabox.height)))
c.saveState();p=c.beginPath()
for i,(x,y) in enumerate(polygon):
 (p.moveTo if i==0 else p.lineTo)(ox+x*pw/iw,ph-y*ph/ih)
p.close();c.clipPath(p,stroke=0,fill=0);c.drawImage(str(patch),ox,0,pw,ph);c.restoreState();c.save();buf.seek(0)
page.merge_page(PdfReader(buf).pages[0]);writer=PdfWriter()
for page in r.pages:writer.add_page(page)
writer.add_metadata({'/Title':'Giggle Dumplings 2027 - Arbeitsmaster v20'});writer.write(target)
f=PdfReader(target);assert len(f.pages)==26
for i in range(26):
 if i!=3:assert f.pages[i].get_contents().get_data()==r.pages[i].get_contents().get_data()
manifest={'date':'2026-10-04','base':str(base.relative_to(ROOT)),'master':str(target.relative_to(ROOT)),'patch':str(patch.relative_to(ROOT)),'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'source_pixels':[iw,ih],'clip_polygon_pixels':polygon,'method':'Native PDF clipped overlay. Original image unchanged underneath; generated image only visible inside local polygon behind bow.','changed_pages':[4],'other_25_content_streams':'identical','image_generation_calls':1,'visual_review':'pending','user_review':'pending','print_release':False}
(patch.parent/'local-patch-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(target)
