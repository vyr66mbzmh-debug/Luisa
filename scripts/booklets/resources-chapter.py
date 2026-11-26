from pathlib import Path
from playwright.sync_api import sync_playwright
import pymupdf as pdf
import json
from argparse import ArgumentParser
import os
from html import escape
from urllib.parse import urljoin

parser = ArgumentParser(
    description="Export a Resources chapter as paired two-up A4 handouts."
)
parser.add_argument("book", help="Book key from teaching-catalogue.js")
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
parser.add_argument("--plan", type=Path, help="JSON with one-based mapping and changed panel numbers")
parser.add_argument("--previous-student", type=Path, help="Matching student edition before the edits")
parser.add_argument("--previous-worked", type=Path, help="Matching worked edition before the edits")
args = parser.parse_args()
if bool(args.plan) != bool(args.previous_student) or bool(args.plan) != bool(args.previous_worked):
    parser.error("Supply the edit plan and both previous editions together.")
here = Path(__file__).resolve().parent
repo = here.parents[1]
lib = args.book
num = args.chapter
dest = args.output.resolve()
dest.mkdir(parents=True, exist_ok=True)
base = args.base_url.rstrip("/") + "/"
panel_css = (here / "resources-panel.css").read_text()
panel_exporter = (here / "resources-panel.js").read_text()
catalogue = json.loads((repo / "teaching-catalogue.js").read_text().split("=", 1)[1].strip().rstrip(";"))
volume = catalogue[lib]
chapter = next(item for item in volume["chapters"] if item["number"] == num)
assets = (repo / chapter["booklet"]).parent.parent
deck = json.loads((assets / f"chapter-{num:02}.json").read_bytes())["slides"]
subject = volume["title"]
colours = {
    "further-statistics-1": (219 / 255, 64 / 255, 64 / 255),
    "further-mechanics-1": (233 / 255, 119 / 255, 56 / 255),
}
previous = {"student": args.previous_student, "worked": args.previous_worked}
mapping = list(range(1, len(deck) + 1))
changed = set(mapping)
if args.plan:
    plan = json.loads(args.plan.read_text())
    mapping = plan["mapping"]
    changed = set(plan["changed"])
    if (len(mapping) != len(deck) or mapping[0] != 1 or 1 in changed or
        any(type(n) is not int or n < 1 for n in mapping) or
        not changed.issubset(range(2, len(deck) + 1))):
        parser.error("The plan must map every panel and retain the original cover.")
    for edition, path in previous.items():
        with pdf.open(path) as original:
            if max(mapping) > 2 * len(original):
                parser.error(f"The {edition} reference is too short for the plan.")
elif lib not in colours:
    parser.error("Use the chapter’s approved covers and an edit plan for this module.")
white = (1, 1, 1)
navy = (24 / 255, 57 / 255, 87 / 255)
red = (1, 0.63, 0.64)
font = args.font_directory / "Georgia.ttf"
bold = font.with_name("Georgia Bold.ttf")
ref = pdf.open(repo / "resources/pure-year-1/v11/booklets/chapter-01.pdf")
size = ref[0].rect
ref.close()
labels = {}
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


def copy_panel_area(page, original, old_index, area, dy):
    # Clip the physical PDF content so a removed question is also removed from text search.
    with pdf.open() as single:
        single.insert_pdf(original, from_page=old_index, to_page=old_index, links=False)
        single[0].clip_to_rect(area)
        offset = pdf.Matrix(1, 0, 0, 1, 0, dy)
        page.show_pdf_page(area * offset, single, 0, clip=area)
    for link in original[old_index].get_links():
        if link.get("uri") and area.contains(link["from"]):
            page.insert_link({"kind": pdf.LINK_URI, "uri": link["uri"], "from": link["from"] * offset})


with sync_playwright() as pw:
    b = pw.chromium.launch(channel=os.environ.get("LUISA_BROWSER_CHANNEL", "chrome"))
    page = b.new_page(viewport={"width": 1440, "height": 900})
    paper = b.new_page()
    paper.goto(base + "vendor/katex.min.css")
    page.goto(urljoin(base, chapter["slides"]))
    page.locator("#slide-content .source-slide, #slide-content .ch14").first.wait_for(state="attached")
    for n, slide in enumerate(deck, 1):
        if n == 1 or n not in changed:
            continue
        page.evaluate("n=>FMQ_TEST.show(n-1)", n)
        page.evaluate("document.fonts.ready")
        labels[n] = page.locator("#lesson-title").inner_text()
        page.evaluate("Promise.all([...document.images].map(e=>e.decode()))")
        for edition in ["student", "worked"]:
            # The legacy FM/FS teaching templates use the completed diagram in both
            # paper editions. Native exercise pages expose only the question initially.
            initial = edition == "student" and args.plan is not None
            page.evaluate("FMQ_TEST.reset()" if initial else "FMQ_TEST.revealAll()")
            page.evaluate("document.fonts.ready")
            page.evaluate("Promise.all([...document.images].map(e=>e.decode()))")
            if page.locator(".katex-error").count():
                raise ValueError(f"Invalid classroom maths on panel {n}")
            dat = page.evaluate(panel_exporter, {"edition": edition})
            w, h = dat["w"], dat["h"]
            if page.locator("#lesson-exam-title:not([hidden])").count():
                h += 52
                dat["html"] = (
                    '<div style="font:32px Lesson;padding:5px 16px;height:52px">Exam style question</div>'
                    + dat["html"]
                )
            css = "".join(
                f'<link rel="stylesheet" href="{escape(link, quote=True)}">' for link in dat["css"]
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
    original = pdf.open(previous[edition]) if args.plan else None
    # Preserve an unchanged A4 sheet as a single page, including its links.
    # Repeatedly clipping and re-embedding both halves nests old drawing objects.
    intact_sheets = {
        j // 2 for j in range(0, len(deck) - 1, 2)
        if original is not None and mapping[j:j + 2] == [j + 1, j + 2]
        and changed.isdisjoint((j + 1, j + 2))
    }
    for j, s in enumerate(deck):
        n = j + 1
        lower = j % 2
        if j // 2 in intact_sheets:
            if not lower:
                doc.insert_pdf(original, from_page=j // 2, to_page=j // 2, final=False)
            if n > 1:
                toc.append([1, f"{n}. " + (s.get("navigationTitle") or s["title"]), j // 2 + 1])
            continue
        Y = 413.25 * lower
        if not lower:
            doc.new_page(width=size.width, height=size.height)
        page = doc[-1]
        panel = pdf.Rect(14.625, 11.625 + Y, 580.875, 415.875 + Y)
        header = pdf.Rect(15, 12 + Y, 580.5, Y + 33.75)
        body = pdf.Rect(17, Y + 36, 578, Y + 413.8)
        if original is not None:
            old = mapping[j]
            old_index, half = divmod(old - 1, 2)
            old_y = 413.25 * half
            if n == 1 or (n not in changed and n == old):
                crop = pdf.Rect(0, 0 if n == 1 else old_y + 8, size.width, 417.9 if n == 1 else old_y + 416)
                copy_panel_area(page, original, old_index, crop, 0)
                if n > 1:
                    toc.append([1, f"{n}. " + (s.get("navigationTitle") or s["title"]), j // 2 + 1])
                continue
        if n == 1:
            title = deck[0]["title"]
            page.draw_rect(panel, fill=colours[lib], color=None)
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
        title = labels.get(n, s["title"])
        if original is not None and n not in changed:
            words = original[old_index].get_text("words", clip=pdf.Rect(16, old_y + 11, 497, old_y + 32))
            title = " ".join(word[4] for word in sorted(words, key=lambda w: w[0])) or title
        mark_x = 500 if n >= 100 else 515
        width = (mark_x - 28 if edition == "worked" else 526)
        title_size = min(13.5, 13.5 * width / max(1, pdf.Font(fontfile=str(font)).text_length(title, fontsize=13.5)))
        page.insert_text(
            (21.67, Y + 27.75),
            title,
            fontname="Georgia",
            fontfile=font,
            fontsize=title_size,
            color=red if s.get("extension") else white,
        )
        if edition == "worked":
            page.insert_text(
                (mark_x, Y + 27.75), "Solution", fontname="tibo", fontsize=10.5, color=red
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
        if n in changed:
            with pdf.open(dest / f"{edition}-{n:02}.pdf") as p:
                place_panel(page, body, p)
        else:
            crop = pdf.Rect(15.3, old_y + 34.3, 580.15, old_y + 415.15)
            copy_panel_area(page, original, old_index, crop, Y - old_y)
        toc.append([1, f"{n}. " + (s.get("navigationTitle") or title), j // 2 + 1])
    doc.set_toc(toc)
    doc.subset_fonts()
    doc.set_metadata({"title": f"{subject} · {deck[0]['title']} · " + edition})
    doc.save(dest / (edition + ".pdf"), garbage=2 if intact_sheets else 4, deflate=True, use_objstms=1)
    doc.close()
    if original is not None:
        original.close()
(dest / "panels.json").write_text(json.dumps(ledger, indent=1))
