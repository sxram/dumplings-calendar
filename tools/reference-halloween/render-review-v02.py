"""Render all editions and compact contact sheets for review v02."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'05-kdp/review/v02'
def run(lang):
 out=BASE/'render'/lang;out.mkdir(parents=True,exist_ok=True)
 subprocess.run([shutil.which('pdftoppm'),'-scale-to','700','-png',str(BASE/f'giggle-dumplings-halloween-{lang}-review-v02.pdf'),str(out/'page')],check=True)
 files=sorted(out.glob('page-*.png')); assert len(files)==111
 for offset in range(0,len(files),20):
  sheet=Image.new('RGB',(1500,1680),'#ddd');draw=ImageDraw.Draw(sheet)
  for i,p in enumerate(files[offset:offset+20]):
   with Image.open(p) as im:
    im.thumbnail((288,304));x=(i%5)*300+(300-im.width)//2;y=(i//5)*336+23;sheet.paste(im,(x,y))
   draw.text((i%5*300+8,i//5*336+5),f'{lang.upper()} PDF {offset+i+1}',fill='black')
  sheet.save(out/f'contact-{offset//20+1:02}.jpg',quality=90)
 print(lang,'111 pages rendered',flush=True)
with ThreadPoolExecutor(max_workers=3) as p:list(p.map(run,('de','en','es')))
