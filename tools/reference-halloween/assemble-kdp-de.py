"""Register-checked German manuscript and full cover. Never overwrites a release."""
from pathlib import Path
import io,json,hashlib,subprocess,copy
from collections import Counter
from xml.etree import ElementTree as ET
from pypdf import PdfReader,PdfWriter,Transformation
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image
R=Path(__file__).resolve().parents[1]; O=R/'05-kdp/upload/de-2026-09-30-v08'; O.mkdir(parents=True,exist_ok=False)
T=O/'sources';T.mkdir()
reg=json.loads((R/'production/assets.json').read_text()); used={}
def source(key):
 a=reg['assets'][key];p=R/a['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],key
 used[key]={'path':a['path'],'sha256':a['sha256']};return p
base=PdfReader(source(reg['selection']['current_review_de']))
plan=json.loads(source(reg['selection']['current_puzzles_de']).read_text())['page_plan']
v08=json.loads(source(reg['selection']['current_review_manifest']).read_text())['page_plan']
intro=next(p['pdf_page'] for p in v08 if p['id']=='craft-introduction')
texts=json.loads(source(reg['selection']['current_comic_text_de']).read_text())
font=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype/DejaVuSans.ttf'
pdfmetrics.registerFont(TTFont('Body',str(font)))
pdfmetrics.registerFont(TTFont('Display','/System/Library/Fonts/Supplemental/Chalkboard.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CoverFriendly','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
def overlay(fn,size=(504,720)):
 b=io.BytesIO();c=canvas.Canvas(b,pagesize=size);fn(c);c.save();b.seek(0);return PdfReader(b).pages[0]
def svgpage(p,name,strip=False):
 tree=ET.fromstring(p.read_text())
 if strip:
  for el in tree.iter():
   if 'font-family' in el.attrib:el.set('font-family','DejaVu Sans, sans-serif')
   if el.tag.endswith('text') and el.get('y')=='42':el.set('font-family','Chalkboard');el.set('font-size','23.1')
  for group in tree.iter():
   for el in list(group):
    if el.tag.endswith('text') and 'Kontrollstrecke' in ''.join(el.itertext()):group.remove(el)
    elif el.tag.endswith('path') and el.get('d','').startswith('M405 762'):group.remove(el)
  if name[:1] in {'0','1','2','3','4','5','6','7','8'} and ('aufgabe' in p.name or 'loesung' in p.name):
   for group in tree.iter():
    for el in list(group):
     if el.tag.endswith('text') and el.get('y')=='693':group.remove(el)
 data=ET.tostring(tree);f=T/(name+'.svg');f.write_bytes(data)
 out=T/(name+'.pdf');subprocess.run(['rsvg-convert','--unlimited','-f','pdf','-o',str(out),str(f)],check=True)
 return PdfReader(out).pages[0]
def scale(p):
 p=copy.copy(p)
 if abs(float(p.mediabox.width)-612)<.1:return p
 assert abs(float(p.mediabox.width)-504)<.1
 p.scale_by(1.1);p.add_transformation(Transformation().translate(28.8,0));p.mediabox.lower_left=(0,0);p.mediabox.upper_right=(612,792);p.cropbox=p.mediabox
 return p
def fixcomic(p,sid):
 # Artwork and existing anatomy repairs stay in place; replace dialogue rail only.
 panels=texts[sid]['panels'];im=Image.open(R/f'05-kdp/specials/v01/{sid}.png');iw,ih=im.size
 aw=423*.62; k=min(aw/iw,561.6/ih);height=ih*k;y=44+(561.6-height)/2;rx=45+aw+13;rw=423-aw-13;rh=height/len(panels)
 def draw(c):
  c.setFillColorRGB(1,1,1);c.rect(rx-1,40,rw+3,570,fill=1,stroke=0)
  for n,panel in enumerate(panels):
   lines=panel['lines']
   if not lines:continue
   top=y+height-n*rh;c.setStrokeColorRGB(0,0,0);c.setLineWidth(.8);c.roundRect(rx,top-rh+5,rw,rh-10,10,fill=0,stroke=1)
   for fs in [12,11.5,11,10.5,10]:
    para=Paragraph('<br/>'.join(lines),ParagraphStyle('dialog',fontName='Body',fontSize=fs,leading=fs*1.22))
    w,h=para.wrap(rw-16,rh-26)
    if h<=rh-26:break
   assert h<=rh-26,sid
   para.drawOn(c,rx+8,top-13-h)
 p.merge_page(overlay(draw));return p
def clean_puzzle_footer(p):
 def draw(c):
  c.setFillColorRGB(1,1,1);c.rect(505,84,55,20,fill=1,stroke=0)
 p.merge_page(overlay(draw,(612,792)));return p
crafts={sid:svgpage(source('crafts.v04.'+name),sid,True) for sid,name in [('B01','01-monstermaske-de'),('B02','02-kuerbismaske-de'),('B07','04-wendetuer-schild-de')]}
entries=[];w=PdfWriter()
for e in plan:
 sid=e['id'];kind=e['kind']
 if sid=='cover' or sid in ['B06','reverse-B06'] or kind=='solution' or sid.startswith('reverse-L'):continue
 if kind=='blank':w.add_blank_page(612,792)
 else:
  if sid in crafts:p=copy.copy(crafts[sid])
  elif kind=='puzzle':
   rel=f'05-kdp/specials/drafts/user-puzzles-v01/{int(sid[1:]):02}-aufgabe-de.svg'
   key=next(k for k,a in reg['assets'].items() if a['path']==rel);p=svgpage(source(key),sid)
  else:
   num=int(e.get('source_pdf_page',intro));p=copy.copy(base.pages[num-1])
   if sid in ['C01','C05','C06']:p=fixcomic(p,sid)
  p=scale(p)
  if kind=='puzzle':p=clean_puzzle_footer(p)
  # Remove old footer numbers visually; replace with actual physical page number.
  def footer(c):
   c.setFillColorRGB(1,1,1);c.rect(40,0,550,29,fill=1,stroke=0)
   c.setStrokeColorRGB(0,0,0);c.setLineWidth(.715);c.line(78.3,49.2,543.6,49.2)
   c.setFillColorRGB(0,0,0);c.setFont('Body',8.8);c.drawString(78.3,36,'Giggle Dumplings');c.drawRightString(543.6,36,str(len(w.pages)+1))
  if kind!='front':p.merge_page(overlay(footer,(612,792)))
  w.add_page(p)
 entries.append({'id':sid,'kind':kind,'page':len(w.pages)})
# Two solution sheets without inserted blank backs.
sols=[]
for n in range(1,9):
 rel=f'05-kdp/specials/drafts/user-puzzles-v01/{n:02}-loesung-de.svg'
 key=next(k for k,a in reg['assets'].items() if a['path']==rel)
 sols.append(svgpage(source(key),f'L{n:02}'))
for block in range(2):
 p=PdfWriter().add_blank_page(612,792)
 for i in range(4):
  q=copy.copy(sols[block*4+i]);s=.48;tx=48+(i%2)*270;ty=414-(i//2)*354
  p.merge_transformed_page(q,Transformation().scale(s).translate(tx,ty))
  # Cover the inherited tiny source footer in each reduced solution tile.
  def tile_footer(c):
   c.setFillColorRGB(1,1,1);c.rect(tx+505*s,ty+84*s,55*s,20*s,fill=1,stroke=0)
  p.merge_page(overlay(tile_footer,(612,792)))
 w.add_page(p);entries.append({'id':f'solutions-{block+1}','kind':'solutions','page':len(w.pages)})
count=len(w.pages);assert count==128,count
assert len({e['id'] for e in entries if e['kind']=='coloring'})==30
for i,e in enumerate(entries):
 if e['kind'] in ['crafts','coloring','comic','mini','jokes','puzzle']:
  assert e['page']%2==1 and entries[i+1]['kind']=='blank',e
w.add_metadata({'/Title':'Giggle Dumplings – Das große Halloween-Special','/Author':'Stefan Marx'})
raw=T/'interior-layout.pdf';w.write(raw)
interior=O/'Giggle-Dumplings-Halloween-DE-Innenbuch.pdf'
subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4','-sColorConversionStrategy=Gray','-dProcessColorModel=/DeviceGray','-dEmbedAllFonts=true','-dDownsampleGrayImages=false','-dDownsampleColorImages=false',f'-sOutputFile={interior}',str(raw)],check=True)
# Full wrap, proportional cover placement on matching dark purple background.
front=svgpage(source(reg['selection']['current_cover_front_de']),'cover-front')
back=svgpage(source(reg['selection']['current_cover_back_de']),'cover-back')
spine=count*.002252*72;cw=1242+spine;ch=810
def background(c):c.setFillColorRGB(.12,.055,.20);c.rect(0,0,cw,ch,fill=1,stroke=0)
cover=overlay(background,(cw,ch))
for p,x in [(back,9),(front,621+spine)]:
 sw,sh=float(p.mediabox.width),float(p.mediabox.height);s=min(612/sw,792/sh)
 cover.merge_transformed_page(p,Transformation().scale(s).translate(x+(612-sw*s)/2,9+(792-sh*s)/2))
def barcode(c):c.setFillColorRGB(1,1,1);c.rect(450,27,144,86.4,fill=1,stroke=0)
cover.merge_page(overlay(barcode,(cw,ch)))
def spine_title(c):
 fs=8.5;asc=pdfmetrics.getAscent('CoverFriendly')/1000*fs;desc=pdfmetrics.getDescent('CoverFriendly')/1000*fs
 assert asc-desc <= spine-9
 c.saveState();c.translate(621+spine/2,405);c.rotate(90)
 c.setFillColorRGB(1,.96,.84);c.setFont('CoverFriendly',fs)
 c.drawCentredString(0,-(asc+desc)/2,'Giggle Dumplings - Das große Halloween-Special');c.restoreState()
cover.merge_page(overlay(spine_title,(cw,ch)))
writer=PdfWriter();writer.add_page(cover);writer.write(T/'cover-layout.pdf')
subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4','-sColorConversionStrategy=CMYK','-dProcessColorModel=/DeviceCMYK','-dEmbedAllFonts=true','-dDownsampleColorImages=false',f'-sOutputFile={O / "Giggle-Dumplings-Halloween-DE-Umschlag.pdf"}',str(T/'cover-layout.pdf')],check=True)
check=PdfReader(interior);assert len(check.pages)==count
assert all(tuple(map(float,p.mediabox))==(0.,0.,612.,792.) for p in check.pages)
manifest={'date':'2026-09-30','language':'de','interior_pages':count,'trim_inches':[8.5,11],'bleed_interior':False,'paper':'white','ink':'black','cover_finish':'glossy','spine_inches':count*.002252,'cover_points':[cw,ch],'page_plan':entries,'sources':used,'counts':dict(Counter(e['kind'] for e in entries)),'upload_ready':False,'open':['Nutzer-Sichtprüfung und KDP-Vorschau','Papierprobe der Bastelseiten','Quellauflösung teilweise unter 300 dpi; nicht durch Upscaling behoben','Coverformat-Anpassung mit violetten Randflächen braucht Nutzerreview'],'removed':['Kürbis-Klappmaul / alte Kürbiskarte B06','Fingerpuppen (B07 durch Wendetürschild ersetzt)','Einladungskarte']}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pages':count,'counts':manifest['counts'],'cover_points':manifest['cover_points'],'output':str(O)},ensure_ascii=False))
