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
assert len(src.pages) == len(dst.pages) == len(manifest['months']) == 12
with pdfplumber.open(outputs[0]) as pdf, pdfplumber.open(source) as original:
    for i, (a, b, record) in enumerate(zip(src.pages, dst.pages, manifest['months']), 1):
        assert list(a.mediabox) == list(b.mediabox)
        text = b.extract_text()
        assert record['title'] in text
        assert record['instruction'] in ' '.join(text.split())
        for box in [(0, 0, 492, 595), (492, 0, 841.8, 192), (492, 518, 841.8, 595)]:
            assert original.pages[i-1].crop(box).extract_text() == pdf.pages[i-1].crop(box).extract_text(), (i, 'retained text changed')
        # Calendar cells lie entirely to the left of the puzzle and story areas.
        words = [w for w in pdf.pages[i-1].extract_words()
                 if w['text'].isdigit() and w['x0'] < 482 and 100 < w['top'] < 370]
        found = {int(w['text']): w for w in words}
        assert len(found) == calendar.monthrange(2027, i)[1]
        for day, word in found.items():
            column = round((word['x0'] - 20) / (468 / 7))
            assert column == calendar.weekday(2027, i, day), (i, day, column)
        assert all(str(day) in text for day in found)
report = {'months': 12, 'calendar_year': 2027, 'weekday_positions': 'passed',
          'page_sizes': 'unchanged', 'source_sha256': 'passed',
          'titles_and_instructions': 'passed', 'user_review': 'pending',
          'story_jobs_challenges_facts_text': 'unchanged',
          'gelato_print_review': 'pending', 'note': 'Structure checks are not visual approval.'}
(folder / 'checks.json').write_text(json.dumps(report, indent=2) + '\n')
print('12 months: source, dimensions, titles, instructions and 365 weekday positions passed.')
