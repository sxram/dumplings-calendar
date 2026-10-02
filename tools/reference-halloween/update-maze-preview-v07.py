"""Show Dreamy above the maze in the existing cover frame."""
from pathlib import Path
from xml.etree import ElementTree as E
import json,hashlib
R=Path(__file__).resolve().parents[1];rp=R/'production/assets.json';reg=json.loads(rp.read_text())
a=reg['assets'][reg['selection']['current_cover_back_de']];src=R/a['path']
assert hashlib.sha256(src.read_bytes()).hexdigest()==a['sha256']
t=E.parse(src);n='{http://www.w3.org/2000/svg}'
groups=[e for e in t.iter(n+'g') if e.get('transform','').startswith('translate(') and e.find(n+'svg') is not None]
v=groups[1].find(n+'svg');v.set('viewBox','0 185 1049 738.185185')
for e in list(v):
 if e.tag==n+'rect':v.remove(e)
im=v.find(n+'image');im.set('width','1049');im.set('height','1499');im.set('y','0');im.set('preserveAspectRatio','xMidYMid meet')
o=R/'04-cover/drafts/back-de-v07';o.mkdir(exist_ok=False)
E.register_namespace('',n[1:-1]);p=o/'backcover-de-v07.svg';t.write(p,encoding='utf-8',xml_declaration=True)
k='cover.back.de.v07';reg['assets'][k]={'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'source','usage':'Labyrinth-Vorschau mit vollständig sichtbarem Dreamy oberhalb des Kürbisses','design_status':'review_pending','print_status':'not_released','issues':['Nutzerreview offen'],'origin':{'project':'dumplings-halloween','source':a['path'],'source_sha256':a['sha256'],'note':'Nur mittleren SVG-Ausschnitt verschoben: Quellbereich y185 bis923 statt zentriertem Anschnitt; Rahmen unverändert.'}}
reg['selection']['current_cover_back_de']=k;rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
