"""Verify the visible slide numbers and title banners in both issued editions of every chapter."""
import json
from pathlib import Path
import pymupdf as pdf

ROOT = Path(__file__).resolve().parents[2]


def verify(path, count):
    with pdf.open(path) as document:
        sheets = (count + 1) // 2
        if len(document) != sheets:
            raise ValueError(f'{path} has {len(document)} A4 sheets for {count} slides, expected {sheets}')
        for number in range(1, count + 1):
            if number % 2:
                page = document[(number - 1) // 2]
                drawing = page.get_displaylist()
                words = page.get_text("words")
                text_page = page.get_textpage()
            offset = 413.25 * ((number - 1) % 2)
            corner = pdf.Rect(548, offset + 8, 576, offset + 35)
            digits = [word for word in words if word[4].isdigit() and word[2] > 568
                      and corner.contains(pdf.Rect(word[:4]))]
            if {word[4] for word in digits} != {str(number)}:
                raise ValueError(f'{path}, panel {number}: wrong number')
            # A title banner can paint over an otherwise searchable number.
            pixels = drawing.get_pixmap(matrix=pdf.Matrix(2, 2), clip=pdf.Rect(digits[-1][:4])).samples
            if sum(min(pixels[i:i+3]) > 190 for i in range(0, len(pixels), 3)) < 12:
                raise ValueError(f'{path}, panel {number}: invisible number')
            if number > 1:
                title = pdf.Rect(19, offset + 11, 490, offset + 33)
                title_text = page.get_textbox(title, textpage=text_page)
                if any(c in title_text for c in ("\x00", "\ufffd")):
                    raise ValueError(f'{path}, panel {number}: missing glyph in banner')
                pixmap = drawing.get_pixmap(clip=pdf.Rect(20, offset + 13, 485, offset + 32.75))
                background = pixmap.color_topusage()[1]
                if not any(max(abs(a - b) for a, b in zip(colour, background)) > 70
                           and count >= 2 for colour, count in pixmap.color_count(colors=True).items()):
                    raise ValueError(f'{path}, panel {number}: empty banner')


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
