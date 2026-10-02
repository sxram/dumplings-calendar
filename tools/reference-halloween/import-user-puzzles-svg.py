"""Import registered user puzzles, preserving image bytes; no raster or PDF export."""
import base64, hashlib, html, json, argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',default='05-kdp/specials/drafts/user-puzzles-v01');args=p.parse_args()
out=(ROOT/args.output).resolve();assert out.is_relative_to(ROOT) and not out.exists()
r=json.loads((ROOT/'production/assets.json').read_text())
titles=['Suchbild im Garten','Der Weg durch den Kürbis','Finde die Unterschiede','Unterschiede in der Backstube','Nibbles und sein Schatten','Welche Paare gehören zusammen?','Halloween-Bilder-Sudoku','Baos Spiegelbild']
entries=[];sources={};pending=[]
for n,title in enumerate(titles,1):
 sid=r['selection'][f'current_user_solution_{n:02}'];sol=r['assets'][sid]
 aid=next(k for k,a in r['assets'].items() if a['path']==sol['puzzle_path_by_filename'])
 for kind,key in [('aufgabe',aid),('loesung',sid)]:
  a=r['assets'][key];src=ROOT/a['path'];raw=src.read_bytes()
  assert hashlib.sha256(raw).hexdigest()==a['sha256'] and a['design_status']!='rejected'
  with Image.open(src) as im:iw,ih=im.size
  sources[key]={'path':a['path'],'sha256':a['sha256']}
  w,h=408,584;scale=min(w/iw,h/ih);w,h=iw*scale,ih*scale;x,y=(504-w)/2,84+(584-h)/2
  heading=f'{"Lösung" if kind=="loesung" else "Rätsel"} {n:02}'
  filter_def='<filter id="monochrom" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 1 0 0  0 0 1 0 0  0 0 1 0 0  0 0 0 1 0"/></filter>'
  svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="177.8mm" height="254mm" viewBox="0 0 504 720">
<defs>{filter_def}</defs><rect width="504" height="720" fill="white"/>
<g stroke="black" fill="none" stroke-width=".6"><line x1="48" y1="670" x2="456" y2="670"/></g>
<g id="deutscher-titel" fill="black" font-family="Chalkboard SE, sans-serif"><text x="48" y="35" font-size="11">{heading}</text><text x="48" y="62" font-size="18">{html.escape(title)}</text></g>
<image id="originalvorlage" x="{x:.4f}" y="{y:.4f}" width="{w:.4f}" height="{h:.4f}" preserveAspectRatio="xMidYMid meet" {('filter="url(#monochrom)"' if kind=='loesung' else '')} href="data:image/png;base64,{base64.b64encode(raw).decode()}"/>
<text x="48" y="693" font-family="Chalkboard SE, sans-serif" font-size="8">Giggle Dumplings</text><text x="456" y="693" text-anchor="end" font-family="sans-serif" font-size="9">{heading}</text></svg>'''
  ET.fromstring(svg);name=f'{n:02}-{kind}-de.svg';pending.append((name,svg))
  entries.append({'number':n,'kind':kind,'source_id':key,'file':name,'title':title,'image_px':[iw,ih],'image_box_pt':[x,y,w,h],'effective_dpi':72/scale,'visual_review':'user_pending'})
out.mkdir(parents=True)
for name,svg in pending:(out/name).write_text(svg)
# Future page plan, including the separately requested craft introduction move.
base=r['assets'][r['selection']['current_review_manifest']];plan=json.loads((ROOT/base['path']).read_text())['page_plan'];new=[]
after=dict(zip(['03','07','11','14','18','22','26','29'],range(1,9)))
intro=next(x for x in plan if x['id']=='craft-introduction')
for i,old in enumerate(plan):
 if old['id']=='B01':new.extend([{'id':'craft-introduction','kind':'front'},{'id':'reverse-craft-introduction','kind':'blank'}])
 if old['id']=='craft-introduction':new.append({'id':'reverse-welcome','kind':'blank'})
 else:new.append({'id':old['id'],'kind':old['kind'],'source_pdf_page':old['pdf_page']})
 if old['kind']=='blank' and i and plan[i-1]['kind']=='coloring' and plan[i-1]['id'] in after:
  n=after[plan[i-1]['id']];new.extend([{'id':f'R{n:02}','kind':'puzzle'},{'id':f'reverse-R{n:02}','kind':'blank'}])
for n in range(1,9):new.extend([{'id':f'L{n:02}','kind':'solution'},{'id':f'reverse-L{n:02}','kind':'blank'}])
for i,item in enumerate(new):item.update(pdf_page=i+1,interior_page=i or None)
for i,item in enumerate(new):
 if item['kind'] in ('puzzle','solution','coloring','comic','mini','jokes','crafts'):
  assert i%2==1 and new[i+1]['kind']=='blank'
assert sum(x['kind']=='coloring' for x in new)==30
assert sum(x['kind']=='puzzle' for x in new)==sum(x['kind']=='solution' for x in new)==8
m={'status':'review_draft','sources':sources,'baseline':base,'entries':entries,'page_plan':new,'planned_interior_pages':len(new)-1,'visual_review':'user_pending','embedded_text_review':'open','print_release':False,'pdf_created':False}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
links=''.join(f'<li><a href="{e["file"]}">{e["number"]:02} – {e["kind"]}: {html.escape(e["title"])}</a></li>' for e in entries)
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rätsel und Lösungen</title><h1>Rätsel und Lösungen – Entwurf</h1><p>Originale erhalten. Sichtprüfung offen. Layout und Titel editierbar; eingebettete Bildtexte sind Rasterbestandteile.</p><ul>'+links+'</ul>')
print(f'{len(entries)} SVG-Seiten; acht Aufgaben und acht Lösungen; geplanter Umfang {len(new)-1} Innenseiten; keine PDFs.')
