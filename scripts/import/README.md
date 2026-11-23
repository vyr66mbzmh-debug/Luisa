# Past-paper import pipeline

This pipeline turns owner-supplied past papers (a question paper and mark scheme PDF pair) into Luisa Papers content:
- native HTML and KaTeX prompts;
- vector figure crops;
- the complete official mark scheme as ordered vector crops;
- catalogue and metadata rows;
- evidence.

It is engine-neutral and needs only the bootstrapped environment (`scripts/bootstrap.py`: PyMuPDF, SymPy; Tesseract is optional).

**Rules.** Source PDFs are untrusted and read-only. They stay in the private source folder (WORKSPACE key `pastPaperSource`, or `--source`) and never enter Git; the privacy gate blocks them. Run every script with `python3 -I`. A PDF is used only when its SHA-256 equals the hash recorded in the set (`common.ImportSet.pdf`). Never guess or silently repair a question: record source errors verbatim in the evidence notes. Work files (inventory, page images, asset records) go to `<state>/import/<set>/`.

## Layout
| Path | Purpose |
|---|---|
| `common.py` | Set loading, source-folder lookup, hash-checked PDF access, work-folder paths |
| `lib.py` | Prompt HTML helpers (`m`, `eq`, `mk`, `parts`, `fig`, `table`, `context`, standard instruction texts) |
| `build_assets.py` | Figure SVGs from `figs.json`; mark-scheme crops from `msstart`/`msend`, with a full-coverage assertion |
| `build_payload.py` | `content/exams/<paperId>.json` (prompts plus scheme crops) |
| `integrate.py` | Adds the paper to `content/exams/pilot-metadata.json` and `exam-catalogue.json` (idempotent) |
| `aids/` | `inventory.py` (identify files by cover and hash), `qpstarts.py`, `msstarts.py`, `marks.py` (totals agree), `figscan.py` (figure boxes), `pages.py` (page images, optional OCR), `guard.py` (no foreign labels in scheme crops) |
| `sets/<name>/` | One release's inputs: `papers.py` (PAPERS, ORDER), `maps.py` (topic, skills and chapter keys per question), `prompts/<paperId>.py`, `maths/<paperId>.py` (independent SymPy checks), `figs.json`, `marks.json`, `qpends.json`, `checks.json`, `evidence.py` |

`sets/v072-sample/` is the reference set: the five Sample Assessment Material papers released in v0.72.

## Steps for a new import (one release)
1. Run `python3 -I scripts/import/aids/inventory.py --set <new-set>` after creating `sets/<new-set>/papers.py`, which can start with an empty `PAPERS = {}` and `ORDER = [...]`. Identify each file by its cover, pair QP with MS, and skip byte-identical duplicates (the inventory shows the papers they duplicate). Post the inventory on the issue (file names and hashes are fine; never paths).
2. Fill `papers.py`: code, title, session, dates, minutes, question count, total, qp/ms relative paths and hashes, public indexed copies if any, and `msstart`/`msend`. Use `aids/msstarts.py` and `aids/marks.py`; their totals must AGREE.
3. Write `prompts/<paperId>.py` from the page images (`aids/pages.py`, plus `--ocr` as an aid). Use `figs.json` boxes for figures (`aids/figscan.py`), `marks.json` and `qpends.json`.
4. Run `build_assets.py --set <set> <paperId>`, `aids/guard.py`, `build_payload.py`, then `integrate.py` (with `maps.py` filled). Solve every question independently in `maths/<paperId>.py`, and record a one-line agreement per question in `checks.json`.
5. Copy and adapt `evidence.py` and write `docs/evidence/v<vv>-import-<name>.json`. Update tests (`tests/test_papers_selection.py`, `tests/papers_print_browser.py`) and the register, then follow `docs/agentic/RELEASE-RUNBOOK.md`.

## Reproducibility (v0.73 proof)
The figure SVGs, payloads and catalogue rows of the v0.72 set regenerate byte-for-byte:
```
python3 -I scripts/import/build_assets.py --set v072-sample --figures-only <paperId>   # question paper only
python3 -I scripts/import/build_payload.py --set v072-sample <paperId>
python3 -I scripts/import/integrate.py --set v072-sample <paperId>
```
This was run with the public question-paper copies, which are byte-identical to the owner files. The public mark-scheme copies differ (each page has a watermark), so scheme crops can only be rebuilt from the owner's original mark schemes. The asset records from the original import are kept privately in `<state>/import/v072-sample/assets/`.
