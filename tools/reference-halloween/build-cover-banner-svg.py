"""Reuse approved inner-title ribbon geometry as an editable cover component."""
from pathlib import Path
import hashlib,html,json,math
from xml.etree import ElementTree as ET
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04-cover/drafts/banner-v06';assert not OUT.exists()
r=json.loads((ROOT/'production/assets.json').read_text())
source=r['assets']['frontmatter.review.v01'];assert source['design_status']=='approved'
assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
font='/System/Library/Fonts/Supplemental/ChalkboardSE.ttc'
pdfmetrics.registerFont(TTFont('Bold',font,subfontIndex=0))
text='Das große Halloween-Special';size=26
while pdfmetrics.stringWidth(text,'Bold',size)>375:size-=.25
def path(i=0):
 x=48+i;right=456-i;low=401+i;high=447-i
 return f'M{x} {490-high} C177 {9+i} 327 {9+i} {right} {490-high} L{right-17} 66 L{right-5} {490-low} C323 {56-i} 181 {56-i} {x+5} {490-low} L{x+17} 66 Z'
widths=[pdfmetrics.stringWidth(ch,'Bold',size) for ch in text];x=252-sum(widths)/2;letters=[]
for ch,w in zip(text,widths):
 mid=x+w/2;dx=mid-252;y=49.5+.00066*dx*dx;angle=math.degrees(math.atan(.00132*dx))
 letters.append(f'<text transform="translate({mid:.5f} {y:.5f}) rotate({angle:.5f})" x="{-w/2:.5f}" y="0">{html.escape(ch)}</text>');x+=w
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="177.8mm" height="35.28mm" viewBox="0 0 504 100" role="img" aria-label="{text}">
<title>{text}</title>
<defs>
<linearGradient id="ribbon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffc16a"/><stop offset=".3" stop-color="#f78536"/><stop offset=".7" stop-color="#e96329"/><stop offset="1" stop-color="#ffb750"/></linearGradient>
<linearGradient id="ink" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#fffef0"/><stop offset="1" stop-color="#ffe5aa"/></linearGradient>
</defs>
<g id="bannerform" stroke-linejoin="round" stroke-linecap="round">
<path d="{path()}" transform="translate(0 2.2)" fill="#41243f" stroke="#41243f" stroke-width="3"/>
<path d="{path()}" fill="url(#ribbon)" stroke="#ffe9ad" stroke-width="1.3"/>
<path d="{path(2)}" fill="none" stroke="#a64131" stroke-width=".65" opacity=".75"/>
<path d="M62 42 C184 10 320 10 442 42" fill="none" stroke="#fff0bb" stroke-width="1.4" opacity=".65"/>
</g>
<g id="untertitel" font-family="Chalkboard SE, sans-serif" font-weight="normal" font-size="{size}" fill="url(#ink)" stroke="#a43c37" stroke-width=".7" paint-order="stroke fill" stroke-linejoin="round" xml:space="preserve">{''.join(letters)}</g></svg>'''
ET.fromstring(svg);OUT.mkdir(parents=True);dest=OUT/'halloween-banner-de-v06.svg';dest.write_text(svg)
(OUT/'manifest.json').write_text(json.dumps({'status':'review_draft','source_asset':'frontmatter.review.v01','source_sha256':source['sha256'],'geometry_source':'tools/build-frontmatter-review-v01.py:ribbon_path/banner','text':text,'font':font,'font_size':size,'viewBox':[0,0,504,100],'output':str(dest.relative_to(ROOT)),'visual_review':'user_pending','cover_assembly':'pending','print_release':False},ensure_ascii=False,indent=2)+'\n')
print('Banner-SVG erstellt; Struktur und Textbreite geprüft. Keine Render-/PDF-Ausgabe.')
