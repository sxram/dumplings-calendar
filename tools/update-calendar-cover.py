"""Versioned PDF cover text overlay; preserve all 24 interior pages."""
import io, json, hashlib
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v07.pdf'
target = ROOT / 'output/pdf/giggle-dumplings-2027-ARBEITSMASTER-v08.pdf'
assert not target.exists()
registry = json.loads((ROOT / 'production/assets.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest() == registry['assets'][str(source.relative_to(ROOT))]['sha256']
r = PdfReader(source)
assert len(r.pages) == 26
w, h = map(float, (r.pages[0].mediabox.width, r.pages[0].mediabox.height))
buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=(w, h))
# Cover the complete old raster sticker with a new vector panel.
c.setFillColor(HexColor('#fff7df'))
c.setStrokeColor(HexColor('#e8a343'))
c.setLineWidth(1.5)
c.roundRect(633, 357, 168, 126, 36, fill=1, stroke=1)
c.setFillColor(HexColor('#293c48'))
for text, y, size in [('One story', 457, 17), ('12 chapters', 432, 16), ('12 puzzles', 408, 16), ('Activities', 384, 16)]:
    c.setFont('Helvetica-Bold', size)
    c.drawCentredString(717, y, text)
c.showPage()
c.setFillColor(HexColor('#eaf7fc'))
c.rect(0, 0, w, h, fill=1, stroke=0)
c.setFillColor(HexColor('#173f73'))
for text, y, size, font in [
    ('Giggle Dumplings', 368, 34, 'Helvetica-Bold'),
    ('A Year of Adventures - 2027', 330, 21, 'Helvetica-Bold'),
    ('One magical story. Twelve monthly adventures.', 277, 17, 'Helvetica-Bold'),
    ('Follow the Dumplings through a year of stories, puzzles and activities.', 247, 12, 'Helvetica'),
    ('12 stars. 12 chapters. One magical year.', 216, 12, 'Helvetica'),
]:
    c.setFont(font, size)
    c.drawCentredString(w / 2, y, text)
c.setStrokeColor(HexColor('#acc9db'))
c.setLineWidth(0.6)
c.line(48, 145, w - 48, 145)
lines = ['© 2026 Stefan Marx', 'Giggle Home',
         'Giggle Dumplings - A Year of Adventures - 2027',
         'Publisher: Stefan Marx', 'Friedrichsberger Str. 5, 10243 Berlin',
         '1st edition · 2026']
c.setFont('Helvetica', 9)
for n, line in enumerate(lines):
    c.drawString(48, 126 - n * 14, line)
c.save()
overlays = PdfReader(buf)
r.pages[0].merge_page(overlays.pages[0])
writer = PdfWriter()
for i, page in enumerate(r.pages):
    writer.add_page(overlays.pages[1] if i == 25 else page)
writer.add_metadata({'/Title': 'Giggle Dumplings 2027 - Arbeitsmaster v08'})
writer.write(target)
new = PdfReader(target)
assert len(new.pages) == 26
for i in range(1, 25):
    assert new.pages[i].get_contents().get_data() == r.pages[i].get_contents().get_data()
assert 'One story' in new.pages[0].extract_text()
assert 'Publisher: Stefan Marx' in new.pages[-1].extract_text()
manifest = {'source': str(source.relative_to(ROOT)), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'output': str(target.relative_to(ROOT)), 'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'changed_pages': [1, 26], 'interior_content_streams_unchanged': True,
            'method': 'Vector badge overlays old raster badge; back page rebuilt as native text.',
            'review': 'pending', 'print_release': False}
target.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(target)
