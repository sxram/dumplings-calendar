"""Registered components, standalone DE/EN/ES proof; no whole-book rebuild."""
import hashlib
import importlib.util
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'production/builds/imprint-review-v01'
spec = importlib.util.spec_from_file_location('checks', ROOT / 'tools/check-production-assets.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
registry = json.loads((ROOT / 'production/assets.json').read_text())
errors = checks.check(registry)
if errors:
    raise RuntimeError('\n'.join(errors))
if OUT.exists() and any(OUT.iterdir()):
    raise RuntimeError('Preserve existing proof; choose a new version.')
OUT.mkdir(parents=True, exist_ok=True)
mark_id = registry['selection']['publisher_mark']
mark = registry['assets'][mark_id]
text_id, text_asset = next((k, a) for k, a in registry['assets'].items()
                           if a['path'] == '01-concept/book-texts-v01.json')
texts = json.loads((ROOT / text_asset['path']).read_text())['ui']['imprint_note']
font_path = Path('/System/Library/Fonts/Supplemental/ChalkboardSE.ttc')
pdfmetrics.registerFont(TTFont('Imprint', str(font_path)))
pdf = OUT / 'impressum-halloween-de-en-es-v01.pdf'
c = canvas.Canvas(str(pdf), pagesize=(504, 720), invariant=1)
c.setTitle('Giggle Dumplings - Halloween Impressum / DE EN ES / Sichtentwurf')
c.setAuthor('Stefan Marx')
layout = {'page_pt': [504, 720], 'text_x': 42, 'first_baseline': 116,
          'font_pt': 9.5, 'leading_pt': 14, 'mark_box_pt': [386, 72, 32, 32]}
for lang in ('de', 'en', 'es'):
    lines = texts[lang].splitlines()
    assert len(lines) == 6
    c.setFillGray(0)
    c.setFont('Imprint', layout['font_pt'])
    for i, line in enumerate(lines):
        assert pdfmetrics.stringWidth(line, 'Imprint', 9.5) < 332, line
        c.drawString(42, 116 - i * 14, line)
    c.drawImage(str(ROOT / mark['path']), *layout['mark_box_pt'])
    c.showPage()
c.save()
reader = PdfReader(pdf)
assert len(reader.pages) == 3
for lang, page in zip(('de', 'en', 'es'), reader.pages):
    assert tuple(float(x) for x in page.mediabox[2:]) == (504, 720)
    extracted = page.extract_text()
    for line in texts[lang].splitlines():
        assert line in extracted, (lang, line)
manifest = {'status': 'review_draft', 'languages': ['de', 'en', 'es'],
            'operation': 'Reuse + layout/text; no image generation',
            'layout': layout, 'font': {'path': str(font_path), 'sha256': checks.digest(font_path)},
            'sources': {mark_id: mark, text_id: text_asset},
            'output': {'path': pdf.relative_to(ROOT).as_posix(), 'sha256': checks.digest(pdf)},
            'checks': {'page_count': 3, 'page_pt': [504, 720], 'all_text_present': True,
                       'publisher_mark_native_ppi': 360},
            'visual_review': 'pending', 'print_release': False,
            'whole_book_changed': False}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(pdf)
