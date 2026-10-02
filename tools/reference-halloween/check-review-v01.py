"""Read-only source checks; writes a new review report, never changes illustrations."""
import json, sys, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/(sys.argv[1] if len(sys.argv)>1 else '05-kdp/review/v01-r02')
manifest=json.loads((base/'build-manifest-v01.json').read_text())
rows=[]
for asset in manifest['assets']:
    p=ROOT/asset['path']; a=np.asarray(Image.open(p).convert('RGB'))
    color=(a[:,:,0]!=a[:,:,1])|(a[:,:,1]!=a[:,:,2])
    gray=(~color)&(a[:,:,0]>0)&(a[:,:,0]<255)
    rows.append({'path':asset['path'],'colored_pixels':int(color.sum()),'gray_pixels':int(gray.sum()),'total_pixels':int(color.size),'binary_bw':bool(not color.any() and not gray.any())})
blanks={}
for lang in ['de','en','es']:
    files=sorted((base/'render'/lang).glob('page-*.png'))
    blanks[lang]=[int(p.stem.split('-')[-1]) for p in files if Image.open(p).convert('RGB').getextrema()==((255,255),(255,255),(255,255))]
report={'status':'review-draft-not-print-approved','source_pixel_checks':rows,'rendered_blank_pages':blanks,'effective_dpi_min':min(p['effective_dpi'] for p in manifest['editions'][0]['placements']),'pdf_sha256':{e['language']:hashlib.sha256((base/e['file']).read_bytes()).hexdigest() for e in manifest['editions']}}
with (base/'source-and-render-checks.json').open('x') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print('Assets',len(rows),'binary BW',sum(r['binary_bw'] for r in rows),'minimum effective DPI',report['effective_dpi_min'])
print('Blank rendered pages', {k:len(v) for k,v in blanks.items()})
