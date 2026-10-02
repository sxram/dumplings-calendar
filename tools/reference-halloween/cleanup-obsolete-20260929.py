"""Conservative cleanup: only unchanged, Git-recoverable obsolete artifacts."""
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
r=json.loads((ROOT/'production/assets.json').read_text())
approved={a['path'] for a in r['assets'].values() if a['design_status']=='approved'}
selected={r['assets'][v]['path'] for k,v in r['selection'].items() if k!='current_puzzles_de'}
keep=approved|selected|{'05-kdp/review/v05/giggle-dumplings-halloween-de-review-v05.pdf','05-kdp/review/v06/giggle-dumplings-halloween-de-review-v06.pdf'}
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
dirty=set(subprocess.check_output(['git','diff','HEAD','--name-only','-z'],cwd=ROOT).decode().split('\0'))
targets=[];skipped=[]
for folder in ['05-kdp','production/reviews','raetsel/loesungen_schwarzweiss']:
 for p in (ROOT/folder).rglob('*'):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(ROOT).as_posix()
  obsolete=('render' in p.parts or '__pycache__' in p.parts
    or (rel.startswith('05-kdp/review/v') and p.suffix=='.pdf' and 'giggle-dumplings' in p.name and '/v08/' not in rel)
    or any(rel.startswith('05-kdp/specials/drafts/puzzles-v0'+str(i)+'/') for i in range(1,5))
    or rel.startswith('raetsel/loesungen_schwarzweiss/'))
  if not obsolete or rel in keep:continue
  if rel not in tracked or rel in dirty:skipped.append(rel);continue
  targets.append({'path':rel,'bytes':p.stat().st_size})
paths={a['path'] for a in targets}
removed={k:a for k,a in r['assets'].items() if a['path'] in paths}
missing='mask.pumpkin.svg.v02'
if missing in r['assets'] and not (ROOT/r['assets'][missing]['path']).exists():removed[missing]=r['assets'][missing]
report={'date':'2026-09-29','recovery_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'files':targets,'bytes':sum(x['bytes'] for x in targets),'retired_assets':removed,'skipped_untracked_or_modified':skipped,'note':'Deleted unchanged tracked files recoverable from recovery_commit. Existing missing mask v02 only retired from registry.'}
print(json.dumps({'files':len(targets),'GiB':round(report['bytes']/1024**3,2),'retired_assets':len(removed),'skipped':len(skipped)},ensure_ascii=False))
if not args.apply:raise SystemExit()
log=ROOT/'production/cleanup-20260929.json';assert not log.exists()
log.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for item in targets:
 p=ROOT/item['path'];assert p.resolve().is_relative_to(ROOT) and not p.is_symlink();p.unlink()
for key in removed:r['assets'].pop(key)
r['selection']={k:v for k,v in r['selection'].items() if v in r['assets']}
r['issues']['cleanup']='29.09.2026: obsolete PDFs, render images, superseded puzzle drafts and rejected monochrome solutions removed. Git recovery and retired registry entries: production/cleanup-20260929.json. Historical builders may require recovery of their version-specific inputs.'
r['updated']='2026-09-29'
(ROOT/'production/assets.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
