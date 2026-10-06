"""Six bounded puzzle corrections using original design sources and native geometry.

December's rejected puzzle is never reused: only surrounding reference decoration
is retained, with its entire puzzle and erroneous tracker replaced. Originals and
all approved master pages remain unchanged. Outputs are staged for visual review.
"""
import ast, calendar, hashlib, io, json, math
from collections import Counter
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT=Path(__file__).resolve().parents[1]
PW,PH=1492,1054
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v23.pdf'
MONTHS=[3,4,6,7,8,12]
COMP=ROOT/'production/month-backs/remaining-v24'
STAGED=ROOT/'tmp/pdfs/remaining/candidate-v24d.pdf'
reg=json.loads((ROOT/'production/assets.json').read_text())
sources={m:f'back-images-with-puzzles-v1/{m:02}.png' for m in MONTHS if m!=12}
sources[12]='back-images-with-puzzles-v1/12_not_correct.png'
refs=['back-images-with-puzzles-v1/02.png','back-images-with-puzzles-v1/05.png','back-images-with-puzzles-v1/08.png']
for rel in [BASE]+list(sources.values())+refs:
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==reg['assets'][rel]['sha256'],rel
COMP.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('OriginalText','/System/Library/Fonts/MarkerFelt.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hand','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
# Reuse the already reviewed PDF clip/text helpers, without executing its builder.
helper='tools/build-original-backs-batch-v22.py'
tree=ast.parse((ROOT/helper).read_text())
definitions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
             ['box','text','paragraph','piece','poly','ellipse','line']]
exec(compile(ast.Module(body=definitions,type_ignores=[]),helper,'exec'),globals())

TITLES={3:'Seed Trail',4:'Find the Matching Eggs!',6:'Who Took the Strawberries?',
        7:'Which Shadow Belongs to the Castle?',8:'Who Lives Here?',12:'Complete the Last Star!'}
TASKS={3:'What comes next? Complete the two patterns!',4:'Two eggs are exactly the same. Can you find them?',
       6:'The strawberries are gone! Read the clues and find out who took them.',
       7:'Look carefully! Which shadow matches the sandcastle exactly?',
       8:'Match each woodland animal to its home.',12:'One piece is missing. Which piece completes the star exactly?'}
records=[]


def star_points(x,y,r,inner=.45,n=5):
    return [(x+math.cos(-math.pi/2+i*math.pi/n)*(r if i%2==0 else r*inner),
             y+math.sin(-math.pi/2+i*math.pi/n)*(r if i%2==0 else r*inner)) for i in range(2*n)]


def tracker(c,m):
    # Exact twelve-position vector tracker, confined to the original tracker strip.
    fields={3:(884,175,488,41),4:(837,166,385,42),6:(839,75,582,43),
            7:(826,75,593,42),8:(888,79,528,44),12:(918,56,524,43)}
    x,y,w,h=fields[m];box(c,x,y,w,h,'#fffdf0',r=4)
    for i in range(12):
        xx=x+18+i*(w-36)/11
        p=star_points(xx,y+h/2,15.5)
        poly(c,p,'#f6be36' if i<m else '#fffdf0','#956925' if i<m else '#92795c',1.9)
        if i<m:
            poly(c,star_points(xx-1,y+h/2-1,10),'#ffdc60','#ffdc60',.2)
    return {'filled':m,'empty':12-m,'total':12,'region':fields[m]}


def task(c,m):
    fields={3:(1118,453,259,59),4:(1190,435,258,81),6:(899,725,564,42),
            7:(875,742,574,32),8:(887,675,555,37),12:(1185,662,285,66)}
    x,y,w,h=fields[m];box(c,x,y,w,h,'#fffdf0',r=5)
    end=paragraph(c,x+3,y+20,TASKS[m],w-6,18,21,'#224c64')
    assert end<=y+h+21,(m,end,y+h)
    # Only titles which differ from the fixed plan need a native replacement.
    title_fields={3:(886,459,211,43,30),6:(890,696,575,34,32)}
    if m in title_fields:
        xx,yy,ww,hh,size=title_fields[m]
        box(c,xx,yy,ww,hh,'#f2d9a2' if m==3 else '#fffdf0',r=7)
        text(c,xx+ww/2,yy+hh-6,TITLES[m],size,'#774024' if m==3 else '#164627',center=True)


def seed_icon(c,kind,x,y,size=1):
    c.saveState();c.translate(x,PH-y);c.scale(size,size)
    # Use local PH=0 so helper top coordinates map around the icon center.
    def el(xx,yy,rx,ry,col,stroke='#5b6335'):
        c.setFillColor(HexColor(col));c.setStrokeColor(HexColor(stroke));c.setLineWidth(1)
        c.ellipse(xx-rx,-yy-ry,xx+rx,-yy+ry,fill=1,stroke=1)
    def ln(a,b,col,width=2):
        c.setStrokeColor(HexColor(col));c.setLineWidth(width);c.line(a[0],-a[1],b[0],-b[1])
    if kind=='sunflower':
        el(0,0,10,23,'#474732','#252b22')
        for dx in [-4,1,5]:ln((dx,-17),(dx-2,17),'#e5dabc',1.4)
    elif kind=='acorn':
        el(0,4,14,19,'#b67c39','#704b2b');el(0,-9,16,8,'#83683e','#534126')
        for dx in [-9,-3,3,9]:ln((dx-2,-12),(dx+3,-5),'#b7995c',1)
        ln((0,-17),(3,-23),'#6a4a2b',3)
    elif kind=='pumpkin':
        el(0,0,12,22,'#7b9b48');el(-2,-2,7,17,'#9eba67','#8dad58')
    elif kind=='sprout':
        ln((0,22),(0,-6),'#537f35',3)
        el(-9,-6,12,6,'#89b15c');el(9,-12,12,6,'#6b9b46')
        ln((-4,22),(5,22),'#98794a',2)
    elif kind=='tulip':
        ln((0,22),(0,-1),'#537f35',3);el(-8,10,9,4,'#79a74a')
        p=c.beginPath();pts=[(-14,-16),(-7,-8),(0,-18),(7,-8),(14,-16),(10,0),(0,5),(-10,0)]
        p.moveTo(pts[0][0],-pts[0][1])
        for xx,yy in pts[1:]:p.lineTo(xx,-yy)
        p.close();c.setFillColor(HexColor('#e77f9b'));c.setStrokeColor(HexColor('#a44c6d'));c.drawPath(p,fill=1,stroke=1)
    c.restoreState()


def march(c,src):
    box(c,861,518,615,308,'#fffdf0',r=12)
    seqs=[['sunflower','acorn','pumpkin']*2+['sunflower'],['sprout','sprout','tulip']*2+['sprout','sprout']]
    choices=[['sunflower','pumpkin','acorn','sprout'],['sprout','tulip','sunflower','acorn']]
    for row,(seq,opts) in enumerate(zip(seqs,choices)):
        y=557+row*143
        box(c,869,y-27,595,124,'#fffbea','#b8c688',r=12)
        text(c,888,y+8,str(row+1),27,'#637b36')
        spacing=520/(len(seq)+1)
        for i,k in enumerate(seq):seed_icon(c,k,935+i*spacing,y+5,.75)
        text(c,935+len(seq)*spacing,y+16,'?',29,'#a9576b',center=True)
        for i,k in enumerate(opts):
            x=997+i*120
            text(c,x-33,y+81,'ABCD'[i],19,'#5f6132',center=True)
            seed_icon(c,k,x,y+74,.53)
    assert choices[0][2]=='acorn' and choices[1][1]=='tulip'
    return {'answer':{'row1':'C - acorn','row2':'B - tulip'},'sequences':seqs,'choices':choices,
            'periods':[3,3],'method':'two controlled vector patterns and four options per pattern'}


def april(c,src):
    cols=[867,973,1080,1188,1294,1401]
    crops={'pink':(cols[0]-50,559,cols[0]+50,680),'blue':(cols[1]-50,559,cols[1]+50,680),
           'gold':(cols[2]-50,559,cols[2]+50,680),'green':(cols[3]-50,559,cols[3]+50,680),
           'zigzag':(cols[4]-50,559,cols[4]+50,680),'hearts':(cols[5]-50,559,cols[5]+50,680),
           'red':(cols[0]-50,730,cols[0]+50,851),'stars':(cols[1]-50,730,cols[1]+50,851),
           'confetti':(cols[5]-50,730,cols[5]+50,851)}
    ids=['pink','blue','gold','green','zigzag','hearts','red','gold','stars','confetti']
    box(c,814,515,658,344,'#fffdf0',r=15)
    targets=[]
    for i,key in enumerate(ids):
        x=827+(i%5)*127;y=548+(i//5)*167
        piece(c,src,crops[key],(x+11,y,100,121),9)
        text(c,x+61,y-9,'ABCDEFGHIJ'[i],21,'#44523a',center=True)
        targets.append((x+11,y,100,121))
    freq=Counter(ids);assert sorted(freq.values())==[1]*8+[2]
    assert [chr(65+i) for i,k in enumerate(ids) if freq[k]==2]==['C','H']
    return {'answer':['C','H'],'motifs':ids,'source_crops':crops,'targets':targets,
            'method':'ten original egg images; only C/H reuse exactly one source crop'}


def duck(c,x,y,z=1):
    ellipse(c,x,y+20*z,27*z,21*z,'#e7bf55','#73522e',1.6)
    ellipse(c,x-2*z,y+21*z,17*z,12*z,'#f7d77b','#ab7d37',1.1)
    ellipse(c,x+10*z,y-3*z,21*z,21*z,'#f1ce68','#73522e',1.6)
    ellipse(c,x+13*z,y-6*z,4*z,5*z,'#fffdf0','#725032',.7)
    ellipse(c,x+14*z,y-6*z,2*z,3*z,'#332d22')
    poly(c,[(x+26*z,y),(x+45*z,y+7*z),(x+27*z,y+11*z)],'#e99736','#805223',1)
    for dx in [-10,9]:poly(c,[(x+dx*z,y+38*z),(x+(dx-8)*z,y+45*z),(x+(dx+7)*z,y+45*z)],'#df9237','#805223',.7)


def fox(c,x,y,z=1):
    ellipse(c,x+24*z,y+28*z,16*z,30*z,'#d58339','#714a30',1.4)
    ellipse(c,x+27*z,y+8*z,11*z,12*z,'#fff0d9','#c99d70',.7)
    ellipse(c,x,y+28*z,22*z,28*z,'#dd8e40','#714a30',1.5)
    ellipse(c,x-1*z,y+34*z,12*z,21*z,'#fff0d9','#c99d70',.7)
    for dx in [-15,15]:
        poly(c,[(x+(dx-10)*z,y-9*z),(x+dx*z,y-36*z),(x+(dx+9)*z,y-10*z)],'#c77635','#714a30',1.3)
        poly(c,[(x+(dx-4)*z,y-12*z),(x+dx*z,y-27*z),(x+(dx+4)*z,y-12*z)],'#e6b386','#714a30',.5)
    poly(c,[(x-25*z,y-13*z),(x+25*z,y-13*z),(x+20*z,y+8*z),(x,y+24*z),(x-20*z,y+8*z)],'#e09a4c','#714a30',1.4)
    poly(c,[(x-21*z,y),(x,y+20*z),(x+21*z,y),(x+13*z,y+18*z),(x,y+24*z),(x-13*z,y+18*z)],'#fff0d9','#c99d70',.6)
    for dx in [-10,10]:ellipse(c,x+dx*z,y,3*z,4*z,'#332d22')
    ellipse(c,x,y+18*z,4*z,3*z,'#332d22')
    line(c,(x,y+21*z),(x,y+26*z),'#714a30',1)


def june(c,src):
    # Redaction limited to the obsolete title/incorrect plural missing-item story.
    box(c,889,19,546,57,'#fffdf0',r=12)
    text(c,1161,60,'The Picnic Mystery',42,'#153e26',center=True)
    box(c,858,140,545,65,'#fffdf0',r=7)
    text(c,1130,162,'But when they arrive, their strawberries are missing!',19,'#224c68',center=True)
    text(c,1130,184,'Can they find out who took them?',19,'#224c68',center=True)
    box(c,758,770,714,164,'#fffdf0',r=12)
    suspects=['Rabbit','Squirrel','Duck','Nibbles']
    for i,name in enumerate(suspects):
        x=769+(i%2)*182;y=777+(i//2)*76
        box(c,x,y,176,70,'#fffbea','#b9cda7',r=9)
        if name=='Rabbit':piece(c,'back-images-with-puzzles-v1/05.png',(1375,715,1468,888),(x+7,y+3,47,63),10)
        elif name=='Squirrel':piece(c,'back-images-with-puzzles-v1/08.png',(1320,721,1421,818),(x+5,y+4,65,61),10)
        elif name=='Nibbles':piece(c,src,(1085,426,1235,590),(x+4,y+2,64,66),10)
        else:duck(c,x+28,y+25,.68)
        text(c,x+114,y+40,name,18,'#315326',center=True)
    clues=['Clue 1: Small footprints were found beside the basket.',
           'Clue 2: Whoever took the strawberries did not have wings.',
           'Clue 3: A turquoise circle was found beside the empty basket.']
    for i,s in enumerate(clues):paragraph(c,1146,789+i*48,s,310,17,19,'#285239')
    return {'answer':'Nibbles','suspects':suspects,'clues':clues,
            'wings':[False,False,True,False],'turquoise_glasses':[False,False,False,True],
            'method':'original animal/Nibbles clips; native winged duck; three explicit exclusion clues'}


# Traced exterior of the actual illustrated source castle (crop-relative).
CASTLE=[(61,384),(85,342),(101,338),(111,276),(109,247),(113,230),(113,200),(123,200),
 (129,196),(141,159),(141,123),(149,123),(149,127),(174,130),(180,138),(153,143),(148,139),
 (148,171),(161,210),(174,235),(180,217),(185,207),(203,157),(207,151),(207,121),(213,121),
 (214,131),(237,138),(212,145),(212,159),(228,207),(237,216),(242,158),(251,153),(267,112),
 (276,90),(276,81),(282,83),(282,95),(300,125),(307,130),(308,108),(298,110),(298,91),
 (320,92),(327,55),(327,19),(335,19),(335,27),(356,27),(364,32),(374,33),(382,30),
 (380,39),(376,44),(381,48),(363,51),(337,45),(337,59),(351,89),(365,98),(366,157),
 (380,151),(398,113),(400,57),(408,57),(408,67),(432,71),(443,78),(456,76),(448,87),
 (427,92),(408,87),(408,118),(432,161),(435,202),(440,211),(440,201),(451,201),(451,214),
 (460,214),(465,230),(470,231),(481,262),(487,245),(497,226),(505,249),(510,266),
 (520,269),(530,282),(535,319),(550,348),(560,376),(573,401),(558,439),(539,446),
 (454,448),(422,436),(351,443),(311,450),(268,438),(229,438),(210,425),(148,414),(112,403),(69,390)]


def july(c,src):
    box(c,756,774,714,158,'#fffdf0',r=11)
    a=[(x,y-50 if 180<=x<=237 and y<=218 else y) for x,y in CASTLE]
    b=[(670-x if 19<=y<=51 and x>=335 and x<390 else x,y) for x,y in CASTLE]
    d=[(x,y+70 if 470<=x<=535 and y<283 else y) for x,y in CASTLE]
    variants=[a,b,CASTLE,d]
    assert variants[2]==CASTLE and all(p!=CASTLE for i,p in enumerate(variants) if i!=2)
    # The colored reference and C share the same actual source contour.
    for i,p in enumerate([CASTLE]+variants):
        ox=768+i*140;oy=799;s=.248
        pts=[(ox+(x-61)*s,oy+(y-19)*s) for x,y in p]
        if i==0:
            c.saveState();path=c.beginPath();path.moveTo(pts[0][0],PH-pts[0][1])
            for x,y in pts[1:]:path.lineTo(x,PH-y)
            path.close();c.clipPath(path,stroke=0)
            # Original photograph-like illustration, clipped by the shared contour.
            piece(c,src,(740+61,187+19,740+573,187+450),(ox,oy,512*s,431*s))
            c.restoreState()
            c.setStrokeColor(HexColor('#aa7b26'));c.setLineWidth(1);c.drawPath(path,stroke=1,fill=0)
            text(c,ox+64,793,'Reference',17,'#785733',center=True)
        else:
            poly(c,pts,'#173c52','#173c52',.7)
            text(c,ox+64,793,'ABCD'[i-1],21,'#173c52',center=True)
    return {'answer':'C','source_castle_crop_origin':[740,187], 'reference_polygon':CASTLE,
            'options':variants,'exact_geometry_shared':True,'original_option_count':4,
            'method':'original illustrated castle clipped by traced contour; C duplicates that contour; three explicit contour mutations'}


def burrow(c,x,y,kind):
    if kind=='burrow':
        ellipse(c,x,y+25,49,25,'#987246','#61482c',1.5)
        ellipse(c,x-8,y+28,20,17,'#342c23','#5c452e',1.3)
        for dx in [-33,-20,11,26,37]:line(c,(x+dx,y+7),(x+dx+3,y-5),'#6a8c3e',2)
        for dx in [-27,20,38]:ellipse(c,x+dx,y+18,6,3,'#bb9259','#997244',.7)
    else:
        for dx,dy,rx,ry in [(-34,25,20,17),(-10,7,25,19),(23,15,28,21),(44,34,15,14)]:
            ellipse(c,x+dx,y+dy,rx,ry,'#8f998f','#556354',1.2)
        ellipse(c,x,y+33,22,18,'#2c352c','#556354',1.3)
        for dx in [-32,27]:ellipse(c,x+dx,y+45,12,4,'#71884d','#4e6436',.8)


def august(c,src):
    # Original August numbers are shifted six weekdays. Reuse the original glyphs.
    x0=23;y0=323;cw=100.5;old_rh=56;rh=280/6
    digit_crops={}
    for day in range(1,32):
        row,col=divmod(day-1,7)
        xx=35+col*cw; yy=343+row*old_rh
        digit_crops[day]=(xx-2,yy-3,xx+(22 if day>=10 else 12),yy+16)
    # Six weeks are needed in August 2027; preserve the original weekday header
    # and bottom woodland decoration, and reuse every original number glyph.
    box(c,23,323,703.5,280,'#fffdf0')
    for j in range(8):line(c,(23+j*cw,323),(23+j*cw,603),'#c2d8ca',.7)
    for j in range(7):line(c,(23,323+j*rh),(726.5,323+j*rh),'#c2d8ca',.7)
    placements=[]
    for row,days in enumerate(calendar.Calendar(0).monthdayscalendar(2027,8)):
        for col,day in enumerate(days):
            if day:
                crop=digit_crops[day];w=crop[2]-crop[0];h=crop[3]-crop[1]
                dst=(33+col*cw,338+row*rh,w,h)
                piece(c,src,crop,dst)
                placements.append({'day':day,'weekday':col,'row':row,'source':crop,'target':dst})
    assert placements[0]['weekday']==6 and placements[-1]['weekday']==1
    box(c,765,714,706,225,'#fffdf0',r=12)
    for i,name in enumerate(['Owl','Rabbit','Squirrel','Fox']):
        xx=779+i*171;yy=722
        box(c,xx,yy,159,94,'#fffbea','#a9c5a4',r=10)
        if name=='Owl':piece(c,src,(818,720,903,816),(xx+49,yy+2,62,65),9)
        elif name=='Rabbit':piece(c,'back-images-with-puzzles-v1/05.png',(1375,715,1468,888),(xx+57,yy+1,46,66),9)
        elif name=='Squirrel':piece(c,src,(1320,721,1421,818),(xx+43,yy+5,73,65),9)
        else:fox(c,xx+71,yy+26,.60)
        text(c,xx+80,yy+86,name,17,'#35532c',center=True)
    homes=['nest','den','tree hollow','burrow']
    for i,name in enumerate(homes):
        xx=779+i*171;yy=826
        box(c,xx,yy,159,102,'#fffbea','#a9c5a4',r=10)
        if name=='nest':piece(c,src,(1350,843,1470,937),(xx+32,yy+10,96,69),8)
        elif name=='tree hollow':piece(c,src,(812,843,936,937),(xx+33,yy+10,94,69),8)
        else:burrow(c,xx+81,yy+28,name)
        text(c,xx+13,yy+20,str(i+1),19,'#41694c',center=True)
        text(c,xx+81,yy+92,name,16,'#35532c',center=True)
    return {'answer':{'Owl':3,'Rabbit':4,'Squirrel':1,'Fox':2},'homes':homes,
            'calendar_positions':placements,'calendar_original_error':'1 August originally Monday; corrected to Sunday',
            'method':'original owl/rabbit/squirrel/home clips plus native fox and distinct burrow/rock-den'}


def december(c,src):
    area=(760,721,714,280)
    # Completely remove the rejected five-point-star puzzle within its own panel.
    box(c,*area,'#fffdf0',r=14)
    cx,cy=899,862;r=96;inner=.57
    pts=star_points(cx,cy,r,inner,12)
    cut=list(range(3,8))
    missing=[(cx,cy)]+[pts[i] for i in cut]
    colors=['#f8c53f','#efac25','#ffe180','#e89d23']
    for i in range(24):
        if i in [3,4,5,6]:continue
        poly(c,[(cx,cy),pts[i],pts[(i+1)%24]],colors[i%4],'#b37923',.9)
    outline=[pts[i] for i in range(0,4)]+[(cx,cy)]+[pts[i] for i in range(7,24)]
    poly(c,missing,'#fffdf0','#715733',1.6)
    # Draw outer edges only where facets exist; the cut boundary is explicit.
    for i in range(24):
        if i not in [3,4,5,6]:line(c,pts[i],pts[(i+1)%24],'#a66c1e',2)
    normalized=[(x-cx,y-cy) for x,y in missing]
    a=[(x-14 if i==2 else x,y) for i,(x,y) in enumerate(normalized)]
    b=[(x,y+17 if i==3 else y) for i,(x,y) in enumerate(normalized)]
    d=[(x+17 if i==4 else x,y) for i,(x,y) in enumerate(normalized)]
    options=[a,b,normalized,d]
    assert options[2]==normalized and all(v!=normalized for i,v in enumerate(options) if i!=2)
    for i,p in enumerate(options):
        ox=1007+i*112;oy=874;z=1
        q=[(ox+x*z,oy+y*z) for x,y in p]
        # Uniform scale and orientation for the cut and all four choices.
        poly(c,q,'#f6bd36','#795825',1.6)
        for j in range(1,len(q)-1):poly(c,[q[0],q[j],q[j+1]],colors[j%4],'#b37923',.7)
        text(c,ox+43,781,'ABCD'[i],23,'#22516e',center=True)
    for xx,yy in [(790,774),(1011,961),(792,945)]:poly(c,star_points(xx,yy,10),'#f5c03e','#af7b27',.8)
    return {'answer':'C','star_points':12,'full_star_polygon':pts,'missing_polygon':missing,
            'normalized_options':options,'option_scale':1,'reference_scale':1,
            'source_restriction':'Rejected original used as surrounding design reference only; entire invalid puzzle and tracker replaced.',
            'method':'24-vertex twelve-point star; one exact geometric cut reused as C; faceted gold native vectors'}


builders={3:march,4:april,6:june,7:july,8:august,12:december}
writer=PdfWriter();base=PdfReader(ROOT/BASE)
for month in MONTHS:
    src=sources[month];mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH))
    c.drawImage(str(ROOT/src),0,0,PW,PH)
    tr=tracker(c,month);task(c,month);proof=builders[month](c,src)
    c.save();mem.seek(0);p=PdfReader(mem).pages[0]
    p.scale_to(float(base.pages[2*month].mediabox.width),float(base.pages[2*month].mediabox.height))
    assert TASKS[month] in ' '.join(p.extract_text().split()),month
    writer.add_page(p)
    if month!=8:
        # Transcribed source grid starts verified in the inspected source pages.
        first_seen={3:0,4:3,6:1,7:3,12:2}[month]
        assert calendar.weekday(2027,month,1)==first_seen
    records.append({'month':month,'source':src,'title':TITLES[month],'task':TASKS[month],
                    'tracker':tr,'puzzle':proof,'calendar_day_count':calendar.monthrange(2027,month)[1],
                    'original_prose_and_lettering':'retained except June title and missing-strawberry story correction',
                    'visual_review':'pending','user_review':'pending'})
writer.add_metadata({'/Title':'Giggle Dumplings - six corrected backs WORKING REVIEW v24',
                     '/Subject':'March, April, June, July, August, December. Native corrections to original design. No print release.'})
with STAGED.open('wb') as f:writer.write(f)
manifest={'date':'2026-10-06','base':BASE,'months':records,
          'sources':{r:reg['assets'][r]['sha256'] for r in [BASE]+list(sources.values())+refs},
          'visual_review':'pending','user_review':'pending','print_status':'not_released',
          'image_generation_calls':0,'january':'Original retained; route uniqueness still unproved. No discarded answer C reused.',
          'february':'User accepted v23 difficulty on 2026-10-06; retain unchanged.',
          'october':'User accepted v22 design on 2026-10-06; retain unchanged.'}
(COMP/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Staged six corrected original-design backs; pairs and exact-match geometry verified.')
