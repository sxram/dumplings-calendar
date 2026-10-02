"""Non-mutating PDF checks plus a registered English edition check report."""
from pathlib import Path
import json,hashlib
from collections import Counter
import pdfplumber
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];E=R/'editions/en';O=E/'output/v01'
reg=json.loads((R/'production/assets.json').read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'manifest.json').read_text());interior=O/'Giggle-Dumplings-Halloween-EN-Interior-v01.pdf';cover=O/'Giggle-Dumplings-Halloween-EN-Cover-v01.pdf'
assert digest(interior)==m['outputs'][interior.name]
assert digest(cover)==m['outputs'][cover.name]
for a in m['source_assets'].values():assert digest(R/a['path'])==a['sha256'],a['path']
r=PdfReader(interior);cr=PdfReader(cover);assert len(r.pages)==128 and len(cr.pages)==1
assert all(tuple(map(float,p.mediabox))==(0.,0.,612.,792.) for p in r.pages)
assert abs(float(cr.pages[0].mediabox.width)-1262.754432)<.01 and float(cr.pages[0].mediabox.height)==810
text='\n'.join(p.extract_text() for p in r.pages)
for s in ['Entwurf','Rätsel','Lösung','DEUTSCHE','Klebelasche','Ausmalbilder','Fledermaus','Herausgeber','Bastelzeit']:assert s not in text,s
counts=Counter(e['kind'] for e in m['page_plan']);assert counts==m['counts']
assert len({e['id'] for e in m['page_plan'] if e['kind']=='coloring'})==30
for e in m['page_plan']:
    if e['kind']=='blank':assert not r.pages[e['page']-1].extract_text().strip()
margin_issues=[]
with pdfplumber.open(interior) as pdf:
    for n,p in enumerate(pdf.pages,1):
        for ch in p.chars:
            if ch['text'].strip() and (ch['x0']<18 or ch['x1']>594 or ch['top']<18 or ch['bottom']>774):margin_issues.append([n,ch['text'],ch['x0'],ch['top']])
assert not margin_issues,margin_issues[:5]
def resources(reader):
    seen=set();spaces=Counter();unembedded=[]
    def visit(res):
        for ob in res.get('/Font',{}).values():
            f=ob.get_object()
            if f.get('/Subtype')=='/Type3':continue
            ff=f.get('/DescendantFonts',[f])[0].get_object();d=ff.get('/FontDescriptor',{});d=d.get_object() if hasattr(d,'get_object') else d
            if not any(k in d for k in ['/FontFile','/FontFile2','/FontFile3']):unembedded.append(str(f.get('/BaseFont')))
        for ob in res.get('/XObject',{}).values():
            x=ob.get_object()
            if id(x) in seen:continue
            seen.add(id(x))
            if x.get('/Subtype')=='/Image' and not x.get('/ImageMask'):spaces[str(x.get('/ColorSpace'))]+=1
            if x.get('/Subtype')=='/Form':visit(x.get('/Resources',{}))
    for p in reader.pages:visit(p.get('/Resources',{}))
    assert not unembedded,unembedded
    return dict(spaces)
ics=resources(r);ccs=resources(cr)
assert all(k=='/DeviceGray' for k in ics),ics
assert all(k=='/DeviceCMYK' for k in ccs),ccs
report={'date':'2026-09-30','result':'technical_checks_passed','pages':128,'counts':dict(counts),'trim_pt':[612,792],'cover_pt':[float(cr.pages[0].mediabox.width),810],'all_used_fonts_embedded':True,'interior_image_color_spaces':ics,'cover_image_color_spaces':ccs,'text_outside_18pt_safe_area':margin_issues,'blank_backs_verified':62,'source_hashes_unchanged':True,'german_native_text_scan':'passed','paragraph_fit_checks':len(m['paragraph_fit_checks']),'targeted_visual_checks':['English cover: translated title, badge, spine, back copy and retained preview crops','Page 3: welcome and ownership line','Page 19: updated C01 dialogue rail','Page 53: embedded title/instructions and decorative contours','Page 117: standee instruction area','Page 123: embedded door-sign lettering','Page 125: garland text and tabs'],'full_book_visual_review':'not performed; user review pending','kdp_preview':'pending','craft_paper_test':'pending','print_release':False,'native_resolution_warning':'Inherited raster quality; cover background approximately 136–140 dpi effective. Rendering at 300 dpi does not add native detail.'}
approved=m.get('user_visual_review','').startswith('approved_by_user')
if approved:
    report['full_book_visual_review']='User confirmed the English edition looks good on 2026-09-30; assistant performed targeted checks only.'
p=O/'checks.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for p in [p,E/'README.md',E/'listing-v01.md',E/'ocr-check-v01.json']:
    key='edition.en.v01.'+p.relative_to(E).as_posix().replace('/','.')
    reg['assets'][key]={'path':str(p.relative_to(R)),'sha256':digest(p),'role':'derived','usage':'English edition production documentation and technical checks','design_status':'review_pending','print_status':'not_released','issues':['English user review and KDP preview pending'],'origin':{'project':'dumplings-halloween','source':'editions/en/output/v01/manifest.json'}}
if approved:
    for key,a in reg['assets'].items():
        if key.startswith('edition.en.v01.'):
            a['design_status']='user_approved'
            a['issues']=['User visual review approved 2026-09-30; KDP preview and physical craft test pending']
else:
    reg['issues']['english_edition']='EN v01 komplett: 128 Seiten, 30 Ausmalmotive, 8 Rätsel, 7 Bastelseiten; Innenbuch und Umschlag unter editions/en/output/v01. Struktur/Satz/Quellprüfungen bestanden. Nutzerreview, KDP-Vorschau und Papierprobe offen; DE v11 unverändert.'
reg['issues']['puzzles']='Aktuell acht Rätselseiten und zwei Sammel-Lösungsseiten im 128-seitigen DE-/EN-Innenbuch; ältere 144-Seiten-Planung überholt.'
reg['issues']['specials']='Aktuell sieben Bastelseiten: zwei Fotomasken, drei Aufsteller-Seiten, Wendetürschild, Girlande. Kürbis-Klappmaul/Karte, Fingerpuppen und Einladung entfernt. Reale Papierprobe offen.'
(R/'production/assets.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pages':128,'safe_area_issues':0,'fonts':'embedded','interior':'grayscale','cover':'CMYK','sources':'unchanged','user_review':'pending'},ensure_ascii=False))
