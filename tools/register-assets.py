"""Explicitly add new local assets; never refresh a recorded checksum silently."""
import argparse
import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('checker', ROOT / 'tools/check-production-assets.py')
checker = module_from_spec(spec)
spec.loader.exec_module(checker)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--add-new', action='store_true', required=True)
    args = parser.parse_args()
    register = ROOT / 'production/assets.json'
    data = json.loads(register.read_text())
    recorded = {a['path'] for a in data['assets'].values()}
    count = 0
    for rel in sorted(checker.inventory() - recorded):
        p = ROOT / rel
        folder = Path(rel).parts[0]
        reference = folder in {'characters', 'drafts'}
        usage = {'characters': 'Figuren- und Stilreferenz', 'calender-images-v0': 'Monatsillustration: lokale Ausgangsfassung',
                 'back-images-with-puzzles-v1': 'Bestehender unterer Seitenentwurf mit Rasterrätsel',
                 'drafts': 'Historischer Entwurf; keine automatische Produktionsauswahl',
                 'publisher_mark': 'Publisher-Zeichen; Freigabe nicht lokal belegt'}.get(folder, 'Bestehender Kalender-Arbeitsstand')
        issues = ['Nutzerfreigabe und technische Gelato-Druckprüfung nicht belegt']
        if p.name == '12_not_correct.png':
            issues.append('Dateiname kennzeichnet Dezember ausdrücklich als nicht korrekt; gesperrt')
        a = {'path': rel, 'sha256': checker.digest(p), 'role': 'reference' if reference else 'source',
             'usage': usage, 'design_status': 'rejected' if p.name == '12_not_correct.png' else ('reference_only' if reference else 'review_pending'),
             'print_status': 'not_released', 'issues': issues,
             'origin': {'project': 'dumplings-calendar', 'note': 'Vorhandener lokaler Bestand; historische Freigabe nicht automatisch übernommen'}}
        if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
            from PIL import Image
            with Image.open(p) as im:
                a['pixels'] = list(im.size)
                a['color_mode'] = im.mode
        if p.suffix.lower() == '.pdf':
            from pypdf import PdfReader
            r = PdfReader(p)
            a['page_count'] = len(r.pages)
            a['page_sizes_pt'] = sorted({tuple(round(float(v), 3) for v in page.mediabox) for page in r.pages})
        data['assets'][rel] = a
        count += 1
    register.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(f'{count} neue Assets registriert; bestehende Einträge unverändert.')

if __name__ == '__main__':
    main()
