"""Check preserved content, source hashes and real 2027 weekday positions."""
import argparse
import calendar
import hashlib
import json
from pathlib import Path
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('folder')
args = parser.parse_args()
folder = ROOT / args.folder
manifest = json.loads((folder / 'manifest.json').read_text())
source = ROOT / manifest['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['source_sha256']
outputs = list(folder.glob('*ARBEITSMASTER*.pdf'))
assert len(outputs) == 1
src = PdfReader(source)
dst = PdfReader(outputs[0])
recovered = manifest.get('source_layout') == 'recovered_26_page'
assert len(src.pages) == (26 if recovered else 12)
assert len(dst.pages) == len(manifest['months']) == 12
source_pages = [src.pages[2+i*2] for i in range(12)] if recovered else src.pages
with pdfplumber.open(outputs[0]) as pdf, pdfplumber.open(source) as original:
    for i, (a, b, record) in enumerate(zip(source_pages, dst.pages, manifest['months']), 1):
        assert list(a.mediabox) == list(b.mediabox)
        text = b.extract_text()
        assert record['title'] in text
        assert record['instruction'] in ' '.join(text.split())
        boxes = [(0, 50, 479, 595), (479, 0, 841.8, 180), (479, 505, 841.8, 595)] if recovered else [(0, 0, 492, 595), (492, 0, 841.8, 192), (492, 518, 841.8, 595)]
        op = original.pages[2+(i-1)*2] if recovered else original.pages[i-1]
        for box in boxes:
            assert op.crop(box).extract_text() == pdf.pages[i-1].crop(box).extract_text(), (i, 'retained text changed')
        if recovered:
            assert ''.join(op.crop((0,0,479,50)).extract_text().split()) == ''.join(pdf.pages[i-1].crop((0,0,479,50)).extract_text().split())
        # Calendar cells lie entirely to the left of the puzzle and story areas.
        words = [w for w in pdf.pages[i-1].extract_words()
                 if w['text'].isdigit() and w['x0'] < (469 if recovered else 482) and (90 if recovered else 100) < w['top'] < 370]
        found = {int(w['text']): w for w in words}
        assert len(found) == calendar.monthrange(2027, i)[1]
        for day, word in found.items():
            column = round((word['x0'] - (19 if recovered else 20)) / ((455 if recovered else 468) / 7))
            assert column == calendar.weekday(2027, i, day), (i, day, column)
        assert all(str(day) in text for day in found)
        if recovered:
            stars = [c for c in pdf.pages[i-1].curves if 50 < c['top'] < 80 and round(c['x0']) in [492+j*17 for j in range(12)]]
            stars.sort(key=lambda c:c['x0'])
            assert len(stars) == 12
            assert [c['non_stroking_color'] != (1.,1.,1.) for c in stars] == [j < i for j in range(12)], (i, 'tracker')
report = {'months': 12, 'calendar_year': 2027, 'weekday_positions': 'passed',
          'page_sizes': 'unchanged', 'source_sha256': 'passed',
          'titles_and_instructions': 'passed', 'user_review': 'pending',
          'story_jobs_challenges_facts_text': 'unchanged',
          'star_trackers': '1/12 through 12/12 passed' if recovered else 'not separately checked',
          'gelato_print_review': 'pending', 'note': 'Structure checks are not visual approval.'}
(folder / 'checks.json').write_text(json.dumps(report, indent=2) + '\n')
print('12 months: source, dimensions, titles, instructions and 365 weekday positions passed.')
