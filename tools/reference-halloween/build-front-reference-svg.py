"""Editable German text over the revised user cover illustration."""
from pathlib import Path
import base64,hashlib,html,json,math
from xml.etree import ElementTree as ET
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'04-cover/drafts/front-de-v10'
OUT.mkdir(parents=True,exist_ok=True)
dest=OUT/'cover-front-de-v10.svg';assert not dest.exists()
bg=(ROOT/'04-cover/drafts/front-de-v07/background.png').read_bytes()
pdfmetrics.registerFont(TTFont('CoverBold','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=1))
subtitle='Das große Halloween-Special';size=43
while pdfmetrics.stringWidth(subtitle,'CoverBold',size)>610:size-=.25
widths=[pdfmetrics.stringWidth(c,'CoverBold',size) for c in subtitle]
x=512-sum(widths)/2;letters=[]
for c,w in zip(subtitle,widths):
 mid=x+w/2;dx=mid-512;y=440+.00030*dx*dx;angle=math.degrees(math.atan(.0006*dx))
 letters.append(f'<text transform="translate({mid} {y}) rotate({angle})" x="{-w/2}" font-size="{size}">{html.escape(c)}</text>');x+=w
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1536" width="1024" height="1536">
<title>Giggle Dumplings – Vorderseitenentwurf DE v10</title>
<image width="1024" height="1536" href="data:image/png;base64,{base64.b64encode(bg).decode()}"/>
<g font-family="Chalkboard SE, sans-serif" font-weight="bold" fill="#fff7df" stroke="#a74729" stroke-width="1.3" paint-order="stroke fill" stroke-linejoin="round">
<g id="subtitle">{''.join(letters)}</g>
<g id="coloring-sticker" text-anchor="middle" transform="rotate(-8 151 635)">
<text x="151" y="622" font-size="77">30</text><text x="151" y="665" font-size="37">Ausmal-</text><text x="151" y="704" font-size="37">bilder</text></g>
<g id="puzzle-sticker" text-anchor="middle" transform="rotate(8 870 635)" stroke="#583078"><text x="870" y="608" font-size="34">plus</text><text x="870" y="661" font-size="42">Rätsel</text></g>
</g>
<text id="extras" x="512" y="1430" text-anchor="middle" font-family="Chalkboard SE, sans-serif" font-weight="bold" font-size="32" fill="#3e2058">Mit Comics, Witzen &amp; Bastelspaß</text>
</svg>'''
ET.fromstring(svg);dest.write_text(svg)
(OUT/'manifest.json').write_text(json.dumps({'status':'review_draft','source':'production/references/front-fraft.png','background':'04-cover/drafts/front-de-v07/background.png','background_sha256':hashlib.sha256(bg).hexdigest(),'subtitle':subtitle,'subtitle_font_size':size,'visual_review':'user_pending','print_release':False,'note':'Source aspect ratio preserved. Final 7x10 trim/bleed adaptation is still pending.'},ensure_ascii=False,indent=2)+'\n')
print('Vorderseite v10 mit editierbaren Texten erstellt; XML und Untertitelbreite geprüft.')
