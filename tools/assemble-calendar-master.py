"""Replace only the twelve lower pages in the existing complete calendar."""
import argparse
import hashlib
import json
import zlib
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--lower', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--base', default='giggle_dumplings_2027_complete_calendar_with_back-drafts.pdf')
parser.add_argument('--month-image', action='append', default=[], help='MONTH=registered/path.png')
args = parser.parse_args()
registry = json.loads((ROOT / 'production/assets.json').read_text())
base_rel = args.base
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
corrections = {}
for value in args.month_image:
    month, rel = value.split('=', 1)
    month = int(month)
    assert month in [2,4,6] and month not in corrections
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() == registry['assets'][rel]['sha256']
    corrections[month] = rel
assert len(base.pages) == 26 and len(lower.pages) == 12
writer = PdfWriter()
pages = []
for index, page in enumerate(base.pages):
    replaced = index in range(2, 25, 2)
    month = index // 2 if replaced else None
    source_page = lower.pages[month-1] if replaced else page
    image_month = (index+1)//2 if index in range(1,24,2) else None
    image_rel = corrections.get(image_month)
    if image_rel:
        objects = [v.get_object() for v in page['/Resources']['/XObject'].values()
                   if v.get_object().get('/Subtype') == '/Image']
        assert len(objects) == 1
        image = objects[0]
        with Image.open(ROOT/image_rel) as im:
            assert im.mode == 'RGB' and im.size == (int(image['/Width']),int(image['/Height']))
            image._data = zlib.compress(im.tobytes())
        image[NameObject('/Filter')] = NameObject('/FlateDecode')
        image[NameObject('/ColorSpace')] = NameObject('/DeviceRGB')
        image[NameObject('/BitsPerComponent')] = NumberObject(8)
        image.pop('/DecodeParms', None)
        image.pop('/SMask', None)
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
                  'corrected_image': image_rel,
                  'content_sha256': hashlib.sha256(source_page.get_contents().get_data()).hexdigest()})
writer.add_metadata({'/Title': out.stem,
                     '/Subject': 'Working master. February, April and June correction drafts; user and Gelato review pending.'})
with out.open('wb') as f:
    writer.write(f)
check = PdfReader(out)
assert len(check.pages) == 26
for page, record in zip(check.pages, pages):
    assert hashlib.sha256(page.get_contents().get_data()).hexdigest() == record['content_sha256']
    if record['corrected_image']:
        objects = [v.get_object() for v in page['/Resources']['/XObject'].values() if v.get_object().get('/Subtype') == '/Image']
        with Image.open(ROOT/record['corrected_image']) as im:
            assert objects[0].get_data() == im.tobytes()
manifest = {'status': 'working_master', 'design_review': 'user_pending', 'print_status': 'not_released',
            'sources': {base_rel: registry['assets'][base_rel]['sha256'],
                        args.lower: registry['assets'][args.lower]['sha256']},
            'corrected_images': corrections,
            'issues': ['Correction drafts and vector puzzle styling await user review.',
                       'Imprint and Gelato product-specific print checks pending.'],
            'page_count': 26, 'preserved_pages': 14-len(corrections), 'replaced_lower_pages': 12, 'corrected_upper_pages':len(corrections), 'pages': pages}
out.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
print(f'26 pages: 12 lower pages replaced; {len(corrections)} corrected images embedded with exact pixel verification; {14-len(corrections)} existing pages preserved.')
