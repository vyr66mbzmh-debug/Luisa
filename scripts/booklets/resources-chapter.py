from pathlib import Path
from playwright.sync_api import sync_playwright
import pymupdf as pdf
import json
from argparse import ArgumentParser
import os

parser = ArgumentParser(
    description="Export an FM1 or FS1 Resources chapter as paired two-up A4 handouts."
)
parser.add_argument("book", choices=["further-mechanics-1", "further-statistics-1"])
parser.add_argument("chapter", type=int)
parser.add_argument(
    "output",
    type=Path,
    help="Staging folder for both editions and the individual panels",
)
parser.add_argument("--base-url", required=True, help="Root of the served checkout")
parser.add_argument(
    "--font-directory",
    type=Path,
    default=Path("/System/Library/Fonts/Supplemental"),
    help="Directory containing the approved Georgia regular and bold fonts",
)
args = parser.parse_args()
here = Path(__file__).resolve().parent
repo = here.parents[1]
lib = args.book
num = args.chapter
dest = args.output.resolve()
dest.mkdir(parents=True, exist_ok=True)
base = args.base_url.rstrip("/") + "/"
panel_css = (here / "resources-panel.css").read_text()
panel_exporter = (here / "resources-panel.js").read_text()
assets = repo / "resources/teaching/v003" / lib
deck = json.loads((assets / f"chapter-{num:02}.json").read_bytes())["slides"]
subject = lib.replace("further-", "Further ").replace("-1", " 1").title()
bg = {
    "further-statistics-1": (219 / 255, 64 / 255, 64 / 255),
    "further-mechanics-1": (233 / 255, 119 / 255, 56 / 255),
}[lib]
white = (1, 1, 1)
navy = (24 / 255, 57 / 255, 87 / 255)
red = (1, 0.63, 0.64)
font = args.font_directory / "Georgia.ttf"
bold = font.with_name("Georgia Bold.ttf")
ref = pdf.open(repo / "resources/pure-year-1/v11/booklets/chapter-01.pdf")
size = ref[0].rect
ref.close()
labels = []
ledger = []


def place_panel(page, rectangle, panel):
    page.show_pdf_page(rectangle, panel, 0)
    source = panel[0]
    scale = min(
        rectangle.width / source.rect.width, rectangle.height / source.rect.height
    )
    dx = rectangle.x0 + (rectangle.width - source.rect.width * scale) / 2
    dy = rectangle.y0 + (rectangle.height - source.rect.height * scale) / 2
    matrix = pdf.Matrix(scale, 0, 0, scale, dx, dy)
    for link in source.get_links():
        uri = link.get("uri", "")
        if uri.startswith(("https://", "http://")):
            page.insert_link(
                {"kind": pdf.LINK_URI, "from": link["from"] * matrix, "uri": uri}
            )


with sync_playwright() as pw:
    b = pw.chromium.launch(channel=os.environ.get("LUISA_BROWSER_CHANNEL", "chrome"))
    page = b.new_page(viewport={"width": 1440, "height": 900})
    paper = b.new_page()
    paper.goto(base + "vendor/katex.min.css")
    page.goto(base + f"teaching-lesson-viewer.html?book={lib}&chapter={num}")
    page.wait_for_function("window.FMQ_TEST?.getState().slide")
    for n, slide in enumerate(deck, 1):
        page.evaluate("n=>FMQ_TEST.show(n-1)", n)
        page.evaluate("document.fonts.ready")
        labels.append(page.locator("#lesson-title").inner_text())
        if n == 1:
            continue
        page.evaluate("FMQ_TEST.revealAll()")
        page.evaluate("Promise.all([...document.images].map(e=>e.decode()))")
        for edition in ["student", "worked"]:
            dat = page.evaluate(panel_exporter, {"edition": edition})
            w, h = dat["w"], dat["h"]
            if page.locator("#lesson-exam-title:not([hidden])").count():
                h += 52
                dat["html"] = (
                    '<div style="font:32px Lesson;padding:5px 16px;height:52px">Exam style question</div>'
                    + dat["html"]
                )
            css = "".join(
                f'<link rel="stylesheet" href="{link}">' for link in dat["css"]
            )
            source = f"""<!doctype html><base href="{base}">{css}<style>
   :root {{--panel-width:{w}px;--panel-height:{h}px;}}
   {panel_css}
   @page {{size:{w}px {h}px; margin:0}}
   </style><main>{dat["html"]}</main>"""
            paper.set_content(source, wait_until="load")
            paper.add_script_tag(
                content=(repo / "scripts/booklets/print-maths.js").read_text()
            )
            paper.evaluate("prepareBookletMath(document)")
            paper.evaluate("Promise.all([...document.images].map(e=>e.decode()))")
            paper.evaluate("document.fonts.ready")
            path = dest / f"{edition}-{n:02}.pdf"
            paper.pdf(path=path, prefer_css_page_size=True, print_background=True)
            with pdf.open(path) as a:
                assert len(a) == 1, (slide["id"], edition)
            ledger.append(
                [n, slide["id"], edition, paper.locator(".write-area").count()]
            )
    b.close()
for edition in ["student", "worked"]:
    doc = pdf.open()
    toc = []
    for j, s in enumerate(deck):
        n = j + 1
        lower = j % 2
        Y = 413.25 * lower
        if not lower:
            doc.new_page(width=size.width, height=size.height)
        page = doc[-1]
        panel = pdf.Rect(14.625, 11.625 + Y, 580.875, 415.875 + Y)
        header = pdf.Rect(15, 12 + Y, 580.5, Y + 33.75)
        body = pdf.Rect(17, Y + 36, 578, Y + 413.8)
        if n == 1:
            title = deck[0]["title"]
            page.draw_rect(panel, fill=bg, color=None)
            page.insert_text(
                (21.7, 27.75),
                f"{subject} Chapter {num} - {title}",
                fontsize=13.5,
                fontname="Georgia",
                fontfile=font,
                color=white,
            )
            page.insert_text(
                (574 - pdf.get_text_length("1", fontname="tibo", fontsize=13.5), 27.75),
                "1", fontname="tibo", fontsize=13.5, color=white,
            )
            typeface = pdf.Font(fontfile=str(bold))
            lines = [""]
            for word in title.split():
                t = (lines[-1] + " " + word).strip()
                if typeface.text_length(t, fontsize=36) > 530 and lines[-1]:
                    lines.append(word)
                else:
                    lines[-1] = t
            y = 225 - 21 * (len(lines) - 1)
            for line in lines:
                page.insert_text(
                    ((size.width - typeface.text_length(line, fontsize=36)) / 2, y),
                    line,
                    fontsize=36,
                    fontname="GeorgiaBold",
                    fontfile=bold,
                    color=white,
                )
                y += 43
            if edition == "worked":
                subtitle = "Solutions"
                width = typeface.text_length(subtitle, fontsize=24)
                colour = white if lib == "further-statistics-1" else (0.65, 0.07, 0.12)
                page.insert_text(
                    ((size.width - width) / 2, y),
                    subtitle,
                    fontsize=24,
                    fontname="GeorgiaBold",
                    fontfile=bold,
                    color=colour,
                )
            continue
        page.draw_rect(panel, color=navy, width=0.55)
        page.draw_rect(header, fill=navy, color=None)
        title = labels[j]
        page.insert_text(
            (21.67, Y + 27.75),
            title,
            fontname="Georgia",
            fontfile=font,
            fontsize=13.5,
            color=red if s.get("extension") else white,
        )
        if edition == "worked":
            page.insert_text(
                (518, Y + 27.75), "Solution", fontname="tibo", fontsize=10.5, color=red
            )
        page.insert_text(
            (
                574 - pdf.get_text_length(str(n), fontname="tibo", fontsize=13.5),
                Y + 27.75,
            ),
            str(n),
            fontname="tibo",
            fontsize=13.5,
            color=white,
        )
        with pdf.open(dest / f"{edition}-{n:02}.pdf") as p:
            place_panel(page, body, p)
        toc.append([1, f"{n}. " + (s.get("navigationTitle") or title), j // 2 + 1])
    doc.set_toc(toc)
    doc.subset_fonts()
    doc.set_metadata({"title": f"{subject} · {deck[0]['title']} · " + edition})
    doc.save(dest / (edition + ".pdf"), garbage=4, deflate=True, use_objstms=1)
    doc.close()
(dest / "panels.json").write_text(json.dumps(ledger, indent=1))
