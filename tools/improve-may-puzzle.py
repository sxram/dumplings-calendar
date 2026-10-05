"""Replace May only; deterministic garden search scene."""
import hashlib, importlib.util, io, json, math, re
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('puzzles',ROOT/'tools/build-calendar-puzzles.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=ROOT/'production/puzzles/may-v10';out.mkdir(exist_ok=False)
s=m.header(5)
s.rect(5,63,310,220,'#eff6e8','#9ebd91',.6)
# Garden layers: fence, tree, beds, winding stepping stones, basket.
for x in range(16,308,18):
 s.poly([(x,134),(x,108),(x+5,101),(x+10,108),(x+10,134)],'#e1ceb0','#c7b18f',.6)
s.rect(10,121,302,4,'#e1ceb0','#c7b18f',.5)
s.rect(256,97,15,150,'#d5b68c','#ad916d',.7)
for x,y,r in [(242,87,23),(268,85,24),(291,95,20),(236,107,22),(268,111,28),(291,117,19)]:
 s.circle(x,y,r,'#b6d29a','#8eb47d',.7)
for x,y in [(238,90),(256,105),(278,85),(287,113)]:
 s.circle(x,y,3,'#e9b0a0','#c99283',.6)
s.ellipse(120,254,105,18,'#dbe8c8','#a7c58c',.7)
s.ellipse(87,164,74,27,'#d6e7be','#a7c58c',.7)
s.ellipse(238,221,63,26,'#d6e7be','#a7c58c',.7)
for i in range(7):
 x=165+13*math.sin(i*.65);y=150+i*18
 s.ellipse(x,y,12,5,'#ddd7bf','#bcb99e',.6)
# Stems and leaves build a real search field; butterflies remain complete.
for i in range(35):
 x=22+(i*43)%276;y=166+(i*31)%102
 if 140<x<189:continue
 s.line(x,y,x,y-19,'#7b9d68',.8)
 s.ellipse(x-4,y-8,5,2.5,'#a0bd81','#7b9d68',.5)
 s.ellipse(x+4,y-13,5,2.5,'#b3c98e','#7b9d68',.5)
 m.flower(s,x,y-22,['#efd8a9','#e9b6b3','#d9c3df'][i%3])
for x,y in [(39,94),(86,85),(112,115),(191,91)]:
 s.line(x,y,x,y+11,'#8dad73',.7)
 for dx in [-4,4]:s.ellipse(x+dx,y+4,5,2.5,'#b4cc92','#8dad73',.5)
 m.flower(s,x,y,'#efd8a9')
s.rect(65,242,43,23,'#dcb47c','#a87d48',.8)
s.bezier([(68,242),(64,216),(108,216),(105,242)],'#a87d48',1.4)
for y in [250,257]:s.line(67,y,106,y,'#b28e5c',.5)
for x in [74,83,92,101]:s.line(x,244,x,262,'#b28e5c',.5)
for x,y in [(55,157),(115,218),(211,173),(283,268)]:
 s.poly([(x-9,y),(x,y-8),(x+9,y),(x,y+8)],'#b7cc91','#88a370',.5)
positions=[(38,114,.70),(100,159,.72),(196,104,.72),(279,108,.70),(235,191,.72),(83,235,.72),(119,263,.72),(288,246,.70)]
for x,y,z in positions:m.butterfly(s,x,y,z)
assert len(positions)==8 and len(set((x,y) for x,y,z in positions))==8
(out/'05-puzzle.svg').write_text(s.svg());(out/'05-drawing.json').write_text(json.dumps(s.ops,indent=2)+'\n')
reg=json.loads((ROOT/'production/assets.json').read_text())
base='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v09.pdf';source='update_26-10-02/giggle_dumplings_2027_current_master_v4.pdf'
for rel in [base,source]:assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256']
page=PdfReader(ROOT/source).pages[10];raw=page.get_contents().get_data()
pattern=rb'BT 1 0 0 1 (164|185|206|227) 557\.2756 Tm (/F2\+0 25 Tf 30 TL \([2027]\) Tj T\* ET)'
raw,count=re.subn(pattern,lambda q:b'BT 1 0 0 1 '+str(int(q.group(1))+41).encode()+b' 557.2756 Tm '+q.group(2),raw);assert count==4
a=list(re.finditer(rb'1 1 1 rg\n([^\n]+) RG\n1 w\nn\n491 100 m\n',raw));b=list(re.finditer(rb'[^\n]+ rg\n[^\n]+ RG\n1 w\nn\n25 14 m\n',raw));assert len(a)==len(b)==1
new=raw[:a[0].start()]+raw[b[0].start():];new=new.replace(b'BT /F1 8.5 Tf 10.2 TL ET',b'.141176 .27451 .352941 rg\nBT /F1 8.5 Tf 10.2 TL ET')
stream=DecodedStreamObject();stream.set_data(new);page[NameObject('/Contents')]=stream
mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(float(page.mediabox.width),float(page.mediabox.height)))
c.setFillColor(HexColor('#ffffff'));c.setStrokeColor(HexColor('#b2d781'));c.setLineWidth(.8);c.roundRect(479,100,348.89,315.2756,12,fill=1,stroke=1);s.render(c,493,110);c.save();mem.seek(0);page.merge_page(PdfReader(mem).pages[0])
r=PdfReader(ROOT/base);writer=PdfWriter()
for i,p in enumerate(r.pages):writer.add_page(page if i==10 else p)
writer.add_metadata({'/Title':'Giggle Dumplings 2027 - Arbeitsmaster v10'})
target=ROOT/'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v10.pdf';assert not target.exists();writer.write(target)
final=PdfReader(target);assert len(final.pages)==26
for i in range(26):
 if i!=10:assert final.pages[i].get_contents().get_data()==r.pages[i].get_contents().get_data()
assert m.TITLES[4] in final.pages[10].extract_text() and m.TASKS[4] in ' '.join(final.pages[10].extract_text().split())
proof={'base':base,'output':str(target.relative_to(ROOT)),'answer':{'count':8,'positions':positions},'construction':'8 complete butterflies, added after all garden scenery; no additional butterfly motifs','changed_pages':[11],'other_25_content_streams':'identical','visual_review':'pending','print_release':False}
(out/'manifest.json').write_text(json.dumps(proof,indent=2)+'\n')
print(target)
