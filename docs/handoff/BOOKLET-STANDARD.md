# Booklet standard

Updated 9 November 2026 from the owner's approved v0.35 and v0.36 instructions. These requirements apply to current booklets and every subsequent slide or booklet change. The canonical requirement IDs are BKT-035, BKT-036-COVER, BKT-036-SOLUTIONS, BKT-036-ORIGINALS and BKT-036-RETENTION in [the register](../requirements/register.json).

## Page and title-panel design

Use A4 pages with two original slide panels per page. Preserve the accepted chapter, slide and page order, titles, numbering, questions, theory, diagrams and working areas. The coloured cover is the upper title panel on the first physical page. The lower panel on that page follows the normal teaching-panel design.

Fill the entire title panel, including its integrated top banner, with the colour assigned below. Centre the chapter title in white (#FFFFFF), using Georgia Bold at 36 points. Wrap long titles and verify their fit. The accepted 62 title panels all fit at 36 points.

| Book | Filename prefix | Owner book folder | Title-panel background |
|---|---|---|---|
| Pure Year 1 | Pure1 | Pure 1 | #2E6B9E, RGB(46, 107, 158) |
| Pure Year 2 | Pure2 | Pure 2 | #2E6B9E, RGB(46, 107, 158) |
| Mechanics Year 1 | Mechanics1 | Mechanics 1 | #5A3838, RGB(90, 56, 56) |
| Mechanics Year 2 | Mechanics2 | Mechanics 2 | #5A3838, RGB(90, 56, 56) |
| Statistics Year 1 | Statistics1 | Statistics 1 | #5A3838, RGB(90, 56, 56) |
| Statistics Year 2 | Statistics2 | Statistics 2 | #5A3838, RGB(90, 56, 56) |
| Core Pure Year 1 | CorePure1 | Pure Core 1 | #0E8A5A, RGB(14, 138, 90) |
| Core Pure Year 2 | CorePure2 | Pure Core 2 | #0E8A5A, RGB(14, 138, 90) |

The white title-panel banner names the subject, year, chapter number and topic. For example, `Statistics Year 1 Chapter 1 - Data Collection`. The cover composition has no standalone slide-number marker. Keep the title-only design, including on the private solution cover.

## Teaching-panel banners and content

Later panels have white teaching backgrounds and the existing navy-blue banners (#183957, RGB(24, 57, 87)). Preserve their accepted white titles and white slide numbers. Omit Luisa from every booklet header. Maintain the existing banner typography and mathematical typesetting.

The student version conceals answers and provides the accepted handwriting space. The private solution version preserves the student page composition and fills the corresponding answer areas with the complete supplied working in red. Insert the red word `Solution` immediately before each white slide number. The remaining banner title stays white on the same navy background. Keep all header elements clear of one another.

Supplied raster diagrams retain their original colours and aspect ratios. Preserve meaningful diagrams, arrows, annotations, intermediate steps and source crops. Native revealed working must be red and readable. Fit complete answer ink into the real student PDF writing rectangles while retaining question and cue text. Verify every answer's destination and its association with the question.

## Filenames and locations

Use `BookYear_ChNN_Chapter_Title.pdf`, including a two-digit chapter number and underscores between title words. Examples are `CorePure1_Ch01_Complex_Numbers.pdf` and `Statistics2_Ch02_Conditional_Probability.pdf`. Preserve the textbook's chapter numbers, including the combined Statistics and Mechanics numbering. The private solution version uses the same basename in its own collection. The LaTeX file uses the same basename with `.tex`.

Resolve the following paths from the `website` repository root. Its parent is the local `_LUISA` workspace. Machine-specific absolute paths are held in the private `WORKSPACE.json` under `LUISA_STATE_DIR`.

| Document | Location |
|---|---|
| Public student PDF | Each chapter's `booklet` path in [teaching-catalogue.js](../../teaching-catalogue.js) |
| Student owner copy | `../Students Handout/<Owner book folder>/<basename>.pdf` |
| Student LaTeX original | `../Students Handout/_Latex original/<Owner book folder>/<basename>.tex` |
| Student reproduction asset | `../Students Handout/_Latex original/<Owner book folder>/_assets/<basename>.pdf` |
| Private solution PDF | `../Student Handout Solutions/<Owner book folder>/<basename>.pdf` |
| Private solution LaTeX original | `../Student Handout Solutions/_Latex original/<Owner book folder>/<basename>.tex` |
| Private solution reproduction asset | `../Student Handout Solutions/_Latex original/<Owner book folder>/_assets/<basename>.pdf` |
| Private authoring candidates | `../materials/build/scripts/v035-final/` |
| Private checkpoint and evidence | `../materials/build/output/v035-final/` |

LaTeX originals are compilable PDF-backed reproduction documents with bundled PDF assets. The owner selected this format for token efficiency. Compile from each book's LaTeX folder and verify the resulting pages against the finished booklet. Content edits belong in the teaching source, followed by regeneration of the PDF and its reproduction bundle.

Keep solution PDFs, LaTeX sources, reproduction assets, intermediate documents and machine-specific state in the private workspace. Public releases contain the student booklets and their catalogue links.

## Latest-only replacement and selective deletion

The owner authorises selective deletion of superseded generated PDF and LaTeX documents after verified replacement. Apply the rule per chapter and per requested output collection.

1. Identify the exact course, year and chapter being replaced, its canonical basename, existing references and required reproduction assets. Use the catalogue and the chapter manifest to establish that identity.
2. Build the replacement in a temporary working location. Render the PDF, check complete content and layout, compile the LaTeX reproduction, and compare the owner copy with the approved output.
3. Install the verified PDF, `.tex` file and its matching current `_assets` PDF as one chapter bundle. Verify all installed hashes and references before marking the chapter checked.
4. Delete the superseded variants and temporary `.new`, `.part`, dated, numbered or backup copies belonging to that replaced chapter. Remove its obsolete reproduction assets once their references have been replaced. Keep a single current canonical document and its required current reproduction asset in the final collection.
5. Preserve all chapters outside the requested replacement set. Preserve source PowerPoints, textbook PDFs, reference libraries and unrelated owner files. Release recovery archives follow the established [DEVOPS policy](../DEVOPS.md).

Catalogue-required compatibility aliases must contain the current student PDF bytes. Refresh those aliases and their references together. Apply the same selective cleanup to job-owned intermediate PDF/LaTeX copies once the chapter is accepted and the files are no longer needed by unfinished work. Preserve useful verification manifests and hashes.

Existing unverified solution drafts remain candidates until their replacement passes acceptance. During partial completion, the chapter manifest must distinguish accepted chapters from unfinished ones. Remove the collection's unfinished marker when the full collection passes its final checks.

## Change propagation and reporting

Any changed slide or dependent teaching asset requires refreshed affected student and private solution PDFs, both LaTeX reproduction bundles and the owner copies. Recheck source content, maths, reveal correspondence, rendered pages and answer placement before renewing acceptance. Track deck, dependent-asset, renderer and output fingerprints.

For scoped work, preserve prior fingerprint entries for unselected chapters. A changed unselected chapter requires a stale/needs-regeneration status. Acceptance must continue to refer to the source and output that were actually checked.

Every release and development report starts with a visible Luisa website link. Website links use `./` so both the root deployment and ADA's `/AL/` deployment resolve correctly. Publication and final release email follow [the release workflow](../DEVOPS.md) and [FR-024](RELEASE-EMAIL.md).
