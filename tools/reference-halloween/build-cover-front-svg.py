"""Assemble editable German cover draft from registered, unchanged images."""
from pathlib import Path
import base64, hashlib, json, math
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '04-cover/drafts/front-de-v06'
assert not OUT.exists(), 'Use a new version for revisions'
registry = json.loads((ROOT / 'production/assets.json').read_text())
sources = {}
def source(key):
    a = registry['assets'][key]
    data = (ROOT / a['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == a['sha256'], key
    sources[key] = {'path': a['path'], 'sha256': a['sha256']}
    return data
def image(key, x, y, w, h):
    data = base64.b64encode(source(key)).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{data}"/>'
background = image('cover.background', 0, 0, 504, 720)
title = image('cover.title.transparent.v02', 24, 20, 456, 228)
banner = ET.fromstring(source('cover.banner.de.v06'))
banner.set('x', '0'); banner.set('y', '211')
banner.set('width', '504'); banner.set('height', '100')
banner_svg = ET.tostring(banner, encoding='unicode')
points = ' '.join(f'{(49 if i%2==0 else 42)*math.cos(i*math.pi/12):.2f},{(49 if i%2==0 else 42)*math.sin(i*math.pi/12):.2f}' for i in range(24))
stickers = '''<defs><linearGradient id="seal-orange" x2="0" y2="1"><stop stop-color="#ffcf70"/><stop offset=".5" stop-color="#ff8f35"/><stop offset="1" stop-color="#d64e32"/></linearGradient><linearGradient id="seal-purple" x2="0" y2="1"><stop stop-color="#bb86db"/><stop offset=".5" stop-color="#8550b2"/><stop offset="1" stop-color="#51317c"/></linearGradient></defs><g xmlns="http://www.w3.org/2000/svg" font-family="Chalkboard SE, sans-serif" text-anchor="middle" stroke-linejoin="round">
<g id="sticker-ausmalbilder" transform="translate(66 331) rotate(-9)">
<circle cy="3" r="45" fill="#21112e" opacity=".5"/>
<polygon points="POINTS" fill="url(#seal-orange)" stroke="#fff1c9" stroke-width="2.5"/>
<polygon points="POINTS" transform="scale(.86)" fill="none" stroke="#ffe2a4" stroke-width=".9"/>
<text y="-7" font-size="35" font-weight="bold" fill="#fff7df" stroke="#83374a" stroke-width=".7" paint-order="stroke fill">30</text>
<text x="0" y="12" font-size="14" fill="#fff7df">Ausmal-</text>
<text x="0" y="28" font-size="14" fill="#fff7df">bilder</text>
</g>
<g id="sticker-raetsel" transform="translate(436 331) rotate(9)">
<circle cy="3" r="45" fill="#21112e" opacity=".5"/>
<polygon points="POINTS" fill="url(#seal-purple)" stroke="#fff1c9" stroke-width="2.5"/>
<polygon points="POINTS" transform="scale(.86)" fill="none" stroke="#eacbff" stroke-width=".9"/>
<text x="0" y="-11" font-size="28" fill="#fff7df">+</text>
<text x="0" y="15" font-size="23" font-weight="bold" fill="#fff7df">Rätsel</text>
</g>
<g id="sticker-extras">
<rect x="80" y="674" width="344" height="32" rx="16" fill="#21112e" opacity=".5"/>
<rect x="80" y="671" width="344" height="32" rx="16" fill="#fff0cb" stroke="#edaa56" stroke-width="1.5"/>
<text x="252" y="693" font-size="18" fill="#432343">Mit Comics, Witzen &amp; Bastelspaß</text>
</g></g>'''
stickers = stickers.replace('POINTS', points)
decor = '''<g id="halloween-dekor" stroke-linecap="round" stroke-linejoin="round">
+<defs>
+<g id="funkel"><path d="M0 -8 Q1 -1 6 0 Q1 1 0 8 Q-1 1 -6 0 Q-1 -1 0 -8Z" fill="#ffcf70"/><circle cx="0" cy="0" r="1.2" fill="#fff6d5"/></g>
+<g id="fledermaus"><path d="M-3 0 L-2 -4 L0 -2 L2 -4 L3 0 Q12 -9 21 -7 Q16 -1 20 4 Q13 0 10 7 Q5 3 2 7 L0 9 L-2 7 Q-5 3 -10 7 Q-13 0 -20 4 Q-16 -1 -21 -7 Q-12 -9 -3 0Z" fill="#9865b5" stroke="#d6a2e4" stroke-width=".7"/><circle cx="-1.4" cy="1" r=".7" fill="#ffe6a6"/><circle cx="1.4" cy="1" r=".7" fill="#ffe6a6"/></g>
+</defs>
+<g fill="none" stroke="#c39ad8" stroke-width=".8" opacity=".6">
+<path d="M4 4 L70 4 M4 4 L4 70 M4 4 L51 51 M4 4 L67 28 M4 4 L28 67 M4 24 Q12 22 18 18 Q22 12 24 4 M4 44 Q21 39 32 32 Q39 21 44 4 M4 64 Q30 59 47 47 Q59 30 64 4"/>
+<path d="M500 4 L434 4 M500 4 L500 70 M500 4 L453 51 M500 4 L437 28 M500 4 L476 67 M500 24 Q492 22 486 18 Q482 12 480 4 M500 44 Q483 39 472 32 Q465 21 460 4 M500 64 Q474 59 457 47 Q445 30 440 4"/>
+</g>
+<use href="#fledermaus" transform="translate(61 70) rotate(-18)"/>
+<use href="#fledermaus" transform="translate(452 67) rotate(18) scale(.8)"/>
+<use href="#funkel" transform="translate(91 28)"/><use href="#funkel" transform="translate(410 27) scale(.8)"/>
+<use href="#funkel" transform="translate(28 113) scale(.7)"/><use href="#funkel" transform="translate(475 116)"/>
+<use href="#funkel" transform="translate(160 18) scale(.5)"/><use href="#funkel" transform="translate(343 18) scale(.6)"/>
+<g fill="#ffcc78"><circle cx="114" cy="45" r="1.8"/><circle cx="390" cy="50" r="1.5"/><circle cx="23" cy="88" r="1.7"/><circle cx="483" cy="87" r="1.8"/></g>
+</g>'''.replace('\n+', '\n')
svg = f''' <svg xmlns="http://www.w3.org/2000/svg" width="177.8mm" height="254mm" viewBox="0 0 504 720">
<title>Giggle Dumplings – Das große Halloween-Special – Coverentwurf DE</title>
{background}{decor}

{title}{banner_svg}{stickers}</svg>'''
ET.fromstring(svg)
OUT.mkdir(parents=True)
(OUT/'cover-front-de-v06.svg').write_text(svg)
(OUT/'stickers-de-v05.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 504 720">'+stickers+'</svg>')
(OUT/'manifest.json').write_text(json.dumps({'status':'review_draft', 'sources':sources, 'claims':['30 Ausmalbilder','+ Rätsel','Mit Comics, Witzen & Bastelspaß'], 'claim_basis':'30 Motive und 8 Nutzer-Rätsel laut aktuellem Seitenplan; Comics, Witze und Bastelvorlagen vorhanden', 'visual_review':'user_pending', 'print_release':False, 'note':'Vorderseitenentwurf; keine Rücken-/Beschnittberechnung. Rasterquellen unverändert eingebettet; Schrift benötigt Chalkboard SE.'},ensure_ascii=False,indent=2)+'\n')
print('Cover-SVG, separate Aufkleberebene und Manifest erstellt; XML geprüft.')
