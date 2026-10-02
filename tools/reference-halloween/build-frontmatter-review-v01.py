"""Standalone registered title/Pips proof; preserved original images, PDF layout only."""
import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'production/builds/frontmatter-review-v01'
spec=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py')
checks=importlib.util.module_from_spec(spec); spec.loader.exec_module(checks)
r=json.loads((ROOT/'production/assets.json').read_text())
errors=checks.check(r)
if errors: raise RuntimeError('\n'.join(errors))
if OUT.exists(): raise RuntimeError('Preserve previous proof; select new version')
OUT.mkdir(parents=True)
used={}
def source(rel):
 key,a=next((k,a) for k,a in r['assets'].items() if a['path']==rel)
 assert a['design_status']!='rejected'
 used[key]=a
 return ROOT/rel
ui=json.loads(source('01-concept/book-texts-v01.json').read_text())['ui']
copy=json.loads(source('01-concept/frontmatter-texts-v01.json').read_text())
logo=source('04-cover/drafts/v01/title-inner-bw.png')
friends=source('05-kdp/specials/v01/B03.png')
pips=source('05-kdp/specials/v01/B05.png')
font=Path('/System/Library/Fonts/Supplemental/ChalkboardSE.ttc')
pdfmetrics.registerFont(TTFont('Body',str(font)))
pdfmetrics.registerFont(TTFont('Bold',str(font),subfontIndex=1))
pdf=OUT/'innentitel-pips-de-en-es-v01.pdf'
c=canvas.Canvas(str(pdf),pagesize=(504,720),invariant=1)
c.setTitle('Giggle Dumplings - Innentitel und Pips - DE EN ES - Sichtentwurf')
c.setAuthor('Stefan Marx')
placements=[]
def centered(text,y,size=14,font='Body'):
 assert pdfmetrics.stringWidth(text,font,size)<=420, text
 c.setFont(font,size); c.drawCentredString(252,y,text)
def fitted_image(path,box):
 x,y,w,h=box; iw,ih=ImageReader(str(path)).getSize(); scale=min(w/iw,h/ih)
 c.drawImage(str(path),x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale)
def ribbon_path(inset=0):
 # Native PDF vector adaptation of the existing curved, notched series banner.
 p=c.beginPath(); x=48+inset; right=456-inset; low=401+inset; high=447-inset
 p.moveTo(x,high); p.curveTo(177,481-inset,327,481-inset,right,high)
 p.lineTo(right-17,424); p.lineTo(right-5,low)
 p.curveTo(323,434+inset,181,434+inset,x+5,low)
 p.lineTo(x+17,424); p.close(); return p

def banner(text):
 c.setLineJoin(1); c.setLineCap(1); c.setLineWidth(2.2)
 c.drawPath(ribbon_path(),stroke=1,fill=0)
 c.setLineWidth(.85); c.setDash(4,3); c.drawPath(ribbon_path(5),stroke=1,fill=0); c.setDash()
 size=20
 while pdfmetrics.stringWidth(text,'Bold',size)>335: size-=.25
 widths=[pdfmetrics.stringWidth(ch,'Bold',size) for ch in text]
 total=sum(widths); x=252-total/2
 for ch,w in zip(text,widths):
  mid=x+w/2; dx=mid-252; y=441-0.00066*dx*dx
  c.saveState(); c.translate(mid,y); c.rotate(math.degrees(math.atan(-.00132*dx)))
  c.setFont('Bold',size); c.drawString(-w/2,0,ch); c.restoreState(); x+=w
 return size

for lang in ('de','en','es'):
 fitted_image(logo,(32,476,440,220))
 size=banner(ui['subtitle'][lang])
 for i,line in enumerate(copy[lang]['title_lines']): centered(line,354-i*24,15)
 fitted_image(friends,(70,138,364,182))
 centered(ui['edition'][lang],86,11)
 placements.append({'language':lang,'kind':'title','title_box':[32,476,440,220], 'banner':'curved notched vector with inset stitching','subtitle_font_pt':size,'friends_box':[70,138,364,182]})
 c.showPage()
 centered(copy[lang]['heading'],634,28,'Bold')
 centered(copy[lang]['guest'],600,14)
 # PDF clipping places only the existing Pips component; source pixels are unchanged.
 crop=(975,130,1580,760); x,y,w=141,302,222
 iw,ih=ImageReader(str(pips)).getSize(); scale=w/(crop[2]-crop[0]); h=(crop[3]-crop[1])*scale
 c.saveState(); clip=c.beginPath(); clip.rect(x,y,w,h); c.clipPath(clip,stroke=0,fill=0)
 c.drawImage(str(pips),x-crop[0]*scale,y-(ih-crop[3])*scale,iw*scale,ih*scale); c.restoreState()
 c.setLineWidth(1.4); c.roundRect(359,476,79,42,16,stroke=1,fill=0)
 c.setFillColorRGB(1,1,1); tail=c.beginPath(); tail.moveTo(365,480); tail.lineTo(345,465); tail.lineTo(376,477); c.drawPath(tail,stroke=1,fill=1); c.setFillColorRGB(0,0,0)
 c.setFont('Body',16); c.drawCentredString(398.5,490,copy[lang]['boo'])
 for i,line in enumerate(copy[lang]['body']): centered(line,258-i*25,16)
 for i,line in enumerate(copy[lang]['invite']): centered(line,139-i*23,15,'Bold')
 placements.append({'language':lang,'kind':'pips','source_crop_px':crop,'placement_pt':[x,y,w,h],'source_pixels_unchanged':True})
 c.showPage()
c.save()
reader=PdfReader(pdf); assert len(reader.pages)==6
for idx,lang in enumerate(('de','en','es')):
 title=reader.pages[2*idx].extract_text(); intro=reader.pages[2*idx+1].extract_text()
 assert ''.join(ui['subtitle'][lang].split()) in ''.join(title.split()),(lang,title)
 for text in copy[lang]['title_lines']+[ui['edition'][lang]]: assert text in title,text
 for text in [copy[lang]['heading'],copy[lang]['guest'],copy[lang]['boo']]+copy[lang]['body']+copy[lang]['invite']: assert text in intro,text
for page in reader.pages: assert list(map(float,page.mediabox))==[0,0,504,720]
m={'status':'review_draft','print_release':False,'whole_book_changed':False,'operation':'Reuse + PDF layout/text; no image generation or raster editing','sources':used,'placements':placements,'font':{'path':str(font),'sha256':checks.digest(font)},'checks':{'pages':6,'page_pt':[504,720],'all_localized_text_present':True},'visual_review':'pending','limitations':['Existing raster resolution unchanged; native resolution not newly approved','Whole-book insertion and physical page plan pending'],'output':{'path':pdf.relative_to(ROOT).as_posix(),'sha256':checks.digest(pdf)}}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(pdf)
