"""German editable mask sheets, no PDFs or automatic rendering."""
import argparse, base64, hashlib, json
from pathlib import Path
from xml.etree import ElementTree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'05-kdp/specials/drafts/masks-v02'
r=json.loads((ROOT/'production/assets.json').read_text())
sunny=r['assets']['mask.sunny.v02'];sp=ROOT/sunny['path']
assert hashlib.sha256(sp.read_bytes()).hexdigest()==sunny['sha256']
items=[('sunny','Sunny als kleiner Vampir',sp),('pumpkin','Meine Kürbis-Fotomaske',OUT/'pumpkin-mask-v01.png')]
parser=argparse.ArgumentParser()
parser.add_argument('--mask',choices=['sunny','pumpkin'])
parser.add_argument('--version',default='v03')
args=parser.parse_args()
for key,title,source in items:
    if args.mask and key!=args.mask:continue
    dest=OUT/f'{key}-maske-de-{args.version}.svg'
    assert not dest.exists(), 'Use a new version instead of overwriting'
    data=base64.b64encode(source.read_bytes()).decode()
    # Preserve existing Sunny layout geometry; pumpkin is a new unreviewed component.
    if key=='sunny':
        eyes=[(525,596,87,46),(1005,596,87,46)]
        outline='M676 47 C696 -20 813 -20 842 49 C1044 68 1176 185 1188 385 C1330 507 1330 747 1168 883 C985 1042 539 1038 344 877 C205 757 214 566 275 468 C239 470 239 406 311 358 C340 182 476 75 676 47 Z'
    else:
        # Measured against the actual pumpkin source, not the generation prompt.
        eyes=[(525,539,133,78),(1008,539,133,78)]
        outline='M 688 72 C 675 20 796 8 830 48 C 850 78 861 113 870 140 C 866 103 877 77 895 60 Q 905 58 913 65 Q 928 38 962 32 Q 977 30 987 56 C 1030 23 1077 58 1128 83 Q 1143 94 1127 108 C 1102 131 1109 150 1067 168 Q 1084 184 1089 200 C 1225 206 1330 360 1359 524 C 1393 724 1296 933 1129 949 Q 1105 953 1080 948 C 1024 976 960 984 910 970 Q 844 1004 768 984 Q 689 1004 620 970 C 567 984 500 976 452 948 C 301 977 187 818 173 650 C 151 474 228 307 350 232 Q 425 194 490 201 C 545 160 614 160 678 189 C 705 157 708 117 688 72 Z'
    eye_svg=''.join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>' for cx,cy,rx,ry in eyes)
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="177.8mm" height="254mm" viewBox="0 0 504 720">
<rect width="504" height="720" fill="white"/>
<g font-family="Chalkboard SE, sans-serif" fill="black"><text x="36" y="42" font-size="23">{title}</text></g>
<g transform="translate(-12 98) scale(.34375)" fill="none" stroke="black">
<image href="data:image/png;base64,{data}" width="1536" height="1024"/>
<g id="schnittlinien" stroke-width="1.6"><path d="{outline}"/>
{eye_svg}</g>
<rect id="klebeflaeche" x="1020" y="740" width="87" height="81" stroke-width="1.6" stroke-dasharray="3 6"/>
</g>
<g font-family="Chalkboard SE, sans-serif" font-size="10.5" fill="black">
<text x="36" y="480">1  Male die Maske aus und klebe das Blatt auf dünnen Karton.</text>
<text x="36" y="497">2  Schneide an der feinen äußeren Linie aus.</text>
<text x="36" y="514">3  Lass die kleinen inneren Augenovale ausschneiden.</text>
<text x="36" y="531">    Bitte eine erwachsene Person um Hilfe.</text>
<text x="36" y="548">4  Klebe das markierte Stielende hinten an die punktierte Stelle.</text>
<text x="36" y="565">    Lass den Kleber trocknen. Halte die Maske für ein Foto hoch!</text>
<text x="248" y="590" font-size="9">Stiel: linkes Ende hinten ankleben</text>
</g>
<g id="stiel" fill="none" stroke="black" stroke-width=".65"><rect x="248" y="600" width="194" height="30" rx="3"/><path d="M276 600 V630" stroke-dasharray="1 2"/></g>
<g font-family="sans-serif" font-size="9"><text x="36" y="653">Bei 100 % drucken. Kontrollmaß: 5 cm</text></g>
<path d="M36 669 H177.732 M36 666 V672 M177.732 666 V672" fill="none" stroke="black"/>
</svg>'''
    ElementTree.fromstring(svg)
    dest.write_text(svg)
    print(dest.name,'SVG structure valid')
