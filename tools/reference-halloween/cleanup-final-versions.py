"""Archive verified obsolete versions, then remove only exact inventoried files."""
from pathlib import Path
import json,hashlib,tarfile,argparse
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
rp=R/'production/assets.json';reg=json.loads(rp.read_text())
keep=['05-kdp/upload/interior-de-v11','05-kdp/upload/cover-de-v11']
targets=[]
for p in (R/'05-kdp/upload').iterdir():
 if p.is_dir() and str(p.relative_to(R)) not in keep:targets.append(p)
for p in (R/'05-kdp/review').iterdir():
 if p.is_dir() and p.name!='v08':targets.append(p)
for rel in ['05-kdp/production/de-v01','04-cover/drafts/back-de-v05','04-cover/drafts/back-de-v06','03-coloring-pages/drafts/crafts-de-v03','03-coloring-pages/drafts/bastelideen-v01','05-kdp/specials/drafts/pumpkin-card-v01','05-kdp/specials/drafts/puzzles-v01','05-kdp/specials/drafts/puzzles-v02','05-kdp/specials/drafts/puzzles-v03','05-kdp/specials/drafts/puzzles-v04','05-kdp/specials/drafts/mask-sunny-v01','05-kdp/specials/drafts/masks-v02']:
 p=R/rel
 if p.exists():targets.append(p)
# Rejected mouth-card only; retain other current craft sources.
for rel in ['03-coloring-pages/drafts/crafts-de-v04/03-kuerbiskarte-de.svg','03-coloring-pages/drafts/crafts-components-v04/pumpkin-pair.png']:
 p=R/rel
 if p.exists():targets.append(p)
files=[]
for target in targets:
 assert target.resolve().is_relative_to(R) and target!=R and not target.is_symlink()
 for p in ([target] if target.is_file() else sorted(target.rglob('*'))):
  if p.is_file():
   assert not p.is_symlink()
   files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
paths={f['path'] for f in files};assert len(paths)==len(files)
for sel in ['current_kdp_interior_de','current_kdp_cover_de','current_cover_front_de','current_cover_back_de']:
 a=reg['assets'][reg['selection'][sel]];assert a['path'] not in paths
 assert hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==a['sha256']
report={'files':files,'bytes':sum(f['bytes'] for f in files),'retired_assets':{k:a for k,a in reg['assets'].items() if a['path'] in paths},'retained':'Innenbuch v11, Cover v11, aktuelle Cover-SVGs, Review v08 als Produktionsbasis und verwendete Illustrationsquellen','note':'Historische Builder benötigen ggf. Quellen aus diesem Archiv; laufende endgültige PDFs sind eigenständig.'}
print(json.dumps({'files':len(files),'GiB':round(report['bytes']/1024**3,2),'directories':[str(p.relative_to(R)) for p in targets]},ensure_ascii=False),flush=True)
if not args.apply:raise SystemExit()
archive=R/'production/archive/obsolete-versions-20260930.tar.gz';archive.parent.mkdir(exist_ok=True)
assert not archive.exists()
with tarfile.open(archive,'w:gz',compresslevel=1) as tar:
 for f in files:tar.add(R/f['path'],arcname=f['path'],recursive=False)
print('Archiv erstellt; prüfe alle enthaltenen Dateien.',flush=True)
with tarfile.open(archive,'r:gz') as tar:
 assert {m.name for m in tar.getmembers()}==paths
 for f in files:
  stream=tar.extractfile(f['path']);h=hashlib.sha256()
  for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
  assert h.hexdigest()==f['sha256'],f['path']
report['archive']=str(archive.relative_to(R));report['archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
(R/'production/cleanup-final-20260930.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for f in files:
 p=R/f['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'];p.unlink()
for target in targets:
 if target.is_dir():
  for p in sorted(target.rglob('*'),key=lambda p:len(p.parts),reverse=True):
   if p.is_dir() and not any(p.iterdir()):p.rmdir()
  if not any(target.iterdir()):target.rmdir()
for k in report['retired_assets']:reg['assets'].pop(k)
reg['selection']={k:v for k,v in reg['selection'].items() if v in reg['assets']}
reg.setdefault('issues',{})['final_cleanup']='30.09.2026: veraltete Versionen archiviert und aus Arbeitsordnern entfernt; Wiederherstellung gemäß production/cleanup-final-20260930.json.'
rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print('Bereinigung abgeschlossen. Endgültige Dateien und ihre Prüfsummen erhalten.',flush=True)
