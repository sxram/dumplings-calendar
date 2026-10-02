"""Reposition existing preview art in editable SVG; preserve approved originals."""
from pathlib import Path
import base64,json,hashlib
from xml.etree import ElementTree as E
R=Path(__file__).resolve().parents[1];regpath=R/'production/assets.json'
reg=json.loads(regpath.read_text());old=reg['assets'][reg['selection']['current_cover_back_de']]
src=R/old['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==old['sha256']
tree=E.parse(src);root=tree.getroot();ns='{http://www.w3.org/2000/svg}'
groups=[e for e in root.iter(ns+'g') if e.get('transform','').startswith('translate(') and e.find(ns+'svg') is not None]
assert len(groups)==3
middle=groups[1].find(ns+'svg');im=middle.find(ns+'image');im.set('y','18')
middle.insert(0,E.Element(ns+'rect',{'width':'270','height':'190','fill':'white'}))
right=groups[2].find(ns+'svg');right.set('viewBox','0 240 1122 853')
replacement=R/'03-coloring-pages/drafts/v01/14-monster-picnic.png'
a=next(a for a in reg['assets'].values() if a['path']==str(replacement.relative_to(R)))
assert hashlib.sha256(replacement.read_bytes()).hexdigest()==a['sha256']
im=right.find(ns+'image');im.set('width','1122');im.set('height','1402');im.set('preserveAspectRatio','xMidYMid meet');im.set('href','data:image/png;base64,'+base64.b64encode(replacement.read_bytes()).decode())
out=R/'04-cover/drafts/back-de-v06';out.mkdir(exist_ok=False)
E.register_namespace('',ns[1:-1]);f=out/'backcover-de-v06.svg';tree.write(f,encoding='utf-8',xml_declaration=True)
manifest={'source':old['path'],'source_sha256':old['sha256'],'replacement':a['path'],'replacement_sha256':a['sha256'],'changes':['Mittleres Labyrinth innerhalb des festen Rahmens 18 SVG-Einheiten nach unten verschoben','Rechter Rahmen: Picknick mit Monstern, Ausschnitt mit vollständigen Köpfen und Figuren','Linke Vorschau unverändert'],'design_status':'review_pending','print_status':'not_released'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for path in [f,out/'manifest.json']:
 k='cover.back.de.v06'+('.manifest' if path.suffix=='.json' else '')
 reg['assets'][k]={'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':'source','usage':'Rückseite mit korrigierten Vorschauen','design_status':'review_pending','print_status':'not_released','issues':['Nutzerreview offen'],'origin':{'project':'dumplings-halloween','note':'Layoutänderung vorhandener registrierter Quellen; keine Bildgenerierung.'}}
reg['selection']['current_cover_back_de']='cover.back.de.v06'
regpath.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
