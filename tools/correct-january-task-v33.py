"""Replace only January's native instruction text; preserve artwork and paths."""
import io,json,hashlib
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[1]
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v32.pdf'
OUT='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v33.pdf'
COMP=ROOT/'production/january-task/v33'
reg=json.loads((ROOT/'production/assets.json').read_text())
assert reg['selection']['current_working_master']==BASE
assert hashlib.sha256((ROOT/BASE).read_bytes()).hexdigest()==reg['assets'][BASE]['sha256']
assert not (ROOT/OUT).exists(), 'Version already exists; do not overwrite'
old=['Help Nibbles find the golden star! Use','the footprints to find the right way','through the snowy forest. There are','many dead ends - can you make it to','the star?']
text='Which footprints lead to the golden star? Follow the trail!'
assert text in (ROOT/'month-puzzles.md').read_text()
r=PdfReader(ROOT/BASE);w=PdfWriter(clone_from=r);p=w.pages[2];cs=ContentStream(p.get_contents(),w)
drop=set();removed=[]
for i,(a,o) in enumerate(cs.operations):
 if o!=b'BT':continue
 j=i+1
 while cs.operations[j][1]!=b'ET':j+=1
 tokens=[str(aa[0]) for aa,oo in cs.operations[i:j] if oo==b'Tj']
 if len(tokens)==1 and tokens[0] in old:
  tm=[aa for aa,oo in cs.operations[i:j] if oo==b'Tm']
  assert len(tm)==1 and abs(float(tm[0][4])-1197)<.01
  drop.update(range(i,j+1));removed+=tokens
assert removed==old,removed
cs.operations=[v for i,v in enumerate(cs.operations) if i not in drop];p.replace_contents(cs)
pdfmetrics.registerFont(TTFont('JanuaryTask','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
size=20;leading=22.6;width=269;lines=[];line=''
for word in text.split():
 trial=(line+' '+word).strip()
 if line and pdfmetrics.stringWidth(trial,'JanuaryTask',size)>width:lines.append(line);line=word
 else:line=trial
lines.append(line)
assert len(lines)*leading<=78
mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(1492,1054));c.setFillColor(HexColor('#173e59'));c.setFont('JanuaryTask',size)
for n,line in enumerate(lines):c.drawString(1197,1054-394-size-n*leading,line)
c.save();mem.seek(0);over=PdfReader(mem).pages[0];over.scale_to(float(p.mediabox.width),float(p.mediabox.height));p.merge_page(over)
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v33','/Subject':'January instruction corrected to agreed wording. Original paths unchanged; route validation and user review pending. Not print released.'})
with (ROOT/OUT).open('wb') as f:w.write(f)
q=PdfReader(ROOT/OUT)
assert len(q.pages)==26
assert ' '.join(q.pages[2].extract_text().split()).count(text)==1
assert 'Help Nibbles' not in q.pages[2].extract_text()
for n in range(26):
 if n==2:continue
 assert r.pages[n].get_contents().get_data()==q.pages[n].get_contents().get_data(),n
 assert [(im.name,hashlib.sha256(im.data).hexdigest()) for im in r.pages[n].images]==[(im.name,hashlib.sha256(im.data).hexdigest()) for im in q.pages[n].images],n
assert [(im.name,hashlib.sha256(im.data).hexdigest()) for im in r.pages[2].images]==[(im.name,hashlib.sha256(im.data).hexdigest()) for im in q.pages[2].images]
manifest={'base':BASE,'base_sha256':reg['assets'][BASE]['sha256'],'output':OUT,'changed_page':3,'removed_native_lines':removed,'task':{'text':text,'lines':lines,'font_size':size,'leading':leading,'font':'ChalkboardSE regular embedded','color':'#173e59','horizontal_stretch':False,'box':[1193,394,1470,480]},'unchanged_pages_verified':25,'verification':'Decoded content streams and image bytes equal on 25 other pages; January image bytes equal','path_geometry':'unchanged; unique solution still unverified','visual_review':'pending','user_review':'pending','print_status':'not_released','image_generation_calls':0}
(COMP/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('v33 created; 25 other pages unchanged; January image data unchanged; new task:',lines)
