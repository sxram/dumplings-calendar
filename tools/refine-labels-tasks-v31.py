"""Restore illustrated names and set puzzle instructions without per-word stretching."""
import io,json,math,hashlib,copy
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[1];PW,PH=1492,1054
BASE='output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v30.pdf';COMP=ROOT/'production/labels-tasks/v31';COMP.mkdir(parents=True,exist_ok=True)
STAGE=ROOT/'tmp/pdfs/v31/candidate.pdf';STAGE.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('TaskUniform','/System/Library/Fonts/Supplemental/ChalkboardSE.ttc',subfontIndex=0))
TASKS={1:'Help Nibbles find the golden star! Use the footprints to find the right way through the snowy forest. There are many dead ends - can you make it to the star?',2:'Follow each path. Which mailbox gets each letter?',3:'What comes next? Complete the two patterns!',4:'Two eggs are exactly the same. Can you find them?',5:'Eight butterflies are hiding in the picture. Can you find them all?',6:'The strawberries are gone! Read the clues and find out who took them.',7:'Look carefully! Which shadow matches the sandcastle exactly?',8:'Match each woodland animal to its home.',9:'These two pictures look almost the same. Can you find all 6 differences?',10:'Find the 5 matching pairs. Which 2 pumpkins are left without a partner?',11:'What happened first? Put the 4 pictures in the correct order.',12:'One piece is missing. Which piece completes the star exactly?'}
REGIONS={1:(1193,394,1470,480),2:(1177,448,1443,539),3:(1118,453,1380,512),4:(1190,435,1449,516),5:(1157,397,1465,469),6:(899,725,1464,767),7:(875,742,1450,774),8:(887,679,1332,708),9:(902,686,1441,720),10:(1084,634,1432,690),11:(1227,644,1472,698),12:(1185,662,1471,728)}
TITLES={1:'Follow the Footprints!',2:'Special Delivery',3:'Seed Trail',4:'Find the Matching Eggs!',5:'Find the Butterflies!',6:'Who Took the Strawberries?',7:'Which Shadow Belongs to the Castle?',8:'Who Lives Here?',9:'Find the 6 Differences!',10:'Pumpkin Pairs',11:'Put the Storm Story in Order!',12:'Complete the Last Star!'}
TITLE_BOXES={1:(896,398,1188,451),2:(900,454,1147,495),3:(886,459,1097,502),4:(846,441,1179,489),5:(834,395,1150,453),6:(891,696,1465,730),7:(869,696,1464,741),8:(869,637,1280,681),9:(901,650,1210,687),10:(851,634,1079,690),11:(832,649,1214,684),12:(823,658,1180,720)}
CLUES=['Clue 1: Small footprints were found beside the basket.','Clue 2: Whoever took the strawberries did not have wings.','Clue 3: A turquoise circle was found beside the empty basket.']
BRANDS={m:((25,45,176,140) if m<6 else (17,44,163,141)) for m in range(1,12)}
BRANDS[12]=(169,85,313,182)
# November was not converted in v29: preserve the unchanged original brand as verified.
BRANDS.pop(11)

def in_region(x,y,b,pad=6):return b[0]-pad<=x<=b[2]+pad and b[1]-pad<=y<=b[3]+pad

def wrap(s,width,size):
 out=[];line=''
 for word in s.split():
  trial=(line+' '+word).strip()
  if line and pdfmetrics.stringWidth(trial,'TaskUniform',size)>width:out.append(line);line=word
  else:line=trial
 if line:out.append(line)
 return out

def paragraph(c,s,b,max_size=24):
 x,y,xx,yy=b;width=xx-x-8;height=yy-y-8;size=max_size
 while size>=13:
  ls=wrap(s,width,size);leading=size*1.13
  if len(ls)*leading<=height+4:break
  size-=.5
 assert size>=13,(s,b)
 c.setFillColor(HexColor('#173e59'));c.setFont('TaskUniform',size)
 for k,line in enumerate(ls):c.drawString(x+4,PH-(y+size+k*leading),line)
 return {'text':s,'font':'ChalkboardSE regular embedded','size':size,'leading':leading,'lines':ls,'box':b,'horizontal_stretch':False}

def image_clip(c,source,box,source_box=None):
 source_box=source_box or box;x,y,xx,yy=box;sx,sy,sxx,syy=source_box
 c.saveState();p=c.beginPath();p.rect(x,PH-yy,xx-x,yy-y);c.clipPath(p,fill=0,stroke=0)
 scale_x=(xx-x)/(sxx-sx);scale_y=(yy-y)/(syy-sy)
 c.drawImage(str(ROOT/source),x-sx*scale_x,PH-yy-(PH-syy)*scale_y,PW*scale_x,PH*scale_y)
 c.restoreState()

r=PdfReader(ROOT/BASE);w=PdfWriter(clone_from=r);review=PdfWriter();records=[]
for m in range(1,13):
 page=w.pages[2*m];cs=ContentStream(page.get_contents(),w);drop=set();removed=[]
 if m<=5:
  dates=[]
  for k,(aa,oo) in enumerate(cs.operations):
   if oo!=b'Tj' or not str(aa[0]).isdigit() or k<5:continue
   mm,oper=cs.operations[k-5]
   if oper==b'cm' and list(mm[:4])==[1,0,0,1] and 0<float(mm[4])<840 and 400<float(mm[5])<800:
    mm[4]=FloatObject(float(mm[4])-10);dates.append(int(str(aa[0])))
  import calendar
  assert dates==list(range(1,calendar.monthrange(2027,m)[1]+1))
 for i,(args,op) in enumerate(cs.operations):
  if op!=b'BT':continue
  j=i+1
  while j<len(cs.operations) and cs.operations[j][1]!=b'ET':j+=1
  tokens=[str(a[0]) for a,o in cs.operations[i:j] if o==b'Tj']
  if not tokens:continue
  mat=None
  for k in range(i-1,max(-1,i-5),-1):
   if cs.operations[k][1]==b'cm':mat=cs.operations[k][0];break
  if mat is None:continue
  x=float(mat[4]);y=PH-float(mat[5]);b=REGIONS[m]
  target=in_region(x,y,b)
  if m==6 and y<732:target=False
  if m==9 and y<690:target=False
  if m==6:target|=in_region(x,y,(1140,771,1462,914))
  if m in BRANDS:target|=in_region(x,y,BRANDS[m])
  if m==5:target|=in_region(x,y,(558,866,662,941),pad=0)
  if target:drop.update(range(i,j+1));removed.extend(tokens)
 cs.operations=[v for i,v in enumerate(cs.operations) if i not in drop];page.replace_contents(cs)
 mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(PW,PH));src=f'back-images-with-puzzles-v1/{m:02}.png' if m!=12 else 'back-images-with-puzzles-v1/12_not_correct.png'
 if m in BRANDS:image_clip(c,src,BRANDS[m])
 if m==5:image_clip(c,src,(558,866,662,941))
 if m==2:
  # Replace only surplus blank backing with nearby original village scenery, avoiding original task text.
  image_clip(c,src,(1177,501,1443,539),(1177,532,1443,570))
 b=REGIONS[m]
 if m==2:b=(1177,448,1443,501)
 layout=paragraph(c,TASKS[m],b);clues=[]
 if m==6:
  for k,t in enumerate(CLUES):clues.append(paragraph(c,t,(1142,772+k*48,1460,819+k*48),max_size=17))
 c.save();mem.seek(0);overlay=PdfReader(mem).pages[0];overlay.scale_to(float(page.mediabox.width),float(page.mediabox.height));page.merge_page(overlay);review.add_page(copy.deepcopy(page))
 records.append({'month':m,'task':layout,'title':{'text':TITLES[m],'status':'retained unchanged from v29'},'clues':clues,'restored_brand':BRANDS.get(m),'original_brand_unchanged':m==11,'restored_may_small_sign':m==5,'removed_text_tokens':removed,'visual_review':'pending','user_review':'pending'})
w.add_metadata({'/Title':'Giggle Dumplings 2027 - ARBEITSMASTER v31','/Subject':'Working master. January-May calendar inset, illustrated name signs restored, uniform puzzle task typography. Review pending; not print released.'})
with STAGE.open('wb') as f:w.write(f)
with (ROOT/'tmp/pdfs/v31/backs.pdf').open('wb') as f:review.write(f)
(COMP/'manifest.json').write_text(json.dumps({'base':BASE,'sources':'original back-images-with-puzzles-v1; December rejected source used only for unchanged illustrated sign, not puzzle or tracker','months':records,'changed_pages':[2*m+1 for m in range(1,13)],'visual_review':'pending','user_review':'pending','print_status':'not_released','image_generation_calls':0,'calendar_shift_from_v29_design_units':12,'calendar_date_count_shifted':151},indent=2)+'\n')
print('Twelve backs staged: original illustrated names, un-stretched task type, smaller February backing.')
