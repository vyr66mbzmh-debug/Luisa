# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.77 -->
**Release 0.77 · GitHub #141.** Written for any successor agent, engine or person; it needs no earlier conversation.

**Current state.** Luisa v0.77 is the published version on Cloudflare (owner edition) and ADA (staff and pupil editions), all built from one merged revision recorded on GitHub #141. Papers holds 44 past papers (444 questions) and 83 PMT questions (58 Core Pure 1, 25 Core Pure 2; 704 marks), 9,149 questions in all. Every question exists once.

**What changed (PAP-077-1 … PAP-077-5 in docs/requirements/register.json, each with acceptance criteria).**
- **Duplicates removed (PAP-077-1).** The 51 PMT copies (v0.75/v0.76 `duplicateOf`) are deleted from `pmt-catalogue.json`, `content/pmt/` and `resources/pmt/`. The survivor is the official past paper (47) or else the earliest PMT question (4). Survivors keep their wording, marks, scheme and difficulty and gain the copy's chapter keys and skills. Counts: 134 → 83 PMT (Core Pure 1 73 → 58, Core Pure 2 61 → 25), 1,183 → 704 marks, bank 9,200 → 9,149. `pmt-catalogue.json` `migrations` maps every removed ID to its survivor; Papers replaces a saved copy with its survivor once and says so. Full removed → retained list: `docs/evidence/v077-duplicates-removed.json`.
- **No-duplicates rule (PAP-077-2).** `scripts/duplicates.py` compares every question (shingles plus equations; threshold 0.4 where an official or PMT question is involved, 0.95 between Luisa's own). Every candidate must be decided in `docs/evidence/duplicate-decisions.json` (51 duplicates, 13 confirmed not duplicates). `scripts/luisa.py check` fails on a copy, an undecided candidate or a stale migration. `scripts/import/pmt.py` and `scripts/import/integrate.py` refuse a copy; a new official paper that repeats a PMT question prints the exact `duplicates.py remove` command. The generator's copy safety net stays. The one-time bank-wide check found no further copies.
- **Tickbox retired (PAP-077-3).** The PMT tickbox, its state key and tests are gone in every edition; an old saved `pmt` key is ignored.
- **PMT is exam-style (PAP-077-4).** PMT questions are in the "Exam style" box for pupils and in teacher exam papers, where only the mark scheme names the source.
- **Original exams (PAP-077-5, best effort).** 56 of the 83 PMT questions were matched by sight to an Edexcel 8FM0/01 or 9FM0 paper (2018–2022 and the Sample) and carry `originalExam`, shown in the mark scheme after the PMT label; 27 are "unknown". Nothing was guessed; three look-alikes were rejected. Evidence: `docs/evidence/v077-pmt-original-exams.json`. Source PDFs stay outside Git.

**How to add questions now.** Run the importer as before; if it stops with a duplicate, keep the official paper (or the earlier PMT question), record the decision with `python3 scripts/duplicates.py remove …` or as a not-duplicate in `duplicate-decisions.json`, then rerun the gate.

**Next jobs.** None from this assignment. The owner may review the remaining PMT source slips listed in `tests/test_pmt.py` (`SOURCE_SLIPS`) and the 27 PMT questions without a known original.

**Verified.** The gate, the duplicate, PMT and Papers tests and the full Papers browser and print suites passed; exact-head CI, the independent code review and the live checks (owner, disconnected use, ADA staff and pupil, accounts unchanged, the published report's single handoff, recovery ZIP) are recorded on #141.

**Outstanding.** Two owner notes from v0.65 still await the owner's view: the per-cell marks in the one three-cell table question, and the course label for a future 9FM0 Mechanics paper.

**Usage.** v0.77 used 24,977,814 tokens up to the release build (main session since the v0.77 baseline, per-call transcript usage via scripts/release/tokens.py; mostly cached context); the final count is on #141.
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
