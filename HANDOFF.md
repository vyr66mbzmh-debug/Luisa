# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.73 -->
**Release 0.73 · GitHub #130.** Written for any successor agent, engine or person; it needs no earlier conversation.

**Current state.** Luisa v0.73 is the published version on Cloudflare (owner edition) and ADA (staff and pupil editions), all built from one merged revision recorded on GitHub #130. This is a tooling release with no user-visible feature changes. Papers holds 44 past papers (444 questions, 3,450 marks), as in v0.72. Numbering: the owner decided that the Sample papers import is v0.72 (#128) and this tooling job is v0.73.

**What changed (OPS-064 … OPS-070 in docs/requirements/register.json, each with acceptance criteria).**
- **Release tooling in Git (OPS-064).** Everything needed to import, build, test, land, deploy, verify, archive and report is in `scripts/release/` and `scripts/import/`, each with a README, and in the runbook `docs/agentic/RELEASE-RUNBOOK.md`. The v0.72 Sample papers are the reference import set; their figures, payloads and catalogue rows regenerate byte-for-byte. v0.73 itself was released with this tooling. The old private and /tmp copies are kept, each with a pointer note to the new location.
- **Private data stays private (OPS-065).** Scripts read private values only through `scripts/release/private.py` (WORKSPACE.json, `LUISA_STATE_DIR`) and never print them. `python3 scripts/luisa.py privacy`, which is in the gate, blocks:
  - personal absolute paths;
  - private hosts and addresses, matched by committed hashes (and by exact private values when the private configuration is present);
  - stray email addresses in documentation and scripts;
  - owner source PDFs.

  The 30 legacy lesson files that recorded a personal OneDrive path in an unused `source` field now record `owner materials/…`.
- **Agent-neutral (OPS-066).** AGENTS.md starts with a quick start for any AI agent. The independent reviewer is a role with inputs and a JSON schema (`docs/agentic/review-record.schema.json`), which `scripts/land.py` validates. CLAUDE.md is only a pointer.
- **Reproducible environment (OPS-067).** `python3 scripts/bootstrap.py` builds `<state>/env` from exact pins in `requirements-tools.txt`. It includes Node through nodejs-wheel, and uses the installed Chrome or else Playwright's Chromium. Tooling under `scripts/` uses no ripgrep, does not call Node and has no string-evaluated browser waits; a test enforces this. The local browser suites still use string waits against a local server without ADA's CSP (decision: they are not run against ADA).
- **Cold-start check (OPS-068).** `python3 scripts/luisa.py doctor` prints PASS or MISSING per item, with the human action for each MISSING item, and never prints private values.
- **One handoff per report (OPS-069).** `scripts/release/report.py` builds development-progress.html, the release report and both email bodies. Each contains HANDOFF.md exactly once, under "Luisa v<version> handoff", using the version from release.json. The separate short bracketed handoff paragraph used up to v0.72 is gone. The gate (`luisa.py report`) and tests check this, and the pupil edition still strips the section. Earlier reports are left as published.
- **Completion check (OPS-070).** `scripts/release/finish.py` refuses to send the owner report, and `finish.py complete` refuses to finish, unless all of these are present: HANDOFF.md and the report agree with release.json, the register names the issue, the issue has evidence and a token log with its source, and an SMTP record exists.
- **HANDOFF.md layout.** This file now holds only the current release block plus the standing sections "Tooling, access and where everything lives" and "Standing rules and authority". Earlier blocks and the historical notes (v0.51–v0.72, the foundation record, ADA and PWA history) moved verbatim to `docs/handoff/HISTORY.md`; `scripts/release/docs.py` moves each superseded block there.

**Next jobs.** None assigned. A later import of genuine June 2022 papers needs the owner to supply them (see #124).

**Verified.** The gate passed with 0 skips (including the privacy and report checks), and the Papers browser suites passed from a freshly bootstrapped environment after the old /tmp environment was set aside. Doctor reported PASS. A no-context reviewer did a cold-start dry run, and its gaps were fixed. Exact-head CI and the independent review are recorded on #130, as are the live checks: owner, disconnected use, ADA staff and pupil, the published report's single handoff, accounts unchanged, and the recovery ZIP.

**Outstanding.** Two owner notes from v0.65 still await the owner's view: the per-cell marks in the one three-cell table question, and the course label for a future 9FM0 Mechanics paper.

**Usage.** v0.73 implementation used about 29.4 million tokens in the main session up to the pull request (132 API calls, mostly cached context reads; source: the session transcript's per-call usage, summed with scripts/release/tokens.py). Review and release totals, with their source, are logged on GitHub #130.
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
