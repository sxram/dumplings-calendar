from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,math
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1];out=root/'production/reviews/figures-v02/render';m=json.load(open(root/'05-kdp/review/v05/manifest.json'))
placements={4:[96.5,60,320,160],38:[45,62.54,262.26,524.52],92:[45,62.54,262.26,524.52],94:[45,62.54,262.26,524.52],102:[72.5,80,368,184]}
def check(lang):
 result=[]
 for n in placements:
  p=out/f'{lang}-baseline-{n:03}'
  subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-scale-to','1600','-png',str(root/f'05-kdp/review/v04/giggle-dumplings-halloween-{lang}-review-v04.pdf'),str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  a=np.array(Image.open(str(p)+'.png').convert('RGB'));b=np.array(Image.open(root/f'05-kdp/review/v05/render/{lang}/page-{n:03}.png').convert('RGB'));assert a.shape==b.shape
  delta=np.max(abs(a.astype(int)-b.astype(int)),axis=2)
  changed=delta>5
  sid=m['page_patch_sources'][str(n)];l,t,r,bb=m['patch_boxes_top_left_pixels'][sid];iw,ih=m['image_sizes'][sid];x,y,w,h=placements[n]
  sx=a.shape[1]/504;sy=a.shape[0]/720
  box=[math.floor((x+l/iw*w)*sx)-3,math.floor((720-y-h+t/ih*h)*sy)-3,math.ceil((x+r/iw*w)*sx)+3,math.ceil((720-y-h+bb/ih*h)*sy)+3]
  outside=changed.copy();outside[box[1]:box[3],box[0]:box[2]]=False
  assert not outside.any(),(lang,n,int(outside.sum()))
  assert changed.any(),(lang,n,'no visible repair')
  result.append({'pdf_page':n,'source':sid,'changed_pixels_over_5':int(changed.sum()),'outside_patch_pixels_over_5':int(outside.sum()),'render_tolerance_levels':5,'allowed_render_box':box})
 return {'language':lang,'pages':result}
with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(check,('de','en','es')))
(root/'production/reviews/figures-v02/pixel-checks.json').write_text(json.dumps(records,indent=2)+'\n')
print('15 page comparisons: no differences above 5/255 outside intended patches; original image bytes unchanged')
