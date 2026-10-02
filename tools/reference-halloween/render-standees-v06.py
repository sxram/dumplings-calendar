from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v06'
PAGES=[100,102,104]
def run(lang):
 out=OUT/'render'/lang;out.mkdir(parents=True,exist_ok=True)
 for p in PAGES:
  subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-singlefile','-scale-to','1600','-png',str(OUT/f'giggle-dumplings-halloween-{lang}-review-v06.pdf'),str(out/f'page-{p:03}')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 for j in range(0,3,2):
  sh=Image.new('RGB',(1600,1200),'#ddd');d=ImageDraw.Draw(sh)
  for i,p in enumerate(PAGES[j:j+2]):
   im=Image.open(out/f'page-{p:03}.png');im.thumbnail((780,1160));x=i*800+(800-im.width)//2;y=30;sh.paste(im,(x,y));d.text((x,y-20),f'{lang.upper()} Innenseite {p-1}',fill='black')
  sh.save(out/f'contact-{j//2+1}.jpg',quality=95)
 print(lang,'3 changed pages rendered',flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,('de','en','es')))
