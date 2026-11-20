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
