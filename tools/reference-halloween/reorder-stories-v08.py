import json,importlib.util,copy,sys
sys.dont_write_bytecode=True
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import TextStringObject
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v08';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('checks',ROOT/'tools/check-production-assets.py');ch=importlib.util.module_from_spec(spec);spec.loader.exec_module(ch)
r=json.loads((ROOT/'production/assets.json').read_text());assert not ch.check(r)
oldm=json.loads((ROOT/'05-kdp/review/v07/manifest.json').read_text());oldplan=oldm['page_plan']
s=importlib.util.spec_from_file_location('assembly',ROOT/'tools/assemble-review-v02.py');assembly=importlib.util.module_from_spec(s);s.loader.exec_module(assembly)
assert not any(OUT.iterdir()), 'Output directory must be empty'
order=list(range(7));colors=0
for i in range(7,len(oldplan),2):
    p=oldplan[i];assert oldplan[i+1]['kind']=='blank'
    if p['kind']=='comic':continue
    order.extend((i,i+1))
    if p['kind']=='coloring':
        colors+=1
        if colors%5==0:
            j=next(j for j,q in enumerate(oldplan) if q.get('id')==f'C0{colors//5}')
            order.extend((j,j+1))
assert len(order)==111 and len(set(order))==111
newplan=[]
for n,i in enumerate(order):
    p=copy.deepcopy(oldplan[i]);p['pdf_page']=n+1
    if n==0: p['interior_page']=None;p.pop('side',None)
    else: p['interior_page']=n;p['side']='recto' if n%2 else 'verso'
    newplan.append(p)
assert len({p['id'] for p in newplan if p['kind']=='coloring'})==colors==30
for i in range(7,len(newplan),2):
    assert newplan[i]['side']=='recto' and newplan[i+1]['kind']=='blank'
editions=[]
for lang in ('de','en','es'):
    src=PdfReader(ROOT/f'05-kdp/review/v07/giggle-dumplings-halloween-{lang}-review-v07.pdf');w=PdfWriter()
    for newi,oldi in enumerate(order):
        page=w.add_page(src.pages[oldi]);oldp=oldplan[oldi];newp=newplan[newi]
        if oldp['kind'] not in ('cover','blank','front') and oldp['interior_page']!=newp['interior_page']:
            assembly.footer_update(page,oldp['interior_page'],newp['interior_page'])
    dest=OUT/f'giggle-dumplings-halloween-{lang}-review-v08.pdf'
    w.add_metadata({'/Title':f'Giggle Dumplings Halloween {lang.upper()} - v08','/Subject':'Geschichten verteilt; Sichtfassung ohne Druckfreigabe'})
    with dest.open('xb') as f:w.write(f)
    out=PdfReader(dest);assert len(out.pages)==111
    for i,p in enumerate(out.pages):
        assert tuple(map(float,p.mediabox))==(0,0,504,720)
        expected=w.pages[i]
        def ops(pg):
            def norm(v):
                if isinstance(v,float):return round(v,5)
                if isinstance(v,(list,tuple)):return [norm(x) for x in v]
                return v
            c=pg.get_contents();return norm(c.operations) if c else []
        if ops(expected)!=ops(p):
            print('DIFF',[(a,b) for a,b in zip(ops(expected),ops(p)) if a!=b][:2],flush=True)
        assert ops(expected)==ops(p), (lang,i+1)
        assert assembly.assets(src.pages[order[i]])==assembly.assets(p)
        if newplan[i]['kind']=='blank':assert assembly.blank(p)
    editions.append({'language':lang,'path':str(dest.relative_to(ROOT)),'sha256':ch.digest(dest)})
    print(lang,'reordered; 111 pages and footer numbers checked')
manifest={'status':'review_draft','upload_ready':False,'interior_pages':110,'review_pages':111,'page_plan':newplan,'sources':{'baseline':'book.review.v07','builder':'tools/reorder-stories-v08.py'},'story_placement':'C01-C06 after coloring 05,10,15,20,25,30','checks':{'coloring_unique':30,'blank_backs_preserved':True,'page_count':111,'content_reordered_only':True},'visual_review':'pending','physical_paper_test':'open','print_release':False}
manifest['editions']=editions
manifest['source_page_order']=[i+1 for i in order]
manifest['checks']['recto_parity']=True
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
