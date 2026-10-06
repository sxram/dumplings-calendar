"""Five original-designed lower pages, with bounded PDF clips and native vectors.

No image generation or raster retouching. Source images remain byte-identical.
All coordinates below use original pixels, top-left origin; outputs use existing
master page dimensions. Run only with registered, unchanged source files.
"""
import calendar
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'production/month-backs/original-batch-v22'
BASE = 'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v20.pdf'
MASTER = 'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v22.pdf'
REVIEW = 'output/pdf/giggle-dumplings-five-backs-REVIEW-v22.pdf'
MONTHS = [2, 5, 9, 10, 11]
PW, PH = 1492, 1054
REG = json.loads((ROOT / 'production/assets.json').read_text())
SOURCES = [BASE] + [f'back-images-with-puzzles-v1/{m:02}.png' for m in MONTHS]
for rel in SOURCES:
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == REG['assets'][rel]['sha256'], rel
for rel in [MASTER, REVIEW]:
    assert not (ROOT / rel).exists(), 'Version already exists: ' + rel
OUT.mkdir(exist_ok=False)
pdfmetrics.registerFont(TTFont('OriginalText', '/System/Library/Fonts/MarkerFelt.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hand', '/System/Library/Fonts/Supplemental/ChalkboardSE.ttc', subfontIndex=0))


def box(c, x, y, w, h, fill, stroke=None, r=0):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke or fill))
    c.setLineWidth(1)
    if r:
        c.roundRect(x, PH-y-h, w, h, r, fill=1, stroke=bool(stroke))
    else:
        c.rect(x, PH-y-h, w, h, fill=1, stroke=bool(stroke))


def text(c, x, y, s, size=20, color='#16485e', font='OriginalText', center=False):
    c.setFillColor(HexColor(color))
    c.setFont(font, size)
    (c.drawCentredString if center else c.drawString)(x, PH-y, s)


def paragraph(c, x, y, s, width, size=20, leading=26, color='#16485e'):
    lines, line = [], ''
    for word in s.split():
        nxt = (line + ' ' + word).strip()
        if line and pdfmetrics.stringWidth(nxt, 'OriginalText', size) > width:
            lines.append(line)
            line = word
        else:
            line = nxt
    if line:
        lines.append(line)
    for i, line in enumerate(lines):
        text(c, x, y+i*leading, line, size, color)
    return y + len(lines)*leading


def piece(c, src, crop, target, radius=0):
    """Clip an unchanged source image into a bounded destination rectangle."""
    sx, sy, ex, ey = crop
    x, y, w, h = target
    ax, ay = w/(ex-sx), h/(ey-sy)
    c.saveState()
    p = c.beginPath()
    if radius:
        p.roundRect(x, PH-y-h, w, h, radius)
    else:
        p.rect(x, PH-y-h, w, h)
    c.clipPath(p, stroke=0)
    c.drawImage(str(ROOT/src), x-sx*ax, PH-y-(1054-sy)*ay,
                1492*ax, 1054*ay)
    c.restoreState()


def poly(c, pts, fill, stroke='#283642', width=1):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke))
    c.setLineWidth(width)
    p = c.beginPath()
    p.moveTo(pts[0][0], PH-pts[0][1])
    for x, y in pts[1:]:
        p.lineTo(x, PH-y)
    p.close()
    c.drawPath(p, stroke=1, fill=1)


def ellipse(c, x, y, rx, ry, fill, stroke=None, width=1):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke or fill))
    c.setLineWidth(width)
    c.ellipse(x-rx, PH-y-ry, x+rx, PH-y+ry, fill=1, stroke=bool(stroke))


def line(c, a, b, color, width=2):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(a[0], PH-a[1], b[0], PH-b[1])


def tracker(c, src, month):
    # Copy original illustrated gold/empty stars; correct count without new style.
    specs = {
        5: ((822,139,855,175), (975,139,1008,175), (816,132,411,47)),
        9: ((864,76,900,113), (1289,76,1325,113), (862,72,558,42)),
        10: ((863,74,899,112), (1333,74,1369,112), (857,71,567,43)),
        11: ((879,76,915,113), (1379,76,1415,113), (871,73,552,42)),
    }
    if month == 2:
        return {'filled': 2, 'empty': 10, 'method': 'unchanged original; visually counted'}
    gold, empty, region = specs[month]
    x, y, w, h = region
    box(c, x, y, w, h, '#fffdf0')
    step = (w-36)/11
    for i in range(12):
        piece(c, src, gold if i < month else empty, (x+i*step, y+3, 35, 37))
    return {'filled': month, 'empty': 12-month, 'source_clips': [gold, empty],
            'region': region, 'method': 'original star sprites, exactly twelve placements'}


CONTENT = {
    2: {'story': 'Friendly letters lead the Dumplings through the snowy village. At the old bridge they discover the second golden star.',
        'job': ['Carries letters', 'Finds addresses', 'Delivers kind notes'],
        'challenge': 'Leave someone a kind little note.',
        'fact': 'Handwritten notes can make people feel remembered.',
        'story_box': (902, 211, 425, 199), 'job_box': (283, 701, 196, 214),
        'challenge_box': (606, 683, 185, 196), 'fact_box': (337, 942, 386, 70)},
    5: {'story': 'A trail of butterflies leads the friends across the meadow to an old tree hollow, where they discover star number five.',
        'job': ['Watches butterflies', 'Studies nature', 'Follows tiny clues'],
        'challenge': 'Do one small thing to help nature.',
        'fact': 'Butterflies taste with sensors on their feet.',
        'story_box': (816, 190, 408, 149), 'job_box': (279, 710, 194, 181),
        'challenge_box': (550, 681, 224, 173), 'fact_box': (298, 944, 395, 50)},
    9: {'story': 'At ancient ruins the friends find star number nine and a stone circle with twelve star-shaped spaces. At last, the stars seem connected.',
        'job': ['Uses a brush', 'Studies ruins', 'Records old clues'],
        'challenge': 'Discover something you never noticed before.',
        'fact': 'Archaeologists study objects and sites to learn about the past.',
        'story_box': (868, 122, 526, 68), 'job_box': (268, 710, 182, 220),
        'challenge_box': (512, 708, 193, 217), 'fact_box': (302, 951, 700, 52)},
    10: {'story': 'At a pumpkin farm the Dumplings find a tiny door in a giant pumpkin. Behind it waits the tenth golden star.',
         'job': ['Carves pumpkins', 'Sketches designs', 'Works carefully'],
         'challenge': 'Make something funny with autumn leaves.',
         'fact': 'Pumpkins are fruits and belong to the squash family.',
         'story_box': (868, 116, 530, 75), 'job_box': (269, 710, 182, 222),
         'challenge_box': (511, 710, 186, 195), 'fact_box': (303, 949, 682, 57)},
    11: {'story': 'A strong autumn storm sweeps through the forest. After it calms, exposed roots reveal the eleventh golden star.',
         'job': ['Reports the weather', 'Observes the wind', 'Checks storm clues'],
         'challenge': 'Help someone when things get difficult.',
         'fact': 'Strong wind can move branches and expose roots.',
         'story_box': (871, 116, 518, 78), 'job_box': (268, 709, 182, 222),
         'challenge_box': (511, 708, 197, 215), 'fact_box': (303, 966, 710, 59)},
}


def recovered_text(c, month):
    data = CONTENT[month]
    ink = '#123d24' if month == 5 else '#183e64'
    for key in ['story', 'job', 'challenge', 'fact']:
        x, y, w, h = data[key+'_box']
        box(c, x, y, w, h, '#fffdf0', r=5)
        if key == 'job':
            for i, job in enumerate(data[key]):
                yy = y+29+i*54
                ellipse(c, x+9, yy-6, 5, 5, '#db9662')
                bottom = paragraph(c, x+21, yy, job, w-26, 20, 24, ink)
                assert bottom <= y+h, (month, key)
        else:
            size = 19 if key in ['story', 'fact'] else 22
            leading = 23 if key in ['story', 'fact'] else 29
            bottom = paragraph(c, x+3, y+23, data[key], w-7, size, leading, ink)
            assert bottom <= y+h+leading, (month, key, bottom, y+h)


TITLES = {2: 'Special Delivery', 5: 'Find the Butterflies!',
          9: 'Find the 6 Differences!', 10: 'Pumpkin Pairs', 11: 'Put the Storm Story in Order!'}
INSTRUCTIONS = {
    2: 'Follow each path. Which mailbox gets each letter?',
    5: 'Eight butterflies are hiding in the picture. Can you find them all?',
    9: 'These two pictures look almost the same. Can you find all 6 differences?',
    10: 'Find the 5 matching pairs. Which 2 pumpkins are left without a partner?',
    11: 'What happened first? Put the 4 pictures in the correct order.',
}


def header_text(c, m):
    fields = {2: (1177,448,265,91), 5:(1157,397,307,72),
              9:(902,686,538,34), 10:(1084,634,347,56), 11:(1227,644,244,54)}
    x,y,w,h = fields[m]
    box(c,x,y,w,h,'#fffdf0',r=4)
    end = paragraph(c,x+3,y+19,INSTRUCTIONS[m],w-7,17,20,'#16475b' if m==5 else '#1b4576')
    assert end <= y+h+20
    if m == 2:
        # Original title contains punctuation differing from the agreed title.
        box(c,900,454,247,41,'#f2d9a2',r=7)
        text(c,1023,487,TITLES[m],29,'#941e35',center=True)


def february(c, src):
    area = (867, 539, 608, 383)
    # Reuse the original village decoration, not the unusable raster path network.
    piece(c,src,(480,0,859,180),area,12)
    # Original illustrated letters and mailboxes remain unchanged in small clips.
    for crop,target in [
        ((870,542,970,604),(869,556,104,65)),
        ((870,616,970,681),(869,634,104,68)),
        ((870,691,970,755),(869,713,104,67)),
        ((870,768,971,834),(869,792,104,69)),
        ((1383,566,1474,633),(1380,555,91,67)),
        ((1383,645,1474,712),(1380,634,91,67)),
        ((1383,722,1474,789),(1380,713,91,67)),
        ((1383,799,1474,869),(1380,792,91,70)),
    ]:
        piece(c,src,crop,target,8)
    # Four independently parameterized cubic paths. Same style at every endpoint.
    # Distinct endpoint tangents and bridge gaps make crossings unambiguous.
    starts = [590,669,747,828]
    ends = [747,590,828,669]
    handles = [(1110,503,1255,875),(1125,821,1260,504),
               (1090,903,1250,670),(1118,654,1278,864)]
    curves = [[(971,sy),(a,b),(d,e),(1382,ey)] for sy,ey,(a,b,d,e) in zip(starts,ends,handles)]
    def bez(p,t):
        return ((1-t)**3*p[0][0]+3*(1-t)**2*t*p[1][0]+3*(1-t)*t*t*p[2][0]+t**3*p[3][0],
                (1-t)**3*p[0][1]+3*(1-t)**2*t*p[1][1]+3*(1-t)*t*t*p[2][1]+t**3*p[3][1])
    for pts in curves:
        for color,width in [('#ffffff',16),('#5593c7',10),('#a8daf1',5)]:
            c.setStrokeColor(HexColor(color)); c.setLineWidth(width);c.setLineCap(1)
            p=c.beginPath();p.moveTo(pts[0][0],PH-pts[0][1]);p.curveTo(*[v for x,y in pts[1:] for v in (x,PH-y)])
            c.drawPath(p)
    return {'answer':dict(zip('ABCD',[3,1,4,2])), 'curves':curves,
            'crossings':'independent cubics; white bridge outlines in drawing order',
            'editable':'native PDF cubic paths, geometry recorded here', 'area':area}


def may(c, src):
    # Correct only the erroneous B, retaining all other original calendar text.
    box(c,33,368,24,37,'#fffdf0',r=2)
    text(c,36,398,'3',24,'#145222')
    # Eight visually identified source butterflies, all inside the task picture.
    positions=[(910,498),(1170,533),(1403,620),(879,653),
               (1029,701),(1265,727),(894,797),(934,868)]
    assert len(set(positions))==8
    return {'answer':8,'source_positions':positions,'method':'original eight retained; positions individually inspected',
            'calendar_patch':'Monday 3 May: B replaced by native 3'}


def september(c, src):
    crop=(757,722,1108,940)
    targets=[(757,722,351,218),(1121,722,351,218)]
    diffs=['flag missing','flower color','one arch stone missing',
           'one extra berry','cloud missing','extra magnifying glass by Bao']
    for i,(x,y,w,h) in enumerate(targets):
        piece(c,src,crop,(x,y,w,h),14)
        # Both scenes contain the same small illustrated Bao and identical extras.
        piece(c,src,(25,702,175,887),(x+225,y+131,41,60),9)
        # Flag on the ruins: a defined added object, removed only on the right.
        if i==0:
            line(c,(x+110,y+51),(x+110,y+11),'#5c4527',2)
            poly(c,[(x+110,y+11),(x+129,y+15),(x+110,y+23)],'#e39a31','#915921',1)
        # Flower and berry cluster: fixed common construction with one mutation.
        for k in range(6):
            a=k*math.pi/3
            ellipse(c,x+50+7*math.cos(a),y+171+7*math.sin(a),4,6,
                    '#f277af' if i==0 else '#f5cf38','#8c703d',.6)
        ellipse(c,x+50,y+171,3,3,'#f4d355','#8c703d',.5)
        ellipse(c,x+117,y+187,16,10,'#517b39','#304e29',1)
        for dx,dy in [(-7,-3),(3,1)]+([(8,-4)] if i else []):
            ellipse(c,x+117+dx,y+187+dy,3,3,'#cf4952','#762b35',.5)
        # One added arch stone vs an empty wedge: exactly this polygon differs.
        stone=[(x+205,y+40),(x+219,y+39),(x+217,y+53),(x+207,y+56)]
        poly(c,stone,'#cead78' if i==0 else '#65b5df','#785b3d',1)
        # One controlled cloud at an otherwise common, clear sky position.
        if i==0:
            for dx,dy,rx,ry in [(-9,0,8,3),(-3,-3,7,5),(5,-2,7,4),(11,0,8,3)]:
                ellipse(c,x+87+dx,y+40+dy,rx,ry,'#fffdf1')
        # Bao's additional magnifier on the right only.
        if i:
            line(c,(x+277,y+188),(x+286,y+197),'#6f4926',4)
            ellipse(c,x+272,y+182,7,7,'#a9d6ec','#794c25',2)
    # Original mechanism remains common story art, outside the comparison panels.
    return {'answer':diffs,'count':6,'common_source_crop':crop,'targets':targets,
            'difference_centers_local':[(117,17),(50,171),(213,47),(117,187),(87,39),(274,185)],
            'method':'one original crop duplicated; six distinct native mutations only',
            'mechanism_in_comparison':'not included in either cropped scene; upper story illustration unchanged'}


def october(c, src):
    # Original seven illustrated motifs; actual pairs are made by reusing one crop.
    cols=[(761,879),(880,991),(996,1108),(1116,1232),(1237,1349),(1355,1470)]
    slots=[]
    for row in range(2):
        for i,(a,b) in enumerate(cols):
            slots.append((a,700+row*124,b-a,112))
    crops={
        'smile':(769,707,869,810),'flowers':(884,705,984,808),
        'triangle':(1002,705,1102,808),'cheeks':(1120,705,1220,808),
        'stars':(1243,705,1343,808),'hearts':(1359,705,1459,808),
        'leaf':(1243,829,1343,932),
    }
    ids=['smile','flowers','triangle','cheeks','stars','flowers',
         'hearts','smile','hearts','triangle','leaf','stars']
    box(c,758,696,714,245,'#fffdf0',r=9)
    for i,(x,y,w,h) in enumerate(slots):
        box(c,x+1,y,w-3,h,'#fffbea','#d9dcb4',r=11)
        # Exact same destination dimensions for every pumpkin ensure pair identity.
        # Exclude the original label badge while keeping each complete illustrated stem.
        xx=x+(w-100)/2; yy=y+5
        c.saveState(); p=c.beginPath(); p.moveTo(xx+31,PH-yy)
        for px,py in [(xx+100,yy),(xx+100,yy+103),(xx,yy+103),(xx,yy+30),(xx+31,yy+30)]:
            p.lineTo(px,PH-py)
        p.close();c.clipPath(p,stroke=0)
        piece(c,src,crops[ids[i]],(xx,yy,100,103))
        c.restoreState()
        ellipse(c,x+14,y+13,12,12,'#e6b568')
        text(c,x+14,y+20,'ABCDEFGHIJKL'[i],19,'#342517',center=True)
    freq=Counter(ids)
    pairs=['A-H','B-F','C-J','E-L','G-I']
    assert sorted(freq.values())==[1,1,2,2,2,2,2]
    assert [chr(65+i) for i,k in enumerate(ids) if freq[k]==1]==['D','K']
    return {'answer':{'pairs':pairs,'unpaired':['D','K']},'motif_ids':ids,
            'crops':crops,'slots':slots,'sprite_dimensions':[100,103],
            'method':'original illustrated pumpkins, exact source clips duplicated'}


def november(c, src):
    # Trim only the old A-D badge band; reuse the four actual story illustrations.
    crops=[(766,741,929,899),(947,741,1109,899),
           (1127,741,1290,899),(1308,741,1471,899)]
    order=[2,0,3,1]
    box(c,754,701,724,250,'#fffdf0',r=12)
    for i,state in enumerate(order):
        x=764+i*181
        piece(c,src,crops[state],(x,718,163,181),9)
        c.setStrokeColor(HexColor('#542e1a'));c.setLineWidth(2)
        c.circle(x+81.5,PH-925,21,stroke=1,fill=0)
    return {'answer':[3,1,4,2],'displayed_states':['fallen tree','clouds','star','wind'],
            'chronological_states':['clouds','wind','fallen tree','star'],
            'source_crops':crops,'source_order':order,'method':'original panels shuffled; no answer-revealing letter badges'}


def calendar_review(month):
    # Transcribed from the inspected source grids, not a second generated calendar.
    inspected={
        2:[[1,2,3,4,5,6,7],[8,9,10,11,12,13,14],[15,16,17,18,19,20,21],[22,23,24,25,26,27,28]],
        5:[[0,0,0,0,0,1,2],[3,4,5,6,7,8,9],[10,11,12,13,14,15,16],[17,18,19,20,21,22,23],[24,25,26,27,28,29,30],[31,0,0,0,0,0,0]],
        9:[[0,0,1,2,3,4,5],[6,7,8,9,10,11,12],[13,14,15,16,17,18,19],[20,21,22,23,24,25,26],[27,28,29,30,0,0,0]],
        10:[[0,0,0,0,1,2,3],[4,5,6,7,8,9,10],[11,12,13,14,15,16,17],[18,19,20,21,22,23,24],[25,26,27,28,29,30,31]],
        11:[[1,2,3,4,5,6,7],[8,9,10,11,12,13,14],[15,16,17,18,19,20,21],[22,23,24,25,26,27,28],[29,30,0,0,0,0,0]],
    }[month]
    assert inspected == calendar.Calendar(0).monthdayscalendar(2027,month)
    return {'year':2027,'inspected_rows':inspected,'positions_verified':calendar.monthrange(2027,month)[1],
            'may_original_B_corrected':month==5}


base=PdfReader(ROOT/BASE)
review_writer=PdfWriter()
replacement_pages={}
records=[]
builders={2:february,5:may,9:september,10:october,11:november}
for month in MONTHS:
    src=f'back-images-with-puzzles-v1/{month:02}.png'
    with Image.open(ROOT/src) as im:
        assert list(im.size)==REG['assets'][src]['pixels'] and im.mode=='RGB'
    mem=io.BytesIO()
    c=canvas.Canvas(mem,pagesize=(PW,PH))
    c.drawImage(str(ROOT/src),0,0,PW,PH)
    # Original prose and original lettering retained per latest preservation instruction.
    tr=tracker(c,src,month)
    header_text(c,month)
    puzzle=builders[month](c,src)
    c.showPage();c.save();mem.seek(0)
    page=PdfReader(mem).pages[0]
    page.scale_to(float(base.pages[2*month].mediabox.width),float(base.pages[2*month].mediabox.height))
    replacement_pages[2*month]=page
    review_writer.add_page(page)
    # Native final instructions and recovered prose must survive export.
    native=' '.join(page.extract_text().split())
    assert INSTRUCTIONS[month] in native, (month,'instruction')
    records.append({'month':month,'source':src,'title':TITLES[month],'instruction':INSTRUCTIONS[month],
                    'calendar':calendar_review(month),'tracker':tr,'puzzle':puzzle,
                    'text_status':'Original full prose retained; recovered wording remains a separate editorial comparison', 'visual_review':'pending','user_review':'pending'})

review_writer.add_metadata({'/Title':'Giggle Dumplings - Five original-designed backs REVIEW v22',
                            '/Subject':'Working review; February, May, September, October, November. Not print released.'})
with (ROOT/REVIEW).open('wb') as f:
    review_writer.write(f)
master_writer=PdfWriter()
for i,p in enumerate(base.pages):
    master_writer.add_page(replacement_pages.get(i,p))
master_writer.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v22',
                            '/Subject':'Working master. Five locally corrected original-designed lower pages; user/print review pending.'})
with (ROOT/MASTER).open('wb') as f:
    master_writer.write(f)
check=PdfReader(ROOT/MASTER)
unchanged=[]
for i,p in enumerate(check.pages):
    if i not in replacement_pages:
        assert p.get_contents().get_data()==base.pages[i].get_contents().get_data(), i
        unchanged.append(i+1)
assert len(check.pages)==26 and len(unchanged)==21
manifest={'date':'2026-10-06','status':'working_master','print_status':'not_released',
          'base':BASE,'master':MASTER,'review':REVIEW,'months':records,
          'sources':{s:REG['assets'][s]['sha256'] for s in SOURCES},
          'preserved_page_content_streams':unchanged,'replaced_pages':[i+1 for i in replacement_pages],
          'image_generation_calls':0,'original_files_modified':False,
          'visual_review':'pending','user_review':'pending',
          'remaining_months':[1,3,4,6,7,8,12],
          'issues':['Exact recovered prose wording vs original full text remains an editorial comparison.', 'Original January puzzle unresolved.', 'Remaining seven months not completed.',
                    'Gelato template, resolution, binding, bleed and final print checks open.']}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Five lower pages built; 21 other content streams unchanged; zero image generation calls.')
