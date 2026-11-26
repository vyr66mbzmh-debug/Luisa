"""Write a private LaTeX reproduction of an accepted Resources booklet.

Run pdflatex on the resulting .tex file from its directory. The bundled PDF
keeps the approved vector type and drawings. Browser links are restored as
PDF annotations because embedding a page as artwork drops its annotations.
"""
import argparse
from pathlib import Path
import shutil

import pymupdf as pdf


def reproduce(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    assets = target.parent / "_assets"
    assets.mkdir(exist_ok=True)
    asset = assets / target.with_suffix(".pdf").name
    shutil.copyfile(source, asset)
    with pdf.open(source) as document:
        size = document[0].rect
        lines = [
            r"\documentclass{article}",
            rf"\usepackage[paperwidth={size.width}bp,paperheight={size.height}bp,margin=0pt]{{geometry}}",
            r"\pagestyle{empty}",
            r"\pdfhorigin=0pt\pdfvorigin=0pt",
            r"\pdfminorversion=7",
            r"\begin{document}",
        ]
        for number, page in enumerate(document, 1):
            if page.rect != size:
                raise ValueError(f"Inconsistent page size on page {number}")
            lines.append(rf'\pdfximage page {number} {{"_assets/{asset.name}"}}')
            lines.append(r"\shipout\vbox{\offinterlineskip%")
            for link in page.get_links():
                uri = link.get("uri", "")
                if not uri.startswith(("https://", "http://")):
                    continue
                rect = link["from"]
                # A PDF hex string also handles TeX and URI punctuation literally.
                address = uri.encode("utf-8").hex()
                lines.extend([
                    rf"\vbox to 0pt{{\kern{rect.y0:.4f}bp%",
                    rf"\hbox to 0pt{{\kern{rect.x0:.4f}bp%",
                    rf"\pdfannot width {rect.width:.4f}bp height 0bp depth {rect.height:.4f}bp",
                    rf"{{/Subtype/Link/Border[0 0 0]/A<</S/URI/URI<{address}>>>}}\hss}}\vss}}%",
                ])
            lines.append(r"\hbox{\pdfrefximage\pdflastximage}}")
        lines.append(r"\end{document}")
        target.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path, help="Destination .tex path")
    args = parser.parse_args()
    reproduce(args.source, args.target)
