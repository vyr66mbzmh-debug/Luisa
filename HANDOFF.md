# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.76 -->
**Release 0.76 · GitHub #138.** Written for any successor agent, engine or person; it needs no earlier conversation.

**Current state.** Luisa v0.76 is the published version on Cloudflare (owner edition) and ADA (staff and pupil editions), all built from one merged revision recorded on GitHub #138. Papers holds 44 past papers (444 questions) and 134 PMT questions (73 Core Pure 1, 61 Core Pure 2; 1,183 marks), 9,200 questions in all. The owner's three-release assignment (v0.74 mark-scheme flag, v0.75 and v0.76 PMT) is complete.

**What changed (PAP-076-1 … PAP-076-8 in docs/requirements/register.json, each with acceptance criteria).**
- **Import (PAP-076-1, 2).** The eight owner PDFs "PMT further maths questions/Year 2/Ch.N …" were identified by content and hash (inventory on #138; hashes and pages in `docs/evidence/v076-import-pmt-core-pure-2.json`). The set `scripts/import/sets/v076-pmt-cp2/` (prompts, `questions.json`, `figs.json`, `files.py`) feeds `scripts/import/pmt.py` exactly as in v0.75. Source PDFs stay outside Git.
- **Schemes (PAP-076-3).** Each question's scheme is its own page-image crops (`markScheme: source`). `scripts/mark_schemes.py check` now rejects a PMT row whose steps are not crops of its own scheme. Year 2 has no misplaced appendix.
- **Difficulty (PAP-076-4).** The v0.75 rubric, unchanged: 13 easy, 36 medium, 12 difficult, each with a one-line reason. Reviewer re-rate of 10 (15%, seed 76): 7 of 10 agreed blind, 9 of 10 after resolution by the rubric.
- **Tickbox (PAP-076-5).** Core Pure 2 joins the "PMT" tickbox. A version-2 saved session now restores its old exam box to exam-style and past papers only, never PMT (a v0.75 review finding).
- **Duplicates (PAP-076-6).** 36 copies carry `duplicateOf` (34 past paper, 2 PMT); Ch.6 Q6 is confirmed not a copy of June 2025 9FM0/01 Q2. The selection heading says how many copies a generated paper skips, and the count box is capped at that pool. The six Core Pure 1 copies whose originals span several chapters now carry those chapters too.
- **Tests and evidence (PAP-076-7, 8).** `tests/test_pmt.py` per chapter for both books; a mixed past-paper + Core Pure 1 + Core Pure 2 exam print test with no source before the scheme.

**Source slips kept as printed (for owner review).** Ch.1 Q10 "r(cosθ θ+ isinθ)" (same as Core Pure 1 Ch.2 Q7); Ch.3 Q6(c) lacks "where" (the Sample paper copy has it). Ch.2 Q4, Ch.3 Q2, Ch.5 Q5 and Ch.6 Q3 and Q6 print only question totals.

**Owner note.** Copies and their past-paper originals can differ in difficulty (Core Pure 1: 6 of 15; Core Pure 2: 19 of 36) because the PMT ratings follow the new rubric and the past-paper ratings come from earlier imports. Both were kept; no generated paper holds both copies.

**Next jobs.** None from this assignment. The owner may review the source slips and the difficulty note above.

**Verified.** The gate, the PMT tests and the full Papers browser and print suites passed; exact-head CI, the independent code review and the live checks (owner, disconnected use, ADA staff and pupil, accounts unchanged, the published report's single handoff, recovery ZIP) are recorded on #138.

**Outstanding.** Two owner notes from v0.65 still await the owner's view: the per-cell marks in the one three-cell table question, and the course label for a future 9FM0 Mechanics paper.

**Usage.** v0.76 used 9,381,102 tokens up to the release build (main session since the v0.76 baseline plus the independent maths reviewer; the Core Pure 2 transcription ran earlier in the same session and is counted on #137); the final count is on #138.
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
