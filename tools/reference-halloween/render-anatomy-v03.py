from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05-kdp/review/v03'
PAGES=[10,16,26,30,34,40,44,46,52,62,68,78]
def run(lang):
 out=OUT/'render'/lang;out.mkdir(parents=True,exist_ok=True)
 for p in PAGES:
  subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-singlefile','-scale-to','1000','-png',str(OUT/f'giggle-dumplings-halloween-{lang}-review-v03.pdf'),str(out/f'page-{p:03}')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 for j in range(2):
  sh=Image.new('RGB',(1200,1680),'#ddd');d=ImageDraw.Draw(sh)
  for i,p in enumerate(PAGES[j*6:j*6+6]):
   im=Image.open(out/f'page-{p:03}.png');im.thumbnail((580,520));x=(i%2)*600+(600-im.width)//2;y=(i//2)*560+28;sh.paste(im,(x,y));d.text((x,y-20),f'{lang.upper()} Innenseite {p-1}',fill='black')
  sh.save(out/f'contact-{j+1}.jpg',quality=92)
 print(lang,'12 changed pages rendered',flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,('de','en','es')))
