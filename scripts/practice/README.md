# Practice Booklet extraction

This pipeline consumes native chapter LaTeX whose adjacent PDFs match the already
published Practice Booklet PDFs byte for byte. Originals remain read-only. All
source-location inventories belong outside Git. Pass the native source root
explicitly; do not place machine-specific paths in these scripts.

1. `inventory.py --native-root "$PRACTICE_NATIVE_ROOT" --private-output "$PRACTICE_WORK"`
2. `extract.py --inventory "$PRACTICE_WORK/native-inventory.json" --output "$PRACTICE_WORK/native-questions.json"`
3. Acquire the repository resource guard before PDF processing, then run
   `locate.py --questions "$PRACTICE_WORK/native-questions.json" --output "$PRACTICE_WORK/locations.json"`.
4. `build.py --inventory "$PRACTICE_WORK/native-inventory.json" --questions "$PRACTICE_WORK/native-questions.json" --locations "$PRACTICE_WORK/locations.json" --report "$PRACTICE_WORK/build-report.json"`
5. `python3 -m unittest discover -s tests -p test_practice_extraction.py`
6. `node scripts/practice/check-math.cjs`

The PDF steps require PyMuPDF. Release the resource guard in a finally block or
shell trap, including on failure. Rendering accepts the native booklet dialect
and fails on unsupported commands. Source-defined vector and derivative macros
expand to native mathematical notation; the long-division rule is represented
by an overline over the dividend. Source image files are copied unchanged to
content-addressed filenames. Data tables retain borders, while layout tables
use a separate CSS class. The row source marker is a label anchor in PDF points,
not a complete question crop rectangle.

Every hint is removed from `question` and retained in `hints`. Build outputs have
empty `steps` and `solutionStatus: pending`; generating a prompt does not approve
a worked solution or make the row ready for inclusion in a paper. Lead-owned
integration supplies checked solutions, skill mappings and the root catalogue.
Rebuilding extracted data overwrites those fields, so merge downstream data only
after extraction has completed.
