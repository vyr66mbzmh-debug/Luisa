# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.74 -->
**Release 0.74 · GitHub #135.** Written for any successor agent, engine or person; it needs no earlier conversation.

**Current state.** Luisa v0.74 is the published version on Cloudflare (owner edition) and ADA (staff and pupil editions), all built from one merged revision recorded on GitHub #135. Papers holds 44 past papers (444 questions, 3,450 marks) and 9,066 questions in all. This release is the first of three owner-assigned releases; v0.75 (PMT Core Pure 1) and v0.76 (PMT Core Pure 2) follow.

**What changed (PAP-074-1 … PAP-074-4 in docs/requirements/register.json, each with acceptance criteria).**
- **Mark-scheme flag (PAP-074-1).** Every catalogue row (`textbook-catalogue.json`, `practice-catalogue.json`, `exam-catalogue.json`) has `markScheme`:
  - `official`: the paired official exam-board scheme. A past paper qualifies only when every step is an official `-ms-` crop of that same paper.
  - `source`: a marking scheme printed in the question's own source, recorded with its kind and source page in `sourceScheme`. It is reserved for PMT.
  - `worked`: Luisa worked solutions only.
  - `none`: neither.

  `scripts/mark_schemes.py` derives the values (`apply`, `check`, `counts`), and `luisa.py check` fails on any mismatch. Current counts: 444 official (past papers) and 8,622 worked (554 exam style, 1,921 Practice Booklet, 6,147 skill questions). The Practice Booklet PDFs contain no mark schemes.
- **Exam paper eligibility (PAP-074-2).** Only `official` and `source` questions can go in the teacher-only exam paper: timed generation draws only on them, and `create()` refuses any other row for every print option. The panel shows "N of M questions in the chosen sources and topics have an official mark scheme…", and Generate is disabled when N is 0. A worked-solution question added by hand is labelled "No mark scheme" and blocks Preview until it is removed. Questions without marks stay excluded.
- **Sources (PAP-074-3).** The front page and question pages print no source, paper, series, original question number, context line or ID. Each scheme entry prints "Source: <exact source> · ID <bank id>". Other printouts are unchanged.
- **Tests (PAP-074-4).** `tests/test_mark_schemes.py` covers the derivation, tampering and unchanged IDs. The browser tests cover timed generation over mixed sources, a manual flag-false question, and sources absent from question pages and present in the scheme (DOM and real PDF text) for mixed papers and a mixed source.

**Next jobs.** v0.75 imports the PMT Core Pure 1 revision questions and v0.76 the Core Pure 2 ones. The source is the owner's OneDrive folder "PMT further maths questions" (Year 1 and Year 2, 17 PDFs). The work adds a "PMT" source tickbox, per-question difficulty using a written rubric, duplicate links to existing past-paper questions, and the mark-scheme flag from each PDF. PMT chapters without a scheme are imported with the flag `worked` or `none` and are listed as needing a scheme.

**Verified.** The gate passed with 0 skips, and the full Papers browser and print suites passed. Exact-head CI and the independent review are recorded on #135, as are the live checks: owner, disconnected use, ADA staff and pupil, the published report's single handoff, accounts unchanged, and the recovery ZIP.

**Outstanding.** Two owner notes from v0.65 still await the owner's view: the per-cell marks in the one three-cell table question, and the course label for a future 9FM0 Mechanics paper.

**Usage.** About 6.7 million tokens in the lead session up to the pull request (35 API calls; per-call transcript usage via scripts/release/tokens.py), plus the independent reviewer; final totals are in the token log on #135.
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
