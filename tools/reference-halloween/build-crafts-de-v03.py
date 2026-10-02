"""Editable craft layouts; existing bitmap artwork retained via SVG viewports."""
from pathlib import Path
import base64, hashlib, json
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[1]
O=R/'03-coloring-pages/drafts/crafts-de-v04'
O.mkdir(exist_ok=False)
old=R/'03-coloring-pages/drafts/bastelideen-v01/images'
def text(x,y,s,size=12):
    from html import escape
    return f'<text x="{x}" y="{y}" font-size="{size}">{escape(s)}</text>'
def pic(file,box,x,y,w,h):
    data=base64.b64encode((old/file).read_bytes()).decode()
    iw,ih=(1536,1024) if 'pumpkin-pair' in file else (1024,1536)
    cid='crop'+hashlib.sha256(f'{file}{box}{x}{y}'.encode()).hexdigest()[:10]
    bx,by,bw,bh=map(float,box.split())
    return f'<defs><clipPath id="{cid}"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}"/></clipPath></defs><svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{box}" overflow="hidden" preserveAspectRatio="xMidYMid meet"><g clip-path="url(#{cid})"><image width="{iw}" height="{ih}" href="data:image/png;base64,{data}"/></g></svg>'
def page(name,title,body,steps):
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="215.9mm" height="279.4mm" viewBox="0 0 612 792"><rect width="612" height="792" fill="white"/><g font-family="Arial, sans-serif" fill="black">'
    svg+=text(48,42,title,24)+body
    for i,s in enumerate(steps): svg+=text(48,660+i*18,s,11)
    svg+=text(48,765,'Entwurf · Bei 100 % drucken · Kontrollstrecke: 5 cm',9)
    svg+='<path d="M405 762h141.732m-141.732 -3v6m141.732 -6v6" fill="none" stroke="black"/></g></svg>'
    ET.fromstring(svg)
    (O/name).write_text(svg)
def pumpkin(x,y,w,h,opened=False):
    # Controlled vector artwork; face is contained within each specified panel.
    mouth=('M-64 3 Q0 20 64 3 Q62 66 0 66 Q-62 66 -64 3Z' if opened else 'M-45 23 Q0 56 45 23')
    return f'''<g transform="translate({x} {y}) scale({w/180} {h/190})" stroke="black" stroke-width="2" stroke-linejoin="round" fill="white">
    <path d="M-9 -65 L-5 -91 Q8 -96 13 -85 L8 -65"/>
    <path d="M0 -65 C-90 -96 -106 54 -52 74 Q-28 91 0 78 Q28 91 52 74 C106 54 90 -96 0 -65Z"/>
    <path d="M-27 -60 Q-55 -25 -43 -4 M27 -60 Q55 -25 43 -4" fill="none"/>
    <path d="M-47 -24 Q-34 -39 -21 -24 M21 -24 Q34 -39 47 -24" fill="none"/>
    <path d="M0 -18L-8 -4H8Z"/><path d="{mouth}" fill="none"/>
    </g>'''
body=text(48,68,'Zwei Teile ausschneiden – eine Karte basteln.',12)
for y,label in [(103,'A · Außenseite'),(348,'B · Innenseite')]:
    body+=text(66,y-10,label,12)
    body+=f'<rect x="66" y="{y}" width="480" height="210" fill="none" stroke="black" stroke-width="1.2"/>'
    body+=f'<path d="M306 {y}v210" fill="none" stroke="black" stroke-dasharray="5 4"/>'
body+=pic('../../crafts-components-v04/pumpkin-pair.png','0 100 768 780',326,112,200,194)
body+=pic('../../crafts-components-v04/pumpkin-pair.png','768 100 768 780',326,357,200,194)
body+=text(95,421,'Was hat dein Kürbis',13)+text(95,443,'verschluckt?',13)
body+=text(95,479,'Male es hier hinein!',11)
body+=text(141,584,'A: Bild außen falten. B: Bild innen falten.',12)
body+=text(104,605,'Weiße Seiten zusammenkleben, obere Kanten gleich ausrichten.',11)
body+=text(156,624,'Die Mittelfalte bleibt als schmaler Streifen kleberfrei.',10)
page('03-kuerbiskarte-de.svg','Das Kürbis-Klappmaul',body,[
 '1  Male beide Kürbisse aus. Zeichne innen links deine Überraschung.',
 '2  Schneide die zwei Rechtecke aus. Falte beide an der gestrichelten Linie.',
 '3  Lege B in A: Bilder sichtbar, weiße Seiten aneinander, Oberkanten bündig.',
 '4  Klebe die weißen Seiten dünn zusammen. Lass die Mittelfalte kleberfrei.',
 '5  Schließe die Karte vorsichtig. Lass den Kleber trocknen. Fertig!'])
body=pic('../../crafts-components-v04/monster-mask.png','0 230 1024 930',66,100,480,436)
# Do not reuse invalid generated stick tab; mask body is isolated through viewport.
page('01-monstermaske-de.svg','Meine Dumpling-Monstermaske',body,[
 '1  Male die Maske aus. Klebe sie auf dünnen Karton.',
 '2  Schneide an der äußeren schwarzen Kontur entlang.',
 '3  Lass die Augen an den inneren schwarzen Kreisen ausschneiden.',
 '    Bitte eine erwachsene Person um Hilfe. Die Maske wird nicht gefaltet.',
 '4  Klebe einen stabilen Kartonstiel hinten an eine Wange.'])
body=pic('../../crafts-components-v04/pumpkin-mask.png','0 205 1024 1088',66,92,480,510)
page('02-kuerbismaske-de.svg','Meine Kürbismaske',body,[
 '1  Male den Kürbis aus und klebe ihn auf dünnen Karton.',
 '2  Schneide nur den Kürbis mit Blatt und Stiel aus; Sterne bleiben übrig.',
 '3  Lass die Augen an den inneren schwarzen Kreisen ausschneiden.',
 '4  Klebe einen stabilen Kartonstiel hinten an eine Wange.',
 'Bitte eine erwachsene Person um Hilfe beim Ausschneiden.'])
# Matching symmetric rounded rectangles provide reproducible back-to-back edges.
body=text(48,70,'Zwei Seiten – ein Schild zum Wenden.',12)
for i,(box,x) in enumerate([('45 472 450 820',65),('530 480 458 820',321)]):
    body+=f'<defs><clipPath id="sign{i}"><rect x="{x}" y="105" width="226" height="450" rx="24"/></clipPath></defs>'
    body+=f'<g clip-path="url(#sign{i})">'+pic('B07-wendetuer-schild-v01.png',box,x+9,158,208,379)+'</g>'
    body+=f'<rect x="{x}" y="105" width="226" height="450" rx="24" fill="none" stroke="black" stroke-width="1.5"/><circle cx="{x+113}" cy="130" r="9" fill="white" stroke="black"/>'
page('04-wendetuer-schild-de.svg','Mein Wendetürschild',body,[
 '1  Male beide Schildseiten aus.',
 '2  Schneide an den äußeren abgerundeten Rechtecken entlang.',
 '3  Klebe die weißen Rückseiten zusammen, Oberkanten gleich ausgerichtet.',
 '4  Lass das obere Loch durch beide Lagen ausschneiden.',
 '5  Ziehe eine kurze Schnur durch das Loch und hänge das Schild auf.'])
manifest={'status':'review_draft','language':'de','page_mm':[215.9,279.4],
 'pages':[{'path':p.name,'blank_reverse':True} for p in sorted(O.glob('*.svg'))],
 'card':{'pieces':2,'piece_pt':[480,210],'fold_x':306,'front_face_panel':'right','inside_face_panel':'right','equal_face_viewports_pt':[200,194],'back_to_back':True,'physical_test':'open'},
 'review':'Nutzerreview offen; Maskenlinien und rasterbasierte Motive noch nicht druckfreigegeben',
 'replaces':['B01 mask','B02 mask','B06 old pumpkin card','B07 finger puppets'],
 'retained_existing':['B03 standees','B04 standees','B05 standees','B08 garland'],
 'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in old.glob('*.png')}}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
html='<html lang="de"><meta charset="utf-8"><title>Neue Bastelseiten</title><style>body{background:#eee;font-family:sans-serif}object{width: min(95vw,750px);height:970px;display:block;margin:20px auto;background:white}h1,p{text-align:center}</style><h1>Neue Bastelseiten · Entwurf</h1><p>Kürbiskarte: zwei Teile Rücken an Rücken kleben. Papierprobe und Nutzerreview offen.</p>'
for p in sorted(O.glob('*.svg')): html+=f'<object data="{p.name}" type="image/svg+xml"></object>'
(O/'index.html').write_text(html+'</html>')
print('4 SVG-Seiten + Übersicht + Manifest angelegt; SVG-Struktur gültig.')
