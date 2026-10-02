"""Assemble registered, approved front matter with existing review pages.
Never runs the legacy illustrator/layout builder. Preserves page graphics and text,
except the explicitly renumbered footer of shifted content pages.
"""
import sys
sys.dont_write_bytecode=True
import argparse, copy, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import TextStringObject, FloatObject
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py')
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
PAINT={b'Do',b'Tj',b'TJ',b"'",b'"',b'S',b's',b'f',b'F',b'f*',b'B',b'B*',b'b',b'b*',b'sh'}

def blank(page):
 stream=page.get_contents()
 return not stream or not any(op in PAINT for _,op in stream.operations)

def assets(page):
 result={}
 for name,obj in page.get('/Resources',{}).get('/XObject',{}).items():
  obj=obj.get_object();result[str(name)]=hashlib.sha256(obj.get_data()).hexdigest()
 return result

def footer_update(page,old,new):
 stream=page.get_contents(); ops=stream.operations
 candidates=[]
 for i,(args,op) in enumerate(ops):
  if op==b'Tj' and str(args[0])==str(old):
   nearby=ops[max(0,i-5):i]
   tm=next((a for a,o in nearby if o==b'Tm' and float(a[-1])==15),None)
   tf=next((a for a,o in nearby if o==b'Tf'),None)
   if tm is not None and tf is not None: candidates.append((i,tm,tf))
 if len(candidates)!=1: raise ValueError(f'Expected one known footer {old}: {len(candidates)}')
 i,tm,tf=candidates[0]
 font=page['/Resources']['/Font'][tf[0]].get_object()
 first=int(font['/FirstChar']); widths=font['/Widths']; size=float(tf[1])
 width=lambda s:sum(float(widths[ord(ch)-first]) for ch in str(s))*size/1000
 tm[4]=FloatObject(float(tm[4])+width(old)-width(new))
 ops[i][0][0]=TextStringObject(str(new))
 page.replace_contents(stream)
 return i

def run(output):
 r=json.loads((ROOT/'production/assets.json').read_text())
 errors=checks.check(r)
 if errors: raise ValueError('\n'.join(errors))
 used={}
 def selected(key,approved=False):
  aid=r['selection'][key];a=r['assets'][aid]
  if a['design_status'] in ('reference_only','rejected'):raise ValueError(f'Blocked source {aid}')
  if approved and a['design_status']!='approved':raise ValueError(f'Approval missing: {aid}')
  used[aid]=copy.deepcopy(a)
  return ROOT/a['path'],aid
 fm_path,fm_id=selected('frontmatter_pages',True); im_path,im_id=selected('imprint_pages',True)
 baseline_path,baseline_id=selected('review_baseline_manifest')
 baseline=json.loads(baseline_path.read_text());old_plan=baseline['page_plan']
 assert baseline['review_pages']==109 and baseline['interior_pages']==108
 output=output.resolve();assert output.is_relative_to(ROOT)
 if output.exists():raise ValueError('Select a new, unused version directory')
 inputs={lang:selected('review_baseline_'+lang) for lang in ('de','en','es')}
 fm=PdfReader(fm_path);im=PdfReader(im_path);assert len(fm.pages)==6 and len(im.pages)==3
 plan=[]
 def record(kind,sid,**extras):
  n=len(plan);p={'pdf_page':n+1,'interior_page':n or None,'kind':kind,'id':sid,**extras}
  if n:p['side']='recto' if n%2 else 'verso'
  plan.append(p)
 record('cover','cover')
 for kind,sid in [('front','title'),('front','imprint'),('front','welcome'),('front','craft-introduction'),('front','pips'),('blank','reverse-pips')]:record(kind,sid)
 for p in old_plan[5:]:record(p['kind'],p['id'],baseline_pdf_page=p['pdf_page'])
 counts=Counter(p['kind'] for p in plan)
 assert counts['coloring']==30 and counts['comic']==6 and counts['mini']==4 and counts['jokes']==4 and counts['crafts']==8
 assert len({p['id'] for p in plan if p['kind']=='coloring'})==30
 for i,p in enumerate(plan):
  if p['kind'] in ('coloring','comic','jokes','mini','crafts'):
   assert p['side']=='recto' and plan[i+1]['kind']=='blank' and plan[i+1]['side']=='verso'
 assert (len(plan)-1)%2==0
 output.mkdir(parents=True)
 editions=[]
 for li,lang in enumerate(('de','en','es')):
  base_path,base_id=inputs[lang];base=PdfReader(base_path);assert len(base.pages)==109
  writer=PdfWriter();origins=[]
  first=[(base,0,base_id),(fm,li*2,fm_id),(im,li,im_id),(base,3,base_id),(base,4,base_id),(fm,li*2+1,fm_id)]
  for reader,index,aid in first:
   writer.add_page(reader.pages[index]);origins.append({'source_id':aid,'source_pdf_page':index+1})
  writer.add_blank_page(width=504,height=720);origins.append({'new_blank':True})
  for p in old_plan[5:]:
   page=writer.add_page(base.pages[p['pdf_page']-1]);entry={'source_id':base_id,'source_pdf_page':p['pdf_page']}
   if p['kind']!='blank':
    footer_update(page,p['interior_page'],p['interior_page']+2)
    entry['footer_change']=[p['interior_page'],p['interior_page']+2]
   origins.append(entry)
  writer.add_metadata({'/Title':f'Giggle Dumplings - Halloween - {lang.upper()} - Sichtfassung v02','/Author':'Stefan Marx','/Subject':f'Sichtfassung, keine Druckfreigabe; {len(plan)-1} Innenseiten plus separate Covervorschau'})
  dest=output/f'giggle-dumplings-halloween-{lang}-review-v02.pdf'
  with dest.open('xb') as f:writer.write(f)
  rendered=PdfReader(dest);assert len(rendered.pages)==len(plan)
  sources={base_id:base,fm_id:fm,im_id:im}
  for p,page,origin in zip(plan,rendered.pages,origins):
   assert tuple(map(float,page.mediabox))==(0,0,504,720)
   if p['kind']=='blank':assert blank(page),p
   if origin.get('new_blank'):continue
   source=sources[origin['source_id']].pages[origin['source_pdf_page']-1]
   # Copy the source into an independent writer before applying the expected footer change.
   verifier=PdfWriter();expected=verifier.add_page(source)
   if 'footer_change' in origin:footer_update(expected,*origin['footer_change'])
   assert expected.get_contents().operations==page.get_contents().operations,(lang,p['pdf_page'],'changed content operators')
   assert assets(expected)==assets(page),(lang,p['pdf_page'],'changed embedded image')
   expected_text=source.extract_text()
   if 'footer_change' in origin:
    old,new=origin['footer_change']; token=f'Giggle Dumplings\n{old}\n'
    assert expected_text.count(token)==1
    expected_text=expected_text.replace(token,f'Giggle Dumplings\n{new}\n')
   assert expected_text==page.extract_text(),(lang,p['pdf_page'],'changed text')
  editions.append({'language':lang,'path':dest.relative_to(ROOT).as_posix(),'sha256':checks.digest(dest),'pages':len(plan),'sources_by_page':origins,'checks':{'page_dimensions':True,'blank_reverses':True,'page_streams_match_expected_sources':True,'embedded_images_unchanged':True,'text_matches_expected_sources':True}})
 manifest={'status':'review_draft','upload_ready':False,'paper':'undecided','trim_inches':[7,10],'bleed':False,'review_pages':len(plan),'interior_pages':len(plan)-1,'content_counts':dict(counts),'page_plan':plan,'sources':used,'builder':{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':checks.digest(Path(__file__))},'editions':editions,'visual_review':'pending','pending':['Comicpointen und Bastelvorlagen redaktionell prüfen','Rätsel und Lösungen fehlen; Umfang separat entscheiden','Native Auflösung und Monochromprüfung vor Druckfreigabe','Bastelvorlagen am Papier testen','Coverbanner und finale KDP-Umschlagdatei offen'],'baseline_note':'Existing v01-r02 PDF content preserved. Later changes to book-texts-v01.json are not silently substituted; reconcile during editorial revision.'}
 (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(f'Created {len(editions)} editions: {len(plan)-1} interior + cover = {len(plan)} PDF pages; source preservation checks passed.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT/'05-kdp/review/v02');run(p.parse_args().output_dir)
