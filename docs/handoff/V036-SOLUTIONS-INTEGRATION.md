# v0.36 solutions integration — next-agent handoff

[Luisa](https://fmq-6d9.pages.dev/) · [Development progress](https://fmq-6d9.pages.dev/development-progress)

Owner instruction, 9 November 2026: load the completed solution booklets into Luisa. They must appear in teaching chapters, View by textbook for the relevant topic, and Development progress. This task is implementation and checked release; the present change only records the requirements and handoff.

## Authority and version

Read AGENTS.md, HANDOFF.md, docs/agentic/LEAD-RULES.md, docs/handoff/BOOKLET-STANDARD.md and requirements BKT-036-SOLUTIONS, BKT-036-ORIGINALS, BKT-036-RETENTION and WEB-036-SOLUTIONS. This explicit owner instruction supersedes previous private-only restrictions on solution PDFs. It does not authorise publishing LaTeX originals, original PowerPoints/textbooks, private diagnostics or machine-specific paths.

The owner calls this version 36, but release.json and the existing student release already say 0.36. Treat it as the requested v0.36 solutions integration follow-up; preserve the historical student release record, use a new commit/artifact identity and increment the service-worker/cache revision. Do not claim this documentation change published solutions. If the release tooling requires a new public version rather than a v0.36 follow-up, surface that naming conflict before choosing v0.37 silently.

## Inputs and existing evidence

Resolve these paths relative to website; consult the private workspace map for another machine:

- `../Students Handout/`: accepted v0.36 student layout reference, 62 chapters and 1,489 pages.
- `../Student Handout Solutions/`: 62 solution PDFs in the eight book folders, using the same chapter basenames; 1,496 pages covering 2,947 teaching slides.
- That collection's `_Latex original/`: 62 compiled PDF-backed LaTeX bundles and matching `_assets` PDFs, retained privately.
- `ACCEPTANCE.json`, `_verification/COLLECTION-AUDIT.json` and `_verification/VIEWER-COMPATIBILITY.json`: current installed hashes and acceptance. Per-chapter records include the viewer compatibility repair and recompiled reproduction checks. Verify current hashes before importing.
- Pure Year 1 Chapter 12 has 39 baseline pages plus seven appendix pages containing its linked teaching solutions; preserve these and the cross-references.

An earlier claim based on one renderer missed a real defect: the red-text conversion wrapped individual text operators in q/Q, causing Apple Quartz to collapse characters onto one another. The final PDFs were repaired using explicit fill-colour restoration, all 1,496 pages were cross-checked, and all 62 reproductions recompiled. Use these final repaired files, not earlier candidates or archived hashes. Regression: Pure1_Ch09_Trigonometric_Ratios.pdf slides 4–5 must be readable in macOS Preview and an independent renderer. Retain the recorded small renderer/antialias exceptions; do not waive new content or placement failures.

## Implementation

1. Inspect current main, dirty state and open work; use an isolated branch and preserve owner edits. Follow the normal issue/PR workflow. Do not regenerate all booklet content merely to add links.
2. Copy only verified solution PDFs into a dedicated deployable resource location. Add one canonical `solutions` resource per teaching chapter in teaching-catalogue.js, keyed by course/year/chapter identity. Validate all 62 mappings and hashes; keep student `booklet`, textbook `pdf` and practice resources distinct.
3. Add a clearly labelled Solutions action to every teaching chapter entry and its chapter/player resource controls, following existing document-viewer conventions. Preserve return navigation, desktop/touch behaviour and existing student resources.
4. In View by textbook, use existing topic-to-chapter relationships to expose the correct solution booklet for each relevant topic. Where one chapter covers several topics, reuse the canonical chapter resource; where several chapters apply, label each distinctly. Do not guess mappings from title similarity or duplicate PDF bytes per topic.
5. Extend scripts/report_chapters.py and Development progress chapter rows to show a distinct direct Solutions link and truthful status. Regenerate the report rather than manually adding links that the next report generation will erase. Separate local booklet acceptance from live integration verification.
6. Refresh applicable download/offline manifests and cache revision. Verify downloading a chapter includes the current solution PDF, offline reopening works, and saved older packs replace stale bytes. Use document-relative URLs compatible with both root deployment and ADA's /AL/ prefix.

## Mandatory propagation for every future slide change

A slide or dependent-asset change invalidates affected chapter acceptance. Regenerate the matching student PDF and solution PDF together; update both PDF-backed LaTeX wrappers/assets, compile both, replace owner copies and the website PDF copies, refresh catalogue/report/offline fingerprints, and verify the installed/published hashes. Review changed content against fully revealed sources and inspect affected pages for complete working, question association, readability, diagrams/crops and banners. Check Apple Quartz/macOS Preview AND an independent renderer. Preserve unselected chapter fingerprints and mark changed sources stale. Delete only superseded generated variants after the replacement bundle passes; preserve original sources and required current assets.

## Acceptance and release

- All 62 solution PDFs available through all three requested surfaces, with correct textbook-topic associations and no broken/HTML-fallback PDF responses.
- Actual PDF bytes, MIME types, chapter identities and page counts verified; Pure1 Ch9 slides 4–5 readable in Preview and independent rendering. Linked Differentiation appendix retained.
- Student PDFs remain unchanged unless the chapter's source actually changed. Solution links must not reveal or alter the student booklet.
- Private LaTeX originals, source materials and private evidence excluded from the public artifact. No new authentication system is requested by this task.
- Targeted navigation/report/offline tests, prefix-host test, full local gate and current-head build/test/scan pass before landing. Self-report pending physical-device checks honestly.
- Publish the same checked artifact to Cloudflare and ADA using docs/DEVOPS.md; verify manifests and actual changed destinations on both hosts. Update requirements, evidence and HANDOFF, then follow the established release-report workflow. Do not equate a push or successful build with a verified release.
