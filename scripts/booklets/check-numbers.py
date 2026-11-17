"""Verify the visible slide numbers in both issued editions of every chapter."""
import json
from pathlib import Path
import pymupdf as pdf

ROOT = Path(__file__).resolve().parents[2]


def verify(path, count):
    with pdf.open(path) as document:
        if len(document) < (count + 1) // 2:
            raise ValueError(f'{path} is missing teaching panels')
        for number in range(1, count + 1):
            page = document[(number - 1) // 2]
            offset = 413.25 * ((number - 1) % 2)
            corner = pdf.Rect(548, offset + 8, 576, offset + 35)
            words = page.get_text('words', clip=corner)
            digits = [word for word in words if word[4].isdigit() and word[2] > 568]
            if {word[4] for word in digits} != {str(number)}:
                raise ValueError(f'{path}, panel {number}: wrong number')
            # A title banner can paint over an otherwise searchable number.
            pixels = page.get_pixmap(matrix=pdf.Matrix(2, 2), clip=pdf.Rect(digits[-1][:4])).samples
            if sum(min(pixels[i:i+3]) > 190 for i in range(0, len(pixels), 3)) < 12:
                raise ValueError(f'{path}, panel {number}: invisible number')


def main():
    catalogue = (ROOT / 'teaching-catalogue.js').read_text().split('=', 1)[1]
    books = json.loads(catalogue.strip().rstrip(';'))
    panels = 0
    for book in books.values():
        for chapter in book['chapters']:
            pupil = ROOT / chapter['booklet']
            deck = pupil.parent.parent / f"chapter-{chapter['number']:02}.json"
            count = len(json.loads(deck.read_text())['slides'])
            for path in (pupil, ROOT / chapter['solutions']):
                verify(path, count)
                panels += count
    print(f'Checked {panels} numbered teaching panels.')


if __name__ == '__main__':
    main()
