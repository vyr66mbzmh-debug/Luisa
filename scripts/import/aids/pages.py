"""Render question-paper or mark-scheme pages to PNG (and optionally OCR them with tesseract, as an aid only).

Usage: python3 -I scripts/import/aids/pages.py --set <set> <paperId> qp|ms [--ocr] [--dpi 200]
Images go to <state>/import/<set>/pages/<paperId>/<kind>/pNN.png (+ .txt with --ocr). Page images are authoritative;
OCR text is never imported without checking it against the image.
"""
import shutil
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import pymupdf  # noqa: E402

ap = common.parser(__doc__)
ap.add_argument('kind', choices=['qp', 'ms'])
ap.add_argument('--ocr', action='store_true')
ap.add_argument('--dpi', type=int, default=200)
args = ap.parse_args()
SET = common.ImportSet(args)
out = SET.work / 'pages' / args.paper / args.kind
out.mkdir(parents=True, exist_ok=True)
d = pymupdf.open(SET.pdf(args.paper, args.kind))
tesseract = shutil.which('tesseract')
if args.ocr and not tesseract:
    raise SystemExit('tesseract is not installed (optional aid): brew install tesseract')
for i, page in enumerate(d, 1):
    png = out / f'p{i:02d}.png'
    if not png.exists():
        page.get_pixmap(dpi=args.dpi, colorspace=pymupdf.csGRAY).save(png)
    if args.ocr and not png.with_suffix('.txt').exists():
        subprocess.run([tesseract, str(png), str(png.with_suffix('')), '--psm', '4'], capture_output=True, check=True)
print(args.paper, args.kind, len(d), 'pages rendered to the private work folder')
