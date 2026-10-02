"""Flatten SVG compositing before cover assembly to avoid PDF viewer mask faults."""
from pathlib import Path
import hashlib, json, subprocess, argparse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--version',default='v09');args=parser.parse_args();version=args.version
O=R/f'05-kdp/upload/cover-de-{version}'
O.mkdir(parents=True,exist_ok=False)
S=O/'sources';S.mkdir()
reg=json.loads((R/'production/assets.json').read_text())
sources={}
for side in ['back','front']:
    a=reg['assets'][reg['selection'][f'current_cover_{side}_de']]
    src=R/a['path']
    assert hashlib.sha256(src.read_bytes()).hexdigest()==a['sha256']
    sources[side]={'path':a['path'],'sha256':a['sha256']}
    # Rendering existing vector/layout layers, not inventing new raster detail.
    subprocess.run(['rsvg-convert','--unlimited','-h','3300','-o',str(S/f'{side}.png'),str(src)],check=True)
interior=R/'05-kdp/upload/de-2026-09-30-v08/Giggle-Dumplings-Halloween-DE-Innenbuch.pdf'
pages=len(PdfReader(interior).pages);assert pages==128
spine=pages*.002252*72;width=1242+spine
pdfmetrics.registerFont(TTFont('Spine','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
raw=S/'cover-layout.pdf'
c=canvas.Canvas(str(raw),pagesize=(width,810),pageCompression=1)
c.setTitle('Giggle Dumplings - Das große Halloween-Special | Umschlag v09')
c.setFillColorRGB(.12,.055,.20);c.rect(0,0,width,810,fill=1,stroke=0)
from PIL import Image
for side,x in [('back',9),('front',621+spine)]:
    path=S/f'{side}.png'
    with Image.open(path) as im:iw,ih=im.size
    w=792*iw/ih
    c.drawImage(str(path),x+(612-w)/2,9,width=w,height=792)
fs=8.5;asc=pdfmetrics.getAscent('Spine')/1000*fs;desc=pdfmetrics.getDescent('Spine')/1000*fs
assert asc-desc<=spine-9
c.saveState();c.translate(621+spine/2,405);c.rotate(90)
c.setFillColorRGB(1,.96,.84);c.setFont('Spine',fs)
c.drawCentredString(0,-(asc+desc)/2,'Giggle Dumplings - Das große Halloween-Special')
c.restoreState();c.showPage();c.save()
out=O/f'Giggle-Dumplings-Halloween-DE-Umschlag-{version}.pdf'
subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4','-dAutoRotatePages=/None','-sColorConversionStrategy=CMYK','-dProcessColorModel=/DeviceCMYK','-dEmbedAllFonts=true','-dDownsampleColorImages=false','-dAutoFilterColorImages=false','-dColorImageFilter=/FlateEncode',f'-sOutputFile={out}',str(raw)],check=True)
p=PdfReader(out);assert len(p.pages)==1
assert abs(float(p.pages[0].mediabox.width)-width)<.01
manifest={'sources':sources,'interior':str(interior.relative_to(R)),'interior_sha256':hashlib.sha256(interior.read_bytes()).hexdigest(),'pages':pages,'cover_points':[width,810],'spine_mm':spine/72*25.4,'changes':['SVG-Masken und Vorschaubild-Clipping vor PDF-Montage gerendert','Zusätzliche weiße Barcodefläche entfernt; kein Beispielbarcode eingebaut','Dunkelviolette Format-Randflächen erhalten'],'render_resolution_dpi':300,'native_source_resolution_note':'Hintergrundquellen weiterhin ca. 136–140 dpi effektiv; Rendering erzeugt keine zusätzlichen Bilddetails.','user_review':'pending','print_status':'not_released'}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for path in sorted(O.rglob('*')):
    if not path.is_file():continue
    key=f'cover.export.{version}.'+path.relative_to(O).as_posix().replace('/','.').replace('.','-')
    reg['assets'][key]={'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':'export' if path==out else 'derived','usage':'Korrigierte Umschlagmontage v09 für 128 Seiten','design_status':'review_pending','print_status':'not_released','issues':['Nutzerreview und KDP-Vorschau offen','Native Hintergrundauflösung unter 300 dpi'],'origin':{'project':'dumplings-halloween','note':'Bestehende ausgewählte SVG-Gestaltung unverändert gerendert; Masken vor Montage aufgelöst.'}}
    if path==out:reg['selection']['current_kdp_cover_de']=key
(R/'production/assets.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(out)
