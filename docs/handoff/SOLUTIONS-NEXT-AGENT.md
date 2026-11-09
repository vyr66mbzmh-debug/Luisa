# Complete the private solution booklets

Prepared 9 November 2026 for the owner's next Astra agent, using medium reasoning. This is the continuation brief for the private solution work stopped on 8 November. The owner will give this task to the next agent. This documentation update performs the handoff.

## Start and scope

Read AGENTS.md, HANDOFF.md, docs/agentic/LEAD-RULES.md and [BOOKLET-STANDARD.md](BOOKLET-STANDARD.md). Inspect Git status, worktrees and the current catalogue before editing.

The accepted student baseline is v0.36 at release revision `41d724dcdfa2acbe21b8b5f622bf2488de16d773`, published on Cloudflare and ADA. It has 62 chapters, 2,947 teaching slides and 1,489 A4 booklet pages. The 62 student owner PDFs and 62 compiled PDF-backed LaTeX reproduction originals are complete. Their public acceptance is recorded in [v036-booklets.json](../evidence/v036-booklets.json) and [v036-acceptance.json](../evidence/v036-acceptance.json).

Complete a matching private solution PDF and LaTeX reproduction bundle for every chapter, using the eight-book locations in the standard. Preserve the accepted student page composition, questions, diagrams, numbering and coloured title panels. Put the complete revealed working in red inside the appropriate answer areas. Add red `Solution` before each white slide number in the existing blue teaching banner. Maintain the student reference PDFs as the accepted baseline throughout private solution development.

## Current private state

Resolve these paths relative to the repository root.

- `../materials/build/output/v035-final/SOLUTIONS-STOPPED-CHECKPOINT.json` records the stop instruction, latest failure and extraction issues.
- `../materials/build/output/v035-final/request.json` records v0.36 and the chosen PDF-backed LaTeX format.
- `../materials/build/output/v035-final/booklets.json` maps chapters to student PDF basenames and owner folders.
- `../materials/build/output/v035-final/solution-map.jsonl`, `pdf-field-fit.json` and the build/verification logs are prototype diagnostics. Review their timestamps and scope before reuse.
- `../Student Handout Solutions/UNFINISHED.txt` marks the current collection as unfinished. Existing solution PDFs and LaTeX sources contain known defects and need replacement after verification.

Candidate scripts are in `../materials/build/scripts/v035-final/`. `solutions.cjs` currently exports per-field PDFs and destination metadata. `red-text.py` can colour native field text. `fit-fields.py` measures visible PDF ink and fits it into student rectangles. `merge-solutions.py` assembles the private booklet and adds the red banner marker. `latex.py` creates and compiles the reproduction wrappers. `regenerate.py` is a draft orchestration entry point. Inspect these candidates and validate their behaviour before running a broad batch.

The prior `make-generator.py` was removed because its stale template would overwrite later fixes. Retain the corrected source and scope behaviour in any replacement workflow.

The original machine also has a pre-existing local main-only owner handoff commit and an untracked `docs/handoff/V0.34-DEVELOPMENT.md`. Preserve that owner material and follow the repository privacy rules when preparing GitHub changes. Use the private workspace map to locate original source materials.

## Known failure modes to resolve

### Masked content and captions

Explicit `data-answer-for` ownership alone does not describe every reveal. Some original masks conceal working geometrically while other pieces have explicit owners. Compare the fully revealed teaching slide with the student panel and account for all substantive hidden working.

Statistics Year 1 Chapter 2, slide 37, cover 44 is a critical regression case. Its student PDF visibly has a blank white field, while PDF text extraction can still return black worked interpolation content beneath that opaque cover. Those concealed spans are not visible captions. The prototype failed at sheet index 18 because it reserved the bottom of all extracted text and produced a negative answer region. Identify the actual visible cue near the top, using its print colour/source identity and rendering. Include the geometrically concealed working in the completed solution.

### Placement and picture crops

Browser-space boxes and an owner-count match do not establish printed containment. Earlier attempts produced clipped working, answers above or left of their fields, and very small calculations. A per-field PDF approach passed a trial on all 27 pages of Statistics Year 2 Chapter 2. Fitting complete visible ink into the exact student PDF rectangles gives a useful basis for verification. Keep aspect ratios and cap magnification so short answers remain consistent with the question typography.

Respect `.lesson-picture-crop` and the source crop metadata. In Statistics Year 2 Chapter 2 slide 43, picture owner 8 displays a cropped portion of a larger source image. Measuring the entire image produced a tiny tree and narrative. The latest trial also trimmed an unrelated fragment reading “selected.” above the tree. Verify the full mathematical diagram remains visible.

Two yellow selection highlights on Statistics Year 2 Chapter 2 slide 18 were omitted from the trial's answer areas, with the full restricted-sample explanations preserved. The approved title-only composition also omits introductory note controls on Mechanics Year 1 Chapters 10 and 11. Those notes remain available in the interactive slides. Review these documented exceptions against the sources.

### Explicit answer association

Carry source cover IDs into custom answer fields. An ordinal match using numeric object keys previously swapped interpolation answers. Statistics Year 1 Chapter 2 slide 30 must associate the six fields with covers `20, 21, 22, 49, 24, 23` and the corresponding answers `55, 75, 100, 0.6 m, Q₂, 0.65 m`.

### Regression examples

Use these examples in addition to the full output review.

| Book | Slides | Previous issue |
|---|---|---|
| Statistics Year 1 Chapter 2 | 9, 21, 28, 30, 37, 38, 54, 68, 90 | Custom association, compact values, concealed working, overflow and multi-part fields |
| Statistics Year 1 Chapter 3 | 6, 16, 27, 28, 29, 33 | Graphical spillovers, clipping and counts placed over the wrong table column |
| Statistics Year 1 Chapter 4 | 2 | Gradient and intercept became too small |
| Statistics Year 1 Chapter 5 | 9 | Samira's 3×4 product table and explanation needed coherent layout |
| Statistics Year 1 Chapter 6 | 17 | Red binomial working obscured the question |
| Statistics Year 1 Chapter 7 | 2 | Compact numeric answers were tiny or outside their fields |
| Statistics Year 2 Chapter 1 | 16 | Parts a and b were scarcely visible |
| Statistics Year 2 Chapter 2 | 18, 26, 43, 44, 46 | Restricted-sample working, labels, cropped trees, colour and scale |
| Statistics Year 2 Chapter 3 | 33 | Normal-distribution working was too small |
| Pure Year 2 Chapter 1 | 4 | Conclusion crossed the next label |
| Pure Year 2 Chapter 3 | 43 | Working crossed the field's lower border |
| Pure Year 2 Chapter 7 | 23 | Working crossed between tangent answer boxes |
| Mechanics Year 2 Chapter 6 | 10 | Time-of-flight working crossed into the next answer header |

## Completion method

1. Inspect the failed prototypes and the supplied sources. Complete and verify a difficult chapter before scaling up. Statistics Year 2 Chapter 2 provides compact answers, diagrams and mixed text/image cases. Resolve the concealed-content case in Statistics Year 1 Chapter 2 before broad generation.
2. Use actual final PDF ink bounds for placement. Preserve the complete working and mathematical diagrams. Check readable size, correct part association, captions, whitespace, aspect ratios and all original intermediate steps.
3. Render and inspect every finished solution page at its A4 scale. Check native text and graphics against the student writing rectangles. A containment test must include diagram/raster pixels as well as glyph coordinates. Resolve any clipping, overlap, missing working or unreadable answer.
4. Verify red revealed text, the blue/white/red header arrangement, all 62 cover designs, page counts, slide numbers and student-content preservation. Compare source/reveal content and question-part associations independently of counts and successful rendering.
5. Compile all 62 private LaTeX reproductions from their current bundled PDF assets and compare their pages/content with the accepted private PDFs. Maintain the current eight-book folder structure.
6. Replace each verified chapter bundle using the latest-only rules in BOOKLET-STANDARD.md. Selectively delete its superseded generated PDFs, `.tex` files and obsolete assets. Preserve unfinished chapters and source references. Keep the unfinished marker until all chapters pass.
7. Record source/dependency/output hashes and per-chapter evidence. Preserve unselected fingerprint entries and mark any changed unselected source stale. Refresh the requirement statuses and HANDOFF.md truthfully through the normal GitHub documentation workflow.

The final deliverables are 62 checked private solution PDFs and 62 checked LaTeX reproduction bundles. Keep the solution documents and assets in the private handout collection. The existing student release remains the reference for this task. Report the exact remaining chapter count if a genuine blocker prevents completion.
