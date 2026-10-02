"""Render every review page and assemble numbered contact sheets for visual QA."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
from PIL import Image, ImageOps, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/(sys.argv[1] if len(sys.argv)>1 else '05-kdp/review/v01')
BIN='/Users/stefan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
def render(lang):
    out=BASE/'render'/lang
    out.mkdir(parents=True,exist_ok=True)
    subprocess.run([BIN,'-scale-to','900','-png',str(BASE/f'giggle-dumplings-halloween-{lang}-review-v01.pdf'),str(out/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    files=sorted(out.glob('page-*.png'))
    # Include every page, including blank backs, in review sheets.
    for offset in range(0,len(files),12):
        sheet=Image.new('RGB',(1440,1740),'#dedede')
        draw=ImageDraw.Draw(sheet)
        for i,p in enumerate(files[offset:offset+12]):
            im=Image.open(p).convert('RGB'); im.thumbnail((345,540))
            x=(i%4)*360+(360-im.width)//2; y=(i//4)*580+24
            sheet.paste(im,(x,y));draw.text((x,y-18),f'{lang.upper()} PDF {offset+i+1}',fill='black')
        sheet.save(out/f'contact-{offset//12+1:02}.jpg',quality=90)
    print(lang,len(files),'pages rendered',flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(render,['de','en','es']))
