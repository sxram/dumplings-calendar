"""Editable back cover from user reference and existing book illustrations."""
from pathlib import Path
import base64,hashlib,html,json
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04-cover/drafts/back-de-v05'
OUT.mkdir(parents=True,exist_ok=True)
assert not (OUT/'backcover-de-v05.svg').exists()
r=json.loads((ROOT/'production/assets.json').read_text());sources={}
def data(path):
 b=(ROOT/path).read_bytes();sources[path]=hashlib.sha256(b).hexdigest()
 return 'data:image/png;base64,'+base64.b64encode(b).decode()
def asset(key):
 a=r['assets'][key];u=data(a['path']);assert sources[a['path']]==a['sha256'];return u
bg=data('04-cover/drafts/back-de-v02/background.png')
def txt(x,y,s,t,fill='#321940',extra=''):
 return f'<text x="{x}" y="{y}" font-size="{s}" fill="{fill}" text-anchor="middle" {extra}>{html.escape(t)}</text>'
parts=[f'<image width="1049" height="1499" href="{bg}"/>']
for y,t in [(110,'Lustig, kreativ'),(195,'und schaurig süß!')]:
 parts.append(txt(524,y,76,t,'#fff1c6','font-weight="bold" stroke="#5b1732" stroke-width="10" paint-order="stroke fill" stroke-linejoin="round"'))
lines=['Entdecke die Halloween-Welt der Giggle Dumplings!', 'Male süße Kürbisse, freche Geister und deine fünf Freunde aus.', 'Löse knifflige Rätsel, lache über Comics und Witze', 'und werde mit den Bastelideen selbst kreativ.', 'Für eine schaurig-schöne Zeit voller Fantasie!']
for i,t in enumerate(lines):parts.append(txt(524,329+i*36,27,t,extra='font-weight="bold"' if i==0 else ''))
for x,lines in [(155,[(624,39,'30'),(651,26,'Ausmal-'),(677,26,'bilder')]),(404,[(633,27,'kindgerechte'),(665,30,'Rätsel')]),(647,[(622,27,'niedliche'),(651,27,'Halloween-'),(680,27,'Figuren')]),(895,[(631,27,'Comics, Witze'),(664,26,'& Bastelspaß')])]:
 for y,size,t in lines:parts.append(txt(x,y,size,t,'#fff8e4','font-weight="bold"'))
# Source illustrations fit inside the existing white frames; no raster edits.
for key,cx,cy,w,h,angle in [('anatomy.v03.05',204,854,242,184,-8),('puzzles.user.halloween_pumpkin_maze_worksheet',526,843,270,190,0),('anatomy.v03.12',849,854,242,184,8)]:
 u=asset(key);parts.append(f'<g transform="translate({cx} {cy}) rotate({angle})"><svg x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden"><image width="{w}" height="{h}" href="{u}" preserveAspectRatio="xMidYMid slice"/></svg></g>')
# 7x10 inch trim draft: 2x1.2 inch area, .25 inch inset from spine and bottom.
bx=(7-.25-2)/7*1049;by=(10-.25-1.2)/10*1499
# Barcode review overlay is appended last and hidden by default.
original=asset('cover.back.reference.v02')
parts.append(f'<defs><filter id="signature-soft-edge" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="7"/></filter><mask id="original-signature" maskUnits="userSpaceOnUse" x="295" y="1320" width="450" height="175"><rect x="318" y="1344" width="405" height="132" rx="24" fill="white" filter="url(#signature-soft-edge)"/></mask></defs><g id="original-signature-layer" transform="translate(-45 0)"><image width="1049" height="1499" href="{original}" mask="url(#original-signature)"/></g>')
mark=asset('06-listing.publisher-mark.drafts.giggling-house-v01')
parts.append(f'''<defs><filter id="publisher-yellow" x="-15%" y="-15%" width="130%" height="130%"><feMorphology in="SourceAlpha" operator="dilate" radius="2" result="edge"/><feFlood flood-color="#ffd56e"/><feComposite in2="edge" operator="in" result="yellow"/><feMerge><feMergeNode in="yellow"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><image x="58" y="1338" width="110" height="110" href="{mark}" filter="url(#publisher-yellow)"/>''')
parts.append(txt(113,1462,18,'Giggle Home','#ffd56e'))
parts.append(f'<g id="barcode-review-overlay" style="display:none"><rect x="{bx}" y="{by}" width="{2/7*1049}" height="{1.2/10*1499}" fill="white"/></g>')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="177.8mm" height="254mm" viewBox="0 0 1049 1499"><title>Halloween Rückseite DE v05</title><g font-family="Chalkboard SE, sans-serif">'+''.join(parts)+'</g></svg>'
ET.fromstring(svg);(OUT/'backcover-de-v05.svg').write_text(svg)
(OUT/'manifest.json').write_text(json.dumps({'sources':sources,'text_lines':lines,'status':'review_draft','visual_review':'user_pending','print_release':False,'barcode_mm':[50.8,30.48],'barcode_inset_mm':6.35,'barcode_overlay':'hidden; last layer; enable display to inspect','signature_shift_x':-45,'notes':['Illustrations are previews, not complete typeset page reproductions','Final cover template, bleed and barcode clearance must be checked before print']},ensure_ascii=False,indent=2)+'\n')
print('Rückseite mit editierbaren Texten und drei Vorschauen erstellt; XML/Quellen geprüft.')
