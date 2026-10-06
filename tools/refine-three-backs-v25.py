"""Targeted user corrections: March pattern, April egg colors/order, August illustrated cards."""
import ast,calendar,hashlib,io,json,math
from collections import Counter
from pathlib import Path
from PIL import Image
from pypdf import PdfReader,PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
ROOT=Path(__file__).resolve().parents[1];PW,PH=1492,1054
COMP=ROOT/'production/month-backs/refinements-v25';records=[]
reg=json.loads((ROOT/'production/assets.json').read_text())
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v24.pdf'
for rel in [BASE,'back-images-with-puzzles-v1/03.png','back-images-with-puzzles-v1/04.png','back-images-with-puzzles-v1/08.png']:
 assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256']
pdfmetrics.registerFont(TTFont('OriginalText','/System/Library/Fonts/MarkerFelt.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hand','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
for rel,names in [('tools/build-original-backs-batch-v22.py',['box','text','paragraph','piece','poly','ellipse','line']),('tools/build-remaining-backs-v24.py',['star_points','tracker','task','seed_icon','march','august'])]:
 tree=ast.parse((ROOT/rel).read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),rel,'exec'),globals())
# Native March construction, revised under the explicit user request.
source=ast.get_source_segment((ROOT/'tools/build-remaining-backs-v24.py').read_text(),next(n for n in ast.parse((ROOT/'tools/build-remaining-backs-v24.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='march'))
source=source.replace("['sprout','sprout','tulip']*2+['sprout','sprout']","['sunflower','sunflower','acorn','pumpkin']*2+['sunflower','sunflower']").replace("['sprout','tulip','sunflower','acorn']","['acorn','sunflower','pumpkin','sprout']").replace("choices[1][1]=='tulip'","choices[1][0]=='acorn'").replace("'row2':'B - tulip'","'row2':'A - acorn'").replace("'periods':[3,3]","'periods':[3,4]")
exec(source,globals())
TITLES={3:'Seed Trail',4:'Find the Matching Eggs!',8:'Who Lives Here?'}
TASKS={3:'What comes next? Complete the two patterns!',4:'Two eggs are exactly the same. Can you find them?',8:'Match each woodland animal to its home.'}

def april_new(c,src):
 cols=[867,973,1080,1188,1294,1401]
 crops={'pink':(cols[0]-50,559,cols[0]+50,680),'blue':(cols[1]-50,559,cols[1]+50,680),'gold':(cols[2]-50,559,cols[2]+50,680),'green':(cols[3]-50,559,cols[3]+50,680),'zigzag':(cols[4]-50,559,cols[4]+50,680),'hearts':(cols[5]-50,559,cols[5]+50,680),'red':(cols[0]-50,730,cols[0]+50,851),'stars':(cols[1]-50,730,cols[1]+50,851),'confetti':(cols[3]-50,730,cols[3]+50,851)}
 ids=['pink','blue','gold','green','zigzag','hearts','red','stars','confetti','gold']
 box(c,814,515,658,344,'#fffdf0',r=15)
 for i,key in enumerate(ids):
  x=827+(i%5)*127;y=548+(i//5)*167
  piece(c,'production/month-backs/refinements-v25/april-recolored-source.png',crops[key],(x+11,y,100,121),9)
  if i==8:
   for dx,dy in [(48,31),(31,83)]:poly(c,star_points(x+11+dx,y+dy,6),'#fffdf0','#fffdf0',.2)
  text(c,x+61,y-9,'ABCDEFGHIJ'[i],21,'#44523a',center=True)
 assert sorted(Counter(ids).values())==[1]*8+[2]
 return {'answer':['C','J'],'motifs':ids,'source_crops':crops,'pair_source':'one gold/dots source crop duplicated; C/J at columns 3 and 5','palette':'similar lavender shells, white patterns','I_distinction':'two native small white stars added to source dotted egg; C/J remain exact duplicates'}

def august_new(c,src):
 # Reuse only the verified August calendar placement code, not the old sketch cards.
 code=ast.get_source_segment((ROOT/'tools/build-remaining-backs-v24.py').read_text(),next(n for n in ast.parse((ROOT/'tools/build-remaining-backs-v24.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='august'))
 prefix=code.split("    box(c,765,714,706,225",1)[0]+"    return placements\n"
 local={};exec(prefix,globals(),local);placements=local['august'](c,src)
 # Limit the task replacement to the original text line, preserving right-side foliage/lantern.
 box(c,887,679,444,29,'#fffdf0',r=3)
 text(c,890,699,TASKS[8],18,'#224c64')
 # Eight finished illustration sources; letters/numbering remain native.
 sheet='production/month-backs/refinements-v25/august-illustrated-source.png'
 box(c,765,714,706,225,'#fffdf0',r=12)
 crops=[(775,715,931,820),(941,715,1101,820),(1110,715,1281,820),(1291,715,1455,820),(775,832,931,937),(941,832,1101,937),(1110,832,1281,937),(1291,832,1455,937)]
 names=['Owl','Rabbit','Squirrel','Fox','nest','den','tree hollow','burrow']
 for i,name in enumerate(names):
  col=i%4;row=i//4;xx=779+col*171;yy=722+row*104
  box(c,xx,yy,159,94 if row==0 else 102,'#fffbea','#a9c5a4',r=10)
  piece(c,sheet,crops[i],(xx+10,yy+3,139,72),7)
  if row:text(c,xx+11,yy+20,str(col+1),19,'#41694c',center=True)
  text(c,xx+80,yy+(86 if row==0 else 92),name,17 if row==0 else 16,'#35532c',center=True)
 return {'answer':{'Owl':3,'Rabbit':4,'Squirrel':1,'Fox':2},'homes':names[4:],'calendar_positions':placements,'cards':crops,'method':'eight illustrated source crops, native labels; no sketch replacements; task mask ends before lantern'}

w=PdfWriter();b=PdfReader(ROOT/BASE)
for month,builder in [(3,march),(4,april_new),(8,august_new)]:
 src=f'back-images-with-puzzles-v1/{month:02}.png';mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH));c.drawImage(str(ROOT/src),0,0,PW,PH)
 tr=tracker(c,month)
 if month!=8:task(c,month)
 proof=builder(c,src);c.save();mem.seek(0);page=PdfReader(mem).pages[0];page.scale_to(float(b.pages[month*2].mediabox.width),float(b.pages[month*2].mediabox.height));w.add_page(page)
 records.append({'month':month,'tracker':tr,'puzzle':proof,'source':src,'visual_review':'pending','user_review':'pending'})
w.add_metadata({'/Title':'Giggle Dumplings - three revised backs WORKING REVIEW v25','/Subject':'User-requested revisions; no print release.'})
with (ROOT/'tmp/pdfs/v25/candidate.pdf').open('wb') as f:w.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'months':records,'image_generation_calls':2,'image_use':'only April egg crops and eight August card crops; full generated pages never selected','user_review':'pending','print_status':'not_released'},indent=2)+'\n')
print('Three pages staged.')
