"""Prepare existing 7x10 review pages at 8.5x11; not the final KDP manuscript."""
from pathlib import Path
import argparse
from pypdf import PdfReader, PdfWriter, Transformation
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
s=(ROOT/a.source).resolve();o=(ROOT/a.output).resolve()
assert s.is_relative_to(ROOT) and o.is_relative_to(ROOT) and not o.exists()
r=PdfReader(s);w=PdfWriter()
for page in r.pages:
    assert float(page.mediabox.width)==504 and float(page.mediabox.height)==720
    page.scale_by(1.1);page.mediabox.lower_left=(0,0);page.mediabox.upper_right=(612,792)
    page.add_transformation(Transformation().translate(28.8,0), expand=False);w.add_page(page)
w.add_metadata({'/Title':'Giggle Dumplings Halloween – 8.5x11 Format Preparation','/Subject':'Preparation artifact; not final KDP upload'})
o.parent.mkdir(parents=True,exist_ok=True)
with o.open('xb') as f:w.write(f)
print(f'{len(r.pages)} Seiten auf 612x792 pt vorbereitet; keine Inhaltsänderung.')
