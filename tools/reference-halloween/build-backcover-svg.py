"""German back cover draft with unchanged registered raster sources."""
from pathlib import Path
import base64, hashlib, html, json
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04-cover/drafts/back-de-v01'
assert not OUT.exists(), 'Choose a new output version'
r=json.loads((ROOT/'production/assets.json').read_text()); sources={}
def uri(key):
    a=r['assets'][key]; b=(ROOT/a['path']).read_bytes()
    assert hashlib.sha256(b).hexdigest()==a['sha256']
    sources[key]={'path':a['path'],'sha256':a['sha256']}
    return 'data:image/png;base64,'+base64.b64encode(b).decode()
cover=uri('cover.background')
mark=uri('06-listing.publisher-mark.drafts.giggling-house-v01')
# Square source windows use the original cover's 1049 x 1499 coordinates.
people=[
 ('Sunny','#bd5628',(40,835,310),['Stürzt sich mutig ins Halloween-Abenteuer.','Na gut, meistens!']),
 ('Mochi','#b34b78',(230,1000,275),['Hat ein großes Herz –','auch für kleine Gespenster.']),
 ('Bao','#7950a1',(395,732,335),['Backt gruselig gute Leckereien','für die Halloween-Party.']),
 ('Nibbles','#347580',(550,1005,280),['Geht jedem Spuk auf die Spur.','Mit einer kleinen Snackpause.']),
 ('Dreamy','#7950a1',(755,915,285),['Träumt von gemütlichen Geistern','und kuscheligen Monstern.'])]
rows=[]
for i,(name,color,(x,y,w),lines) in enumerate(people):
    top=139+i*83
    rows.append(f'<circle cx="91" cy="{top+34}" r="35" fill="{color}" stroke="#edb35d" stroke-width="2"/>')
    rows.append(f'<svg x="58" y="{top+1}" width="66" height="66" viewBox="{x} {y} {w} {w}" overflow="hidden"><defs><clipPath id="portrait-{i}"><circle cx="{x+w/2}" cy="{y+w/2}" r="{w/2}"/></clipPath></defs><image width="1049" height="1499" href="{cover}" clip-path="url(#portrait-{i})"/></svg>')
    rows.append(f'<text x="145" y="{top+18}" font-size="23" font-weight="bold" fill="{color}">{name}</text>')
    for j,line in enumerate(lines):
        rows.append(f'<text x="145" y="{top+39+j*18}" font-size="13.5">{html.escape(line)}</text>')
    if i<4: rows.append(f'<path d="M145 {top+72} H445" stroke="#dfcaa1" stroke-width=".8"/>')
stars=''.join(f'<path transform="translate({x} {y}) scale({s})" d="M0 -7 L2 -2 L7 0 L2 2 L0 7 L-2 2 L-7 0 L-2 -2Z" fill="#ffca6c"/>' for x,y,s in [(18,84,1),(484,108,.8),(16,303,.7),(487,367,1),(19,558,1),(480,579,.7),(30,28,.6),(475,29,.8)])
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="177.8mm" height="254mm" viewBox="0 0 504 720">
<title>Giggle Dumplings – Halloween – Rückseitenentwurf Deutsch</title>
<defs><linearGradient id="night" x2="0" y2="1"><stop stop-color="#29113f"/><stop offset="1" stop-color="#623b7b"/></linearGradient></defs>
<rect width="504" height="720" fill="url(#night)"/>{stars}
<rect x="34" y="39" width="436" height="527" rx="36" fill="#fff5de" stroke="#f8b65c" stroke-width="2"/>
<g font-family="Chalkboard SE, sans-serif" fill="#39213f">
<g text-anchor="middle" font-weight="bold"><text x="252" y="78" font-size="27">Deine Freunde für eine</text><text x="252" y="110" font-size="27" fill="#b65c30">schaurig-schöne Zeit!</text></g>
{''.join(rows)}
<rect x="35" y="583" width="434" height="51" rx="18" fill="#f6aa50" stroke="#fff0cc" stroke-width="1.5"/>
<text x="252" y="604" text-anchor="middle" font-size="17" font-weight="bold">30 Ausmalbilder und jede Menge Rätsel,</text>
<text x="252" y="624" text-anchor="middle" font-size="17">Comics, Witze und Bastelspaß</text>
<rect x="38" y="647" width="67" height="61" rx="12" fill="#fff5de"/>
<image x="47" y="648" width="49" height="49" href="{mark}"/>
<text x="71.5" y="703" text-anchor="middle" font-size="9">Giggle Home</text>
<rect id="barcode-reserved" x="320" y="650" width="144" height="54" fill="white"/>
</g></svg>'''
ET.fromstring(svg);OUT.mkdir(parents=True)
(OUT/'backcover-de-v01.svg').write_text(svg)
(OUT/'manifest.json').write_text(json.dumps({'status':'review_draft','sources':sources,'characters':[{'name':n,'crop':c,'lines':l} for n,_,c,l in people],'visual_review':'user_pending','print_release':False,'barcode':'Placeholder only; final dimensions and placement require selected KDP template'},ensure_ascii=False,indent=2)+'\n')
print('Rückseiten-SVG und Manifest erstellt; Quellen und XML geprüft.')
