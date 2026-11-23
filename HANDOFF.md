# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.75 -->
**Release 0.75 · GitHub #137.** Written for any successor agent, engine or person; it needs no earlier conversation.

**Current state.** Luisa v0.75 is the published version on Cloudflare (owner edition) and ADA (staff and pupil editions), all built from one merged revision recorded on GitHub #137. Papers holds 44 past papers (444 questions) and 73 PMT Core Pure 1 questions (625 marks), 9,139 questions in all. v0.76 (PMT Core Pure 2, #138) is next.

**What changed (PAP-075-1 … PAP-075-8 in docs/requirements/register.json, each with acceptance criteria).**
- **Import (PAP-075-1, 2).** The nine owner PDFs "PMT further maths questions/Year 1/Ch.N …" were identified by content and hash (inventory on #137, hashes and pages in `docs/evidence/v075-import-pmt-core-pure-1.json`). `scripts/import/pmt.py` with the set `scripts/import/sets/v075-pmt-cp1/` (prompts transcribed from rendered pages, `questions.json` metadata, `figs.json`, `scheme-moves.json`) writes `content/pmt/*.json`, `resources/pmt/*/` and `pmt-catalogue.json`. Source PDFs stay outside Git.
- **Schemes (PAP-075-3).** Each question's scheme is its own page-image crops from the sheet; rows carry `markScheme: source` and `sourceScheme` pages. The Ch.6 sheet prints Ch.9 Q10's "Appendix: Alternatives to (b)" after Ch.6 Q3; it is attached to Ch.9 Q10 and both rows carry a source note.
- **Difficulty (PAP-075-4).** Rubric: easy = routine, a standard result applied directly in short structured parts; medium = standard methods over several steps or one signposted non-routine step; difficult (the brief's "hard") = unstructured, multi-concept, method unguided, or long and delicate work. Each row has a one-line reason. Reviewer re-rate of 11 (15%): 6 of 11 agreed blind, 10 of 11 after resolution by the rubric.
- **Tickbox (PAP-075-5).** "PMT" in the Papers sources, off by default; saved sessions without it restore unticked.
- **Duplicates (PAP-075-6).** 15 copies carry `duplicateOf` (13 past paper, 2 PMT). Generation drops the copy when its original is in the pool; nothing is deleted.
- **Tests and evidence (PAP-075-7, 8).** `tests/test_pmt.py` (per chapter: counts, marks, fields, crops, figures, no source in text, part marks, duplicates, offline packs), selection and print browser tests including a mixed past-paper + PMT exam with no source on question pages.

**Source slips kept as printed (for owner review).** Ch.2 Q7 "r(cosθ θ+ isinθ)"; Ch.6 Q2 has no lead-in before its bullet list; Ch.6 Q6 "4x x + 3y + 8z = 3"; the Ch.6/Ch.9 appendix placement. Ch.4 Q4–5 and Ch.8 Q3–4 print only question totals.

**Next jobs.** v0.76 imports PMT Core Pure 2 (8 sheets, 61 questions, 558 marks) by the same process (#138). Year 2 Ch.1 Q10 repeats Year 1 Ch.2 Q7, and Year 2 Ch.3 Q2 is June 2019 9FM0/01 Q2.

**Verified.** The gate, the PMT tests and the full Papers browser and print suites passed; exact-head CI, the independent code review and the live checks (owner, disconnected use, ADA staff and pupil, accounts unchanged, the published report's single handoff, recovery ZIP) are recorded on #137.

**Outstanding.** Two owner notes from v0.65 still await the owner's view: the per-cell marks in the one three-cell table question, and the course label for a future 9FM0 Mechanics paper.

**Usage.** v0.75 used 12,503,346 tokens up to the release build (main session since the v0.75 baseline plus the independent maths reviewer); the final count is on #137.
<!-- END LUISA-RELEASE-BLOCK -->

## Tooling, access and where everything lives

Everything needed to import papers, build, test, land, deploy, verify, archive and report a release is in this repository (OPS-064). Only private values stay outside Git (OPS-065).

**Start from scratch (any agent, any engine, or a human).**
1. Clone the repository. Read AGENTS.md (quick start), this file and `docs/agentic/RELEASE-RUNBOOK.md`.
2. Ask the owner for the private state folder (default `~/.local/share/luisa-agent-state`, or set `LUISA_STATE_DIR`) containing `WORKSPACE.json`. You also need GitHub CLI access to the repository and SSH access to the ADA host.
3. Run `python3 scripts/bootstrap.py`. It creates the pinned environment at `<state>/env`.
4. Run `<state>/env/bin/python scripts/luisa.py doctor`. Every line must say PASS. Each MISSING line names the human action needed.
5. Follow the runbook for the job.

**Where each tool lives.**

| Area | Location | What it does |
|---|---|---|
| Gate, build, artifact checks, privacy scan, cold-start check | `scripts/luisa.py` | Commands: `gate`, `check`, `test`, `scan`, `privacy`, `build`, `check-artifact`, `doctor`, `requirements` |
| Environment | `scripts/bootstrap.py`, `requirements-tools.txt` | Builds the pinned Python environment: Playwright, PyMuPDF, SymPy and Node (nodejs-wheel), plus a browser |
| Release tooling | `scripts/release/` | Its README describes each script: `land_build.py`, `ada.py`, `verify_owner.py`, `qa_live.py`, `qa_offline.py`, `docs.py`, `report.py`, `finish.py`, `tokens.py`, `doctor.py` and `private.py` |
| Past-paper import | `scripts/import/` | Per-paper pipeline (README), with the v0.72 Sample set as the reference input set in `scripts/import/sets/` |
| Landing a reviewed PR | `scripts/land.py` | Run through `scripts/release/land_build.py` |
| Recovery archive | `scripts/archive_release.py` | Run through `scripts/release/finish.py archive` |
| Usage records | `scripts/usage.py` | `start`/`end` per job |
| Release specs | `docs/releases/v<version>.json`, `docs/releases/v<version>-handoff.md` | Release notes, report intro and this file's release block |
| Review role | `docs/agentic/REVIEWER-RULES.md`, `docs/agentic/review-record.schema.json` | Reviewer role and output schema |

**Private configuration keys** (`WORKSPACE.json`; names only, values never in Git, logs or reports): `master`, `mailSender`, `pastPaperSource` (the folder where the owner puts new past papers; since v0.73 `<state>/past-paper-source/`), `ada.sshHost`, `ada.sshPort`, `ada.url`, `ada.pupilEmailDomain`, and `ada.layout.releaseRoot`, `releasePrefix`, `startScript`, `dataDir`, `runtimePython`, `supervisorCommand`, `serviceName`, `nginx`. `scripts/release/private.py` is the only reader.

**What stays private, and why.** The following stay in the private state folder or the owner's machine:
- credentials and SMTP settings, inside the mail adapter;
- the ADA SSH host and the server's internal paths;
- mail sender and recipient;
- account databases and their snapshots;
- owner source PDFs;
- unpublished corrections;
- session transcripts;
- release work folders (`<state>/releases/v<version>/`, holding QA results and printed PDFs);
- owner reports (`<state>/reports/`).

The repository is public, so anything committed is visible to everyone. `python3 scripts/luisa.py privacy` (part of the gate) blocks credentials, personal paths, private hosts and owner source PDFs.

**The ADA website address** is public. The owner site's offline page links pupils to it, and the auth app names it. The SSH host and server layout are private.

## Standing rules and authority
- **Rules:** AGENTS.md (mandatory standard), `docs/agentic/LEAD-RULES.md`, `docs/agentic/REVIEWER-RULES.md`, and the requirement register `docs/requirements/register.json` (generated `REQUIREMENTS.md`). New owner instructions take precedence; record them on GitHub and in the register while implementing (OPS-063).
- **Release targets:** every release goes to Cloudflare (owner edition, deployed automatically from main) and to ADA (staff and pupil editions), all from the same checked artifact. Then the recovery ZIP and the SMTP owner report (FR-024, `docs/handoff/RELEASE-EMAIL.md`) follow.
- **Report:** one handoff in every form (OPS-069). A release is complete only when `scripts/release/finish.py complete` passes (OPS-070).
- **Usage limits:** never schedule wakeups. On a usage limit, write the exact resume point to `<state>/v<version-without-dot>/PROGRESS.md` (the agent's notes folder; the tools' work folder is `<state>/releases/v<version>/`, see the runbook) and stop; the owner restarts the work.
- **Legacy Maths progress:** questions 3423/3423 (100%) and sections 132/132, reported separately from slide, booklet and expanded-index progress.

## History
Earlier release handoffs (v0.51 onwards) and the historical notes kept here before v0.73 are in `docs/handoff/HISTORY.md`.
