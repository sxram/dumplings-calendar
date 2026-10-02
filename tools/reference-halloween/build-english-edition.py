"""English edition from the final DE artwork, with independent editable text layers.

No new illustrations and no raster retouching. PDF text is removed structurally;
German raster captions receive narrowly bounded vector replacements. Source files
remain unchanged. Run with the bundled Python runtime. User visual review is open.
"""
from pathlib import Path
import io, json, hashlib, copy, math, subprocess, re, argparse
from collections import Counter
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, NameObject, DecodedStreamObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

R=Path(__file__).resolve().parents[1]
E=R/'editions/en'; O=E/'output/v01'; S=E/'sources/v01'
parser=argparse.ArgumentParser()
parser.add_argument('--replace-draft',action='store_true',help='Explicitly rebuild the unapproved English v01 draft only.')
args=parser.parse_args()
if (O/'Giggle-Dumplings-Halloween-EN-Interior-v01.pdf').exists():
    if not args.replace_draft:raise SystemExit('English v01 already exists. Use a new version for approved files; --replace-draft only for unapproved working files.')
    if (O/'manifest.json').exists():assert json.loads((O/'manifest.json').read_text())['user_visual_review']=='pending'
O.mkdir(parents=True,exist_ok=True); S.mkdir(parents=True,exist_ok=True)
reg=json.loads((R/'production/assets.json').read_text()); used={}; checks=[]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source(key):
    a=reg['assets'][key]; p=R/a['path']; assert digest(p)==a['sha256'],key
    used[key]={'path':a['path'],'sha256':a['sha256']}; return p
def registered_path(rel):
    key=next(k for k,a in reg['assets'].items() if a['path']==rel)
    return source(key)
def savejson(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
fonts=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype'
for n,f in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(fonts/f)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
pdfmetrics.registerFont(TTFont('Display','/System/Library/Fonts/Supplemental/Chalkboard.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Cover','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CoverBold','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=1))

# One editable language contract, seeded once; subsequent builds respect edits.
tp=E/'texts-v01.json'
if not tp.exists():
    old=json.loads((R/'01-concept/book-texts-v01.json').read_text())
    motifs=json.loads((R/'01-concept/motifs-v01.json').read_text())
    if isinstance(motifs,dict):motifs=motifs['motifs']
    t={'language':'en-US','subtitle':'The Big Halloween Special',
       'motifs':{m['id']:m['title']['en'] for m in motifs},
       'stories':{k:{'title':v['title']['en'],'panels':[p['lines']['en'] for p in v['panels']]} for k,v in old.items() if re.fullmatch('[CWK][0-9]{2}',k)},
       'ui':{k:v['en'] for k,v in old['ui'].items()},
       'crafts':{k:{f:v[f]['en'] for f in ['title','instruction']} for k,v in old['crafts'].items() if k!='B06'}}
    t['stories']['C01']['panels'][2]=['Pips: Boo.']
    t['stories']['C01']['panels'][3]=['Pips: I wanted to scare you.','Mochi: You did! We don’t have nearly enough cookies!']
    t['stories']['C05']['panels'][0]=['Pips: I guess I’m not scary.','Mochi: You still belong with us!']
    t['stories']['C05']['panels'][2]=['Pips: Boo.','Dreamy: I’ve always wanted such a gentle alarm clock.']
    t['stories']['C06']['panels'][3]=['Spider: Boo.','Nibbles: My cookie’s gone! NOW that’s scary!']
    t['stories']['K03']['panels'][0]=['Mochi: Want to go for a flight?','Dreamy: Is it comfy?']
    t['ui']['content_line']='30 coloring pages · 8 puzzles · 6-page comic story · 4 picture jokes · 4 mini comics · 7 craft pages'
    t['ui']['craft_intro_text']='You’ll need colored pencils, scissors, glue and some thin cardboard. You’ll also need string for the garland and door sign. Color first, then cut along the solid outer lines. Fold only along the dashed lines. Ask an adult to help with cutting, especially the eye holes. Only cut out the craft templates at the back of the book.'
    t['crafts']['B01']={'title':'My Dumpling Monster Mask','lines':['1  Color the mask and glue it onto thin cardboard.','2  Cut along the outer black outline.','3  Ask an adult to cut out the eyes along the inner black circles.','4  Glue a sturdy cardboard handle behind one cheek.','Ask an adult to help with cutting. Do not fold the mask.']}
    t['crafts']['B02']={'title':'My Pumpkin Mask','lines':['1  Color the pumpkin and glue it onto thin cardboard.','2  Cut out the pumpkin, leaf and stem. Leave the stars behind.','3  Ask an adult to cut out the eyes along the inner black circles.','4  Glue a sturdy cardboard handle behind one cheek.','Ask an adult to help with cutting.']}
    t['crafts']['B07']={'title':'My Reversible Door Sign','subtitle':'Two sides — one sign to turn around.','lines':['1  Color both sides of the sign.','2  Cut along the outer rounded rectangles.','3  Glue the blank backs together, lining up the top edges.','4  Ask an adult to cut the top hole through both layers.','5  Thread a short string through the hole and hang up your sign.'],'signs':[['Haunted','in here!'],['Ghost','on a','break']]}
    t['crafts']['B08']={'title':'Our Halloween Garland','lines':['1. Color all six friends.','2. Cut out the pennants along the solid outer lines.','3. Fold the tabs back along the dashed lines.','4. Place string inside the folds and glue the tabs to the backs.'],'tab':'Glue tab','legend':'Solid line: cut    Dashed line: fold'}
    t['puzzles']=[{'title':'Hidden Pictures','instruction':'Find these 8 Halloween objects.'}, {'title':'Pumpkin Maze','instruction':'Help Dreamy reach the little ghost.'}, {'title':'Spot the Differences','instruction':'Find 5 differences between the pictures.'}, {'title':'Baking Differences','instruction':'Find 6 differences between the pictures.'}, {'title':'Which Shadow Matches?','instruction':'Circle Nibbles’ matching shadow.'}, {'title':'Match the Pairs','instruction':'Match each friend to a Halloween symbol.'}, {'title':'Picture Sudoku','instruction':'Use each symbol once in every row'}, {'title':'Mirror Image','instruction':'Circle Bao’s matching mirror image.'}]
    savejson(tp,t)
t=json.loads(tp.read_text())

def overlay(fn,size=(612,792)):
    b=io.BytesIO();c=canvas.Canvas(b,pagesize=size,pageCompression=1);fn(c);c.showPage();c.save();b.seek(0);return PdfReader(b).pages[0]
def line(c,text,x,y,fs=12,font='Body',width=465,center=False):
    f=min(fs,width/pdfmetrics.stringWidth(text,font,1)) if text else fs
    assert f>=fs*.65,(text,f)
    c.setFillGray(0);c.setFont(font,f)
    (c.drawCentredString if center else c.drawString)(x,y,text)
    return f
def para(c,text,x,top,width,height,fs=13,font='Body'):
    for size in [fs-i*.5 for i in range(12) if fs-i*.5>=9]:
        p=Paragraph('<br/>'.join(escape(s) for s in text) if isinstance(text,list) else escape(text),ParagraphStyle('en',fontName=font,fontSize=size,leading=size*1.22))
        _,h=p.wrap(width,height)
        if h<=height:break
    assert h<=height,(text,h,height)
    p.drawOn(c,x,top-h);checks.append({'text':str(text)[:70],'font_size':size,'height':round(h,2),'available':height})
def footer(c,num,rule=False):
    if rule:c.setStrokeGray(0);c.setLineWidth(.715);c.line(78.3,49.2,543.6,49.2)
    line(c,'Giggle Dumplings',78.3,36,8.8)
    c.setFont('Body',8.8);c.drawRightString(543.6,36,str(num))
def header(c,title,kind):
    line(c,{'coloring':'COLORING FUN','comic':'COMIC STORY','mini':'MINI COMIC','jokes':'PICTURE JOKE','crafts':'CRAFT TIME','front':'ENGLISH EDITION'}[kind],78.3,750.75,9.35,'Bold')
    line(c,title,78.3,711.7,23.1,'Display')

# Suppress text-showing operators while retaining text matrices and graphics state.
# This removes text even when Ghostscript combines it with other state in a BT block.
showops={b'Tj',b'TJ',b"'",b'"'}
def strip_text(page):
    cs=page.get_contents()
    if cs is not None:cs.operations=[(a,o) for a,o in cs.operations if o not in showops];page[NameObject('/Contents')]=cs
    seen=set()
    def walk(res):
        for ob in res.get('/XObject',{}).values():
            obj=ob.get_object()
            if id(obj) in seen:continue
            seen.add(id(obj))
            if obj.get('/Subtype')=='/Form':
                cs=ContentStream(obj,page.pdf);cs.operations=[(a,o) for a,o in cs.operations if o not in showops]
                obj.set_data(cs.get_data());walk(obj.get('/Resources',{}))
    walk(page.get('/Resources',{}));return page
def text_only(page):
    page=copy.copy(page);cs=page.get_contents()
    allowed={b'q',b'Q',b'cm',b'BT',b'ET',b'Tc',b'Tw',b'Tz',b'TL',b'Tf',b'Tr',b'Ts',b'Td',b'TD',b'Tm',b'T*',b'Tj',b'TJ',b"'",b'"',b'rg',b'RG',b'g',b'G',b'k',b'K',b'cs',b'CS',b'sc',b'SC',b'scn',b'SCN',b'gs'}
    cs.operations=[(a,o) for a,o in cs.operations if o in allowed];page[NameObject('/Contents')]=cs;return page

basepath=source(reg['selection']['current_kdp_interior_de']); base=PdfReader(basepath)
old_en=PdfReader(source(reg['selection']['current_review_en']))
plan0=json.loads(source(reg['selection']['current_puzzles_de']).read_text())['page_plan']
plan=[{'id':e['id'],'kind':e['kind']} for e in plan0 if e['id'] not in ['cover','B06','reverse-B06'] and e['kind']!='solution' and not e['id'].startswith('reverse-L')]
plan += [{'id':'solutions-1','kind':'solutions'},{'id':'solutions-2','kind':'solutions'}]
for i,e in enumerate(plan,1):e['page']=i
assert len(plan)==len(base.pages)==128
ocr=json.loads((E/'source-text-inventory.json').read_text())
ocr={Path(a['path']).name:a for a in ocr}
def translated_raster(n,solution=False):
    typ='loesung' if solution else 'aufgabe';name=f'{n:02}-{typ}'
    tr=ET.parse(registered_path(f'05-kdp/specials/drafts/user-puzzles-v01/{name}-de.svg'))
    im=next(x for x in tr.iter() if x.tag.endswith('image'))
    px,py,ww,hh=[float(im.get(k)) for k in ['x','y','width','height']]
    data=ocr[name+'.png'];iw,ih=data['size']; replaces=[]
    labels={'Fledermaus':'Bat','Spinne':'Spider','Laterne':'Lantern','Kürbisbonbon':'Pumpkin candy','kleiner Geist':'Little ghost','Schlüssel':'Key','schwarze':'Black cat','Katze':'','Zauberstab':'Magic wand'}
    for a in data['lines']:
        text=a['text'];box=list(a['box']);v=None;font='Body';factor=.80
        if 'Entwurf' in text:v=''
        elif 'LÖSUNG' in text:v='ANSWER';font='Bold'
        elif 'Finde diese' in text:v='Find these 8 objects:'
        elif text in labels:v=labels[text]
        elif box[1]<400:
            if any(s in text for s in ['Suchbild','Labyrinth','Finde die Unterschiede','Welcher Schatten','Verbinde die Paare','Bilder-Sudoku']):v=t['puzzles'][n-1]['title'];font='Display';factor=.72
            elif 'Welches Bild' in text:v='Which Is the';font='Display';factor=.72
            elif 'gespiegelt?' in text:v='Mirror Image?';font='Display';factor=.66
            elif 'Ziehe Linien' in text:v='Draw lines.'
            elif 'nur einmal' in text:v='and once in every column.'
            elif any(s in text for s in ['Finde','Welche Figur','In jeder','Kreise','In den beiden']):v=t['puzzles'][n-1]['instruction']
        if n==4 and 'Finde die Unterschiede' in text:box=[85,125,965,250]
        if v is not None:replaces.append((box,v,font,factor))
    def draw(c):
        c.saveState();c.translate(px,720-py-hh);c.scale(ww/iw,hh/ih)
        for (x0,y0,x1,y1),v,font,factor in replaces:
            pad=18 if v=='ANSWER' else (0 if n==4 and font=='Display' else (5 if font=='Body' else 8))
            c.setFillGray(1);c.rect(max(0,x0-pad),max(0,ih-y1-pad),min(iw,x1+pad)-max(0,x0-pad),min(ih,y1+pad)-max(0,y0-pad),fill=1,stroke=0)
        for (x0,y0,x1,y1),v,font,factor in replaces:
            if not v:continue
            fs=min((y1-y0)*factor,(x1-x0+4)/pdfmetrics.stringWidth(v,font,1))
            # US translation stays within the old text footprint.
            c.setFillGray(0)
            if v=='ANSWER':
                c.roundRect(x0-12,ih-y1-10,x1-x0+24,y1-y0+20,12,fill=1,stroke=0)
                c.setFillGray(1)
            c.setFont(font,fs)
            asc=pdfmetrics.getAscent(font)/1000*fs;des=pdfmetrics.getDescent(font)/1000*fs
            c.drawCentredString((x0+x1)/2,ih-(y0+y1)/2-(asc+des)/2,v)
        c.restoreState()
        line(c,t['puzzles'][n-1]['title'],48,658,18,'Display',408)
    return overlay(draw,(504,720))

writer=PdfWriter()
for entry,p in zip(plan,base.pages):
    sid,kind,num=entry['id'],entry['kind'],entry['page']
    if kind=='blank':writer.add_blank_page(612,792);continue
    p=strip_text(p)
    if sid in ['title','imprint','pips']:
        q=text_only(old_en.pages[{'title':1,'imprint':2,'pips':5}[sid]])
        p.merge_transformed_page(q,Transformation().scale(1.1).translate(28.8,0))
    def draw(c):
        if sid=='welcome':
            header(c,t['ui']['welcome_title'],'front')
            para(c,t['ui']['welcome_text'],89.3,671,430,112,14)
            line(c,t['ui']['belongs'],89.3,525,21,'Display',430)
        elif sid=='craft-introduction':
            header(c,t['ui']['craft_intro_title'],'front')
            para(c,t['ui']['craft_intro_text'],89.3,670,430,180,14)
        elif kind=='coloring':header(c,t['motifs'][sid],kind)
        elif kind in ['comic','mini','jokes']:
            story=t['stories'][sid];header(c,story['title'],kind)
            if kind=='jokes':para(c,story['panels'][0],97,140,426,56,16.5,'Display')
            else:
                with Image.open(registered_path(f'05-kdp/specials/v01/{sid}.png')) as im:iw,ih=im.size
                aw=423*.62;k=min(aw/iw,561.6/ih);height=ih*k;y=44+(561.6-height)/2
                rx=45+aw+13;rw=423-aw-13;rh=height/len(story['panels'])
                for j,lines in enumerate(story['panels']):
                    if lines:para(c,lines,28.8+1.1*(rx+8),1.1*(y+height-j*rh-13),(rw-16)*1.1,(rh-26)*1.1,13.2)
        elif kind=='crafts':
            craft=t['crafts'][sid]
            if sid in ['B01','B02','B07']:
                line(c,craft['title'],48,750,23.1,'Display',516)
                if sid=='B07':
                    line(c,craft['subtitle'],48,722,12,width=516)
                    # Narrow white vector masks only over the embedded German lettering.
                    c.setFillGray(1)
                    for box in [(119,573,113,56),(86,513,190,50),(110,557,166,23),(114,505,15,10),(374,581,120,51),(369.5,539,127.5,43),(370,493,136,52)]:c.rect(*box,fill=1,stroke=0)
                    for txt,x,y in [('Haunted',178,590),('in here!',178,539),('Ghost',436,596),('on a',436,554),('break',436,513)]:line(c,txt,x,y,27,'CoverBold',172 if x<300 else 142,True)
                for j,txt in enumerate(craft['lines']):line(c,txt,48,132-j*18,11,width=516)
            elif sid in ['B03','B04','B05']:
                header(c,craft['title'],kind)
                para(c,craft['instruction'],78.3,667.7,465.3,107,12.65)
                c.setFillGray(1);c.rect(78.3,51,465.3,9,fill=1,stroke=0)
                line(c,'Solid line: cut     Dashed line: fold     No glue needed',78.3,62.7,8.8,width=465.3)
            elif sid=='B08':
                line(c,craft['title'],306,746.9,24.2,'Display',470,True)
                for j,txt in enumerate(craft['lines']):line(c,txt,75,717.2-j*17.6,11,'Cover',465)
                line(c,craft['legend'],306,631,9.9,'Cover',465,True)
                for j in range(6):line(c,craft['tab'],28.8+1.1*(54+(j%2)*222+87),1.1*(394-(j//2)*166+140),7.7,'Cover',150,True)
        if sid not in ['title','imprint','pips']:footer(c,num,kind=='solutions')
    p.merge_page(overlay(draw))
    if kind=='puzzle':p.merge_transformed_page(translated_raster(int(sid[1:])),Transformation().scale(1.1).translate(28.8,0))
    elif kind=='solutions':
        for j in range(4):p.merge_transformed_page(translated_raster((num-127)*4+j+1,True),Transformation().scale(.48).translate(48+(j%2)*270,414-(j//2)*354))
    writer.add_page(p)
writer.add_metadata({'/Title':'Giggle Dumplings – The Big Halloween Special','/Author':'Stefan Marx','/Subject':'English Edition · 128 pages · 8.5 × 11 inches'})
raw=S/'interior-layout.pdf';writer.write(raw)
interior=O/'Giggle-Dumplings-Halloween-EN-Interior-v01.pdf'
subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4','-dAutoRotatePages=/None','-sColorConversionStrategy=Gray','-dProcessColorModel=/DeviceGray','-dEmbedAllFonts=true','-dDownsampleGrayImages=false','-dDownsampleColorImages=false',f'-sOutputFile={interior}',str(raw)],check=True)

# Translate existing SVG text, keeping all approved artwork and preview crops.
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
front=ET.parse(source(reg['selection']['current_cover_front_de'])); back=ET.parse(source(reg['selection']['current_cover_back_de']))
sub=next(x for x in front.iter() if x.get('id')=='subtitle');sub.clear();sub.set('id','subtitle')
fs=43;subtitle=t['subtitle']
while pdfmetrics.stringWidth(subtitle,'CoverBold',fs)>610:fs-=.25
widths=[pdfmetrics.stringWidth(ch,'CoverBold',fs) for ch in subtitle];x=512-sum(widths)/2
for ch,w in zip(subtitle,widths):
    mid=x+w/2;dx=mid-512
    e=ET.SubElement(sub,f'{{{NS}}}text',{'transform':f'translate({mid} {440+.00030*dx*dx}) rotate({math.degrees(math.atan(.0006*dx))})','x':str(-w/2),'font-size':str(fs)});e.text=ch;x+=w
replacements={'Ausmal-':'Coloring','bilder':'Pages','Rätsel':'Puzzles','Mit Comics, Witzen & Bastelspaß':'With Comics, Jokes & Crafts'}
for el in front.iter():
    if el.tag.endswith('text') and el.text in replacements:
        el.text=replacements[el.text]
        if el.text=='Coloring':el.set('font-size','34')
        if el.text=='Puzzles':el.set('font-size','37')
# Small round edition marker in the space between the two existing side badges.
badge=ET.SubElement(front.getroot(),f'{{{NS}}}g',{'id':'english-edition','font-family':'Chalkboard SE, sans-serif','font-weight':'bold','text-anchor':'middle'})
ET.SubElement(badge,f'{{{NS}}}circle',{'cx':'512','cy':'578','r':'64','fill':'#c84c4c','stroke':'#fff1ce','stroke-width':'4'})
for txt,y in [('English',572),('Edition',602)]:ET.SubElement(badge,f'{{{NS}}}text',{'x':'512','y':str(y),'font-size':'27','fill':'#fff1ce'}).text=txt
backmap={'Lustig, kreativ':'Funny, creative','und schaurig süß!':'and spooky-cute!','Entdecke die Halloween-Welt der Giggle Dumplings!':'Explore Halloween with the Giggle Dumplings!','Male süße Kürbisse, freche Geister und deine fünf Freunde aus.':'Color cute pumpkins, playful ghosts and your five friends.','Löse knifflige Rätsel, lache über Comics und Witze':'Solve fun puzzles, giggle at comics and jokes,','und werde mit den Bastelideen selbst kreativ.':'and get creative with hands-on crafts.','Für eine schaurig-schöne Zeit voller Fantasie!':'A not-too-spooky adventure full of imagination!','Ausmal-':'Coloring','bilder':'Pages','kindgerechte':'Kid-friendly','Rätsel':'Puzzles','niedliche':'Cute','Halloween-':'Halloween','Figuren':'Friends','Comics, Witze':'Comics, Jokes','& Bastelspaß':'& Crafts'}
for el in back.iter():
    if el.tag.endswith('text') and el.text in backmap:el.text=backmap[el.text]
for side,tr in [('front',front),('back',back)]:
    for el in tr.iter():
        if el.tag.endswith('title'):el.text=f'Giggle Dumplings – English {side} cover v01'
    p=S/f'cover-{side}-en-v01.svg';tr.write(p,encoding='unicode')
    subprocess.run(['rsvg-convert','--unlimited','-h','3300','-o',str(S/f'cover-{side}.png'),str(p)],check=True)
spine=128*.002252*72;cw=1242+spine
coverraw=S/'cover-layout.pdf';c=canvas.Canvas(str(coverraw),pagesize=(cw,810));c.setTitle('Giggle Dumplings – The Big Halloween Special | English Edition')
c.setFillColorRGB(.12,.055,.20);c.rect(0,0,cw,810,fill=1,stroke=0)
for side,x in [('back',9),('front',621+spine)]:
    path=S/f'cover-{side}.png'
    with Image.open(path) as im:iw,ih=im.size
    ww=792*iw/ih;c.drawImage(str(path),x+(612-ww)/2,9,width=ww,height=792)
fs=8.5;asc=pdfmetrics.getAscent('Cover')/1000*fs;desc=pdfmetrics.getDescent('Cover')/1000*fs;assert asc-desc<=spine-9
c.saveState();c.translate(621+spine/2,405);c.rotate(90);c.setFillColorRGB(1,.96,.84);c.setFont('Cover',fs);c.drawCentredString(0,-(asc+desc)/2,'Giggle Dumplings - The Big Halloween Special');c.restoreState();c.save()
cover=O/'Giggle-Dumplings-Halloween-EN-Cover-v01.pdf'
subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4','-dAutoRotatePages=/None','-sColorConversionStrategy=CMYK','-dProcessColorModel=/DeviceCMYK','-dEmbedAllFonts=true','-dDownsampleColorImages=false','-dAutoFilterColorImages=false','-dColorImageFilter=/FlateEncode',f'-sOutputFile={cover}',str(coverraw)],check=True)

out=PdfReader(interior);assert len(out.pages)==128
assert all(tuple(map(float,p.mediabox))==(0.,0.,612.,792.) for p in out.pages)
assert len({e['id'] for e in plan if e['kind']=='coloring'})==30
for e in plan:
    if e['kind'] in ['coloring','comic','mini','jokes','puzzle','crafts']:assert e['page']%2==1 and plan[e['page']]['kind']=='blank'
    if e['kind']=='blank':assert not out.pages[e['page']-1].extract_text().strip()
alltext='\n'.join(p.extract_text() for p in out.pages)
for forbidden in ['Entwurf','Rätsel','Lösung','DEUTSCHE','Klebelasche','Ausmalbilder','Fledermaus','Herausgeber','Bastelzeit']:assert forbidden not in alltext,forbidden
assert 'This book belongs to:' in out.pages[2].extract_text()
assert digest(basepath)==used[reg['selection']['current_kdp_interior_de']]['sha256']
manifest={'language':'en-US','date':'2026-09-30','page_plan':plan,'counts':dict(Counter(e['kind'] for e in plan)),'pages':128,'trim_inches':[8.5,11],'interior_bleed':False,'interior_ink':'grayscale','paper':'white','cover_points':[cw,810],'spine_mm':spine/72*25.4,'cover_color':'CMYK','source_assets':used,'translation':{'path':str(tp.relative_to(R)),'sha256':digest(tp)},'paragraph_fit_checks':checks,'de_source_unchanged':True,'user_visual_review':'pending','kdp_preview':'pending','physical_craft_test':'pending','print_release':False,'limitations':['Original raster artwork resolution is inherited; 300 dpi cover rendering does not create native detail.','No complete-book visual sign-off; user reviews the PDFs.'],'outputs':{p.name:digest(p) for p in [interior,cover]}}
savejson(O/'manifest.json',manifest)
for p in [tp,E/'source-text-inventory.json',*S.iterdir(),*O.iterdir()]:
    if not p.is_file():continue
    key='edition.en.v01.'+p.relative_to(E).as_posix().replace('/','.');reg['assets'][key]={'path':str(p.relative_to(R)),'sha256':digest(p),'role':'export' if p in [interior,cover] else 'derived','usage':'Complete English Halloween edition, US English, 128 pages','design_status':'review_pending','print_status':'not_released','issues':['English user review and KDP print preview pending'],'origin':{'project':'dumplings-halloween','source':str(basepath.relative_to(R)),'note':'Reuses corrected DE artwork; separate editable English text layers.'}}
    if p==interior:reg['selection']['current_kdp_interior_en']=key
    if p==cover:reg['selection']['current_kdp_cover_en']=key
    if p==tp:reg['selection']['current_texts_en']=key
savejson(R/'production/assets.json',reg)
print(json.dumps({'pages':128,'counts':manifest['counts'],'interior':str(interior),'cover':str(cover),'paragraph_checks':len(checks),'user_review':'pending'},ensure_ascii=False))
