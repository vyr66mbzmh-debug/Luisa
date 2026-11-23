## Luisa v0.73

- Tooling: release scripts in scripts/release/ and the past-paper import pipeline in scripts/import/ (reference set: the v0.72 Sample papers), each with a README; numbered runbook in docs/agentic/RELEASE-RUNBOOK.md; quick start for any AI agent at the top of AGENTS.md.
- Privacy: `python3 scripts/luisa.py privacy` (in the gate) blocks personal paths, private hosts and addresses, stray emails and owner source PDFs; legacy lesson files no longer record a personal path.
- Environment: `python3 scripts/bootstrap.py` (pinned, in the private state folder) and `python3 scripts/luisa.py doctor` (PASS/MISSING with the human action).
- Reports: exactly one handoff in every form, headed with the release.json version; the separate short handoff paragraph is removed; HANDOFF.md holds only the current release block (history in docs/handoff/HISTORY.md).
- Releases are complete only when `scripts/release/finish.py complete` passes (HANDOFF.md, register, issue evidence, token log with its source, SMTP record).
- No user-visible feature changes.

## Luisa v0.72

- Papers: the five Edexcel Sample Assessment Material papers with their official mark schemes: 9MA0/01 Pure Mathematics 1, 9MA0/02 Pure Mathematics 2, 9MA0/03 Statistics and Mechanics (one combined paper), 9FM0/01 Core Pure Mathematics 1 and 9FM0/02 Core Pure Mathematics 2. That is 57 questions and 450 marks.
- The Sample papers have no date and are listed after every dated paper, ordered by code.
- No 2022 paper was added: the June 2022 folder holds exact copies of the Summer 2023 papers.
- Papers now has 44 past papers (444 questions, 3,450 marks). This completes the three-release import of the remaining past papers; the summary is on GitHub #124.

## Luisa v0.71

- Papers: twelve Edexcel papers with their official mark schemes. October 2020: 9MA0/01 Pure Mathematics 1, 9MA0/02 Pure Mathematics 2, 9MA0/31 Statistics, 9MA0/32 Mechanics, 9FM0/01 Core Pure Mathematics 1 and 9FM0/02 Core Pure Mathematics 2. October 2021: 9MA0/01, 9MA0/02, 9MA0/31 and 9MA0/32. November 2021: 9FM0/01 and 9FM0/02. That is 115 questions and 900 marks.
- The undated Core Pure papers (October 2020 and November 2021) follow the official mark scheme series and are ordered by series in the Past Papers list.
- Fix: June 2019 9MA0/01 Q3's worked solution no longer ends with an empty scheme header row.
- Papers now has 39 past papers (387 questions, 3,000 marks). This is release 2 of 3 for the remaining past papers; the sample papers and any genuine 2022 material (v0.72) follow.

## Luisa v0.70

- Papers: nine Edexcel papers with their official mark schemes. June 2019: 9MA0/01 Pure Mathematics 1, 9MA0/02 Pure Mathematics 2, 9MA0/31 Statistics, 9MA0/32 Mechanics, 9FM0/01 Core Pure Mathematics 1 and 9FM0/02 Core Pure Mathematics 2. June 2018: 9MA0/01 Pure Mathematics 1, 9MA0/02 Pure Mathematics 2 and 9MA0/03 Statistics and Mechanics (one combined paper). That is 92 questions and 750 marks.
- Papers now has 27 past papers (272 questions, 2,100 marks). This is release 1 of 3 for the remaining past papers; the 2020/2021 papers (v0.71) and the sample papers (v0.72) follow.

## Luisa v0.69

- Papers: six June 2023 Edexcel papers with their official mark schemes: 9MA0/01 Pure Mathematics 1, 9MA0/02 Pure Mathematics 2, 9MA0/31 Statistics, 9MA0/32 Mechanics, 9FM0/01 Core Pure Mathematics 1 and 9FM0/02 Core Pure Mathematics 2. That is 59 questions and 450 marks in original wording with faithful figures, chapter and skill mappings, paper-order difficulty and per-question evidence (docs/evidence/v069-import-june2023.json).
- Papers now has 18 past papers (180 questions, 1,350 marks).

## Luisa v0.68

- Papers: the specific past paper dropdown lists only papers with at least one question in the selected Course and Book; with Course and Book on All every paper is listed. A chosen paper that is no longer listed after a Course or Book change (or on restore) resets to All past papers.
- Papers: Past paper, Difficulty, Course and Book dropdowns on anything other than All get an active style (Luisa navy border, pale-blue tint, semibold text; WCAG AA). Screen only.
- Papers: while the Past Papers tickbox is unticked the paper dropdown is disabled, visibly greyed out, reset to All and never filters; a saved selection in that state restores the same way.

## Luisa v0.67

- Teacher-only exam paper: one Print choice — Questions only (default), Mark scheme only, Questions and mark scheme. The scheme section follows the paper, takes each question's paired official scheme with all continuations (past papers) or its worked solution (practice and exam-style), heads each "Question N", starts with a title line naming the exam and numbers its own pages "Mark scheme page x of y". Mark scheme only has no front page and no lined pages.
- Timed generation tolerance is ±2 minutes (was ±1).
- New three-paragraph default instructions; the Mechanics g paragraph is still added automatically. The Date field defaults to today in Europe/London ("Sunday 22nd November", ordinal superscripted when printed) and can be cleared.
- Removed builder notes: the "Prints the paper above … no solutions" help, the g instruction note, the "questions without marks … were left out" comment and "· g = 9.8 line included".

## Luisa v0.66

- Teacher-only exam paper: generate a paper to a target time from the chosen topics (presets 32 and 60 minutes, or any whole number of minutes). Time is 6 minutes per 5 marks, rounded down, and lands within one minute of the target; otherwise Luisa reports the closest paper and why.
- Exam papers are ordered easy first (first 20% of marks) and difficult last (last 20%), with a varied middle. Move up/Move down and Order by difficulty are available; a warning shows when a manual order breaks the rule.
- Exam paper questions are headed "Question N". The front page uses smaller, LaTeX-style Computer Modern type and no longer prints the course map; the Regenerate course map control is gone.

## Luisa v0.65

- Sub-question marks are bold bracketed numbers, such as (4), right-aligned in the margin on the last line of the part they score, on screen and in every print layout. Question totals stay on the heading line.
- One paper-time rule: 6 minutes per 5 marks, rounded down (54 marks: 64 minutes). The Papers summary shows it for any selection with a complete mark total.
- Teacher-only exam paper in Papers (owner and ADA staff): an editable front page, one question per two lined pages, question and paper totals, page numbers only and no solutions. The pupil edition omits and denies it.

## Luisa v0.64

- Add the six June 2024 Edexcel papers to Past Papers: 9MA0/01 Pure Mathematics 1, 9MA0/02 Pure Mathematics 2, 9MA0/31 Statistics, 9MA0/32 Mechanics, 9FM0/01 Core Pure Mathematics 1 and 9FM0/02 Core Pure Mathematics 2.
- 59 original questions and 450 marks, with native mathematics, faithful vector figures and each question's complete official mark scheme.
- Past Papers now has 12 papers, 121 questions and 900 marks; Papers has 8,743 questions in total.

## Luisa v0.63

- When one past paper is chosen, Question order offers In paper order, printing that paper's questions in original question-number order. Other selected questions follow in the order they were added.
- With All past papers the order options and behaviour are unchanged; print layouts, saved selections and saved paper IDs are preserved.

## Luisa v0.62

- Add the June 2025 Edexcel Pure Mathematics Paper 2 (9MA0/02) to Past Papers: 15 original questions, 100 marks, native mathematics and the five source figures.
- Pair every question with its complete official mark scheme, including alternatives, examiner notes and helpful diagrams.
- Past Papers now has six papers, 62 questions and 450 marks; Papers has 8,684 questions in total.

## Luisa v0.61

- Default Papers to one question per page and add a Condensed checkbox below the solutions checkbox.
- Remove paper-wide source instructions from printouts. Use a bold page title, a single footer rule and a creation timestamp.
- Allow eight lines for question diagrams and use matching compact headings in solutions and mark schemes.

## Luisa v0.60

- Papers selects Edexcel topics from the textbook chapter list. Separate Exam style and Past Papers controls include a past-paper dropdown.
- Printed question headers use one line with verified marks, including 15 marks for Mechanics Year 2 Chapter 7 Set B Gold. Printed question diagrams use at most six lines of height.

## Luisa v0.22 — 27 October 2026

Mechanics Year 1: 114 checked slides and 58 booklet pages across chapters 8–11. Master workspace migrated to _LUISA with complete source material and recovery package. ADA backup refreshed.

# Luisa release history

## Luisa v0.02 — 26 October 2026

- Corrected the erroneous v2 label; releases increment by0.01.
- Rebuilt Pure1 Chapter1 question/answer layouts, numbering, concealment and reveal order.
- Checked31 slides at3 viewport sizes and the16-page student booklet.
- White slide backgrounds across the existing lesson viewers.
- Existing Pure2 Chapters1–5 retained.


## V11.1 — 24 October 2026

- Added independent answers to trigonometry Exercise 9G questions 8 and 9 (slides 54–55), including the rock-pool sketch and time interval.
- Added matching blank answer spaces to the chapter booklet; retained two original slides per A4 page.
- Kept other teaching slides, all question-library content and existing question printouts unchanged.

## V11 — 24 October 2026

Changes from V10:

- Restored source lesson content, notation, diagrams, question groupings and teaching sequences across all 14 Pure Year 1 chapters.
- Replaced separate skill/topic theory booklets with complete chapter lesson booklets, two individually numbered slides per page, matching the board titles and blue banners.
- Kept theory, hints and explanations in student booklets. Answer covers become writing spaces; revealed board answers use blue.
- Added touch Next controls, independent question-mark answer covers and ticks. Removed technical reveal labels and footer counters.
- Added consistent chapter title pages, red extension titles, boxed theory panels, corrected list indentation and centred binomial notation.
- Kept the existing question library and Print Skill / Print Topic question printouts unchanged.
- Added release history and preserved V10 for rollback.

## V10 — preserved rollback release

Commit: `7b19511209c0c277a0f169e0db53ca9af4cfcb23`

Annotated tag: `fmq-v10`

Original app folder: `fmq-prototype_v10` (preserved).

## Release and rollback procedure

Each published development release increments the version by one, records its change list, and receives an annotated Git tag. Never replace a previously published tag. Before rollback, preserve the current release under its tag. Restore the requested tagged tree in a new commit on main and publish normally; do not reset or erase repository history. Recheck the live version, lesson links, booklets and question printing after deployment.
