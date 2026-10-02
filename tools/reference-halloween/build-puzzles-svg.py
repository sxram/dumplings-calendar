"""Editable German puzzle drafts; registry-backed source, no PDFs."""
import base64, hashlib, json, random, html, argparse
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',default='05-kdp/specials/drafts/puzzles-v04');args=p.parse_args()
OUT=ROOT/args.output;OUT.mkdir(parents=True,exist_ok=False)
r=json.loads((ROOT/'production/assets.json').read_text());sid='02-characters.reference-images.01-character-reference-v02-accessories';a=r['assets'][sid];src=ROOT/a['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==a['sha256']
data=base64.b64encode(src.read_bytes()).decode()
boxes=[(2,285,354,400),(357,325,295,360),(655,212,393,468),(1050,330,295,360),(1320,335,395,360)]
names=['Sunny','Mochi','Bao','Nibbles','Dreamy']
def char(i,x,y,w=110,h=120,flip=False):
 bx,by,bw,bh=boxes[i]
 clip=f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}"/>'
 if i==3:clip='<polygon points="1050,330 1344,330 1344,565 1318,600 1318,695 1050,695"/>'
 if i==4:clip='<polygon points="1400,335 1717,335 1717,695 1320,695 1320,630 1350,570 1370,530 1390,430"/>'
 inner=f'<svg x="0" y="0" width="{w}" height="{h}" viewBox="{bx} {by} {bw} {bh}" preserveAspectRatio="xMidYMid meet"><defs><clipPath id="clip-{i}-{x}-{y}-{flip}">{clip}</clipPath></defs><g clip-path="url(#clip-{i}-{x}-{y}-{flip})"><use href="#reference"/></g></svg>'
 return f'<g transform="translate({x+w if flip else x},{y}) scale({-1 if flip else 1},1)">{inner}</g>'
def text(x,y,t,size=17,anchor='start'):
 return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{html.escape(t)}</text>'
def line(x,y,xx,yy,extra=''):
 return f'<path d="M{x} {y} L{xx} {yy}" fill="none" stroke="black" stroke-width="2.5" {extra}/>'
def rect(x,y,w,h):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" stroke="black" stroke-width="2"/>'
shapes={
'pumpkin':'<path d="M45 25 Q36 7 53 7 L57 26 Z"/><path d="M50 25 C4 5 0 83 30 87 Q50 99 71 87 C101 82 99 6 50 25Z"/><path d="M37 32 Q22 57 37 81 M62 32 Q78 57 62 81" fill="none"/><path d="M26 48 L36 39 L42 51Z M59 51 L65 39 L76 48Z"/><path d="M34 65 Q50 79 67 65" fill="none"/>',
'ghost':'<path d="M18 88 V42 C18 0 82 0 82 42 V88 Q72 72 61 88 Q50 73 39 88 Q28 73 18 88Z"/><ellipse cx="38" cy="42" rx="4" ry="7" fill="black"/><ellipse cx="62" cy="42" rx="4" ry="7" fill="black"/><path d="M40 61 Q50 70 61 60" fill="none"/>',
'hat':'<path d="M22 72 L48 8 L73 72Z"/><ellipse cx="49" cy="77" rx="44" ry="12"/><path d="M29 58 L66 58" fill="none"/>',
'bat':'<path d="M7 30 Q28 51 41 32 L43 19 L51 29 L59 19 L61 32 Q75 51 94 30 L86 70 Q73 54 63 76 Q51 61 39 76 Q25 55 14 70Z"/><circle cx="46" cy="43" r="2" fill="black"/><circle cx="57" cy="43" r="2" fill="black"/>',
'star':'<path d="M50 5 L63 35 L96 39 L71 61 L78 94 L50 77 L22 94 L29 61 L4 39 L37 35Z"/>',
'candy':'<path d="M24 40 L7 28 V75 L25 63 M76 40 L93 28 V75 L75 63Z"/><rect x="24" y="32" width="52" height="40" rx="13"/><path d="M42 34 L34 69 M64 34 L54 70" fill="none"/>'}
def icon(k,x,y,s=60,shadow=False,flip=False):
 body=shapes[k]
 if shadow:
  # Exterior geometry only: exact same outline as the corresponding object.
  if k=='hat':body=body.split('<path d="M29')[0]
  elif k in ['ghost','bat','star']:body=body.split('/>')[0]+'/>'
  elif k=='pumpkin':body='/>' .join(body.split('/>')[:2])+'/>'
 return f'<g transform="translate({x+s if flip else x},{y}) scale({-s/100 if flip else s/100},{s/100})" fill="{"black" if shadow else "white"}" stroke="black" stroke-width="3.5" stroke-linejoin="round">{body}</g>'
def base(n,title,instructions,body,solution=False):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="7in" height="10in" viewBox="0 0 504 720"><defs><image id="reference" width="1717" height="916" href="data:image/png;base64,{data}"/></defs><rect width="504" height="720" fill="white"/><g font-family="Arial, sans-serif" fill="black">{text(36,38,'HALLOWEEN • '+('LÖSUNG ' if solution else 'RÄTSEL ')+str(n).zfill(2),11)}{text(36,73,title,23)}{''.join(text(36,105+j*23,t,15) for j,t in enumerate(instructions))}{body}{text(36,691,'Giggle Dumplings · Deutscher Entwurf v04',10)}{text(468,691,('L' if solution else 'R')+str(n).zfill(2),10,'end')}</g></svg>'''
records=[]
def save(n,title,inst,body,sol,answer):
 for suffix,b,flag in [('raetsel',body,False),('loesung',sol,True)]:
  f=OUT/f'{n:02}-{suffix}-de-v04.svg';f.write_text(base(n,title,inst,b,flag));ET.parse(f)
 records.append({'id':f'R{n:02}','title':title,'instructions':inst,'answer':answer})
def maze(n,cols,rows,seed,host,target):
 rng=random.Random(seed);seen={(0,0)};stack=[(0,0)];edges=set();parent={}
 while stack:
  u=stack[-1];v=[(u[0]+dx,u[1]+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)] if 0<=u[0]+dx<cols and 0<=u[1]+dy<rows and (u[0]+dx,u[1]+dy) not in seen]
  if not v:stack.pop();continue
  z=rng.choice(v);edges.add(frozenset([u,z]));seen.add(z);parent[z]=u;stack.append(z)
 assert len(seen)==cols*rows and len(edges)==cols*rows-1
 path=[(cols-1,rows-1)]
 while path[-1]!=(0,0):path.append(parent[path[-1]])
 path.reverse();cell=408/cols;x0=48;y0=240
 body=char(host,46,143,90,85)+icon(target,367,151,72)+text(145,199,'START → ZIEL',14)
 for y in range(rows):
  for x in range(cols):
   X=x0+x*cell;Y=y0+y*cell
   if y==0:body+=line(X,Y,X+cell,Y)
   if x==0 and y!=0:body+=line(X,Y,X,Y+cell)
   if x==cols-1:
    if y!=rows-1:body+=line(X+cell,Y,X+cell,Y+cell)
   elif frozenset([(x,y),(x+1,y)]) not in edges:body+=line(X+cell,Y,X+cell,Y+cell)
   if y==rows-1 or frozenset([(x,y),(x,y+1)]) not in edges:body+=line(X,Y+cell,X+cell,Y+cell)
 pts=[(x0-15,y0+cell/2)]+[(x0+(x+.5)*cell,y0+(y+.5)*cell) for x,y in path]+[(x0+cols*cell+15,y0+(rows-.5)*cell)]
 route=f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="black" stroke-width="3" stroke-dasharray="5 4"/>'
 save(n,['Sunnys Kürbisweg','Dreamys Geisterpfad'][n-1],['Finde den Weg vom linken Eingang zum rechten Ausgang.','Bleibe zwischen den Linien.'],body,body+route,{'route_cells':path,'grid':[cols,rows],'unique':True})
maze(1,8,8,23,0,'pumpkin');maze(2,11,11,61,4,'ghost')
def scene(y,host,second=False,variant=0,marked=False):
 b=rect(36,y,432,224)+char(host,62,y+76,116,132)+char(2 if host==1 else 3,282,y+76,112,132)
 # Five independent locations, no changes to the characters.
 changes=[(76,18,'star','bat'),(197,15,'ghost','hat'),(337,16,'bat','star'),(181,133,'pumpkin','ghost'),(410,155,'candy','hat')]
 for j,(x,dy,k,q) in enumerate(changes):
  k,q=(k,q) if variant==0 else (q,k)
  b+=icon(q if second else k,x,y+dy,47)
  if marked:b+=f'<circle cx="{x+24}" cy="{y+dy+24}" r="29" fill="none" stroke="black" stroke-width="1.5" stroke-dasharray="4 3"/>'+text(x+48,y+dy+5,str(j+1),12)
 return b
for n,host,title in [(3,1,'Mochis Halloweenfest'),(4,0,'Sunnys Spukbesuch')]:
 b=scene(165,host,variant=n-3)+scene(416,host,True,n-3)
 s=scene(165,host,variant=n-3)+scene(416,host,True,n-3,True)
 save(n,title,['Im unteren Bild haben sich 5 Dinge verändert.','Finde sie und kreise sie ein.'],b,s,{'differences':['oben links','oben Mitte','oben rechts','unten Mitte','unten rechts'],'count':5})
# Shadows: each exterior is matched exactly; four distinct silhouettes.
keys=['pumpkin','ghost','hat','bat'];perm=[2,0,3,1]
b=char(3,364,139, ninety:=90,100)+text(40,202,'Nibbles sucht die passenden Schatten.',15)
for i,k in enumerate(keys):b+=icon(k,55+i*109,270,65)+text(88+i*109,362,str(i+1),18,'middle')
for j,k in enumerate(perm):b+=icon(keys[k],55+j*109,457,65,True)+text(88+j*109,550,'ABCD'[j],18,'middle')
ans=[f'{i+1}–{"ABCD"[perm.index(i)]}' for i in range(4)]
s=b+text(252,622,' · '.join(ans),20,'middle')
save(5,'Schatten im Spukschloss',['Welcher Schatten gehört zu welchem Bild?','Verbinde jede Zahl mit dem passenden Buchstaben.'],b,s,ans)
# Matching pairs with visually identical character-plus-prop cards.
perm=[3,0,4,1,2];b=''
for side in range(2):
 for row in range(5):
  i=row if side==0 else perm[row];x=45 if side==0 else 315;y=151+row*101
  b+=rect(x,y,145,90)+char(i,x+8,y+5,70,77)+icon(keys[i%4],x+84,y+24,43)+text(x+(-12 if side==0 else 158),y+52,str(row+1) if side==0 else 'ABCDE'[row],16,'middle')
s=b
for i in range(5):s+=line(195,196+i*101,309,196+perm.index(i)*101,'stroke-dasharray="4 3"')
save(6,'Wer gehört zusammen?',['Finde jedes Bild auf der rechten Seite wieder.','Verbinde die gleichen Bilder.'],b,s,[f'{i+1}–{"ABCDE"[perm.index(i)]}' for i in range(5)])
# Sudoku count by independent backtracking.
grid=[[1,0,0,4],[0,4,1,0],[2,0,4,0],[0,3,0,1]]
def solve(g):
 empty=next(((r,c) for r in range(4) for c in range(4) if not g[r][c]),None)
 if empty is None:return [[row[:] for row in g]]
 r,c=empty;out=[]
 for v in range(1,5):
  if v in g[r] or any(g[z][c]==v for z in range(4)) or any(g[rr][cc]==v for rr in range(r//2*2,r//2*2+2) for cc in range(c//2*2,c//2*2+2)):continue
  g[r][c]=v;out+=solve(g);g[r][c]=0
 return out
solutions=solve([x[:] for x in grid]);assert len(solutions)==1
b=char(2,362,155, ninety,100)
for i,k in enumerate(keys):b+=icon(k,44+i*73,169,48)
b+=text(36,264,'Zeichne die fehlenden Bilder in die leeren Felder.',14)
def board(g):
 z=''
 for i in range(5):
  w=4 if i%2==0 else 1.3
  z+=f'<path d="M{72+i*90} 291 V651 M72 {291+i*90} H432" fill="none" stroke="black" stroke-width="{w}"/>'
 for row in range(4):
  for col in range(4):
   if g[row][col]:z+=icon(keys[g[row][col]-1],87+col*90,306+row*90,60)
 return z
save(7,'Baos Bilder-Sudoku',['Jedes Bild kommt genau einmal in jeder Zeile,','jeder Spalte und jedem dicken Vierer-Kasten vor.'],b+board(grid),b+board(solutions[0]),{'givens':grid,'solution':solutions[0],'symbol_order':keys,'solution_count':1})
# Four independent horizontal reflection questions; altered prop distinguishes distractor.
b='';answers=[]
for row,i in enumerate([0,1,2,4]):
 y=161+row*120;correct=row%2==0;answers.append(f'{row+1}–'+('A' if correct else 'B'))
 b+=text(37,y+48,str(row+1),16)+char(i,56,y,76,90)+icon('pumpkin',131,y+49,31)+line(180,y-5,180,y+96,'stroke-dasharray="5 4"')
 for j in range(2):
  x=218+j*127;ok=(j==0)==correct
  b+=rect(x-9,y-9,111,106)+char(i,x+24,y,76,90,ok)+icon('pumpkin',x-6,y+49,31,flip=ok)+text(x+44,y+111,'AB'[j],13,'middle')
s=b
for row,ans in enumerate(answers):s+=f'<ellipse cx="{262+(0 if ans.endswith("A") else 127)}" cy="{272+row*120}" rx="16" ry="10" fill="none" stroke="black"/>'
save(8,'Blick in den Zauberspiegel',['Die gestrichelte Linie ist der Spiegel.','Welches Bild passt rechts dazu? Kreise A oder B ein.'],b,s,answers)
manifest={'version':'v04','language':'de','format_inches':[7,10],'status':'draft','source':{'id':sid,'path':a['path'],'sha256':a['sha256']},'character_viewboxes':dict(zip(names,boxes)),'layer_order':['white background','text','clipped unchanged character source','SVG objects and geometry','solution annotations'],'puzzles':records,'visual_review':'pending','user_approval':'open','print_release':False,'book_integration':'open','checks':{'maze_unique_paths':True,'sudoku_unique_solution':True,'difference_count_each':5,'svg_count':16}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
links=''.join(f'<article><h2>{z["id"]} · {z["title"]}</h2><div><img src="{i:02}-raetsel-de-v04.svg" alt="Rätsel {i}"><details><summary>Lösung anzeigen</summary><img src="{i:02}-loesung-de-v04.svg" alt="Lösung {i}"></details></div></article>' for i,z in enumerate(records,1))
(OUT/'index.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><title>Halloween-Rätsel · Entwurf v04</title><style>body{font:17px Arial;background:#eee;margin:30px auto;max-width:1000px}h1,h2,p{margin-left:20px}article{margin:35px 0}article>div{display:flex;gap:16px;align-items:flex-start}img{width:470px;max-width:100%;background:white}details{width:480px}summary{padding:12px;cursor:pointer}</style><h1>Acht Halloween-Rätsel</h1><p>Deutsche editierbare SVG-Entwürfe · Lösungen aufklappen · keine Druckfreigabe</p>'+links+'</html>')
print('8 puzzles + 8 solutions; both mazes are trees; Sudoku uniquely solvable.')
