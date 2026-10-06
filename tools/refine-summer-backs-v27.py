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
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v26.pdf';COMP=ROOT/'production/month-backs/refinements-v27'
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
june_code=june_code[:start]+"        crop={'Rabbit':(773,778,887,874),'Squirrel':(1111,778,1240,874),'Duck':(780,885,889,980),'Nibbles':(1121,885,1240,980)}[name]\n        piece(c,'production/month-backs/refinements-v27/june-portrait-source.png',crop,(x+5,y+4,64,62),3)\n"+june_code[end:]
june_code=june_code.replace("'method':'original animal/Nibbles clips; native winged duck; three explicit exclusion clues'","'method':'four finished isolated portraits; native labels and identical three clues; glasses exclusive to Nibbles'")
exec(june_code,globals())
july_code=ast.get_source_segment(code_text,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='july'))
july_code=july_code.replace("HexColor('#aa7b26'));c.setLineWidth(1)","HexColor('#704d20'));c.setLineWidth(2.2)")
exec(july_code,globals())
b=PdfReader(ROOT/BASE);w=PdfWriter();records=[]
for month,builder in [(6,june),(7,july)]:
 src=f'back-images-with-puzzles-v1/{month:02}.png';mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH));c.drawImage(str(ROOT/src),0,0,PW,PH);tr=tracker(c,month);task(c,month);proof=builder(c,src);c.save();mem.seek(0);page=PdfReader(mem).pages[0];page.scale_to(float(b.pages[2*month].mediabox.width),float(b.pages[2*month].mediabox.height));w.add_page(page)
 if month==6:
  survivors=[n for i,n in enumerate(proof['suspects']) if not proof['wings'][i] and proof['turquoise_glasses'][i]];assert survivors==['Nibbles']
 else:assert proof['options'][2]==proof['reference_polygon']
 records.append({'month':month,'puzzle':proof,'tracker':tr,'visual_review':'pending','user_review':'pending'})
# December is unchanged, with exact native cut geometry checked from its registered source manifest.
dec=next(x for x in json.loads((ROOT/'production/month-backs/remaining-v24/manifest.json').read_text())['months'] if x['month']==12)['puzzle']
cx,cy=dec['missing_polygon'][0];assert dec['normalized_options'][2]==[[x-cx,y-cy] for x,y in dec['missing_polygon']]
assert all(poly!=dec['normalized_options'][2] for i,poly in enumerate(dec['normalized_options']) if i!=2)
assert dec['star_points']==12 and dec['reference_scale']==dec['option_scale']==1
w.add_page(b.pages[24]);records.append({'month':12,'changed':False,'answer':'C','proof':'missing polygon reused as C at identical scale; A/B/D differ; twelve points','user_review':'pending'})
w.add_metadata({'/Title':'Giggle Dumplings - June July December WORKING REVIEW v27','/Subject':'June and July locally refined; December unchanged. No print release.'})
with (ROOT/'tmp/pdfs/v27/candidate.pdf').open('wb') as f:w.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'months':records,'image_generation_calls':1,'image_use':'four June portrait crops only; full generated page not selected','visual_review':'pending','user_review':'pending','print_status':'not_released','january':'Original maze retained. Branching snow corridors and mixed footprint types still do not prove a unique traceable path; Nibbles/Bao discrepancy remains.'},indent=2)+'\n')
print('June and July staged; unchanged December geometry verified.')
