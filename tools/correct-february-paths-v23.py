"""Replace only February's too-easy path panel; October feedback stays open."""
import hashlib
import io
import json
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

ROOT=Path(__file__).resolve().parents[1]
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v22.pdf'
OLD_REVIEW='output/pdf/giggle-dumplings-five-backs-REVIEW-v22.pdf'
SOURCE='back-images-with-puzzles-v1/02.png'
MASTER='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v23.pdf'
REVIEW='output/pdf/giggle-dumplings-five-backs-REVIEW-v23.pdf'
COMP=ROOT/'production/month-backs/february-paths-v23'
reg=json.loads((ROOT/'production/assets.json').read_text())
for rel in [BASE,OLD_REVIEW,SOURCE]:
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256'],rel
for rel in [MASTER,REVIEW]:
    assert not (ROOT/rel).exists(),rel
COMP.mkdir(exist_ok=False)
PW,PH=1492,1054
mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH))

def piece(crop,target,radius=0):
    sx,sy,ex,ey=crop;x,y,w,h=target
    ax,ay=w/(ex-sx),h/(ey-sy)
    c.saveState();p=c.beginPath()
    if radius:p.roundRect(x,PH-y-h,w,h,radius)
    else:p.rect(x,PH-y-h,w,h)
    c.clipPath(p,stroke=0)
    c.drawImage(str(ROOT/SOURCE),x-sx*ax,PH-y-(PH-sy)*ay,PW*ax,PH*ay)
    c.restoreState()

area=(867,539,608,383)
piece((480,0,859,180),area,12)
clips=[
 ((870,542,970,604),(869,556,104,65)),
 ((870,616,970,681),(869,634,104,68)),
 ((870,691,970,755),(869,713,104,67)),
 ((870,768,971,834),(869,792,104,69)),
 ((1383,566,1474,633),(1380,555,91,67)),
 ((1383,645,1474,712),(1380,634,91,67)),
 ((1383,722,1474,789),(1380,713,91,67)),
 ((1383,799,1474,869),(1380,792,91,70)),
]
for crop,target in clips:piece(crop,target,8)

# Adjacent lane exchanges guarantee exactly one crossing per exchanged pair.
# No three-way junctions; every cubic has horizontal tangents at its endpoints.
levels=[590,669,747,828]
order=list('ABCD');orders=[order.copy()]
exchanges=[[(0,1),(2,3)],[(1,2)]]*5
crossings=[]
for col,swaps in enumerate(exchanges):
    for a,b in swaps:
        crossings.append({'column':col,'paths':[order[a],order[b]]})
        order[a],order[b]=order[b],order[a]
    orders.append(order.copy())
assert order==list('BDAC')
assert len(crossings)==15
assert len({tuple(sorted(v)) for v in orders})==1  # every column retains all four paths
jitters=[0,-6,9,-8,4,-5,8,-9,6,-3,0]
xs=[971+(1382-971)*i/10 for i in range(11)]
points={letter:[(xs[j],levels[orders[j].index(letter)]+jitters[j])
                for j in range(11)] for letter in 'ABCD'}
curves={}
for letter,pts in points.items():
    segments=[]
    for a,b in zip(pts,pts[1:]):
        dx=b[0]-a[0]
        segments.append([a,(a[0]+.42*dx,a[1]),(b[0]-.42*dx,b[1]),b])
    curves[letter]=segments
    for color,width in [('#ffffff',11),('#5593c7',6.5),('#a8daf1',3)]:
        c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setLineCap(1)
        p=c.beginPath();p.moveTo(pts[0][0],PH-pts[0][1])
        for seg in segments:
            p.curveTo(*[v for x,y in seg[1:] for v in (x,PH-y)])
        c.drawPath(p)
c.save();mem.seek(0)
base=PdfReader(ROOT/BASE)
overlay=PdfReader(mem).pages[0]
overlay.scale_to(float(base.pages[4].mediabox.width),float(base.pages[4].mediabox.height))
page=base.pages[4]
page.merge_page(overlay)
w=PdfWriter()
for p in base.pages:w.add_page(p)
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v23',
                '/Subject':'February paths revised after user feedback. October feedback unresolved. No print release.'})
with (ROOT/MASTER).open('wb') as f:w.write(f)
review_source=PdfReader(ROOT/OLD_REVIEW);rw=PdfWriter();rw.add_page(page)
for p in review_source.pages[1:]:rw.add_page(p)
rw.add_metadata({'/Title':'Giggle Dumplings - five backs REVIEW v23',
                 '/Subject':'Only February changed from v22; October objection still open.'})
with (ROOT/REVIEW).open('wb') as f:rw.write(f)
check=PdfReader(ROOT/MASTER);old=PdfReader(ROOT/BASE)
assert len(check.pages)==26
for i in range(26):
    if i!=4:assert check.pages[i].get_contents().get_data()==old.pages[i].get_contents().get_data(),i
review_check=PdfReader(ROOT/REVIEW)
for i in range(1,5):
    assert review_check.pages[i].get_contents().get_data()==review_source.pages[i].get_contents().get_data(),i
# SVG stores precisely the same native geometry, including bridge outlines.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="867 539 608 383">']
for letter,segs in curves.items():
    d=f'M {segs[0][0][0]:.4f},{segs[0][0][1]:.4f}'
    for seg in segs:
        d+=' C '+' '.join(f'{x:.4f},{y:.4f}' for x,y in seg[1:])
    for color,width in [('#ffffff',11),('#5593c7',6.5),('#a8daf1',3)]:
        svg.append(f'<path data-letter="{letter}" d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
svg.append('</svg>')
(COMP/'paths.svg').write_text('\n'.join(svg)+'\n')
manifest={'date':'2026-10-06','base':BASE,'master':MASTER,'review':REVIEW,
          'sources':{r:reg['assets'][r]['sha256'] for r in [BASE,OLD_REVIEW,SOURCE]},
          'changed_page':5,'changed_area_original_coordinates':area,
          'answer':dict(zip('ABCD',[3,1,4,2])),'path_cubics':curves,
          'crossings':crossings,'crossing_count':15,'column_orders':orders,
          'topology':'Four independent paths. Only adjacent exchanges; no branches or three-way junctions.',
          'styling':'Same blue on all four routes; white outlines mark underpasses.',
          'preserved_master_pages':25,'preserved_review_pages':4,
          'image_generation_calls':0,'visual_review':'pending','user_review':'pending',
          'print_status':'not_released',
          'october':'Unchanged. User reports an error; specific affected feature requested. Source pixels give five pairs A-H/B-F/C-J/E-L/G-I; D and K single.'}
(COMP/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('February: 15 distinct two-path crossings, fixed mapping; 25 master pages and 4 review pages unchanged.')
