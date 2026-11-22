# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.64 -->
**Release 0.64 · GitHub #112.** Past Papers adds the six June 2024 Edexcel papers. Each has its own Past Papers dropdown option, for example "June 2024 Paper 1 (Maths · 9MA0/01)".

| Paper | Title | Date | Questions | Marks | Easy / Medium / Difficult |
|---|---|---|---|---|---|
| 9MA0/01 | Pure Mathematics 1 | 4 June 2024 | 15 | 100 | Q1–5 / Q6–10 / Q11–15 |
| 9MA0/02 | Pure Mathematics 2 | 11 June 2024 | 15 | 100 | Q1–5 / Q6–10 / Q11–15 |
| 9MA0/31 | Statistics | 20 June 2024 | 6 | 50 | Q1–2 / Q3–4 / Q5–6 |
| 9MA0/32 | Mechanics | 20 June 2024 | 6 | 50 | Q1–2 / Q3–4 / Q5–6 |
| 9FM0/01 | Core Pure Mathematics 1 | 22 May 2024 | 8 | 75 | Q1–2 / Q3–6 / Q7–8 |
| 9FM0/02 | Core Pure Mathematics 2 | 3 June 2024 | 9 | 75 | Q1–3 / Q4–6 / Q7–9 |

Difficulty follows paper order. Papers now has 12 past papers with 121 questions and 900 marks, 554 Exam style questions and 8,068 Practice questions: 8,743 in total.

**Sources.** Each of the 12 owner-supplied PDFs was identified by its cover (board, code, paper, date, question and mark totals), and each question paper was paired with its scheme by cover. Every question's marks agree with its scheme. No paper was held.

**Content.**
- Prompts are native HTML and KaTeX with the original wording, part labels, marks, bold emphasis and question-specific instructions.
- Figures are vector crops of the source diagrams, with their captions.
- Each question prints only its own official mark-scheme pages as ordered vector crops, including alternatives, special cases, examiner notes and diagrams. General marking pages and publisher pages are excluded.
- Every question was solved independently and agrees with its scheme.
- Source hashes, page ranges, crop bounds, mathematical checkpoints, chapter mappings and two source notes are in `docs/evidence/v064-import-june2024.json`:
  - the 9FM0/01 Q8 hours/days wording, kept verbatim
  - an unembedded symbol glyph on 9MA0/01 scheme page 36, shown exactly as the supplied PDF shows it

**Evidence and release.**
- Metadata tests now key papers by ID, because 2024 and 2025 share paper codes.
- A June 2024 identity test checks hashes, marks, scheme pages and every asset hash.
- The selection tests check the 13 dropdown options and the new totals.
- The 2025 papers, saved IDs, In paper order and v0.63 print layouts are unchanged.
- The reviewed PR, live checks, recovery ZIP and owner report outcome are in GitHub #112.

**Usage.** Up to the pull request this job used 37,335,770 tokens in the main session (input 330, cache creation 406,909, cache read 36,781,149, output 147,382; 165 calls), summed from per-call usage in the session transcript. The final figure, including the independent review, is in GitHub #112 and the owner report.

<!-- LUISA-REPORT-HANDOFF v0.63 -->
**Release 0.63 · GitHub #110.** On Papers, when one individual past paper is chosen in the Past Papers dropdown, Question order adds **In paper order** next to Group by topic and As selected. That paper's questions print in original question-number order, and any other selected questions follow in the order they were added. With All past papers (or Past Papers off) the option is removed and the order returns to Group by topic; otherwise behaviour is unchanged. The order is saved with the session (`order: 'paper'`) and restored only while a single paper is chosen. Print layouts, solution options, saved selections and question IDs are unchanged from v0.62.

**Evidence.** `tests/test_papers_selection.py` covers the option appearing and disappearing, mixed-paper ordering, the print snapshot and reload. `tests/papers_print_browser.py` drives papers.html to a real PDF of Paper 1 in paper order (one per page with solutions, and condensed without). The PR, live checks on the owner site and both ADA roles, the recovery ZIP and the owner report outcome are in GitHub #110.

**Standing rule OPS-063.** At the end of every job, update HANDOFF.md and log the handoff and token usage to the GitHub issue before reporting done.

**Usage.** Measured from the per-call API usage records in this Claude Code session transcript (Claude Opus 5.5), up to the release commit: 2,034,262 tokens over 26 model calls, of which 1,974,683 were cache reads, 41,579 cache writes, 52 uncached input and 17,948 output. The final figure, through publication, is in GitHub #110 and the owner report.

<!-- LUISA-REPORT-HANDOFF v0.62 -->
**Release 0.62 · GitHub #107.** Past Papers includes June 2025 Paper 2 (Maths · 9MA0/02), Pure Mathematics 2, sat 12 June 2025 (2 hours). Its 15 original questions carry 3, 4, 2, 5, 7, 6, 4, 9, 8, 9, 11, 8, 3, 8 and 13 marks, totalling 100. Questions 1–5 are Easy, 6–10 Medium and 11–15 Difficult, following paper order. Papers now has six past papers with 62 questions and 450 marks, 554 Exam style questions and 8,068 Practice questions: 8,684 in total.

**Content.** Prompts are native HTML and KaTeX with the original wording, part labels, marks, bold emphasis and question-specific instructions. Figures 1–5 are vector crops of the source diagrams. Each question prints only its own official mark-scheme pages (5–41) as ordered vector crops, including alternatives, special cases, examiner notes and helpful diagrams. General marking pages 1–4 and the publisher page 42 are excluded. Every question was solved independently and agrees with the scheme. Source hashes, page ranges, crop bounds, mathematical checkpoints and chapter mappings are in `docs/evidence/v062-import-pure2.json`.

**Evidence and release.** Tests cover the paper dropdown, chapter filters, a whole paper added in source order that survives reload, all four print combinations as real PDFs and a mixed Paper 1/Paper 2 selection with overlapping question numbers. Earlier papers, saved IDs and v0.61 print layouts are unchanged. The reviewed PR, live manifests, recovery ZIP and owner-only report outcome belong in GitHub #107. Legacy Maths has 3,423 / 3,423 questions (100%) and 132 / 132 sections.

<!-- LUISA-REPORT-HANDOFF v0.61 -->
**Release 0.61 · GitHub #105.** Papers defaults to one question per page. Tick Condensed beneath Include worked solutions at the back to print without dedicated writing areas. Browser sessions saved with two questions per page now use the default. The existing assembled questions, source choices and answer preference still restore.

**Printed layout.** Question paper is the bold page title. The footer has one rule, page numbering and a shared local creation timestamp such as 20/11/26 6:30pm. Paper-wide source instructions are omitted from the printout. Question-specific instructions, dependent Practice Booklet context, solutions, mark schemes and hints retain their original content. Question images preserve their aspect ratio within eight lines of text. The question and its solution use the same compact heading with provenance and known marks.

**Evidence and release.** The print suite covers all four combinations, native PDFs, the timestamp and footer rule, larger figures, original prompts and solution matching. Keep owner offline printing and authenticated ADA roles working. The reviewed PR, live manifests, recovery ZIP and owner-only report outcome belong in GitHub #105. Legacy Maths has 3,423 / 3,423 questions (100%) and 132 / 132 sections.

<!-- LUISA-REPORT-HANDOFF v0.60 -->
**Release 0.60 · GitHub #103.** Papers uses Course → Book → Topics, with no separate skills picker. All 8,669 Edexcel questions resolve to the existing 62 chapters across eight books. The three pools contain 8,068 Practice questions, 554 Exam style booklet questions and 47 actual Past Papers questions. The past-paper dropdown uses catalogue IDs. Existing paper IDs, selection order and print settings survive migration. Old incompatible topic or skill restrictions reset with a notice.

**Printing.** Single-line headers show a bold question number and verified marks in square brackets. Mechanics Year 2 Chapter 7 Set B Gold totals 4 + 8 + 3 = 15 marks. Pure Year 1 Chapter 11 §11.3 Q7 uses a three-cell layout and totals 2 + 3 + 1 = 6 marks. Question images keep their proportions within six lines of text. One question per page, two per page and all questions without writing space remain available with or without solutions. Preserve original question and solution bodies, hints, provenance, continuation pages and past-paper-only timing.

**Evidence and release.** See `docs/evidence/v060-papers-mapping.json` for mapping coverage and the five explicit resolutions. Review shared print geometry independently before landing. Require green build, test and scan checks on the reviewed PR head, then verify actual Papers behaviour and release manifests for Cloudflare owner and both ADA roles. Verify owner offline operation, preserve accounts and credentials, follow recovery retention and submit the owner-only final SMTP report under FR-024. The live revision and release outcome belong in GitHub #103. Legacy Maths has 3,423 / 3,423 questions (100%) and 132 / 132 sections.

<!-- LUISA-REPORT-HANDOFF v0.59 -->
**Release 0.59 · GitHub #101.** Papers contains 8,669 Edexcel questions. Practice questions contains 8,068 entries; Exam bank contains 601, comprising 290 source-labelled exam-style booklet questions, 88 each Bronze/Silver/Gold and 47 actual questions from five June 2025 papers. The pilot covers Pure Mathematics 1, Statistics, Mechanics, Core Pure Mathematics 1 and Core Pure Mathematics 2, with 350 marks in total. Preserve exact original prompts, subparts, diagrams, question numbering and source labels. The original paper's working, rounding and gravity instructions accompany standalone questions. Question-specific official mark schemes retain alternatives and guidance as readable vector or high-resolution images; their image text is not searchable mathematics.

**Selection and printing.** Use the two source checkboxes, topics or skills, random/regenerated or manual selection, and a dynamic eligible-question count. Exam bank difficulty uses Bronze/Silver/Gold as Easy/Medium/Difficult; actual papers use original question order (first/last five for 15+ questions; thirds for shorter papers). Other question difficulty remains unknown. Choose one question per page, two normally, or condensed, with or without solutions. Long questions use readable continuation pages. Whole-question marks count once on the final continuation page, with a printed explanation. Suggested time is ceil(total marks × 5/6) minutes only for entirely actual-past-paper selections with known marks. Topic grouping is the default; selection order remains available.

**Mathematics and acceptance.** Eleven Core Pure 1 Chapter 4 slides explicitly define S/T notation using the original Greek roots and remove the spurious fourth cubic root. Both 24-page booklets and the alias are refreshed. Skill 1.01 Q23 working and its solution PDF are corrected. Independent mathematics, reveal/reset, unchanged-page pixel comparisons and reproduction checks pass. Per-paper source/math/visual checks and integrated six-mode printing are recorded in `docs/evidence/v059-import-*.json`; earlier UI/print/long-question acceptance is in `docs/evidence/v059-integration.json` and `v059-papers-print.json`. Do not replace source acceptance with a successful render. The original 2,475 practice payloads are unchanged.

**Release and continuation.** Build the owner and protected staff/student profiles from the reviewed merged revision. Verify Cloudflare and both ADA roles independently, including actual exam assets, printing, offline owner dependencies, logout and unauthenticated denial. Preserve the private account database and existing credentials. Final deployed revision, checks, recovery archive and owner SMTP acceptance are recorded in GitHub #101; a branch or push alone is not a live release. Keep only the latest five verified recovery ZIPs and the latest verified ADA release. Leave the Mac VPN and network unchanged. Physical iiyama confirmation and the parked network classification remain outstanding. The next owner assignment is pending after release completion. Exact provider token counters are unavailable. Legacy Maths: 3,423/3,423 questions (100%);132/132 sections.

<!-- LUISA-REPORT-HANDOFF v0.58 -->
**Release 0.58 · GitHub #99.** Papers contains 8,622 Edexcel questions: the existing 6,147 plus 2,475 from all 45 Maths Practice Booklets. Choose Luisa, Practice Booklets or both; retain random/regenerated and manual selection by topics or skills. Every imported question has independently checked worked solutions. All 726 source hints appear with solutions at the back. Preserve exact original prompts, subparts, diagrams and stable course/book/chapter/subchapter/question identifiers. The original PDFs are unchanged. When a printed answer or premise is inconsistent, preserve the question and explain the issue in its working. Five dependent questions include explicitly labelled original question context without hints or answers. Mathematics in source labels uses readable notation. Wide tables scroll within a keyboard-accessible question panel on mobile.

**Acceptance.** All 45 chapters received independent source, mathematical and figure review. The combined print audit checks all 2,475 imported questions for exact text, mathematics, image order, part labels, hints and loaded images; no clipping, overflow or pagination warnings remain. Original long-question regressions also pass. Eleven selection browser tests, six print browser tests, six catalogue integrity tests, five offline dependency tests and eight extraction regression tests pass. An actual 22-page PDF was inspected for tables, graphs, portrait images, context, long questions and hints. Normally print two questions per A4 page, allowing extra pages for long content. See docs/evidence/v058-papers-acceptance.json and per-chapter evidence. Native source/table fidelity and strict question-to-working joins must be preserved on future changes.

**Build and release.** The practice index and joined chapter JSON belong to all three profiles. Owner offline chapter packs include their practice questions, worked diagrams and recursive dependencies. The print window opens the cached same-origin paper-preview.html shell so formatting, fonts and diagrams remain available offline; reject a missing or signed-out shell before inserting content. Actual disconnected chapter selection, worked-graph printing and reload pass in Chromium. Build from the reviewed merged revision and verify Cloudflare owner plus authenticated ADA staff and pupil manifests separately. Preserve the private account database and existing credentials. Final deployed revision, live checks, recovery archive and owner SMTP acceptance are recorded in GitHub #99; a checked branch alone is not a live release. Do not use NordVPN on school premises. Keep only the latest five verified website ZIPs and the latest verified ADA release. Marks, difficulty, time filters and additional past-paper imports remain future work requiring genuine metadata. Physical iiyama acceptance and the parked network classification remain outstanding. Next owner assignment pending after this release completes.

<!-- LUISA-REPORT-HANDOFF v0.57 -->
**Release 0.57 · GitHub #97.** Papers is the fourth library tab on both hosts. Its question-level Edexcel catalogue contains 6,147 worked questions (Maths 3,353; Further Maths 2,794), excluding the reference table and 820 other-board questions. Reuse textbook-catalogue.json eligibility, including partial skills; do not infer eligibility from the course alone. Select topics or individual skills, a count and a random or manual selection. Print two questions per A4 page normally, with owner-approved extra space/pages for long questions, followed by matching worked solutions. Preserve original question IDs and use Source: Luisa <skill> Q<number>, with course/book context. Original content and diagrams remain authoritative. Marks, difficulty and time filters await genuine metadata; v0.58 will add Practice Booklet chapter/subchapter/question sources. Selection, browser and print evidence are recorded in #97. Eight selection browser tests and four print checks pass. All 271 long Edexcel prompts retain their exact question/solution content, image order and list markers across readable continuation pages; the remaining 5,876 fit the normal layout. Independent review is complete. Final deployment verification, revision and owner-email outcome belong in #97.

<!-- LUISA-REPORT-HANDOFF v0.56 -->
**Release 0.56 · GitHub #94.** The 62 teaching chapters have 2,969 slides, 1,500 A4 student pages and 1,507 worked pages. Both editions show a slide number in every teaching panel. Solution booklet downloads end in ` SOLUTIONS.pdf`. See docs/evidence/v056-booklets.json. On the smartboard, open a practice chapter through Resources and swipe between pages or tap a PDF destination. Physical iiyama verification is outstanding. The offline download toolbar retains the return routes for staff. Recent chapters keeps four resume positions in the owner browser and four per ADA teacher across devices. The admin title carries a password key. Its logo signs out of administration and opens the library. The contact directory uses GMT, counts successful sign-ins from migration and reports the latest authenticated session, including expiry. Preserve the independent teacher and admin cookies. IP and network labels are parked in #92. Create and verify each new website recovery ZIP before trimming the archive to five; leave other backup types alone. Production evidence and release-email status are recorded in #94.

<!-- LUISA-REPORT-HANDOFF v0.55 -->
**Release 0.55 · GitHub #86.** Mechanics Year 2 Chapter 5 has 21 revised exercise diagrams and an annotated overview. On slide 13 the applied push meets the particle from outside the plane and the acceleration has a superscript exponent. Slide 24 distinguishes the rope angle from the slope angle. Slide 28 marks the slope inclination θ. The classroom slides and both 14-page print editions use the same figures. Keep the force diagram on slide 15 concealed until the reveal. The public diagram and booklet hashes are in docs/evidence/v055-forces.json. Issue #86 records the host and print checks.

<!-- LUISA-REPORT-HANDOFF v0.54 -->
**Release 0.54 · GitHub #84.** Pure Year 2 Numerical Methods has 51 slides and two 26-page booklets. Slides 20–23 animate the four fixed-point constructions. The student booklet provides curves and grids for pupils to draw the construction. Slides 26–27 carry the fullscreen film and GeoGebra cubic. Slides 28–35 contain the tangent comparisons, derivation, fx-CG100 hint, worked cubic, rounding check and editable spreadsheet. The spreadsheet starts at zero. Selecting an estimate shows its formula and the preceding cells used. Keep the worked examples and spreadsheet formulas in the pupil booklet. Core Pure 2 chapter 6 pages 34, 66 and 67 carry the aligned answers and green formula families. Chapter 7 pages 2, 4 and 26 carry the teaching overview, circle-grid Plot reveal and wheel cutaway. Chapter 8 pages 29, 43 and 44 show the racing suspension and connected predator–prey survey. These chapters retain their existing slide counts. Eight booklet PDFs and their private reproduction copies were updated. Across Luisa there are 2,969 slides, 1,500 pupil booklet pages and 1,507 worked booklet pages. The old-to-new page map, print hashes and content checks are in docs/evidence/v054-teaching.json. Check the production revision and recovery outcome in issue #84.

<!-- LUISA-REPORT-HANDOFF v0.53 -->
**Release 0.53 · GitHub #82.** Core Pure 2 chapters 6–8 now include 82 exam-style questions and 163 independently revealed answers. The three student booklets and three worked booklets include the matching exercises and diagrams. Keep the complete printed prompts, part labels, marks, source diagrams and separate worked reveals. Chapter 6 contains 30 marked questions in 80 teaching slides, with 40 pages in each booklet. Chapter 7 contains 29 marked questions in 79 teaching slides, with 40 pages in each booklet. Chapter 8 contains 23 marked questions in 55 teaching slides, with 28 pages in each booklet. Across Luisa there are 3,018 teaching slides, 1,524 student booklet pages and 1,531 worked booklet pages. Source selection, mathematical corrections, artifact hashes and print checks are recorded in docs/evidence/v053-cp2.json. The production and recovery verification record belongs with GitHub issue #82.

<!-- LUISA-REPORT-HANDOFF v0.52 -->
**Release 0.52 · GitHub #80.** Core Pure Year 1 chapter 3, Series, now has 31 teaching slides. Slides 10–18 cover exercise 3A questions 2, 3, 4, 5, 9, 10, 11, 12 and 14. Slides 22–30 cover exercise 3B questions 4, 5, 7, 8, 9, 10, 11, 12 and 14. The existing worked extension is on slide 31. Keep each printed E and E/P prompt, its marks and the 33 individually owned answer covers with their matched SolutionBank working. In 3A 9(a) use +2k in the intermediate expansion. Each of the paired booklets has 16 pages. The teaching release now has 2,955 slides, 1,493 student booklet pages and 1,500 solution booklet pages. See docs/evidence/v052-series.json for the source inventory and acceptance checks. Verify the owner offline pack, both ADA roles and the Cloudflare owner manifest. Record the production revision and recovery check on GitHub #80.

<!-- LUISA-REPORT-HANDOFF v0.51 -->
**Release 0.51 · GitHub #78.** The three main library pages use Resources for the tab. The catalogue heading remains Teaching Resources. All teaching viewers use the page 19 answer-button typeface. Adjacent reveal covers share a height where the space permits, and the size of a cover must conceal the entire answer. Check both the untouched and revealed states. Data tables have cell borders. Cartesian sketches have axes and grid in the student booklet and a completed curve in solutions. In slides, use mathematical type, axis arrowheads and labels with enough space for the endpoint ticks. All existing chapter overviews use three topic-specific visual studies. Pure 1 has fourteen overview pages. The other five books have forty-one overview pages in forty chapters, including the two-part integration overview. Keep any source examples, notes, diagrams and answer controls on these pages. Keep every original exercise prompt, subpart, mark and supplied quantity when updating the slides or either booklet. Restore historic shortened wording against the supplied original. Check both the original question and its working when a removed condition changes what pupils must calculate.

**Pure 1 Chapter 14.** Pages 6, 9, 11–13, 18, 20, 39 and 45 have revised sketches. Page 8 uses the original interactive GeoGebra material with an adjacent link and larger function labels. The embedded slider belongs to the external material. Page 22 teaches the equivalence of exponential and logarithmic form. Page 28 uses base 10 and the example 2³ = 8, then retains each line of the derivation. Page 45 includes the original two prompts. Use the matching student and solution panels for the linear models and log-transformed data on pages 49–54. The report reproduces this handoff in full. Verify all three role-specific manifests at release and record the production revision and backup in GitHub #78.

**Historic questions and printed errata.** The source comparison covered all six books. Use the original question or exact accessible crop when the source notation cannot be transcribed reliably. Preserve the original statement where a printed target is wrong and give the correction in the worked solution. For example, Core Pure 1 chapter 9 page 26 retains the supplied point and plane and shows why the point lies outside it. Pure 2 chapter 9 pages 21, 77 and 87 distinguish printed equations from the corrected result. Applied 2 chapter 8 page 26 includes the original PowerPoint note supplying the missing mass. In mechanics, the supplied support positions, segment lengths and force angles belong on the question diagram.

**Verification and reproduction.** The browser checks visit all 2,947 teaching slides across all 62 chapters and exercise Reveal All and Reset. Review individual source and layout checks in docs/evidence/v051-teaching.json and the booklet and alias records in docs/evidence/v051-booklets.json. Rebuild the two booklets together from the same teaching sources, and verify their protected and owner URLs and offline dependencies. The 62 student booklets contain 1,489 pages and the 62 solution booklets contain 1,496. Check every issued page with MuPDF and Apple Quartz. The private LaTeX reproduction wrappers use the issued PDF pages as artwork. Use the archived authoring recipe and teaching source when editing individual exercises. The archive and release record are tied to the deployed Git revision in GitHub issue #78.

**Release 0.50 handoff**
**Release 0.50 · Issues #74, #75 and #76.** The three host profiles share the six subject-coloured book spines and the new GeoGebra link. The protected pupil profile retains its existing access rules. The GeoGebra diagram on Chapter 14 page 8 requires an internet connection; the Cloudflare offline pack and both printed booklets use the diagram’s static preview.

**Pure Mathematics Year 1, Chapter 14.** Pages 4 and 27 reveal individual table entries and red coordinates, then draw the curve after the final distinct point. Page 5 provides independent curve selectors for both existing comparisons. Page 8 embeds the specified GeoGebra material. Pages 16 and 21 have fully bordered tables with individual covers. Pages 17, 18, 31, 32 and 33 have matched-height covers; 31 and 33 retain the requested line break and prompts. Page 28 has four independent law covers and a stepped change-of-base derivation. Page 34 restores the two owner-supplied questions verbatim with separate Answer and Proof covers. Page 39 reveals 3a, 3b, 4a, 4b, Extension, Graph. Pages 46–49 demonstrate doubling, the Richter amplitude comparison, log–log coordinates and the two linearised models. Keep the source Richter chart, teacher-paced Reveal/Space and Reset. Propagate the revised teaching into the 27-page student and solution booklets, update the public alias, private owner copies and compiled reproduction assets. Preserve the other panels and the licensed textbook file.

The first table remains on page 4 and the two comparison plots remain with their source prompts on page 5. The original earthquake illustration on page 47 is a Richter chart. Its tenfold comparison is explicitly wave amplitude at comparable distances. Generated booklets each contain 54 source slides in 27 pages. For another revision, regenerate from the Chapter 14 teaching assets and compare both PDF flavours, the alias, owner copies, print wrappers and slide interactions. The PDF hashes and two-renderer checks are in docs/evidence/v050-chapter14.json. GitHub #76 holds the numbered requirements and live verification evidence. The versioned Luisa Report carries this handoff in full.

**Next action.** Next owner assignment pending.

**Release 0.48, issue #72.** The three library pages show the calculator, cloud download and quiet version link on Cloudflare and for ADA teachers. The ADA teacher exit button identifies the signed-in teacher in its tooltip and accessible name. Pupils see their identifier and the generic exit button. The version is stamped from release metadata at build time. Teaching Resources subject-colour treatments await owner selection.

**Release 0.47, issue #70.** Teaching slides display the booklet page title and a compact current-page / total selector. The logo returns to Teaching Resources, where ADA users can sign out. The CG100 calculator on Cloudflare and ADA teacher slides opens in a separate window requesting one quarter of the available screen width and its full height. Check chapter navigation, resource menus, page numbers, and the role-specific calculator in the three build profiles.

**Release 0.46, issue #68.** All teaching slides use a single-line banner with the linked Luisa logo, slide selector, chapter title and current page number before the gold reveal icon, reset, full screen and resources. Check chapter navigation, resource menus, page numbers, and the authenticated account controls in the three build profiles.

**Private ADA directory, issue #64.** Apply init-db before switching the gateway. It creates separate student and teacher first-name tables. Populate them privately and preserve authentication state. The administrator can edit first names via Manage and sort both directories. Logo and sign-out match ADA's course toolbar. Admin login selects the administrator on the server. The live password-only form asks for the password only (issue #66). Copy a temporary password on its issue screen for private delivery. For a previously issued password, use a verified original private invitation or issue a replacement. Both course editions remain v0.45.

**Private ADA admin update, issue #62.** Students and Teachers have separate directories. Manage on a row applies to that account only. Teacher resets, forced changes, suspension and session revocation cover every device for the selected teacher. Deploy the reviewed gateway package against the existing private database and environment. No schema migration or account provisioning is required. Keep both course manifests at their existing release. Verify database continuity and the gateway revision separately. The owner-specified class correction was applied in private storage.

**Release 0.45, issue #60.** The private admin page creates teachers by acronym and displays a generated first password for manual delivery. Add the nullable staff timestamp via init-db before restarting. Record only successful authentication. Existing teacher sign-ins before this release have no historical timestamps. The authorised pupil mail merge has since been sent.

**Release 0.44 amendment, issue #58.** ADA logout controls POST with the session token and return directly to sign-in. A successful pupil login invalidates the earlier session immediately. Visible pupil pages check for displacement every ten seconds and when restored or refocused. These checks do not renew a session or record activity. Teachers retain independent device sessions. The owner requested v0.44 on both hosts for this amendment. Verify both live manifests by revision.

**Release 0.44, issue #56.** The private pupil_preview_logins table maps a fictional pupil username to a dedicated five-digit roster row. Apply init-db before activation. Provision both rows in one transaction outside the repository. Reserve a distinct username and unused synthetic number. Real pupils use their school email, staff use their usual credentials and the preview uses the bare alias. Store merge greetings and destinations privately outside ADA. The real pupil mailing awaits explicit owner approval.

**Release 0.43, issue #54.** Staff and pupils authenticate through the same ADA gateway. Deploy a private staff and pupil artifact from the same revision. Staff see the 62 original licensed textbook chapters in By skill, By textbook, Teaching Resources and lessons. Their Offline link opens the Cloudflare offline facility in a new tab. The three Cloudflare and ADA teacher pages share Offline, CG100 and the current version controls. ADA uses the owner-selected compact exit icon with keyboard focus, an accessible name and tooltip. The username appears separately. Verify a direct chapter URL as staff, pupil and guest, and verify all three edition manifests.

**Release 0.42.** The three library pages use one compact row. The logo is at the left, followed directly by By skill, By textbook and Teaching Resources. The separate wordmark and tagline have been removed. Actions occupy the right side. On narrower screens the toolbar scrolls horizontally beside the logo. Offline downloads and Sign out use shared 14px link styles across views. Verify horizontal access and typography on each edition. Issue #52 records NAV-042 and its release evidence.

**Release 0.41.** The three library views share left-aligned By skill, By textbook and Teaching Resources links in that order. Each page has the same top-left logo. The By skill display controls align right; Cloudflare places the development version link last and ADA places account sign-out there. The teaching catalogue retains its established URL. Verify the three entry points in both edition manifests and at phone and desktop widths. Issue #50 records the requirements and live release evidence.

**Release 0.40.** Cloudflare serves the owner library with textbook chapters, development navigation and offline packs. ADA serves the protected student edition at the main college address under /AL/. Build and verify each manifest independently with scripts/luisa.py build and check-artifact using the owner or student profile. Both editions now omit the Teaching chapters introduction and provide named topic, skill and solution print downloads. Running headers preserve the printed skill identifiers in Further and Standard Maths. Where a combined topic page covers several skills, the header identifies its first question. The original print URLs continue to work.

A new pupil login replaces their previous session. Staff can use multiple devices and sign in with an acronym or full college address. Staff have course access. The separate admin login lists staff accounts and manages pupil accounts. Signed-in ADA pages include sign-out. ADA omits version badges, development links, textbook extracts and offline packs. Deploy behind the authenticated ADA gateway and preserve the private SQLite database, credentials and authenticated rollback release. The college proxy retention period and off-host rebuild policy remain unconfirmed. Private owner backups have been restored and checked. GitHub and the Cloudflare owner content remain publicly accessible by owner choice. Never commit production identities, passwords, slips or backups.

The live roster stores class and school number only. Administration shows each pupil’s latest successful sign-in in UK local time. Initial credentials work once and must be replaced before opening content. Minimum password length is eight characters. Admin remains separate from staff course accounts. The owner instructed that no teacher email be sent for this release. Verified the live ADA gateway using two independent browser contexts, all three Polynomials PDF downloads, protected URLs, nested sign-out, and separate staff and pupil access. A restored off-host snapshot displayed 15 staff and 38 pupils in the private admin workflow. The GitHub release record on issue #48 and PR #49 tracks the final host manifests. Refresh this handoff and the requirements register with each release.
<!-- END LUISA-REPORT-HANDOFF -->

## Historical release notes

## v0.38 solution covers

Every chapter solution booklet has a red Solutions subtitle beneath its cover title. The 62 updated PDF fingerprints are in docs/evidence/v038-solutions.json. The owner collection and its PDF-backed LaTeX assets use these same files.

## v0.37 chapter solutions

The owner selected v0.37 for the solutions release. All 62 chapter PDFs match the repaired acceptance hashes across 1,496 pages. Teaching chapters, player controls, textbook topics, Development progress and offline chapter downloads use the corresponding solution resources. Both live deployments and all 62 solution hashes were verified. The release evidence is in docs/evidence/v037-release.json. Physical-device checks remain with the owner.

## Historical v0.36 integration assignment

Read [V036-SOLUTIONS-INTEGRATION.md](docs/handoff/V036-SOLUTIONS-INTEGRATION.md). The owner now authorises verified solution PDFs in teaching chapters, relevant View by textbook topics and Development progress. This supersedes earlier private-only instructions for solution PDFs; LaTeX originals and source/audit materials remain private. Every slide change must refresh both student and solution booklets and their reproduction bundles. All 62 local solution bundles are complete and repaired for Apple Quartz; website integration is pending. v0.36 already exists, so follow the handoff version/cache instructions rather than treating it as a fresh unpublished release.


Updated 9 November 2026. Read AGENTS.md and docs/agentic/LEAD-RULES.md, then the task-specific documents below.

## Booklet requirements and next solution task

- [BOOKLET-STANDARD.md](docs/handoff/BOOKLET-STANDARD.md) is the consolidated design, filename, document-location and selective replacement specification. Apply BKT-035, BKT-036-COVER, BKT-036-SOLUTIONS, BKT-036-ORIGINALS and BKT-036-RETENTION from the canonical requirement register.
- [SOLUTIONS-NEXT-AGENT.md](docs/handoff/SOLUTIONS-NEXT-AGENT.md) is the continuation brief requested for Astra with medium reasoning. It records prototype failures, regression cases and acceptance checks.
- The private workspace map resolves machine-specific paths. Final student copies are in `../Students Handout/`; private solution copies belong in `../Student Handout Solutions/`. Each collection has `_Latex original/<Book>/` reproduction bundles and the same eight book folders.
- The owner requires selective latest-only replacement. After a replacement chapter bundle is verified, install it at its canonical paths and delete that chapter's superseded generated PDF/LaTeX variants and obsolete assets. Preserve other chapters, original source materials and required current aliases/assets. The standard defines the full scope.

## Verified student baseline

Luisa v0.36 student booklets were published on Cloudflare and ADA at `41d724dcdfa2acbe21b8b5f622bf2488de16d773`. Both live manifests matched all 7,811 files and 326 fetched resources per host. Saved v0.35 downloads updated to v0.36 and reopened offline. The recovery archive was verified, ADA's prior release removed after verification, and the final HTML Luisa Report was accepted by SMTP on 8 November 2026 at 22:01 UTC.

All 62 student booklets, 2,947 teaching panels and 1,489 A4 pages are the reference set. The coloured first panels were independently checked with white 36pt Georgia Bold titles. Later teaching content and owner copies were verified. The 62 student PDF-backed LaTeX reproduction originals compiled successfully. Evidence is docs/evidence/v036-booklets.json and docs/evidence/v036-acceptance.json. Physical print/device checks remain with the owner.

## Historical private solution status

The owner stopped solution work on 8 November and requested completion with another model. Existing private solution PDFs and their LaTeX sources remain unfinished drafts with known defects. Their counts and successful renders do not establish acceptance. The next agent can resume under the owner's solution-completion instruction using the dedicated brief.

The private stop record is `../materials/build/output/v035-final/SOLUTIONS-STOPPED-CHECKPOINT.json`. Candidate authoring scripts live in `../materials/build/scripts/v035-final/`. They require inspection and correction. The latest per-field prototype stopped on Statistics Year 1 Chapter 2 slide 37 because hidden black text beneath an opaque student cover was misclassified as a caption. Explicit ownership also missed geometrically masked working. The brief records these issues and the PDF containment trial.

Keep source/output fingerprints tied to the material actually checked. For scoped regeneration, preserve unselected entries and mark changed unselected chapters stale. Resume from verified source and per-chapter evidence before replacing private drafts.

All release and development reports begin with a visible Luisa website link. Use `./` on website pages to preserve the ADA prefix.

Legacy Maths questions are 3,423 / 3,423 (100%), with 132 / 132 sections.

# v0.35 booklet standard

BKT-035 applies to all current and future student booklets. Use descriptive BookYear_ChNN_Chapter_Title.pdf filenames, no Luisa in panel headers, and a Data Collection style first title panel. Its banner names Subject Year N Chapter N - Topic. Later panels preserve their layout and teaching content. Keep the eight book folders of matching owner copies current. Evidence is docs/evidence/v035-booklets.json.

# Luisa handoff

## v0.34 teaching release

Start with docs/evidence/v034-acceptance.json. It records the 62 deck and booklet fingerprints, all 94 named original slide references, and the mapping after removing six Statistics course maps and the final Probability extension. The catalogue contains 2,947 slides and 1,489 A4 booklet pages. Statistics accounts for 463 slides and 234 pages.

All live teaching implementations share lesson-controls.js and lesson-touch.js. Source answer elements have explicit owners. Exercise identifiers, source animation targets and meaningful print-only captions survive separate screen and booklet rendering. The linked STEP sketch and Exercise 12J solution PDFs are included in the Pure Year 1 Chapter 12 offline pack. Private v034 authoring and review outputs are in the established materials build directories. Booklet generation uses the same origin as the slide viewer so the printed mathematics uses the supplied fonts.

Validate the chapter report with python3 scripts/report_chapters.py development-progress.html release-report-0.34.html. The page counts and accepted hashes come from the release evidence. Run python3 scripts/luisa.py gate and require the three current-head CI checks before landing. Verify the production manifests, chapter resources, navigation and the saved v0.33 to v0.34 transition on both hosts. The private v034 release directory holds host verification, recovery and final SMTP submission records. Physical Magic Mouse Chrome/Safari and iPad confirmation remain open.

Legacy Maths questions are 3,423 / 3,423 (100%), with 132 / 132 sections.

## v0.33 chapter reports
Statistics acceptance covers both years (470 slides, 10 booklets, 236 printed pages). The artifact fingerprints and review scope are in docs/evidence/v033-statistics.json. After editing any signed deck or booklet, review the changed material before renewing its acceptance.
Run `python3 scripts/report_chapters.py development-progress.html release-report-0.33.html` after any chapter update, using the new report filename for subsequent releases. Link every available resource independently of final acceptance. Student booklet, source textbook and practice chapter are distinct resources. Render checks alone do not qualify a chapter for final acceptance.

## v0.31 teaching navigation
Implement WEB-031 and SLD-031 in every future teaching player and chapter listing. All seven current players load lesson-touch.js against the slide region and delegate gestures to the existing controls. Standard Maths practice PDFs use the teaching catalogue practice field. Physical smartboard and iPad checks remain with the owner.

## v0.30 Statistics release
Track STA-030, SLD-030, WEB-030 and PUB-030. Slide 55 uses original covers 1, 4, 2, 3, each labelled ?. Include the outstanding Statistics chapters for both years. All ten Statistics chapters have slides and two-up booklets. Source-matched cover labels and explicit exercise overrides take precedence. Full visual and print acceptance for the newly uploaded chapters remains outstanding. See the release report and private v030 browser/print evidence. Verify both hosts and recovery archive before the final email.

## v0.29 release handoff
Statistics Year 1 Chapter 2 uses the replacement 90-slide source and a 45-page student booklet. Slide 68 requires separate Midpoints, Mean and Standard deviation controls. Maintain these in both outputs. See docs/evidence/v029-acceptance.json.
Every release must name implemented requirement IDs on Development progress, link to the chronological version log and include direct links to affected practice booklets alongside the teaching resources. Publish and verify Cloudflare and ADA, finish the recovery archive and handoff, then send the full HTML Luisa Report as the final release action. Only the private SMTP outcome record follows sending. Physical iPad confirmation is with the owner.
Updated: 2026-11-05. Read AGENTS.md and docs/agentic/LEAD-RULES.md first.

## Completed v0.28 — issue #18 / PR #19
Branch task/v028-library-offline. Owner clarified Practice Chapter means the existing chapter-folder PDFs, not generated Print topic PDFs. All 45 Maths chapters now have practice resources; Further Maths retains textbook buttons. Missing Statistics/Moments textbook extracts restored. Offline inventory includes print PDFs and supplementary skill packs; new files require refreshing downloads. Toolbar focused fullscreen and Edexcel-only Further topic print implemented. Browser tests under / and /AL/ pass; physical iPad not newly tested. See docs/evidence/v028-acceptance.json. Published revision e87f9b3662db322872ac5c569668161290f97e13 verified on both Cloudflare and ADA: all 6,941 manifest entries match, with 92 changed/core resources fetched and hash-checked per host. Clean build/test/scan and independent review passed. Recovery ZIP saved; only latest release retained on ADA. See docs/evidence/v028-release.json. Final HTML report submitted through the configured SMTP adapter; private send evidence records acceptance. Work complete; wait for owner instructions.

## Mandatory release email — all future agents
FR-024 is a standing owner requirement, reaffirmed 2026-11-05. Every published release must end with the full HTML report emailed using the existing private SMTP adapter, unless explicitly deferred by the owner. Do not interpret a new chat as removal of authorisation. Read docs/handoff/RELEASE-EMAIL.md for the command, content, checks and failure handling. The private WORKSPACE.json mailSender resolves the configured account; no Apple Mail or unlocked desktop is required. Public v0.27 is unchanged by this documentation task. Delivery for v0.25–v0.27 has not been verified here; do not infer sent status from publication.

## Completed v0.27 scope
Issue #15; PRs #16 and #17 squash-merged. Final checked release a9f0365e0893fda9d8185b8bca686c23d9e1a976 is live on Cloudflare and ADA. Both6867-entry manifests and241 fetched resources per host match the same artifact. All96 replacement Pure Year2 chapter9 originals are delivered as102 teaching panels,51 matching booklet pages and42 textbook pages. Title is Differentiation; overlapping old variants are superseded. Source/maths/visual/interaction/print acceptance: docs/evidence/v027-acceptance.json. Release: docs/evidence/v027-release.json.

Installed-app documents have visible Back controls. Live offline booklet/textbook rendering, page navigation, exact slide/reveal restoration, return to originating downloads page and offline reload pass on both hosts in desktop Chromium standalone emulation. This is not physical iPad acceptance. ADA initially served .mjs with an invalid module MIME type; unchanged PDF.js modules now use .js, and both live module headers are checked.

Owner requires only the latest Luisa release on ADA. Superseded release directories and old source/deployment archives were removed. No historical Luisa backup remains there; recovery stays outside ADA in Cloudflare and OneDrive. OPS-002/DEVOPS record capacity checks, staging, directory activation and cleanup after verification. Unrelated server files preserved. Usage phase boundaries, source usage and detailed acceptance remain privately in materials/build/output/v027; phase allocation is approximate and includes cached context, not an exact provider bill. Work complete; wait for the next owner task. No schedules.

## Completed v0.26 scope
Issue #13; PR #14 squash-merged as272f74c127a749a4127e8925d162664818d4ce42. Current follow-up branch task/13-v026-release-evidence. Owner authorised checked publication; on 2026-11-03 explicitly paused ADA work and skipped its v0.26 copy because ADA is down. Retry ADA with v0.27. All11 requested chapters are locally agent accepted: Pure Year2 10/11/12, Mechanics Year2 6/7/8, Core Pure1 3/5, Core Pure2 6/7/8. Total571 displayed slides,289 booklet pages,260 textbook pages. See docs/evidence/v026-chapters.json. Cloudflare production v0.26 verified:6644 manifest entries match and437 actual resources hash-checked. ADA v0.26 is skipped by explicit owner instruction; no ADA deployment is claimed. See docs/evidence/v026-release.json.

Owner approved splitting Integration original82 into7 readable panels, with matching board/booklet numbering.110 originals become116 displayed slides. Vectors22-slide recheck restores intermediate steps and diagrams. All chapter-specific source/math/visual/interaction/print and both-library checks pass; private detailed evidence and source usage stay in OneDrive materials/build/output/v026.

PWA-001 deferral is explicitly superseded. Owner confirms Vectors works offline on iPad Pro12.9 fifth generation, reported iPadOS27.2. One-action Download all implemented; filter/busy/failure/retry, stale-catalogue and root/AL offline checks pass. Root/AL worker termination, replacement identity, old offline resources and retry pass. Final real-library Download all saves62 packs at both prefixes and all11 requested chapter resources open offline. Testing evidence is recorded in docs/evidence/v026-offline-preview.json. Physical testing of other platforms and the final bulk-download build remains unclaimed. Existing Pure1 chapters10/12 missing dependencies remain explicitly unavailable.

The v0.26 ADA pause was superseded by the owner’s v0.27 dual-host instruction. v0.26 itself remains historically skipped; its delivered chapters are included in v0.27. No automatic schedules.

## Completed v0.25 scope
Issue #10: owner authorised v0.25 conversion of Pure Year 2 chapters 6 and 7 and Core Pure 1 chapters 1 and 4, with teaching slides, two-up student booklets and linked textbook chapters. Publication to Cloudflare and ADA is explicitly authorised after acceptance and repository checks. PR #11 was squash-merged. v0.25 is live on Cloudflare and ADA at checked release revision eb8cbb43fa6e822f9b93797f29061213f732159e. Both manifests and 96 fetched resources per host match the same 6,235-file artifact. See docs/evidence/v025-release.json. This documentation follow-up records that verified release; inspect the live manifest for any later documentation-only revision.

All four chapters are agent accepted: Pure Year 2 chapters 6/7 have 46/53 slides and 23/27 booklet pages; Core Pure 1 chapters 1/4 have 41/48 slides and 21/24 booklet pages. All 188 source slides and 95 booklet pages received source/maths/visual/print review, with independent review and resolved findings. Three viewport sizes, each individual answer/cover, actual Space ordering and Reset were checked. All 88 extracted textbook pages match the original printed content. Both libraries and viewer resource links work below a non-root prefix; the library return preserves the chosen chapter. See docs/evidence/v025-chapters.json. Owner acceptance is not claimed.

The four original decks and both textbooks are readable after OneDrive restoration. Private authoring inputs, scripts, per-slide/page evidence and usage remain in the OneDrive materials build folder. The gate passed 158 requirements, 122 catalogue destinations and 13 tooling tests; current-head remote build/test/scan passed before squash merge. The release was rebuilt cleanly from the merged revision. Cloudflare was verified first, then the same artifact was staged, fully hashed, copied to ADA and verified online. The prior ADA artifact and recovery copy were verified against all 6,155 prior manifest entries. No credentials were created or expanded.

OPS-008 records the owner-reaffirmed requirement to keep the Mac awake during active work with bounded temporary assertions, verified and released when work stops. Do not let idle locking interrupt development; do not bypass a manual lock or change persistent password/security settings.

PR #9 was merged externally by the owner before v0.25; it only added requirements documentation. Its deferral is now superseded by the explicit v0.26 owner instruction.

Usage counters are available for this chat, including cached input. Earlier activities interleaved conversion, checking and shared implementation, so an exact retrospective phase breakdown must not be invented. Private usage evidence records the available boundaries.

## Foundation record
- Repository: https://github.com/vyr66mbzmh-debug/Luisa ; same history and repository ID, local origin updated.
- Foundation PR #3 merged; production manifest verified revision 358d1be, version 0.24, clean. Issue #1 closed; roadmap #2 tracks future scope. A small evidence-record PR follows; inspect current main/live manifest for its exact revision.
- Canonical register: docs/requirements/register.json (158 requirements); generated REQUIREMENTS.md beside it. Historical assertions are not fresh acceptance.
- Main protection: PR, build/test/scan, up-to-date branches, linear history and no bypass; squash merge only. Secret Protection and push protection enabled.
- Cloudflare production: python3 scripts/luisa.py gate, output dist, PYTHON_VERSION=3.12.8. Renamed-repository previews succeeded. Verify each merged revision online.
- Development project: https://github.com/users/vyr66mbzmh-debug/projects/1 (owner access); Status/Priority/PR/Wave fields. Built-in project workflows, no new token.
- Local gate and CI passed: 156 requirements, 110 catalogue destinations, 9 tooling tests, 6155 packaged public files. This is infrastructure evidence, not renewed content acceptance.
- No new chapter work, schedules, paid services or credentials in this setup.

## ADA is a required release target
Every new published website version must also be copied to ADA from the same checked static artifact. Use the established web server; no Python server or SSH tunnel. Keep internal SSH/target details in private WORKSPACE.json. Verify the configured URL prefix, logo, CSS, libraries, teaching slides and PDFs live; record both hosts' revision/version before declaring release complete. See docs/DEVOPS.md.

## PWA requirement history (superseded deferral)
PWA-001 restores the owner’s original installable/offline app requirement, now explicitly covering Apple (iOS/iPadOS/macOS), Windows and Android systems, including the actual iiyama smartboard. See register.json for acceptance criteria and ROADMAP.md for future work. Implementation and partial verification are recorded under PWA-001; other physical devices remain unverified. Owner explicitly prohibited changes to live v0.24 or another publication for this documentation task. PR #9 was merged externally before this task; its implementation is now authorised for v0.26.

## Start next session
1. Inspect git status, git worktree list, open PRs and remote main. Preserve unfinished owner work; do not force reset.
2. Read assigned issue and relevant requirement IDs only. docs/handoff/START-HERE.md has the new-chat prompt.
3. Use one issue/branch/PR, targeted checks, then full gate and risk review. Verify live manifest and actual changed links after automatic deployment.
4. Record usage with scripts/usage.py, update evidence and this handoff. GitHub CLI is absent on the original machine; signed-in UI was used, while connector is read-only. Do not widen access silently.

## Relevant files and inputs
- docs/ARCHITECTURE.md, docs/TWELVE-FACTOR.md, docs/DEVOPS.md.
- docs/ROADMAP.md: remaining availability and deferred features; docs/ACCEPTANCE.md: source/maths/visual/interaction/print evidence.
- docs/OWNER-ACTIONS.md: verified controls and remaining portability boundaries.
- Private LUISA_STATE_DIR/WORKSPACE.json: original machine paths, authoring/mail locations; usage.jsonl is private.
- OneDrive can dehydrate both assets and Git blobs. Use a temporary clone outside OneDrive for full validation if needed; preserve the canonical master and uncommitted overlays.

## Baseline and boundaries
Legacy Maths questions: 3423/3423 (100%); sections 132/132, separate from expanded indexes and teaching progress. Full fresh acceptance is not inferred from those totals.
The public clone serves existing outputs. Original decks/books and historical authoring toolchain are private external inputs; new content needs targeted source access. Full chapter-authoring portability remains a follow-up.

### v0.32
Use each chapter’s catalogue resources for the first column of development progress. Keep mouse drag and touch swipe navigation consistent. Check slide 26’s grouped median-rule reveal and slide 28’s nine independent answer positions against the printed student booklet. Only mark Statistics chapters checked after full source, interaction, visual and print acceptance. Keep the final Luisa Report and disable the separate Cloudflare deployment email only.
