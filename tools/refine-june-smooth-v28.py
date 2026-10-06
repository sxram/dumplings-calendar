"""Targeted June portrait and July contour refinements; unchanged December review."""
import ast,io,json,hashlib,calendar,math
from pathlib import Path
from PIL import Image
from pypdf import PdfReader,PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1];PW,PH=1492,1054
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v27.pdf';COMP=ROOT/'production/month-backs/june-smooth-v28'
reg=json.loads((ROOT/'production/assets.json').read_text())
for rel in [BASE,'back-images-with-puzzles-v1/06.png','back-images-with-puzzles-v1/07.png','tools/build-remaining-backs-v24.py']:
 assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256']
pdfmetrics.registerFont(TTFont('OriginalText','/System/Library/Fonts/MarkerFelt.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hand','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
for rel,names in [('tools/build-original-backs-batch-v22.py',['box','text','paragraph','piece','poly','ellipse','line']),('tools/build-remaining-backs-v24.py',['star_points','tracker','task','june','july'])]:
 tree=ast.parse((ROOT/rel).read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 if rel.endswith('v24.py'):nodes += [n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CASTLE' for t in n.targets)]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),rel,'exec'),globals())
TITLES={6:'Who Took the Strawberries?',7:'Which Shadow Belongs to the Castle?'}
TASKS={6:'The strawberries are gone! Read the clues and find out who took them.',7:'Look carefully! Which shadow matches the sandcastle exactly?'}
code_text=(ROOT/'tools/build-remaining-backs-v24.py').read_text();tree=ast.parse(code_text)
june_code=ast.get_source_segment(code_text,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='june'))
start=june_code.index("        if name=='Rabbit':");end=june_code.index('        text(c,x+114',start)
june_code=june_code[:start]+"        crop={'Rabbit':(773,778,887,874),'Squirrel':(1111,778,1240,874),'Duck':(780,885,889,980),'Nibbles':(1121,885,1240,980)}[name]\n        piece(c,'production/month-backs/june-smooth-v28/june-smooth-source.png',crop,(x+5,y+4,64,62),3)\n"+june_code[end:]
june_code=june_code.replace("'method':'original animal/Nibbles clips; native winged duck; three explicit exclusion clues'","'method':'four smooth finished isolated portraits; native labels and identical three clues; glasses exclusive to Nibbles'")
exec(june_code,globals())
july_code=ast.get_source_segment(code_text,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='july'))
july_code=july_code.replace("HexColor('#aa7b26'));c.setLineWidth(1)","HexColor('#704d20'));c.setLineWidth(2.2)")
exec(july_code,globals())
b=PdfReader(ROOT/BASE);w=PdfWriter();mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH));src='back-images-with-puzzles-v1/06.png';c.drawImage(str(ROOT/src),0,0,PW,PH);tr=tracker(c,6);task(c,6);proof=june(c,src);c.save();mem.seek(0);page=PdfReader(mem).pages[0];page.scale_to(float(b.pages[12].mediabox.width),float(b.pages[12].mediabox.height));w.add_page(page)
assert proof['answer']=='Nibbles'
w.add_metadata({'/Title':'Giggle Dumplings - June smooth portraits WORKING REVIEW v28','/Subject':'Four locally smoothed portraits, no print release.'})
with (ROOT/'tmp/pdfs/v28/candidate.pdf').open('wb') as f:w.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'months':[{'month':6,'puzzle':proof,'tracker':tr,'visual_review':'pending','user_review':'pending'}],'image_generation_calls':1,'image_use':'four portrait crops only; broad smooth shading replaces fur-like surfaces; all other page contents retained','print_status':'not_released'},indent=2)+'\n')
print('June smooth portraits staged.')
