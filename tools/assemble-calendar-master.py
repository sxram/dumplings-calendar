"""Replace only the twelve lower pages in the existing complete calendar."""
import argparse
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--lower', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
registry = json.loads((ROOT / 'production/assets.json').read_text())
base_rel = 'giggle_dumplings_2027_complete_calendar_with_back-drafts.pdf'
base_path = ROOT / base_rel
assert hashlib.sha256(base_path.read_bytes()).hexdigest() == registry['assets'][base_rel]['sha256']
lower_path = ROOT / args.lower
assert hashlib.sha256(lower_path.read_bytes()).hexdigest() == registry['assets'][args.lower]['sha256']
out = (ROOT / args.output).resolve()
assert out.is_relative_to(ROOT)
out.parent.mkdir(parents=True, exist_ok=True)
assert not out.exists()
base = PdfReader(base_path)
lower = PdfReader(lower_path)
assert len(base.pages) == 26 and len(lower.pages) == 12
writer = PdfWriter()
pages = []
for index, page in enumerate(base.pages):
    replaced = index in range(2, 25, 2)
    month = index // 2 if replaced else None
    source_page = lower.pages[month-1] if replaced else page
    if replaced:
        assert len(page.extract_text()) > 20
        assert list(page.mediabox) == list(source_page.mediabox)
        from calendar import month_name
        assert month_name[month] in page.extract_text()
        assert month_name[month] in source_page.extract_text()
    writer.add_page(source_page)
    pages.append({'page': index+1, 'source': args.lower if replaced else base_rel,
                  'source_page': month if replaced else index+1,
                  'month': month, 'replaced': replaced,
                  'content_sha256': hashlib.sha256(source_page.get_contents().get_data()).hexdigest()})
writer.add_metadata({'/Title': 'Giggle Dumplings 2027 - ARBEITSMASTER v04',
                     '/Subject': 'Working master. Illustrations retained from existing complete draft. Not print ready.'})
with out.open('wb') as f:
    writer.write(f)
check = PdfReader(out)
assert len(check.pages) == 26
for page, record in zip(check.pages, pages):
    assert hashlib.sha256(page.get_contents().get_data()).hexdigest() == record['content_sha256']
manifest = {'status': 'working_master', 'design_review': 'user_pending', 'print_status': 'not_released',
            'sources': {base_rel: registry['assets'][base_rel]['sha256'],
                        args.lower: registry['assets'][args.lower]['sha256']},
            'issues': ['February corrected source absent locally; illustration unchanged from existing complete draft.',
                       'April and June tail corrections pending.',
                       'December approval cannot be independently mapped; existing complete draft illustration retained.',
                       'Imprint and Gelato product-specific print checks pending.'],
            'page_count': 26, 'preserved_pages': 14, 'replaced_lower_pages': 12, 'pages': pages}
out.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
print('26 pages: 12 lower pages replaced; 14 existing pages preserved with verified content hashes.')
